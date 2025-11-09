#!/usr/bin/env python3
"""
ASP Literature Mining Tool
Complete workflow to search, filter with AI, find PDFs, and download papers

Usage:
    python asp_literature_miner.py --help
    python asp_literature_miner.py --step all --years 5 --max-results 100 --query-type training
    python asp_literature_miner.py --step search --max-results 500 --query-type broad
    python asp_literature_miner.py --step filter --model "qwen2.5:72b-instruct-q4_K_M" --score-threshold 7.0

Author: Generated for Cincinnati Children's Hospital ASP AI Agent
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try importing optional dependencies
try:
    from pymed import PubMed
    HAS_PYMED = True
except ImportError:
    HAS_PYMED = False
    print("Warning: pymed not installed. Install with: pip install pymed")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. Install with: pip install requests")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Install with: pip install pandas")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Warning: tqdm not installed (pip install tqdm). Proceeding without progress bars.")

# Helper to gracefully handle missing tqdm
def pbar(iterable, **kwargs):
    if HAS_TQDM:
        return tqdm(iterable, **kwargs)
    return iterable


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}→{Colors.END} {text}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")


class ASPLiteratureSearcher:
    """Search PubMed for ASP-related papers"""

    def __init__(self, email="dbhaslam@gmail.com"):
        """Initialize PubMed searcher"""
        if not HAS_PYMED:
            raise ImportError("pymed required. Install with: pip install pymed")

        self.pubmed = PubMed(tool="ASPLiteratureMiner", email=email)
        self.results = []

    def search_asp_papers(self, query: str,
                         years_back: int = 5,
                         max_results: int = 100) -> List[Dict]:
        """
        Search PubMed for ASP papers

        Args:
            query: Custom search query
            years_back: Years back to search
            max_results: Maximum results to retrieve

        Returns:
            List of paper dictionaries
        """

        # Add date filter
        date_from = (datetime.now() - timedelta(days=365*years_back)).strftime("%Y/%m/%d")
        date_to = datetime.now().strftime("%Y/%m/%d")
        date_filter = f' AND ("{date_from}"[Date - Publication] : "{date_to}"[Date - Publication])'

        full_query = query + date_filter

        print_info(f"Searching for papers from {years_back} years back...")
        print_info(f"Query: {query[:80]}...")

        try:
            articles = self.pubmed.query(full_query, max_results=max_results)

            for article in articles:
                try:
                    # Sanitize strings to remove embedded newlines and carriage returns
                    # This fixes a bug where pymed sometimes returns concatenated records
                    def clean_string(s):
                        if s is None:
                            return None
                        # Replace all types of newlines and carriage returns with spaces
                        return str(s).replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').strip()

                    # Clean the PMID specifically - should only be first value if multiple
                    pmid_raw = clean_string(article.pubmed_id)
                    pmid = pmid_raw.split()[0] if pmid_raw else None

                    # Skip if no valid PMID
                    if not pmid or not pmid.isdigit():
                        print_warning(f"Skipping article with invalid PMID: {pmid_raw[:50] if pmid_raw else 'None'}")
                        continue

                    article_data = {
                        'pmid': pmid,
                        'title': clean_string(article.title) or 'Unknown',
                        'authors': ', '.join(
                            [f"{clean_string(au.get('lastname', ''))} {clean_string(au.get('initials', ''))}"
                             for au in article.authors]
                        ) if article.authors else 'Unknown',
                        'year': article.publication_date.year
                                if article.publication_date else 'Unknown',
                        'journal': clean_string(article.journal) or 'Unknown',
                        'abstract': clean_string(article.abstract) or '',
                        'url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                        'doi': clean_string(getattr(article, 'doi', None)),
                    }
                    self.results.append(article_data)
                except Exception as e:
                    print_error(f"Error parsing article: {str(e)[:50]}")
                    continue

            print_success(f"Found {len(self.results)} papers")
            return self.results

        except Exception as e:
            print_error(f"Search failed: {str(e)}")
            return []

    def save_to_csv(self, filename: str) -> bool:
        """Save results to CSV"""
        if not self.results:
            print_error("No results to save")
            return False

        try:
            if HAS_PANDAS:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False, encoding='utf-8')
            else:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)

            print_success(f"Saved {len(self.results)} papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save CSV: {str(e)}")
            return False

    def save_to_json(self, filename: str) -> bool:
        """Save results to JSON"""
        if not self.results:
            print_error("No results to save")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            print_success(f"Saved {len(self.results)} papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save JSON: {str(e)}")
            return False


class AIFilterer:
    """Filter papers using a local LLM (Ollama)"""

    def __init__(self, ollama_url=None, model=None, use_scoring=True, max_tokens=128):
        """Initialize AI filterer"""
        if not HAS_REQUESTS:
            raise ImportError("requests required. Install with: pip install requests")

        # Load from environment with fallback defaults
        ollama_port = os.environ.get('OLLAMA_API_PORT', '11434')
        if ollama_url is None:
            ollama_url = f"http://localhost:{ollama_port}"

        if model is None:
            model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:72b-instruct-q4_K_M')

        self.ollama_url = f"{ollama_url}/api/chat"
        self.ollama_base_url = ollama_url
        self.ollama_tags_url = f"{ollama_url}/api/tags"
        self.model = model
        self.use_scoring = use_scoring
        self.max_tokens = max_tokens
        self.request_times = []  # Track request times for monitoring

        if use_scoring:
            self.system_prompt = (
                "You are an expert medical librarian specializing in Antimicrobial Stewardship education. "
                "Rate papers on relevance to ASP TRAINING/EDUCATION (0-10):\n\n"
                "10: Core ASP education (curriculum design, teaching methods, training programs)\n"
                "8-9: Strong training focus (competency assessment, educational interventions)\n"
                "6-7: Mixed clinical/educational (implementation with training component)\n"
                "4-5: Minimal education (brief mention of training in QI project)\n"
                "1-3: Tangential (general ASP topics, no educational focus)\n"
                "0: Not relevant\n\n"
                "Respond with ONLY the numeric score (0-10). No explanation."
            )
        else:
            self.system_prompt = (
                "You are an expert medical librarian specializing in Antimicrobial Stewardship education. "
                "Your task is to classify abstracts. Respond with ONLY 'Yes' or 'No'. "
                "'Yes' means the paper is primarily about training, teaching, curriculum, or educational principles for ASP. "
                "'No' means the paper is just a report on a QI intervention, antibiotic usage rates, or a clinical trial."
            )

        self.filtered_papers = []

    def check_ollama_connection(self) -> bool:
        """Check if Ollama server is running and model is available"""
        print_info(f"Checking connection to Ollama at {self.ollama_base_url}...")

        # Check if Ollama server is running
        try:
            response = requests.get(self.ollama_base_url, timeout=5)
            if response.status_code != 200:
                print_error(f"Ollama server found, but returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error(f"Could not connect to Ollama at {self.ollama_base_url}")
            print_info("Please start Ollama with: ollama serve")
            return False
        except Exception as e:
            print_error(f"Error connecting to Ollama: {e}")
            return False

        print_success("Ollama server is running")

        # Check if the specified model is available
        print_info(f"Checking if model '{self.model}' is available...")
        try:
            response = requests.get(self.ollama_tags_url, timeout=5)
            response.raise_for_status()
            data = response.json()

            available_models = [m['name'] for m in data.get('models', [])]

            # Check for exact match or with :latest tag
            model_found = False
            for available in available_models:
                if available == self.model or available == f"{self.model}:latest" or available.startswith(f"{self.model}:"):
                    model_found = True
                    break

            if not model_found:
                print_error(f"Model '{self.model}' not found in Ollama")
                print_info(f"Available models: {', '.join(available_models) if available_models else 'none'}")
                print_info(f"Pull the model with: ollama pull {self.model}")
                return False

            print_success(f"Model '{self.model}' is available")

            # Display GPU info if available
            self._check_gpu_availability()

            return True

        except Exception as e:
            print_error(f"Error checking model availability: {e}")
            return False

    def _check_gpu_availability(self):
        """Check and display GPU availability for Ollama"""
        try:
            # Try to get GPU info via nvidia-smi
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and result.stdout:
                print_info("GPU(s) detected:")
                for line in result.stdout.strip().split('\n'):
                    print(f"  {line}")
                print_info("Ollama will automatically use available GPU(s)")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # nvidia-smi not available, running on CPU
            print_warning("GPU not detected. Running on CPU (slower inference)")
        except Exception:
            pass  # Silent fail for GPU check

    def filter_paper(self, paper: Dict, threshold: float = 7.0, retry_count: int = 2) -> Tuple[bool, Optional[float]]:
        """
        Use LLM to determine if a paper is relevant to ASP training/education.
        Returns (is_relevant, score) where score is None for yes/no mode
        """
        user_prompt = f"Title: {paper['title']}\n\nAbstract: {paper['abstract']}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": self.max_tokens  # Limit output tokens for efficiency
            }
        }

        # Track request time for monitoring
        start_time = time.time()

        for attempt in range(retry_count + 1):
            try:
                # Increased timeout for GPU processing
                response = requests.post(self.ollama_url, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                answer = result.get('message', {}).get('content', '').strip()

                elapsed = time.time() - start_time
                self.request_times.append(elapsed)

                # Log slow requests
                if elapsed > 10:
                    print_warning(f"Slow filtering for PMID {paper['pmid']}: {elapsed:.1f}s")

                if self.use_scoring:
                    # Extract numeric score - handle cases where model adds explanation
                    try:
                        # Try to extract just the number
                        import re
                        match = re.search(r'\b([0-9]|10)(?:\.\d+)?\b', answer)
                        if match:
                            score = float(match.group(0))
                        else:
                            score = float(answer)

                        # Clamp to 0-10 range
                        score = max(0.0, min(10.0, score))
                        is_relevant = score >= threshold
                        return (is_relevant, score)
                    except ValueError:
                        print_warning(f"Could not parse score '{answer[:50]}' for PMID {paper['pmid']}, defaulting to 0")
                        return (False, 0.0)
                else:
                    # Yes/No mode
                    is_relevant = 'yes' in answer.lower()
                    return (is_relevant, None)

            except requests.exceptions.Timeout:
                if attempt < retry_count:
                    print_warning(f"Timeout for PMID {paper['pmid']}, retrying ({attempt+1}/{retry_count})...")
                    time.sleep(2)  # Brief delay before retry
                    continue
                else:
                    print_error(f"Ollama request timed out for PMID {paper['pmid']} after {retry_count+1} attempts")
                    return (False, None if not self.use_scoring else 0.0)
            except requests.exceptions.HTTPError as e:
                if attempt < retry_count and e.response.status_code >= 500:
                    print_warning(f"Server error for PMID {paper['pmid']}, retrying ({attempt+1}/{retry_count})...")
                    time.sleep(2)
                    continue
                else:
                    print_error(f"HTTP error for PMID {paper['pmid']}: {e.response.status_code}")
                    return (False, None if not self.use_scoring else 0.0)
            except Exception as e:
                print_error(f"Ollama request failed for PMID {paper['pmid']}: {str(e)[:100]}")
                return (False, None if not self.use_scoring else 0.0)

        return (False, None if not self.use_scoring else 0.0)

    def batch_filter(self, papers_list: List[Dict], threshold: float = 7.0,
                    checkpoint_file: Optional[str] = None) -> List[Dict]:
        """Filter a list of papers using the LLM with checkpointing support"""
        print_info(f"Starting AI filtering for {len(papers_list)} papers...")
        print_info(f"Mode: {'Scoring (0-10)' if self.use_scoring else 'Binary (Yes/No)'}")
        if self.use_scoring:
            print_info(f"Threshold: {threshold}")

        # Load checkpoint if exists
        start_idx = 0
        self.filtered_papers = []
        processed_pmids = set()

        if checkpoint_file and Path(checkpoint_file).exists():
            print_info(f"Loading checkpoint from {checkpoint_file}...")
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                    self.filtered_papers = checkpoint_data.get('filtered_papers', [])
                    processed_pmids = set(checkpoint_data.get('processed_pmids', []))
                    start_idx = len(processed_pmids)
                print_success(f"Resumed from checkpoint: {start_idx} papers already processed")
            except Exception as e:
                print_warning(f"Could not load checkpoint: {e}. Starting from beginning.")

        # Filter papers
        papers_to_process = [p for p in papers_list if p['pmid'] not in processed_pmids]

        for idx, paper in enumerate(pbar(papers_to_process, desc="Filtering Papers")):
            is_relevant, score = self.filter_paper(paper, threshold)

            if is_relevant:
                # Add score to paper data if using scoring mode
                if self.use_scoring and score is not None:
                    paper['relevance_score'] = round(score, 1)
                self.filtered_papers.append(paper)

            processed_pmids.add(paper['pmid'])

            # Adaptive delay based on GPU performance
            # With RTX A6000, we can process faster
            time.sleep(0.2)

            # Save checkpoint every 10 papers
            if checkpoint_file and (idx + 1) % 10 == 0:
                self._save_checkpoint(checkpoint_file, processed_pmids)

        # Final checkpoint save
        if checkpoint_file:
            self._save_checkpoint(checkpoint_file, processed_pmids)

        # Sort by score if using scoring mode
        if self.use_scoring:
            self.filtered_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        print_success(f"AI filtering complete. Kept {len(self.filtered_papers)} relevant papers.")
        if self.use_scoring and self.filtered_papers:
            avg_score = sum(p.get('relevance_score', 0) for p in self.filtered_papers) / len(self.filtered_papers)
            print_info(f"Average relevance score: {avg_score:.1f}/10")

        # Print performance statistics
        if self.request_times:
            avg_time = sum(self.request_times) / len(self.request_times)
            max_time = max(self.request_times)
            min_time = min(self.request_times)
            print_info(f"Performance: avg={avg_time:.1f}s, min={min_time:.1f}s, max={max_time:.1f}s per paper")

        return self.filtered_papers

    def _save_checkpoint(self, checkpoint_file: str, processed_pmids: set):
        """Save filtering progress checkpoint"""
        try:
            checkpoint_data = {
                'filtered_papers': self.filtered_papers,
                'processed_pmids': list(processed_pmids),
                'timestamp': datetime.now().isoformat()
            }
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            print_warning(f"Could not save checkpoint: {e}")

    def save_to_csv(self, filename: str) -> bool:
        """Save filtered results to CSV"""
        if not self.filtered_papers:
            print_error("No filtered results to save")
            return False

        try:
            if HAS_PANDAS:
                df = pd.DataFrame(self.filtered_papers)
                df.to_csv(filename, index=False, encoding='utf-8')
            else:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.filtered_papers[0].keys())
                    writer.writeheader()
                    writer.writerows(self.filtered_papers)

            print_success(f"Saved {len(self.filtered_papers)} filtered papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save CSV: {str(e)}")
            return False

    def save_to_json(self, filename: str) -> bool:
        """Save filtered results to JSON"""
        if not self.filtered_papers:
            print_error("No filtered results to save")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.filtered_papers, f, indent=2)
            print_success(f"Saved {len(self.filtered_papers)} filtered papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save JSON: {str(e)}")
            return False


class OpenAccessFinder:
    """Find open access PDFs for papers"""

    def __init__(self, email: str = "dbhaslam@gmail.com"):
        """Initialize finder"""
        if not HAS_REQUESTS:
            raise ImportError("requests required. Install with: pip install requests")

        self.email = email
        self.results = []
        # Add a User-Agent to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def find_pmc_pdf(self, pmid: str) -> Optional[str]:
        """Find PDF on PubMed Central"""
        try:
            url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
            params = {
                'ids': pmid,
                'idtype': 'pmid',  # Fixed: was 'pubmed', should be 'pmid'
                'format': 'json'
            }

            response = requests.get(url, params=params, timeout=5, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # PMC API returns a list of records
            records = data.get('records', [])
            if records and len(records) > 0:
                # First record should match our PMID
                record = records[0]
                pmcid = record.get('pmcid')
                if pmcid:
                    return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
        except Exception as e:
            pass

        return None

    def find_unpaywall_pdf(self, doi: str) -> Optional[Dict]:
        """Find PDF on Unpaywall"""
        if not doi:
            return None

        try:
            url = f"https://api.unpaywall.org/v2/{doi}"
            params = {'email': self.email}

            response = requests.get(url, params=params, timeout=5, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get('is_oa'):
                best_oa = data.get('best_oa_location', {})
                if best_oa.get('url_for_pdf'):
                    return {
                        'is_open_access': True,
                        'pdf_url': best_oa.get('url_for_pdf'),
                        'host_type': best_oa.get('host_type'),
                    }
        except Exception as e:
            pass

        return None

    def find_pdf(self, pmid: str, doi: Optional[str] = None) -> Dict:
        """Try to find PDF from all sources"""
        result = {
            'pmid': pmid,
            'doi': doi,
            'pmc_pdf': None,
            'unpaywall_pdf': None,
            'found': False,
            'source': None
        }

        # Try PMC first
        pmc_url = self.find_pmc_pdf(pmid)
        if pmc_url:
            result['pmc_pdf'] = pmc_url
            result['found'] = True
            result['source'] = 'PMC'
            return result

        # Try Unpaywall if DOI available
        if doi:
            unpaywall_data = self.find_unpaywall_pdf(doi)
            if unpaywall_data and unpaywall_data.get('pdf_url'):
                result['unpaywall_pdf'] = unpaywall_data['pdf_url']
                result['found'] = True
                result['source'] = 'Unpaywall'
                return result

        return result

    def batch_find_pdfs(self, papers_list: List[Dict],
                       delay: float = 0.5) -> List[Dict]:
        """Find PDFs for batch of papers"""
        print_info(f"Searching for open access PDFs for {len(papers_list)} papers...")

        for paper in pbar(papers_list, desc="Finding PDFs"):
            result = self.find_pdf(
                pmid=paper['pmid'],
                doi=paper.get('doi')
            )
            self.results.append(result)
            time.sleep(delay)

        found_count = sum(1 for r in self.results if r['found'])
        print_success(f"Found open access PDFs for {found_count}/{len(self.results)} papers")

        return self.results

    def save_to_csv(self, filename: str) -> bool:
        """Save PDF locations"""
        if not self.results:
            print_error("No results to save")
            return False

        try:
            if HAS_PANDAS:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False, encoding='utf-8')
            else:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)

            print_success(f"Saved PDF locations to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save CSV: {str(e)}")
            return False

    def save_to_json(self, filename: str) -> bool:
        """Save PDF locations to JSON"""
        if not self.results:
            print_error("No results to save")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            print_success(f"Saved PDF locations to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save JSON: {str(e)}")
            return False


class PDFDownloader:
    """Download PDFs from URLs"""

    def __init__(self, output_dir: str = './asp_pdfs'):
        """Initialize downloader"""
        if not HAS_REQUESTS:
            raise ImportError("requests required. Install with: pip install requests")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.downloaded = []
        self.failed = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_filename_from_pmid(self, pmid: str, title: str = '') -> str:
        """Generate filename from PMID and title"""
        if title:
            safe_title = "".join(c if c.isalnum() or c in ' -_' else ''
                                for c in title[:40]).strip()
            return f"{pmid}_{safe_title}.pdf"
        return f"{pmid}.pdf"

    def download_pdf(self, url: str, filename: str,
                    timeout: int = 30) -> Tuple[bool, str]:
        """
        Download PDF from URL.
        Returns (True/False for success, status message)
        """
        filepath = self.output_dir / filename

        if filepath.exists():
            return (True, "Already Exists")

        try:
            response = requests.get(
                url,
                timeout=timeout,
                stream=True,
                headers=self.headers
            )
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type:
                return (False, f"Not a PDF (Content-Type: {content_type})")

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return (True, "Success")

        except requests.exceptions.HTTPError as e:
            return (False, f"HTTP Error: {e.response.status_code}")
        except requests.exceptions.Timeout:
            return (False, "Timeout")
        except requests.exceptions.RequestException as e:
            return (False, f"Request Error: {str(e)[:50]}")
        except Exception as e:
            return (False, f"General Error: {str(e)[:50]}")

    def batch_download(self, pdf_results: List[Dict],
                      rate_limit: float = 1.0) -> int:
        """Download batch of PDFs"""
        print_info(f"Starting downloads (rate limit: {rate_limit}s between requests)...")

        success_count = 0

        for result in pbar(pdf_results, desc="Downloading PDFs"):
            url = result.get('pmc_pdf') or result.get('unpaywall_pdf')

            if not url:
                self.failed.append({
                    'pmid': result['pmid'],
                    'url': '',
                    'error': 'No URL found'
                })
                continue

            filename = self.get_filename_from_pmid(result['pmid'], '')
            success, message = self.download_pdf(url, filename)

            if success:
                self.downloaded.append(result['pmid'])
                if message == "Success":
                    success_count += 1
            else:
                print_error(f"Failed PMID {result['pmid']}: {message}")
                self.failed.append({
                    'pmid': result['pmid'],
                    'url': url,
                    'error': message
                })

            time.sleep(rate_limit)

        print_success(f"Downloaded {success_count} new PDFs to {self.output_dir}")
        self.save_failed_log(str(self.output_dir / 'download_failures.csv'))
        return success_count

    def save_failed_log(self, filename: str) -> bool:
        """Saves a CSV of failed downloads for review"""
        if not self.failed:
            print_info("No download failures to log.")
            return True

        print_info(f"Saving {len(self.failed)} download failures to {filename}...")
        try:
            fieldnames = self.failed[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.failed)
            return True
        except Exception as e:
            print_error(f"Failed to save failure log: {str(e)}")
            return False

    def get_stats(self) -> Dict:
        """Get download statistics"""
        # Fixed: glob returns Path objects, not strings
        total_size_mb = sum(
            f.stat().st_size / (1024*1024)
            for f in self.output_dir.glob('*.pdf')
            if f.is_file()
        )

        return {
            'total_downloaded_this_run': len(self.downloaded),
            'total_failed_this_run': len(self.failed),
            'total_size_mb': total_size_mb,
            'total_pdfs_in_dir': len(list(self.output_dir.glob('*.pdf')))
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ASP Literature Mining Tool - Search, filter, find, and download papers'
    )
    parser.add_argument('--step',
                       choices=['search', 'filter', 'find', 'download', 'all'],
                       default='all',
                       help='Which step to run')
    parser.add_argument('--query-type',
                       choices=['broad', 'training'],
                       default='broad',
                       help='Type of query to run (broad: all ASP, training: education/curriculum)')
    parser.add_argument('--model',
                       default=None,
                       help='Ollama model to use for filtering (default: from OLLAMA_MODEL env or qwen2.5:72b-instruct-q4_K_M)')
    parser.add_argument('--score-threshold', type=float, default=7.0,
                       help='Minimum relevance score (0-10) for filtering (default: 7.0)')
    parser.add_argument('--skip-ai-filter', action='store_true',
                       help='Skip AI filtering step (useful if Ollama unavailable)')
    parser.add_argument('--years', type=int, default=5,
                       help='Years back to search (default: 5)')
    parser.add_argument('--max-results', type=int, default=100,
                       help='Max papers to retrieve (default: 100)')
    parser.add_argument('--output-dir', default='./asp_literature',
                       help='Output directory (default: ./asp_literature)')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between API requests in seconds (default: 0.5)')
    parser.add_argument('--download-delay', type=float, default=1.0,
                       help='Delay between PDF downloads in seconds (default: 1.0)')

    args = parser.parse_args()

    # Validate dependencies
    if not HAS_REQUESTS:
        print_error("requests library required: pip install requests")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # File paths for pipeline
    papers_raw_csv = output_dir / f'asp_papers_raw_{args.years}yr.csv'
    papers_raw_json = output_dir / f'asp_papers_raw_{args.years}yr.json'
    papers_filtered_csv = output_dir / 'asp_papers_filtered.csv'
    papers_filtered_json = output_dir / 'asp_papers_filtered.json'
    pdf_locations_csv = output_dir / 'pdf_locations.csv'
    pdf_locations_json = output_dir / 'pdf_locations.json'
    pdfs_dir = output_dir / 'pdfs'
    failure_log = pdfs_dir / 'download_failures.csv'

    # Define search queries
    queries = {
        'broad': (
            '(("antimicrobial stewardship"[Title/Abstract] OR '
            '"antibiotic stewardship"[Title/Abstract] OR '
            '"ASP"[Title/Abstract] OR '
            '"antibiotic use"[Title/Abstract] OR '
            '"antimicrobial use"[Title/Abstract]) AND '
            '("intervention"[Title/Abstract] OR '
            '"education"[Title/Abstract] OR '
            '"curriculum"[Title/Abstract] OR '
            '"training"[Title/Abstract] OR '
            '"program"[Title/Abstract] OR '
            '"implementation"[Title/Abstract] OR '
            '"quality improvement"[Title/Abstract] OR '
            '"prescriber"[Title/Abstract] OR '
            '"behavior change"[Title/Abstract]))'
        ),
        'training': (
            '(("antimicrobial stewardship"[Title/Abstract] OR '
            '"antibiotic stewardship"[Title/Abstract]) AND '
            '("education"[Title/Abstract] OR '
            '"curriculum"[Title/Abstract] OR '
            '"training"[Title/Abstract] OR '
            '"medical education"[Title/Abstract] OR '
            '"fellowship"[Title/Abstract] OR '
            '"residency"[Title/Abstract] OR '
            '"prescriber education"[Title/Abstract] OR '
            '"competency"[Title/Abstract] OR '
            '"behavior change"[Title/Abstract]))'
        )
    }
    selected_query = queries[args.query_type]

    # Step 1: Search
    if args.step in ['search', 'all']:
        if not HAS_PYMED:
            print_error("pymed required for search: pip install pymed")
            sys.exit(1)

        print_header(f"STEP 1: SEARCHING PubMed ({args.query_type} query, {args.years} years, max {args.max_results} papers)")

        searcher = ASPLiteratureSearcher()
        searcher.search_asp_papers(
            query=selected_query,
            years_back=args.years,
            max_results=args.max_results
        )

        searcher.save_to_csv(str(papers_raw_csv))
        searcher.save_to_json(str(papers_raw_json))

    # Step 2: Filter with AI
    if args.step in ['filter', 'all'] and not args.skip_ai_filter:
        print_header(f"STEP 2: FILTERING WITH AI ({args.model})")

        # Prefer JSON over CSV
        if papers_raw_json.exists():
            print_info(f"Reading papers from JSON: {papers_raw_json.name}")
            with open(papers_raw_json, 'r', encoding='utf-8') as f:
                papers_list = json.load(f)
        elif papers_raw_csv.exists():
            print_info(f"Reading papers from CSV: {papers_raw_csv.name}")
            if HAS_PANDAS:
                papers_df = pd.read_csv(papers_raw_csv)
                papers_df['abstract'] = papers_df['abstract'].fillna('')
                papers_list = papers_df.to_dict('records')
            else:
                print_error("Cannot read CSV without pandas")
                sys.exit(1)
        else:
            print_error(f"Search results not found")
            print_info("Run with --step search first")
            sys.exit(1)

        filterer = AIFilterer(model=args.model, use_scoring=True)
        if not filterer.check_ollama_connection():
            print_warning("Cannot connect to Ollama. Skipping AI filtering.")
            print_info("Use --skip-ai-filter to suppress this check")
            if args.step == 'all':
                print_info("Continuing with unfiltered papers...")
            else:
                sys.exit(1)
        else:
            # Use checkpoint file for resumable filtering
            checkpoint_file = str(output_dir / 'filter_checkpoint.json')
            filterer.batch_filter(papers_list, threshold=args.score_threshold,
                                checkpoint_file=checkpoint_file)
            filterer.save_to_csv(str(papers_filtered_csv))
            filterer.save_to_json(str(papers_filtered_json))
            # Clean up checkpoint after successful completion
            if Path(checkpoint_file).exists():
                Path(checkpoint_file).unlink()

    # Step 3: Find PDFs
    if args.step in ['find', 'all']:
        print_header("STEP 3: FINDING OPEN ACCESS PDFs")

        # Determine input file (filtered or raw)
        if papers_filtered_json.exists():
            input_json = papers_filtered_json
            print_info(f"Using AI-filtered papers: {input_json.name}")
        elif papers_raw_json.exists():
            input_json = papers_raw_json
            print_info(f"Using raw papers (no AI filtering): {input_json.name}")
        else:
            print_error("No paper list found")
            print_info("Run with --step search first")
            sys.exit(1)

        # Read papers from JSON
        try:
            with open(input_json, 'r', encoding='utf-8') as f:
                papers_list = json.load(f)
                for paper in papers_list:
                    paper.setdefault('doi', None)
        except Exception as e:
            print_error(f"Failed to read papers: {e}")
            sys.exit(1)

        if not papers_list:
            print_error("No papers loaded")
            sys.exit(1)

        finder = OpenAccessFinder()
        finder.batch_find_pdfs(papers_list, delay=args.delay)
        finder.save_to_csv(str(pdf_locations_csv))
        finder.save_to_json(str(pdf_locations_json))

    # Step 4: Download
    if args.step in ['download', 'all']:
        print_header("STEP 4: DOWNLOADING PDFs")

        # Prefer JSON over CSV
        if pdf_locations_json.exists():
            print_info(f"Reading PDF locations from JSON")
            with open(pdf_locations_json, 'r', encoding='utf-8') as f:
                pdf_results = json.load(f)
        elif pdf_locations_csv.exists():
            print_info(f"Reading PDF locations from CSV")
            if HAS_PANDAS:
                pdf_df = pd.read_csv(pdf_locations_csv)
                pdf_df['pmc_pdf'] = pdf_df['pmc_pdf'].fillna('')
                pdf_df['unpaywall_pdf'] = pdf_df['unpaywall_pdf'].fillna('')
                pdf_results = pdf_df.to_dict('records')
            else:
                print_error("Cannot read CSV without pandas")
                sys.exit(1)
        else:
            print_error("PDF locations not found")
            print_info("Run with --step find first")
            sys.exit(1)

        if not pdf_results:
            print_error("No PDF locations loaded")
            sys.exit(1)

        downloader = PDFDownloader(output_dir=str(pdfs_dir))
        downloader.batch_download(pdf_results, rate_limit=args.download_delay)

        stats = downloader.get_stats()
        print_success(f"Download complete: {stats['total_pdfs_in_dir']} PDFs, {stats['total_size_mb']:.1f} MB")
        if stats['total_failed_this_run'] > 0:
            print_info(f"Failures logged to: {failure_log}")

    # Summary
    print_header("COMPLETE!")
    print_success(f"Literature database: {output_dir}")
    print_info(f"Raw Papers: {papers_raw_csv.name}, {papers_raw_json.name}")
    if papers_filtered_csv.exists():
        print_info(f"Filtered Papers: {papers_filtered_csv.name}, {papers_filtered_json.name}")
    print_info(f"PDF Locations: {pdf_locations_csv.name}, {pdf_locations_json.name}")
    print_info(f"PDFs Directory: {pdfs_dir}")
    if failure_log.exists():
        print_info(f"Failure Log: {failure_log}")
    print("\nNext steps:")
    print("  1. Review filtered papers (sorted by relevance score)")
    print("  2. Feed pdfs_dir to your citation_assistant")
    print("  3. Use metadata in your AI training")


if __name__ == '__main__':
    main()
