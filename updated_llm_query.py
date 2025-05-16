"""
Updated LLM query handler with improved error handling
"""
import time
import json
import logging
import requests
import uuid
import random
from flask import request, jsonify, Response, stream_with_context, current_app

def new_llm_query_handler():
    """Process an LLM query and return the response"""
    start_time = time.time()
    data = request.json or {}
    prompt = data.get('query', '')  # Changed from 'prompt' to 'query' to match frontend
    
    if not prompt:
        return jsonify({
            'error': 'No query provided'
        }), 400
        
    # Extract parameters - ensure variables are defined before use
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 1024)
    agent_type = data.get('agent_type', 'general')
    use_rag = data.get('use_rag', False)
    
    # Generate a simple query ID for tracking even if database is unavailable
    query_id = str(uuid.uuid4())
    
    # Try to save query to database, but continue even if it fails
    try:
        # Import here to avoid circular imports
        import clickhouse_llm_query
        
        # Save to ClickHouse if connection is available
        try:
            db_query_id = clickhouse_llm_query.save_llm_query(
                query_text=prompt,
                agent_type=agent_type,
                temperature=temperature,
                max_tokens=max_tokens,
                used_rag=use_rag
            )
            if db_query_id:
                query_id = db_query_id  # Use the database ID if available
        except Exception as e:
            logging.warning(f"Error saving LLM query to ClickHouse: {str(e)}")
            # Continue without saving to database - graceful degradation
    except Exception as e:
        logging.warning(f"Error preparing LLM query: {str(e)}")
        
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
                # Provide a functional simulated LLM response
                # Create a more natural-sounding response based on the query
                sample_responses = [
                    f"Thank you for your query about '{prompt.split()[0] if prompt.split() else 'that topic'}'. ",
                    f"I've analyzed your question about '{prompt.split()[0] if prompt.split() else 'this'}'... ",
                    f"Regarding your inquiry on '{prompt.split()[0] if prompt.split() else 'this topic'}'... ",
                    f"Based on your question about '{prompt.split()[0] if prompt.split() else 'this subject'}'... "
                ]
                
                response_intro = random.choice(sample_responses)
                
                # Create an answer based on the query type
                if "?" in prompt:
                    mock_response = response_intro + "Here's what I can tell you:\n\n"
                    if "how" in prompt.lower():
                        mock_response += "The process typically involves several steps:\n\n"
                        mock_response += "1. First, understand the requirements clearly\n"
                        mock_response += "2. Research the available resources and tools\n"
                        mock_response += "3. Design a proper implementation strategy\n"
                        mock_response += "4. Execute the plan with careful monitoring\n"
                        mock_response += "5. Review and refine the results for optimization\n\n"
                    elif "what" in prompt.lower():
                        mock_response += "This refers to a specialized concept in the field. "
                        mock_response += "It encompasses several important aspects that are worth considering in detail. "
                        mock_response += "The core principles behind this include efficiency, reliability, and scalability.\n\n"
                    elif "why" in prompt.lower():
                        mock_response += "There are several important reasons:\n\n"
                        mock_response += "• It significantly improves system performance\n"
                        mock_response += "• It reduces the likelihood of errors and failures\n"
                        mock_response += "• It aligns with industry best practices and standards\n" 
                        mock_response += "• It enables better scalability for future requirements\n\n"
                    else:
                        mock_response += "The answer depends on several factors including the specific context, requirements, "
                        mock_response += "and constraints of your situation. Generally speaking, the best approach would be "
                        mock_response += "to analyze the specific parameters involved and develop a tailored solution.\n\n"
                elif "hello" in prompt.lower() or "hi" in prompt.lower():
                    mock_response = "Hello! How can I assist you today with the AI Assistant Platform? "
                    mock_response += "I can help with LLM queries, RAG functionality, anomaly detection, "
                    mock_response += "or data pipeline management. What would you like to know more about?\n\n"
                else:
                    mock_response = response_intro + "Here's my analysis:\n\n"
                    mock_response += "This is an important topic that involves multiple considerations. "
                    mock_response += "The key aspects to focus on include system architecture, data processing workflows, "
                    mock_response += "and integration patterns with existing infrastructure. "
                    mock_response += "When implementing solutions in this area, it's crucial to maintain proper "
                    mock_response += "balance between performance, reliability, and maintainability.\n\n"
                    
                mock_response += "Note: This response is generated in a development environment. "
                mock_response += "In production, more detailed and tailored responses would be provided by the LLM service."
                
                # Log that we're using a mock response
                logging.info("Using mock LLM response in development environment")
                
                # Simulate a streaming response character by character
                for char in mock_response:
                    yield f"data: {json.dumps({'text': char})}\n\n"
                    time.sleep(0.01)  # Small delay to simulate streaming
                
                yield "data: [DONE]\n\n"
                return
                
                # Actual production code - commented out until LLM service is available
                # try:
                #     response = requests.post(
                #         'http://localhost:15000/api/local-llm/generate',
                #         json={
                #             'prompt': prompt, 
                #             'system_prompt': system_prompt,
                #             'stream': True,
                #             'max_tokens': max_tokens,
                #             'temperature': temperature
                #         },
                #         stream=True
                #     )
                # except requests.exceptions.ConnectionError:
                #     error_msg = "Cannot connect to LLM service. The local LLM model is not available."
                #     logging.error(error_msg)
                #     yield f"data: {json.dumps({'error': error_msg})}\n\n"
                #     yield "data: [DONE]\n\n"
                #     return
                
                # The code below is disabled since we're using mock responses
                # All this error handling code would be enabled when the real LLM service is connected
                """
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
                """
                
                # This code is for the real LLM service and is disabled while we use mock responses
                """
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
                """

                # For our development environment, save the mock response
                full_response = mock_response  # Use the mock response we created
                
                # Attempt to save to the database if we have a query_id
                if query_id:
                    try:
                        # Try to save to ClickHouse, but don't break if it fails
                        import clickhouse_llm_query
                        clickhouse_llm_query.update_llm_query_response(
                            query_id=query_id,
                            response_text=full_response,
                            response_time_ms=int((time.time() - start_time) * 1000)
                        )
                    except Exception as e:
                        # Log the error but continue - the user still gets a response
                        logging.error(f"Error updating LLM query in ClickHouse: {str(e)}")
                        
                # We already sent the [DONE] message in the mock response section above
                
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