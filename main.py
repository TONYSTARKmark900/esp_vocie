from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "ESP32 Voice Server Running"

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        print("\n==================== NEW REQUEST ====================")

        # RAW DATA CHECK
        raw = request.data
        print("RAW DATA:", raw)

        # decode JSON safely
        data = json.loads(raw)

        samples = data.get("samples", [])

        print("📥 Samples received:", len(samples))

        if len(samples) > 0:
            print("🔎 MIN:", min(samples))
            print("🔎 MAX:", max(samples))
        else:
            print("⚠️ EMPTY SAMPLES")

        print("====================================================\n")

        return jsonify({
            "status": "ok",
            "samples": len(samples)
        })

    except Exception as e:
        print("❌ ERROR:", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
