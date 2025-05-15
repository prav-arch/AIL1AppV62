#!/bin/bash

# Install Python requirements for hybrid ClickHouse 18.16.1 + FAISS setup
# This script installs the necessary Python libraries to work with
# ClickHouse 18.16.1 and FAISS for vector search

# Create a virtual environment (optional)
echo "Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."

# Install ClickHouse driver for Python
pip install clickhouse-driver==0.2.0  # Version compatible with ClickHouse 18.16.1

# Install FAISS for vector search
# For CPU-only version
pip install faiss-cpu

# For GPU version (if CUDA is available)
# pip install faiss-gpu

# Install other required packages
pip install numpy  # Required for FAISS
pip install scikit-learn  # For vector operations and dimensionality reduction
pip install pandas  # For data manipulation
pip install requests  # For API calls
pip install flask  # Web framework
pip install python-dotenv  # For environment variables

echo "Installation complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "To test the installation, try importing the packages in Python:"
echo "python -c 'import clickhouse_driver; import faiss; import numpy; print(\"All packages imported successfully!\")'"