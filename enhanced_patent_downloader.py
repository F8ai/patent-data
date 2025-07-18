#!/usr/bin/env python3
"""
Enhanced Cannabis Patent Downloader
===================================

Advanced script to download comprehensive cannabis patents from multiple sources:
- USPTO PatFT (Patent Full-Text Database)
- Google Patents API
- Patent scrapers for detailed content
- Classification-based searches

Saves all data to patent-data repo corpus directory with proper formatting.
"""

import os
import json
import time
import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, quote_plus
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_patent_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCannabisPatentDownloader:
    """Advanced cannabis patent downloader with multiple data sources."""
    
    def __init__(self, output_dir: str = "agents/patent-agent/data/corpus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Patent classification codes for cannabis/pharmaceutical
        self.cannabis_classifications = [
            "A61K31/05",    # Cannabis compounds
            "A61K36/185",   # Cannabis preparations
            "C07D311/58",   # Cannabinoid chemistry
            "A23L33/105",   # Cannabis food products
            "A61P25/30",    # Cannabis neurological treatments
            "C12N15/8271",  # Cannabis genetic engineering
            "A01H5/00",     # Cannabis cultivation
            "B01D11/02"     # Cannabis extraction
        ]
        
        # Comprehensive cannabis search terms
        self.search_terms = [
            # Basic terms
            "cannabis", "marijuana", "marihuana", "hemp", "cannabinoid",
            # Compounds
            "tetrahydrocannabinol", "THC", "delta-9-THC", "delta-8-THC",
            "cannabidiol", "CBD", "cannabigerol", "CBG", "cannabinol", "CBN",
            "cannabichromene", "CBC", "tetrahydrocannabivarin", "THCV",
            "cannabidivarin", "CBDV", "cannabigerolic acid", "CBGA",
            # Terpenes
            "myrcene", "limonene", "pinene", "linalool", "caryophyllene",
            "humulene", "terpinolene", "ocimene", "bisabolol",
            # Processes
            "cannabis extraction", "cannabis cultivation", "cannabis processing",
            "cannabis purification", "cannabis distillation", "cannabis isolation",
            "supercritical CO2 extraction", "butane extraction", "ethanol extraction",
            # Products
            "cannabis oil", "cannabis concentrate", "cannabis edible", "cannabis topical",
            "cannabis vaporizer", "cannabis delivery system", "cannabis capsule",
            "cannabis tincture", "cannabis patch", "cannabis inhaler",
            # Medical
            "medical marijuana", "medical cannabis", "therapeutic cannabis",
            "cannabis treatment", "cannabis therapy", "cannabis medicine",
            # Testing
            "cannabis testing", "cannabis analysis", "cannabis potency",
            "cannabis contamination", "cannabis quality control"
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        self.downloaded_patents = set()
        self.patent_data = {}
        
    def search_google_patents(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search Google Patents for cannabis-related patents."""
        patents = []
        
        try:
            base_url = "https://patents.google.com/"
            search_url = f"{base_url}?q={quote_plus(query)}&country=US&type=PATENT"
            
            logger.info(f"Searching Google Patents for: {query}")
            
            response = self.session.get(search_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract patent results
                patent_items = soup.find_all('article', class_='result')
                
                for item in patent_items[:max_results]:
                    try:
                        patent_link = item.find('h3').find('a')['href']
                        patent_number = re.search(r'/patent/([^/]+)', patent_link).group(1)
                        title = item.find('h3').get_text(strip=True)
                        
                        # Get snippet/abstract
                        snippet_elem = item.find('div', class_='snippet')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        patents.append({
                            'patent_number': patent_number,
                            'title': title,
                            'abstract': snippet,
                            'url': f"https://patents.google.com{patent_link}",
                            'source': 'Google Patents'
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing patent item: {e}")
                        continue
                
                logger.info(f"Found {len(patents)} patents for query: {query}")
                
        except Exception as e:
            logger.error(f"Error searching Google Patents for '{query}': {e}")
        
        return patents
    
    def get_patent_details_google(self, patent_number: str) -> Optional[Dict]:
        """Get detailed patent information from Google Patents."""
        try:
            url = f"https://patents.google.com/patent/{patent_number}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            patent_data = {
                'patent_number': patent_number,
                'source': 'Google Patents'
            }
            
            # Extract title
            title_elem = soup.find('span', {'itemprop': 'title'})
            if title_elem:
                patent_data['title'] = title_elem.get_text(strip=True)
            
            # Extract abstract
            abstract_elem = soup.find('div', class_='abstract')
            if abstract_elem:
                patent_data['abstract'] = abstract_elem.get_text(strip=True)
            
            # Extract inventors
            inventors = []
            inventor_elems = soup.find_all('dd', {'itemprop': 'inventor'})
            for elem in inventor_elems:
                inventors.append(elem.get_text(strip=True))
            patent_data['inventors'] = inventors
            
            # Extract assignees
            assignees = []
            assignee_elems = soup.find_all('dd', {'itemprop': 'assignee'})
            for elem in assignee_elems:
                assignees.append(elem.get_text(strip=True))
            patent_data['assignees'] = assignees
            
            # Extract dates
            date_elems = soup.find_all('time')
            for elem in date_elems:
                date_type = elem.get('itemprop', '')
                date_value = elem.get('datetime', '')
                if date_type and date_value:
                    patent_data[f"{date_type}_date"] = date_value
            
            # Extract description
            description_elem = soup.find('section', {'itemprop': 'description'})
            if description_elem:
                patent_data['description'] = description_elem.get_text(strip=True)
            
            # Extract claims
            claims = []
            claims_section = soup.find('section', {'itemprop': 'claims'})
            if claims_section:
                claim_elems = claims_section.find_all('div', class_='claim')
                for claim in claim_elems:
                    claims.append(claim.get_text(strip=True))
            patent_data['claims'] = claims
            
            return patent_data
            
        except Exception as e:
            logger.error(f"Error getting patent details for {patent_number}: {e}")
            return None
    
    def search_uspto_patft(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search USPTO PatFT database."""
        patents = []
        
        try:
            base_url = "https://patft.uspto.gov/netacgi/nph-Parser"
            
            # Search parameters
            params = {
                'Sect1': 'PTO2',
                'Sect2': 'HITOFF',
                'p': '1',
                'u': '/netahtml/PTO/search-bool.html',
                'r': '0',
                'f': 'S',
                'l': '50',
                'TERM1': query,
                'FIELD1': 'ABST',
                'co1': 'AND',
                'TERM2': '',
                'FIELD2': '',
                'd': 'PTXT',
                's1': '',
                'op1': 'AND',
                's2': '',
                'op2': 'AND',
                's3': '',
                'op3': 'AND',
                's4': '',
                'op4': 'AND',
                's5': '',
                'op5': 'AND',
                's6': ''
            }
            
            logger.info(f"Searching USPTO PatFT for: {query}")
            
            response = self.session.get(base_url, params=params, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse search results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/netacgi/nph-Parser' in href and 'Sect1=PTO1' in href:
                        # Extract patent number from link
                        patent_match = re.search(r's1=(\d+)', href)
                        if patent_match:
                            patent_number = patent_match.group(1)
                            title = link.get_text(strip=True)
                            
                            patents.append({
                                'patent_number': patent_number,
                                'title': title,
                                'source': 'USPTO PatFT',
                                'url': f"https://patft.uspto.gov{href}"
                            })
                
                logger.info(f"Found {len(patents)} patents from USPTO PatFT")
                
        except Exception as e:
            logger.error(f"Error searching USPTO PatFT: {e}")
        
        return patents
    
    def save_patent_to_corpus(self, patent_data: Dict):
        """Save patent data to corpus directory in multiple formats."""
        try:
            patent_number = patent_data.get('patent_number', 'unknown')
            clean_number = ''.join(c for c in str(patent_number) if c.isalnum())
            
            # Enhanced patent document
            patent_doc = {
                **patent_data,
                'download_timestamp': datetime.now().isoformat(),
                'processed_for_training': True
            }
            
            # Save as JSON
            json_file = self.output_dir / f"cannabis_patent_{clean_number}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(patent_doc, f, indent=2, ensure_ascii=False)
            
            # Save as training text
            text_file = self.output_dir / f"cannabis_patent_{clean_number}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"PATENT NUMBER: {patent_number}\n")
                f.write(f"TITLE: {patent_doc.get('title', 'N/A')}\n")
                f.write(f"SOURCE: {patent_doc.get('source', 'N/A')}\n")
                f.write("=" * 80 + "\n")
                f.write("ABSTRACT:\n")
                f.write(patent_doc.get('abstract', 'N/A') + "\n\n")
                
                if patent_doc.get('inventors'):
                    f.write("INVENTORS:\n")
                    for inventor in patent_doc['inventors']:
                        f.write(f"- {inventor}\n")
                    f.write("\n")
                
                if patent_doc.get('assignees'):
                    f.write("ASSIGNEES:\n")
                    for assignee in patent_doc['assignees']:
                        f.write(f"- {assignee}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("DESCRIPTION:\n")
                f.write(patent_doc.get('description', 'N/A') + "\n\n")
                
                if patent_doc.get('claims'):
                    f.write("=" * 80 + "\n")
                    f.write("CLAIMS:\n")
                    for i, claim in enumerate(patent_doc['claims'], 1):
                        f.write(f"Claim {i}: {claim}\n\n")
            
            # Add to JSONL corpus for training
            jsonl_file = self.output_dir / "cannabis_patents_corpus.jsonl"
            with open(jsonl_file, 'a', encoding='utf-8') as f:
                corpus_entry = {
                    'text': f"Patent {patent_number}: {patent_doc.get('title', '')}. {patent_doc.get('abstract', '')} {patent_doc.get('description', '')}",
                    'metadata': {
                        'patent_number': patent_number,
                        'title': patent_doc.get('title', ''),
                        'source': patent_doc.get('source', ''),
                        'type': 'cannabis_patent'
                    }
                }
                f.write(json.dumps(corpus_entry) + '\n')
            
            logger.info(f"Saved cannabis patent {patent_number} to corpus")
            self.downloaded_patents.add(patent_number)
            
        except Exception as e:
            logger.error(f"Error saving patent {patent_number}: {e}")
    
    def create_summary_report(self):
        """Create comprehensive summary of downloaded patents."""
        try:
            summary = {
                'download_date': datetime.now().isoformat(),
                'total_patents': len(self.downloaded_patents),
                'search_terms_used': self.search_terms,
                'classification_codes': self.cannabis_classifications,
                'output_directory': str(self.output_dir),
                'downloaded_patents': list(self.downloaded_patents),
                'files_created': {
                    'json_files': len(list(self.output_dir.glob('*.json'))),
                    'text_files': len(list(self.output_dir.glob('*.txt'))),
                    'corpus_file': 'cannabis_patents_corpus.jsonl'
                }
            }
            
            # Save summary
            summary_file = self.output_dir / "download_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            # Create CSV index
            csv_file = self.output_dir / "cannabis_patents_index.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Patent Number', 'Title', 'Source', 'Download Date'])
                for patent_number in self.downloaded_patents:
                    json_file = self.output_dir / f"cannabis_patent_{patent_number}.json"
                    if json_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as pf:
                            data = json.load(pf)
                            writer.writerow([
                                patent_number,
                                data.get('title', 'N/A'),
                                data.get('source', 'N/A'),
                                data.get('download_timestamp', 'N/A')
                            ])
            
            logger.info(f"Created summary report: {len(self.downloaded_patents)} cannabis patents downloaded")
            
        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
    
    def download_all_cannabis_patents(self):
        """Main method to download comprehensive cannabis patents."""
        logger.info("Starting enhanced cannabis patent download")
        
        all_patents = []
        
        # Search Google Patents for each term
        for term in self.search_terms:
            logger.info(f"Searching Google Patents for: {term}")
            patents = self.search_google_patents(term, max_results=20)
            all_patents.extend(patents)
            time.sleep(2)  # Rate limiting
        
        # Search USPTO PatFT
        for term in self.search_terms[:10]:  # Limit to top terms
            logger.info(f"Searching USPTO PatFT for: {term}")
            patents = self.search_uspto_patft(term, max_results=10)
            all_patents.extend(patents)
            time.sleep(3)  # Rate limiting
        
        # Remove duplicates
        unique_patents = {}
        for patent in all_patents:
            patent_id = patent.get('patent_number')
            if patent_id and patent_id not in unique_patents:
                unique_patents[patent_id] = patent
        
        logger.info(f"Found {len(unique_patents)} unique cannabis patents")
        
        # Download detailed information for each patent
        for i, (patent_id, patent_data) in enumerate(unique_patents.items(), 1):
            logger.info(f"Processing patent {i}/{len(unique_patents)}: {patent_id}")
            
            # Get detailed information from Google Patents
            detailed_data = self.get_patent_details_google(patent_id)
            if detailed_data:
                patent_data.update(detailed_data)
            
            # Save to corpus
            self.save_patent_to_corpus(patent_data)
            
            # Rate limiting
            time.sleep(1)
            
            # Progress update
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(unique_patents)} patents processed")
        
        # Create summary report
        self.create_summary_report()
        
        logger.info(f"Cannabis patent download complete! {len(self.downloaded_patents)} patents saved to {self.output_dir}")

def main():
    """Main entry point."""
    downloader = EnhancedCannabisPatentDownloader()
    downloader.download_all_cannabis_patents()

if __name__ == "__main__":
    main()