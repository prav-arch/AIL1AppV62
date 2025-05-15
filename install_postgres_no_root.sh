#!/bin/bash
# Simple PostgreSQL Installation Script for Replit with pgvector extension (No Root Access)
# Downloads precompiled binaries optimized for cloud environments
# Creates user l1_app_user with password 'l1' and database l1_app_db

# Set up color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Simple PostgreSQL Installation Script for Replit with pgvector${NC}"
echo -e "${YELLOW}This will install PostgreSQL with pgvector extension in your home directory${NC}\n"

# Define Installation Directory
INSTALL_DIR="$HOME/.postgres"
DATA_DIR="$INSTALL_DIR/data"
BIN_DIR="$INSTALL_DIR/bin"
LIB_DIR="$INSTALL_DIR/lib"
DOWNLOAD_DIR="$INSTALL_DIR/download"

# Create directories
mkdir -p $INSTALL_DIR
mkdir -p $DATA_DIR
mkdir -p $BIN_DIR
mkdir -p $LIB_DIR
mkdir -p $DOWNLOAD_DIR

cd $DOWNLOAD_DIR

# Download precompiled PostgreSQL binaries
echo -e "${GREEN}Downloading PostgreSQL binaries...${NC}"
curl -s --insecure https://files.postgresqlweb.com/pg_16.2_pgvector_amd64.tar.gz -o postgres.tar.gz

if [ ! -f postgres.tar.gz ] || [ $(stat -c%s postgres.tar.gz) -lt 1000000 ]; then
    echo -e "${RED}Failed to download PostgreSQL binaries.${NC}"
    echo -e "${YELLOW}Trying alternative download...${NC}"
    curl -s --insecure https://share.pgvector.org/pg_16.2_pgvector_linux_x64.tar.gz -o postgres.tar.gz
    
    if [ ! -f postgres.tar.gz ] || [ $(stat -c%s postgres.tar.gz) -lt 1000000 ]; then
        echo -e "${RED}Failed to download PostgreSQL binaries. Exiting.${NC}"
        exit 1
    fi
fi

# Extract binaries
echo -e "${GREEN}Extracting PostgreSQL binaries...${NC}"
tar -xzf postgres.tar.gz -C $INSTALL_DIR

# Initialize database cluster
echo -e "${GREEN}Initializing database cluster...${NC}"
$BIN_DIR/initdb -D $DATA_DIR

# Configure PostgreSQL
echo -e "${GREEN}Configuring PostgreSQL...${NC}"
cat > $DATA_DIR/postgresql.conf << EOF
listen_addresses = '*'
port = 5433
shared_preload_libraries = 'vector'
max_connections = 100
shared_buffers = 128MB
EOF

# Configure authentication
cat > $DATA_DIR/pg_hba.conf << EOF
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

# Create management scripts
echo -e "${GREEN}Creating management scripts...${NC}"

# Start script
cat > $INSTALL_DIR/start.sh << EOF
#!/bin/bash
export PATH=$BIN_DIR:\$PATH
export LD_LIBRARY_PATH=$LIB_DIR:\$LD_LIBRARY_PATH
$BIN_DIR/pg_ctl -D $DATA_DIR -l $INSTALL_DIR/logfile start
EOF
chmod +x $INSTALL_DIR/start.sh

# Stop script
cat > $INSTALL_DIR/stop.sh << EOF
#!/bin/bash
export PATH=$BIN_DIR:\$PATH
export LD_LIBRARY_PATH=$LIB_DIR:\$LD_LIBRARY_PATH
$BIN_DIR/pg_ctl -D $DATA_DIR stop
EOF
chmod +x $INSTALL_DIR/stop.sh

# Status script
cat > $INSTALL_DIR/status.sh << EOF
#!/bin/bash
export PATH=$BIN_DIR:\$PATH
export LD_LIBRARY_PATH=$LIB_DIR:\$LD_LIBRARY_PATH
$BIN_DIR/pg_ctl -D $DATA_DIR status
EOF
chmod +x $INSTALL_DIR/status.sh

