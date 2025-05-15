"""
Start the AI Assistant Platform server on port 15000
"""

import os
from main import app
from waitress import serve

if __name__ == "__main__":
    port = 15000
    print(f"Starting server on port {port}...")
    serve(app, host="0.0.0.0", port=port)