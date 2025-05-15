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
$INSTALL_DIR/bin/initdb -D $PGDATA --no-locale --encoding=UTF8

echo "Downloading pgvector source..."
cd $INSTALL_DIR
wget --no-check-certificate https://github.com/pgvector/pgvector/archive/refs/tags/v0.5.1.tar.gz -O pgvector-0.5.1.tar.gz

echo "Extracting pgvector..."
tar -xzf pgvector-0.5.1.tar.gz
cd pgvector-0.5.1

echo "Building pgvector..."
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config install

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
echo "Database name: l1_app_db"
echo "Username: l1_app_user"
echo "Password: l1"
echo "Host: localhost"
echo "Port: 5432"
echo ""
echo "Connection string: postgresql://l1_app_user:l1@localhost:5432/l1_app_db"
echo ""
echo "To start PostgreSQL server: pg_ctl -D $PGDATA start"
echo "To stop PostgreSQL server: pg_ctl -D $PGDATA stop"
echo "PostgreSQL binaries are installed in: $INSTALL_DIR/bin"

# Also set environment variables for the application
echo ""
echo "Setting up environment variables for the application..."
echo "export DATABASE_URL=postgresql://l1_app_user:l1@localhost:5432/l1_app_db"
echo "export PGHOST=localhost"
echo "export PGPORT=5432"
echo "export PGUSER=l1_app_user"
echo "export PGPASSWORD=l1"
echo "export PGDATABASE=l1_app_db"