# Environment setup script
cat > $INSTALL_DIR/env.sh << EOF
export PATH=$BIN_DIR:\$PATH
export LD_LIBRARY_PATH=$LIB_DIR:\$LD_LIBRARY_PATH
export PGDATA=$DATA_DIR
export PGHOST=localhost
export PGPORT=5433
EOF

# Start PostgreSQL
echo -e "${GREEN}Starting PostgreSQL server...${NC}"
bash $INSTALL_DIR/start.sh
sleep 5

# Check if PostgreSQL is running
if ! bash $INSTALL_DIR/status.sh > /dev/null; then
    echo -e "${RED}Failed to start PostgreSQL. Please check the logs at $INSTALL_DIR/logfile${NC}"
    exit 1
fi

# Create user and database
echo -e "${GREEN}Creating user l1_app_user and database l1_app_db...${NC}"
export PATH=$BIN_DIR:$PATH
export LD_LIBRARY_PATH=$LIB_DIR:$LD_LIBRARY_PATH

$BIN_DIR/psql -p 5433 -d postgres << EOF
CREATE USER l1_app_user WITH PASSWORD 'l1';
CREATE DATABASE l1_app_db OWNER l1_app_user;
ALTER USER l1_app_user WITH SUPERUSER;
EOF

# Setup pgvector extension and tables
echo -e "${GREEN}Setting up pgvector extension and tables...${NC}"
$BIN_DIR/psql -p 5433 -d l1_app_db << EOF
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table for document embeddings
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    embedding vector(1536) NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index for faster similarity searches
CREATE INDEX IF NOT EXISTS document_embeddings_idx ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Grant permissions to l1_app_user
GRANT ALL PRIVILEGES ON TABLE document_embeddings TO l1_app_user;
GRANT ALL PRIVILEGES ON SEQUENCE document_embeddings_id_seq TO l1_app_user;
EOF

# Update .env file with PostgreSQL connection information
echo -e "${GREEN}Updating .env file with PostgreSQL connection information...${NC}"
if [ -f ".env" ]; then
    # Backup existing .env file
    cp .env .env.bak
    
    # Remove existing PostgreSQL related variables
    grep -v "^PG" .env > .env.tmp
    
    # Add new PostgreSQL variables
    cat >> .env.tmp << EOF

# PostgreSQL with pgvector configuration
PGUSER=l1_app_user
PGPASSWORD=l1
PGDATABASE=l1_app_db
PGHOST=localhost
PGPORT=5433
DATABASE_URL=postgresql://l1_app_user:l1@localhost:5433/l1_app_db
EOF
    
    # Replace old .env with new one
    mv .env.tmp .env
else
    # Create new .env file
    cat > .env << EOF
# PostgreSQL with pgvector configuration
PGUSER=l1_app_user
PGPASSWORD=l1
PGDATABASE=l1_app_db
PGHOST=localhost
PGPORT=5433
DATABASE_URL=postgresql://l1_app_user:l1@localhost:5433/l1_app_db
EOF
fi

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}PostgreSQL with pgvector extension is installed and running on port 5433${NC}"
echo -e "${YELLOW}User: l1_app_user | Password: l1 | Database: l1_app_db${NC}"
echo ""
echo "To start/stop PostgreSQL:"
echo "  - Start: bash $INSTALL_DIR/start.sh"
echo "  - Stop: bash $INSTALL_DIR/stop.sh"
echo "  - Status: bash $INSTALL_DIR/status.sh"
echo ""
echo "To load PostgreSQL environment variables:"
echo "  source $INSTALL_DIR/env.sh"
echo ""
echo "Connection string:"
echo "  postgresql://l1_app_user:l1@localhost:5433/l1_app_db"
echo ""
echo "Connection information has been added to your .env file"