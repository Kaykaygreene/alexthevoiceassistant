import os
import uuid
from io import BytesIO

import openai
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
# Supports either name so it matches your .env either way
API_KEY = os.getenv("API_KEY") or os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_FILES_DIR = os.path.join(BASE_DIR, "saved_files")
GENERATED_IMAGES_DIR = os.path.join(BASE_DIR, "generated_images")
os.makedirs(SAVED_FILES_DIR, exist_ok=True)
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

app = Flask(__name__)

# Fallback values used only if a visitor leaves the fields blank
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
        "questions, search the web, save notes to a text file, create a "
        "simple web page, and generate images when asked."
    )
    first_message = f"Hello {name}, I'm Alex, your voice assistant. How can I help you today?"
    return jsonify({"prompt": prompt, "first_message": first_message})

# ---------------------------------------------------------------------------
# Client tool endpoints — names/params match exactly what's configured on
# the ElevenLabs agent (generateimage, createhtmlfile, saveToTxt, searchWeb)
# ---------------------------------------------------------------------------
@app.route("/api/generateimage", methods=["POST"])
def generateimage():
    if not OPENAI_API_KEY:
        return jsonify({"error": "Server is missing OPENAI_API_KEY"}), 500

    data = request.json or {}
    prompt = data.get("prompt", "")
    filename = safe_filename(data.get("filename", "image.png"))
    size = data.get("size", "1024x1024")

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.images.generate(prompt=prompt, model="gpt-image-1", size=size, n=1)
    image_url = response.data[0].url

    img_response = requests.get(image_url, timeout=30)
    image = Image.open(BytesIO(img_response.content))
    path = os.path.join(GENERATED_IMAGES_DIR, filename)
    image.save(path)

    return jsonify({"result": f"Image saved as {filename}", "url": f"/files/images/{filename}"})


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


@app.route("/files/saved/<path:filename>")
def get_saved_file(filename):
    return send_from_directory(SAVED_FILES_DIR, filename)


@app.route("/files/images/<path:filename>")
def get_image_file(filename):
    return send_from_directory(GENERATED_IMAGES_DIR, filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)