#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
This script verifies the connection to PostgreSQL and performs basic operations
to ensure everything is working correctly.
"""

import os
import sys
import time
import psycopg2
from psycopg2 import sql


def test_connection(connection_string=None):
    """Test connection to PostgreSQL using provided connection string or environment variables"""
    
    if connection_string is None:
        # Try to get connection string from environment
        connection_string = os.environ.get('DATABASE_URL')
        
        # If still not available, try to construct from individual parts
        if connection_string is None:
            host = os.environ.get('PGHOST', 'localhost')
            port = os.environ.get('PGPORT', '5432')
            dbname = os.environ.get('PGDATABASE', 'l1_app_db')
            user = os.environ.get('PGUSER', 'l1_app_user')
            password = os.environ.get('PGPASSWORD', 'test')
            
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    print(f"Testing connection with: {connection_string.replace(os.environ.get('PGPASSWORD', 'test'), '****')}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(connection_string)
        print("✅ Connected to PostgreSQL successfully!")
        
        # Create a cursor
        cur = conn.cursor()
        
        # Get PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()
        if version:
            print(f"✅ PostgreSQL version: {version[0]}")
        else:
            print("❌ Could not retrieve PostgreSQL version")
        
        # Test creating a table
        print("Testing table operations...")
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        print("✅ Created test table")
        
        # Test inserting data
        cur.execute(sql.SQL("""
            INSERT INTO connection_test (test_name) 
            VALUES (%s) RETURNING id
        """), ("Connection test executed at " + time.strftime("%Y-%m-%d %H:%M:%S"),))
        result = cur.fetchone()
        if result:
            new_id = result[0]
            conn.commit()
            print(f"✅ Inserted test row with ID: {new_id}")
        else:
            conn.commit()
            print("✅ Inserted test row (ID unknown)")
        
        # Test retrieving data
        cur.execute(sql.SQL("""
            SELECT * FROM connection_test 
            ORDER BY timestamp DESC 
            LIMIT 5
        """))
        rows = cur.fetchall()
        print(f"✅ Retrieved {len(rows)} rows from test table")
        for row in rows:
            print(f"   - ID: {row[0]}, Name: {row[1]}, Time: {row[2]}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        print("\n✅ All PostgreSQL connection tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test FAILED: {e}")
        
        # Provide debugging suggestions
        if "could not connect to server" in str(e):
            print("\nPossible issues:")
            print("1. PostgreSQL server is not running")
            print("2. Port configuration is incorrect")
            print("3. Network access to the database is restricted")
            print("\nTry running:")
            print("~/postgres14/bin/pg_ctl -D ~/pgdata14 status")
            print("If not running, start with:")
            print("~/postgres14/bin/pg_ctl -D ~/pgdata14 start")
            
        elif "password authentication failed" in str(e):
            print("\nPossible issues:")
            print("1. Username or password is incorrect")
            print("2. Authentication method in pg_hba.conf might be too restrictive")
            print("\nVerify credentials and check pg_hba.conf settings")
            
        elif "database" in str(e) and "does not exist" in str(e):
            print("\nPossible issues:")
            print("1. Database name is incorrect")
            print("2. Database has not been created")
            print("\nTry creating the database:")
            print("~/postgres14/bin/createdb -O l1_app_user l1_app_db")
            
        return False


if __name__ == "__main__":
    # Check if a connection string was provided as command-line argument
    if len(sys.argv) > 1:
        test_connection(sys.argv[1])
    else:
        # Use default or environment variables
        test_connection()