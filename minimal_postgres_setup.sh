#!/bin/bash

# Minimal PostgreSQL setup for GPU servers
# Uses SQLite as a temporary fallback until PostgreSQL is available

# Set variables
USER_HOME=$HOME
SQLITE_DB_FILE="$USER_HOME/temp_db.sqlite"
DB_USER="l1_app_user"
DB_PASSWORD="test"
DB_NAME="l1_app_db"

# Create .env file with database configuration
ENV_FILE="$USER_HOME/.env"

echo "# Creating database environment configuration"
cat > $ENV_FILE << EOL
# Database configuration
# Using SQLite as temporary storage until PostgreSQL is available

# SQLite connection (currently in use)
DATABASE_URL=sqlite:///$SQLITE_DB_FILE

# PostgreSQL connection (for future use)
# DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Vector storage type
VECTOR_STORAGE=sqlite
EOL

echo "Created database configuration at: $ENV_FILE"
echo ""
echo "IMPORTANT INSTRUCTIONS FOR YOUR GPU SERVER:"
echo "=========================================="
echo "1. This script has set up a minimal environment using SQLite as"
echo "   a temporary database since PostgreSQL installation requires"
echo "   internet access or pre-built binaries."
echo ""
echo "2. To use the temporary SQLite database:"
echo "   - Source the environment file: source $ENV_FILE"
echo "   - The application will automatically use SQLite"
echo ""
echo "3. RECOMMENDED: For a proper PostgreSQL installation on your GPU server,"
echo "   please contact your system administrator with these options:"
echo ""
echo "   A) Request PostgreSQL access if it's already installed centrally"
echo "      (this is common on many GPU clusters)"
echo ""
echo "   B) Ask them to install PostgreSQL 16.2 for your user account"
echo ""
echo "   C) Download PostgreSQL binaries on a machine with internet access"
echo "      and copy them to your GPU server using scp or rsync"
echo ""
echo "4. Once you have PostgreSQL installed, update the .env file"
echo "   to use the PostgreSQL connection string instead of SQLite"
echo ""
echo "Note: Your application should work with SQLite for development"
echo "but PostgreSQL is recommended for production use."