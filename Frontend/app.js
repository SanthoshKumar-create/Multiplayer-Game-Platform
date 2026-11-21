// Replace this with your deployed API Gateway stage URL. Do not add a trailing slash.
const API_BASE_URL = "PASTE_API_GATEWAY_INVOKE_URL_HERE";

const messageEl = document.getElementById("message");
const sessionView = document.getElementById("session-view");
const statusPill = document.getElementById("status-pill");

function showMessage(message, isError = false) {
  messageEl.textContent = message;
  messageEl.style.color = isError ? "#ff9b9b" : "#69e0db";
}
function ensureApiConfigured() {
  if (!API_BASE_URL.startsWith("https://")) {
    throw new Error("Configure your API Gateway URL in frontend/app.js before using the app.");
  }
}
async function api(path, options = {}) {
  ensureApiConfigured();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {"Content-Type":"application/json", ...(options.headers || {})}
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || data.error || `Request failed (${response.status})`);
  return data;
}
function renderSession(session) {
  const players = Array.isArray(session.players) ? session.players : [];
  sessionView.innerHTML = `
    <div class="session-card">
      <p class="eyebrow">SESSION IDENTIFIER</p>
      <div class="session-id"></div>
      <div class="stats">
        <div class="stat"><small>PLAYERS</small><strong class="player-count"></strong></div>
        <div class="stat"><small>CAPACITY</small><strong class="capacity"></strong></div>
        <div class="stat"><small>STATUS</small><strong class="session-status"></strong></div>
      </div>
      <p class="eyebrow">HOST</p><p class="host-name"></p>
      <p class="eyebrow">PLAYERS IN ROOM</p><div class="players"></div>
    </div>`;
  sessionView.querySelector(".session-id").textContent = session.sessionId;
  sessionView.querySelector(".player-count").textContent = players.length;
  sessionView.querySelector(".capacity").textContent = session.maxPlayers;
  sessionView.querySelector(".session-status").textContent = session.status || "WAITING";
  sessionView.querySelector(".host-name").textContent = session.host || "—";
  const playerBox = sessionView.querySelector(".players");
  players.forEach(name => {
    const chip = document.createElement("span");
    chip.className = "player";
    chip.textContent = name;
    playerBox.appendChild(chip);
  });
  statusPill.textContent = session.status || "WAITING";
  document.getElementById("lookupId").value = session.sessionId;
  document.getElementById("sessionId").value = session.sessionId;
}

document.getElementById("create-form").addEventListener("submit", async event => {
  event.preventDefault();
  const host = document.getElementById("host").value.trim();
  const maxPlayers = Number(document.getElementById("maxPlayers").value);
  try {
    showMessage("Creating your session…");
    const result = await api("/sessions", {method:"POST", body:JSON.stringify({host,maxPlayers})});
    renderSession(result.session);
    showMessage(`Session created. Share this ID: ${result.session.sessionId}`);
  } catch (error) { showMessage(error.message, true); }
});

document.getElementById("join-form").addEventListener("submit", async event => {
  event.preventDefault();
  const sessionId = document.getElementById("sessionId").value.trim();
  const playerName = document.getElementById("playerName").value.trim();
  try {
    showMessage("Joining session…");
    const result = await api("/sessions/join", {method:"POST", body:JSON.stringify({sessionId,playerName})});
    renderSession(result.session);
    showMessage(result.message || "Joined session successfully.");
  } catch (error) { showMessage(error.message, true); }
});

document.getElementById("lookup-form").addEventListener("submit", async event => {
  event.preventDefault();
  const id = document.getElementById("lookupId").value.trim();
  try {
    showMessage("Loading session…");
    const result = await api(`/sessions/${encodeURIComponent(id)}`);
    renderSession(result.session);
    showMessage("Session details refreshed.");
  } catch (error) { showMessage(error.message, true); }
});
