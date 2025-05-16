"""
Database models for the application
"""

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

class LLMQuery(db.Model):
    """Model to store LLM queries"""
    __tablename__ = 'llm_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=True)
    agent_type = db.Column(db.String(50), nullable=True)
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=1024)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time_ms = db.Column(db.Integer, nullable=True)
    prompt_tokens = db.Column(db.Integer, nullable=True)
    completion_tokens = db.Column(db.Integer, nullable=True)
    error = db.Column(db.Text, nullable=True)
    used_rag = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'query_text': self.query_text,
            'response_text': self.response_text,
            'agent_type': self.agent_type,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'response_time_ms': self.response_time_ms,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'error': self.error,
            'used_rag': self.used_rag
        }

class Document(db.Model):
    """Model to store documents for RAG"""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    meta_data = db.Column(db.Text, nullable=True)  # JSON string - renamed to avoid reserved word
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary"""
        chunks_count = 0
        if self.chunks is not None:
            chunks_count = db.session.query(DocumentChunk).filter_by(document_id=self.id).count()
            
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'metadata': self.meta_data,  # Keep the original key in the output
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'chunks_count': chunks_count
        }

class DocumentChunk(db.Model):
    """Model to store document chunks for vector search"""
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    meta_data = db.Column(db.Text, nullable=True)  # JSON string - renamed to avoid reserved word
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'chunk_text': self.chunk_text,
            'metadata': self.meta_data,  # Keep the original key in the output
            'created_at': self.created_at.isoformat() if self.created_at else None
        }