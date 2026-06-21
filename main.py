import network
import urequests
import ujson
import time
from machine import ADC, Pin
import gc

# ---------------- WIFI ----------------
ssid = "YOUR_WIFI_NAME"
password = "YOUR_WIFI_PASSWORD"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting WiFi...")

timeout = 15
while not wifi.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1

if not wifi.isconnected():
    raise Exception("WiFi Failed")

print("WiFi Connected:", wifi.ifconfig())

# ---------------- MIC ----------------
mic = ADC(Pin(35))
mic.atten(ADC.ATTN_11DB)
mic.width(ADC.WIDTH_12BIT)

SERVER_URL = "https://esp-vocie.onrender.com/upload"

# ---------------- RECORD ----------------
def record_audio(duration_ms=1500):
    samples = []
    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        val = mic.read()

        # center signal
        val = val - 2048

        # clamp (prevents clipping)
        if val > 1200:
            val = 1200
        if val < -1200:
            val = -1200

        samples.append(val)

        time.sleep_ms(2)

    return samples

# ---------------- SEND ----------------
def send_audio(samples):
    try:
        gc.collect()

        # LIMIT SIZE (VERY IMPORTANT)
        samples = samples[:800]

        payload = ujson.dumps({"samples": samples})

        print("\nSending samples:", len(samples))

        r = urequests.post(
            SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        print("Response:", r.text)
        r.close()

        gc.collect()

    except Exception as e:
        print("Error:", e)

# ---------------- LOOP ----------------
while True:
    print("\n🎤 Recording...")

    samples = record_audio()

    print("Samples captured:", len(samples))

    send_audio(samples)

    time.sleep(2)
