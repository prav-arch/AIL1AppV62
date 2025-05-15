#!/bin/bash

# PostgreSQL installation script using apt.postgresql.org packages
# This script doesn't require root privileges and uses portable binary archives

# Set up environment variables for local installation
USER_HOME=$HOME
INSTALL_DIR=$USER_HOME/postgres16
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

# Use PostgreSQL's official apt repository packages (portable binaries)
# These are pre-built packages that can be extracted and used without installation
echo "Downloading PostgreSQL 16.2 binaries..."

# Direct link to Debian packages for PostgreSQL 16.2
if [ "$(uname -m)" = "x86_64" ]; then
  # For 64-bit systems
  wget --no-check-certificate http://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-16/postgresql-16_16.2-1.pgdg20.04+1_amd64.deb
  PACKAGE="postgresql-16_16.2-1.pgdg20.04+1_amd64.deb"
else
  # For ARM systems
  wget --no-check-certificate http://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-16/postgresql-16_16.2-1.pgdg20.04+1_arm64.deb
  PACKAGE="postgresql-16_16.2-1.pgdg20.04+1_arm64.deb"
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to download PostgreSQL package."
    exit 1
fi

echo "Extracting data.tar.xz from Debian package..."
ar x $PACKAGE data.tar.xz
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract data archive from package."
    exit 1
fi

echo "Extracting PostgreSQL files from data archive..."
tar -xf data.tar.xz -C $INSTALL_DIR
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract PostgreSQL files."
    exit 1
fi

# Find postgresql binary directory
INITDB_PATH=$(find $INSTALL_DIR -name "initdb" -type f | grep bin | head -1)
if [ -z "$INITDB_PATH" ]; then
    echo "Error: Could not find initdb binary in the extracted files."
    echo "Content of installation directory:"
    find $INSTALL_DIR -type d | head -20
    exit 1
fi

# Reorganize files if needed
BIN_DIR=$(dirname "$INITDB_PATH")
echo "Found PostgreSQL binaries at: $BIN_DIR"

if [ "$BIN_DIR" != "$INSTALL_DIR/bin" ]; then
    echo "Reorganizing files to $INSTALL_DIR/bin..."
    mkdir -p $INSTALL_DIR/bin
    cp -R $BIN_DIR/* $INSTALL_DIR/bin/
    
    # Also copy lib files if they exist
    USR_LIB_DIR=$(echo $BIN_DIR | sed 's|/bin$|/lib|')
    if [ -d "$USR_LIB_DIR" ]; then
        mkdir -p $INSTALL_DIR/lib
        cp -R $USR_LIB_DIR/* $INSTALL_DIR/lib/
    fi
    
    # And share files (for extensions)
    USR_SHARE_DIR=$(echo $BIN_DIR | sed 's|/bin$|/share|')
    if [ -d "$USR_SHARE_DIR" ]; then
        mkdir -p $INSTALL_DIR/share
        cp -R $USR_SHARE_DIR/* $INSTALL_DIR/share/
    fi
fi

# Verify all required binaries exist
if [ ! -f "$INSTALL_DIR/bin/initdb" ] || [ ! -f "$INSTALL_DIR/bin/pg_ctl" ] || [ ! -f "$INSTALL_DIR/bin/psql" ]; then
    echo "Error: Missing critical PostgreSQL binaries."
    echo "Files in $INSTALL_DIR/bin:"
    ls -la $INSTALL_DIR/bin
    exit 1
fi

chmod -R +x $INSTALL_DIR/bin

echo "Cleaning up download files..."
rm -f $PACKAGE data.tar.xz

echo "PostgreSQL installation successful!"
echo "PostgreSQL binaries installed at: $INSTALL_DIR/bin"

# Initialize database
echo "Initializing PostgreSQL database cluster..."
mkdir -p $PGDATA
echo "Created data directory at: $PGDATA"

echo "Running initdb command..."
$INSTALL_DIR/bin/initdb -D $PGDATA
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

# Configure PostgreSQL
echo "Configuring PostgreSQL..."
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

echo "=========================================================="
echo "PostgreSQL installation complete!"
echo ""
echo "Environment file created at: $ENV_FILE"
echo "To load PostgreSQL environment variables, run:"
echo "source $ENV_FILE"
echo "=========================================================="
echo ""
echo "Database connection information:"
echo "Database name: $DB_NAME"
echo "Username: $DB_USER"
echo "Password: $DB_PASSWORD"
echo "Host: localhost"
echo "Port: 5432"
echo ""
echo "Connection string: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
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