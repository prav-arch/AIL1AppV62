#!/bin/bash

# Direct ClickHouse version 24 binary download script
# No parameters - everything is hardcoded for maximum compatibility

# Create download directory
mkdir -p ~/clickhouse_download
cd ~/clickhouse_download

echo "=== Downloading ClickHouse 24.2.2.71 Binaries ==="

# Direct download links to ClickHouse 24.2.2.71 binaries
wget https://github.com/ClickHouse/ClickHouse/releases/download/v24.2.2.71/clickhouse-common-static-24.2.2.71-amd64.tgz
wget https://github.com/ClickHouse/ClickHouse/releases/download/v24.2.2.71/clickhouse-server-24.2.2.71-amd64.tgz
wget https://github.com/ClickHouse/ClickHouse/releases/download/v24.2.2.71/clickhouse-client-24.2.2.71-amd64.tgz

echo "=== Extracting ClickHouse Binaries ==="

# Create directories
mkdir -p ~/clickhouse24/bin
mkdir -p ~/clickhouse24_data
mkdir -p ~/clickhouse24_config
mkdir -p ~/clickhouse24_config/config.d
mkdir -p ~/clickhouse24_config/users.d
mkdir -p ~/clickhouse24_config/logs
mkdir -p ~/clickhouse24_tmp

# Extract binaries
tar -xzf clickhouse-common-static-24.2.2.71-amd64.tgz -C ~/clickhouse24_tmp
tar -xzf clickhouse-server-24.2.2.71-amd64.tgz -C ~/clickhouse24_tmp
tar -xzf clickhouse-client-24.2.2.71-amd64.tgz -C ~/clickhouse24_tmp

# Copy binaries to bin directory
cp ~/clickhouse24_tmp/usr/bin/clickhouse ~/clickhouse24/bin/

# Set permissions
chmod -R u+wx ~/clickhouse24
chmod -R u+wx ~/clickhouse24_data
chmod -R u+wx ~/clickhouse24_config

# Create basic configuration
echo "=== Creating ClickHouse Configuration ==="

# Generate main config file
cat > ~/clickhouse24_config/config.xml << EOL
<?xml version="1.0"?>
<clickhouse>
    <logger>
        <level>trace</level>
        <log>$HOME/clickhouse24_config/logs/clickhouse-server.log</log>
        <errorlog>$HOME/clickhouse24_config/logs/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>

    <path>$HOME/clickhouse24_data/</path>
    <tmp_path>$HOME/clickhouse24_data/tmp/</tmp_path>
    <user_files_path>$HOME/clickhouse24_config/user_files/</user_files_path>
    <format_schema_path>$HOME/clickhouse24_config/format_schemas/</format_schema_path>
    
    <listen_host>127.0.0.1</listen_host>
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    <interserver_http_port>9009</interserver_http_port>

    <max_connections>4096</max_connections>
    <keep_alive_timeout>10</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>
    <mark_cache_size>5368709120</mark_cache_size>
    
    <user_directories>
        <users_xml>
            <path>$HOME/clickhouse24_config/users.xml</path>
        </users_xml>
        <local_directory>
            <path>$HOME/clickhouse24_config/users.d/</path>
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
cat > ~/clickhouse24_config/users.xml << EOL
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

# Create database initialization script
cat > ~/init_clickhouse24_db.sql << EOL
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

-- Create vector index
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
cat > ~/start_clickhouse24.sh << EOL
#!/bin/bash

# Start ClickHouse Server

# Set environment
export CLICKHOUSE_HOME="$HOME/clickhouse24"
export CLICKHOUSE_CONFIG="$HOME/clickhouse24_config/config.xml"

# Check if ClickHouse is already running
if pgrep -f "clickhouse-server" > /dev/null; then
    echo "ClickHouse is already running."
else
    echo "Starting ClickHouse server..."
    "$CLICKHOUSE_HOME/bin/clickhouse" server --config="$CLICKHOUSE_CONFIG" &
    
    # Wait for server to start
    sleep 5
    
    # Initialize database if needed
    if ! "$CLICKHOUSE_HOME/bin/clickhouse" client --query="SHOW DATABASES LIKE 'l1_app_db'" | grep -q "l1_app_db"; then
        echo "Initializing database..."
        "$CLICKHOUSE_HOME/bin/clickhouse" client < "$HOME/init_clickhouse24_db.sql"
        echo "Database initialized."
    fi
fi

echo "ClickHouse is running. Connect with:"
echo "$CLICKHOUSE_HOME/bin/clickhouse client --user=l1_app_user --password=test --database=l1_app_db"
EOL

# Create stop script
cat > ~/stop_clickhouse24.sh << EOL
#!/bin/bash

# Stop ClickHouse Server
if pgrep -f "clickhouse-server" > /dev/null; then
    echo "Stopping ClickHouse server..."
    pkill -f "clickhouse-server"
    echo "ClickHouse server stopped."
else
    echo "ClickHouse server is not running."
fi
EOL

# Create environment file
cat > ~/.clickhouse24_env << EOL
# ClickHouse Environment Variables
export CLICKHOUSE_HOME="$HOME/clickhouse24"
export CLICKHOUSE_CONFIG="$HOME/clickhouse24_config/config.xml"
export PATH="$CLICKHOUSE_HOME/bin:\$PATH"
EOL

# Create .env file for application
cat > ~/.clickhouse_env << EOL
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

# Make scripts executable
chmod +x ~/start_clickhouse24.sh
chmod +x ~/stop_clickhouse24.sh

# Clean up
rm -rf ~/clickhouse24_tmp
echo "Downloaded files are in ~/clickhouse_download"

echo "=== ClickHouse 24 Download Complete ==="
echo ""
echo "ClickHouse has been downloaded to ~/clickhouse24"
echo ""
echo "To start ClickHouse server:"
echo "~/start_clickhouse24.sh"
echo ""
echo "To stop ClickHouse server:"
echo "~/stop_clickhouse24.sh"
echo ""
echo "To connect to ClickHouse:"
echo "~/clickhouse24/bin/clickhouse client --user=l1_app_user --password=test --database=l1_app_db"
echo ""
echo "Connection string for your application:"
echo "clickhouse://l1_app_user:test@localhost:9000/l1_app_db"
echo ""
echo "Environment file location:"
echo "~/.clickhouse24_env"