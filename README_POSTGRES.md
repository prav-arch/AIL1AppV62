# PostgreSQL 16.2 with pgvector Installation Guide

This guide explains how to install PostgreSQL 16.2 with the pgvector extension on a GPU server without root privileges.

## Prerequisites

- Linux-based server with GPU(s)
- GCC compiler and build tools
- Adequate storage space (~500MB for installation, plus space for data)
- An account without root privileges

## Installation Steps

1. **Download the installation script:**
   Make sure the script has executable permissions:
   ```
   chmod +x install_postgres_pgvector.sh
   ```

2. **Run the installation script:**
   ```
   ./install_postgres_pgvector.sh
   ```
   This will:
   - Download and compile PostgreSQL 16.2 in your home directory
   - Install pgvector extension
   - Create a database `l1_app_db` with user `l1_app_user` and password `test`
   - Set up necessary configuration files
   - Create `.pgenv` file with environment variables

3. **Load environment variables:**
   After installation, load the PostgreSQL environment variables:
   ```
   source ~/.pgenv
   ```
   To make this permanent, add to your `.bashrc` or `.profile`:
   ```
   echo 'source ~/.pgenv' >> ~/.bashrc
   ```

## Usage

The installation script creates a `.pgenv` file with all necessary environment variables:

- `PATH` - Updated to include PostgreSQL binaries
- `PGDATA` - Location of your PostgreSQL data directory
- `DATABASE_URL` - Connection string for applications
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Individual connection parameters

### Common PostgreSQL Commands

1. **Start PostgreSQL server:**
   ```
   pg_ctl -D $PGDATA start
   ```

2. **Stop PostgreSQL server:**
   ```
   pg_ctl -D $PGDATA stop
   ```

3. **Check PostgreSQL status:**
   ```
   pg_ctl -D $PGDATA status
   ```

4. **Connect to database:**
   ```
   psql -d l1_app_db
   ```

5. **Restart PostgreSQL:**
   ```
   pg_ctl -D $PGDATA restart
   ```

### Application Configuration

In your application's .env file, use the following database connection string:
```
DATABASE_URL=postgresql://l1_app_user:test@localhost:5432/l1_app_db
```

## pgvector Usage

After installation, the pgvector extension is available in your database. You can use it for storing and querying vector embeddings:

1. **Create a table with vector column:**
   ```sql
   CREATE TABLE items (
     id bigserial PRIMARY KEY,
     embedding vector(384)
   );
   ```

2. **Insert vector data:**
   ```sql
   INSERT INTO items (embedding) VALUES ('[1,2,3,...]');
   ```

3. **Perform similarity search:**
   ```sql
   SELECT * FROM items ORDER BY embedding <-> '[3,2,1,...]' LIMIT 5;
   ```

## Performance Tips for GPU Servers

- Store `PGDATA` on local SSD or fast storage if available
- Tune `shared_buffers` in postgresql.conf to optimize memory usage
- Set up a backup routine for your data
- Consider using `maintenance_work_mem` for vacuum operations

## File Permissions

The installation script sets all PostgreSQL files and directories with `u=rwx` permissions (read, write, execute for the user). This ensures that:

- You can read all configuration files
- You can write to data files and logs
- You can execute all PostgreSQL binaries

If you encounter permission issues after installation, you can restore the correct permissions with:

```bash
chmod -R u=rwx ~/postgres16
chmod -R u=rwx ~/postgres16/data
```

## Troubleshooting

If you encounter issues:

1. **Check logs:**
   ```
   tail -100 $PGDATA/pg_log/postgresql-*.log
   ```

2. **Verify pgvector installation:**
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

3. **Test vector operations:**
   ```sql
   CREATE TABLE vector_test (id serial, v vector(3));
   INSERT INTO vector_test (v) VALUES ('[1,2,3]'), ('[4,5,6]');
   SELECT * FROM vector_test ORDER BY v <-> '[3,1,2]' LIMIT 5;
   ```

4. **Check for port conflicts:**
   If PostgreSQL won't start, check if another process is using port 5432:
   ```
   netstat -tuln | grep 5432
   ```