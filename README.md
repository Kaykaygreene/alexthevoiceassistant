# Alex — AI Voice Assistant

A web-based conversational AI assistant built with **Flask** and the **ElevenLabs Conversational AI SDK**. Alex listens (or reads typed messages), responds with natural-sounding speech, and can call custom backend tools mid-conversation — like searching the web, checking the weather, doing math, or saving generated content to a file.

---

## Overview

Alex runs as a small web app: a Flask backend serves the page and exposes a set of API routes, and a vanilla JS frontend connects to an ElevenLabs Conversational AI agent over a signed WebSocket session. The agent handles the actual conversation (speech-to-text, language understanding, and text-to-speech), and calls back into the Flask backend whenever it needs to use a tool.

Users can talk to Alex out loud, or switch to a text-based fallback mode. The UI shows a live animated "orb" that reacts while Alex is speaking, plus a scrolling transcript of the conversation.

---

## Features

- **Real-time voice conversation** via the ElevenLabs Conversational AI SDK (mic in, speech out).
- **Text mode fallback** — type messages instead of speaking, in the same session.
- **Personalized greetings** — the agent's first message and prompt are customized with the user's name.
- **Live transcript** of the full conversation, with a speaking indicator on the agent's messages.
- **Custom tools the agent can call:**
  - 🔍 `searchWeb` — search the web for a query
  - 🧮 `calculator` — evaluate a math expression
  - 🌤️ `weather` — check current weather for a location
  - 🕒 `getTime` — get the current time for a timezone
  - 📄 `saveToTxt` — save text content to a downloadable `.txt` file
  - 🌐 `createhtmlfile` — generate a downloadable HTML page from content
- Generated files (text/HTML) are saved server-side and linked directly in the chat transcript.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, vanilla JavaScript (ES modules) |
| Conversational AI | [ElevenLabs Conversational AI](https://elevenlabs.io/) (`@elevenlabs/client` SDK) |
| Voice | ElevenLabs speech-to-text and text-to-speech, via the agent |

---

## How It Works

1. The user enters their name and picks **Voice** or **Text** mode, then clicks **Start**.
2. The frontend requests a signed session URL from the backend (`/api/signed-url`) and any personalized prompt/greeting overrides (`/api/overrides`).
3. It opens a session with the ElevenLabs agent using that signed URL, passing the overrides and a set of **client tools**.
4. As the conversation runs, the agent streams responses and, when needed, invokes one of the client tools (e.g. `weather`). The frontend forwards that call to the matching Flask API route (e.g. `POST /api/weather`), gets a result, and returns it to the agent to continue the conversation.
5. Messages are rendered live in the transcript, and the orb animates while the agent is speaking.

---

## Requirements

- Python 3.9+
- Packages: `flask`, `requests`, `python-dotenv`, `duckduckgo_search`
- An ElevenLabs account with a configured Conversational AI **Agent** (for the Agent ID and prompt/voice setup)
- ElevenLabs API key

No API key is needed for weather (uses the free [Open-Meteo](https://open-meteo.com/) API) or web search (uses the `duckduckgo_search` package).

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kaykaygreene/alexthevoiceassistant.git
   cd alexthevoiceassistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install flask requests python-dotenv duckduckgo_search
   ```
   (or `pip install -r requirements.txt` if you've generated one with `pip freeze > requirements.txt`)

4. **Set your environment variables** in a `.env` file:
   ```env
   AGENT_ID="your_elevenlabs_agent_id_here"
   API_KEY="your_elevenlabs_api_key_here"
   ```
   > `ELEVENLABS_API_KEY` also works as the key name if you prefer — the app checks for either.

---

## Usage

1. Start the Flask app:
   ```bash
   python app.py
   ```
2. Open the app in your browser at `http://127.0.0.1:5000` (or the port set by the `PORT` env variable).
3. Enter your name, choose **🎙️ Voice** or **⌨️ Text** mode, and click **Start**.
4. Talk to (or type to) Alex. Click **End conversation** to stop the session.

Files created by the `saveToTxt` and `createhtmlfile` tools are written to a local `saved_files/` folder and served back at `/files/saved/<filename>`, with a direct link dropped into the transcript.

---

## Project Structure

```
alexthevoiceassistant/
├── app.py                 # Flask app: routes + API + tool endpoints
├── templates/
│   └── index.html         # Main page
├── static/
│   ├── main.js             # Frontend logic (ElevenLabs SDK integration)
│   └── style.css           # Styling
├── saved_files/            # Files created by saveToTxt / createhtmlfile (auto-generated)
├── requirements.txt
└── .env                    # API keys (not committed)
```

---

## Credits

Built by **Karlene A. Greene**
