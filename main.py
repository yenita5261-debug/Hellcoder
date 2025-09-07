from flask import Flask, request, jsonify, Response
import requests
import re
import threading

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================
TARGET = "https://osintpromax-2andkey-eishwk.onrender.com?query="

# Replacement
pattern = re.compile(r'@?promaxchatbot', re.I)

# ==============================
# STATE (to track active IP)
# ==============================
active_ip = None
lock = threading.Lock()

# ==============================
# ROUTES
# ==============================
@app.before_request
def check_single_active():
    global active_ip
    client_ip = request.remote_addr

    with lock:
        if active_ip is None:
            # पहला device -> allow and lock
            active_ip = client_ip
            print(f"✅ API locked to {client_ip}")
        elif active_ip != client_ip:
            # कोई और device -> block
            return jsonify({"error": f"Access locked for {active_ip}. Your IP {client_ip} denied."}), 403

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LODEMONHACKER API</title>
    </head>
    <body style="font-family: Arial; text-align:center; padding:40px;">
        <h2>🔥 Welcome to LODEMONHACKER API 🔥</h2>
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
            # Replace @ProMaxChatBot with @LOD3MON
            def replace_response(d):
                if isinstance(d, str):
                    return pattern.sub('@LOD3MON', d)
                if isinstance(d, list):
                    return [replace_response(i) for i in d]
                if isinstance(d, dict):
                    return {k: replace_response(v) for k, v in d.items()}
                return d
            return jsonify(replace_response(data))
        except Exception:
            replaced = pattern.sub('@LOD3MON', text)
            return Response(replaced, mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
