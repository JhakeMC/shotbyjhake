/* Booking page only: the request form and the availability calendar.
   Booked days come from bookings.json in this folder. Add a booking there
   (or set data-endpoint on the form in app.js to a form service that accepts
   JSON POSTs) and the day is blocked for everyone. */
(() => {
  const form = document.getElementById("bookingForm");
  if (!form) return;

  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pad = n => String(n).padStart(2, "0");
  const iso = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const pretty = d => {
    const t = new Date(d + "T00:00:00");
    return isNaN(t) ? d : t.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  };
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const KEY = "shotbyjhake:bookings";

  const now = new Date();
  const todayISO = iso(now);
  const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const cal = document.getElementById("cal");
  const calMonth = document.getElementById("calMonth");
  const dateField = document.getElementById("bk-date");
  const done = document.getElementById("bk-done");
  const formErr = document.getElementById("bk-form-err");
  const field = n => form.querySelector(`[name="${n}"]`);

  let shared = [];          /* dates booked in bookings.json */
  let booked = new Set();   /* every date that is taken, shared + this device */
  let view = new Date(now.getFullYear(), now.getMonth(), 1);
  let selected = "";

  /* Bookings made in this browser, so a request never looks open again here. */
  const mine = () => { try { const v = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(v) ? v : []; } catch { return []; } };
  const remember = b => { try { localStorage.setItem(KEY, JSON.stringify([...mine(), b])); } catch { /* storage off: email is the record */ } };
  const refresh = () => { booked = new Set([...shared, ...mine()].map(b => b.date).filter(Boolean)); };

  const setErr = (name, msg) => {
    const p = document.getElementById(`bk-${name}-err`), input = field(name);
    if (p) p.textContent = msg;
    if (input) msg ? input.setAttribute("aria-invalid", "true") : input.removeAttribute("aria-invalid");
  };

  const render = () => {
    const y = view.getFullYear(), m = view.getMonth();
    const first = new Date(y, m, 1).getDay(), days = new Date(y, m + 1, 0).getDate();
    let html = DAY_NAMES.map(d => `<div class="wd" aria-hidden="true">${d}</div>`).join("");
    for (let i = 0; i < first; i++) html += `<div class="pad" aria-hidden="true"></div>`;
    for (let d = 1; d <= days; d++) {
      const dt = new Date(y, m, d), key = iso(dt);
      const past = key < todayISO, taken = booked.has(key);
      const cls = ["d", past ? "past" : "", taken ? "booked" : "", key === todayISO ? "today" : "", key === selected ? "sel" : ""].filter(Boolean).join(" ");
      const label = `${MONTHS[m]} ${d}, ${y} — ${taken ? "booked" : past ? "past" : "open"}`;
      html += `<button type="button" class="${cls}" data-date="${key}"${past || taken ? " disabled" : ""} aria-label="${esc(label)}"${key === selected ? ' aria-pressed="true"' : ""}>${d}</button>`;
    }
    cal.innerHTML = html;
    calMonth.textContent = `${MONTHS[m]} ${y}`;
  };

  const showDone = (b, sent) => {
    const lines = [
      `Date: ${pretty(b.date)}`,
      `Shoot: ${b.type}`,
      `Name: ${b.name}`,
      `Email: ${b.email}`,
      b.phone ? `Phone: ${b.phone}` : "",
      b.location ? `Location: ${b.location}` : "",
      b.notes ? `Details: ${b.notes}` : ""
    ].filter(Boolean).join("\n");
    const mail = `mailto:${SITE.email}?subject=${encodeURIComponent("Booking request – " + pretty(b.date))}&body=${encodeURIComponent(lines)}`;
    done.hidden = false;
    done.innerHTML = `<div class="done">
      <h2>${sent ? "Request sent" : "Almost done"}</h2>
      <p>${sent
        ? `Thank you, ${esc(b.name)}. Your request for ${esc(pretty(b.date))} is in and I will confirm by email.`
        : `Your request for ${esc(pretty(b.date))} is saved here. Last step: send it to me so I can confirm it.`}</p>
      <div class="btns">${sent ? "" : `<a class="btn" href="${esc(mail)}">Send it by email</a>`}<a class="btn ghost" href="#bookingForm" id="bk-again">Book another date</a></div>
    </div>`;
    done.scrollIntoView({ block: "center", behavior: "smooth" });
  };

  /* Pick a day on the calendar */
  cal.addEventListener("click", e => {
    const b = e.target.closest("button[data-date]");
    if (!b || b.disabled) return;
    selected = b.dataset.date;
    dateField.value = selected;
    setErr("date", "");
    render();
  });

  document.getElementById("calPrev").addEventListener("click", () => {
    const p = new Date(view.getFullYear(), view.getMonth() - 1, 1);
    view = p < thisMonth ? thisMonth : p;
    render();
  });
  document.getElementById("calNext").addEventListener("click", () => {
    view = new Date(view.getFullYear(), view.getMonth() + 1, 1);
    render();
  });

  /* Typing a date in the form moves the calendar to that month */
  dateField.min = todayISO;
  dateField.addEventListener("change", () => {
    const v = dateField.value;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) return;
    selected = v;
    const t = new Date(Number(v.slice(0, 4)), Number(v.slice(5, 7)) - 1, 1);
    if (t >= thisMonth) view = t;
    render();
  });

  done.addEventListener("click", e => {
    if (!e.target.closest("#bk-again")) return;
    e.preventDefault();
    form.reset();
    selected = "";
    setErr("name", ""); setErr("email", ""); setErr("date", "");
    formErr.textContent = "";
    done.hidden = true; done.innerHTML = "";
    render();
    field("name").focus();
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    formErr.textContent = "";
    ["name", "email", "date"].forEach(n => setErr(n, ""));
    const val = n => String(field(n).value || "").trim();
    const data = { name: val("name"), email: val("email"), phone: val("phone"), date: val("date"), type: val("type") || "Portrait", location: val("location"), notes: val("notes") };

    if (!data.name) setErr("name", "Please add your name.");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) setErr("email", "Please add an email I can reply to.");
    if (!data.date) setErr("date", "Pick a date for the shoot.");
    else if (data.date < todayISO) setErr("date", "That date has already passed.");
    else if (booked.has(data.date)) setErr("date", "That day is already taken. Please pick another.");

    const bad = form.querySelector('[aria-invalid="true"]');
    if (bad) { formErr.textContent = "Please fix the fields marked in red."; bad.focus(); return; }

    const booking = { id: "bk-" + Date.now().toString(36), created: new Date().toISOString(), status: "requested", ...data };

    let sent = false;
    if (form.dataset.endpoint) {
      try {
        sent = (await fetch(form.dataset.endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(booking) })).ok;
      } catch { sent = false; }
    }

    remember(booking);
    refresh();
    selected = booking.date;
    render();
    showDone(booking, sent);
    if (window.sfx) window.sfx.chime();
  });

  fetch("bookings.json", { cache: "no-store" })
    .then(r => r.ok ? r.json() : [])
    .then(list => {
      shared = (Array.isArray(list) ? list : []).filter(b => b && b.date && b.status !== "cancelled").map(b => b.date);
      refresh();
      render();
    })
    .catch(() => { /* no file yet: everything shows as open */ });

  render();
})();
