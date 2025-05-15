# PostgreSQL Installation Guide for Security-Restricted Environments

This guide provides instructions for installing PostgreSQL with pgvector support in environments with security restrictions.

## Option 1: Full Installation (Internet Access Required)

The `offline_postgres_setup.sh` script provides a complete PostgreSQL installation including:

- PostgreSQL 16.2 binary installation (no system privileges required)
- pgvector extension setup (for vector similarity search)
- Database creation with proper user setup
- Environment variable configuration

### Usage

```bash
# Make the script executable
chmod +x offline_postgres_setup.sh

# Run the installation script
./offline_postgres_setup.sh
```

The script will:
1. Download PostgreSQL binaries directly to your home directory
2. Set up PostgreSQL to run without root privileges
3. Create the database, user, and password according to requirements
4. Install pgvector extension
5. Configure the necessary environment variables

## Option 2: If You Face Security Issues

If the standard installation doesn't work due to security restrictions, you may need to:

1. **Change the port**: If port 5432 is blocked, modify the `PORT` variable in the script.

2. **Use pre-downloaded files**: If you can't download files directly, download PostgreSQL and pgvector on another machine and transfer them.

3. **Adjust connection method**: If direct connections are blocked, consider using SSH tunneling.

## Configuration Details

The installation configures:

- Database name: `l1_app_db`
- Database user: `l1_app_user`
- Database password: `test`
- Default port: `5432` (configurable)

## Environment Variables

After installation, you'll have two environment files:

1. `.pgenv`: PostgreSQL binary environment variables
2. `.env`: Application database connection details

Source the PostgreSQL environment in your shell:

```bash
source ~/.pgenv
```

## Managing PostgreSQL

Start PostgreSQL:
```bash
$PGINSTALL/bin/pg_ctl -D $PGDATA start
```

Stop PostgreSQL:
```bash
$PGINSTALL/bin/pg_ctl -D $PGDATA stop
```

Connect to database:
```bash
$PGINSTALL/bin/psql -d l1_app_db -U l1_app_user
```

## Troubleshooting

If you encounter issues:

1. **Port conflicts**: Change the port in the `.pgenv` file

2. **Permission errors**: Ensure all PostgreSQL directories have proper permissions
   ```bash
   chmod -R u+wx ~/postgres
   chmod -R u+wx ~/pgdata
   ```

3. **Connectivity issues**: Verify PostgreSQL is running
   ```bash
   $PGINSTALL/bin/pg_ctl -D $PGDATA status
   ```

4. **pgvector issues**: Check if the extension was created properly
   ```bash
   $PGINSTALL/bin/psql -d l1_app_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

## Application Connection

Your application should use this connection string:
```
postgresql://l1_app_user:test@localhost:5432/l1_app_db
```

All connection details are stored in the `.env` file in your home directory.

## Security Considerations

This installation is designed for non-root users in security-restricted environments:

- All files remain in user space (no system directories required)
- No root privileges needed
- Authentication configured for local connections only
- Default permissions set for user access only