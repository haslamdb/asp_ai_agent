#!/usr/bin/env python3
"""
ASP Literature Mining Tool
Complete workflow to search, find PDFs, and download antimicrobial stewardship papers

Usage:
    python asp_literature_miner.py --help
    python asp_literature_miner.py --step all --years 5 --max-results 100
    python asp_literature_miner.py --step search --max-results 500
    
Author: Generated for Cincinnati Children's Hospital ASP AI Agent
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import csv

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


class ASPLiteratureSearcher:
    """Search PubMed for ASP-related papers"""
    
    def __init__(self, email="your.email@example.com"):
        """Initialize PubMed searcher"""
        if not HAS_PYMED:
            raise ImportError("pymed required. Install with: pip install pymed")
        
        self.pubmed = PubMed(tool="ASPLiteratureMiner", email=email)
        self.results = []
    
    def search_asp_papers(self, query: Optional[str] = None, 
                         years_back: int = 5, 
                         max_results: int = 100) -> List[Dict]:
        """
        Search PubMed for ASP papers
        
        Args:
            query: Custom search query (uses default ASP search if None)
            years_back: Years back to search
            max_results: Maximum results to retrieve
            
        Returns:
            List of paper dictionaries
        """
        
        # Default comprehensive ASP search
        if query is None:
            query = (
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
            )
        
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
                    article_data = {
                        'pmid': article.pubmed_id,
                        'title': article.title or 'Unknown',
                        'authors': ', '.join(
                            [f"{au['lastname']} {au['initials']}" 
                             for au in article.authors]
                        ) if article.authors else 'Unknown',
                        'year': article.publication_date.year 
                                if article.publication_date else 'Unknown',
                        'journal': article.journal or 'Unknown',
                        'abstract': article.abstract or '',
                        'url': f'https://pubmed.ncbi.nlm.nih.gov/{article.pubmed_id}/',
                        'doi': getattr(article, 'doi', None),
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
    
    def save_to_csv(self, filename: str = 'asp_literature.csv') -> bool:
        """Save results to CSV"""
        if not self.results:
            print_error("No results to save")
            return False
        
        try:
            if HAS_PANDAS:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
            else:
                # Fallback without pandas
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
            
            print_success(f"Saved {len(self.results)} papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save CSV: {str(e)}")
            return False
    
    def save_to_json(self, filename: str = 'asp_literature.json') -> bool:
        """Save results to JSON"""
        if not self.results:
            print_error("No results to save")
            return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print_success(f"Saved {len(self.results)} papers to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save JSON: {str(e)}")
            return False


class OpenAccessFinder:
    """Find open access PDFs for papers"""
    
    def __init__(self, email: str = "your.email@example.com"):
        """Initialize finder"""
        if not HAS_REQUESTS:
            raise ImportError("requests required. Install with: pip install requests")
        
        self.email = email
        self.results = []
    
    def find_pmc_pdf(self, pmid: str) -> Optional[str]:
        """Find PDF on PubMed Central"""
        try:
            url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
            params = {
                'ids': pmid,
                'idtype': 'pubmed',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if 'result' in data and pmid in data['result']:
                pmcid = data['result'][pmid].get('pmcid')
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
            
            response = requests.get(url, params=params, timeout=5)
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
        
        for idx, paper in enumerate(papers_list):
            if (idx + 1) % 50 == 0:
                print_info(f"Progress: {idx + 1}/{len(papers_list)}")
            
            result = self.find_pdf(
                pmid=paper['pmid'],
                doi=paper.get('doi')
            )
            self.results.append(result)
            
            time.sleep(delay)
        
        found_count = sum(1 for r in self.results if r['found'])
        print_success(f"Found open access PDFs for {found_count}/{len(self.results)} papers")
        
        return self.results
    
    def save_to_csv(self, filename: str = 'pdf_locations.csv') -> bool:
        """Save PDF locations"""
        if not self.results:
            print_error("No results to save")
            return False
        
        try:
            if HAS_PANDAS:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
            else:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
            
            print_success(f"Saved PDF locations to {filename}")
            return True
        except Exception as e:
            print_error(f"Failed to save CSV: {str(e)}")
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
    
    def get_filename_from_pmid(self, pmid: str, title: str = '') -> str:
        """Generate filename from PMID and title"""
        if title:
            safe_title = "".join(c if c.isalnum() or c in ' -_' else '' 
                                for c in title[:40])
            return f"{pmid}_{safe_title}.pdf"
        return f"{pmid}.pdf"
    
    def download_pdf(self, url: str, filename: str, 
                    timeout: int = 30) -> bool:
        """Download PDF from URL"""
        filepath = self.output_dir / filename
        
        # Skip if already exists
        if filepath.exists():
            return True
        
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Verify it's a PDF
            if 'application/pdf' not in response.headers.get('content-type', ''):
                return False
            
            # Write file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
        
        except Exception as e:
            return False
    
    def batch_download(self, pdf_results: List[Dict], 
                      rate_limit: float = 1.0) -> int:
        """Download batch of PDFs"""
        print_info(f"Starting downloads (rate limit: {rate_limit}s between requests)...")
        
        success_count = 0
        
        for idx, result in enumerate(pdf_results):
            # Find best URL
            url = result.get('pmc_pdf') or result.get('unpaywall_pdf')
            
            if not url:
                self.failed.append(result['pmid'])
                continue
            
            # Try to download
            filename = self.get_filename_from_pmid(result['pmid'], '')
            success = self.download_pdf(url, filename)
            
            if success:
                self.downloaded.append(result['pmid'])
                success_count += 1
                
                if (idx + 1) % 25 == 0:
                    print_info(f"Downloaded {success_count}/{idx + 1}")
            else:
                self.failed.append(result['pmid'])
            
            time.sleep(rate_limit)
        
        print_success(f"Downloaded {success_count} PDFs to {self.output_dir}")
        return success_count
    
    def get_stats(self) -> Dict:
        """Get download statistics"""
        total_size_mb = sum(
            (self.output_dir / f).stat().st_size / (1024*1024)
            for f in self.output_dir.glob('*.pdf')
            if f.is_file()
        )
        
        return {
            'total_downloaded': len(self.downloaded),
            'total_failed': len(self.failed),
            'total_size_mb': total_size_mb,
            'pdf_count': len(list(self.output_dir.glob('*.pdf')))
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ASP Literature Mining Tool - Search, find, and download papers'
    )
    parser.add_argument('--step',
                       choices=['search', 'find', 'download', 'all'],
                       default='all',
                       help='Which step to run')
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
    
    papers_csv = output_dir / f'asp_papers_{args.years}yr.csv'
    pdf_locations_csv = output_dir / 'pdf_locations.csv'
    pdfs_dir = output_dir / 'pdfs'
    
    # Step 1: Search
    if args.step in ['search', 'all']:
        if not HAS_PYMED:
            print_error("pymed required for search: pip install pymed")
            sys.exit(1)
        
        print_header(f"STEP 1: SEARCHING PubMed ({args.years} years, max {args.max_results} papers)")
        
        searcher = ASPLiteratureSearcher()
        searcher.search_asp_papers(
            years_back=args.years,
            max_results=args.max_results
        )
        
        searcher.save_to_csv(str(papers_csv))
        searcher.save_to_json(str(output_dir / f'asp_papers_{args.years}yr.json'))
    
    # Step 2: Find PDFs
    if args.step in ['find', 'all']:
        print_header("STEP 2: FINDING OPEN ACCESS PDFs")
        
        if not papers_csv.exists():
            print_error(f"Search results not found: {papers_csv}")
            print_info("Run with --step search first")
            sys.exit(1)
        
        # Read papers
        if HAS_PANDAS:
            papers_df = pd.read_csv(papers_csv)
            papers_list = papers_df.to_dict('records')
        else:
            import json
            with open(papers_csv.with_suffix('.json')) as f:
                papers_list = json.load(f)
        
        finder = OpenAccessFinder()
        finder.batch_find_pdfs(papers_list, delay=args.delay)
        finder.save_to_csv(str(pdf_locations_csv))
    
    # Step 3: Download
    if args.step in ['download', 'all']:
        print_header("STEP 3: DOWNLOADING PDFs")
        
        if not pdf_locations_csv.exists():
            print_error(f"PDF locations not found: {pdf_locations_csv}")
            print_info("Run with --step find first")
            sys.exit(1)
        
        # Read PDF locations
        if HAS_PANDAS:
            pdf_df = pd.read_csv(pdf_locations_csv)
            pdf_results = pdf_df.to_dict('records')
        else:
            import json
            with open(pdf_locations_csv.with_suffix('.json')) as f:
                pdf_results = json.load(f)
        
        downloader = PDFDownloader(output_dir=str(pdfs_dir))
        downloader.batch_download(pdf_results, rate_limit=args.download_delay)
        
        stats = downloader.get_stats()
        print_success(f"Download complete: {stats['pdf_count']} PDFs, {stats['total_size_mb']:.1f} MB")
    
    # Summary
    print_header("COMPLETE!")
    print_success(f"Literature database: {output_dir}")
    print_info(f"Papers CSV: {papers_csv}")
    print_info(f"PDF Locations: {pdf_locations_csv}")
    print_info(f"PDFs Directory: {pdfs_dir}")
    print("\nNext steps:")
    print("  1. Review papers_csv to understand literature")
    print("  2. Feed pdfs_dir to your citation_assistant")
    print("  3. Use metadata in your AI training")


if __name__ == '__main__':
    main()