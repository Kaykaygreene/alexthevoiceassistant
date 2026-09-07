import os
import uuid
import math

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
# Supports either name so it matches your .env either way
API_KEY = os.getenv("API_KEY") or os.getenv("ELEVENLABS_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_FILES_DIR = os.path.join(BASE_DIR, "saved_files")
os.makedirs(SAVED_FILES_DIR, exist_ok=True)

app = Flask(__name__)

# Fallback value used only if a visitor leaves the name field blank
USER_NAME = "Alex"


def safe_filename(filename: str) -> str:
    """Strip any path parts so a tool call can't write outside its folder."""
    return os.path.basename(filename or f"{uuid.uuid4().hex}.txt")


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
    """Prompt/first_message override, served to the browser. Accepts
    an optional ?name= so each visitor is greeted by name."""
    name = request.args.get("name", "").strip() or USER_NAME

    prompt = (
        "You are Alex, a helpful voice assistant. You can answer general "
        "questions, chat casually, do quick math, search the web, tell the "
        "current date and time, check the weather for a place, save notes "
        "to a text file, and create a simple web page when asked. When you "
        "use a tool that saves a file, the app already shows the user a "
        "link to it automatically — just confirm what you made in a "
        "sentence or two. Don't add disclaimers about being text-based."
    )
    first_message = f"Hello {name}, I'm Alex, your voice assistant. How can I help you today?"
    return jsonify({"prompt": prompt, "first_message": first_message})


# ---------------------------------------------------------------------------
# Client tool endpoints — names/params must match exactly what's configured
# on the ElevenLabs agent
# ---------------------------------------------------------------------------
@app.route("/api/createhtmlfile", methods=["POST"])
def createhtmlfile():
    data = request.json or {}
    filename = safe_filename(data.get("filename", "page.html"))
    content = data.get("data", "")
    title = data.get("title", "Untitled")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<div>{content}</div>
</body>
</html>
"""
    path = os.path.join(SAVED_FILES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return jsonify({"result": f"Created {filename}", "url": f"/files/saved/{filename}"})


@app.route("/api/savetotxt", methods=["POST"])
def savetotxt():
    data = request.json or {}
    filename = safe_filename(data.get("filename", "notes.txt"))
    content = data.get("data", "")

    path = os.path.join(SAVED_FILES_DIR, filename)
    with open(path, "a", encoding="utf-8") as f:
        f.write(str(content) + "\n")

    return jsonify({"result": f"Saved to {filename}", "url": f"/files/saved/{filename}"})


@app.route("/api/searchweb", methods=["POST"])
def searchweb():
    from duckduckgo_search import DDGS

    query = (request.json or {}).get("query", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    summary = "\n".join(f"{r['title']}: {r['body']}" for r in results) or "No results found."
    return jsonify({"result": summary})


@app.route("/api/weather", methods=["POST"])
def weather():
    """Looks up current weather for a place name using Open-Meteo (free, no API key)."""
    place = (request.json or {}).get("location", "")
    if not place:
        return jsonify({"error": "Missing location"}), 400

    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": place, "count": 1},
        timeout=15,
    ).json()
    results = geo.get("results")
    if not results:
        return jsonify({"result": f"I couldn't find a place called {place}."})

    lat, lon = results[0]["latitude"], results[0]["longitude"]
    found_name = results[0].get("name", place)

    forecast = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "celsius",
        },
        timeout=15,
    ).json()
    current = forecast.get("current", {})
    temp = current.get("temperature_2m")

    if temp is None:
        return jsonify({"result": f"I couldn't get the weather for {found_name} right now."})

    return jsonify({"result": f"It's currently {temp}°C in {found_name}."})


@app.route("/api/calculator", methods=["POST"])
def calculator():
    expression = (request.json or {}).get("expression", "")
    if not expression:
        return jsonify({"error": "Missing expression"}), 400

    # Only allow safe characters — no arbitrary code execution
    allowed = set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        return jsonify({"result": "That expression contains characters I can't safely evaluate."})

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return jsonify({"result": f"{expression} = {result}"})
    except Exception:
        return jsonify({"result": f"I couldn't evaluate '{expression}'."})


@app.route("/api/gettime", methods=["POST"])
def gettime():
    tz_name = (request.json or {}).get("timezone", "America/Port_of_Spain")
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/Port_of_Spain")

    now = datetime.now(tz)
    formatted = now.strftime("%A, %B %d, %Y at %I:%M %p (%Z)")
    return jsonify({"result": formatted})


@app.route("/files/saved/<path:filename>")
def get_saved_file(filename):
    return send_from_directory(SAVED_FILES_DIR, filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)