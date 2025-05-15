#!/bin/bash

# Simple script to restart PostgreSQL 14.2 installation

# Configuration - paths to PostgreSQL installation
PGBIN="$HOME/postgres14/bin"
PGDATA="$HOME/pgdata14"

echo "=== PostgreSQL Restart Script ==="

# Step 1: Check if PostgreSQL is running
echo "Step 1: Checking PostgreSQL status..."
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "PostgreSQL is currently running."
    
    # Step 2: Stop PostgreSQL
    echo "Step 2: Stopping PostgreSQL..."
    $PGBIN/pg_ctl -D $PGDATA stop -m fast
    
    # Wait for it to shut down
    sleep 3
    
    # Check if it's really stopped
    if $PGBIN/pg_ctl -D $PGDATA status > /dev/null 2>&1; then
        echo "WARNING: PostgreSQL did not stop properly. Trying force stop..."
        $PGBIN/pg_ctl -D $PGDATA stop -m immediate
        sleep 2
    fi
else
    echo "PostgreSQL is not currently running."
fi

# Step 3: Start PostgreSQL
echo "Step 3: Starting PostgreSQL..."
$PGBIN/pg_ctl -D $PGDATA start

# Step 4: Wait for PostgreSQL to start
echo "Step 4: Waiting for PostgreSQL to start..."
sleep 5

# Step 5: Verify PostgreSQL is running
echo "Step 5: Verifying PostgreSQL status..."
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "✅ PostgreSQL successfully restarted!"
    
    # Step 6: Test connection
    echo "Step 6: Testing connection..."
    if $PGBIN/psql -h localhost -p 5432 -d postgres -c "SELECT version();" > /dev/null 2>&1; then
        echo "✅ Connection successful!"
        
        # Show version
        echo "PostgreSQL version information:"
        $PGBIN/psql -h localhost -p 5432 -d postgres -c "SELECT version();"
    else
        echo "❌ Connection test failed. Authentication issues may still exist."
        
        # Show suggestions
        echo ""
        echo "Possible solutions:"
        echo "1. Check pg_hba.conf configuration"
        echo "   Run: ./fix_postgres_auth.sh"
        echo "2. Verify database user exists"
        echo "   Run: ./create_postgres_user.sh"
    fi
else
    echo "❌ PostgreSQL failed to start!"
    
    # Check logs
    echo "Last 10 lines of PostgreSQL log:"
    tail -10 $PGDATA/log/*.log 2>/dev/null || echo "No log files found."
    
    echo ""
    echo "Possible issues:"
    echo "1. Port 5432 may already be in use"
    echo "2. Database files may be corrupted"
    echo "3. Insufficient permissions on data directory"
    
    echo ""
    echo "Try these commands:"
    echo "1. Check if port 5432 is in use:"
    echo "   netstat -tuln | grep 5432"
    echo "2. Check permissions:"
    echo "   ls -la $PGDATA"
    echo "3. Check detailed logs:"
    echo "   cat $PGDATA/log/*.log"
fi

echo ""
echo "=== PostgreSQL Restart Complete ==="