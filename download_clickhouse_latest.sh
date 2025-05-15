#!/bin/bash

# ClickHouse Direct Binary Download Script
# This script downloads the latest stable ClickHouse binaries directly
# This approach works better for security-restricted environments

# Create download directory
mkdir -p ~/clickhouse_download
cd ~/clickhouse_download

echo "=== Downloading ClickHouse Latest Stable Binaries ==="

# Alternative download URLs using ClickHouse's official repositories
# These are more reliable and work in most environments
wget https://packages.clickhouse.com/deb/pool/stable/clickhouse-common-static_latest_amd64.deb
wget https://packages.clickhouse.com/deb/pool/stable/clickhouse-server_latest_amd64.deb
wget https://packages.clickhouse.com/deb/pool/stable/clickhouse-client_latest_amd64.deb

# Create directories for ClickHouse installation
mkdir -p ~/clickhouse
mkdir -p ~/clickhouse/bin
mkdir -p ~/clickhouse_data
mkdir -p ~/clickhouse_config
mkdir -p ~/clickhouse_config/config.d
mkdir -p ~/clickhouse_config/users.d
mkdir -p ~/clickhouse_config/logs
mkdir -p ~/clickhouse_tmp

echo "=== Extracting ClickHouse Binaries ==="

# Extract the .deb packages
for pkg in *.deb; do
  echo "Extracting $pkg..."
  dpkg-deb -x "$pkg" ~/clickhouse_tmp
done

# Copy the binaries to the bin directory
cp ~/clickhouse_tmp/usr/bin/clickhouse ~/clickhouse/bin/

# Set permissions
chmod -R u+wx ~/clickhouse
chmod -R u+wx ~/clickhouse_data
chmod -R u+wx ~/clickhouse_config

# Create basic configuration
echo "=== Creating ClickHouse Configuration ==="

# Generate main config file
cat > ~/clickhouse_config/config.xml << EOL
<?xml version="1.0"?>
<clickhouse>
    <logger>
        <level>trace</level>
        <log>$HOME/clickhouse_config/logs/clickhouse-server.log</log>
        <errorlog>$HOME/clickhouse_config/logs/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>

    <path>$HOME/clickhouse_data/</path>
    <tmp_path>$HOME/clickhouse_data/tmp/</tmp_path>
    <user_files_path>$HOME/clickhouse_config/user_files/</user_files_path>
    <format_schema_path>$HOME/clickhouse_config/format_schemas/</format_schema_path>
    
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
            <path>$HOME/clickhouse_config/users.xml</path>
        </users_xml>
        <local_directory>
            <path>$HOME/clickhouse_config/users.d/</path>
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
cat > ~/clickhouse_config/users.xml << EOL
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
cat > ~/init_clickhouse_db.sql << EOL
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

-- Create vector index (using HNSW which is better in newer versions)
ALTER TABLE document_chunks ADD VECTOR INDEX embedding_idx embedding TYPE HNSW;

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
cat > ~/start_clickhouse.sh << EOL
#!/bin/bash

# Start ClickHouse Server

# Set environment
export CLICKHOUSE_HOME="$HOME/clickhouse"
export CLICKHOUSE_CONFIG="$HOME/clickhouse_config/config.xml"

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
        "$CLICKHOUSE_HOME/bin/clickhouse" client < "$HOME/init_clickhouse_db.sql"
        echo "Database initialized."
    fi
fi

echo "ClickHouse is running. Connect with:"
echo "$CLICKHOUSE_HOME/bin/clickhouse client --user=l1_app_user --password=test --database=l1_app_db"
EOL

# Create stop script
cat > ~/stop_clickhouse.sh << EOL
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
cat > ~/.clickhouse_env << EOL
# ClickHouse Environment Variables
export CLICKHOUSE_HOME="$HOME/clickhouse"
export CLICKHOUSE_CONFIG="$HOME/clickhouse_config/config.xml"
export PATH="$CLICKHOUSE_HOME/bin:\$PATH"

# Database connection details
export CLICKHOUSE_HOST=localhost
export CLICKHOUSE_PORT=9000
export CLICKHOUSE_USER=l1_app_user
export CLICKHOUSE_PASSWORD=test
export CLICKHOUSE_DATABASE=l1_app_db

# Using ClickHouse for vectors
export DATABASE_TYPE=clickhouse
export DATABASE_URL=clickhouse://l1_app_user:test@localhost:9000/l1_app_db
export VECTOR_STORAGE=clickhouse
EOL

# Make scripts executable
chmod +x ~/start_clickhouse.sh
chmod +x ~/stop_clickhouse.sh

# Clean up
rm -rf ~/clickhouse_tmp
echo "Downloaded files are in ~/clickhouse_download"

echo "=== ClickHouse Latest Stable Download Complete ==="
echo ""
echo "ClickHouse has been downloaded to ~/clickhouse"
echo ""
echo "To start ClickHouse server:"
echo "~/start_clickhouse.sh"
echo ""
echo "To stop ClickHouse server:"
echo "~/stop_clickhouse.sh"
echo ""
echo "To connect to ClickHouse:"
echo "~/clickhouse/bin/clickhouse client --user=l1_app_user --password=test --database=l1_app_db"
echo ""
echo "Connection string for your application:"
echo "clickhouse://l1_app_user:test@localhost:9000/l1_app_db"
echo ""
echo "Environment file with connection details created at:"
echo "~/.clickhouse_env"
echo ""
echo "To load environment variables into your shell:"
echo "source ~/.clickhouse_env"