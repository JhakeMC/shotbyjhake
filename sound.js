/* Small interaction sounds. Synthesised in the browser, so there is nothing extra to download. */
(() => {
  let ctx = null;
  const quiet = () => { try { return localStorage.getItem("shotbyjhake:sound") === "off"; } catch { return false; } };
  const audio = () => {
    if (ctx) return ctx;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    try { ctx = new AC(); } catch { return null; }
    return ctx;
  };
  const note = (freq, at, dur, volume, type) => {
    const c = audio();
    if (!c || quiet()) return;
    if (c.state === "suspended") c.resume().catch(() => {});
    const t = c.currentTime + at;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(volume, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(c.destination);
    o.start(t);
    o.stop(t + dur + 0.03);
  };
  window.sfx = {
    tick: () => note(1240, 0, 0.06, 0.03, "triangle"),
    pop: () => { note(660, 0, 0.1, 0.035, "sine"); note(990, 0.045, 0.12, 0.028, "sine"); },
    chime: () => { note(784, 0, 0.16, 0.035, "sine"); note(988, 0.1, 0.18, 0.03, "sine"); note(1319, 0.2, 0.26, 0.026, "sine"); }
  };

  /* One place for every click, so each control sounds the same on every page. */
  document.addEventListener("click", e => {
    const day = e.target.closest(".cal .d");
    if (day) { if (!day.disabled) window.sfx.tick(); return; }
    if (e.target.closest(".lb .x") || (e.target.classList && e.target.classList.contains("lb"))) { window.sfx.tick(); return; }
    if (e.target.closest(".lb")) { window.sfx.pop(); return; }
    if (e.target.closest(".ph")) { window.sfx.pop(); return; }
    if (e.target.closest("a, button")) window.sfx.tick();
  }, true);

  /* Browsers only allow audio after a gesture; warm it up on the first touch. */
  const warm = () => { const c = audio(); if (c && c.state === "suspended") c.resume().catch(() => {}); };
  document.addEventListener("pointerdown", warm, { once: true, passive: true });
})();
