import { Conversation } from "https://esm.sh/@elevenlabs/client@latest";

const startForm = document.getElementById("startForm");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const nameInput = document.getElementById("nameInput");
const orb = document.getElementById("orb");
const voiceModeBtn = document.getElementById("voiceModeBtn");
const textModeBtn = document.getElementById("textModeBtn");
const textFallback = document.getElementById("textFallback");
const textInput = document.getElementById("textInput");
const textSendBtn = document.getElementById("textSendBtn");
const modeSection = document.getElementById("modeSection");

let conversation = null;
let mode = "voice";
let hasGreeted = false;
let currentAgentBubble = null; 
function setMode(newMode) {
  mode = newMode;
  voiceModeBtn.classList.toggle("active", mode === "voice");
  textModeBtn.classList.toggle("active", mode === "text");
}
function bubble(text, who) {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;

  if (who === "agent") {
    const icon = document.createElement("span");
    icon.className = "speaker-icon";
    icon.textContent = "🔊";
    div.appendChild(icon);
    currentAgentBubble = div;
  }

  const textNode = document.createElement("span");
  textNode.textContent = text;
  div.appendChild(textNode);

  transcriptEl.appendChild(div);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

function setSpeaking(isSpeaking) {
  orb.classList.toggle("speaking", isSpeaking);
  statusEl.textContent = isSpeaking ? "Alex is speaking…" : "connected";
  if (currentAgentBubble) {
    currentAgentBubble.classList.toggle("speaking", isSpeaking);
  }
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function sendTextMessage() {
  const text = textInput.value.trim();
  if (!text || !conversation) return;
  bubble(text, "user");
  textInput.value = "";
  try {
    await conversation.sendUserMessage(text);
  } catch (err) {
    console.error(err);
    bubble("⚠️ Message failed — the session may have disconnected.", "agent");
  }
}

voiceModeBtn.addEventListener("click", () => setMode("voice"));
textModeBtn.addEventListener("click", () => setMode("text"));
textSendBtn.addEventListener("click", sendTextMessage);
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendTextMessage();
});
nameInput.addEventListener("focus", () => {
  modeSection.classList.remove("hidden");
}, { once: true });

// Keys must exactly match the tool names configured on the ElevenLabs agent
const clientTools = {
  createhtmlfile: async ({ title, filename, data: content }) => {
    const data = await postJSON("/api/createhtmlfile", { title, filename, data: content });
    if (data.url) bubble(`🌐 Page ready: ${window.location.origin}${data.url}`, "agent");
    return data.result || data.error;
  },
  saveToTxt: async ({ filename, data: content }) => {
    const data = await postJSON("/api/savetotxt", { filename, data: content });
    if (data.url) bubble(`📄 Saved: ${window.location.origin}${data.url}`, "agent");
    return data.result || data.error;
  },
  calculator: async ({ expression }) => {
    const data = await postJSON("/api/calculator", { expression });
    return data.result || data.error;
  },
  getTime: async ({ timezone }) => {
    const data = await postJSON("/api/gettime", { timezone });
    return data.result || data.error;
  },
  searchWeb: async ({ query }) => {
    const data = await postJSON("/api/searchweb", { query });
    return data.result || data.error;
  },
  weather: async ({ location }) => {
    const data = await postJSON("/api/weather", { location });
    return data.result || data.error;
  },
};

startForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    if (mode === "voice") {
      statusEl.textContent = "requesting microphone…";
      await navigator.mediaDevices.getUserMedia({ audio: true });
    }

    statusEl.textContent = "connecting…";

    const name = encodeURIComponent(nameInput.value.trim());
    const [signedRes, overridesRes] = await Promise.all([
      fetch("/api/signed-url"),
      fetch(`/api/overrides?name=${name}`),
    ]);
    const signedData = await signedRes.json();
    const overridesData = await overridesRes.json();
    if (signedData.error) throw new Error(signedData.error);

    conversation = await Conversation.startSession({
      signedUrl: signedData.signed_url,
      clientTools,
      overrides: {
        agent: {
          prompt: { prompt: overridesData.prompt },
          firstMessage: overridesData.first_message,
        },
        
      },
onConnect: () => {
  hasGreeted = false;
    currentAgentBubble = null; 
  statusEl.textContent = "Alex is speaking…";
  orb.classList.add("connected", "speaking");
  startBtn.disabled = true;
  nameInput.disabled = true;
  stopBtn.disabled = false;
  textInput.disabled = true;
  textSendBtn.disabled = true;
},
onDisconnect: () => {
  statusEl.textContent = "idle";
  orb.classList.remove("connected", "speaking");
  startBtn.disabled = false;
  nameInput.disabled = false;
  stopBtn.disabled = true;
  textInput.disabled = true;
  textSendBtn.disabled = true;
  textFallback.style.display = "none";
  hasGreeted = false;
  conversation = null;
},
onMessage: (msg) => {
  bubble(msg.message, msg.source === "ai" ? "agent" : "user");
  if (msg.source === "ai" && !hasGreeted) {
    hasGreeted = true;
    setSpeaking(false);
    textInput.disabled = false;
    textSendBtn.disabled = false;
    if (mode === "text") {
      textFallback.style.display = "flex";
    }
  }
},
      onError: (err) => {
        console.error(err);
        statusEl.textContent = "error (see console)";
      },
    });
  } catch (err) {
    console.error(err);
    statusEl.textContent = `error — ${err.message}`;
  }
});

stopBtn.addEventListener("click", async () => {
  if (conversation) {
    await conversation.endSession();
    conversation = null;
  }
});