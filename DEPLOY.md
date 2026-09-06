# Deploying Alex as a web app (shareable link)

This adds a browser-based version of Alex next to your desktop script. It
reproduces your `conversation_override` (dynamic prompt + first message)
using ElevenLabs' browser SDK instead of the Python SDK's `DefaultAudioInterface`,
since a public web link can't use your computer's microphone directly.

## 0. Rotate your API key first

You pasted a live ElevenLabs API key in a chat earlier. Revoke it in the
ElevenLabs dashboard and generate a new one before doing anything else below.
Never commit real keys to GitHub or paste them anywhere public — always keep
them in `.env` (already gitignored) or your host's secret manager.

## 1. Enable prompt/first-message overrides on your agent

In the ElevenLabs dashboard, open your agent → Security settings, and make
sure "First message" and "System prompt" overrides are allowed. Without this,
`conversation_config_override` (and this web app's equivalent) will be
ignored or rejected.

## 2. Push these new files to GitHub

    git add .
    git commit -m "Add web version for deployment"
    git push

## 3. Deploy on Render (free tier)

1. Go to https://render.com and sign in with GitHub.
2. New + -> Web Service -> select your `alexthevoiceassistant` repo.
3. Render should pick up `render.yaml` automatically. If not, set manually:
   - Build Command: `pip install -r requirements-web.txt`
   - Start Command: `gunicorn server:app`
4. Under Environment, add your (new, rotated) secrets:
   - `AGENT_ID`
   - `API_KEY`
5. Create Web Service. You'll get a public URL like
   `https://alex-voice-assistant.onrender.com` -- that's your shareable link.

Every future `git push` to `main` auto-redeploys.

## 4. Test it

Open the link, click "Start Conversation", allow microphone access, and talk.
Alex should greet you with the same first message and follow the same
schedule-aware prompt as your local script.

## Notes

- Free tier sleeps after inactivity -- first load after idle time takes
  ~30-60 seconds to wake up.
- This link is public once shared. Each conversation uses your ElevenLabs
  minutes, so keep an eye on usage/spending limits if you share it widely.
- Your original `main.py` still works locally exactly as before -- this is a
  separate way to reach the same agent from a browser.
