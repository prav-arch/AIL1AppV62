#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Clean Minio Installation...${NC}"

# Create necessary directories
echo "Creating directories..."
mkdir -p ~/minio/data
mkdir -p ~/.minio

# Download Minio binary with certificate checks disabled
echo "Downloading Minio..."
wget --no-check-certificate https://dl.min.io/server/minio/release/linux-amd64/minio -O ~/minio/minio
chmod +x ~/minio/minio

# Download Minio client with certificate checks disabled
echo "Downloading Minio client..."
wget --no-check-certificate https://dl.min.io/client/mc/release/linux-amd64/mc -O ~/minio/mc
chmod +x ~/minio/mc

# Kill any existing Minio processes
echo "Terminating any existing Minio processes..."
pkill -9 -f "minio server" || true

# Remove any existing Minio configuration
echo "Removing existing Minio configuration..."
rm -rf ~/.minio/*

# Create brand-new configuration file
echo "Creating new configuration file..."
cat > ~/.minio/config.json << EOF
{
        "version": "10",
        "credential": {
                "accessKey": "dpcoeadmin",
                "secretKey": "dpcoeadmin"
        }
}
EOF

# Set permissions on config file
chmod 600 ~/.minio/config.json

# Create environment file
echo "Setting environment variables..."
cat > ~/minio/.env << EOF
export MINIO_ROOT_USER=dpcoeadmin
export MINIO_ROOT_PASSWORD=dpcoeadmin
EOF

# Create startup script
echo "Creating startup script..."
cat > ~/minio/start-clean-minio.sh << EOF
#!/bin/bash

# Source environment variables
source ~/minio/.env

# Print credentials for verification
echo "Starting Minio with credentials:"
echo "User: \$MINIO_ROOT_USER"
echo "Password: \$MINIO_ROOT_PASSWORD"

# Start Minio server with specific settings
~/minio/minio server --console-address :8001 --address :8000 --quiet ~/minio/data
EOF

chmod +x ~/minio/start-clean-minio.sh

# Create script to run Minio in foreground with debug output
cat > ~/minio/start-debug-minio.sh << EOF
#!/bin/bash

# Source environment variables
source ~/minio/.env

# Print credentials for verification
echo "Starting Minio in debug mode with credentials:"
echo "User: \$MINIO_ROOT_USER"
echo "Password: \$MINIO_ROOT_PASSWORD"

# Start Minio server with debugging enabled
~/minio/minio server --console-address :8001 --address :8000 ~/minio/data
EOF

chmod +x ~/minio/start-debug-minio.sh

# Start Minio in the background
echo "Starting Minio in the background..."
screen -dmS minio ~/minio/start-clean-minio.sh || {
  echo -e "${RED}Failed to start Minio in the background. Screen may not be installed.${NC}"
  echo -e "${YELLOW}You can run it in the foreground with: ~/minio/start-clean-minio.sh${NC}"
  exit 1
}

# Wait for Minio to start
echo "Waiting for Minio to start..."
sleep 5

# Configure Minio client
echo "Configuring Minio client..."
export MC_INSECURE=true
~/minio/mc config host remove myminio 2>/dev/null || true
~/minio/mc --insecure config host add myminio http://127.0.0.1:8000 dpcoeadmin dpcoeadmin

# Test if Minio is working
echo "Testing Minio connection..."
if ~/minio/mc ls myminio; then
  echo -e "${GREEN}Successfully connected to Minio!${NC}"
  
  # Create a bucket
  echo "Creating data bucket..."
  ~/minio/mc --insecure mb myminio/data-bucket || true
  
  # Display access information
  echo -e "${GREEN}Installation complete!${NC}"
  echo -e "${GREEN}Access the Minio API at: http://SERVER_IP:8000${NC}"
  echo -e "${GREEN}Access the Minio Console at: http://SERVER_IP:8001${NC}"
  echo -e "${GREEN}Username: dpcoe${NC}"
  echo -e "${GREEN}Password: dpcoeadmin${NC}"
else
  echo -e "${RED}Failed to connect to Minio.${NC}"
  echo -e "${YELLOW}You can check logs with: screen -r minio${NC}"
  echo -e "${YELLOW}Or try running in debug mode: ~/minio/start-debug-minio.sh${NC}"
fi

# Show management commands
echo -e "${GREEN}Management commands:${NC}"
echo -e "  ${YELLOW}Start:${NC} screen -dmS minio ~/minio/start-clean-minio.sh"
echo -e "  ${YELLOW}Stop:${NC} pkill -f 'minio server'"
echo -e "  ${YELLOW}Debug:${NC} ~/minio/start-debug-minio.sh"
echo -e "  ${YELLOW}View logs:${NC} screen -r minio"