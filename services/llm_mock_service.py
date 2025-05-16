"""
LLM Mock Service for development environments
This module provides a mock implementation of LLM functionality when the real service isn't available
"""
import json
import logging
import os
import random
import time
from flask import Flask, request, Response, stream_with_context

def create_mock_server(port=15000):
    """Create a mock LLM server for development environments"""
    app = Flask(__name__)
    
    @app.route('/v1/chat/completions', methods=['POST'])
    def chat_completions():
        """Mock implementation of OpenAI-compatible chat completions endpoint"""
        data = request.json
        messages = data.get('messages', [])
        prompt = ""
        
        # Extract the last user message as the prompt
        for message in reversed(messages):
            if message.get('role') == 'user':
                prompt = message.get('content', '')
                break
        
        # If streaming is requested, use an SSE response
        if data.get('stream', False):
            def generate():
                response = generate_mock_response(prompt)
                
                # Send a fake response token by token with short delays
                for i, token in enumerate(response.split()):
                    chunk = {
                        "id": f"chatcmpl-{random.randint(1000, 9999)}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "gpt-3.5-turbo",
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": token + " "
                                },
                                "finish_reason": None
                            }
                        ]
                    }
                    
                    # Add finish reason to the last token
                    if i == len(response.split()) - 1:
                        chunk["choices"][0]["finish_reason"] = "stop"
                    
                    yield f"data: {json.dumps(chunk)}\n\n"
                    time.sleep(0.05)  # Simulate thinking time
                
                yield "data: [DONE]\n\n"
                
            return Response(stream_with_context(generate()), mimetype='text/event-stream')
        else:
            response = generate_mock_response(prompt)
            
            return {
                "id": f"chatcmpl-{random.randint(1000, 9999)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.split()),
                    "total_tokens": len(prompt.split()) + len(response.split())
                }
            }
    
    return app

def generate_mock_response(prompt):
    """Generate a mock response based on the prompt"""
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
        response = response_intro + "Here's what I can tell you:\n\n"
        if "how" in prompt.lower():
            response += "The process typically involves several steps:\n\n"
            response += "1. First, understand the requirements clearly\n"
            response += "2. Research the available resources and tools\n"
            response += "3. Design a proper implementation strategy\n"
            response += "4. Execute the plan with careful monitoring\n"
            response += "5. Review and refine the results for optimization\n\n"
        elif "what" in prompt.lower():
            response += "This refers to a specialized concept in the field. "
            response += "It encompasses several important aspects that are worth considering in detail. "
            response += "The core principles behind this include efficiency, reliability, and scalability.\n\n"
        elif "why" in prompt.lower():
            response += "There are several important reasons:\n\n"
            response += "• It significantly improves system performance\n"
            response += "• It reduces the likelihood of errors and failures\n"
            response += "• It aligns with industry best practices and standards\n" 
            response += "• It enables better scalability for future requirements\n\n"
        else:
            response += "The answer depends on several factors including the specific context, requirements, "
            response += "and constraints of your situation. Generally speaking, the best approach would be "
            response += "to analyze the specific parameters involved and develop a tailored solution.\n\n"
    elif "hello" in prompt.lower() or "hi" in prompt.lower():
        response = "Hello! How can I assist you today with the AI Assistant Platform? "
        response += "I can help with LLM queries, RAG functionality, anomaly detection, "
        response += "or data pipeline management. What would you like to know more about?\n\n"
    else:
        response = response_intro + "Here's my analysis:\n\n"
        response += "This is an important topic that involves multiple considerations. "
        response += "The key aspects to focus on include system architecture, data processing workflows, "
        response += "and integration patterns with existing infrastructure. "
        response += "When implementing solutions in this area, it's crucial to maintain proper "
        response += "balance between performance, reliability, and maintainability.\n\n"
    
    return response

def start_mock_llm_server():
    """Start the mock LLM server on port 15000"""
    port = 15000
    app = create_mock_server(port)
    
    from threading import Thread
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    logging.info(f"Mock LLM server started on port {port}")
    
    return server_thread