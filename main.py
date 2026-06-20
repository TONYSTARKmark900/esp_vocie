from flask import Flask, request, jsonify
import numpy as np
import wave
import io
import os
import requests

app = Flask(__name__)

# ---------------------------
# Convert ESP32 samples → WAV
# ---------------------------
def samples_to_wav(samples):
    audio = np.array(samples, dtype=np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(8000)
        wf.writeframes(audio.tobytes())

    buffer.seek(0)
    return buffer

# ---------------------------
# Deepgram Speech-to-Text
# ---------------------------
def transcribe_audio(wav_file):
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not api_key:
        raise Exception("Missing DEEPGRAM_API_KEY in environment variables")

    url = "https://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }

    response = requests.post(url, headers=headers, data=wav_file)

    result = response.json()

    # extract text safely
    text = result["results"]["channels"][0]["alternatives"][0]["transcript"]

    return text

# ---------------------------
# Home route
# ---------------------------
@app.route("/")
def home():
    return "ESP32 Deepgram Voice Server Running"

# ---------------------------
# Upload route (ESP32 sends here)
# ---------------------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        samples = data["samples"]

        print("Received samples:", len(samples))

        wav_file = samples_to_wav(samples)

        text = transcribe_audio(wav_file.read())

        print("VOICE TEXT:", text)

        return jsonify({
            "status": "ok",
            "text": text
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
