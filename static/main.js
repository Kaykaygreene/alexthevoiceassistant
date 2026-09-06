import { Conversation } from "https://esm.sh/@elevenlabs/client@latest";

const startForm = document.getElementById("startForm");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const nameInput = document.getElementById("nameInput");
const orb = document.getElementById("orb");

let conversation = null;

function bubble(text, who) {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;
  div.textContent = text;
  transcriptEl.appendChild(div);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

// Keys must exactly match the tool names configured on the ElevenLabs agent
const clientTools = {
  generateimage: async ({ prompt, filename, size }) => {
    const data = await postJSON("/api/generateimage", { prompt, filename, size });
    if (data.url) bubble(`🖼️ Image ready: ${window.location.origin}${data.url}`, "agent");
    return data.result || data.error;
  },
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
  searchWeb: async ({ query }) => {
    const data = await postJSON("/api/searchweb", { query });
    return data.result || data.error;
  },
};

startForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    statusEl.textContent = "requesting microphone…";
    await navigator.mediaDevices.getUserMedia({ audio: true });

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
        statusEl.textContent = "connected";
        orb.classList.add("connected");
        startBtn.disabled = true;
        nameInput.disabled = true;
        stopBtn.disabled = false;
      },
      onDisconnect: () => {
        statusEl.textContent = "idle";
        orb.classList.remove("connected");
        startBtn.disabled = false;
        nameInput.disabled = false;
        stopBtn.disabled = true;
      },
      onMessage: (msg) => bubble(msg.message, msg.source === "ai" ? "agent" : "user"),
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