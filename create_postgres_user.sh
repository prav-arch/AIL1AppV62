#!/bin/bash

# PostgreSQL User Management Script
# This script helps you create and manage PostgreSQL users

# Configuration - adjust these paths to match your installation
PGBIN="$HOME/postgres14/bin"
PGDATA="$HOME/pgdata14"

# Default user credentials
DEFAULT_USER="l1_app_user"
DEFAULT_PASSWORD="test"
DEFAULT_DB="l1_app_db"

echo "=== PostgreSQL User Management ==="

# Check if PostgreSQL is running
if ! $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
    echo "PostgreSQL is not running. Starting server..."
    $PGBIN/pg_ctl -D $PGDATA start
    sleep 3
    
    # Check again
    if ! $PGBIN/pg_ctl -D $PGDATA status > /dev/null; then
        echo "Failed to start PostgreSQL server!"
        exit 1
    fi
fi

# Menu for user management
echo "Select an option:"
echo "1. Create the standard user ($DEFAULT_USER with password '$DEFAULT_PASSWORD')"
echo "2. Create a new custom user"
echo "3. Reset password for existing user"
echo "4. List all users"
echo "5. Delete a user"
echo "6. Exit"

read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo "Creating standard user ($DEFAULT_USER)..."
        
        # Check if user already exists
        if $PGBIN/psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DEFAULT_USER'" | grep -q 1; then
            echo "User $DEFAULT_USER already exists!"
            read -p "Do you want to reset the password? (y/n): " reset
            
            if [ "$reset" = "y" ]; then
                $PGBIN/psql -d postgres -c "ALTER USER $DEFAULT_USER WITH PASSWORD '$DEFAULT_PASSWORD';"
                echo "Password for $DEFAULT_USER has been reset to '$DEFAULT_PASSWORD'"
            fi
        else
            # Create user and database
            $PGBIN/psql -d postgres -c "CREATE ROLE $DEFAULT_USER WITH LOGIN PASSWORD '$DEFAULT_PASSWORD' CREATEDB;"
            $PGBIN/createdb -O $DEFAULT_USER $DEFAULT_DB
            
            # Grant privileges
            $PGBIN/psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DEFAULT_DB TO $DEFAULT_USER;"
            
            echo "Created user $DEFAULT_USER with password '$DEFAULT_PASSWORD'"
            echo "Created database $DEFAULT_DB owned by $DEFAULT_USER"
        fi
        
        # Show connection string
        echo ""
        echo "Connection string:"
        echo "postgresql://$DEFAULT_USER:$DEFAULT_PASSWORD@localhost:5432/$DEFAULT_DB"
        ;;
        
    2)
        read -p "Enter new username: " new_user
        read -p "Enter password for $new_user: " new_password
        read -p "Create a database for this user? (y/n): " create_db
        
        # Create user
        $PGBIN/psql -d postgres -c "CREATE ROLE $new_user WITH LOGIN PASSWORD '$new_password' CREATEDB;"
        echo "Created user $new_user"
        
        if [ "$create_db" = "y" ]; then
            read -p "Enter database name: " db_name
            $PGBIN/createdb -O $new_user $db_name
            $PGBIN/psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $new_user;"
            echo "Created database $db_name owned by $new_user"
            
            # Show connection string
            echo ""
            echo "Connection string:"
            echo "postgresql://$new_user:$new_password@localhost:5432/$db_name"
        fi
        ;;
        
    3)
        read -p "Enter username to reset password: " reset_user
        read -p "Enter new password for $reset_user: " reset_password
        
        # Check if user exists
        if $PGBIN/psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$reset_user'" | grep -q 1; then
            $PGBIN/psql -d postgres -c "ALTER USER $reset_user WITH PASSWORD '$reset_password';"
            echo "Password for $reset_user has been reset to '$reset_password'"
        else
            echo "User $reset_user does not exist!"
        fi
        ;;
        
    4)
        echo "Listing all PostgreSQL users:"
        $PGBIN/psql -d postgres -c "\du"
        
        echo ""
        echo "Listing all databases:"
        $PGBIN/psql -d postgres -c "\l"
        ;;
        
    5)
        read -p "Enter username to delete: " delete_user
        read -p "This will delete user $delete_user. Are you sure? (y/n): " confirm
        
        if [ "$confirm" = "y" ]; then
            # Check if user exists
            if $PGBIN/psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$delete_user'" | grep -q 1; then
                # List databases owned by this user
                echo "Checking for databases owned by $delete_user..."
                owned_dbs=$($PGBIN/psql -d postgres -tAc "SELECT datname FROM pg_database d JOIN pg_roles r ON d.datdba = r.oid WHERE r.rolname = '$delete_user';")
                
                if [ -n "$owned_dbs" ]; then
                    echo "User $delete_user owns the following databases:"
                    echo "$owned_dbs"
                    read -p "Drop these databases? (y/n): " drop_dbs
                    
                    if [ "$drop_dbs" = "y" ]; then
                        for db in $owned_dbs; do
                            $PGBIN/dropdb $db
                            echo "Dropped database $db"
                        done
                    else
                        echo "Reassigning databases to postgres user..."
                        for db in $owned_dbs; do
                            $PGBIN/psql -d postgres -c "ALTER DATABASE $db OWNER TO postgres;"
                            echo "Reassigned $db to postgres user"
                        done
                    fi
                fi
                
                # Delete user
                $PGBIN/psql -d postgres -c "DROP ROLE $delete_user;"
                echo "Deleted user $delete_user"
            else
                echo "User $delete_user does not exist!"
            fi
        else
            echo "Operation cancelled"
        fi
        ;;
        
    6)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid option!"
        ;;
esac

echo ""
echo "=== User Management Complete ==="
echo ""
echo "To verify connection with your user, run:"
echo "$PGBIN/psql -U username -d database_name"