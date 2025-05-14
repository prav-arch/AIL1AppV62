from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Test endpoint working"})

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Simple Test Page</h1>
            <p>Testing basic Flask functionality</p>
            <a href="/test" class="btn btn-primary">Test API</a>
        </div>
    </body>
    </html>
    """

app = app  # For Gunicorn to pick up

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)