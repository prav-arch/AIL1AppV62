#!/bin/bash

# Simple PostgreSQL 14.2 installation script (no root required, no pgvector)
# This script installs PostgreSQL without requiring system privileges

# Configuration
PG_VERSION="14.2"
PG_ARCH="x64"  # Change to arm64 if needed
INSTALL_DIR="$HOME/postgres"
DATA_DIR="$HOME/pgdata"
APP_USER="l1_app_user"
APP_PASSWORD="test"
APP_DB="l1_app_db"
PORT=5432  # Change if standard port is blocked by security

echo "=== PostgreSQL $PG_VERSION Installation (No Root Required) ==="
echo "User home: $HOME"
echo "Install location: $INSTALL_DIR"
echo "Data directory: $DATA_DIR"
echo "Database port: $PORT"

# Create necessary directories
mkdir -p "$INSTALL_DIR" "$DATA_DIR"
cd "$HOME"

# Download PostgreSQL binaries (if internet is available)
echo "Downloading PostgreSQL $PG_VERSION binaries..."
wget -q --no-check-certificate https://get.enterprisedb.com/postgresql/postgresql-$PG_VERSION-1-linux-$PG_ARCH-binaries.tar.gz

# Extract PostgreSQL
echo "Extracting PostgreSQL..."
tar -xzf postgresql-$PG_VERSION-1-linux-$PG_ARCH-binaries.tar.gz -C "$INSTALL_DIR" --strip-components=1

# Set permissions
chmod -R u+wx "$INSTALL_DIR"
chmod -R u+wx "$DATA_DIR"

# Set environment variables
echo "Setting up environment variables..."
cat > "$HOME/.pgenv" << EOL
# PostgreSQL Environment Variables
export PGINSTALL="$INSTALL_DIR"
export PGDATA="$DATA_DIR"
export PGPORT="$PORT"
export PATH="\$PGINSTALL/bin:\$PATH"
EOL

# Source the environment file
source "$HOME/.pgenv"

# Initialize the database
echo "Initializing PostgreSQL database..."
"$INSTALL_DIR/bin/initdb" -D "$DATA_DIR" --encoding=UTF8 --no-locale

# Configure postgresql.conf for non-standard security environments
echo "Configuring PostgreSQL..."
cat >> "$DATA_DIR/postgresql.conf" << EOL
# Security-restricted environment settings
listen_addresses = 'localhost'
port = $PORT
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
EOL

# Configure authentication
cat > "$DATA_DIR/pg_hba.conf" << EOL
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
EOL

# Start PostgreSQL
echo "Starting PostgreSQL server..."
"$INSTALL_DIR/bin/pg_ctl" -D "$DATA_DIR" start

# Wait for PostgreSQL to start
sleep 5

# Create role and database
echo "Creating application database and user..."
"$INSTALL_DIR/bin/psql" -p "$PORT" -d postgres -c "CREATE ROLE $APP_USER WITH LOGIN PASSWORD '$APP_PASSWORD' CREATEDB;"
"$INSTALL_DIR/bin/createdb" -p "$PORT" -O "$APP_USER" "$APP_DB"

# Create environment file for the application
cat > "$HOME/.env" << EOL
# PostgreSQL Connection Details
DATABASE_URL=postgresql://$APP_USER:$APP_PASSWORD@localhost:$PORT/$APP_DB
PGHOST=localhost
PGPORT=$PORT
PGDATABASE=$APP_DB
PGUSER=$APP_USER
PGPASSWORD=$APP_PASSWORD
EOL

echo "=== Installation Complete ==="
echo ""
echo "To use PostgreSQL in your environment:"
echo "1. Add this line to your .bashrc or .profile:"
echo "   source $HOME/.pgenv"
echo ""
echo "2. Start PostgreSQL (if not already running):"
echo "   $INSTALL_DIR/bin/pg_ctl -D $DATA_DIR start"
echo ""
echo "3. Stop PostgreSQL when done:"
echo "   $INSTALL_DIR/bin/pg_ctl -D $DATA_DIR stop"
echo ""
echo "4. Connect to your database:"
echo "   $INSTALL_DIR/bin/psql -p $PORT -d $APP_DB -U $APP_USER"
echo ""
echo "Database connection string for your application:"
echo "postgresql://$APP_USER:$APP_PASSWORD@localhost:$PORT/$APP_DB"
echo ""
echo "Environment file with all connection details created at:"
echo "$HOME/.env"
echo ""
echo "IMPORTANT: In security-restricted environments, you may need to:"
echo "- Use a non-standard port if port $PORT is blocked"
echo "- Set up SSH tunneling if direct database access is restricted"