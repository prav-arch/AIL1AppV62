#!/usr/bin/env python3
"""
Web page scraper and vector indexer using PostgreSQL with pgvector
This script demonstrates:
1. Scraping content from web pages
2. Chunking the content into manageable pieces
3. Generating embeddings for each chunk
4. Storing them in PostgreSQL with pgvector
5. Performing similarity searches
"""

import os
import re
import json
import time
import logging
import numpy as np
import psycopg2
import requests
from psycopg2.extras import Json, execute_values
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    'dbname': 'l1_app_db',
    'user': 'l1_app_user',
    'password': 'test',
    'host': 'localhost',
    'port': '5432'
}

# Vector dimension for embeddings
VECTOR_DIM = 384

class WebScraper:
    """Class for scraping web pages and extracting content"""
    
    @staticmethod
    def extract_content(url, ignore_ssl_errors=False):
        """
        Extract content from a web page
        
        Args:
            url: URL to scrape
            ignore_ssl_errors: Whether to ignore SSL certificate errors
            
        Returns:
            tuple: (title, content, metadata)
        """
        try:
            # Set up request options
            request_options = {}
            if ignore_ssl_errors:
                request_options['verify'] = False
                
            # Send request to the URL
            logger.info(f"Fetching content from {url}")
            response = requests.get(url, **request_options, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Extract main content
            # First try with article tag
            content = ""
            article = soup.find('article')
            if article:
                content = article.get_text(separator='\n', strip=True)
            
            # If no article tag or content is too short, get body content
            if not content or len(content) < 100:
                # Get main content (excluding headers, footers, navigations, etc.)
                main_content = soup.find('main') or soup.find('div', {'id': 'content'}) or soup.find('div', {'class': 'content'})
                if main_content:
                    content = main_content.get_text(separator='\n', strip=True)
                else:
                    # Fallback to body minus some common tags
                    for tag in soup(['header', 'footer', 'nav', 'aside', 'script', 'style']):
                        tag.decompose()
                    content = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
            
            # Build metadata
            domain = urlparse(url).netloc
            metadata = {
                'url': url,
                'domain': domain,
                'title': title,
                'scrape_time': datetime.now().isoformat(),
                'content_length': len(content)
            }
            
            return title, content, metadata
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Certificate Error: {str(e)}")
            logger.info("You can ignore SSL certificate errors by setting ignore_ssl_errors=True")
            raise
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise

class TextProcessor:
    """Class for processing text into chunks"""
    
    @staticmethod
    def chunk_text(text, chunk_size=1000, chunk_overlap=200):
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split into chunks
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # If text is shorter than chunk_size, return it as a single chunk
        if len(text) <= chunk_size:
            return [text]
        
        # Split text into chunks
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good boundary (newline or period)
            if end < len(text):
                # Look for a newline or period to end the chunk
                for i in range(min(100, chunk_overlap)):
                    if end - i > start and (text[end - i] == '\n' or text[end - i] == '.'):
                        end = end - i + 1  # Include the newline or period
                        break
            
            # Add the chunk
            chunks.append(text[start:end])
            
            # Move to the next chunk, with overlap
            start = end - chunk_overlap
            
            # Make sure we're making progress
            if start >= end:
                start = end
        
        return chunks
    
    @staticmethod
    def clean_text(text):
        """
        Clean text to improve embedding quality
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Replace multiple newlines with single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        return text.strip()
    
    @staticmethod
    def generate_embeddings(text):
        """
        Generate embeddings for text
        
        In a real application, you would use a pre-trained model like:
        - SentenceTransformers
        - OpenAI Embeddings API
        - Hugging Face models
        
        For this example, we'll use a mock implementation
        that creates reproducible random vectors based on the text hash
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            Embeddings vector
        """
        # For consistency, use the hash of the text to seed the random generator
        np.random.seed(hash(text) % 2**32)
        
        # Generate a random vector of the right dimension
        vector = np.random.rand(VECTOR_DIM).astype(np.float32)
        
        # Normalize to unit length
        vector = vector / np.linalg.norm(vector)
        
        return vector

class PgVectorDatabase:
    """Class for interacting with PostgreSQL + pgvector"""
    
    def __init__(self, db_params=None, vector_dim=VECTOR_DIM):
        """
        Initialize the PostgreSQL vector database service
        
        Args:
            db_params: Database connection parameters
            vector_dim: Dimension of the vectors (default: 384)
        """
        self.db_params = db_params or DB_PARAMS
        self.vector_dim = vector_dim
        self.conn = None
        
        # Initialize database
        self._initialize_db()
    
    def _get_connection(self):
        """
        Get a database connection
        
        Returns:
            psycopg2 connection object
        """
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                dbname=self.db_params['dbname'],
                user=self.db_params['user'],
                password=self.db_params['password'],
                host=self.db_params['host'],
                port=self.db_params['port']
            )
        return self.conn
    
    def _initialize_db(self):
        """Initialize the database with the required tables and extension"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check and create pgvector extension
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                logger.info("pgvector extension created or already exists")
            except Exception as e:
                logger.error(f"Error creating pgvector extension: {str(e)}")
                if conn:
                    conn.rollback()
                raise
            
            # Create web pages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS web_pages (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    domain TEXT,
                    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                );
            """)
            
            # Create page chunks table with vector support
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS page_chunks (
                    id SERIAL PRIMARY KEY,
                    page_id INTEGER REFERENCES web_pages(id) ON DELETE CASCADE,
                    chunk_index INTEGER,
                    chunk_text TEXT NOT NULL,
                    embedding vector({self.vector_dim}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(page_id, chunk_index)
                );
            """)
            
            # Create index on the vector column
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS page_chunks_embedding_idx 
                    ON page_chunks 
                    USING ivfflat (embedding vector_l2_ops)
                    WITH (lists = 100);
                """)
            except Exception as e:
                logger.warning(f"Could not create vector index, continuing without it: {str(e)}")
                if conn:
                    conn.rollback()
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            if conn:
                conn.rollback()
            raise
    
    def add_webpage(self, url, title, content, metadata=None):
        """
        Add a webpage to the database
        
        Args:
            url: URL of the webpage
            title: Title of the webpage
            content: Content of the webpage
            metadata: Additional metadata
            
        Returns:
            int: ID of the inserted webpage
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert webpage if not exists
            cursor.execute("""
                INSERT INTO web_pages (url, title, domain, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET
                    title = EXCLUDED.title,
                    metadata = EXCLUDED.metadata,
                    scrape_time = CURRENT_TIMESTAMP
                RETURNING id;
            """, (
                url,
                title,
                urlparse(url).netloc,
                Json(metadata or {})
            ))
            
            page_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Added webpage {url} with ID {page_id}")
            return page_id
            
        except Exception as e:
            logger.error(f"Error adding webpage: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def add_chunks(self, page_id, chunks):
        """
        Add content chunks to the database
        
        Args:
            page_id: ID of the webpage
            chunks: List of text chunks
            
        Returns:
            int: Number of chunks added
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Clean the chunk
                cleaned_chunk = TextProcessor.clean_text(chunk)
                
                # Skip empty chunks
                if not cleaned_chunk:
                    continue
                
                # Generate embedding
                embedding = TextProcessor.generate_embeddings(cleaned_chunk)
                
                # Insert chunk
                cursor.execute("""
                    INSERT INTO page_chunks (page_id, chunk_index, chunk_text, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (page_id, chunk_index) DO UPDATE SET
                        chunk_text = EXCLUDED.chunk_text,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """, (
                    page_id,
                    i,
                    cleaned_chunk,
                    embedding.tolist(),
                    Json({'index': i, 'length': len(cleaned_chunk)})
                ))
            
            conn.commit()
            
            logger.info(f"Added {len(chunks)} chunks for page ID {page_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def search(self, query, top_k=5):
        """
        Search the vector database for chunks similar to the query
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = TextProcessor.generate_embeddings(query)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Search using vector similarity
            cursor.execute("""
                SELECT 
                    pc.id as chunk_id,
                    pc.page_id,
                    wp.url,
                    wp.title,
                    pc.chunk_text,
                    pc.embedding <-> %s as distance
                FROM 
                    page_chunks pc
                JOIN 
                    web_pages wp ON pc.page_id = wp.id
                ORDER BY 
                    distance ASC
                LIMIT %s
            """, (query_embedding.tolist(), top_k))
            
            results = []
            for row in cursor.fetchall():
                chunk_id, page_id, url, title, text, distance = row
                
                # Calculate similarity score (lower distance = higher similarity)
                similarity = 1.0 / (1.0 + float(distance))
                
                results.append({
                    'chunk_id': chunk_id,
                    'page_id': page_id,
                    'url': url,
                    'title': title,
                    'text': text,
                    'similarity': similarity
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            return []
    
    def get_stats(self):
        """
        Get statistics about the vector database
        
        Returns:
            Dictionary of statistics
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {
                'webpages_count': 0,
                'chunks_count': 0,
                'vector_dim': self.vector_dim,
                'total_text_size': '0 KB'
            }
            
            # Get webpage count
            cursor.execute("SELECT COUNT(*) FROM web_pages")
            stats['webpages_count'] = cursor.fetchone()[0]
            
            # Get chunk count
            cursor.execute("SELECT COUNT(*) FROM page_chunks")
            stats['chunks_count'] = cursor.fetchone()[0]
            
            # Get total text size
            cursor.execute("SELECT SUM(LENGTH(chunk_text)) FROM page_chunks")
            text_size = cursor.fetchone()[0] or 0
            stats['total_text_size'] = f"{text_size / 1024:.2f} KB"
            
            # Get size information
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('web_pages')) as webpages_size,
                    pg_size_pretty(pg_total_relation_size('page_chunks')) as chunks_size
            """)
            size_info = cursor.fetchone()
            if size_info:
                stats['webpages_size'] = size_info[0]
                stats['chunks_size'] = size_info[1]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector database stats: {str(e)}")
            return {
                'error': str(e),
                'webpages_count': 0,
                'chunks_count': 0
            }
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

def scrape_and_index_webpage(url, db, ignore_ssl_errors=False):
    """
    Scrape a webpage and index its content
    
    Args:
        url: URL to scrape
        db: Database instance
        ignore_ssl_errors: Whether to ignore SSL certificate errors
        
    Returns:
        dict: Result information
    """
    start_time = time.time()
    
    try:
        # Scrape the webpage
        title, content, metadata = WebScraper.extract_content(url, ignore_ssl_errors)
        
        # Add webpage to database
        page_id = db.add_webpage(url, title, content, metadata)
        
        # Chunk the content
        chunks = TextProcessor.chunk_text(content)
        logger.info(f"Split content into {len(chunks)} chunks")
        
        # Add chunks to database
        num_chunks = db.add_chunks(page_id, chunks)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return {
            'success': True,
            'page_id': page_id,
            'url': url,
            'title': title,
            'chunks': num_chunks,
            'processing_time': f"{processing_time:.2f}s"
        }
        
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        return {
            'success': False,
            'url': url,
            'error': str(e)
        }

def main():
    """Main function to demonstrate web scraping and vector indexing"""
    logger.info("Web Scraping and Vector Indexing Example\n")
    
    # Create database instance
    try:
        db = PgVectorDatabase()
        logger.info("Connected to PostgreSQL with pgvector")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return
    
    # URLs to scrape
    urls = [
        "https://en.wikipedia.org/wiki/Vector_database",
        "https://en.wikipedia.org/wiki/PostgreSQL",
        "https://en.wikipedia.org/wiki/Web_scraping"
    ]
    
    # Scrape and index each URL
    results = []
    for url in urls:
        logger.info(f"\nProcessing {url}")
        result = scrape_and_index_webpage(url, db, ignore_ssl_errors=True)
        results.append(result)
        time.sleep(1)  # Be nice to the server
    
    # Print results
    logger.info("\n===== Processing Results =====")
    for result in results:
        if result['success']:
            logger.info(f"✓ {result['url']}")
            logger.info(f"  Title: {result['title']}")
            logger.info(f"  Chunks: {result['chunks']}")
            logger.info(f"  Time: {result['processing_time']}")
        else:
            logger.info(f"✗ {result['url']}")
            logger.info(f"  Error: {result['error']}")
    
    # Get database stats
    stats = db.get_stats()
    logger.info("\n===== Database Statistics =====")
    logger.info(f"Web pages: {stats['webpages_count']}")
    logger.info(f"Chunks: {stats['chunks_count']}")
    logger.info(f"Vector dimension: {stats['vector_dim']}")
    logger.info(f"Total text size: {stats['total_text_size']}")
    if 'webpages_size' in stats:
        logger.info(f"Web pages table size: {stats['webpages_size']}")
        logger.info(f"Chunks table size: {stats['chunks_size']}")
    
    # Perform a search
    query = "Tell me about PostgreSQL and vector databases"
    logger.info(f"\n===== Search Results for: '{query}' =====")
    search_results = db.search(query, top_k=3)
    
    for i, result in enumerate(search_results):
        logger.info(f"\nResult {i+1} (Similarity: {result['similarity']:.4f})")
        logger.info(f"URL: {result['url']}")
        logger.info(f"Title: {result['title']}")
        logger.info(f"Text snippet: {result['text'][:200]}...")
    
    # Close the database connection
    db.close()
    
    logger.info("\nExample completed!")

if __name__ == "__main__":
    main()