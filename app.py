import os
import logging
from flask import Flask
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key")

# Configure app settings from config.py
app.config.from_pyfile('config.py')

# Initialize Socket.IO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes to register blueprints
from routes.dashboard import dashboard_bp
from routes.llm_assistant import llm_assistant_bp
from routes.rag import rag_bp
from routes.anomalies import anomalies_bp
from routes.data_pipeline import data_pipeline_bp
from routes.kafka_browser import kafka_browser_bp

# Register blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(llm_assistant_bp)
app.register_blueprint(rag_bp)
app.register_blueprint(anomalies_bp)
app.register_blueprint(data_pipeline_bp)
app.register_blueprint(kafka_browser_bp)
