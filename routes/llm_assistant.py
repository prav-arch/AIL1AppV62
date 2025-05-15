"""
LLM Assistant routes for the AI Assistant Platform.
Handles interactions with the LLM for chat conversations.
"""

from flask import Blueprint, render_template, request, jsonify, session
from db import execute_query, add_conversation, add_message, get_messages
import logging
import os
import time
import json

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
llm_assistant_bp = Blueprint('llm_assistant', __name__, url_prefix='/llm_assistant')

@llm_assistant_bp.route('/')
def index():
    """LLM Assistant main page."""
    # Get conversation history from database
    conversations = get_user_conversations()
    
    return render_template(
        'llm_assistant.html', 
        conversations=conversations
    )

@llm_assistant_bp.route('/conversation/<int:conversation_id>')
def get_conversation(conversation_id):
    """Get a specific conversation."""
    user_id = session.get('user_id', 1)  # Default to user 1 for now
    
    # Get messages for the conversation
    messages = get_messages(conversation_id)
    
    return jsonify({'messages': messages})

@llm_assistant_bp.route('/new_conversation', methods=['POST'])
def new_conversation():
    """Create a new conversation."""
    user_id = session.get('user_id', 1)  # Default to user 1 for now
    
    # Create a new conversation in the database
    conversation_id = add_conversation(user_id, title="New Conversation")
    
    # Add initial system message
    system_message = """You are an AI assistant. You help users with their questions and tasks."""
    add_message(conversation_id, "system", system_message)
    
    return jsonify({'conversation_id': conversation_id})

@llm_assistant_bp.route('/message', methods=['POST'])
def send_message():
    """Send a message to the LLM and get a response."""
    try:
        # Get request data
        data = request.json
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        user_id = session.get('user_id', 1)  # Default to user 1 for now
        
        # Validate inputs
        if not conversation_id or not message:
            return jsonify({'error': 'Missing conversation_id or message'}), 400
        
        # Add user message to database
        add_message(conversation_id, "user", message)
        
        # Call LLM service to get response
        # This will be implemented with a call to the local LLM service
        # For now, we'll simulate a response
        time.sleep(0.5)  # Simulate processing time
        response = simulate_llm_response(message)
        
        # Add assistant message to database
        add_message(conversation_id, "assistant", response)
        
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_user_conversations(limit=20):
    """Get conversations for a user."""
    user_id = session.get('user_id', 1)  # Default to user 1 for now
    
    try:
        conversations = execute_query("""
            SELECT c.id, c.title, c.created_at, c.updated_at,
                (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
                (SELECT content FROM messages WHERE conversation_id = c.id AND role = 'user' 
                 ORDER BY timestamp DESC LIMIT 1) as last_message
            FROM conversations c
            WHERE c.user_id = %s
            ORDER BY c.updated_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        return conversations if conversations else []
    except Exception as e:
        logger.error(f"Error getting user conversations: {str(e)}")
        return []

def simulate_llm_response(message):
    """Simulate a response from the LLM."""
    # For now, just return a simple response
    # In the real implementation, this would call the local LLM service
    return f"I understand you said: {message}. I'm a simulated response until the LLM service is fully integrated with PostgreSQL."