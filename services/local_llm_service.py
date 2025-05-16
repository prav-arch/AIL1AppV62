import os
import logging
from typing import Iterator, Dict, List, Optional, Any
from llama_cpp import Llama
import os

logger = logging.getLogger(__name__)

class LocalLLMService:
    """Local LLM service using llama-cpp-python"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the LLM service with the model path"""
        if not model_path:
            # Default model path
            model_path = "/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        
        # Check if the model exists
        if not os.path.exists(model_path):
            logger.warning(f"Model not found at {model_path}. Please provide a valid model path.")
            self.llm = None
        else:
            try:
                logger.info(f"Loading model from {model_path}")
                # Force GPU usage for better performance
                self.llm = Llama(
                    model_path=model_path,
                    n_ctx=1024,
                    chat_format="llama-2",  # Adjust if your model uses a different format
                    n_gpu_layers=-1,  # Use all available GPU layers (-1)
                    use_gpu=True      # Force GPU usage
                )
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}")
                self.llm = None
        
        self.model_path = model_path
    
    def is_ready(self) -> bool:
        """Check if the LLM is ready to use"""
        return self.llm is not None
    
    def query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Query the LLM with a prompt and return the response"""
        if not self.is_ready():
            return "Error: LLM not initialized. Please check the model path."
        
        try:
            # Create the messages for the chat
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=256,
                temperature=0.7,
            )
            
            # Extract the generated text
            output = response["choices"][0]["message"]["content"]
            return output
        
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            return f"Error querying LLM: {str(e)}"
    
    def query_stream(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 256, 
                     temperature: float = 0.7) -> Iterator[Dict[str, Any]]:
        """Query the LLM with a prompt and stream the response"""
        if not self.is_ready():
            yield {"error": "LLM not initialized. Please check the model path."}
            return
        
        try:
            # Create the messages for the chat
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            # Generate streaming response
            for chunk in self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Error streaming from LLM: {str(e)}")
            yield {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_ready():
            return {"status": "not_loaded", "model_path": self.model_path}
        
        return {
            "status": "loaded",
            "model_path": self.model_path,
            "context_length": self.llm.n_ctx,
            "chat_format": self.llm.chat_format,
        }