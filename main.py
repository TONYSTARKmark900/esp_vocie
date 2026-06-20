from flask import Flask, request, jsonify
import numpy as np
import wave
import io
import os
import requests

app = Flask(__name__)

# -------------------------
# CONVERT SAMPLES → WAV
# -------------------------
def samples_to_wav(samples):
    audio = np.array(samples, dtype=np.int16)

    # normalize signal (IMPORTANT)
    audio = audio * 16

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(8000)
        wf.writeframes(audio.tobytes())

    buffer.seek(0)
    return buffer

# -------------------------
# DEEPGRAM STT
# -------------------------
def transcribe_audio(wav_bytes):
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    url = "https://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }

    response = requests.post(url, headers=headers, data=wav_bytes)

    result = response.json()

    try:
        text = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    except:
        text = ""

    return text

# -------------------------
# COMMAND SYSTEM
# -------------------------
def process_command(text):
    text = text.lower()

    print("COMMAND TEXT:", text)

    if "activate command panel" in text:
        return "COMMAND_PANEL_ON"

    if "turn on light" in text:
        return "LIGHT_ON"

    if "turn off light" in text:
        return "LIGHT_OFF"

    return "UNKNOWN"

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return "ESP32 Voice System Running"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json

        samples = data["samples"]

        print("\nSamples received:", len(samples))

        wav_file = samples_to_wav(samples)

        text = transcribe_audio(wav_file.read())

        command = process_command(text)

        print("TEXT:", text)
        print("COMMAND:", command)

        return jsonify({
            "status": "ok",
            "text": text,
            "command": command
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "status": "error",
            "text": "",
            "command": "NONE"
        })

# -------------------------
# START SERVER
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
