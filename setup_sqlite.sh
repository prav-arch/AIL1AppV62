#!/bin/bash

# Simple script to set up SQLite database for the application
# This requires no installation or internet access

# Directory for the database
DB_DIR="$HOME/sqlite_db"
mkdir -p $DB_DIR

# Database file location
DB_FILE="$DB_DIR/app.db"

# Check if sqlite3 is available
if ! command -v sqlite3 &> /dev/null; then
    echo "Error: sqlite3 command not found."
    echo "Please check if SQLite is installed on your system."
    exit 1
fi

echo "Setting up SQLite database at: $DB_FILE"

# Create a basic schema and tables (if needed)
# This is just an example - adjust according to your application's needs
sqlite3 $DB_FILE <<EOF
-- Create tables for a vector database
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    metadata TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    chunk_text TEXT,
    embedding_json TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS vector_db_stats (
    id INTEGER PRIMARY KEY,
    documents_count INTEGER DEFAULT 0,
    chunks_count INTEGER DEFAULT 0,
    vector_dim INTEGER,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial stats
INSERT OR IGNORE INTO vector_db_stats (id, vector_dim)
VALUES (1, 384);

-- Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
EOF

# Create environment file
ENV_FILE="$HOME/.db_env"
cat > $ENV_FILE << EOF
# Database Environment Variables
export DATABASE_URL="sqlite:///$DB_FILE"
export VECTOR_STORAGE="sqlite"
EOF

echo "=========================================================="
echo "SQLite database setup complete!"
echo ""
echo "Database location: $DB_FILE"
echo ""
echo "Environment file created at: $ENV_FILE"
echo "To load database environment variables, run:"
echo "source $ENV_FILE"
echo ""
echo "For your application, use the connection string:"
echo "sqlite:///$DB_FILE"
echo "=========================================================="
echo ""
echo "USAGE GUIDE:"
echo "-----------"
echo "1. Connect to database: sqlite3 $DB_FILE"
echo "2. Run SQL queries: sqlite3 $DB_FILE \"SELECT * FROM documents;\""
echo "3. Import data: sqlite3 $DB_FILE \".import data.csv table_name\""
echo "4. Backup database: cp $DB_FILE $DB_FILE.backup"
echo ""
echo "In your application code, update the connection string to:"
echo "DATABASE_URL=sqlite:///$DB_FILE"