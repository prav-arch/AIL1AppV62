"""
LLM Service Manager
This module handles starting and managing the LLM service when the application starts
"""
import os
import subprocess
import threading
import time
import logging
import atexit

# LLM process global reference
llm_process = None
LLM_PORT = 15000

def start_llm_service():
    """Start the LLM service using the models in /tmp/llm_models"""
    global llm_process
    
    # Check if the LLM process is already running
    if llm_process is not None and llm_process.poll() is None:
        logging.info("LLM service is already running")
        return True
    
    logging.info("Starting LLM service...")
    
    # Check if model exists
    model_path = "/tmp/llm_models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        logging.warning(f"LLM model not found at {model_path}, checking alternative paths...")
        
        # Check for other models in the directory
        model_dir = "/tmp/llm_models"
        if os.path.exists(model_dir):
            models = [f for f in os.listdir(model_dir) if f.endswith('.gguf')]
            if models:
                model_path = os.path.join(model_dir, models[0])
                logging.info(f"Using alternative model: {model_path}")
            else:
                logging.error("No GGUF models found in /tmp/llm_models")
                return False
        else:
            logging.error("LLM models directory not found at /tmp/llm_models")
            return False
    
    try:
        # Start the LLM service in a separate process
        cmd = [
            "python3", "-m", "llama_cpp.server",
            "--model", model_path,
            "--host", "0.0.0.0",
            "--port", str(LLM_PORT),
            "--n-gpu-layers", "32",  # Use GPU acceleration
            "--chat-format", "llama-2"  # Use a standard chat format
        ]
        
        # Start the process
        llm_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Register function to clean up process on application exit
        atexit.register(stop_llm_service)
        
        # Start a thread to check the LLM service status
        threading.Thread(target=monitor_llm_service, daemon=True).start()
        
        # Wait a moment for the service to start
        time.sleep(2)
        
        # Check if the service started successfully
        if llm_process.poll() is not None:
            out, err = llm_process.communicate()
            logging.error(f"Failed to start LLM service: {err.decode('utf-8')}")
            return False
        
        logging.info(f"LLM service started on port {LLM_PORT}")
        return True
    
    except Exception as e:
        logging.error(f"Error starting LLM service: {str(e)}")
        return False

def stop_llm_service():
    """Stop the LLM service"""
    global llm_process
    
    if llm_process is not None:
        logging.info("Stopping LLM service...")
        
        try:
            llm_process.terminate()
            # Wait a few seconds for graceful termination
            for _ in range(5):
                if llm_process.poll() is not None:
                    break
                time.sleep(1)
                
            # Force kill if still running
            if llm_process.poll() is None:
                llm_process.kill()
                
            llm_process = None
            logging.info("LLM service stopped")
        except Exception as e:
            logging.error(f"Error stopping LLM service: {str(e)}")

def monitor_llm_service():
    """Monitor the LLM service and restart if it crashes"""
    global llm_process
    
    while True:
        # Check if process has exited
        if llm_process is not None and llm_process.poll() is not None:
            exit_code = llm_process.returncode
            logging.warning(f"LLM service exited with code {exit_code}, restarting...")
            
            # Clean up old process
            llm_process = None
            
            # Restart the service
            start_llm_service()
        
        # Check every 30 seconds
        time.sleep(30)

def check_llm_service():
    """Check if the LLM service is running"""
    global llm_process
    
    if llm_process is None:
        return False
    
    return llm_process.poll() is None