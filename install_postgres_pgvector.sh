#!/bin/bash

# Set up environment variables
INSTALL_DIR=/tmp/postgresql
PG_VERSION=16.2
PGDATA=$INSTALL_DIR/data
PATH=$INSTALL_DIR/bin:$PATH
export PGDATA PATH

echo "Creating installation directory..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

echo "Downloading PostgreSQL 16.2 binaries..."
wget --no-check-certificate https://ftp.postgresql.org/pub/source/v16.2/postgresql-16.2.tar.gz

echo "Extracting PostgreSQL..."
tar -xzf postgresql-16.2.tar.gz
cd postgresql-16.2

echo "Configuring PostgreSQL..."
./configure --prefix=$INSTALL_DIR

echo "Building PostgreSQL..."
make
make install

echo "Initializing PostgreSQL database cluster..."
mkdir -p $PGDATA
$INSTALL_DIR/bin/initdb -D $PGDATA

echo "Downloading pgvector source..."
cd $INSTALL_DIR
wget --no-check-certificate https://github.com/pgvector/pgvector/archive/refs/tags/v0.5.1.tar.gz -O pgvector-0.5.1.tar.gz

echo "Extracting pgvector..."
tar -xzf pgvector-0.5.1.tar.gz
cd pgvector-0.5.1

echo "Building pgvector..."
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config
make USE_PGXS=1 PG_CONFIG=$INSTALL_DIR/bin/pg_config install

echo "Configuring PostgreSQL to enable pgvector..."
echo "shared_preload_libraries = 'vector'" >> $PGDATA/postgresql.conf
echo "listen_addresses = '*'" >> $PGDATA/postgresql.conf
echo "port = 5432" >> $PGDATA/postgresql.conf

# Set up authentication with trust method for easier testing
echo "# TYPE  DATABASE        USER            ADDRESS                 METHOD" > $PGDATA/pg_hba.conf
echo "local   all             all                                     trust" >> $PGDATA/pg_hba.conf
echo "host    all             all             127.0.0.1/32            trust" >> $PGDATA/pg_hba.conf
echo "host    all             all             ::1/128                 trust" >> $PGDATA/pg_hba.conf
echo "host    all             all             0.0.0.0/0               trust" >> $PGDATA/pg_hba.conf

echo "Starting PostgreSQL server..."
$INSTALL_DIR/bin/pg_ctl -D $PGDATA start

echo "Creating application user and database..."
# Create the l1_app_user with password 'l1' and all privileges needed
$INSTALL_DIR/bin/psql -d postgres -c "CREATE ROLE l1_app_user WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'l1';"

# Create the l1_app_db owned by l1_app_user
$INSTALL_DIR/bin/createdb -O l1_app_user l1_app_db

# Grant all privileges on the database to the user
$INSTALL_DIR/bin/psql -d l1_app_db -c "GRANT ALL PRIVILEGES ON DATABASE l1_app_db TO l1_app_user;"

echo "Enabling pgvector extension in the application database..."
$INSTALL_DIR/bin/psql -d l1_app_db -c "CREATE EXTENSION vector;"

echo "Verifying pgvector installation..."
$INSTALL_DIR/bin/psql -d l1_app_db -U l1_app_user -c "CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));"
$INSTALL_DIR/bin/psql -d l1_app_db -U l1_app_user -c "INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"
$INSTALL_DIR/bin/psql -d l1_app_db -U l1_app_user -c "SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;"

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