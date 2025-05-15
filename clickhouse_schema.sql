-- ClickHouse 18.16.1 Database Schema
-- This schema is compatible with ClickHouse 18.16.1 and doesn't use any
-- vector-specific features (which will be handled by FAISS instead)

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS l1_app_db;

-- Use the database
USE l1_app_db;

-- Documents table to store document metadata
CREATE TABLE IF NOT EXISTS documents
(
    id String,
    name String,
    description String,
    metadata String,
    file_path String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Document chunks table to store text chunks
-- Note: embeddings are NOT stored in ClickHouse, only the chunk text
-- The embeddings will be generated and stored in FAISS separately
CREATE TABLE IF NOT EXISTS document_chunks
(
    id UInt64,
    document_id String,
    chunk_index UInt32,
    chunk_text String,
    metadata String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, chunk_index);

-- Create an index to speed up lookups by document_id
ALTER TABLE document_chunks ADD INDEX idx_document_id document_id TYPE minmax GRANULARITY 8192;

-- Vector database stats for tracking
CREATE TABLE IF NOT EXISTS vector_db_stats
(
    id UInt8,
    documents_count UInt32 DEFAULT 0,
    chunks_count UInt32 DEFAULT 0,
    vector_dim UInt16,
    last_modified DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY id;

-- Insert initial stats
INSERT INTO vector_db_stats (id, vector_dim) VALUES (1, 384) ON DUPLICATE KEY UPDATE last_modified = now();

-- Users table (if needed by your application)
CREATE TABLE IF NOT EXISTS users
(
    id String,
    username String,
    email String,
    password_hash String,
    is_active UInt8 DEFAULT 1,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Logs table for application logs
CREATE TABLE IF NOT EXISTS app_logs
(
    id UInt64,
    timestamp DateTime DEFAULT now(),
    level String,
    message String,
    component String,
    details String
) ENGINE = MergeTree()
ORDER BY (timestamp, level);