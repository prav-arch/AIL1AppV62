"""
Web Scraper with Advanced Error Handling
This module provides robust web scraping functionality with SSL error handling
and fallback mechanisms specifically designed for ClickHouse 18.16.1
"""

import requests
import logging
import json
import trafilatura
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import ssl
import time
import random
from typing import Dict, Any, List, Tuple, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress only the specific InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WebScraper:
    """Web scraper with enhanced error handling and SSL workarounds"""
    
    def __init__(self, user_agent=None, timeout=30, max_retries=3, retry_delay=2):
        """Initialize the web scraper"""
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.session = self._create_session()
    
    def _create_session(self):
        """Create a requests session with predefined headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def extract_content(self, url: str, ignore_ssl_errors=True) -> Dict[str, Any]:
        """
        Extract content from a URL with retries and error handling
        
        Args:
            url: The URL to scrape
            ignore_ssl_errors: Whether to ignore SSL certificate errors
            
        Returns:
            Dictionary with extracted content and metadata
        """
        url = url.strip()
        logger.info(f"Extracting content from {url}")
        
        # Parse domain from URL
        domain = urlparse(url).netloc
        
        # Try multiple methods to fetch the content
        content = None
        error = None
        
        for attempt in range(self.max_retries):
            try:
                # Try trafilatura first (gives best results for most pages)
                logger.info(f"Attempt {attempt+1}/{self.max_retries} using trafilatura")
                downloaded = trafilatura.fetch_url(url, timeout=self.timeout)
                if downloaded:
                    content = trafilatura.extract(downloaded, include_comments=False, include_tables=True, 
                                                 include_images=True, include_links=True, output_format='txt')
                    
                    if content and len(content.strip()) > 100:  # Consider it successful if we got meaningful content
                        logger.info(f"Successfully extracted content with trafilatura (length: {len(content)})")
                        break
            
            except Exception as e:
                logger.warning(f"Error with trafilatura: {e}")
                # Continue to next method
            
            if not content or len(content.strip()) < 100:
                try:
                    # Try with requests as fallback
                    logger.info(f"Attempt {attempt+1}/{self.max_retries} using requests")
                    verify = not ignore_ssl_errors
                    response = self.session.get(url, timeout=self.timeout, verify=verify)
                    response.raise_for_status()
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title
                    title = soup.title.string if soup.title else ""
                    
                    # Extract main content (remove scripts, styles, etc.)
                    for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                        script.extract()
                    
                    # Get text content
                    content = soup.get_text(separator='\n', strip=True)
                    
                    if content and len(content.strip()) > 100:
                        logger.info(f"Successfully extracted content with requests/BeautifulSoup (length: {len(content)})")
                        break
                
                except requests.exceptions.SSLError:
                    if ignore_ssl_errors:
                        logger.warning(f"SSL Error with {url}, retrying with SSL verification disabled")
                        try:
                            # Retry with SSL verification disabled
                            response = self.session.get(url, timeout=self.timeout, verify=False)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.content, 'html.parser')
                            content = soup.get_text(separator='\n', strip=True)
                            
                            if content and len(content.strip()) > 100:
                                logger.info(f"Successfully extracted content with SSL verification disabled (length: {len(content)})")
                                break
                        except Exception as e:
                            logger.warning(f"Error with SSL verification disabled: {e}")
                            error = str(e)
                
                except Exception as e:
                    logger.warning(f"Error with requests: {e}")
                    error = str(e)
            
            # If we reached here, the attempt failed. Wait before retrying
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (attempt + 1) + random.uniform(0, 1)
                logger.info(f"Waiting {delay:.2f} seconds before next attempt...")
                time.sleep(delay)
        
        # If all attempts failed, return an error
        if not content or len(content.strip()) < 100:
            logger.error(f"Failed to extract content from {url} after {self.max_retries} attempts")
            return {
                'url': url,
                'success': False,
                'error': error or "Failed to extract meaningful content",
                'content': None,
                'title': None,
                'domain': domain,
                'metadata': {'url': url, 'error': error}
            }
        
        # Clean up the content a bit
        content = self._clean_content(content)
        
        # Extract title from the URL if we don't have it
        if 'title' not in locals() or not title:
            # Try to get title from the last part of the URL path
            path = urlparse(url).path
            if path and path != '/':
                title = path.strip('/').split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            else:
                title = domain
        
        return {
            'url': url,
            'success': True,
            'content': content,
            'title': title,
            'domain': domain,
            'metadata': {
                'url': url,
                'domain': domain,
                'title': title,
                'length': len(content)
            }
        }
    
    def _clean_content(self, text: str) -> str:
        """Clean extracted content to improve quality"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        # Remove duplicate lines that often appear in scraped content
        unique_lines = []
        prev_line = None
        for line in lines:
            if line != prev_line:
                unique_lines.append(line)
                prev_line = line
        
        # Join back with newlines
        cleaned_text = '\n'.join(unique_lines)
        
        # Limit to a reasonable size (10 MB)
        if len(cleaned_text) > 10 * 1024 * 1024:
            cleaned_text = cleaned_text[:10 * 1024 * 1024]
            logger.warning(f"Content truncated to 10 MB")
        
        return cleaned_text
    
    def extract_links(self, url: str, max_links: int = 10) -> List[str]:
        """
        Extract links from a URL
        
        Args:
            url: The URL to extract links from
            max_links: Maximum number of links to extract
            
        Returns:
            List of URLs found on the page
        """
        try:
            verify = False  # Ignore SSL errors by default for link extraction
            response = self.session.get(url, timeout=self.timeout, verify=verify)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            base_url = urlparse(url)
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                
                # Skip empty links, anchors, and javascript
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                # Handle relative URLs
                if not href.startswith(('http://', 'https://')):
                    if href.startswith('/'):
                        href = f"{base_url.scheme}://{base_url.netloc}{href}"
                    else:
                        href = f"{base_url.scheme}://{base_url.netloc}/{href}"
                
                # Add to list if unique
                if href not in links:
                    links.append(href)
                
                # Stop when we reach max_links
                if len(links) >= max_links:
                    break
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {e}")
            return []
    
    def bulk_extract(self, urls: List[str], ignore_ssl_errors=True) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs
        
        Args:
            urls: List of URLs to scrape
            ignore_ssl_errors: Whether to ignore SSL certificate errors
            
        Returns:
            List of dictionaries with extracted content and metadata
        """
        results = []
        for url in urls:
            try:
                result = self.extract_content(url, ignore_ssl_errors)
                results.append(result)
            except Exception as e:
                logger.error(f"Error extracting content from {url}: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'content': None,
                    'title': None,
                    'domain': urlparse(url).netloc,
                    'metadata': {'url': url, 'error': str(e)}
                })
        
        return results


class TextProcessor:
    """Process text into chunks for embedding and storage"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split into chunks
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Clean the text
        text = TextProcessor.clean_text(text)
        
        # Split text by paragraphs first
        paragraphs = text.split('\n')
        paragraphs = [p for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            # If paragraph is too big, split it into sentences
            if len(paragraph) > chunk_size:
                sentences = TextProcessor._split_into_sentences(paragraph)
                for sentence in sentences:
                    if current_size + len(sentence) <= chunk_size:
                        current_chunk.append(sentence)
                        current_size += len(sentence)
                    else:
                        # Current chunk is full, add it to chunks
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                        
                        # Start a new chunk with overlap
                        overlap_start = max(0, len(current_chunk) - chunk_overlap // len(current_chunk[0]) if current_chunk else 0)
                        current_chunk = current_chunk[overlap_start:] + [sentence]
                        current_size = sum(len(s) for s in current_chunk)
            else:
                # If adding this paragraph would exceed chunk size, save current chunk and start a new one
                if current_size + len(paragraph) > chunk_size:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    
                    # Start a new chunk with overlap
                    overlap_start = max(0, len(current_chunk) - chunk_overlap // len(current_chunk[0]) if current_chunk else 0)
                    current_chunk = current_chunk[overlap_start:] + [paragraph]
                    current_size = sum(len(s) for s in current_chunk)
                else:
                    current_chunk.append(paragraph)
                    current_size += len(paragraph)
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Handle case where chunks might still be too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Further split this chunk
                sub_chunks = TextProcessor._split_chunk(chunk, chunk_size, chunk_overlap // 2)
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - not perfect but works for most cases
        # For a more advanced solution, consider using nltk or spacy
        import re
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def _split_chunk(text: str, max_size: int, overlap: int) -> List[str]:
        """Split a large chunk into smaller pieces with overlap"""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a good break point
            break_point = text.rfind(' ', start + max_size // 2, end)
            if break_point == -1:
                break_point = end
            
            chunks.append(text[start:break_point])
            start = break_point - overlap
            if start < 0:
                start = 0
        
        return chunks
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text to improve embedding quality"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Replace multiple newlines with single newline
        import re
        text = re.sub(r'\n+', '\n', text)
        
        # Remove unusual characters but keep unicode for international text
        text = re.sub(r'[^\w\s\p{P}\p{S}\p{M}\n]', '', text, flags=re.UNICODE)
        
        return text


# Example usage
if __name__ == "__main__":
    # Test the scraper
    scraper = WebScraper()
    url = "https://en.wikipedia.org/wiki/ClickHouse"
    result = scraper.extract_content(url)
    
    if result['success']:
        print(f"Title: {result['title']}")
        print(f"Content length: {len(result['content'])}")
        print(f"First 500 chars: {result['content'][:500]}...")
        
        # Test chunking
        chunks = TextProcessor.chunk_text(result['content'])
        print(f"Split into {len(chunks)} chunks")
        print(f"First chunk: {chunks[0][:200]}...")
    else:
        print(f"Error: {result['error']}")