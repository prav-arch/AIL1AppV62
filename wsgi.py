import os
from app import app, socketio

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Run with Socket.IO integration
    socketio.run(app, host="0.0.0.0", port=port)
