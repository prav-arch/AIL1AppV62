#!/bin/bash

# PostgreSQL Connection Test Script
# Simple script to verify PostgreSQL installation and connectivity

# Set paths for PostgreSQL binaries and data
PGBIN="$HOME/postgres14/bin"
PGDATA="$HOME/pgdata14"
PGPORT=5432
PGUSER="l1_app_user"
PGPASS="test"
PGDB="l1_app_db"

echo "=== PostgreSQL Connection Test ==="
echo "Testing connection to PostgreSQL 14.2 installation"
echo ""

# Check if PostgreSQL is running
echo "Step 1: Checking if PostgreSQL server is running..."
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "✅ PostgreSQL server is running"
else
    echo "❌ PostgreSQL server is NOT running!"
    echo "Attempting to start PostgreSQL server..."
    $PGBIN/pg_ctl -D $PGDATA start
    sleep 3
    
    # Check again
    if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
        echo "✅ PostgreSQL server successfully started"
    else
        echo "❌ Failed to start PostgreSQL server!"
        echo "Please check installation and try: $PGBIN/pg_ctl -D $PGDATA start"
        exit 1
    fi
fi

echo ""
echo "Step 2: Checking PostgreSQL version..."
if $PGBIN/psql -V; then
    echo "✅ PostgreSQL client installed correctly"
else
    echo "❌ PostgreSQL client not found or not working!"
    exit 1
fi

echo ""
echo "Step 3: Testing connection to database..."
if $PGBIN/psql -h localhost -p $PGPORT -U $PGUSER -d $PGDB -c "SELECT 1 AS connection_test;" > /dev/null 2>&1; then
    echo "✅ Successfully connected to $PGDB as $PGUSER"
else
    echo "❌ Failed to connect to database!"
    echo "Checking if database exists..."
    
    # Try connecting to postgres database
    if $PGBIN/psql -h localhost -p $PGPORT -d postgres -c "SELECT datname FROM pg_database WHERE datname='$PGDB';" | grep -q "$PGDB"; then
        echo "✅ Database $PGDB exists"
        echo "❌ But connection failed - check credentials and pg_hba.conf"
    else
        echo "❌ Database $PGDB does not exist!"
        echo "Attempting to create database..."
        $PGBIN/createdb -h localhost -p $PGPORT -O $PGUSER $PGDB
        
        if $PGBIN/psql -h localhost -p $PGPORT -d postgres -c "SELECT datname FROM pg_database WHERE datname='$PGDB';" | grep -q "$PGDB"; then
            echo "✅ Database $PGDB created successfully"
        else
            echo "❌ Failed to create database!"
        fi
    fi
fi

echo ""
echo "Step 4: Testing database operations..."
echo "Creating test table and inserting data..."

# Create test table and insert data
$PGBIN/psql -h localhost -p $PGPORT -U $PGUSER -d $PGDB -c "
CREATE TABLE IF NOT EXISTS connection_test (
    id SERIAL PRIMARY KEY,
    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);

INSERT INTO connection_test (message) VALUES ('Connection test executed at $(date)');

SELECT * FROM connection_test ORDER BY test_time DESC LIMIT 5;
"

if [ $? -eq 0 ]; then
    echo "✅ Database operations completed successfully"
else
    echo "❌ Database operations failed!"
fi

echo ""
echo "Step 5: Checking environment variables..."
echo "DATABASE_URL: ${DATABASE_URL:-"Not set"}"
echo "PGHOST: ${PGHOST:-"Not set"}"
echo "PGPORT: ${PGPORT:-"Not set"}"
echo "PGDATABASE: ${PGDATABASE:-"Not set"}"
echo "PGUSER: ${PGUSER:-"Not set"}"
echo "PGPASSWORD: ${PGPASSWORD:-"Not set (this is good for security)"}"

echo ""
echo "=== PostgreSQL Connection Test Complete ==="
echo ""
echo "If all steps show ✅, your PostgreSQL installation is working correctly!"
echo "If you see any ❌, check the error messages and fix the issues."
echo ""
echo "PostgreSQL 14.2 Connection String for applications:"
echo "postgresql://$PGUSER:$PGPASS@localhost:$PGPORT/$PGDB"