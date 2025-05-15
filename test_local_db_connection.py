#!/usr/bin/env python3
"""
Test script to verify connection to the local PostgreSQL database
installed via the install_postgres_no_root.sh script.
"""

import os
import sys
import psycopg2
from datetime import datetime

def test_postgresql_connection():
    """Test connection to PostgreSQL and perform basic operations"""
    
    # Database connection parameters
    db_params = {
        'dbname': os.environ.get('PGDATABASE', 'l1_app_db'),
        'user': os.environ.get('PGUSER', 'l1_app_user'),
        'password': os.environ.get('PGPASSWORD', 'l1'),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5433'),
    }
    
    print(f"Connecting to PostgreSQL database: {db_params['dbname']} on {db_params['host']}:{db_params['port']}")
    print(f"Using credentials: {db_params['user']}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a query to get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"\nSuccessfully connected to PostgreSQL:")
        print(f"  {version[0]}")
        
        # Test table creation
        print("\nCreating test table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            );
        """)
        conn.commit()
        
        # Insert test data
        test_message = f"Connection test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        cursor.execute(
            "INSERT INTO connection_test (message, created_at) VALUES (%s, %s) RETURNING id;",
            (test_message, datetime.now())
        )
        inserted_id = cursor.fetchone()[0]
        conn.commit()
        print(f"  Created test record with ID: {inserted_id}")
        
        # Retrieve the data
        cursor.execute("SELECT id, message, created_at FROM connection_test ORDER BY created_at DESC LIMIT 5;")
        records = cursor.fetchall()
        
        print("\nRecent test records:")
        for record in records:
            print(f"  ID: {record[0]}, Time: {record[2]}, Message: {record[1]}")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        print("\nDatabase connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError connecting to PostgreSQL: {str(e)}")
        print("\nPossible issues to check:")
        print("  1. Is PostgreSQL running? Run: ~/status_postgres.sh")
        print("  2. Is PostgreSQL running on port 5433? Check the port in the connection string.")
        print("  3. Are the username and password correct?")
        print("  4. Can you connect using the command line tool?")
        print("     PGPASSWORD=l1 psql -h localhost -p 5433 -U l1_app_user -d l1_app_db")
        
        return False

if __name__ == "__main__":
    print("PostgreSQL Local Connection Test")
    print("=" * 30)
    test_postgresql_connection()