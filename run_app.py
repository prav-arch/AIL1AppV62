import os
from main import app

if __name__ == "__main__":
    # Set default port to 15000 as requested
    port = int(os.environ.get("PORT", 15000))
    app.run(host='0.0.0.0', port=port, debug=True)