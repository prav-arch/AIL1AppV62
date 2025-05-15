"""
AI Assistant Platform - Main Application

This is the main entry point for the AI Assistant Platform.
It initializes the Flask application and sets up the PostgreSQL database connection.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# Configure database connection
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
if not app.config['DATABASE_URL']:
    logger.warning("DATABASE_URL not set, some features may not work properly")

# Initialize database
from db import init_db

# Initialize database
with app.app_context():
    try:
        # Initialize the database with all required tables
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Import and register blueprints for different sections of the application
from routes.dashboard import dashboard_bp
from routes.llm_assistant import llm_assistant_bp
from routes.rag import rag_bp
from routes.anomalies import anomalies_bp
from routes.data_pipeline import data_pipeline_bp
from routes.kafka_browser import kafka_browser_bp

app.register_blueprint(dashboard_bp)
app.register_blueprint(llm_assistant_bp)
app.register_blueprint(rag_bp)
app.register_blueprint(anomalies_bp)
app.register_blueprint(data_pipeline_bp)
app.register_blueprint(kafka_browser_bp)

# Root route - redirect to dashboard
@app.route('/')
def index():
    """Root route redirects to the dashboard."""
    return redirect(url_for('dashboard.index'))

# Add error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error_code=500, error_message="Server error"), 500

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "1.0.0"})

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)