#!/bin/bash
# Very Simple PostgreSQL Installation Script
# Focused on direct download of binaries to the correct locations

# Set up color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Very Simple PostgreSQL Installation for Replit${NC}"
echo -e "${YELLOW}This script will download PostgreSQL binaries directly${NC}\n"

# Set directory structure
PG_HOME=$HOME/.postgres
mkdir -p $PG_HOME/bin
mkdir -p $PG_HOME/lib
mkdir -p $PG_HOME/share
mkdir -p $PG_HOME/data
mkdir -p $PG_HOME/logs
mkdir -p $PG_HOME/tmp

cd $PG_HOME/tmp

# Download individual binaries instead of the full package
echo -e "${GREEN}Downloading essential PostgreSQL binaries...${NC}"

# List of essential binaries
BINARIES=(
  "initdb"
  "postgres"
  "pg_ctl"
  "psql"
  "createdb"
  "createuser"
  "pg_dump"
  "pg_restore"
)

# Download each binary directly
for binary in "${BINARIES[@]}"; do
  echo -e "${YELLOW}Downloading $binary...${NC}"
  URL="https://ftp.postgresql.org/pub/binary/v16.2/linux/binaries/$binary"
  curl -L --insecure -s $URL -o $PG_HOME/bin/$binary
  chmod +x $PG_HOME/bin/$binary
done

# Create library symlinks needed by binaries
echo -e "${GREEN}Setting up library symlinks...${NC}"
ln -sf /lib64/libpthread.so.0 $PG_HOME/lib/libpthread.so
ln -sf /lib64/libc.so.6 $PG_HOME/lib/libc.so
ln -sf /usr/lib64/libz.so.1 $PG_HOME/lib/libz.so

# Create basic configuration
echo -e "${GREEN}Creating configuration...${NC}"
cat > $PG_HOME/data/postgresql.conf << EOF
listen_addresses = '*'
port = 5433
max_connections = 100
shared_buffers = 128MB
EOF

# Create management scripts
echo -e "${GREEN}Creating management scripts...${NC}"

# Start script
cat > $PG_HOME/start.sh << EOF
#!/bin/bash
export PATH=$PG_HOME/bin:\$PATH
export LD_LIBRARY_PATH=$PG_HOME/lib:\$LD_LIBRARY_PATH
$PG_HOME/bin/pg_ctl -D $PG_HOME/data -l $PG_HOME/logs/server.log start
EOF
chmod +x $PG_HOME/start.sh

# Stop script
cat > $PG_HOME/stop.sh << EOF
#!/bin/bash
export PATH=$PG_HOME/bin:\$PATH
export LD_LIBRARY_PATH=$PG_HOME/lib:\$LD_LIBRARY_PATH
$PG_HOME/bin/pg_ctl -D $PG_HOME/data stop
EOF
chmod +x $PG_HOME/stop.sh

# Status script
cat > $PG_HOME/status.sh << EOF
#!/bin/bash
export PATH=$PG_HOME/bin:\$PATH
export LD_LIBRARY_PATH=$PG_HOME/lib:\$LD_LIBRARY_PATH
$PG_HOME/bin/pg_ctl -D $PG_HOME/data status
EOF
chmod +x $PG_HOME/status.sh

# Env script
cat > $PG_HOME/env.sh << EOF
export PATH=$PG_HOME/bin:\$PATH
export LD_LIBRARY_PATH=$PG_HOME/lib:\$LD_LIBRARY_PATH
export PGDATA=$PG_HOME/data
export PGHOST=localhost
export PGPORT=5433
export PGUSER=l1_app_user
export PGPASSWORD=l1
export PGDATABASE=l1_app_db
EOF

# Initialize database
echo -e "${GREEN}Initializing database...${NC}"
$PG_HOME/bin/initdb -D $PG_HOME/data 2>/dev/null || echo -e "${YELLOW}Initialization skipped - possibly already initialized${NC}"

# Start server and create user/database
echo -e "${GREEN}Starting PostgreSQL and creating user/database...${NC}"
$PG_HOME/start.sh

# Wait a bit for the server to start
sleep 3

# Create user and database
$PG_HOME/bin/createuser -p 5433 -s l1_app_user 2>/dev/null || echo -e "${YELLOW}User creation skipped - may already exist${NC}"
$PG_HOME/bin/createdb -p 5433 -O l1_app_user l1_app_db 2>/dev/null || echo -e "${YELLOW}Database creation skipped - may already exist${NC}"

echo -e "${GREEN}PostgreSQL set up completed${NC}"
echo -e "${YELLOW}To use PostgreSQL:${NC}"
echo "  - Start: $PG_HOME/start.sh"
echo "  - Stop: $PG_HOME/stop.sh"
echo "  - Status: $PG_HOME/status.sh"
echo "  - Environment: source $PG_HOME/env.sh"
echo 
echo -e "${YELLOW}Connection string:${NC}"
echo "postgresql://l1_app_user:l1@localhost:5433/l1_app_db"