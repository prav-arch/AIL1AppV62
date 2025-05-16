"""
ClickHouse Tables Inspection Script
This script connects to ClickHouse and displays information about tables,
specifically focusing on the llm_prompts table.
"""

from clickhouse_driver import Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ClickHouse connection parameters
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'port': 9000,
    'user': 'default',
    'password': '',
    'database': 'l1_app_db',
    'connect_timeout': 10
}

def check_tables():
    """Check tables in ClickHouse"""
    try:
        # Connect to ClickHouse
        client = Client(**CLICKHOUSE_CONFIG)
        
        # Show databases
        logger.info("Available databases:")
        databases = client.execute("SHOW DATABASES")
        for db in databases:
            print(f"- {db[0]}")
        
        # Show tables in the current database
        logger.info(f"\nTables in {CLICKHOUSE_CONFIG['database']}:")
        tables = client.execute(f"SHOW TABLES FROM {CLICKHOUSE_CONFIG['database']}")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check if llm_prompts table exists
        llm_prompts_exists = any(table[0] == 'llm_prompts' for table in tables)
        
        if llm_prompts_exists:
            # Show schema of the llm_prompts table
            logger.info("\nSchema of llm_prompts table:")
            schema = client.execute("DESCRIBE TABLE llm_prompts")
            print("\nColumn Name\tType\t\tDefault Type\tDefault Expression")
            print("-" * 70)
            for column in schema:
                print(f"{column[0]}\t{column[1]}\t{column[2]}\t{column[3] or 'None'}")
            
            # Count records in the llm_prompts table
            count = client.execute("SELECT count() FROM llm_prompts")[0][0]
            logger.info(f"\nNumber of records in llm_prompts table: {count}")
            
            # Show sample records if any exist
            if count > 0:
                logger.info("\nSample records from llm_prompts table:")
                sample = client.execute("""
                    SELECT id, prompt, substr(response, 1, 50) as response_preview, 
                           created_at, response_time
                    FROM llm_prompts
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                print("\nID\t\t\t\tPrompt\t\tResponse Preview\t\tCreated At\t\tResponse Time")
                print("-" * 120)
                for row in sample:
                    print(f"{row[0]}\t{row[1][:20]}...\t{row[2]}...\t{row[3]}\t{row[4]}")
        else:
            logger.info("\nllm_prompts table does not exist yet. Send a prompt to create it.")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to ClickHouse: {e}")
        return False

if __name__ == "__main__":
    check_tables()