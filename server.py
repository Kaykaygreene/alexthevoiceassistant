import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
# Supports either name so it matches your .env either way
API_KEY = os.getenv("API_KEY") or os.getenv("ELEVENLABS_API_KEY")

app = Flask(__name__)

# Same values your script hardcodes — move these to a database/session per
# visitor later if this needs to be personalized per user.
USER_NAME = "Karlene"
SCHEDULE = "Sales Meeting with Taipy at 10:00; Gym with Sophie at 17:00"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/signed-url")
def signed_url():
    if not AGENT_ID or not API_KEY:
        return jsonify({"error": "Server is missing AGENT_ID or API_KEY"}), 500

    resp = requests.get(
        "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        params={"agent_id": AGENT_ID},
        headers={"xi-api-key": API_KEY},
        timeout=15,
    )
    if not resp.ok:
        return jsonify({"error": "Failed to get signed URL", "detail": resp.text}), 500

    return jsonify(resp.json())


@app.route("/api/overrides")
def overrides():
    """Same prompt/first_message logic as your Python script's
    conversation_override, but served to the browser."""
    prompt = (
        f"You are a helpful assistant. Your interlocutor has the following "
        f"schedule: {SCHEDULE}."
    )
    first_message = f"Hello {USER_NAME} I am Alex, your voice assistant, how can I help you today?"
    return jsonify({"prompt": prompt, "first_message": first_message})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
