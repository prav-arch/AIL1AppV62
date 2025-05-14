import logging
import json
import os
import requests
from typing import Dict, Any, List, Optional, Generator, AsyncGenerator, Union, Literal
import asyncio
import aiohttp
from urllib.parse import urljoin

# Configure logging
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM API"""
    
    def __init__(self, base_url: Optional[str] = None, verify_ssl: bool = False):
        """
        Initialize the LLM service.
        
        Args:
            base_url: Base URL of the LLM API
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url or os.environ.get("LLM_API_BASE_URL", "http://127.0.0.1:8080")
        self.verify_ssl = verify_ssl
        logger.info(f"LLM Service initialized with base URL: {self.base_url}")
    
    def query(self, prompt: str, **kwargs) -> str:
        """
        Send a query to the LLM and get a response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Returns:
            The LLM's response as a string
        """
        try:
            endpoint = "/api/generate"
            url = urljoin(self.base_url, endpoint)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": False
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            logger.debug(f"Sending query to LLM: {prompt[:100]}...")
            
            # Make the API request
            response = requests.post(
                url,
                json=payload,
                verify=self.verify_ssl,
                timeout=60  # 60-second timeout
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse the JSON response
            result = response.json()
            
            if "error" in result:
                raise Exception(f"LLM API error: {result['error']}")
            
            # Extract the generated text
            if "response" in result:
                return result["response"]
            elif "text" in result:
                return result["text"]
            elif "generated_text" in result:
                return result["generated_text"]
            else:
                logger.warning(f"Unexpected response format: {result}")
                return str(result)
        
        except requests.RequestException as e:
            logger.error(f"Failed to communicate with LLM API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in LLM query: {str(e)}")
            raise
    
    def query_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Send a query to the LLM and get a streaming response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Yields:
            Chunks of the LLM's response as they become available
        """
        try:
            endpoint = "/api/generate"
            url = urljoin(self.base_url, endpoint)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": True
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            logger.debug(f"Sending streaming query to LLM: {prompt[:100]}...")
            
            # Make the API request with streaming enabled
            with requests.post(
                url,
                json=payload,
                verify=self.verify_ssl,
                stream=True,
                timeout=120  # 2-minute timeout
            ) as response:
                # Check for successful response
                response.raise_for_status()
                
                # Process the streaming response
                for line in response.iter_lines():
                    if line:
                        # Skip empty lines
                        line = line.decode('utf-8')
                        
                        # Handle SSE format if applicable
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                        
                        # Skip heartbeat messages
                        if line == '[DONE]':
                            break
                        
                        try:
                            # Try to parse as JSON
                            chunk = json.loads(line)
                            
                            # Extract the text content based on response format
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                # OpenAI-like format
                                content = chunk["choices"][0].get("text", "") or chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            elif "response" in chunk:
                                yield chunk["response"]
                            elif "text" in chunk:
                                yield chunk["text"]
                            elif "generated_text" in chunk:
                                yield chunk["generated_text"]
                            else:
                                # Fallback for unknown formats
                                logger.warning(f"Unexpected chunk format: {chunk}")
                                if isinstance(chunk, dict):
                                    for key, value in chunk.items():
                                        if isinstance(value, str) and value:
                                            yield value
                                            break
                        except json.JSONDecodeError:
                            # If not JSON, yield the raw line
                            yield line
                            
        except requests.RequestException as e:
            logger.error(f"Failed to communicate with LLM API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in LLM streaming query: {str(e)}")
            raise
    
    async def aquery(self, prompt: str, **kwargs) -> str:
        """
        Asynchronously send a query to the LLM and get a response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Returns:
            The LLM's response as a string
        """
        try:
            endpoint = "/api/generate"
            url = urljoin(self.base_url, endpoint)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": False
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            logger.debug(f"Sending async query to LLM: {prompt[:100]}...")
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    ssl=bool(self.verify_ssl),  # Convert to bool to avoid type issues
                    timeout=aiohttp.ClientTimeout(total=60)  # 60-second timeout
                ) as response:
                    # Check for successful response
                    response.raise_for_status()
                    
                    # Parse the JSON response
                    result = await response.json()
                    
                    if "error" in result:
                        raise Exception(f"LLM API error: {result['error']}")
                    
                    # Extract the generated text
                    if "response" in result:
                        return result["response"]
                    elif "text" in result:
                        return result["text"]
                    elif "generated_text" in result:
                        return result["generated_text"]
                    else:
                        logger.warning(f"Unexpected response format: {result}")
                        return str(result)
        
        except aiohttp.ClientError as e:
            logger.error(f"Failed to communicate with LLM API asynchronously: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in async LLM query: {str(e)}")
            raise
    
    async def aquery_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Asynchronously send a query to the LLM and get a streaming response.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM
            
        Yields:
            Chunks of the LLM's response as they become available
        """
        try:
            endpoint = "/api/generate"
            url = urljoin(self.base_url, endpoint)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": True
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            logger.debug(f"Sending async streaming query to LLM: {prompt[:100]}...")
            
            # Make the API request with streaming enabled
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    ssl=bool(self.verify_ssl),  # Convert to bool to avoid type issues
                    timeout=aiohttp.ClientTimeout(total=120)  # 2-minute timeout
                ) as response:
                    # Check for successful response
                    response.raise_for_status()
                    
                    # Process the streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        # Handle SSE format if applicable
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                        
                        # Skip heartbeat messages
                        if line == '[DONE]':
                            break
                        
                        try:
                            # Try to parse as JSON
                            chunk = json.loads(line)
                            
                            # Extract the text content based on response format
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                # OpenAI-like format
                                content = chunk["choices"][0].get("text", "") or chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            elif "response" in chunk:
                                yield chunk["response"]
                            elif "text" in chunk:
                                yield chunk["text"]
                            elif "generated_text" in chunk:
                                yield chunk["generated_text"]
                            else:
                                # Fallback for unknown formats
                                logger.warning(f"Unexpected chunk format: {chunk}")
                                if isinstance(chunk, dict):
                                    for key, value in chunk.items():
                                        if isinstance(value, str) and value:
                                            yield value
                                            break
                        except json.JSONDecodeError:
                            # If not JSON, yield the raw line
                            yield line
                            
        except aiohttp.ClientError as e:
            logger.error(f"Failed to communicate with LLM API asynchronously: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in async LLM streaming query: {str(e)}")
            raise

    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Get an embedding for the given text.
        
        Args:
            text: The text to embed
            **kwargs: Additional parameters for the embedding model
            
        Returns:
            A list of floats representing the embedding
        """
        try:
            endpoint = "/api/embeddings"
            url = urljoin(self.base_url, endpoint)
            
            # Prepare the request payload
            payload = {
                "input": text,
                "model": kwargs.get("model", "text-embedding-ada-002")
            }
            
            # Make the API request
            response = requests.post(
                url,
                json=payload,
                verify=self.verify_ssl,
                timeout=30  # 30-second timeout
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse the JSON response
            result = response.json()
            
            if "error" in result:
                raise Exception(f"LLM API error: {result['error']}")
            
            # Extract the embedding
            if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
                return result["data"][0]["embedding"]
            elif "embedding" in result:
                return result["embedding"]
            else:
                logger.warning(f"Unexpected embedding response format: {result}")
                raise ValueError("Could not parse embedding from response")
        
        except requests.RequestException as e:
            logger.error(f"Failed to communicate with LLM API for embedding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise

    def check_health(self) -> bool:
        """
        Check if the LLM API is healthy and responsive.
        
        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            # Try a simple heartbeat endpoint first, if available
            endpoints = ["/health", "/api/health", "/v1/health", "/"]
            
            for endpoint in endpoints:
                try:
                    url = urljoin(self.base_url, endpoint)
                    response = requests.get(
                        url,
                        verify=self.verify_ssl,
                        timeout=5  # Short timeout for health check
                    )
                    if response.status_code < 300:
                        logger.info(f"LLM API health check successful on endpoint: {endpoint}")
                        return True
                except requests.RequestException:
                    # Try the next endpoint
                    continue
            
            # If no heartbeat endpoint worked, try a simple query
            logger.warning("Heartbeat endpoints failed, trying a simple query for health check")
            self.query("hello", max_tokens=10)
            logger.info("LLM API health check successful via query")
            return True
            
        except Exception as e:
            logger.error(f"LLM API health check failed: {str(e)}")
            return False