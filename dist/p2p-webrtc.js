// Pseudo-multijoueur (WebRTC P2P) : stream canvas + contrôle invité via DataChannel.
// Objectif: 100% Vercel (signaling via /api/rtc/* si Vercel KV configuré, sinon mode manuel).
(function () {
  const params = new URLSearchParams(window.location.search);

  const isJoinMode = params.get("p2p") === "join";
  const roomId = params.get("room") || "";
  const joinKey = params.get("key") || "";

  const STUN_SERVERS = [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "stun:stun1.l.google.com:19302" },
  ];

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const waitForIceGatheringComplete = (pc) =>
    new Promise((resolve) => {
      if (pc.iceGatheringState === "complete") return resolve();
      const onChange = () => {
        if (pc.iceGatheringState === "complete") {
          pc.removeEventListener("icegatheringstatechange", onChange);
          resolve();
        }
      };
      pc.addEventListener("icegatheringstatechange", onChange);
    });

  const api = {
    async createRoom() {
      const r = await fetch("/api/rtc/create", { method: "POST" });
      if (!r.ok) throw new Error("create-room failed");
      return await r.json();
    },
    async setOffer({ roomId, hostKey, offer }) {
      const r = await fetch("/api/rtc/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ roomId, hostKey, offer }),
      });
      if (!r.ok) throw new Error("set-offer failed");
      return await r.json();
    },
    async getOffer(roomId) {
      const r = await fetch(`/api/rtc/offer?roomId=${encodeURIComponent(roomId)}`, { cache: "no-store" });
      if (!r.ok) throw new Error("get-offer failed");
      return await r.json();
    },
    async setAnswer({ roomId, joinKey, answer }) {
      const r = await fetch("/api/rtc/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ roomId, joinKey, answer }),
      });
      if (!r.ok) throw new Error("set-answer failed");
      return await r.json();
    },
    async getAnswer(roomId) {
      const r = await fetch(`/api/rtc/answer?roomId=${encodeURIComponent(roomId)}`, { cache: "no-store" });
      if (!r.ok) throw new Error("get-answer failed");
      return await r.json();
    },
  };

  const ensureUi = () => {
    const startPanel = document.querySelector(".start-actions");
    if (!startPanel) return null;

    const container = document.createElement("div");
    container.style.display = "grid";
    container.style.gap = "10px";
    container.style.marginTop = "12px";
    container.style.maxWidth = "520px";

    const title = document.createElement("div");
    title.style.color = "rgba(255,255,255,0.85)";
    title.style.fontSize = "13px";
    title.style.letterSpacing = "0.02em";
    title.textContent = "Multijoueur (beta) — WebRTC P2P (stream + contrôle)";

    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.flexWrap = "wrap";
    row.style.gap = "10px";

    const hostBtn = document.createElement("button");
    hostBtn.type = "button";
    hostBtn.textContent = "Créer une salle";
    hostBtn.style.cursor = "pointer";
    hostBtn.style.border = "1px solid rgba(255,255,255,0.22)";
    hostBtn.style.background = "rgba(0,0,0,0.18)";
    hostBtn.style.color = "white";
    hostBtn.style.padding = "10px 12px";
    hostBtn.style.borderRadius = "12px";

    const joinInput = document.createElement("input");
    joinInput.type = "text";
    joinInput.placeholder = "Lien d’invitation (coller ici)";
    joinInput.style.flex = "1";
    joinInput.style.minWidth = "220px";

    const joinBtn = document.createElement("button");
    joinBtn.type = "button";
    joinBtn.textContent = "Rejoindre";
    joinBtn.style.cursor = "pointer";
    joinBtn.style.border = "1px solid rgba(255,255,255,0.22)";
    joinBtn.style.background = "rgba(0,0,0,0.18)";
    joinBtn.style.color = "white";
    joinBtn.style.padding = "10px 12px";
    joinBtn.style.borderRadius = "12px";

    const status = document.createElement("div");
    status.style.color = "rgba(255,255,255,0.70)";
    status.style.fontSize = "12px";
    status.style.lineHeight = "1.4";
    status.textContent = "Astuce: l’hôte lance le jeu normalement, puis partage le lien. L’invité n’a pas besoin de télécharger les assets.";

    const linkBox = document.createElement("textarea");
    linkBox.readOnly = true;
    linkBox.rows = 2;
    linkBox.placeholder = "Lien d’invitation…";
    linkBox.style.display = "none";
    linkBox.style.width = "100%";
    linkBox.style.background = "rgba(0,0,0,0.18)";
    linkBox.style.border = "1px solid rgba(255,255,255,0.18)";
    linkBox.style.color = "white";
    linkBox.style.padding = "10px 12px";
    linkBox.style.borderRadius = "12px";
    linkBox.style.resize = "vertical";

    row.appendChild(hostBtn);
    row.appendChild(joinInput);
    row.appendChild(joinBtn);

    container.appendChild(title);
    container.appendChild(row);
    container.appendChild(status);
    container.appendChild(linkBox);

    startPanel.appendChild(container);

    return { hostBtn, joinBtn, joinInput, status, linkBox };
  };

  const setStatus = (ui, text) => {
    if (!ui) return;
    ui.status.textContent = text;
  };

  const getEmulator = () => {
    const emulator = window.__revcGamepadEmulator;
    const idx = window.__revcGamepadIndex;
    if (!emulator || typeof idx !== "number") return null;
    return { emulator, idx };
  };

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

  const applyRemotePadStateToHost = (state) => {
    const emu = getEmulator();
    if (!emu) return;
    const { emulator, idx } = emu;

    // axes: 0..3 in [-1..1]
    if (Array.isArray(state.axes)) {
      for (let i = 0; i < Math.min(4, state.axes.length); i++) {
        const v = clamp(Number(state.axes[i] || 0), -1, 1);
        try {
          emulator.MoveAxis(idx, i, v);
        } catch {
          // ignore
        }
      }
    }

    // buttons: array of {pressed,value}
    if (Array.isArray(state.buttons)) {
      for (let i = 0; i < Math.min(16, state.buttons.length); i++) {
        const b = state.buttons[i] || {};
        const value = clamp(Number(b.value ?? (b.pressed ? 1 : 0)), 0, 1);
        try {
          emulator.PressButton(idx, i, value, Boolean(b.pressed));
        } catch {
          // ignore
        }
      }
    }
  };

  const buildKeyboardPad = () => {
    const down = new Set();
    window.addEventListener("keydown", (e) => down.add(e.code));
    window.addEventListener("keyup", (e) => down.delete(e.code));

    const tick = () => {
      // Left stick: WASD
      const x = (down.has("KeyD") ? 1 : 0) + (down.has("KeyA") ? -1 : 0);
      const y = (down.has("KeyS") ? 1 : 0) + (down.has("KeyW") ? -1 : 0);

      // Buttons (very approximate mapping)
      const btn = (pressed) => ({ pressed, value: pressed ? 1 : 0 });
      const buttons = new Array(16).fill(0).map(() => btn(false));
      buttons[0] = btn(down.has("Space")); // A
      buttons[1] = btn(down.has("KeyF")); // B
      buttons[2] = btn(down.has("KeyE")); // X
      buttons[3] = btn(down.has("KeyR")); // Y
      buttons[4] = btn(down.has("KeyQ")); // LB
      buttons[5] = btn(down.has("KeyV")); // RB
      buttons[8] = btn(down.has("Backspace")); // Back
      buttons[9] = btn(down.has("Enter")); // Start

      return { axes: [clamp(x, -1, 1), clamp(y, -1, 1), 0, 0], buttons };
    };

    return { tick };
  };

  const getFirstRealGamepad = () => {
    try {
      const pads = (navigator.getGamepads && navigator.getGamepads()) || [];
      for (const p of pads) if (p && p.connected) return p;
    } catch {
      // ignore
    }
    return null;
  };

  const encodeSdp = (desc) => JSON.stringify(desc);
  const decodeSdp = (raw) => JSON.parse(raw);

  async function runHost(ui) {
    setStatus(ui, "Création de la salle…");
    const created = await api.createRoom();
    const { roomId, hostKey, joinKey } = created;

    const inviteUrl = new URL(window.location.href);
    inviteUrl.searchParams.set("p2p", "join");
    inviteUrl.searchParams.set("room", roomId);
    inviteUrl.searchParams.set("key", joinKey);
    // évite de propager des params inutiles
    inviteUrl.searchParams.delete("custom_saves");
    inviteUrl.searchParams.delete("request_original_game");

    ui.linkBox.style.display = "block";
    ui.linkBox.value = inviteUrl.toString();

    setStatus(ui, "Création de l’offre WebRTC…");
    const pc = new RTCPeerConnection({ iceServers: STUN_SERVERS });

    // Video stream from canvas (host runs the game)
    const canvas = document.getElementById("canvas");
    if (!canvas || !canvas.captureStream) {
      setStatus(ui, "Canvas introuvable ou captureStream indisponible.");
      return;
    }
    const stream = canvas.captureStream(60);
    for (const track of stream.getTracks()) {
      pc.addTrack(track, stream);
    }

    const dc = pc.createDataChannel("input", { ordered: true });
    dc.addEventListener("message", (ev) => {
      try {
        const msg = JSON.parse(String(ev.data || ""));
        if (msg && msg.t === "pad") {
          applyRemotePadStateToHost(msg.s);
        }
      } catch {
        // ignore
      }
    });

    const offer = await pc.createOffer({ offerToReceiveVideo: true });
    await pc.setLocalDescription(offer);
    await waitForIceGatheringComplete(pc);

    await api.setOffer({ roomId, hostKey, offer: encodeSdp(pc.localDescription) });
    setStatus(ui, "Lien prêt. En attente de l’invité…");

    // poll answer
    for (;;) {
      await sleep(1200);
      let answerRes;
      try {
        answerRes = await api.getAnswer(roomId);
      } catch {
        continue;
      }
      if (answerRes && answerRes.answer) {
        await pc.setRemoteDescription(decodeSdp(answerRes.answer));
        setStatus(ui, "Connecté. (Contrôle invité actif)");
        break;
      }
    }
  }

  async function runJoin() {
    // Hide start UI; show a video element
    const startContainer = document.querySelector(".start-container");
    if (startContainer) startContainer.style.display = "none";
    const disclaimer = document.querySelector(".disclaimer");
    if (disclaimer) disclaimer.style.display = "none";
    const developedBy = document.querySelector(".developed-by");
    if (developedBy) developedBy.style.display = "none";
    const clickToPlay = document.querySelector(".click-to-play");
    if (clickToPlay) clickToPlay.style.display = "none";

    const video = document.createElement("video");
    video.autoplay = true;
    video.playsInline = true;
    video.muted = true; // évite le blocage autoplay; l'audio du jeu n'est pas capturé dans ce POC
    video.style.position = "fixed";
    video.style.inset = "0";
    video.style.width = "100%";
    video.style.height = "100%";
    video.style.objectFit = "contain";
    video.style.background = "black";
    video.style.zIndex = "99999";
    document.body.appendChild(video);

    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.left = "12px";
    overlay.style.right = "12px";
    overlay.style.bottom = "12px";
    overlay.style.zIndex = "100000";
    overlay.style.display = "flex";
    overlay.style.gap = "10px";
    overlay.style.alignItems = "center";

    const btn = document.createElement("button");
    btn.textContent = "Activer le contrôle";
    btn.style.cursor = "pointer";
    btn.style.border = "1px solid rgba(255,255,255,0.22)";
    btn.style.background = "rgba(0,0,0,0.45)";
    btn.style.color = "white";
    btn.style.padding = "10px 12px";
    btn.style.borderRadius = "12px";

    const info = document.createElement("div");
    info.style.color = "rgba(255,255,255,0.85)";
    info.style.fontSize = "12px";
    info.style.flex = "1";
    info.textContent = "Connexion…";

    overlay.appendChild(btn);
    overlay.appendChild(info);
    document.body.appendChild(overlay);

    const pc = new RTCPeerConnection({ iceServers: STUN_SERVERS });
    pc.addEventListener("track", (ev) => {
      if (ev.streams && ev.streams[0]) {
        video.srcObject = ev.streams[0];
      } else {
        const ms = new MediaStream([ev.track]);
        video.srcObject = ms;
      }
    });

    let dataChannel = null;
    pc.addEventListener("datachannel", (ev) => {
      dataChannel = ev.channel;
      dataChannel.addEventListener("open", () => {
        info.textContent = "Connecté. Cliquez “Activer le contrôle”.";
      });
    });

    // Wait for offer to exist
    info.textContent = "Attente de l’offre…";
    for (;;) {
      try {
        const offerRes = await api.getOffer(roomId);
        if (offerRes && offerRes.offer) {
          await pc.setRemoteDescription(decodeSdp(offerRes.offer));
          break;
        }
      } catch {
        // ignore
      }
      await sleep(1200);
    }

    info.textContent = "Création de la réponse…";
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    await waitForIceGatheringComplete(pc);
    await api.setAnswer({ roomId, joinKey, answer: encodeSdp(pc.localDescription) });

    info.textContent = "Connecté (vidéo).";

    const kb = buildKeyboardPad();

    let isControlEnabled = false;
    btn.addEventListener("click", async () => {
      isControlEnabled = !isControlEnabled;
      btn.textContent = isControlEnabled ? "Désactiver le contrôle" : "Activer le contrôle";
      info.textContent = isControlEnabled
        ? "Contrôle actif (WASD + Space/F/E/R)."
        : "Contrôle désactivé.";
      if (isControlEnabled) {
        try {
          await video.requestFullscreen?.();
        } catch {
          // ignore
        }
      }
    });

    // Send input state
    for (;;) {
      await sleep(50);
      if (!isControlEnabled) continue;
      if (!dataChannel || dataChannel.readyState !== "open") continue;

      const gp = getFirstRealGamepad();
      let payload;
      if (gp) {
        payload = {
          axes: [gp.axes?.[0] ?? 0, gp.axes?.[1] ?? 0, gp.axes?.[2] ?? 0, gp.axes?.[3] ?? 0],
          buttons: (gp.buttons || []).slice(0, 16).map((b) => ({
            pressed: Boolean(b && b.pressed),
            value: clamp(Number(b && b.value ? b.value : b && b.pressed ? 1 : 0), 0, 1),
          })),
        };
      } else {
        payload = kb.tick();
      }

      try {
        dataChannel.send(JSON.stringify({ t: "pad", s: payload }));
      } catch {
        // ignore
      }
    }
  }

  async function main() {
    // Join mode starts immediately
    if (isJoinMode) {
      if (!roomId || !joinKey) return;
      try {
        await runJoin();
      } catch (e) {
        console.error(e);
      }
      return;
    }

    const ui = ensureUi();
    if (!ui) return;

    ui.joinBtn.addEventListener("click", () => {
      const raw = ui.joinInput.value.trim();
      if (!raw) return;
      try {
        const u = new URL(raw);
        window.location.href = u.toString();
      } catch {
        // ignore
      }
    });

    ui.hostBtn.addEventListener("click", async () => {
      ui.hostBtn.disabled = true;
      try {
        await runHost(ui);
      } catch (e) {
        console.error(e);
        setStatus(ui, "Erreur: signaling indisponible. Configure Vercel KV ou utilise un mode manuel.");
      }
    });
  }

  window.addEventListener("DOMContentLoaded", () => {
    main().catch((e) => console.error(e));
  });
})();

