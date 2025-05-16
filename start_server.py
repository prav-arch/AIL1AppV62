"""
Server startup script that uses the correct port configuration
"""
import os
import sys
import subprocess
from port_config import PORT

def main():
    """Run the server on the configured port"""
    print(f"Starting server on port {PORT}...")
    
    # Build the gunicorn command with the correct port
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{PORT}",
        "--reuse-port",
        "--reload",
        "main:app"
    ]
    
    # Execute the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main()