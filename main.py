from flask import Flask, request, jsonify
import numpy as np
import wave
import io
import os
from openai import OpenAI

app = Flask(__name__)

# 🔑 MUST be set in Render Environment Variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
    buffer.name = "audio.wav"
    return buffer

# ---------------------------
# Whisper transcription
# ---------------------------
def transcribe(wav_file):
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=wav_file
    )
    return result.text

# ---------------------------
# HOME
# ---------------------------
@app.route("/")
def home():
    return "Whisper Voice Server Running"

# ---------------------------
# MAIN UPLOAD ENDPOINT
# ---------------------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        samples = data["samples"]

        print("Received samples:", len(samples))

        # convert audio
        wav_file = samples_to_wav(samples)

        # Whisper AI
        text = transcribe(wav_file)

        print("TRANSCRIBED:", text)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
