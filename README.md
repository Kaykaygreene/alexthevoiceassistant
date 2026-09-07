# Alex — AI Voice Assistant

A conversational AI assistant built with the **ElevenLabs Conversational AI SDK**, available two ways: as a **web app** (Flask backend + browser UI) or as a **terminal CLI**. Alex listens (or reads typed messages), responds with natural-sounding speech, and can call custom tools mid-conversation — like searching the web, checking the weather, doing math, or saving generated content to a file.

---

## Overview

Alex has two entry points that share the same ElevenLabs agent:

- **`server.py` (web app)** — a Flask backend serves a browser UI and exposes a set of API routes. A vanilla JS frontend connects to the ElevenLabs Conversational AI agent over a signed WebSocket session, with a live animated "orb," a scrolling transcript, and a text-mode fallback. The agent calls back into the Flask backend whenever it needs to use a tool (search, weather, calculator, etc.).
- **`main.py` (CLI)** — a lightweight terminal script that connects to the same agent using the ElevenLabs Python SDK directly, using your machine's microphone and speakers for input/output. It's set up with a hardcoded name and daily schedule baked into the prompt, so it greets you and already knows your day's agenda.

In both cases, the agent itself (speech-to-text, language understanding, text-to-speech) is handled by ElevenLabs Conversational AI — the two scripts are just different front doors into it.

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
- **Terminal mode** (`main.py`) — talk to Alex directly through your mic and speakers, no browser needed, with a schedule/context baked into the prompt.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web backend | Python, Flask |
| Web frontend | HTML, CSS, vanilla JavaScript (ES modules), `@elevenlabs/client` SDK |
| CLI | Python, `elevenlabs` SDK (`Conversation`, `DefaultAudioInterface`) |
| Conversational AI | [ElevenLabs Conversational AI](https://elevenlabs.io/) |
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
- Packages: `flask`, `requests`, `python-dotenv`, `duckduckgo_search`, `elevenlabs` (for the CLI)
- A working microphone/speakers if running the CLI (`main.py`)
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
   pip install flask requests python-dotenv duckduckgo_search elevenlabs
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

### Option 1: Web app

1. Start the Flask app:
   ```bash
   python server.py
   ```
2. Open the app in your browser at `http://127.0.0.1:5000` (or the port set by the `PORT` env variable).
3. Enter your name, choose **🎙️ Voice** or **⌨️ Text** mode, and click **Start**.
4. Talk to (or type to) Alex. Click **End conversation** to stop the session.

Files created by the `saveToTxt` and `createhtmlfile` tools are written to a local `saved_files/` folder and served back at `/files/saved/<filename>`, with a direct link dropped into the transcript.

### Option 2: Terminal CLI

1. Run:
   ```bash
   python main.py
   ```
2. Alex greets you by name and speaks through your default speakers; reply out loud through your microphone.
3. Press `Ctrl+C` to end the session.

The CLI's name and schedule/context are currently hardcoded near the top of `main.py` — edit the `user_name` and `schedule` variables there to personalize it.

---

## Project Structure

```
alexthevoiceassistant/
├── server.py                 # Flask app: routes + API + tool endpoints (web version)
├── main.py                 # Terminal CLI version (mic + speakers, ElevenLabs Python SDK)
├── templates/
│   └── index.html         # Main page (web version)
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
