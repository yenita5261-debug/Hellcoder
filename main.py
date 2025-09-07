from flask import Flask, request, jsonify, Response
import requests
import re
import threading

app = Flask(name)

# ==============================
# CONFIG
# ==============================
TARGET = "https://osintpromax-2andkey-eishwk.onrender.com?query="

# Telegram bot config
TELEGRAM_TOKEN = "8237933590:AAF9KGzKfhHUGKGp8_6eZc5lI-JWzGFx39I"
CHAT_ID = "8016126238"

# Replacement
pattern = re.compile(r'@?promaxchatbot', re.I)

# ==============================
# STATE (to track active IP)
# ==============================
active_ip = None
lock = threading.Lock()

# ==============================
# UTILS
# ==============================
def send_to_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

def replace_response(data):
    if isinstance(data, str):
        return pattern.sub('@LOD3MON', data)
    if isinstance(data, list):
        return [replace_response(i) for i in data]
    if isinstance(data, dict):
        return {k: replace_response(v) for k, v in data.items()}
    return data

# ==============================
# ROUTES
# ==============================
@app.before_request
def check_single_active():
    global active_ip
    client_ip = request.remote_addr

    send_to_telegram(f"Request from {client_ip}")

    with lock:
        if active_ip is None:
            active_ip = client_ip
            send_to_telegram(f"✅ API locked to {client_ip}")
        elif active_ip != client_ip:
            return jsonify({"error": f"Access locked for {active_ip}. Your IP {client_ip} denied."}), 403

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAVAN API</title>
    </head>
    <body style="font-family: Arial; text-align:center; padding:40px;">
        <h2>🔥 Welcome to RAVAN API 🔥</h2>
        <p>Use: <code>/search?query=919999999999</code></p>
    </body>
    </html>
    """

@app.route("/search")
def search():
    number = request.args.get("query")
    if not number:
        return jsonify({"error": "Please provide ?query=NUMBER"}), 400

    try:
        resp = requests.get(TARGET + number, timeout=10)
        text = resp.text

        try:
            data = resp.json()
            return jsonify(replace_response(data))
        except Exception:
            replaced = pattern.sub('@LOD3MON', text)
            return Response(replaced, mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if name == "main":
    app.run(host="0.0.0.0", port=5000)