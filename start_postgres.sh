#!/bin/bash

# Simple script to start PostgreSQL 14.2 installation

# Configuration - paths to PostgreSQL installation (change these if needed)
PGBIN="$HOME/postgres14/bin"
PGDATA="$HOME/pgdata14"

echo "=== Starting PostgreSQL 14.2 ==="

# Step 1: Make sure the necessary directories exist
if [ ! -d "$PGBIN" ]; then
    echo "❌ ERROR: PostgreSQL binary directory not found at $PGBIN"
    echo "Did you run the PostgreSQL installation script?"
    exit 1
fi

if [ ! -d "$PGDATA" ]; then
    echo "❌ ERROR: PostgreSQL data directory not found at $PGDATA"
    echo "Did you run the PostgreSQL initialization?"
    exit 1
fi

# Step 2: Check if PostgreSQL is already running
echo "Step 1: Checking if PostgreSQL is already running..."
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null 2>&1; then
    echo "PostgreSQL is already running!"
    echo "If you want to restart it, use: ./restart_postgres.sh"
    exit 0
fi

# Step 3: Start PostgreSQL server
echo "Step 2: Starting PostgreSQL server..."
$PGBIN/pg_ctl -D $PGDATA start

# Step 4: Wait for PostgreSQL to start
echo "Step 3: Waiting for PostgreSQL to start..."
sleep 3

# Step 5: Verify PostgreSQL is running
echo "Step 4: Verifying PostgreSQL status..."
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "✅ PostgreSQL successfully started!"
    
    # Step 6: Show connection information
    echo ""
    echo "Connection information:"
    echo "----------------------"
    echo "Host: localhost"
    echo "Port: 5432"
    echo "Default database: postgres"
    echo ""
    echo "To connect using psql:"
    echo "$PGBIN/psql -h localhost -p 5432 -d postgres"
    echo ""
    echo "To connect to the application database:"
    echo "$PGBIN/psql -h localhost -p 5432 -U l1_app_user -d l1_app_db"
    echo ""
    echo "Connection string for applications:"
    echo "postgresql://l1_app_user:test@localhost:5432/l1_app_db"
else
    echo "❌ PostgreSQL failed to start!"
    
    # Show error information
    echo ""
    echo "Possible issues:"
    echo "1. Port 5432 may already be in use"
    echo "2. Database files may be corrupted"
    echo "3. Insufficient permissions on data directory"
    
    echo ""
    echo "Try these commands to diagnose:"
    echo "1. Check port usage: netstat -tuln | grep 5432"
    echo "2. Check PostgreSQL log: tail -20 $PGDATA/log/*.log"
    echo "3. Fix permissions: chmod -R u+wx $PGDATA"
fi

echo ""
echo "=== PostgreSQL Start Process Complete ==="