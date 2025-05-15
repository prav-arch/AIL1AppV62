"""
Test script to verify PostgreSQL connection and functionality.
Uses the l1_app_user/l1_app_db credentials.
"""

import os
import sys
import psycopg2
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection string
# First try with environment variable, then with our custom credentials
ENV_DATABASE_URL = os.environ.get('DATABASE_URL')
CUSTOM_DATABASE_URL = 'postgresql://l1_app_user:l1@localhost:5432/l1_app_db'

def test_connection(url, name):
    """Test a specific database connection"""
    print(f"\n----- Testing {name} connection -----")
    print(f"Connection string: {url.split('@')[1] if '@' in url else 'localhost'}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(url)
        
        # Create a cursor
        with conn.cursor() as cur:
            # Check connection by querying the PostgreSQL version
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"Connected successfully! PostgreSQL version: {version}")
            
            # Create a test table
            print("\nCreating test table...")
            test_table_name = f"test_table_{int(time.time())}"
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {test_table_name} (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    value INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print(f"Test table '{test_table_name}' created successfully!")
            
            # Insert some test data
            print("\nInserting test data...")
            test_data = [
                ("Test Item 1", 100),
                ("Test Item 2", 200),
                ("Test Item 3", 300),
            ]
            
            for name, value in test_data:
                cur.execute(
                    f"INSERT INTO {test_table_name} (name, value) VALUES (%s, %s) RETURNING id",
                    (name, value)
                )
                id = cur.fetchone()[0]
                print(f"Inserted: ID={id}, Name='{name}', Value={value}")
            
            conn.commit()
            
            # Query the data
            print("\nQuerying test data...")
            cur.execute(f"SELECT id, name, value, created_at FROM {test_table_name} ORDER BY id")
            rows = cur.fetchall()
            
            print(f"Found {len(rows)} rows:")
            for row in rows:
                print(f"ID: {row[0]}, Name: '{row[1]}', Value: {row[2]}, Created: {row[3]}")
            
            # Clean up - drop the test table
            print("\nCleaning up...")
            cur.execute(f"DROP TABLE {test_table_name}")
            conn.commit()
            print(f"Test table '{test_table_name}' dropped successfully!")
            
            print(f"\n----- {name} connection test completed successfully! -----")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error with {name} connection: {e}")
        return False

def test_postgres_connection():
    """Test PostgreSQL connection with both the environment and custom credentials"""
    print("===== POSTGRESQL CONNECTION TESTS =====")

    # Test environment variable connection
    if ENV_DATABASE_URL:
        env_test_success = test_connection(ENV_DATABASE_URL, "Environment Variable")
    else:
        print("\n----- Environment Variable connection test SKIPPED (no DATABASE_URL set) -----")
        env_test_success = False
    
    # Test custom credentials connection
    custom_test_success = test_connection(CUSTOM_DATABASE_URL, "Custom l1_app_user Credentials")
    
    # Summary
    print("\n===== TEST SUMMARY =====")
    if ENV_DATABASE_URL:
        print(f"Environment Variable Connection Test: {'SUCCESS' if env_test_success else 'FAILED'}")
    else:
        print("Environment Variable Connection Test: SKIPPED (no DATABASE_URL set)")
    
    print(f"Custom Credentials Connection Test: {'SUCCESS' if custom_test_success else 'FAILED'}")
    
    return env_test_success or custom_test_success

if __name__ == "__main__":
    test_postgres_connection()