"""
Legal open-access paper downloader with CORE API integration and progress tracking
"""

import requests
import time
import os
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
from downloader.utils import get_logger, validate_doi, normalize_doi

logger = get_logger(__name__)


@dataclass
class DownloadProgress:
    """Progress tracking for downloads"""
    current: int = 0
    total: int = 0
    downloaded: int = 0
    failed: int = 0
    skipped: int = 0
    current_doi: str = ""
    status: str = "idle"  # idle, starting, processing, downloading, completed, stopped
    output_folder: str = ""
    start_time: Optional[datetime] = None
    
    @property
    def progress_percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        return data


class OpenAccessDownloader:
    """Modern open-access paper downloader with CORE API integration"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Science Downloader) AppleWebKit/537.36'
        })
        
        # Progress tracking
        self.progress = DownloadProgress()
        self.stop_flag = False
        self.downloaded_dois: Set[str] = set()
        self.failed_dois: Set[str] = set()
        
        # Load existing tracking data
        self._load_tracking_data()
        
    def download_papers(self, doi_file: Path, output_folder: Path) -> Dict[str, Any]:
        """
        Download papers from a DOI file using CORE API
        
        Args:
            doi_file: Path to file containing DOIs (one per line)
            output_folder: Directory to save papers
            
        Returns:
            Dict with download summary
        """
        try:
            logger.info(f"Starting download from {doi_file} to {output_folder}")
            
            # Read DOIs
            dois = self._load_dois(doi_file)
            if not dois:
                return {
                    'success': False,
                    'error': 'No valid DOIs found in file',
                    'total_requested': 0
                }
            
            # Initialize progress
            self.progress = DownloadProgress(
                total=len(dois),
                status="starting",
                output_folder=str(output_folder),
                start_time=datetime.now()
            )
            self.stop_flag = False
            
            # Ensure output directory exists
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Process DOIs
            results = self._process_dois(dois, output_folder)
            
            # Save tracking data
            self._save_tracking_data()
            
            # Update final status
            self.progress.status = "completed" if not self.stop_flag else "stopped"
            
            logger.info(f"Download completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in download_papers: {e}")
            self.progress.status = "error"
            return {
                'success': False,
                'error': str(e),
                'total_requested': 0
            }
    
    def _load_dois(self, doi_file: Path) -> List[str]:
        """Load and validate DOIs from file"""
        dois = []
        try:
            with open(doi_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        doi = normalize_doi(line)
                        if validate_doi(doi):
                            # Skip if already downloaded
                            if doi not in self.downloaded_dois:
                                dois.append(doi)
                            else:
                                self.progress.skipped += 1
                                logger.info(f"Skipping already downloaded DOI: {doi}")
                        else:
                            logger.warning(f"Invalid DOI at line {line_num}: {line}")
                            
        except Exception as e:
            logger.error(f"Error reading DOI file: {e}")
            
        return dois
    
    def _process_dois(self, dois: List[str], output_folder: Path) -> Dict[str, Any]:
        """Process DOIs and download papers"""
        self.progress.status = "processing"
        
        for i, doi in enumerate(dois):
            if self.stop_flag:
                break
                
            self.progress.current = i + 1
            self.progress.current_doi = doi
            self.progress.status = "downloading"
            
            try:
                result = self._download_single_paper(doi, output_folder)
                
                if result['success']:
                    self.progress.downloaded += 1
                    self.downloaded_dois.add(doi)
                    logger.info(f"Downloaded: {doi}")
                else:
                    self.progress.failed += 1
                    self.failed_dois.add(doi)
                    logger.warning(f"Failed to download {doi}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.progress.failed += 1
                self.failed_dois.add(doi)
                logger.error(f"Exception downloading {doi}: {e}")
            
            # Rate limiting
            if not self.stop_flag and i < len(dois) - 1:
                time.sleep(self.config.delay_between_downloads)
        
        return {
            'success': True,
            'total_requested': len(dois),
            'downloaded': self.progress.downloaded,
            'failed': self.progress.failed,
            'skipped': self.progress.skipped
        }
    
    def _download_single_paper(self, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Download a single paper using CORE API with arXiv, NCBI, and Europe PMC fallbacks"""
        # Try CORE API first
        core_result = self._try_core_api(doi, output_folder)
        if core_result['success']:
            return core_result
        
        logger.info(f"CORE failed for {doi}: {core_result.get('error', 'Unknown error')}. Trying arXiv...")
        
        # Try arXiv as second fallback
        arxiv_result = self._try_arxiv_api(doi, output_folder)
        if arxiv_result['success']:
            return arxiv_result
        
        logger.info(f"arXiv failed for {doi}: {arxiv_result.get('error', 'Unknown error')}. Trying NCBI...")
        
        # Try NCBI as third fallback
        ncbi_result = self._try_ncbi_api(doi, output_folder)
        if ncbi_result['success']:
            return ncbi_result
        
        logger.info(f"NCBI failed for {doi}: {ncbi_result.get('error', 'Unknown error')}. Trying Europe PMC...")
        
        # Try Europe PMC as fourth fallback
        europepmc_result = self._try_europepmc_api(doi, output_folder)
        if europepmc_result['success']:
            return europepmc_result
        
        # All failed, return comprehensive error
        core_error = core_result.get('error', 'CORE API failed')
        arxiv_error = arxiv_result.get('error', 'arXiv API failed')
        ncbi_error = ncbi_result.get('error', 'NCBI API failed')
        europepmc_error = europepmc_result.get('error', 'Europe PMC API failed')
        
        return {
            'success': False,
            'error': f'All sources failed - CORE: {core_error}; arXiv: {arxiv_error}; NCBI: {ncbi_error}; Europe PMC: {europepmc_error}',
            'doi': doi
        }
    
    def _try_core_api(self, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download using CORE API with retry logic"""
        max_retries = 3
        base_delay = 10  # Base delay for exponential backoff
        
        for attempt in range(max_retries + 1):
            try:
                # Search CORE API for the paper
                search_url = f"{self.config.core_base_url}/search/works"
                params = {
                    'q': f'doi:"{doi}"',
                    'limit': self.config.core_max_results,
                    'apiKey': self.config.core_api_key
                }
                
                response = self.session.get(
                    search_url, 
                    params=params, 
                    timeout=self.config.core_timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('totalHits', 0) > 0:
                    results = data.get('results', [])
                    for paper in results:
                        # Try to download the paper
                        download_result = self._try_download_paper(paper, doi, output_folder, source="CORE")
                        if download_result['success']:
                            return download_result
                    
                    return {
                        'success': False,
                        'error': 'Paper found but no downloadable PDF available',
                        'doi': doi
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Paper not found in CORE database',
                        'doi': doi
                    }
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit exceeded
                    if attempt < max_retries:
                        # Exponential backoff: 10s, 20s, 40s
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit for {doi}, waiting {delay}s before retry {attempt + 1}")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f'Rate limit exceeded after {max_retries} retries',
                            'doi': doi
                        }
                elif e.response.status_code == 500:  # Server error
                    if attempt < max_retries:
                        delay = 5  # Shorter delay for server errors
                        logger.warning(f"Server error for {doi}, waiting {delay}s before retry {attempt + 1}")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f'Server error after {max_retries} retries',
                            'doi': doi
                        }
                else:
                    return {
                        'success': False,
                        'error': f'CORE API HTTP error: {str(e)}',
                        'doi': doi
                    }
            except requests.exceptions.RequestException as e:
                return {
                    'success': False,
                    'error': f'CORE API request failed: {str(e)}',
                    'doi': doi
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'CORE download error: {str(e)}',
                    'doi': doi
                }
    
    def _try_arxiv_api(self, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download using arXiv API"""
        try:
            # Smart arXiv search - handle different DOI formats
            search_query = self._build_arxiv_search_query(doi)
            logger.info(f"Searching arXiv for {doi} with query: {search_query}")
            
            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': self.config.arxiv_max_results
            }
            
            response = self.session.get(
                self.config.arxiv_base_url,
                params=params,
                timeout=self.config.arxiv_timeout
            )
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            if not entries:
                return {
                    'success': False,
                    'error': f'Paper not found in arXiv (searched: {search_query})',
                    'doi': doi
                }
            
            # Get the first entry
            entry = entries[0]
            
            # Extract paper info
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_elem.text.strip() if title_elem is not None else 'unknown'
            
            # Get arXiv ID
            id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
            if id_elem is None:
                return {
                    'success': False,
                    'error': 'No arXiv ID found',
                    'doi': doi
                }
            
            arxiv_id = id_elem.text.split('/')[-1]  # Extract ID from URL
            
            # Get PDF link
            pdf_link = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('type') == 'application/pdf':
                    pdf_link = link.get('href')
                    break
            
            if not pdf_link:
                return {
                    'success': False,
                    'error': 'No PDF link found in arXiv entry',
                    'doi': doi
                }
            
            # Create paper metadata for download
            paper_data = {
                'title': title,
                'downloadUrl': pdf_link,
                'authors': self._extract_arxiv_authors(entry),
                'arxiv_id': arxiv_id
            }
            
            # Try to download
            return self._try_download_paper(paper_data, doi, output_folder, source="arXiv")
            
        except ET.ParseError as e:
            return {
                'success': False,
                'error': f'arXiv XML parsing error: {str(e)}',
                'doi': doi
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'arXiv API request failed: {str(e)}',
                'doi': doi
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'arXiv download error: {str(e)}',
                'doi': doi
            }
    
    def _build_arxiv_search_query(self, doi: str) -> str:
        """Build an intelligent arXiv search query based on DOI format"""
        
        # Handle arXiv DOIs (10.48550/arXiv.XXXX.XXXXX)
        if doi.startswith('10.48550/arXiv.'):
            arxiv_id = doi.replace('10.48550/arXiv.', '')
            # Search by arXiv ID directly - much more reliable
            return f'id:{arxiv_id}'
        
        # Handle other potential arXiv formats
        if 'arxiv' in doi.lower():
            # Extract potential arXiv ID patterns
            import re
            arxiv_pattern = r'(\d{4}\.\d{4,5})'
            match = re.search(arxiv_pattern, doi)
            if match:
                arxiv_id = match.group(1)
                return f'id:{arxiv_id} OR doi:{doi}'
        
        # Default: search by DOI
        return f'doi:{doi}'
    
    def _extract_arxiv_authors(self, entry) -> List[str]:
        """Extract author names from arXiv entry"""
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name_elem = author.find('{http://www.w3.org/2005/Atom}name')
            if name_elem is not None:
                authors.append(name_elem.text.strip())
        return authors
    
    def _try_ncbi_api(self, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download using NCBI E-utilities API"""
        try:
            logger.info(f"Searching NCBI for {doi}")
            
            # Step 1: Search PubMed for the DOI
            search_result = self._ncbi_search(doi)
            if not search_result['success']:
                return search_result
            
            pmid = search_result['pmid']
            logger.info(f"Found PMID {pmid} for DOI {doi}")
            
            # Step 2: Try to find full-text links
            link_result = self._ncbi_get_links(pmid)
            if not link_result['success']:
                return link_result
            
            # Step 3: Get paper metadata
            paper_info = self._ncbi_get_paper_info(pmid)
            
            # Step 4: Try to download from available sources
            for link_info in link_result['links']:
                download_result = self._try_ncbi_download(link_info, doi, output_folder, paper_info)
                if download_result['success']:
                    return download_result
            
            return {
                'success': False,
                'error': f'Paper found in NCBI (PMID: {pmid}) but no downloadable PDF available',
                'doi': doi
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'NCBI API error: {str(e)}',
                'doi': doi
            }
    
    def _ncbi_search(self, doi: str) -> Dict[str, Any]:
        """Search NCBI PubMed for a DOI"""
        try:
            search_url = f"{self.config.ncbi_base_url}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'{doi}[DOI]',
                'retmode': 'json',
                'retmax': self.config.ncbi_max_results,
                'api_key': self.config.ncbi_api_key,
                'tool': self.config.ncbi_tool,
                'email': self.config.ncbi_email
            }
            
            response = self.session.get(search_url, params=params, timeout=self.config.ncbi_timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Add rate limiting
            time.sleep(1.0 / self.config.ncbi_rate_limit)  # Respect rate limit
            
            if 'esearchresult' in data and data['esearchresult']['idlist']:
                pmid = data['esearchresult']['idlist'][0]
                return {
                    'success': True,
                    'pmid': pmid
                }
            else:
                return {
                    'success': False,
                    'error': 'Paper not found in PubMed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'PubMed search failed: {str(e)}'
            }
    
    def _ncbi_get_links(self, pmid: str) -> Dict[str, Any]:
        """Get external links for a PubMed article"""
        try:
            # Check PMC (PubMed Central) first
            pmc_links = self._ncbi_check_pmc(pmid)
            if pmc_links['success']:
                return pmc_links
            
            # Then check other external links
            link_url = f"{self.config.ncbi_base_url}/elink.fcgi"
            params = {
                'dbfrom': 'pubmed',
                'db': 'pubmed',
                'id': pmid,
                'cmd': 'llinks',
                'retmode': 'json',
                'api_key': self.config.ncbi_api_key,
                'tool': self.config.ncbi_tool,
                'email': self.config.ncbi_email
            }
            
            response = self.session.get(link_url, params=params, timeout=self.config.ncbi_timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Add rate limiting
            time.sleep(1.0 / self.config.ncbi_rate_limit)
            
            links = []
            if 'linksets' in data:
                for linkset in data['linksets']:
                    if 'iurllist' in linkset:
                        for url_info in linkset['iurllist']:
                            if 'url' in url_info:
                                links.append({
                                    'url': url_info['url'],
                                    'name': url_info.get('name', 'External Link'),
                                    'source': 'PubMed Links'
                                })
            
            if links:
                return {
                    'success': True,
                    'links': links
                }
            else:
                return {
                    'success': False,
                    'error': 'No external links found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Link retrieval failed: {str(e)}'
            }
    
    def _ncbi_check_pmc(self, pmid: str) -> Dict[str, Any]:
        """Check if article is available in PMC (PubMed Central)"""
        try:
            link_url = f"{self.config.ncbi_base_url}/elink.fcgi"
            params = {
                'dbfrom': 'pubmed',
                'db': 'pmc',
                'id': pmid,
                'retmode': 'json',
                'api_key': self.config.ncbi_api_key,
                'tool': self.config.ncbi_tool,
                'email': self.config.ncbi_email
            }
            
            response = self.session.get(link_url, params=params, timeout=self.config.ncbi_timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Add rate limiting
            time.sleep(1.0 / self.config.ncbi_rate_limit)
            
            if 'linksets' in data and data['linksets']:
                for linkset in data['linksets']:
                    if 'linksetdbs' in linkset:
                        for linksetdb in linkset['linksetdbs']:
                            if linksetdb.get('dbto') == 'pmc' and 'links' in linksetdb:
                                pmc_ids = linksetdb['links']
                                if pmc_ids:
                                    pmc_id = pmc_ids[0]
                                    return {
                                        'success': True,
                                        'links': [{
                                            'url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/",
                                            'name': 'PMC Full Text PDF',
                                            'source': 'PMC',
                                            'pmc_id': pmc_id
                                        }]
                                    }
            
            return {
                'success': False,
                'error': 'Article not available in PMC'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PMC check failed: {str(e)}'
            }
    
    def _ncbi_get_paper_info(self, pmid: str) -> Dict[str, Any]:
        """Get paper metadata from PubMed"""
        try:
            fetch_url = f"{self.config.ncbi_base_url}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml',
                'api_key': self.config.ncbi_api_key,
                'tool': self.config.ncbi_tool,
                'email': self.config.ncbi_email
            }
            
            response = self.session.get(fetch_url, params=params, timeout=self.config.ncbi_timeout)
            response.raise_for_status()
            
            # Add rate limiting
            time.sleep(1.0 / self.config.ncbi_rate_limit)
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract basic info
            title = ""
            authors = []
            
            article = root.find('.//Article')
            if article is not None:
                title_elem = article.find('.//ArticleTitle')
                if title_elem is not None:
                    title = title_elem.text or ""
                
                # Extract authors
                author_list = article.find('.//AuthorList')
                if author_list is not None:
                    for author in author_list.findall('.//Author'):
                        last_name = author.find('.//LastName')
                        first_name = author.find('.//ForeName')
                        if last_name is not None:
                            name = last_name.text or ""
                            if first_name is not None and first_name.text:
                                name = f"{first_name.text} {name}"
                            authors.append(name)
            
            return {
                'title': title[:100],  # Truncate title
                'authors': authors[:5],  # Limit authors
                'pmid': pmid
            }
            
        except Exception as e:
            logger.warning(f"Could not get paper info for PMID {pmid}: {e}")
            return {
                'title': 'Unknown',
                'authors': [],
                'pmid': pmid
            }
    
    def _try_ncbi_download(self, link_info: Dict, doi: str, output_folder: Path, paper_info: Dict) -> Dict[str, Any]:
        """Try to download from an NCBI link"""
        try:
            download_url = link_info['url']
            source_name = link_info.get('source', 'NCBI')
            
            # Create filename
            title = paper_info.get('title', 'unknown')
            safe_title = re.sub(r'[^\w\-_\.]', '_', title)
            pmid = paper_info.get('pmid', 'unknown')
            
            filename = f"{safe_title}_{pmid}_{doi.replace('/', '_')}_NCBI.pdf"
            filepath = output_folder / filename
            
            # Download the content
            response = self.session.get(download_url, timeout=self.config.download_timeout, stream=True)
            response.raise_for_status()
            
            # Check Content-Type header
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                return {
                    'success': False,
                    'error': f'NCBI link returned HTML instead of PDF (Content-Type: {content_type})',
                    'doi': doi
                }
            
            # Download and validate content
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
                    if len(content) > 1024 * 1024:  # 1MB validation limit
                        with open(filepath, 'wb') as f:
                            f.write(content)
                            for remaining_chunk in response.iter_content(chunk_size=8192):
                                if remaining_chunk:
                                    f.write(remaining_chunk)
                        break
            else:
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            # Validate PDF
            if not self._is_valid_pdf(content[:1024]):
                if filepath.exists():
                    filepath.unlink()
                return {
                    'success': False,
                    'error': 'Downloaded content from NCBI is not a valid PDF',
                    'doi': doi
                }
            
            # Verify file
            if filepath.exists() and filepath.stat().st_size > 1000:
                return {
                    'success': True,
                    'doi': doi,
                    'file_path': str(filepath),
                    'title': paper_info.get('title', ''),
                    'authors': paper_info.get('authors', []),
                    'source': f'NCBI-{source_name}',
                    'pmid': paper_info.get('pmid', '')
                }
            else:
                return {
                    'success': False,
                    'error': 'Downloaded NCBI file is empty or too small',
                    'doi': doi
                }
                
        except Exception as e:
            if 'filepath' in locals() and filepath.exists():
                try:
                    filepath.unlink()
                except:
                    pass
            return {
                'success': False,
                'error': f'NCBI download failed: {str(e)}',
                'doi': doi
            }
    
    def _try_europepmc_api(self, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download using Europe PMC API"""
        try:
            logger.info(f"Searching Europe PMC for {doi}")
            
            # Step 1: Search Europe PMC for the DOI
            search_result = self._europepmc_search(doi)
            if not search_result['success']:
                return search_result
            
            results = search_result['results']
            logger.info(f"Found {len(results)} results in Europe PMC for DOI {doi}")
            
            # Try each result until we find a downloadable one
            for paper_info in results:
                download_result = self._try_europepmc_download(paper_info, doi, output_folder)
                if download_result['success']:
                    return download_result
            
            return {
                'success': False,
                'error': f'Paper found in Europe PMC but no downloadable PDF available',
                'doi': doi
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Europe PMC API error: {str(e)}',
                'doi': doi
            }
    
    def _europepmc_search(self, doi: str) -> Dict[str, Any]:
        """Search Europe PMC for a DOI"""
        try:
            search_url = f"{self.config.europepmc_base_url}/search"
            params = {
                'query': f'DOI:"{doi}"',
                'format': self.config.europepmc_format,
                'resulttype': 'core',
                'pageSize': self.config.europepmc_max_results,
                'page': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=self.config.europepmc_timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Add rate limiting
            time.sleep(60.0 / self.config.europepmc_rate_limit)  # Convert from per-minute to delay
            
            if 'resultList' in data and data['resultList']['result']:
                results = []
                for result in data['resultList']['result']:
                    paper_info = {
                        'id': result.get('id'),
                        'pmid': result.get('pmid'),
                        'pmcid': result.get('pmcid'),
                        'doi': result.get('doi'),
                        'title': result.get('title', '')[:100],
                        'authors': self._extract_europepmc_authors(result),
                        'source': result.get('source', 'MED'),
                        'isOpenAccess': result.get('isOpenAccess', 'N'),
                        'inPMC': result.get('inPMC', 'N'),
                        'inEPMC': result.get('inEPMC', 'N'),
                        'hasTextMinedTerms': result.get('hasTextMinedTerms', 'N'),
                        'fullTextUrlList': result.get('fullTextUrlList', {})
                    }
                    results.append(paper_info)
                
                return {
                    'success': True,
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': 'Paper not found in Europe PMC'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Europe PMC search failed: {str(e)}'
            }
    
    def _extract_europepmc_authors(self, result: Dict) -> List[str]:
        """Extract author names from Europe PMC result"""
        authors = []
        
        # Try authorList first
        if 'authorList' in result and 'author' in result['authorList']:
            for author in result['authorList']['author'][:5]:  # Limit to 5 authors
                full_name = author.get('fullName', '')
                if full_name:
                    authors.append(full_name)
                else:
                    # Build name from parts
                    first_name = author.get('firstName', '')
                    last_name = author.get('lastName', '')
                    if first_name and last_name:
                        authors.append(f"{first_name} {last_name}")
                    elif last_name:
                        authors.append(last_name)
        
        # Fallback to authorString if available
        if not authors and 'authorString' in result:
            author_string = result['authorString']
            # Split by common delimiters
            if ',' in author_string:
                authors = [a.strip() for a in author_string.split(',')[:5]]
            elif ';' in author_string:
                authors = [a.strip() for a in author_string.split(';')[:5]]
            else:
                authors = [author_string]
        
        return authors
    
    def _try_europepmc_download(self, paper_info: Dict, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download from Europe PMC"""
        try:
            download_url = None
            source_name = "Europe PMC"
            
            # Priority 1: Check if paper is in PMC (highest quality)
            if paper_info.get('inPMC') == 'Y' and paper_info.get('pmcid'):
                pmcid = paper_info['pmcid']
                if pmcid.startswith('PMC'):
                    pmcid = pmcid[3:]  # Remove PMC prefix
                
                # Try PMC full text XML endpoint
                xml_url = f"{self.config.europepmc_base_url}/{pmcid}/fullTextXML"
                xml_result = self._try_europepmc_xml_download(xml_url, paper_info, doi, output_folder)
                if xml_result['success']:
                    return xml_result
            
            # Priority 2: Check fullTextUrlList for PDF links
            full_text_urls = paper_info.get('fullTextUrlList', {})
            if 'fullTextUrl' in full_text_urls:
                for url_info in full_text_urls['fullTextUrl']:
                    if url_info.get('documentStyle') == 'pdf' or url_info.get('availabilityCode') == 'OA':
                        download_url = url_info.get('url')
                        source_name = f"Europe PMC-{url_info.get('site', 'PDF')}"
                        break
            
            # Priority 3: Try to construct PMC PDF URL if we have PMCID
            if not download_url and paper_info.get('pmcid'):
                pmcid = paper_info['pmcid']
                if pmcid.startswith('PMC'):
                    pmcid = pmcid[3:]
                download_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/"
                source_name = "Europe PMC-PMC"
            
            if download_url:
                return self._download_europepmc_pdf(download_url, paper_info, doi, output_folder, source_name)
            
            return {
                'success': False,
                'error': 'No downloadable PDF URL found in Europe PMC',
                'doi': doi
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Europe PMC download failed: {str(e)}',
                'doi': doi
            }
    
    def _try_europepmc_xml_download(self, xml_url: str, paper_info: Dict, doi: str, output_folder: Path) -> Dict[str, Any]:
        """Try to download XML from Europe PMC and convert or save as alternative"""
        try:
            response = self.session.get(xml_url, timeout=self.config.europepmc_timeout)
            response.raise_for_status()
            
            # Check if we got XML content
            content_type = response.headers.get('content-type', '').lower()
            if 'xml' not in content_type and 'text' not in content_type:
                return {
                    'success': False,
                    'error': 'Europe PMC XML endpoint did not return XML content'
                }
            
            # Save as XML file (alternative format)
            title = paper_info.get('title', 'unknown')
            safe_title = re.sub(r'[^\w\-_\.]', '_', title)
            pmcid = paper_info.get('pmcid', 'unknown')
            
            filename = f"{safe_title}_{pmcid}_{doi.replace('/', '_')}_EuropePMC.xml"
            filepath = output_folder / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            if filepath.exists() and filepath.stat().st_size > 1000:
                return {
                    'success': True,
                    'doi': doi,
                    'file_path': str(filepath),
                    'title': paper_info.get('title', ''),
                    'authors': paper_info.get('authors', []),
                    'source': 'Europe PMC-XML',
                    'pmcid': paper_info.get('pmcid', ''),
                    'note': 'Downloaded as XML - full text available'
                }
            else:
                return {
                    'success': False,
                    'error': 'Europe PMC XML file is empty or too small'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Europe PMC XML download failed: {str(e)}'
            }
    
    def _download_europepmc_pdf(self, download_url: str, paper_info: Dict, doi: str, output_folder: Path, source_name: str) -> Dict[str, Any]:
        """Download PDF from Europe PMC URL"""
        try:
            # Create filename
            title = paper_info.get('title', 'unknown')
            safe_title = re.sub(r'[^\w\-_\.]', '_', title)
            pmcid = paper_info.get('pmcid', '')
            pmid = paper_info.get('pmid', '')
            
            identifier = pmcid if pmcid else (pmid if pmid else 'unknown')
            filename = f"{safe_title}_{identifier}_{doi.replace('/', '_')}_EuropePMC.pdf"
            filepath = output_folder / filename
            
            # Download the content
            response = self.session.get(download_url, timeout=self.config.download_timeout, stream=True)
            response.raise_for_status()
            
            # Check Content-Type header
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                return {
                    'success': False,
                    'error': f'Europe PMC link returned HTML instead of PDF (Content-Type: {content_type})',
                    'doi': doi
                }
            
            # Download and validate content
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
                    if len(content) > 1024 * 1024:  # 1MB validation limit
                        with open(filepath, 'wb') as f:
                            f.write(content)
                            for remaining_chunk in response.iter_content(chunk_size=8192):
                                if remaining_chunk:
                                    f.write(remaining_chunk)
                        break
            else:
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            # Validate PDF
            if not self._is_valid_pdf(content[:1024]):
                if filepath.exists():
                    filepath.unlink()
                return {
                    'success': False,
                    'error': 'Downloaded content from Europe PMC is not a valid PDF',
                    'doi': doi
                }
            
            # Verify file
            if filepath.exists() and filepath.stat().st_size > 1000:
                return {
                    'success': True,
                    'doi': doi,
                    'file_path': str(filepath),
                    'title': paper_info.get('title', ''),
                    'authors': paper_info.get('authors', []),
                    'source': source_name,
                    'pmcid': paper_info.get('pmcid', ''),
                    'pmid': paper_info.get('pmid', '')
                }
            else:
                return {
                    'success': False,
                    'error': 'Downloaded Europe PMC file is empty or too small',
                    'doi': doi
                }
                
        except Exception as e:
            if 'filepath' in locals() and filepath.exists():
                try:
                    filepath.unlink()
                except:
                    pass
            return {
                'success': False,
                'error': f'Europe PMC PDF download failed: {str(e)}',
                'doi': doi
            }
    
    def _try_download_paper(self, paper: Dict, doi: str, output_folder: Path, source: str = "CORE") -> Dict[str, Any]:
        """Try to download a paper from CORE or arXiv data"""
        try:
            # Get download URL
            download_url = paper.get('downloadUrl')
            if not download_url:
                # Try repository document
                repo_doc = paper.get('repositoryDocument', {})
                download_url = repo_doc.get('pdfOrigin')
            
            if not download_url:
                return {
                    'success': False,
                    'error': 'No download URL available',
                    'doi': doi
                }
            
            # Create filename
            title = paper.get('title', 'unknown')[:50]  # Truncate title
            safe_title = re.sub(r'[^\w\-_\.]', '_', title)
            
            # Include source and arXiv ID if available
            source_suffix = f"_{source}"
            if source == "arXiv" and paper.get('arxiv_id'):
                arxiv_id = paper.get('arxiv_id').replace('/', '_')
                filename = f"{safe_title}_{arxiv_id}_{doi.replace('/', '_')}{source_suffix}.pdf"
            else:
                filename = f"{safe_title}_{doi.replace('/', '_')}{source_suffix}.pdf"
            filepath = output_folder / filename
            
            # Download the content
            pdf_response = self.session.get(
                download_url, 
                timeout=self.config.download_timeout,
                stream=True
            )
            pdf_response.raise_for_status()
            
            # Check Content-Type header first
            content_type = pdf_response.headers.get('content-type', '').lower()
            if 'text/html' in content_type or 'text/plain' in content_type:
                return {
                    'success': False,
                    'error': f'Download URL returned HTML/text instead of PDF (Content-Type: {content_type})',
                    'doi': doi
                }
            
            # Download content to memory first for validation
            content = b''
            for chunk in pdf_response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
                    # Stop if we've read enough to validate (first 1MB)
                    if len(content) > 1024 * 1024:
                        # Still download the rest to a file
                        with open(filepath, 'wb') as f:
                            f.write(content)
                            for remaining_chunk in pdf_response.iter_content(chunk_size=8192):
                                if remaining_chunk:
                                    f.write(remaining_chunk)
                        break
            else:
                # Small file, we have all content in memory
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            # Validate that it's actually a PDF file
            if not self._is_valid_pdf(content[:1024]):  # Check first 1KB
                # Remove the invalid file
                if filepath.exists():
                    filepath.unlink()
                return {
                    'success': False,
                    'error': 'Downloaded content is not a valid PDF (likely HTML/text from publisher paywall)',
                    'doi': doi
                }
            
            # Verify the file was saved and has reasonable size
            if filepath.exists() and filepath.stat().st_size > 1000:  # At least 1KB
                return {
                    'success': True,
                    'doi': doi,
                    'file_path': str(filepath),
                    'title': paper.get('title', ''),
                    'authors': paper.get('authors', []),
                    'source': source,
                    'arxiv_id': paper.get('arxiv_id', '') if source == "arXiv" else ''
                }
            else:
                return {
                    'success': False,
                    'error': 'Downloaded file is empty or too small to be a valid PDF',
                    'doi': doi
                }
                
        except Exception as e:
            # Clean up any partially downloaded file
            if 'filepath' in locals() and filepath.exists():
                try:
                    filepath.unlink()
                except:
                    pass
            return {
                'success': False,
                'error': f'PDF download failed: {str(e)}',
                'doi': doi
            }
    
    def _is_valid_pdf(self, content: bytes) -> bool:
        """Check if content starts with PDF magic bytes and is not HTML"""
        if not content or len(content) < 4:
            return False
        
        # Check for PDF magic bytes
        if content.startswith(b'%PDF-'):
            return True
        
        # Check for common HTML indicators (case insensitive)
        content_lower = content.lower()
        html_indicators = [
            b'<!doctype html',
            b'<html',
            b'<head>',
            b'<title>',
            b'<body>',
            b'<h1>',
            b'<div>',
            b'<p>',
            b'text/html'
        ]
        
        for indicator in html_indicators:
            if indicator in content_lower:
                return False
        
        # Additional check for common error pages
        error_indicators = [
            b'access denied',
            b'unauthorized',
            b'login required',
            b'subscription required',
            b'paywall',
            b'not available',
            b'error 403',
            b'error 404'
        ]
        
        for indicator in error_indicators:
            if indicator in content_lower:
                return False
        
        return True
    
    def get_progress(self) -> DownloadProgress:
        """Get current download progress"""
        return self.progress
    
    def set_stop_flag(self):
        """Stop the current download process"""
        self.stop_flag = True
        self.progress.status = "stopping"
        logger.info("Download stop requested")
    
    def clear_progress(self):
        """Clear current progress tracking"""
        self.progress = DownloadProgress()
        self.stop_flag = False
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get comprehensive download statistics"""
        return {
            'total_downloaded': len(self.downloaded_dois),
            'total_failed': len(self.failed_dois),
            'current_session': self.progress.to_dict(),
            'last_update': datetime.now().isoformat()
        }
    
    def _get_downloaded_dois(self) -> Set[str]:
        """Get set of successfully downloaded DOIs"""
        return self.downloaded_dois
    
    def _get_failed_dois(self) -> Set[str]:
        """Get set of failed DOIs"""
        return self.failed_dois
    
    def clear_all_tracking(self) -> int:
        """Clear all tracking data"""
        total_cleared = len(self.downloaded_dois) + len(self.failed_dois)
        self.downloaded_dois.clear()
        self.failed_dois.clear()
        self._save_tracking_data()
        return total_cleared
    
    def _load_tracking_data(self):
        """Load tracking data from disk"""
        try:
            # Load downloaded DOIs
            downloaded_file = self.config.data_dir / "downloaded_library.txt"
            if downloaded_file.exists():
                with open(downloaded_file, 'r', encoding='utf-8') as f:
                    self.downloaded_dois = set(line.strip() for line in f if line.strip())
            
            # Load failed DOIs
            failed_file = self.config.data_dir / "failed_dois.txt"
            if failed_file.exists():
                with open(failed_file, 'r', encoding='utf-8') as f:
                    self.failed_dois = set(line.strip() for line in f if line.strip())
                    
        except Exception as e:
            logger.error(f"Error loading tracking data: {e}")
    
    def _save_tracking_data(self):
        """Save tracking data to disk"""
        try:
            # Save downloaded DOIs
            downloaded_file = self.config.data_dir / "downloaded_library.txt"
            with open(downloaded_file, 'w', encoding='utf-8') as f:
                for doi in sorted(self.downloaded_dois):
                    f.write(f"{doi}\n")
            
            # Save failed DOIs
            failed_file = self.config.data_dir / "failed_dois.txt"
            with open(failed_file, 'w', encoding='utf-8') as f:
                for doi in sorted(self.failed_dois):
                    f.write(f"{doi}\n")
                    
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")

    # Legacy method for compatibility
    def download_paper(self, doi: str, output_dir: Path, progress_callback=None) -> Dict[str, Any]:
        """
        Download a single paper (legacy compatibility method)
        
        Args:
            doi: DOI of the paper
            output_dir: Directory to save the paper
            progress_callback: Callback function for progress updates
            
        Returns:
            Dict with download result
        """
        return self._download_single_paper(doi, output_dir)
        
    def _try_source(self, doi: str, source_url: str, output_dir: Path, progress_callback=None) -> Dict[str, Any]:
        """Try to download from a specific legal source (legacy compatibility)"""
        # This now uses CORE API instead of the old placeholder
        return self._download_single_paper(doi, output_dir)
    
    def _extract_pdf_url(self, html_content: str, base_url: str) -> Optional[str]:
        """Extract PDF URL from legal repository page HTML (legacy compatibility)"""
        # This method is no longer needed with CORE API integration
        return None 