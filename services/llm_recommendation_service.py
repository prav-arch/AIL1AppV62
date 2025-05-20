"""
LLM-based Recommendation Service for Anomaly Detection

This module provides functions for generating intelligent recommendations
for detected anomalies using the local Mistral model.
"""

import json
import os
import logging
import re
import importlib.util
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class LLMRecommendationService:
    """Service for generating LLM-based recommendations for anomalies"""
    
    def __init__(self, model_path: str = None):
        """Initialize the LLM recommendation service"""
        self.model_path = model_path or "/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the local LLM if available"""
        # Check if model exists
        if not os.path.exists(self.model_path):
            logger.warning(f"LLM model not found at {self.model_path}")
            return False
            
        # Check if llama_cpp is available
        if not importlib.util.find_spec("llama_cpp"):
            logger.warning("llama_cpp module not available")
            return False
            
        # Initialize the model
        try:
            from llama_cpp import Llama
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,      # Context window size
                n_batch=512,     # Batch size for prompt processing
                verbose=False    # Disable verbose output
            )
            logger.info(f"Initialized Mistral model from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if LLM recommendations are available"""
        return self.llm is not None
    
    def generate_recommendations(self, anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations for an anomaly using the local LLM"""
        if not self.is_available():
            logger.warning("LLM not available, cannot generate recommendations")
            return []
            
        try:
            # Get context from anomaly
            context_str = "\n".join(anomaly.get("context", []))
            
            # Format severity level text
            severity_text = "CRITICAL" if anomaly.get('severity', 0) >= 3 else "ERROR" if anomaly.get('severity', 0) == 2 else "WARNING"
            
            # Create a detailed prompt for the LLM
            prompt = f"""
            You are an expert system administrator and software developer. Analyze the following log anomaly and provide specific, actionable recommendations to address the issue.
            
            ANOMALY DETAILS:
            Type: {anomaly.get('type', '')}
            Component: {anomaly.get('component', '')}
            Message: {anomaly.get('message', '')}
            Severity: {severity_text}
            Source: {anomaly.get('source_file', '')}:{anomaly.get('line_number', 0)}
            
            CONTEXT:
            {context_str}
            
            Based on this information, provide 3-5 actionable recommendations to fix this issue. For each recommendation, include:
            1. A clear title (max 10 words)
            2. A detailed description of what to do (2-3 sentences)
            
            Format your response as a JSON array of objects with 'title' and 'description' fields.
            Example:
            [
              {{
                "title": "First recommendation title",
                "description": "Detailed description of what to do and why it will help resolve the issue."
              }},
              {{
                "title": "Second recommendation title",
                "description": "Another detailed description with specific actions to take."
              }}
            ]
            """
            
            # Generate response from the LLM
            output = self.llm(
                prompt,
                max_tokens=1000,
                temperature=0.2,  # Low temperature for more focused recommendations
                stop=["</s>"]     # Stop at the end token
            )
            
            # Extract text from response
            response_text = output.get('choices', [{}])[0].get('text', '')
            
            # Try to extract JSON from the response
            return self._parse_recommendations(response_text)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _parse_recommendations(self, text: str) -> List[Dict[str, str]]:
        """Parse recommendations from LLM response text"""
        recommendations = []
        
        try:
            # First, try to find and extract JSON array
            json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
            
            if json_match:
                # Parse JSON array if found
                json_str = json_match.group(0)
                parsed_recs = json.loads(json_str)
                
                # Validate parsed recommendations
                if isinstance(parsed_recs, list) and all(isinstance(r, dict) and 'title' in r and 'description' in r for r in parsed_recs):
                    return parsed_recs
            
            # If JSON parsing fails, try to extract recommendations manually
            # Find recommendation titles (often numbered or with clear headings)
            title_pattern = r'(?:^\d+\.\s+|\*\*|\b)([A-Z][^.!?:]*(?::|\.))(?:\s|\n)'
            titles = re.findall(title_pattern, text, re.MULTILINE)
            
            # Extract descriptions following titles
            for i, title in enumerate(titles[:5]):  # Limit to 5 recommendations
                title = title.strip(': .\n\r\t')
                description = ""
                
                # Try to find the description after the title until the next title or end
                start_pos = text.find(title) + len(title)
                end_pos = len(text)
                
                if i < len(titles) - 1:
                    next_title = titles[i + 1]
                    next_pos = text.find(next_title)
                    if next_pos > start_pos:
                        end_pos = next_pos
                
                description = text[start_pos:end_pos].strip(': .\n\r\t')
                
                # Clean up the description
                description = re.sub(r'^\s*[-:]\s*', '', description)
                description = description.strip()
                
                if title and description:
                    recommendations.append({
                        "title": title[:50],  # Limit title length
                        "description": description[:300]  # Limit description length
                    })
                    
        except Exception as e:
            logger.error(f"Error parsing recommendations: {e}")
            
        return recommendations

# Create a singleton instance
recommendation_service = LLMRecommendationService()

def get_recommendations_for_anomaly(anomaly: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get LLM-generated recommendations for an anomaly"""
    return recommendation_service.generate_recommendations(anomaly)