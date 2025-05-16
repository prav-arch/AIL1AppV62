"""
Simplified Web Scraper Service
This module provides robust web scraping functionality without signal handling issues
"""

import requests
import logging
import time
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

class WebScraperService:
    """Safe web scraper service for multi-threaded Flask environments"""
    
    def __init__(self, user_agent=None, timeout=30, max_retries=3, retry_delay=2):
        """Initialize the web scraper service"""
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
    
    def scrape_url(self, url, ignore_ssl_errors=True):
        """
        Scrape content from a URL using multiple fallback mechanisms
        
        Args:
            url: The URL to scrape
            ignore_ssl_errors: Whether to ignore SSL certificate errors
            
        Returns:
            dict: A dictionary containing the scraped content and metadata
        """
        domain = urlparse(url).netloc
        
        # Track content extraction success
        content = None
        title = None
        extraction_method = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping attempt {attempt+1}/{self.max_retries} for {url}")
                
                # Set SSL verification based on parameter
                verify = not ignore_ssl_errors
                
                # Get the raw HTML content
                response = self.session.get(url, timeout=self.timeout, verify=verify)
                response.raise_for_status()
                html_content = response.text
                
                # First try using BeautifulSoup with careful extraction
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.text.strip() if title_tag else domain
                
                # Extract main content (remove scripts, styles, etc.)
                for tag in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav', 'iframe']):
                    tag.decompose()
                
                # Try to extract main content area if present
                main_content = None
                
                # Look for common main content containers
                for container in ['main', 'article', '#content', '.content', '#main', '.main']:
                    if container.startswith('#'):
                        element = soup.find(id=container[1:])
                    elif container.startswith('.'):
                        element = soup.find(class_=container[1:])
                    else:
                        element = soup.find(container)
                    
                    if element:
                        main_content = element.get_text(separator='\n', strip=True)
                        break
                
                # If no main content area found, extract body content
                if not main_content or len(main_content) < 100:
                    body = soup.find('body')
                    if body:
                        main_content = body.get_text(separator='\n', strip=True)
                
                # Clean up content
                if main_content:
                    # Remove excessive whitespace
                    content = '\n'.join(line.strip() for line in main_content.splitlines() if line.strip())
                    extraction_method = 'beautifulsoup'
                    
                    # If content is long enough, consider it a success
                    if len(content) > 200:
                        logger.info(f"Successfully extracted content with BeautifulSoup (length: {len(content)})")
                        break
                
                # If we couldn't extract meaningful content, try a more aggressive approach
                if not content or len(content) < 200:
                    # Extract all paragraph text
                    paragraphs = soup.find_all('p')
                    paragraph_text = '\n\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                    
                    if paragraph_text and len(paragraph_text) > 200:
                        content = paragraph_text
                        extraction_method = 'paragraphs'
                        logger.info(f"Extracted content from paragraphs (length: {len(content)})")
                        break
            
            except requests.exceptions.SSLError as ssl_error:
                logger.warning(f"SSL Error with {url}: {ssl_error}")
                if ignore_ssl_errors:
                    # Already ignoring SSL errors, try again with a delay
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # Return error information
                    return {
                        'success': False,
                        'error': f'SSL certificate error: {str(ssl_error)}',
                        'url': url
                    }
            
            except requests.exceptions.RequestException as req_error:
                logger.warning(f"Request error with {url}: {req_error}")
                time.sleep(self.retry_delay)
                continue
            
            # If we've tried all methods and still don't have content, wait and try again
            time.sleep(self.retry_delay)
        
        # If we couldn't extract content after all attempts
        if not content or len(content) < 100:
            logger.warning(f"Failed to extract meaningful content from {url}")
            return {
                'success': False,
                'error': 'Could not extract meaningful content from the webpage',
                'url': url
            }
        
        # Return the successfully extracted content
        return {
            'success': True,
            'url': url,
            'domain': domain,
            'title': title,
            'content': content,
            'length': len(content),
            'extraction_method': extraction_method
        }

# Create a singleton instance
scraper_service = WebScraperService()