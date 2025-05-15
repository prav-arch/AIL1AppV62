# Updating Application Configuration for Local PostgreSQL

After installing PostgreSQL using the `install_postgres_no_root.sh` script, you'll need to update your application to use the local database. Here's how to do it:

## 1. Update Environment Variables

Create or modify your `.env` file to include these variables:

```
# PostgreSQL Connection Information
DATABASE_URL=postgresql://l1_app_user:l1@localhost:5433/l1_app_db
PGUSER=l1_app_user
PGPASSWORD=l1
PGDATABASE=l1_app_db
PGHOST=localhost
PGPORT=5433
```

## 2. Application Configuration Update

If your application has a database configuration file (like `config.py`), update it with:

```python
# Database Configuration
DB_CONFIG = {
    'user': 'l1_app_user',
    'password': 'l1',
    'host': 'localhost',
    'port': '5433',
    'database': 'l1_app_db'
}

# SQLAlchemy URI
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
```

## 3. Run Database Migrations

After updating the configuration, you may need to run database migrations:

```bash
# Using Flask-Migrate (if applicable)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or using SQLAlchemy directly
python -c "from app import db; db.create_all()"
```

## 4. Testing the Connection

Create a test script to verify the connection:

```python
# test_db_connection.py
import os
import psycopg2

# Get database connection parameters
db_params = {
    'dbname': os.environ.get('PGDATABASE', 'l1_app_db'),
    'user': os.environ.get('PGUSER', 'l1_app_user'),
    'password': os.environ.get('PGPASSWORD', 'l1'),
    'host': os.environ.get('PGHOST', 'localhost'),
    'port': os.environ.get('PGPORT', '5433'),
}

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Successfully connected to PostgreSQL: {version[0]}")
    
    # Close communication with the database
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
```

Run the test script with:

```bash
python test_db_connection.py
```

## 5. Restarting Your Application

After making these changes, restart your application to apply the new database configuration:

```bash
# For Flask applications
flask run

# Or using gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Important Notes

1. **Port Conflict**: The script installs PostgreSQL on port 5433 (not the default 5432) to avoid conflicts with existing PostgreSQL installations.

2. **Database Schema**: If you're switching from an existing database, you'll need to recreate your schema in the new database.

3. **Connection Pooling**: For production applications, consider configuring a connection pool for better performance.