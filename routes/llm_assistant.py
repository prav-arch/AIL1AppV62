from flask import Blueprint, render_template, request, jsonify
from services.llm_service import LLMService

llm_assistant_bp = Blueprint('llm_assistant', __name__, url_prefix='/llm-assistant')

@llm_assistant_bp.route('/')
def index():
    return render_template('llm_assistant.html')

@llm_assistant_bp.route('/query', methods=['POST'])
def query_llm():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        llm_service = LLMService()
        response = llm_service.query(prompt)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500