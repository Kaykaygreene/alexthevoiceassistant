## Alex The Voice Assistant

A Python-based voice assistant using **OpenAI GPT** for conversational AI and **ElevenLabs** for speech synthesis. This assistant listens to your voice, responds naturally with speech, and can run custom tools like web searches or file saving.

---

## Features

* Conversational AI with **OpenAI GPT-3.5/4**.
* **Voice Generation** using **ElevenLabs** for natural-sounding voice.
* Tools include:

  * Web search
  * Saving text to files
  * Creating HTML files
  * Generating images via OpenAI DALL·E
* Modular design with **tool registration** for easy customization.

---

## Requirements

* Python 3.12+
* pip packages:

  ```bash
  pip install -r requirements.txt
  ```

* ElevenLabs API key.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Kaykaygreene/alexthevoiceassistant.git
   cd alexthevoiceassistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your **API keys** in a `.env` file:

   ```env
   OPENAI_API_KEY="your_openai_api_key_here"
   ELEVENLABS_API_KEY="your_elevenlabs_api_key_here"
   AGENT_ID="your_elevenlabs_agent_id_here"
   ```

---

## Usage

Run the assistant:

```bash
python main.py
```

Speak into your microphone. The assistant will respond with ElevenLabs-generated speech.

* Say **exit** to quit the program.

---

## Tools

The assistant supports these tools:

* **Web search**: `searchWeb(query="your query")`
* **Save to TXT**: `saveToTxt(filename="file.txt", data="your data")`
* **Create HTML file**: `createHtmlFile(filename="file.html", data="your content", title="Page Title")`
* **Generate image**: `generateImage(prompt="image description", filename="image.png")`

---
