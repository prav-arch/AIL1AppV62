#!/bin/bash

# Direct PostgreSQL 14.2 installation script
# No parameters, everything hardcoded for maximum compatibility

# Create directories
mkdir -p ~/postgres14
mkdir -p ~/pgdata14

cd ~

# Download PostgreSQL 14.2 directly from official source
wget --no-check-certificate https://ftp.postgresql.org/pub/source/v14.2/postgresql-14.2.tar.gz

# Extract files
tar -xzf postgresql-14.2.tar.gz
cd postgresql-14.2

# Configure with explicit paths
./configure --prefix=$HOME/postgres14 --without-readline

# Compile and install
make
make install

# Set permissions
chmod -R u+wx ~/postgres14
chmod -R u+wx ~/pgdata14

# Create environment file with hardcoded paths
cat > ~/.pg14env << EOL
# PostgreSQL 14.2 Environment
export PGINSTALL=$HOME/postgres14
export PGDATA=$HOME/pgdata14
export PGPORT=5432
export PATH=$HOME/postgres14/bin:$PATH
EOL

# Load environment
source ~/.pg14env

# Initialize database
$HOME/postgres14/bin/initdb -D $HOME/pgdata14 --encoding=UTF8 --no-locale

# Configure PostgreSQL
cat >> $HOME/pgdata14/postgresql.conf << EOL
# Direct configuration for PostgreSQL 14.2
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
EOL

# Set authentication method - using trust for simplicity
cat > $HOME/pgdata14/pg_hba.conf << EOL
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
EOL

# Start PostgreSQL
$HOME/postgres14/bin/pg_ctl -D $HOME/pgdata14 start

# Wait for PostgreSQL to start
sleep 5

# Create user and database
$HOME/postgres14/bin/psql -d postgres -c "CREATE ROLE l1_app_user WITH LOGIN PASSWORD 'test' CREATEDB;"
$HOME/postgres14/bin/createdb -O l1_app_user l1_app_db

# Create application env file
cat > ~/.env << EOL
# PostgreSQL 14.2 Connection Details
DATABASE_URL=postgresql://l1_app_user:test@localhost:5432/l1_app_db
PGHOST=localhost
PGPORT=5432
PGDATABASE=l1_app_db
PGUSER=l1_app_user
PGPASSWORD=test
EOL

echo "=== PostgreSQL 14.2 Installation Complete ==="
echo ""
echo "To use PostgreSQL 14.2:"
echo "1. Source environment variables: source ~/.pg14env"
echo ""
echo "2. Start PostgreSQL: ~/postgres14/bin/pg_ctl -D ~/pgdata14 start"
echo ""
echo "3. Connect to database: ~/postgres14/bin/psql -d l1_app_db -U l1_app_user"
echo ""
echo "Connection string for your application:"
echo "postgresql://l1_app_user:test@localhost:5432/l1_app_db"
echo ""
echo "If you encounter issues with compilation, check if gcc and make are available."