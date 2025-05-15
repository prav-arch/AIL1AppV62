#!/bin/bash

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

echo "Downloading PostgreSQL 16.2 source..."
wget --no-check-certificate https://ftp.postgresql.org/pub/source/v16.2/postgresql-16.2.tar.gz

echo "Extracting PostgreSQL..."
tar -xzf postgresql-16.2.tar.gz
cd postgresql-16.2

echo "Configuring PostgreSQL for local installation..."
# Configure with --prefix to install in user's home directory
./configure --prefix=$INSTALL_DIR \
            --without-readline \
            --without-zlib

echo "Building PostgreSQL (this may take a while)..."
make -j $(nproc)
make install

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

echo "Downloading pgvector source..."
cd $INSTALL_DIR
wget --no-check-certificate https://github.com/pgvector/pgvector/archive/refs/tags/v0.5.1.tar.gz -O pgvector-0.5.1.tar.gz

echo "Extracting pgvector..."
tar -xzf pgvector-0.5.1.tar.gz
cd pgvector-0.5.1

echo "Building pgvector..."
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config install

# Set proper permissions for pgvector
chmod -R u=rwx $INSTALL_DIR/share/extension
chmod -R u=rwx $INSTALL_DIR/lib

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

echo "Creating application user and database..."
# Create the l1_app_user with password 'test' as requested
$INSTALL_DIR/bin/psql -d postgres -c "CREATE ROLE $DB_USER WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD '$DB_PASSWORD';"

# Create the l1_app_db owned by l1_app_user
$INSTALL_DIR/bin/createdb -O $DB_USER $DB_NAME

# Grant all privileges on the database to the user
$INSTALL_DIR/bin/psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "Enabling pgvector extension in the application database..."
$INSTALL_DIR/bin/psql -d $DB_NAME -c "CREATE EXTENSION vector;"

echo "Verifying pgvector installation..."
$INSTALL_DIR/bin/psql -d $DB_NAME -U $DB_USER -c "CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));"
$INSTALL_DIR/bin/psql -d $DB_NAME -U $DB_USER -c "INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"
$INSTALL_DIR/bin/psql -d $DB_NAME -U $DB_USER -c "SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;"

echo "Installation complete!"
echo "Use the following environment variables to connect to your PostgreSQL server:"
echo "export PATH=$INSTALL_DIR/bin:\$PATH"
echo "export PGDATA=$PGDATA"
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
echo "To start PostgreSQL server: pg_ctl -D $PGDATA start"
echo "To stop PostgreSQL server: pg_ctl -D $PGDATA stop"
echo "PostgreSQL binaries are installed in: $INSTALL_DIR/bin"

# Also set environment variables for the application
echo ""
echo "Setting up environment variables for the application..."
cat > $USER_HOME/.pgenv << EOF
# PostgreSQL 16.2 Environment Variables
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
echo "A configuration file has been created at: $USER_HOME/.pgenv"
echo "To load the PostgreSQL environment variables, run:"
echo "source $USER_HOME/.pgenv"
echo ""
echo "Add this line to your .bashrc or .profile to make it permanent:"
echo "echo 'source $USER_HOME/.pgenv' >> $USER_HOME/.bashrc"
echo "=========================================================="
echo ""
echo "USAGE GUIDE:"
echo "-----------"
echo "1. Start PostgreSQL:   pg_ctl -D $PGDATA start"
echo "2. Stop PostgreSQL:    pg_ctl -D $PGDATA stop"
echo "3. Connect to DB:      psql -d $DB_NAME"
echo "4. Check PG status:    pg_ctl -D $PGDATA status"
echo "5. Restart PostgreSQL: pg_ctl -D $PGDATA restart"
echo ""
echo "For GPU servers without root privileges, you may want to:"
echo "- Set PGDATA to use a local SSD or fast storage area if available"
echo "- Tune shared_buffers in postgresql.conf for optimal performance"
echo "- Consider setting up a backup routine for your data"
echo ""
echo "To modify database settings, edit: $PGDATA/postgresql.conf"

# Final permission check - ensure all files have u=rwx
echo ""
echo "Setting final permissions to u=rwx for all PostgreSQL files..."
chmod -R u=rwx $INSTALL_DIR
chmod -R u=rwx $PGDATA

echo "Permission settings complete."