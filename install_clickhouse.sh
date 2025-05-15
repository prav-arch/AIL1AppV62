#!/bin/bash

# ClickHouse Installation Script for security-restricted environments
# This installs ClickHouse without root privileges in your home directory

# Configuration
CLICKHOUSE_VERSION="23.8.8.20"
INSTALL_DIR="$HOME/clickhouse"
DATA_DIR="$HOME/clickhouse_data"
USER_DIR="$HOME/clickhouse_user"
TMP_DIR="$HOME/clickhouse_tmp"
PORT=9000  # Default ClickHouse port

echo "=== ClickHouse Installation Script ==="
echo "Installing ClickHouse $CLICKHOUSE_VERSION to $INSTALL_DIR"
echo "Data will be stored in $DATA_DIR"

# Create directories
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$USER_DIR" "$TMP_DIR"
cd "$HOME"

# Download ClickHouse binary
echo "Downloading ClickHouse binary..."
wget -q --no-check-certificate "https://github.com/ClickHouse/ClickHouse/releases/download/v$CLICKHOUSE_VERSION/clickhouse-common-static-$CLICKHOUSE_VERSION-amd64.tgz"
wget -q --no-check-certificate "https://github.com/ClickHouse/ClickHouse/releases/download/v$CLICKHOUSE_VERSION/clickhouse-server-$CLICKHOUSE_VERSION-amd64.tgz"
wget -q --no-check-certificate "https://github.com/ClickHouse/ClickHouse/releases/download/v$CLICKHOUSE_VERSION/clickhouse-client-$CLICKHOUSE_VERSION-amd64.tgz"

# Extract files
echo "Extracting ClickHouse binaries..."
tar -xzf "clickhouse-common-static-$CLICKHOUSE_VERSION-amd64.tgz" -C "$TMP_DIR"
tar -xzf "clickhouse-server-$CLICKHOUSE_VERSION-amd64.tgz" -C "$TMP_DIR"
tar -xzf "clickhouse-client-$CLICKHOUSE_VERSION-amd64.tgz" -C "$TMP_DIR"

# Move binaries to install directory
cp -r "$TMP_DIR/usr/bin" "$INSTALL_DIR/"

# Set permissions
chmod -R u+wx "$INSTALL_DIR" "$DATA_DIR" "$USER_DIR"

# Create basic configuration
echo "Creating ClickHouse configuration..."
mkdir -p "$USER_DIR/config"
mkdir -p "$USER_DIR/config.d"
mkdir -p "$USER_DIR/users.d"

# Generate main config file
cat > "$USER_DIR/config/config.xml" << EOL
<?xml version="1.0"?>
<clickhouse>
    <logger>
        <level>trace</level>
        <log>$USER_DIR/logs/clickhouse-server.log</log>
        <errorlog>$USER_DIR/logs/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>

    <path>$DATA_DIR/</path>
    <tmp_path>$DATA_DIR/tmp/</tmp_path>
    <user_files_path>$USER_DIR/user_files/</user_files_path>
    <format_schema_path>$USER_DIR/format_schemas/</format_schema_path>
    
    <mark_cache_size>5368709120</mark_cache_size>
    
    <listen_host>127.0.0.1</listen_host>
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    <interserver_http_port>9009</interserver_http_port>

    <max_connections>4096</max_connections>
    <keep_alive_timeout>10</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>
    <mark_cache_size>5368709120</mark_cache_size>
    
    <path>$DATA_DIR/</path>
    <tmp_path>$DATA_DIR/tmp/</tmp_path>
    
    <user_directories>
        <users_xml>
            <path>$USER_DIR/config/users.xml</path>
        </users_xml>
        <local_directory>
            <path>$USER_DIR/users.d/</path>
        </local_directory>
    </user_directories>
    
    <vector_index>
        <committee_size>3</committee_size>
        <max_elements_per_shard>100000</max_elements_per_shard>
        <vector_index_cache_size>536870912</vector_index_cache_size>
    </vector_index>
</clickhouse>
EOL

# Generate users config file
cat > "$USER_DIR/config/users.xml" << EOL
<?xml version="1.0"?>
<clickhouse>
    <users>
        <default>
            <password></password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
            <access_management>1</access_management>
        </default>
        
        <l1_app_user>
            <password>test</password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </l1_app_user>
    </users>

    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <load_balancing>random</load_balancing>
        </default>
    </profiles>

    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
</clickhouse>
EOL

# Create directory for logs
mkdir -p "$USER_DIR/logs"

# Create environment file
cat > "$HOME/.clickhouse_env" << EOL
# ClickHouse Environment Variables
export CLICKHOUSE_HOME="$INSTALL_DIR"
export CLICKHOUSE_DATA="$DATA_DIR"
export CLICKHOUSE_CONFIG="$USER_DIR/config/config.xml"
export CLICKHOUSE_USER_CONFIG="$USER_DIR/config/users.xml"
export PATH="\$CLICKHOUSE_HOME/bin:\$PATH"
EOL

