#!/usr/bin/env python3
"""
Manual Download Helper for ASP Literature
Generates various export formats for manually downloading failed papers

Usage:
    python manual_download_helper.py
    python manual_download_helper.py --input asp_literature/pdfs/download_failures.csv
    python manual_download_helper.py --format all
"""

import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict
import sys


class ManualDownloadHelper:
    """Generate helpful outputs for manually downloading papers"""

    def __init__(self, failures_file: str = None, filtered_papers_file: str = None):
        """Initialize helper"""
        self.failures_file = Path(failures_file) if failures_file else \
            Path('asp_literature/pdfs/download_failures.csv')
        self.filtered_papers_file = Path(filtered_papers_file) if filtered_papers_file else \
            Path('asp_literature/asp_papers_filtered.json')

        self.failed_papers = []
        self.load_data()

    def load_data(self):
        """Load failed downloads and paper metadata"""
        # Load failures
        failed_pmids = set()
        if self.failures_file.exists():
            with open(self.failures_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    failed_pmids.add(row['pmid'])

        # Load full paper metadata for failed PMIDs
        if self.filtered_papers_file.exists():
            with open(self.filtered_papers_file, 'r') as f:
                all_papers = json.load(f)
                self.failed_papers = [p for p in all_papers if p['pmid'] in failed_pmids]

        print(f"Loaded {len(self.failed_papers)} failed papers with metadata")

    def generate_pubmed_links(self, output_file: str = None):
        """Generate text file with PubMed links"""
        output_file = output_file or 'asp_literature/manual_download_links.txt'

        with open(output_file, 'w') as f:
            f.write("ASP Literature - Manual Download Links\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Papers to download: {len(self.failed_papers)}\n")
            f.write("Instructions: Visit each link and download PDF if available\n")
            f.write("Save PDFs to: asp_literature/pdfs/ with filename: PMID.pdf\n\n")
            f.write("=" * 80 + "\n\n")

            for i, paper in enumerate(self.failed_papers, 1):
                pmid = paper['pmid']
                title = paper['title']
                year = paper.get('year', 'Unknown')
                journal = paper.get('journal', 'Unknown')

                f.write(f"{i}. PMID {pmid} - {title[:80]}\n")
                f.write(f"   Journal: {journal} ({year})\n")
                f.write(f"   PubMed: https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n")

                # Add DOI link if available
                if paper.get('doi'):
                    f.write(f"   DOI: https://doi.org/{paper['doi']}\n")

                f.write("\n")

        print(f"✓ Generated PubMed links: {output_file}")
        return output_file

    def generate_endnote_xml(self, output_file: str = None):
        """Generate EndNote XML export"""
        output_file = output_file or 'asp_literature/manual_download_endnote.xml'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<xml>\n')
            f.write('<records>\n')

            for paper in self.failed_papers:
                f.write('  <record>\n')
                f.write('    <database name="PubMed" path="pubmed.nih.gov">PubMed</database>\n')
                f.write('    <source-app name="Manual Export" version="1.0">Manual Export</source-app>\n')
                f.write(f'    <rec-number>{paper["pmid"]}</rec-number>\n')

                f.write('    <ref-type name="Journal Article">17</ref-type>\n')

                f.write('    <contributors>\n')
                if paper.get('authors'):
                    f.write('      <authors>\n')
                    for author in paper['authors'].split(', ')[:5]:  # First 5 authors
                        if author.strip():
                            f.write(f'        <author>{author.strip()}</author>\n')
                    f.write('      </authors>\n')
                f.write('    </contributors>\n')

                f.write('    <titles>\n')
                f.write(f'      <title>{self._escape_xml(paper["title"])}</title>\n')
                if paper.get('journal'):
                    f.write(f'      <secondary-title>{self._escape_xml(paper["journal"])}</secondary-title>\n')
                f.write('    </titles>\n')

                if paper.get('year'):
                    f.write('    <dates>\n')
                    f.write(f'      <year>{paper["year"]}</year>\n')
                    f.write('    </dates>\n')

                if paper.get('doi'):
                    f.write(f'    <electronic-resource-num>{paper["doi"]}</electronic-resource-num>\n')

                f.write(f'    <urls>\n')
                f.write(f'      <related-urls>\n')
                f.write(f'        <url>https://pubmed.ncbi.nlm.nih.gov/{paper["pmid"]}/</url>\n')
                f.write(f'      </related-urls>\n')
                f.write(f'    </urls>\n')

                f.write('  </record>\n')

            f.write('</records>\n')
            f.write('</xml>\n')

        print(f"✓ Generated EndNote XML: {output_file}")
        return output_file

    def generate_bibtex(self, output_file: str = None):
        """Generate BibTeX file"""
        output_file = output_file or 'asp_literature/manual_download.bib'

        with open(output_file, 'w', encoding='utf-8') as f:
            for paper in self.failed_papers:
                pmid = paper['pmid']

                # Clean title and authors
                title = paper['title'].replace('{', '').replace('}', '')
                authors = paper.get('authors', 'Unknown').replace(',', ' and')

                f.write(f"@article{{pmid{pmid},\n")
                f.write(f"  title = {{{title}}},\n")
                f.write(f"  author = {{{authors}}},\n")

                if paper.get('journal'):
                    f.write(f"  journal = {{{paper['journal']}}},\n")
                if paper.get('year'):
                    f.write(f"  year = {{{paper['year']}}},\n")
                if paper.get('doi'):
                    f.write(f"  doi = {{{paper['doi']}}},\n")

                f.write(f"  pmid = {{{pmid}}},\n")
                f.write(f"  url = {{https://pubmed.ncbi.nlm.nih.gov/{pmid}/}},\n")
                f.write("  note = {Manual download required}\n")
                f.write("}\n\n")

        print(f"✓ Generated BibTeX: {output_file}")
        return output_file

    def generate_csv_for_librarian(self, output_file: str = None):
        """Generate CSV for librarian request"""
        output_file = output_file or 'asp_literature/librarian_request.csv'

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['PMID', 'Title', 'Authors', 'Journal', 'Year', 'DOI',
                         'PubMed_URL', 'Relevance_Score', 'Notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for paper in self.failed_papers:
                writer.writerow({
                    'PMID': paper['pmid'],
                    'Title': paper['title'],
                    'Authors': paper.get('authors', '')[:100],  # Truncate for readability
                    'Journal': paper.get('journal', ''),
                    'Year': paper.get('year', ''),
                    'DOI': paper.get('doi', ''),
                    'PubMed_URL': f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/",
                    'Relevance_Score': paper.get('relevance_score', ''),
                    'Notes': 'Not available via open access - institutional access needed'
                })

        print(f"✓ Generated librarian request CSV: {output_file}")
        return output_file

    def generate_pmid_list(self, output_file: str = None):
        """Generate simple PMID list"""
        output_file = output_file or 'asp_literature/failed_pmids.txt'

        with open(output_file, 'w') as f:
            f.write("# List of PMIDs that failed to download\n")
            f.write(f"# Total: {len(self.failed_papers)} papers\n")
            f.write("# One PMID per line - can be used with batch downloaders\n\n")

            for paper in self.failed_papers:
                f.write(f"{paper['pmid']}\n")

        print(f"✓ Generated PMID list: {output_file}")
        return output_file

    def generate_summary_report(self, output_file: str = None):
        """Generate summary report"""
        output_file = output_file or 'asp_literature/manual_download_report.txt'

        # Analyze by journal
        journal_counts = {}
        for paper in self.failed_papers:
            journal = paper.get('journal', 'Unknown')
            journal_counts[journal] = journal_counts.get(journal, 0) + 1

        top_journals = sorted(journal_counts.items(), key=lambda x: -x[1])[:10]

        with open(output_file, 'w') as f:
            f.write("ASP Literature Manual Download Summary Report\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Total papers needing manual download: {len(self.failed_papers)}\n\n")

            f.write("Top 10 Journals (may have institutional subscriptions):\n")
            f.write("-" * 80 + "\n")
            for journal, count in top_journals:
                f.write(f"  {count:3d} papers - {journal}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("Generated Export Files:\n")
            f.write("-" * 80 + "\n")
            f.write("  - manual_download_links.txt      : Direct PubMed/DOI links\n")
            f.write("  - manual_download_endnote.xml    : Import to EndNote\n")
            f.write("  - manual_download.bib            : BibTeX format\n")
            f.write("  - librarian_request.csv          : Send to librarian\n")
            f.write("  - failed_pmids.txt               : Plain PMID list\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("Recommended Actions:\n")
            f.write("-" * 80 + "\n")
            f.write("1. Check if Cincinnati Children's has subscriptions to top journals\n")
            f.write("2. Send librarian_request.csv to medical librarian\n")
            f.write("3. Import EndNote XML to reference manager\n")
            f.write("4. For high-relevance papers, request via interlibrary loan\n")
            f.write("5. Check author webpages/ResearchGate for preprints\n")
            f.write("\n")

        print(f"✓ Generated summary report: {output_file}")
        return output_file

    def _escape_xml(self, text):
        """Escape XML special characters"""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

    def generate_all(self):
        """Generate all export formats"""
        print(f"\n{'=' * 80}")
        print("Generating Manual Download Helper Files")
        print(f"{'=' * 80}\n")

        self.generate_pubmed_links()
        self.generate_endnote_xml()
        self.generate_bibtex()
        self.generate_csv_for_librarian()
        self.generate_pmid_list()
        self.generate_summary_report()

        print(f"\n{'=' * 80}")
        print("✅ All files generated in asp_literature/")
        print(f"{'=' * 80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate helpful files for manually downloading failed papers'
    )
    parser.add_argument('--input',
                       default='asp_literature/pdfs/download_failures.csv',
                       help='Path to download failures CSV')
    parser.add_argument('--papers',
                       default='asp_literature/asp_papers_filtered.json',
                       help='Path to filtered papers JSON')
    parser.add_argument('--format',
                       choices=['links', 'endnote', 'bibtex', 'csv', 'pmids', 'summary', 'all'],
                       default='all',
                       help='Which format to generate')

    args = parser.parse_args()

    helper = ManualDownloadHelper(
        failures_file=args.input,
        filtered_papers_file=args.papers
    )

    if not helper.failed_papers:
        print("No failed papers found. Nothing to do.")
        sys.exit(0)

    if args.format == 'all':
        helper.generate_all()
    elif args.format == 'links':
        helper.generate_pubmed_links()
    elif args.format == 'endnote':
        helper.generate_endnote_xml()
    elif args.format == 'bibtex':
        helper.generate_bibtex()
    elif args.format == 'csv':
        helper.generate_csv_for_librarian()
    elif args.format == 'pmids':
        helper.generate_pmid_list()
    elif args.format == 'summary':
        helper.generate_summary_report()


if __name__ == '__main__':
    main()
