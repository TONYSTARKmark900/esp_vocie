from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/")
def home():
    return "ESP32 Voice Server Running"

# -----------------------------
# UPLOAD ROUTE (FIXED PARSING)
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        # 🔥 IMPORTANT FIX: ESP32 sends raw JSON string
        raw_data = request.data

        print("\n📦 RAW DATA RECEIVED:", raw_data)

        # Decode JSON safely
        data = json.loads(raw_data)

        samples = data.get("samples", [])

        print("📥 Samples received:", len(samples))

        if len(samples) > 0:
            print("🔎 MIN:", min(samples), "MAX:", max(samples))
        else:
            print("⚠️ EMPTY SAMPLES RECEIVED")

        # -----------------------------
        # OPTIONAL: simple debug response
        # -----------------------------
        return jsonify({
            "status": "ok",
            "samples_received": len(samples)
        })

    except Exception as e:
        print("❌ SERVER ERROR:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    # IMPORTANT for Render / cloud hosting
    app.run(host="0.0.0.0", port=10000)
