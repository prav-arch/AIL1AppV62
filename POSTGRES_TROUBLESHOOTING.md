# PostgreSQL Troubleshooting Guide

This guide helps resolve common issues with the PostgreSQL installation on GPU servers without root privileges.

## Common Error 1: "pg_ctl: command not found"

**Problem**: The PostgreSQL binaries aren't in your system PATH.

**Solutions**:

1. Source the environment file:
   ```bash
   source ~/.pgenv
   ```

2. Use the full path to pg_ctl:
   ```bash
   /path/to/postgres16/bin/pg_ctl -D /path/to/postgres16/data start
   ```

3. Find where pg_ctl is installed:
   ```bash
   find ~/ -name "pg_ctl" -type f
   ```

## Common Error 2: "directory is not a database cluster directory"

**Problem**: The data directory hasn't been properly initialized with initdb.

**Solutions**:

1. Run the manual initialization script:
   ```bash
   ./initialize_db.sh
   ```
   This will guide you through initializing a new data directory.

2. Or manually initialize the directory:
   ```bash
   # Replace these paths with your actual paths
   /path/to/postgres16/bin/initdb -D /path/to/postgres16/data
   ```

3. Verify the data directory has the required files:
   ```bash
   ls -la /path/to/postgres16/data
   ```
   The directory should contain files like `PG_VERSION`, `postgresql.conf`, etc.

## Common Error 3: "could not connect to server"

**Problem**: The PostgreSQL server isn't running.

**Solutions**:

1. Start the server:
   ```bash
   /path/to/postgres16/bin/pg_ctl -D /path/to/postgres16/data start
   ```

2. Check if the server is already running:
   ```bash
   /path/to/postgres16/bin/pg_ctl -D /path/to/postgres16/data status
   ```

3. Check for port conflicts:
   ```bash
   netstat -tuln | grep 5432
   ```

## Common Error 4: "role l1_app_user does not exist"

**Problem**: The database user hasn't been created.

**Solution**:
```bash
/path/to/postgres16/bin/psql -d postgres -c "CREATE ROLE l1_app_user WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'test';"
```

## Common Error 5: "database l1_app_db does not exist"

**Problem**: The database hasn't been created.

**Solution**:
```bash
/path/to/postgres16/bin/createdb -O l1_app_user l1_app_db
```

## Common Error 6: Permission issues

**Problem**: Files or directories have incorrect permissions.

**Solution**:
```bash
chmod -R u=rwx /path/to/postgres16
chmod -R u=rwx /path/to/postgres16/data
```

## Getting Help

If you're still having issues, check the PostgreSQL log files:
```bash
tail -100 /path/to/postgres16/data/pg_log/postgresql-*.log
```

Or try running the server in foreground mode for more detailed output:
```bash
/path/to/postgres16/bin/postgres -D /path/to/postgres16/data
```