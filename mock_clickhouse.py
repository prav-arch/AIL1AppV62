"""
Mock ClickHouse implementation for development environment
This module provides mock implementations for when ClickHouse is not available
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory storage for development
_llm_queries = []
_next_id = 1

def get_llm_query_count() -> int:
    """Get the total count of LLM queries"""
    return len(_llm_queries)

def get_today_llm_query_count() -> int:
    """Get the count of LLM queries from today"""
    today = datetime.now().date()
    return sum(1 for q in _llm_queries if q['created_at'].date() == today)

def save_llm_query(query_text: str, agent_type: str = 'general', 
                  temperature: float = 0.7, max_tokens: int = 1024, 
                  used_rag: bool = False) -> str:
    """Save a new LLM query to memory"""
    global _next_id
    
    query_id = str(uuid.uuid4())
    
    query = {
        'id': query_id,
        'query_text': query_text,
        'response_text': '',
        'agent_type': agent_type,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'created_at': datetime.now(),
        'response_time_ms': None,
        'prompt_tokens': None,
        'completion_tokens': None,
        'error': None,
        'used_rag': used_rag
    }
    
    _llm_queries.append(query)
    _next_id += 1
    
    logger.info(f"Saved LLM query to memory with ID: {query_id}")
    return query_id

def update_llm_query_response(query_id: str, response_text: str, 
                            response_time_ms: int = None,
                            prompt_tokens: int = None, 
                            completion_tokens: int = None,
                            error: str = None) -> bool:
    """Update an LLM query with the response"""
    for query in _llm_queries:
        if query['id'] == query_id:
            if response_text:
                query['response_text'] = response_text
            if response_time_ms is not None:
                query['response_time_ms'] = response_time_ms
            if prompt_tokens is not None:
                query['prompt_tokens'] = prompt_tokens
            if completion_tokens is not None:
                query['completion_tokens'] = completion_tokens
            if error:
                query['error'] = error
                
            logger.info(f"Updated LLM query response for ID: {query_id}")
            return True
            
    logger.error(f"Cannot find LLM query with ID: {query_id}")
    return False

def get_llm_queries(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Get paginated LLM queries"""
    # Calculate pagination
    total_count = len(_llm_queries)
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
    
    # Sort by created_at descending
    sorted_queries = sorted(_llm_queries, key=lambda q: q['created_at'], reverse=True)
    
    # Get the requested page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_queries = sorted_queries[start_idx:end_idx]
    
    # Format the results
    formatted_queries = []
    for q in page_queries:
        formatted_queries.append({
            'id': q['id'],
            'query_text': q['query_text'],
            'response_text': q['response_text'],
            'agent_type': q['agent_type'],
            'temperature': q['temperature'],
            'max_tokens': q['max_tokens'],
            'created_at': q['created_at'].isoformat(),
            'response_time_ms': q['response_time_ms'],
            'prompt_tokens': q['prompt_tokens'],
            'completion_tokens': q['completion_tokens'],
            'error': q['error'],
            'used_rag': q['used_rag']
        })
    
    return {
        'queries': formatted_queries,
        'total': total_count,
        'pages': total_pages,
        'current_page': page
    }

# Add a few sample queries for development visualization
save_llm_query("What's the weather like today?")
save_llm_query("Can you help me with a Python coding problem?")
save_llm_query("Summarize the latest news about AI")
update_llm_query_response(_llm_queries[0]['id'], "I'm sorry, I don't have access to current weather information. You can check a weather service like weather.com for the latest updates.", 450, 25, 35)
update_llm_query_response(_llm_queries[1]['id'], "Of course! I'd be happy to help with your Python coding problem. Could you please share the specific problem or code snippet you're working with?", 520, 30, 42)
update_llm_query_response(_llm_queries[2]['id'], "Recent AI news includes advances in large language models, new applications in healthcare, and ongoing discussions about AI regulation. Would you like more specific information on any of these topics?", 680, 28, 48)