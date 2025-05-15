#!/bin/bash
# Setup script for local PostgreSQL environment variables

# Set up color output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up local PostgreSQL environment variables${NC}"

# Create or update .env file
cat > .env << EOF
# PostgreSQL Connection Information
DATABASE_URL=postgresql://l1_app_user:l1@localhost:5433/l1_app_db
PGUSER=l1_app_user
PGPASSWORD=l1
PGDATABASE=l1_app_db
PGHOST=localhost
PGPORT=5433

# Application Settings
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
EOF

echo -e "${GREEN}.env file created successfully!${NC}"
echo -e "${YELLOW}Environment variables:${NC}"
cat .env

echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Make sure PostgreSQL is running using ~/start_postgres.sh"
echo "2. Test the database connection using: python test_local_db_connection.py"
echo "3. Restart your application to apply the new settings"