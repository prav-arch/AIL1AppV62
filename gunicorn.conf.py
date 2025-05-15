"""
Gunicorn configuration file
"""

import os

# Bind to the specified port (default to 15000)
bind = f"0.0.0.0:{os.environ.get('PORT', '15000')}"

# Number of worker processes
workers = 1

# Reload when code changes
reload = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'