import { Conversation } from "https://esm.sh/@elevenlabs/client@latest";

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");

let conversation = null;

function log(text) {
  const p = document.createElement("p");
  p.textContent = text;
  transcriptEl.appendChild(p);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

startBtn.addEventListener("click", async () => {
  try {
    statusEl.textContent = "Status: requesting microphone…";
    await navigator.mediaDevices.getUserMedia({ audio: true });

    statusEl.textContent = "Status: connecting…";

    const [signedRes, overridesRes] = await Promise.all([
      fetch("/api/signed-url"),
      fetch("/api/overrides"),
    ]);
    const signedData = await signedRes.json();
    const overridesData = await overridesRes.json();
    if (signedData.error) throw new Error(signedData.error);

    conversation = await Conversation.startSession({
      signedUrl: signedData.signed_url,
      overrides: {
        agent: {
          prompt: { prompt: overridesData.prompt },
          firstMessage: overridesData.first_message,
        },
      },
      onConnect: () => {
        statusEl.textContent = "Status: connected";
        startBtn.disabled = true;
        stopBtn.disabled = false;
      },
      onDisconnect: () => {
        statusEl.textContent = "Status: idle";
        startBtn.disabled = false;
        stopBtn.disabled = true;
      },
      onMessage: (msg) => log(`${msg.source === "ai" ? "Alex" : "You"}: ${msg.message}`),
      onError: (err) => {
        console.error(err);
        statusEl.textContent = "Status: error (see console)";
      },
    });
  } catch (err) {
    console.error(err);
    statusEl.textContent = `Status: error — ${err.message}`;
  }
});

stopBtn.addEventListener("click", async () => {
  if (conversation) {
    await conversation.endSession();
    conversation = null;
  }
});
