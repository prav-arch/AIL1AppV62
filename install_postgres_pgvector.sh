#!/bin/bash
# PostgreSQL 16.2 Installation Script with pgvector extension (No Root Access)
# Creates user l1_app_user with password 'l1' and database l1_app_db

# Set up color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PostgreSQL 16.2 Installation Script with pgvector (No Root Required)${NC}"
echo -e "${YELLOW}This will install PostgreSQL 16.2 with pgvector extension in your home directory${NC}\n"

# Set environment variables
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH

# Create installation directories
echo -e "${GREEN}Creating installation directories...${NC}"
mkdir -p $PGROOT
mkdir -p $PGDATA
mkdir -p $HOME/postgresql/downloads
mkdir -p $HOME/postgresql/logs
mkdir -p $HOME/postgresql/backups
mkdir -p $HOME/postgresql/extensions

# Change to downloads directory
cd $HOME/postgresql/downloads

# Download PostgreSQL source
echo -e "${GREEN}Downloading PostgreSQL 16.2 source...${NC}"
wget -q https://ftp.postgresql.org/pub/source/v16.2/postgresql-16.2.tar.gz
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to download PostgreSQL source. Check your internet connection.${NC}"
    exit 1
fi

# Extract source
echo -e "${GREEN}Extracting PostgreSQL source files...${NC}"
tar -xzf postgresql-16.2.tar.gz

# Download pgvector source
echo -e "${GREEN}Downloading pgvector extension...${NC}"
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to download pgvector source. Check your internet connection or if git is installed.${NC}"
    exit 1
fi

# Configure and compile PostgreSQL
echo -e "${GREEN}Configuring PostgreSQL...${NC}"
cd postgresql-16.2
./configure --prefix=$PGROOT --without-readline
if [ $? -ne 0 ]; then
    echo -e "${RED}Configuration failed. Please check the output above.${NC}"
    exit 1
fi

echo -e "${GREEN}Compiling PostgreSQL (this may take a while)...${NC}"
make -j4
if [ $? -ne 0 ]; then
    echo -e "${RED}Compilation failed. Please check the output above.${NC}"
    exit 1
fi

echo -e "${GREEN}Installing PostgreSQL...${NC}"
make install
if [ $? -ne 0 ]; then
    echo -e "${RED}Installation failed. Please check the output above.${NC}"
    exit 1
fi

# Build and install pgvector extension
echo -e "${GREEN}Building pgvector extension...${NC}"
cd ../pgvector
export PG_CONFIG=$PGROOT/bin/pg_config
make
if [ $? -ne 0 ]; then
    echo -e "${RED}pgvector build failed. Please check the output above.${NC}"
    exit 1
fi

echo -e "${GREEN}Installing pgvector extension...${NC}"
make install
if [ $? -ne 0 ]; then
    echo -e "${RED}pgvector installation failed. Please check the output above.${NC}"
    exit 1
fi

# Initialize database
echo -e "${GREEN}Initializing database cluster...${NC}"
$PGROOT/bin/initdb -D $PGDATA
if [ $? -ne 0 ]; then
    echo -e "${RED}Database initialization failed. Please check the output above.${NC}"
    exit 1
fi

# Configure PostgreSQL
echo -e "${GREEN}Configuring PostgreSQL...${NC}"
cat > $PGDATA/postgresql.conf << EOF
# Basic Configuration
listen_addresses = '*'
port = 5433
max_connections = 100

# Memory Configuration
shared_buffers = 512MB
work_mem = 32MB
maintenance_work_mem = 64MB

# Logging
logging_collector = on
log_directory = '$HOME/postgresql/logs'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 0
log_min_messages = warning

# Query tuning
random_page_cost = 1.1
effective_cache_size = 1GB

# Enable extensions
shared_preload_libraries = 'vector'
EOF

# Configure client authentication
cat > $PGDATA/pg_hba.conf << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

# Create startup script
cat > $HOME/start_postgres.sh << 'EOF'
#!/bin/bash
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH

pg_ctl -D $PGDATA -l $HOME/postgresql/logs/server.log start
EOF
chmod +x $HOME/start_postgres.sh

