# Deployment Instructions for LLM Assistant Application

## Local Deployment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   # Development mode
   python main.py
   
   # Production mode
   gunicorn --bind 0.0.0.0:15000 main:app
   ```

5. **Access the application:**
   - The application will be available at http://localhost:15000

## GPU Server Deployment

1. **Copy files to server:**
   ```bash
   scp -r * user@your-gpu-server:/path/to/deployment/directory
   ```

2. **Install dependencies on server:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run with systemd (recommended for production):**
   
   Create a systemd service file at `/etc/systemd/system/llm-assistant.service`:
   ```
   [Unit]
   Description=LLM Assistant Application
   After=network.target
   
   [Service]
   User=<your-username>
   WorkingDirectory=/path/to/deployment/directory
   ExecStart=/path/to/deployment/directory/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:15000 main:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable llm-assistant
   sudo systemctl start llm-assistant
   ```

5. **Check service status:**
   ```bash
   sudo systemctl status llm-assistant
   ```

## Notes

1. All CSS and JavaScript resources are included locally for offline use
2. The application runs on port 15000 by default
3. No external CDN dependencies are required
4. For development, modify `main.py` if you need to change configurations
5. Production deployments should set `debug=False` for security

## Troubleshooting

If styles are not loading properly, ensure:
1. All files in the `/static` directory are properly copied
2. The web server has permissions to access these files
3. No firewall rules are blocking access to port 15000