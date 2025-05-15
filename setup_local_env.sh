#!/bin/bash
# Setup local environment variables for PostgreSQL with pgvector

# Set up color output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up PostgreSQL environment variables...${NC}"

# Check if PostgreSQL is installed in ~/.postgres
if [ -d "$HOME/.postgres" ]; then
    # Setup for binary installation
    export PATH=$HOME/.postgres/bin:$PATH
    export LD_LIBRARY_PATH=$HOME/.postgres/lib:$LD_LIBRARY_PATH
    export PGDATA=$HOME/.postgres/data
    export PGHOST=localhost
    export PGPORT=5433
    export PGUSER=l1_app_user
    export PGPASSWORD=l1
    export PGDATABASE=l1_app_db
    export DATABASE_URL="postgresql://l1_app_user:l1@localhost:5433/l1_app_db"
    
    echo -e "${YELLOW}Using local PostgreSQL installation in ~/.postgres${NC}"
# Check if PostgreSQL is installed in ~/postgresql
elif [ -d "$HOME/postgresql" ]; then
    # Setup for source installation
    export PGROOT=$HOME/postgresql/install
    export PGDATA=$HOME/postgresql/data
    export PATH=$PGROOT/bin:$PATH
    export LD_LIBRARY_PATH=$PGROOT/lib:$LD_LIBRARY_PATH
    export PGHOST=localhost
    export PGPORT=5433
    export PGUSER=l1_app_user
    export PGPASSWORD=l1
    export PGDATABASE=l1_app_db
    export DATABASE_URL="postgresql://l1_app_user:l1@localhost:5433/l1_app_db"
    
    echo -e "${YELLOW}Using local PostgreSQL installation in ~/postgresql${NC}"
else
    # Use cloud PostgreSQL if local installation not found
    echo -e "${YELLOW}Local PostgreSQL installation not found.${NC}"
    echo -e "${YELLOW}Using cloud PostgreSQL instance from .env file.${NC}"
fi

echo -e "${GREEN}Environment variables set:${NC}"
echo "PGHOST=$PGHOST"
echo "PGPORT=$PGPORT"
echo "PGUSER=$PGUSER"
echo "PGDATABASE=$PGDATABASE"
echo "DATABASE_URL=$DATABASE_URL"
echo ""
echo -e "${YELLOW}You can now connect to PostgreSQL using:${NC}"
echo "psql -d l1_app_db"
echo ""
echo -e "${YELLOW}To use these variables in your application, source this script:${NC}"
echo "source ./setup_local_env.sh"