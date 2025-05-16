"""
Start the application on port 15000
"""
import os
import subprocess
import signal
import time
import sys

# Set port to 15000
PORT = 15000

def handle_exit(signum, frame):
    """Handle exit signals"""
    print(f"Shutting down server on port {PORT}...")
    sys.exit(0)

def main():
    """Start the application on port 15000"""
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Kill any existing gunicorn processes
    try:
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        # Give it a moment to shut down
        time.sleep(1)
    except Exception as e:
        print(f"Warning: Failed to kill existing processes: {e}")
        
    # Start gunicorn on port 15000
    print(f"Starting application on port {PORT}...")
    
    # Build the command
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{PORT}",
        "--workers", "1",
        "main:app"
    ]
    
    # Execute the command
    process = subprocess.Popen(cmd)
    
    # Wait for the process to complete
    try:
        process.wait()
    except KeyboardInterrupt:
        print("Interrupted by user")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()