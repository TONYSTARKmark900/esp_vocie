from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "ESP32 Voice Server Running"

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    print("Received from ESP32:", data)

    return jsonify({"status": "ok", "message": "received"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
