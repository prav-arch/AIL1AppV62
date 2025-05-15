# PostgreSQL Troubleshooting Guide

This guide addresses common problems when setting up PostgreSQL in security-restricted environments.

## Installation Problems

### Problem: Cannot download PostgreSQL binaries
**Solution:**
1. Download PostgreSQL binaries on another machine
2. Transfer the file via SCP or other secure file transfer
3. Continue the installation script from the extraction step

### Problem: Cannot compile pgvector
**Solution:**
1. Check if development tools are available:
   ```bash
   which gcc make
   ```
2. If not available, either:
   - Request them from your system administrator
   - Use a fallback method with FAISS for vector operations

### Problem: Directory permission issues
**Solution:**
1. Make sure all directories have proper permissions:
   ```bash
   chmod -R u+wx ~/postgres
   chmod -R u+wx ~/pgdata
   ```
2. Check if any parent directories have restrictive permissions

## Connection Problems

### Problem: Cannot connect to PostgreSQL
**Solution:**
1. Verify PostgreSQL is running:
   ```bash
   ~/postgres/bin/pg_ctl -D ~/pgdata status
   ```

2. Check connection settings:
   ```bash
   cat ~/.env
   ~/postgres/bin/psql -p 5432 -h localhost -U l1_app_user -d l1_app_db
   ```

3. If PostgreSQL is running but you cannot connect:
   - Check pg_hba.conf for connection restrictions
   - Verify port restrictions

### Problem: Application cannot connect to PostgreSQL
**Solution:**
1. Check environment variables:
   ```bash
   cat ~/.env
   echo $DATABASE_URL
   ```

2. Test connection with psql using the same credentials:
   ```bash
   ~/postgres/bin/psql "postgresql://l1_app_user:test@localhost:5432/l1_app_db"
   ```

3. Check for network restrictions between application and database

## pgvector Problems

### Problem: pgvector extension not available
**Solution:**
1. Verify the extension was created:
   ```bash
   ~/postgres/bin/psql -d l1_app_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

2. Manually create the extension:
   ```bash
   ~/postgres/bin/psql -d l1_app_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

3. If extension creation fails, check installation:
   ```bash
   cd ~/pgvector
   export PG_CONFIG=~/postgres/bin/pg_config
   make USE_PGXS=1
   make USE_PGXS=1 install
   ```

### Problem: Vector operations not working
**Solution:**
1. Test vector operations directly:
   ```bash
   ~/postgres/bin/psql -d l1_app_db -c "CREATE TABLE IF NOT EXISTS vector_test (id serial PRIMARY KEY, embedding vector(3));"
   ~/postgres/bin/psql -d l1_app_db -c "INSERT INTO vector_test (embedding) VALUES ('[1,2,3]');"
   ~/postgres/bin/psql -d l1_app_db -c "SELECT * FROM vector_test;"
   ```

2. If the test fails, try reinstalling pgvector with debug logs:
   ```bash
   cd ~/pgvector
   export PG_CONFIG=~/postgres/bin/pg_config
   make USE_PGXS=1 clean
   make USE_PGXS=1 CFLAGS="-g -O0" > pgvector_build.log 2>&1
   make USE_PGXS=1 install > pgvector_install.log 2>&1
   ```

## Security Problems

### Problem: Port access restricted
**Solution:**
1. Try using a non-standard port:
   - Edit `~/pgdata/postgresql.conf` to use a different port (e.g., 15432)
   - Update `.pgenv` and `.env` files with the new port
   - Restart PostgreSQL

2. If all ports are restricted, consider:
   - Setting up SSH tunnel for database access
   - Using Unix socket connections instead of TCP/IP

### Problem: Firewall blocking connections
**Solution:**
1. Verify local-only connections work:
   ```bash
   ~/postgres/bin/psql -h localhost -p 5432 -U l1_app_user -d l1_app_db
   ```

2. If local connections work but network connections don't:
   - Check firewall rules
   - Use local connections only for the application

## Fallback Options

If PostgreSQL cannot be installed or used due to security restrictions:

1. **FAISS Option**: Use FAISS for vector operations with SQLite for regular database operations
   - Modify application to use `VECTOR_STORAGE=faiss` in `.env`
   - Set `DATABASE_URL=sqlite:///~/database.sqlite` in `.env`

2. **Embedded Option**: Use SQLite with custom vector functions
   - Implement L2/cosine distance functions in SQLite
   - Store vectors as TEXT/BLOB in SQLite