from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import logging
import os
from services.local_llm_service import LocalLLMService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Blueprint
local_llm_bp = Blueprint('local_llm', __name__, url_prefix='/api/local-llm')

# Initialize the LLM service
# You can set a custom model path in environment variable or use the default
model_path = os.environ.get('LLM_MODEL_PATH', '/tmp/llm_models/tinyllama-1.1b-chat-v1.0.Q4_k_M.gguf')
llm_service = LocalLLMService(model_path=model_path)

@local_llm_bp.route('/status', methods=['GET'])
def get_status():
    """Check if the LLM is ready"""
    if llm_service.is_ready():
        return jsonify({
            "status": "ready",
            "model_info": llm_service.get_model_info()
        })
    else:
        return jsonify({
            "status": "not_ready",
            "error": "LLM model not loaded. Check server logs for details."
        }), 503

@local_llm_bp.route('/generate', methods=['POST'])
def generate():
    """Generate a response from the LLM"""
    data = request.json or {}
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Get parameters
    system_prompt = data.get('system_prompt', 'You are a helpful AI assistant.')
    stream = data.get('stream', False)
    max_tokens = data.get('max_tokens', 256)
    temperature = data.get('temperature', 0.7)
    
    # Check if the model is ready
    if not llm_service.is_ready():
        return jsonify({
            'error': 'LLM model not loaded. Check server logs for details.'
        }), 503
    
    if stream:
        # Streaming response
        def generate_stream():
            for chunk in llm_service.query_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if "error" in chunk:
                    yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                    return
                
                # Extract token from the chunk
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    token = chunk["choices"][0]["delta"].get("content", "")
                    if token:
                        yield f"data: {json.dumps({'text': token})}\n\n"
            
            # Signal the end of the stream
            yield "data: [DONE]\n\n"
        
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/event-stream'
        )
    else:
        # Non-streaming response
        response = llm_service.query(prompt=prompt, system_prompt=system_prompt)
        return jsonify({'text': response})

@local_llm_bp.route('/chat', methods=['POST'])
def chat():
    """Chat with the LLM using messages format"""
    data = request.json or {}
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({'error': 'Messages are required'}), 400
    
    # Get parameters
    stream = data.get('stream', False)
    max_tokens = data.get('max_tokens', 256)
    temperature = data.get('temperature', 0.7)
    
    # Check if the model is ready
    if not llm_service.is_ready():
        return jsonify({
            'error': 'LLM model not loaded. Check server logs for details.'
        }), 503
    
    # Extract the user prompt from the last message
    if messages[-1]['role'] != 'user':
        return jsonify({'error': 'Last message must be from the user'}), 400
    
    prompt = messages[-1]['content']
    
    # Extract system prompt if present
    system_prompt = None
    for message in messages:
        if message['role'] == 'system':
            system_prompt = message['content']
            break
    
    if stream:
        # Streaming response (reusing the generate endpoint)
        def generate_stream():
            for chunk in llm_service.query_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if "error" in chunk:
                    yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                    return
                
                # Extract token from the chunk
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    token = chunk["choices"][0]["delta"].get("content", "")
                    if token:
                        yield f"data: {json.dumps({'text': token})}\n\n"
            
            # Signal the end of the stream
            yield "data: [DONE]\n\n"
        
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/event-stream'
        )
    else:
        # Non-streaming response
        response = llm_service.query(prompt=prompt, system_prompt=system_prompt)
        return jsonify({
            'message': {
                'role': 'assistant',
                'content': response
            }
        })