# Create shutdown script
cat > $HOME/stop_postgres.sh << 'EOF'
#!/bin/bash
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH

pg_ctl -D $PGDATA stop
EOF
chmod +x $HOME/stop_postgres.sh

# Create status script
cat > $HOME/status_postgres.sh << 'EOF'
#!/bin/bash
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH

pg_ctl -D $PGDATA status
EOF
chmod +x $HOME/status_postgres.sh

# Create backup script
cat > $HOME/backup_postgres.sh << 'EOF'
#!/bin/bash
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH

BACKUP_DIR=$HOME/postgresql/backups
DATE_FORMAT=$(date +%Y%m%d_%H%M%S)

echo "Creating backup of all databases..."
$PGROOT/bin/pg_dumpall -p 5433 -f $BACKUP_DIR/full_backup_$DATE_FORMAT.sql

echo "Done. Backup saved to $BACKUP_DIR/full_backup_$DATE_FORMAT.sql"
EOF
chmod +x $HOME/backup_postgres.sh

# Add environment settings to .bashrc
echo -e "${GREEN}Adding PostgreSQL environment to .bashrc...${NC}"
cat >> $HOME/.bashrc << 'EOF'

# PostgreSQL environment variables
export PGROOT=$HOME/postgresql/install
export PGDATA=$HOME/postgresql/data
export PATH=$PGROOT/bin:$PATH
export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH
EOF

# Source updated environment variables
source $HOME/.bashrc

# Start PostgreSQL server
echo -e "${GREEN}Starting PostgreSQL server...${NC}"
$HOME/start_postgres.sh

# Wait for PostgreSQL to start
echo -e "${YELLOW}Waiting for PostgreSQL to start...${NC}"
sleep 5

# Create user, database, and enable pgvector
echo -e "${GREEN}Creating user l1_app_user, database l1_app_db, and enabling pgvector...${NC}"
$PGROOT/bin/psql -p 5433 -d postgres << EOF
CREATE USER l1_app_user WITH PASSWORD 'l1';
CREATE DATABASE l1_app_db OWNER l1_app_user;
ALTER USER l1_app_user WITH SUPERUSER;
EOF

# Connect to the l1_app_db database and enable pgvector
$PGROOT/bin/psql -p 5433 -d l1_app_db << EOF
CREATE EXTENSION vector;

-- Create a table for document embeddings
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    embedding vector(1536) NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index for faster similarity searches
CREATE INDEX document_embeddings_idx ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Grant permissions to l1_app_user
GRANT ALL PRIVILEGES ON TABLE document_embeddings TO l1_app_user;
GRANT ALL PRIVILEGES ON SEQUENCE document_embeddings_id_seq TO l1_app_user;
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create user, database, or enable pgvector. Check if PostgreSQL is running.${NC}"
    exit 1
fi

# Create connection string example
CONNECTION_STRING="postgresql://l1_app_user:l1@localhost:5433/l1_app_db"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}Connection string for your application:${NC}"
echo $CONNECTION_STRING
echo
echo -e "${YELLOW}PostgreSQL with pgvector is now installed and running!${NC}"
echo "The pgvector extension has been enabled and a document_embeddings table has been created."
echo
echo -e "${YELLOW}To manage PostgreSQL:${NC}"
echo "  - Start server: ~/start_postgres.sh"
echo "  - Stop server: ~/stop_postgres.sh"
echo "  - Check status: ~/status_postgres.sh"
echo "  - Create backup: ~/backup_postgres.sh"
echo
echo -e "${YELLOW}To connect to the database:${NC}"
echo "  PGPASSWORD=l1 psql -h localhost -p 5433 -U l1_app_user -d l1_app_db"
echo
echo -e "${YELLOW}Quick pgvector test:${NC}"
echo "  PGPASSWORD=l1 psql -h localhost -p 5433 -U l1_app_user -d l1_app_db -c \"INSERT INTO document_embeddings (document_id, chunk_id, embedding, text) VALUES ('test-doc', 1, '[0.1, 0.2, 0.3]'::vector, 'Test document'); SELECT * FROM document_embeddings;\""