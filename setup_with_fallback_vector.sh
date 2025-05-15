#!/bin/bash

# Setup script with vector search fallback for GPU servers
# Uses FAISS for vector operations instead of pgvector

# Set variables
USER_HOME=$HOME
SQLITE_DB_FILE="$USER_HOME/temp_db.sqlite"
DB_USER="l1_app_user"
DB_PASSWORD="test"
DB_NAME="l1_app_db"

# Create .env file with database and vector configuration
ENV_FILE="$USER_HOME/.env"

echo "# Creating database environment configuration"
cat > $ENV_FILE << EOL
# Database and vector search configuration

# SQLite connection (currently in use)
DATABASE_URL=sqlite:///$SQLITE_DB_FILE

# PostgreSQL connection (for future use)
# DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Vector storage type - using FAISS instead of pgvector
VECTOR_STORAGE=faiss

# Path to store FAISS vector indices
VECTOR_DIR=$USER_HOME/vector_indices
EOL

# Create directory for FAISS indices
mkdir -p $USER_HOME/vector_indices

echo "Created database configuration at: $ENV_FILE"
echo ""
echo "VECTOR STORAGE CONFIGURATION"
echo "============================"
echo "Since pgvector requires PostgreSQL, this script configures:"
echo ""
echo "1. SQLite for regular database operations"
echo "2. FAISS for vector similarity search (instead of pgvector)"
echo ""
echo "FAISS is a library for efficient similarity search that works"
echo "without requiring PostgreSQL. The application will store vector"
echo "indices in: $USER_HOME/vector_indices"
echo ""
echo "IMPORTANT: For production use, PostgreSQL with pgvector"
echo "is still recommended, but FAISS should work for development"
echo "and testing purposes on your GPU server."
echo ""
echo "To use this configuration:"
echo "1. Source the environment file: source $ENV_FILE"
echo "2. The application will automatically use SQLite + FAISS"
echo ""
echo "TECHNICAL INFORMATION:"
echo "FAISS (Facebook AI Similarity Search) is designed for"
echo "efficient similarity search and clustering of dense vectors."
echo "It's actually well-optimized for GPU operations, which"
echo "could be beneficial on your GPU server."