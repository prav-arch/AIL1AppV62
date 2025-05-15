"""
Database models for the AI Assistant Platform
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    documents = db.relationship('Document', backref='user', lazy=True)

class Conversation(db.Model):
    """Model for LLM conversations"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    """Model for individual messages in a conversation"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'))
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', or 'system'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    """Model for documents in the RAG system"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    source = db.Column(db.String(255))  # 'upload', 'web_scrape', etc.
    source_url = db.Column(db.Text)  # for scraped documents
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')

class DocumentChunk(db.Model):
    """Model for document chunks with embeddings"""
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'))
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    # For PostgreSQL with pgvector, we'll store the embedding as a binary
    embedding_data = db.Column(db.LargeBinary)  # Serialized vector, can be adapted for pgvector
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RagSearch(db.Model):
    """Model to track RAG search history"""
    __tablename__ = 'rag_searches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    query = db.Column(db.Text, nullable=False)
    top_k = db.Column(db.Integer)
    search_time = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimeSeries(db.Model):
    """Model for time series data used in anomaly detection"""
    __tablename__ = 'time_series'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    tags = db.Column(JSONB)  # store additional metadata
    
    anomalies = db.relationship('Anomaly', backref='time_series', lazy=True)

class Anomaly(db.Model):
    """Model for detected anomalies"""
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    time_series_id = db.Column(db.Integer, db.ForeignKey('time_series.id'))
    algorithm = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    severity = db.Column(db.Float, nullable=False)  # 0-1 scale
    score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='open')  # 'open', 'acknowledged', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    alerts = db.relationship('AnomalyAlert', backref='anomaly', lazy=True, cascade='all, delete-orphan')

class AnomalyAlert(db.Model):
    """Model for anomaly alerts"""
    __tablename__ = 'anomaly_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    anomaly_id = db.Column(db.Integer, db.ForeignKey('anomalies.id', ondelete='CASCADE'))
    alert_type = db.Column(db.String(50), nullable=False)  # 'email', 'slack', etc.
    recipient = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)

class PipelineJob(db.Model):
    """Model for data pipeline jobs"""
    __tablename__ = 'pipeline_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    schedule = db.Column(db.String(100))  # cron expression
    pipeline_type = db.Column(db.String(50), nullable=False)  # 'nifi', 'airflow', etc.
    config = db.Column(JSONB)  # configuration details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    runs = db.relationship('JobRun', backref='job', lazy=True, cascade='all, delete-orphan')

class JobRun(db.Model):
    """Model for pipeline job runs"""
    __tablename__ = 'job_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('pipeline_jobs.id', ondelete='CASCADE'))
    status = db.Column(db.String(50), nullable=False)  # 'running', 'success', 'failed', etc.
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    logs = db.Column(db.Text)
    error_message = db.Column(db.Text)

class KafkaTopic(db.Model):
    """Model for Kafka topics"""
    __tablename__ = 'kafka_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    partition_count = db.Column(db.Integer, nullable=False)
    replication_factor = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('KafkaMessage', backref='topic', lazy=True)

class KafkaConsumerGroup(db.Model):
    """Model for Kafka consumer groups"""
    __tablename__ = 'kafka_consumer_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KafkaMessage(db.Model):
    """Model for stored Kafka messages"""
    __tablename__ = 'kafka_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('kafka_topics.id', ondelete='CASCADE'))
    partition = db.Column(db.Integer, nullable=False)
    offset = db.Column(db.BigInteger, nullable=False)
    key = db.Column(db.Text)
    value = db.Column(db.Text)
    headers = db.Column(JSONB)
    timestamp = db.Column(db.DateTime, nullable=False)

class Setting(db.Model):
    """Model for application settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    
    __table_args__ = (db.UniqueConstraint('category', 'key'),)

class ActivityLog(db.Model):
    """Model for activity logs"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100))  # e.g., 'document', 'anomaly', etc.
    entity_id = db.Column(db.Integer)
    details = db.Column(JSONB)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)