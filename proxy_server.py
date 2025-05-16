"""
Proxy Server that listens on port 15000 and forwards to port 5000
This solves the port configuration issue without modifying workflows
"""
from flask import Flask, request, Response
import requests
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProxyServer")

app = Flask(__name__)

# Target application running on port 5000
TARGET_URL = "http://localhost:5000"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
def proxy(path):
    """
    Forward all requests to the target application
    """
    target = f"{TARGET_URL}/{path}"
    logger.info(f"Forwarding request to {target}")
    
    # Copy the incoming request method, headers, and data
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    try:
        # Forward the request to the target
        resp = requests.request(
            method=request.method,
            url=target,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            stream=True,
            verify=False  # Since we're connecting to localhost
        )
        
        # Create a Flask response object from the target response
        response = Response(
            response=resp.iter_content(chunk_size=10*1024),
            status=resp.status_code
        )
        
        # Copy response headers
        for key, value in resp.headers.items():
            if key.lower() not in ('transfer-encoding', 'content-encoding', 'content-length'):
                response.headers[key] = value
                
        return response
        
    except Exception as e:
        logger.error(f"Error forwarding request: {e}")
        return f"Proxy Error: {str(e)}", 500

def start_proxy_server():
    """Start the proxy server on port 15000"""
    app.run(host='0.0.0.0', port=15000, debug=False, threaded=True)

if __name__ == '__main__':
    # Start the proxy server in a thread
    proxy_thread = threading.Thread(target=start_proxy_server)
    proxy_thread.daemon = True
    proxy_thread.start()
    
    logger.info("Proxy server started on port 15000, forwarding to port 5000")
    
    # Keep the script running
    try:
        proxy_thread.join()
    except KeyboardInterrupt:
        logger.info("Proxy server shutting down")