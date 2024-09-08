from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Hello, world!"})

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    # Process webhook data
    return jsonify({"status": "success", "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
