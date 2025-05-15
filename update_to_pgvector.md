# Updating Application to Use PostgreSQL 16.2 with pgvector

This guide explains how to update your application to use PostgreSQL 16.2 with pgvector for vector storage instead of FAISS.

## 1. Installation

First, install PostgreSQL 16.2 with pgvector extension using the provided installation script:

```bash
chmod +x install_postgres_pgvector.sh
./install_postgres_pgvector.sh
```

This script will:
- Install PostgreSQL 16.2 in your home directory (no root required)
- Install the pgvector extension
- Create user l1_app_user with password 'l1'
- Create database l1_app_db
- Enable pgvector extension in the database
- Create a document_embeddings table with proper indexes

## 2. Environment Configuration

After installation, update your environment variables:

```bash
chmod +x setup_local_env.sh
./setup_local_env.sh
```

This will create a `.env` file with the necessary PostgreSQL connection details.

## 3. Testing the Installation

Run the test script to verify that PostgreSQL with pgvector is working correctly:

```bash
python test_pgvector.py
```

This will test:
- pgvector initialization
- Adding embeddings
- Searching embeddings by similarity
- Retrieving embeddings
- Deleting embeddings

## 4. Migrating Existing Data

If you have existing embeddings in FAISS, migrate them to pgvector using:

```bash
python migrate_faiss_to_pgvector.py
```

This will:
- Load all embeddings from your FAISS indexes
- Insert them into the PostgreSQL pgvector database
- Verify the migration was successful

## 5. Updating Application Code

Update your application to use `services/pgvector_db.py` instead of `services/faiss_vector_db.py`:

### Import Changes

```python
# Change this:
from services.faiss_vector_db import add_embedding, search_embeddings, init_vector_db

# To this:
from services.pgvector_db import add_embedding, search_embeddings, init_vector_db
```

The API for pgvector_db.py is designed to be compatible with faiss_vector_db.py, so most code should work without changes.

### Main Application Initialization

Ensure your main application initializes the pgvector database:

```python
# In your main.py or app.py
from services.pgvector_db import init_vector_db

# Initialize at startup
init_vector_db()
```

### Web Scraping Integration

Update the web scraping functionality to use pgvector:

```python
# When importing text and creating embeddings:
from services.pgvector_db import add_embedding, batch_add_embeddings

# If using an embedding model:
model = ...  # Your embedding model
embedding = model.encode(text)
add_embedding(document_id, chunk_id, embedding, text, metadata)
```

## 6. Performance Considerations

pgvector vs. FAISS performance notes:

- **Search Speed**: FAISS may be faster for very large collections (millions of vectors), but pgvector performance is excellent for most use cases and offers the advantage of persistence.
  
- **Indexing**: The installation script creates an IVF index on the vector column. If you have more than 100K vectors, you might want to tune the `lists` parameter.

- **Connection Pooling**: For production applications, consider setting up connection pooling to avoid creating new database connections for each operation.

## 7. Monitoring

Monitor PostgreSQL performance:

```bash
# Check PostgreSQL status
~/status_postgres.sh

# View recent logs
tail -f ~/postgresql/logs/postgresql-*.log
```

## 8. Backup and Recovery

Regular backups are important:

```bash
# Create a backup
~/backup_postgres.sh

# Backups are stored in ~/postgresql/backups/
```

## 9. Troubleshooting

If you encounter issues:

1. Verify PostgreSQL is running: `~/status_postgres.sh`
2. Check the PostgreSQL logs: `tail -f ~/postgresql/logs/postgresql-*.log`
3. Test database connection: `python test_local_db_connection.py`
4. If pgvector operations fail, ensure the extension is enabled: 
   ```
   PGPASSWORD=l1 psql -h localhost -p 5433 -U l1_app_user -d l1_app_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```