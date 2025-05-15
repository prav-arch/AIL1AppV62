#!/bin/bash

# ClickHouse Connection Test Script
# This script verifies ClickHouse is working correctly

# Set the ClickHouse home directory
CLICKHOUSE_HOME="$HOME/clickhouse25"

echo "=== ClickHouse Connection Test ==="

# Step 1: Check if ClickHouse is running
echo "Step 1: Checking if ClickHouse server is running..."
if pgrep -f "clickhouse-server" > /dev/null; then
    echo "✅ ClickHouse server is running"
else
    echo "❌ ClickHouse server is NOT running!"
    echo "Starting ClickHouse server..."
    
    # Try to start the server
    ~/start_clickhouse25.sh
    
    # Wait a bit
    sleep 5
    
    # Check again
    if pgrep -f "clickhouse-server" > /dev/null; then
        echo "✅ ClickHouse server started successfully"
    else
        echo "❌ Failed to start ClickHouse server!"
        echo "Please check the server logs and try to start it manually:"
        echo "~/start_clickhouse25.sh"
        exit 1
    fi
fi

# Step 2: Basic connection test
echo ""
echo "Step 2: Testing basic connection..."
if "$CLICKHOUSE_HOME/bin/clickhouse" client --query="SELECT 1" > /dev/null 2>&1; then
    echo "✅ Basic connection successful"
else
    echo "❌ Basic connection failed!"
    echo "Please check your ClickHouse configuration"
    exit 1
fi

# Step 3: Version check
echo ""
echo "Step 3: Checking ClickHouse version..."
VERSION=$("$CLICKHOUSE_HOME/bin/clickhouse" client --query="SELECT version()")
echo "✅ ClickHouse version: $VERSION"

# Step 4: Test application user
echo ""
echo "Step 4: Testing connection with application credentials..."
if "$CLICKHOUSE_HOME/bin/clickhouse" client --user=l1_app_user --password=test --query="SELECT 1" > /dev/null 2>&1; then
    echo "✅ Connection with application credentials successful"
else
    echo "❌ Connection with application credentials failed!"
    echo "Creating user in case it doesn't exist..."
    "$CLICKHOUSE_HOME/bin/clickhouse" client --query="CREATE USER IF NOT EXISTS l1_app_user IDENTIFIED BY 'test'"
    "$CLICKHOUSE_HOME/bin/clickhouse" client --query="GRANT ALL ON *.* TO l1_app_user"
    
    # Try again
    if "$CLICKHOUSE_HOME/bin/clickhouse" client --user=l1_app_user --password=test --query="SELECT 1" > /dev/null 2>&1; then
        echo "✅ Connection with application credentials now successful"
    else
        echo "❌ Still cannot connect with application credentials"
        echo "Check the users.xml configuration"
    fi
fi

# Step 5: Check for application database
echo ""
echo "Step 5: Checking for application database..."
if "$CLICKHOUSE_HOME/bin/clickhouse" client --query="SHOW DATABASES LIKE 'l1_app_db'" | grep -q "l1_app_db"; then
    echo "✅ Application database exists"
else
    echo "❌ Application database does not exist!"
    echo "Creating application database..."
    "$CLICKHOUSE_HOME/bin/clickhouse" client --query="CREATE DATABASE IF NOT EXISTS l1_app_db"
    echo "✅ Created application database"
fi

# Step 6: Test table operations
echo ""
echo "Step 6: Testing table operations in application database..."
"$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="
CREATE TABLE IF NOT EXISTS test_connection (
    id UInt32,
    test_time DateTime DEFAULT now(),
    message String
) ENGINE = MergeTree()
ORDER BY id
"

if [ $? -eq 0 ]; then
    echo "✅ Table creation successful"
    
    # Insert data
    "$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="
    INSERT INTO test_connection (id, message) VALUES
    (1, 'Connection test at $(date)')
    "
    
    if [ $? -eq 0 ]; then
        echo "✅ Data insertion successful"
        
        # Query data
        RESULT=$("$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="SELECT COUNT() FROM test_connection")
        echo "✅ Query successful, found $RESULT row(s)"
    else
        echo "❌ Data insertion failed"
    fi
else
    echo "❌ Table creation failed"
fi

# Step 7: Test vector operations if available
echo ""
echo "Step 7: Testing vector operations..."
"$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="
CREATE TABLE IF NOT EXISTS vector_test (
    id UInt32,
    embedding Array(Float32)
) ENGINE = MergeTree()
ORDER BY id
"

if [ $? -eq 0 ]; then
    echo "✅ Vector table creation successful"
    
    # Try to add vector index
    "$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="
    ALTER TABLE vector_test ADD VECTOR INDEX embedding_idx embedding TYPE HNSW
    " 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Vector index creation successful"
        
        # Insert vector data
        "$CLICKHOUSE_HOME/bin/clickhouse" client --database=l1_app_db --query="
        INSERT INTO vector_test (id, embedding) VALUES
        (1, [0.1, 0.2, 0.3, 0.4, 0.5])
        "
        
        if [ $? -eq 0 ]; then
            echo "✅ Vector data insertion successful"
            echo "✅ Vector operations are fully supported"
        else
            echo "❌ Vector data insertion failed"
        fi
    else
        echo "⚠️ Vector index creation not supported"
    fi
else
    echo "❌ Vector table creation failed"
fi

echo ""
echo "=== ClickHouse Connection Test Complete ==="
echo ""
echo "To connect to ClickHouse manually:"
echo "$CLICKHOUSE_HOME/bin/clickhouse client --user=l1_app_user --password=test --database=l1_app_db"
echo ""
echo "Connection string for applications:"
echo "clickhouse://l1_app_user:test@localhost:9000/l1_app_db"