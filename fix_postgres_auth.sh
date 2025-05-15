#!/bin/bash

# Script to fix PostgreSQL authentication issues by updating pg_hba.conf
# Use this when you get "Authentication method might be too restrictive" errors

# Configuration - adjust these paths to match your installation
PGBIN="$HOME/postgres14/bin"
PGDATA="$HOME/pgdata14"

echo "=== PostgreSQL Authentication Fix ==="

# Check if PostgreSQL is running
if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "PostgreSQL is running. Will need to restart after changes."
    pg_running=true
else
    echo "PostgreSQL is not running."
    pg_running=false
fi

# Backup original pg_hba.conf
echo "Creating backup of original pg_hba.conf..."
cp $PGDATA/pg_hba.conf $PGDATA/pg_hba.conf.bak
echo "Backup created at: $PGDATA/pg_hba.conf.bak"

# Create a new pg_hba.conf with more permissive settings
echo "Updating pg_hba.conf with more permissive settings..."
cat > $PGDATA/pg_hba.conf << EOL
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow specific users with password authentication
host    all             l1_app_user     all                     md5
# Allow any user from localhost with password
host    all             all             localhost               md5
EOL

chmod 600 $PGDATA/pg_hba.conf
echo "Updated pg_hba.conf with more permissive settings."

# Restart PostgreSQL to apply changes
if [ "$pg_running" = true ]; then
    echo "Restarting PostgreSQL to apply changes..."
    $PGBIN/pg_ctl -D $PGDATA restart
    
    # Wait for PostgreSQL to restart
    sleep 3
    
    if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
        echo "PostgreSQL restarted successfully."
    else
        echo "Failed to restart PostgreSQL. Trying to start..."
        $PGBIN/pg_ctl -D $PGDATA start
        sleep 3
        
        if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
            echo "PostgreSQL started successfully."
        else
            echo "Failed to start PostgreSQL. Please check the logs."
            exit 1
        fi
    fi
else
    echo "Starting PostgreSQL..."
    $PGBIN/pg_ctl -D $PGDATA start
    
    sleep 3
    
    if $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
        echo "PostgreSQL started successfully."
    else
        echo "Failed to start PostgreSQL. Please check the logs."
        exit 1
    fi
fi

# Test the connection
echo "Testing connection with default credentials..."
if $PGBIN/psql -h localhost -p 5432 -U l1_app_user -d l1_app_db -c "SELECT 1 AS connection_test;" > /dev/null 2>&1; then
    echo "✅ Connection successful! Authentication issue is fixed."
else
    echo "❌ Connection still failing. Let's try to diagnose the issue..."
    
    # Check if the database exists
    if ! $PGBIN/psql -h localhost -d postgres -c "SELECT datname FROM pg_database WHERE datname='l1_app_db';" | grep -q "l1_app_db"; then
        echo "The database 'l1_app_db' does not exist!"
        read -p "Do you want to create it now? (y/n): " create_db
        
        if [ "$create_db" = "y" ]; then
            # First check if user exists
            if ! $PGBIN/psql -h localhost -d postgres -c "SELECT rolname FROM pg_roles WHERE rolname='l1_app_user';" | grep -q "l1_app_user"; then
                echo "Creating user 'l1_app_user'..."
                $PGBIN/psql -h localhost -d postgres -c "CREATE ROLE l1_app_user WITH LOGIN PASSWORD 'test' CREATEDB;"
            fi
            
            echo "Creating database 'l1_app_db'..."
            $PGBIN/createdb -h localhost -O l1_app_user l1_app_db
            echo "Database created."
        fi
    fi
    
    # Check if user exists
    if ! $PGBIN/psql -h localhost -d postgres -c "SELECT rolname FROM pg_roles WHERE rolname='l1_app_user';" | grep -q "l1_app_user"; then
        echo "The user 'l1_app_user' does not exist!"
        read -p "Do you want to create this user now? (y/n): " create_user
        
        if [ "$create_user" = "y" ]; then
            echo "Creating user 'l1_app_user'..."
            $PGBIN/psql -h localhost -d postgres -c "CREATE ROLE l1_app_user WITH LOGIN PASSWORD 'test' CREATEDB;"
            echo "User created."
        fi
    fi
    
    # Try with different authentication methods
    echo "Checking if we can connect with alternative settings..."
    
    # Try as postgres user
    if $PGBIN/psql -h localhost -d postgres -c "SELECT 1 AS postgres_test;" > /dev/null 2>&1; then
        echo "✅ Connected as postgres user. The issue is specific to l1_app_user."
        
        # Reset l1_app_user password
        echo "Resetting password for l1_app_user..."
        $PGBIN/psql -h localhost -d postgres -c "ALTER USER l1_app_user WITH PASSWORD 'test';"
        
        echo "Granting all privileges on l1_app_db to l1_app_user..."
        $PGBIN/psql -h localhost -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE l1_app_db TO l1_app_user;"
    else
        echo "❌ Cannot connect even as postgres user. This suggests a more fundamental authentication issue."
        
        # Set everything to trust temporarily
        echo "Setting all authentication methods to 'trust' temporarily..."
        cat > $PGDATA/pg_hba.conf << EOL
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             0.0.0.0/0               trust
EOL
        
        echo "Reloading PostgreSQL configuration..."
        $PGBIN/pg_ctl -D $PGDATA reload
        
        echo "Now try connecting again with your application."
    fi
fi

echo ""
echo "=== Authentication Fix Complete ==="
echo ""
echo "If you're still having issues, you may need to:"
echo "1. Check if your user has the correct permissions"
echo "2. Verify the database exists and is accessible"
echo "3. Make sure the PostgreSQL port (default 5432) is not blocked"
echo ""
echo "Connection string for your application:"
echo "postgresql://l1_app_user:test@localhost:5432/l1_app_db"