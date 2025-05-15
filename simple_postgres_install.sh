#!/bin/bash

# Simple PostgreSQL installation using pre-compiled binaries
# This doesn't require compilation tools and is much faster

# Set up environment variables for local installation
USER_HOME=$HOME
INSTALL_DIR=$USER_HOME/postgres16
PG_VERSION=16.2
PGDATA=$INSTALL_DIR/data
PATH=$INSTALL_DIR/bin:$PATH
export PGDATA PATH

# Database credentials as requested
DB_USER="l1_app_user"
DB_PASSWORD="test"
DB_NAME="l1_app_db"

echo "Creating installation directory..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Determine system architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
  POSTGRES_ARCH="linux-x64"
elif [ "$ARCH" = "aarch64" ]; then
  POSTGRES_ARCH="linux-arm64"
else
  echo "Unsupported architecture: $ARCH"
  echo "This script supports x86_64 and aarch64 architectures."
  exit 1
fi

# Use PostgreSQL official download mirror
echo "Downloading PostgreSQL $PG_VERSION for $ARCH..."
if [ "$ARCH" = "x86_64" ]; then
  # For x86_64
  wget --no-check-certificate https://ftp.postgresql.org/pub/binary/v$PG_VERSION/linux-x64/postgresql-$PG_VERSION-linux-x64.tar.gz
elif [ "$ARCH" = "aarch64" ]; then
  # For ARM64
  wget --no-check-certificate https://ftp.postgresql.org/pub/binary/v$PG_VERSION/linux-arm64/postgresql-$PG_VERSION-linux-arm64.tar.gz
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to download PostgreSQL binaries."
    echo "Please check your internet connection or try again later."
    exit 1
fi

echo "Extracting PostgreSQL..."
if [ "$ARCH" = "x86_64" ]; then
  tar -xzf postgresql-$PG_VERSION-linux-x64.tar.gz -C $INSTALL_DIR --strip-components=1
elif [ "$ARCH" = "aarch64" ]; then
  tar -xzf postgresql-$PG_VERSION-linux-arm64.tar.gz -C $INSTALL_DIR --strip-components=1
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to extract PostgreSQL binaries."
    exit 1
fi

# Verify binary exists
if [ ! -f "$INSTALL_DIR/bin/initdb" ]; then
    echo "Error: initdb binary was not found at $INSTALL_DIR/bin/initdb"
    echo "Extraction appears to have failed."
    exit 1
fi

echo "PostgreSQL binaries extracted successfully!"
echo "initdb is located at: $INSTALL_DIR/bin/initdb"

# Initialize database
echo "Initializing PostgreSQL database cluster..."
mkdir -p $PGDATA
echo "Created data directory at: $PGDATA"

echo "Running initdb command..."
$INSTALL_DIR/bin/initdb -D $PGDATA --no-locale --encoding=UTF8
if [ $? -ne 0 ]; then
    echo "Error: initdb failed. Please check the error message above."
    exit 1
fi
echo "Database initialization successful!"

# Set proper permissions - u=rwx (user read, write, execute)
echo "Setting permissions to u=rwx..."
chmod -R u=rwx $PGDATA
chmod -R u=rwx $INSTALL_DIR/bin
echo "Permissions set."

# Verify the data directory has the required files
echo "Verifying data directory structure..."
if [ -f "$PGDATA/PG_VERSION" ]; then
    echo "PG_VERSION found. Data directory appears valid."
else
    echo "ERROR: $PGDATA/PG_VERSION not found. Data directory may not be properly initialized."
    echo "Contents of $PGDATA:"
    ls -la $PGDATA
    exit 1
fi

# Configure PostgreSQL
echo "Configuring PostgreSQL..."
echo "shared_preload_libraries = 'vector'" >> $PGDATA/postgresql.conf
echo "listen_addresses = '*'" >> $PGDATA/postgresql.conf
echo "port = 5432" >> $PGDATA/postgresql.conf
echo "log_destination = 'stderr'" >> $PGDATA/postgresql.conf
echo "logging_collector = on" >> $PGDATA/postgresql.conf
echo "log_directory = 'pg_log'" >> $PGDATA/postgresql.conf
echo "log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'" >> $PGDATA/postgresql.conf
echo "log_statement = 'all'" >> $PGDATA/postgresql.conf

# Set up authentication
mkdir -p $PGDATA/pg_log
echo "# TYPE  DATABASE        USER            ADDRESS                 METHOD" > $PGDATA/pg_hba.conf
echo "local   all             all                                     md5" >> $PGDATA/pg_hba.conf
echo "host    all             all             127.0.0.1/32            md5" >> $PGDATA/pg_hba.conf
echo "host    all             all             ::1/128                 md5" >> $PGDATA/pg_hba.conf
echo "host    all             all             0.0.0.0/0               md5" >> $PGDATA/pg_hba.conf

echo "Starting PostgreSQL server..."
$INSTALL_DIR/bin/pg_ctl -D $PGDATA start

if [ $? -ne 0 ]; then
    echo "Error starting PostgreSQL server. Please check the error messages above."
    exit 1
fi

echo "Creating application user and database..."
# Create the l1_app_user with password 'test' as requested
$INSTALL_DIR/bin/psql -d postgres -c "CREATE ROLE $DB_USER WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD '$DB_PASSWORD';"

# Create the l1_app_db owned by l1_app_user
$INSTALL_DIR/bin/createdb -O $DB_USER $DB_NAME

# Grant all privileges on the database to the user
$INSTALL_DIR/bin/psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Create environment file
echo "Creating environment file..."
ENV_FILE=$HOME/.pgenv

cat > $ENV_FILE << EOF
# PostgreSQL Environment Variables
export PATH=$INSTALL_DIR/bin:\$PATH
export PGDATA=$PGDATA
export DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
export PGHOST=localhost
export PGPORT=5432
export PGUSER=$DB_USER
export PGPASSWORD=$DB_PASSWORD
export PGDATABASE=$DB_NAME
EOF

echo "Environment file created at $ENV_FILE"
echo "To load these environment variables, run:"
echo "source $ENV_FILE"

echo "PostgreSQL installation complete!"
echo ""
echo "IMPORTANT: The pgvector extension needs to be installed separately."
echo "This installation includes only PostgreSQL without the pgvector extension."
echo "You can still use the database for non-vector operations."
echo ""
echo "USAGE GUIDE:"
echo "-----------"
echo "1. Start PostgreSQL:   $INSTALL_DIR/bin/pg_ctl -D $PGDATA start"
echo "2. Stop PostgreSQL:    $INSTALL_DIR/bin/pg_ctl -D $PGDATA stop"
echo "3. Connect to DB:      $INSTALL_DIR/bin/psql -d $DB_NAME"
echo "4. Check PG status:    $INSTALL_DIR/bin/pg_ctl -D $PGDATA status"
echo ""
echo "To connect after sourcing ~/.pgenv:"
echo "source ~/.pgenv"
echo "psql -d $DB_NAME"