# proxy_app.py
import os, requests
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

RECCO_TRACK = "https://api.reccobeats.com/v1/track"
RECCO_FEATURES = "https://api.reccobeats.com/v1/track/{track_id}/audio-features"

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/reccobeats/track")
def track():
    ids = request.args.get("ids")
    if not ids:
        return jsonify({"error": "missing ids"}), 400
    url = f"{RECCO_TRACK}?ids={ids}"
    r = requests.get(url, timeout=10)
    return jsonify(r.json()), r.status_code

@app.route("/reccobeats/audio-features/<tid>")
def features(tid):
    url = RECCO_FEATURES.format(track_id=tid)
    r = requests.get(url, timeout=10)
    return jsonify(r.json()), r.status_code

@app.route("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run()