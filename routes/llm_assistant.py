from flask import Blueprint, render_template, request, jsonify
from services.llm_service import LLMService
from vector_service import VectorService
from clickhouse_models import DocumentChunk
import time
import json
import logging
from clickhouse_models import LLMPrompt  # Import the LLMPrompt model

# Configure logging
logger = logging.getLogger(__name__)

llm_assistant_bp = Blueprint('llm_assistant', __name__, url_prefix='/llm-assistant')

@llm_assistant_bp.route('/')
def index():
    return render_template('llm_assistant.html')

@llm_assistant_bp.route('/query', methods=['POST'])
def query_llm():
    data = request.json or {}
    prompt = data.get('prompt', '')
    stream = data.get('stream', False)  # Check if streaming is requested
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Use streaming if requested
    if stream:
        return stream_llm_response(prompt)
    
    try:
        # Start timing for response time measurement
        start_time = time.time()
        
        # Search vector database for relevant context
        vector_service = VectorService()
        relevant_chunks = vector_service.search_similar_text(prompt, top_k=3)
        
        # Build context from relevant chunks
        context_parts = []
        if relevant_chunks:
            chunk_ids = [int(chunk_id) if str(chunk_id).isdigit() else 0 for chunk_id, _ in relevant_chunks]
            chunks_data = DocumentChunk.get_by_ids(chunk_ids)
            
            for chunk in chunks_data:
                if chunk:
                    context_parts.append(f"Context: {chunk.get('chunk_text', '')}")
        
        # Create enhanced prompt with context
        if context_parts:
            enhanced_prompt = f"""Based on the following context information, please answer the user's question:

{chr(10).join(context_parts)}

User Question: {prompt}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, please say so and provide a general response."""
        else:
            enhanced_prompt = prompt
        
        # Query the LLM service with enhanced prompt
        llm_service = LLMService()
        response = llm_service.query(enhanced_prompt)
        
        # End timing
        end_time = time.time()
        
        # Prepare metadata
        metadata = {
            'start_time': start_time,
            'end_time': end_time,
            'response_time': end_time - start_time,
            'model': 'mistral-7b-instruct',
            'client_ip': request.remote_addr,
            'user_agent': request.user_agent.string,
            'streaming': False
        }
        
        # Save the prompt and response to ClickHouse
        try:
            prompt_id = LLMPrompt.create(
                prompt=prompt,
                response=response,
                metadata=metadata,
                user_id=request.cookies.get('user_id', None)
            )
            logger.info(f"LLM prompt saved to ClickHouse with ID: {prompt_id}")
        except Exception as db_error:
            logger.error(f"Failed to save LLM prompt to ClickHouse: {str(db_error)}")
            # Continue even if saving to database fails
        
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in LLM query: {str(e)}")
        return jsonify({'error': str(e)}), 500

def stream_llm_response(prompt):
    """Stream the LLM response"""
    from flask import Response, stream_with_context
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Prepare metadata for eventual storage
    start_time = time.time()
    metadata = {
        'start_time': start_time,
        'model': 'mistral-7b-instruct',
        'client_ip': request.remote_addr,
        'user_agent': request.user_agent.string,
        'streaming': True
    }
    
    def generate():
        try:
            # Search vector database for relevant context
            vector_service = VectorService()
            relevant_chunks = vector_service.search_similar_text(prompt, top_k=3)
            
            # Build context from relevant chunks
            context_parts = []
            if relevant_chunks:
                chunk_ids = [int(chunk_id) if str(chunk_id).isdigit() else 0 for chunk_id, _ in relevant_chunks]
                chunks_data = DocumentChunk.get_by_ids(chunk_ids)
                
                for chunk in chunks_data:
                    if chunk:
                        context_parts.append(f"Context: {chunk.get('chunk_text', '')}")
            
            # Create enhanced prompt with context
            if context_parts:
                enhanced_prompt = f"""Based on the following context information, please answer the user's question:

{chr(10).join(context_parts)}

User Question: {prompt}

Please provide a helpful answer based on the context above. If the context doesn't contain relevant information, please say so and provide a general response."""
            else:
                enhanced_prompt = prompt
            
            llm_service = LLMService()
            full_response = ""
            
            # Stream the response chunks
            for chunk in llm_service.query_stream(enhanced_prompt):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # After streaming completes, save to ClickHouse
            end_time = time.time()
            metadata['end_time'] = end_time
            metadata['response_time'] = end_time - start_time
            
            try:
                prompt_id = LLMPrompt.create(
                    prompt=prompt,
                    response=full_response,
                    metadata=metadata,
                    user_id=request.cookies.get('user_id', None)
                )
                logger.info(f"Streamed LLM prompt saved to ClickHouse with ID: {prompt_id}")
            except Exception as db_error:
                logger.error(f"Failed to save streamed LLM prompt to ClickHouse: {str(db_error)}")
            
            # Signal completion
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming LLM query: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@llm_assistant_bp.route('/history', methods=['GET'])
def get_history():
    """Get recent LLM prompt history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = LLMPrompt.get_recent(limit=limit)
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Error getting LLM history: {str(e)}")
        return jsonify({'error': str(e)}), 500