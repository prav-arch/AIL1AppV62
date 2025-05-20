#!/bin/bash

# Script to download the Mistral 7B model for local LLM-based anomaly detection recommendations

echo "Creating model directory..."
mkdir -p /tmp/llm_models

# Set model details
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH="/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

echo "Downloading Mistral 7B model..."
echo "This may take some time depending on your internet connection..."

# Use wget with progress and retry options
wget -c --progress=bar --retry-connrefused --tries=5 -O "$MODEL_PATH" "$MODEL_URL"

# Check if download was successful
if [ $? -eq 0 ]; then
    echo "Download completed successfully!"
    echo "Model saved to: $MODEL_PATH"
    
    # Check file size to verify integrity
    FILE_SIZE=$(stat -c%s "$MODEL_PATH")
    echo "File size: $FILE_SIZE bytes"
    
    # A reasonable size check
    if [ "$FILE_SIZE" -gt 3000000000 ]; then
        echo "File size appears correct."
    else
        echo "Warning: File seems too small, it might be incomplete."
    fi
else
    echo "Error: Download failed!"
    exit 1
fi

echo "Model ready for use with the anomaly detection recommendation system."