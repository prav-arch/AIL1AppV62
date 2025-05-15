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
echo "local   all             all                                     trust" > $PGDATA/pg_hba.conf
echo "host    all             all             127.0.0.1/32            trust" >> $PGDATA/pg_hba.conf
echo "host    all             all             ::1/128                 trust" >> $PGDATA/pg_hba.conf

echo "Starting PostgreSQL server..."
$INSTALL_DIR/bin/pg_ctl -D $PGDATA start

echo "Creating test database and enabling pgvector extension..."
$INSTALL_DIR/bin/createdb test
$INSTALL_DIR/bin/psql -d test -c "CREATE EXTENSION vector;"

echo "Verifying pgvector installation..."
$INSTALL_DIR/bin/psql -d test -c "CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));"
$INSTALL_DIR/bin/psql -d test -c "INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"
$INSTALL_DIR/bin/psql -d test -c "SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;"

echo "Installation complete!"
echo "Use the following environment variables to connect to your PostgreSQL server:"
echo "export PATH=$INSTALL_DIR/bin:\$PATH"
echo "export PGDATA=$PGDATA"
echo ""
echo "To start PostgreSQL server: pg_ctl -D $PGDATA start"
echo "To stop PostgreSQL server: pg_ctl -D $PGDATA stop"
echo "PostgreSQL binaries are installed in: $INSTALL_DIR/bin"