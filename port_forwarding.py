"""
Port Forwarding Script
This script forwards requests from port 5000 to port 15000
"""
import socketserver
import http.server
import urllib.request
import urllib.error
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PortForwarding")

# Target application port (where the real application is running)
TARGET_PORT = 15000
# Source port (where Replit is listening)
SOURCE_PORT = 5000

class ForwardingHandler(http.server.BaseHTTPRequestHandler):
    """Handler that forwards requests from port 5000 to port 15000"""
    
    def do_GET(self):
        """Handle GET requests by forwarding them to port 15000"""
        self._forward_request("GET")
    
    def do_POST(self):
        """Handle POST requests by forwarding them to port 15000"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        self._forward_request("POST", post_data)
    
    def _forward_request(self, method, data=None):
        """Forward the request to the target port"""
        target_url = f"http://localhost:{TARGET_PORT}{self.path}"
        logger.info(f"Forwarding {method} request from port {SOURCE_PORT} to {target_url}")
        
        try:
            # Create the request
            req = urllib.request.Request(target_url, data=data, method=method)
            
            # Copy headers
            for header_name, header_value in self.headers.items():
                req.add_header(header_name, header_value)
            
            # Send the request to the target service
            with urllib.request.urlopen(req) as response:
                # Copy the response status code
                self.send_response(response.status)
                
                # Copy response headers
                for header_name, header_value in response.getheaders():
                    self.send_header(header_name, header_value)
                self.end_headers()
                
                # Copy the response body
                self.wfile.write(response.read())
                
        except urllib.error.URLError as e:
            logger.error(f"Failed to forward request: {e}")
            self.send_response(502)  # Bad Gateway
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error forwarding request: {e}".encode())

def start_port_forwarding():
    """Start the port forwarding server"""
    handler = ForwardingHandler
    server = socketserver.ThreadingTCPServer(("", SOURCE_PORT), handler)
    logger.info(f"Starting port forwarding from port {SOURCE_PORT} to port {TARGET_PORT}")
    server.serve_forever()
    
def start_application():
    """Start the actual application on port 15000"""
    import subprocess
    logger.info(f"Starting application on port {TARGET_PORT}")
    subprocess.Popen(["gunicorn", "--bind", f"0.0.0.0:{TARGET_PORT}", "main:app"])

if __name__ == "__main__":
    # Start the application on port 15000
    start_application()
    
    # Give it a moment to start up
    time.sleep(2)
    
    # Start the port forwarding service on port 5000
    forwarding_thread = threading.Thread(target=start_port_forwarding)
    forwarding_thread.daemon = True
    forwarding_thread.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Exiting port forwarding service")