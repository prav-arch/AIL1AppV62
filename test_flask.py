from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/api/test')
def test():
    return jsonify({"message": "API working"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)