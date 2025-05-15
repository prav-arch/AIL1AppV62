#!/usr/bin/env python3
"""
Example script demonstrating how to connect to the PostgreSQL with pgvector
using the l1_app_user, l1_app_db, and password 'test'
"""

import os
import json
import numpy as np
import psycopg2
from psycopg2.extras import Json, execute_values

# Database connection parameters
DB_PARAMS = {
    'dbname': 'l1_app_db',
    'user': 'l1_app_user',
    'password': 'test',
    'host': 'localhost',
    'port': '5432'
}

# Alternatively, use the DATABASE_URL (preferred method)
# DATABASE_URL = "postgresql://l1_app_user:test@localhost:5432/l1_app_db"
# Or use the environment variables:
# - PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

def connect_to_db():
    """Connect to the PostgreSQL database"""
    try:
        # Connection via database parameters
        conn = psycopg2.connect(
            dbname=DB_PARAMS['dbname'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
            host=DB_PARAMS['host'],
            port=DB_PARAMS['port']
        )
        
        # Alternative connection using URL: 
        # conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        
        print("Connected to PostgreSQL!")
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def verify_pgvector_extension():
    """Verify that the pgvector extension is properly installed"""
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            result = cursor.fetchone()
            if result:
                print(f"pgvector extension is installed: version {result[1]}")
                return True
            else:
                print("pgvector extension is not installed!")
                return False
        except Exception as e:
            print(f"Error verifying pgvector extension: {e}")
            return False
        finally:
            conn.close()
    return False

def create_vector_table():
    """Create a sample table with vector data type"""
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Drop table if it exists
            cursor.execute("DROP TABLE IF EXISTS vector_items;")
            
            # Create table with vector data type
            cursor.execute("""
                CREATE TABLE vector_items (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    embedding vector(384),
                    metadata JSONB
                );
            """)
            
            conn.commit()
            print("Vector table created successfully!")
            return True
        except Exception as e:
            print(f"Error creating vector table: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def insert_vector_data():
    """Insert sample vector data"""
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Generate some random vectors
            texts = [
                "This is a sample text for vector embedding",
                "Another example of text that will be embedded",
                "Vector databases are used for similarity search",
                "PostgreSQL with pgvector extension provides vector support"
            ]
            
            # Insert each text with a random vector
            for i, text in enumerate(texts):
                # Generate a random 384-dimensional vector
                vector = np.random.rand(384).astype(np.float32)
                # Normalize to unit length
                vector = vector / np.linalg.norm(vector)
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO vector_items (text, embedding, metadata)
                    VALUES (%s, %s, %s)
                """, (
                    text,
                    vector.tolist(),
                    Json({'index': i, 'source': 'example_script', 'length': len(text)})
                ))
            
            conn.commit()
            print(f"Inserted {len(texts)} vector items!")
            return True
        except Exception as e:
            print(f"Error inserting vector data: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def search_vectors():
    """Perform a vector similarity search"""
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Generate a random query vector
            query_vector = np.random.rand(384).astype(np.float32)
            query_vector = query_vector / np.linalg.norm(query_vector)
            
            # Search for similar vectors
            cursor.execute("""
                SELECT id, text, embedding <-> %s AS distance
                FROM vector_items
                ORDER BY distance
                LIMIT 2
            """, (query_vector.tolist(),))
            
            results = cursor.fetchall()
            print("\nVector search results:")
            for result in results:
                print(f"ID: {result[0]}, Distance: {result[2]:.4f}")
                print(f"Text: {result[1]}\n")
            
            return True
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return False
        finally:
            conn.close()
    return False

def main():
    """Main function to demonstrate PostgreSQL with pgvector usage"""
    print("PostgreSQL with pgvector Example\n")
    
    # Check if pgvector extension is installed
    if not verify_pgvector_extension():
        print("Please make sure pgvector extension is installed.")
        return
    
    # Create vector table
    if not create_vector_table():
        print("Failed to create vector table.")
        return
    
    # Insert sample data
    if not insert_vector_data():
        print("Failed to insert vector data.")
        return
    
    # Perform a similarity search
    if not search_vectors():
        print("Failed to search vectors.")
        return
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()