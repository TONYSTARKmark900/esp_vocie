from flask import Flask, request, jsonify
import numpy as np
import wave
import io
import os
import requests

app = Flask(__name__)

# -----------------------------
# CONVERT ESP32 SAMPLES → WAV
# -----------------------------
def samples_to_wav(samples):
    audio = np.array(samples, dtype=np.int16)

    # clamp to avoid distortion crashes
    audio = np.clip(audio, -32768, 32767)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)      # 16-bit PCM
        wf.setframerate(8000)   # ESP32 typical rate
        wf.writeframes(audio.tobytes())

    buffer.seek(0)
    return buffer

# -----------------------------
# DEEPGRAM TRANSCRIPTION (FIXED)
# -----------------------------
def transcribe_audio(wav_bytes):
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not api_key:
        print("❌ Missing DEEPGRAM_API_KEY")
        return ""

    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }

    response = requests.post(url, headers=headers, data=wav_bytes)

    result = response.json()

    # DEBUG (VERY IMPORTANT)
    print("\n🔥 DEEPGRAM RAW RESPONSE:")
    print(result)

    try:
        text = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        return text
    except:
        return ""

# -----------------------------
# COMMAND ENGINE
# -----------------------------
def process_command(text):
    text = text.lower().strip()

    print("🧠 TEXT RECEIVED:", text)

    if "activate command panel" in text:
        return "COMMAND_PANEL_ON"

    if "turn on light" in text:
        return "LIGHT_ON"

    if "turn off light" in text:
        return "LIGHT_OFF"

    return "UNKNOWN"

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return "ESP32 Voice Server Running"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        samples = data.get("samples", [])

        print("\n📥 Samples received:", len(samples))

        if len(samples) == 0:
            return jsonify({
                "status": "error",
                "text": "",
                "command": "NO_AUDIO"
            })

        # DEBUG AUDIO SIGNAL
        print("🔎 MIN:", min(samples), "MAX:", max(samples))

        # Convert to WAV
        wav_file = samples_to_wav(samples)

        # Send to Deepgram
        text = transcribe_audio(wav_file.read())

        command = process_command(text)

        print("📝 FINAL TEXT:", text)
        print("⚡ COMMAND:", command)

        return jsonify({
            "status": "ok",
            "text": text,
            "command": command
        })

    except Exception as e:
        print("❌ ERROR:", e)

        return jsonify({
            "status": "error",
            "text": "",
            "command": "ERROR"
        })

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
