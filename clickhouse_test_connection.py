#!/usr/bin/env python3
"""
ClickHouse Connection Test Script
This script verifies the connection to ClickHouse and performs basic operations
to ensure everything is working correctly.
"""

import os
import sys
import time
import traceback

# Check if clickhouse-driver is installed
try:
    from clickhouse_driver import Client
except ImportError:
    print("clickhouse-driver package is not installed.")
    print("Installing using pip...")
    
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "clickhouse-driver"])
    
    print("clickhouse-driver installed successfully")
    from clickhouse_driver import Client


def test_connection(host=None, port=None, user=None, password=None, database=None):
    """Test connection to ClickHouse using provided parameters or environment variables"""
    
    # Use provided parameters or get from environment
    host = host or os.environ.get('CLICKHOUSE_HOST', 'localhost')
    port = port or os.environ.get('CLICKHOUSE_PORT', '9000')
    user = user or os.environ.get('CLICKHOUSE_USER', 'l1_app_user')
    password = password or os.environ.get('CLICKHOUSE_PASSWORD', 'test')
    database = database or os.environ.get('CLICKHOUSE_DATABASE', 'l1_app_db')
    
    print(f"Testing connection to ClickHouse at {host}:{port}, database: {database}")
    
    try:
        # Connect to ClickHouse
        client = Client(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connect_timeout=10
        )
        
        print("✅ Connected to ClickHouse successfully!")
        
        # Get ClickHouse version
        version = client.execute("SELECT version()")[0][0]
        print(f"✅ ClickHouse version: {version}")
        
        # List databases
        databases = client.execute("SHOW DATABASES")
        print(f"✅ Available databases: {', '.join([db[0] for db in databases])}")
        
        # Test creating a table
        print("Testing table operations...")
        client.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id UInt32,
                test_name String,
                timestamp DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY id
        """)
        print("✅ Created test table")
        
        # Test inserting data
        test_id = int(time.time())
        client.execute(
            "INSERT INTO connection_test (id, test_name) VALUES",
            [(test_id, "Connection test executed at " + time.strftime("%Y-%m-%d %H:%M:%S"))]
        )
        print(f"✅ Inserted test row with ID: {test_id}")
        
        # Test retrieving data
        rows = client.execute("SELECT * FROM connection_test ORDER BY timestamp DESC LIMIT 5")
        print(f"✅ Retrieved {len(rows)} rows from test table")
        for row in rows:
            print(f"   - ID: {row[0]}, Name: {row[1]}, Time: {row[2]}")
        
        # Test vector index if available (newer ClickHouse versions)
        try:
            client.execute("""
                CREATE TABLE IF NOT EXISTS vector_test (
                    id UInt32,
                    embedding Array(Float32)
                ) ENGINE = MergeTree()
                ORDER BY id
            """)
            
            # Add vector index
            try:
                client.execute("""
                    ALTER TABLE vector_test 
                    ADD VECTOR INDEX vec_idx embedding TYPE MSTG
                """)
                print("✅ Created vector index (MSTG) successfully!")
                
                # Insert test vector
                test_vector = [0.1, 0.2, 0.3, 0.4, 0.5] * 10  # 50-dim vector
                client.execute(
                    "INSERT INTO vector_test (id, embedding) VALUES",
                    [(1, test_vector)]
                )
                print("✅ Inserted test vector data")
                
                # Test vector search if available
                try:
                    result = client.execute("""
                        SELECT id, distance(embedding, [0.11, 0.21, 0.31, 0.41, 0.51, 
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5,
                                                    0.1, 0.2, 0.3, 0.4, 0.5]) AS dist
                        FROM vector_test
                        ORDER BY dist ASC
                        LIMIT 1
                    """)
                    print("✅ Vector similarity search works!")
                except Exception as e:
                    print(f"⚠️ Vector similarity search not fully supported: {e}")
            except Exception as e:
                print(f"⚠️ Vector index creation not supported: {e}")
        except Exception as e:
            print(f"⚠️ Vector operations not fully supported: {e}")
        
        print("\n✅ All ClickHouse connection tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test FAILED: {e}")
        traceback.print_exc()
        
        # Provide debugging suggestions
        if "Connection refused" in str(e):
            print("\nPossible issues:")
            print("1. ClickHouse server is not running")
            print("2. Port configuration is incorrect")
            print("\nTry running:")
            print("./start_clickhouse.sh")
            
        elif "Authentication failed" in str(e):
            print("\nPossible issues:")
            print("1. Username or password is incorrect")
            print("2. User does not have access to the specified database")
            
        elif "Database" in str(e) and "doesn't exist" in str(e):
            print("\nPossible issues:")
            print("1. Database name is incorrect")
            print("2. Database has not been created")
            print("\nTry creating the database:")
            print("$CLICKHOUSE_HOME/bin/clickhouse-client --query=\"CREATE DATABASE l1_app_db\"")
            
        return False


if __name__ == "__main__":
    # Check if connection parameters were provided as command-line arguments
    if len(sys.argv) > 1:
        test_connection(
            host=sys.argv[1] if len(sys.argv) > 1 else None,
            port=sys.argv[2] if len(sys.argv) > 2 else None,
            user=sys.argv[3] if len(sys.argv) > 3 else None,
            password=sys.argv[4] if len(sys.argv) > 4 else None,
            database=sys.argv[5] if len(sys.argv) > 5 else None
        )
    else:
        # Use environment variables
        test_connection()