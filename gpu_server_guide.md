# GPU Server Deployment Guide

This guide will help you deploy the application to your GPU server while ensuring it connects to ClickHouse and uses GPU acceleration.

## Prerequisites

1. A CUDA-capable GPU server with CUDA libraries installed
2. ClickHouse 18.16.1 installed and running at localhost:9000
3. Python 3.8+ installed on the server

## Installation Steps

1. **Clone the repository to your GPU server**

2. **Install required dependencies**:
   ```bash
   pip install flask clickhouse-driver gunicorn llama-cpp-python faiss-cpu
   
   # Install llama-cpp-python with CUDA support (important for GPU acceleration)
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall
   ```

3. **Download the LLM model**:
   ```bash
   mkdir -p /tmp/llm_models
   wget -O /tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

4. **Set up ClickHouse database**:
   ```bash
   # Create database if not exists
   clickhouse-client -q "CREATE DATABASE IF NOT EXISTS l1_app_db"
   ```

5. **Update environment variables**:
   Create a `.env` file in the application root with:
   ```
   USE_REAL_CLICKHOUSE=1
   CLICKHOUSE_HOST=localhost
   CLICKHOUSE_PORT=9000
   CLICKHOUSE_USER=default
   CLICKHOUSE_PASSWORD=
   CLICKHOUSE_DB=l1_app_db
   LLM_MODEL_PATH=/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

## Running the Application

1. **Start the application**:
   ```bash
   # Run with Gunicorn
   gunicorn --bind 0.0.0.0:15000 --reuse-port --reload main:app
   ```

2. **Check that the application is running**:
   Open a browser on your server and go to: `http://localhost:15000`

## Testing

1. **Verify GPU acceleration**:
   The console logs should show messages about using GPU layers. Look for log entries like:
   ```
   LLAMA_CUBLAS=1, FP16=1
   Using CUDA for GPU acceleration
   ```

2. **Check ClickHouse connectivity**:
   Go to the dashboard and make sure the application displays LLM query counts correctly.

3. **Test the LLM functionality**:
   Go to the LLM Assistant tab and try sending a query to verify it uses the GPU.

## Troubleshooting

### GPU Not Detected
- Make sure CUDA libraries are installed: `nvidia-smi` should show your GPU
- Verify llama-cpp-python is installed with CUDA support

### ClickHouse Connection Issues
- Check if ClickHouse is running: `clickhouse-client -q "SELECT 1"`
- Verify the connection parameters in your .env file
- Make sure the l1_app_db database exists

### LLM Model Not Found
- Double check the model path in the environment variables
- Verify the model file exists and is readable

### Application Crashes
- Check the application logs for specific error messages
- Increase memory limits if necessary for large models