# Set up environment for current session
source "$HOME/.clickhouse_env"

# Create .env file for the application
cat > "$HOME/.env" << EOL
# ClickHouse Connection Details
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=l1_app_user
CLICKHOUSE_PASSWORD=test
CLICKHOUSE_DATABASE=l1_app_db

# Using ClickHouse instead of PostgreSQL
DATABASE_TYPE=clickhouse
DATABASE_URL=clickhouse://l1_app_user:test@localhost:9000/l1_app_db
VECTOR_STORAGE=clickhouse
EOL

# Create database initialization script
cat > "$HOME/init_clickhouse_db.sql" << EOL
-- Create database
CREATE DATABASE IF NOT EXISTS l1_app_db;

-- Use the database
USE l1_app_db;

-- Create a table for documents
CREATE TABLE IF NOT EXISTS documents
(
    id String,
    name String,
    description String,
    metadata String,
    file_path String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Create a table for document chunks with vector support
CREATE TABLE IF NOT EXISTS document_chunks
(
    id UInt64,
    document_id String,
    chunk_index UInt32,
    chunk_text String,
    embedding Array(Float32),
    metadata String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, chunk_index);

-- Create vector index if ClickHouse supports it (23.8+)
-- This creates a MSTG (Multi-Space Tiny Graph) vector index
ALTER TABLE document_chunks ADD VECTOR INDEX embedding_idx embedding TYPE MSTG;

-- Create a table for vector database stats
CREATE TABLE IF NOT EXISTS vector_db_stats
(
    id UInt8,
    documents_count UInt32 DEFAULT 0,
    chunks_count UInt32 DEFAULT 0,
    vector_dim UInt16,
    last_modified DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY id;

-- Insert initial stats
INSERT INTO vector_db_stats (id, vector_dim) VALUES (1, 384);
EOL

# Create start script
cat > "$HOME/start_clickhouse.sh" << EOL
#!/bin/bash

# Start ClickHouse Server
source "\$HOME/.clickhouse_env"

# Check if ClickHouse is already running
if pgrep -f "clickhouse-server" > /dev/null; then
    echo "ClickHouse is already running."
else
    echo "Starting ClickHouse server..."
    "\$CLICKHOUSE_HOME/bin/clickhouse-server" --config="\$CLICKHOUSE_CONFIG" &
    
    # Wait for server to start
    sleep 5
    
    # Initialize database if needed
    if ! "\$CLICKHOUSE_HOME/bin/clickhouse-client" --query="SHOW DATABASES LIKE 'l1_app_db'" | grep -q "l1_app_db"; then
        echo "Initializing database..."
        "\$CLICKHOUSE_HOME/bin/clickhouse-client" < "\$HOME/init_clickhouse_db.sql"
        echo "Database initialized."
    fi
fi

echo "ClickHouse is running. Connect with:"
echo "\$CLICKHOUSE_HOME/bin/clickhouse-client --user=l1_app_user --password=test --database=l1_app_db"
EOL

# Create stop script
cat > "$HOME/stop_clickhouse.sh" << EOL
#!/bin/bash

# Stop ClickHouse Server
source "\$HOME/.clickhouse_env"

if pgrep -f "clickhouse-server" > /dev/null; then
    echo "Stopping ClickHouse server..."
    pkill -f "clickhouse-server"
    echo "ClickHouse server stopped."
else
    echo "ClickHouse server is not running."
fi
EOL

# Make scripts executable
chmod +x "$HOME/start_clickhouse.sh" "$HOME/stop_clickhouse.sh"

# Clean up temporary directory and downloaded archives
rm -rf "$TMP_DIR"
rm -f "$HOME/clickhouse-common-static-$CLICKHOUSE_VERSION-amd64.tgz"
rm -f "$HOME/clickhouse-server-$CLICKHOUSE_VERSION-amd64.tgz"
rm -f "$HOME/clickhouse-client-$CLICKHOUSE_VERSION-amd64.tgz"

echo "=== ClickHouse Installation Complete ==="
echo ""
echo "ClickHouse has been installed to $INSTALL_DIR"
echo ""
echo "To start ClickHouse server:"
echo "./start_clickhouse.sh"
echo ""
echo "To stop ClickHouse server:"
echo "./stop_clickhouse.sh"
echo ""
echo "To connect to ClickHouse:"
echo "$INSTALL_DIR/bin/clickhouse-client --user=l1_app_user --password=test --database=l1_app_db"
echo ""
echo "Connection string for your application:"
echo "clickhouse://l1_app_user:test@localhost:9000/l1_app_db"
echo ""
echo "Environment variables have been set in $HOME/.clickhouse_env"
echo "Add this line to your .bashrc or .profile to persist them:"
echo "source $HOME/.clickhouse_env"