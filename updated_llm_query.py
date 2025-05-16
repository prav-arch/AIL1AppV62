"""
Updated LLM query handler with improved error handling
"""
import time
import json
import logging
import requests
from flask import request, jsonify, Response, stream_with_context, current_app

def new_llm_query_handler():
    """Process an LLM query and return the response"""
    start_time = time.time()
    data = request.json or {}
    
    # Accept either 'query' or 'prompt' field for flexibility
    prompt = data.get('query', data.get('prompt', ''))
    
    if not prompt:
        # Return a more informative error message
        return jsonify({
            'error': 'No query provided. Please include a "query" or "prompt" field in your request.'
        }), 400
        
    # Extract parameters - ensure variables are defined before use
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 1024)
    agent_type = data.get('agent_type', 'general')
    use_rag = data.get('use_rag', False)
    
    # Save query to database
    query_id = None
    try:
        # Import here to avoid circular imports
        import clickhouse_llm_query
        
        # Save to ClickHouse if connection is available
        try:
            query_id = clickhouse_llm_query.save_llm_query(
                query_text=prompt,
                agent_type=agent_type,
                temperature=temperature,
                max_tokens=max_tokens,
                used_rag=use_rag
            )
        except Exception as e:
            logging.error(f"Error saving LLM query to ClickHouse: {str(e)}")
            # Continue without saving to database - graceful degradation
    except Exception as e:
        logging.error(f"Error preparing LLM query: {str(e)}")
        
    # Use streaming response to the local LLM endpoint
    try:
        # Create system prompt based on agent type
        if agent_type == 'general':
            system_prompt = "You are a helpful, friendly assistant that provides accurate and concise information."
        elif agent_type == 'coding':
            system_prompt = "You are a coding expert that helps with programming problems, explains code, and suggests best practices."
        elif agent_type == 'data':
            system_prompt = "You are a data analysis expert that helps with statistics, data visualization, and data science concepts."
        else:
            system_prompt = "You are a helpful assistant that provides accurate and useful information."
            
        # Handle RAG if enabled
        if use_rag:
            # This is a placeholder for actual RAG implementation
            system_prompt += "\n\n[Relevant information from knowledge base would be added here]"
        
        def generate():
            full_response = ""
            
            try:
                # Make request to the local LLM API on port 15000
                try:
                    response = requests.post(
                        'http://localhost:15000/api/local-llm/generate',
                        json={
                            'prompt': prompt, 
                            'system_prompt': system_prompt,
                            'stream': True,
                            'max_tokens': max_tokens,
                            'temperature': temperature
                        },
                        stream=True
                    )
                except requests.exceptions.ConnectionError:
                    # Since we're in a local development environment without the actual
                    # LLM model, provide a graceful mock response
                    error_msg = "Cannot connect to LLM service. The local LLM model is not available."
                    logging.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # Check if the request was successful
                if response.status_code != 200:
                    error_msg = f"Error from LLM API: {response.text}"
                    logging.error(error_msg)
                    
                    # Update the ClickHouse record with the error if we have a query_id
                    if query_id:
                        try:
                            import clickhouse_llm_query
                            clickhouse_llm_query.update_llm_query_response(
                                query_id=query_id,
                                response_text="",
                                error=error_msg,
                                response_time_ms=int((time.time() - start_time) * 1000)
                            )
                        except Exception as e:
                            logging.error(f"Error updating LLM query error in ClickHouse: {str(e)}")
                    
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                
                # Stream the response from the LLM API
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        try:
                            chunk_text = chunk.decode('utf-8')
                            # Check if the chunk is a proper SSE data format
                            if chunk_text.startswith('data: '):
                                chunk_text = chunk_text[6:].strip()  # Remove 'data: ' prefix
                                
                                # Skip [DONE] message
                                if chunk_text == '[DONE]':
                                    continue
                                    
                                try:
                                    json_chunk = json.loads(chunk_text)
                                    if 'token' in json_chunk:
                                        token = json_chunk['token']
                                        full_response += token
                                        yield f"data: {json.dumps({'token': token})}\n\n"
                                except json.JSONDecodeError:
                                    # If not valid JSON, just pass it through
                                    full_response += chunk_text
                                    yield f"data: {json.dumps({'token': chunk_text})}\n\n"
                            else:
                                # For non-SSE formatted responses, wrap them
                                full_response += chunk_text
                                yield f"data: {json.dumps({'token': chunk_text})}\n\n"
                        except Exception as e:
                            error_msg = f"Error processing chunk: {str(e)}"
                            logging.error(error_msg)
                            yield f"data: {json.dumps({'error': error_msg})}\n\n"

                # Save the full response to the database
                if query_id:
                    try:
                        import clickhouse_llm_query
                        clickhouse_llm_query.update_llm_query_response(
                            query_id=query_id,
                            response_text=full_response,
                            response_time_ms=int((time.time() - start_time) * 1000)
                        )
                    except Exception as e:
                        logging.error(f"Error updating LLM query in ClickHouse: {str(e)}")
                
                # Stream the [DONE] message
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_msg = f"Error in LLM streaming: {str(e)}"
                logging.error(error_msg)
                
                # Update the ClickHouse record with the error if we have a query_id
                if query_id:
                    try:
                        import clickhouse_llm_query
                        clickhouse_llm_query.update_llm_query_response(
                            query_id=query_id, 
                            response_text=full_response,
                            error=error_msg,
                            response_time_ms=int((time.time() - start_time) * 1000)
                        )
                    except Exception as err:
                        logging.error(f"Error updating LLM query error in ClickHouse: {str(err)}")
                
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                yield "data: [DONE]\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    except Exception as e:
        error_msg = f"Error processing LLM request: {str(e)}"
        logging.error(error_msg)
        
        # Update the ClickHouse record with the error if we have a query_id
        if query_id:
            try:
                import clickhouse_llm_query
                clickhouse_llm_query.update_llm_query_response(
                    query_id=query_id,
                    response_text="",
                    error=error_msg,
                    response_time_ms=int((time.time() - start_time) * 1000)
                )
            except Exception as err:
                logging.error(f"Error updating LLM query error in ClickHouse: {str(err)}")
        
        return jsonify({
            'error': error_msg
        }), 500