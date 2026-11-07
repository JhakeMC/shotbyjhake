/* Builds every page from content.js. You normally never need to edit this file. */
(() => {
  const S = SITE, page = document.body.dataset.page;
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = i => typeof i === "string" ? { src: i, alt: "" } : i;
  const fmt = d => { const t = new Date(d + "T00:00:00"); return isNaN(t) ? esc(d || "") : t.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }); };
  const newest = a => [...(a || [])].sort((x, y) => String(y.date).localeCompare(String(x.date)));
  const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const paras = t => [].concat(t || []).map(p => `<p>${esc(p)}</p>`).join("");
  const href = u => /^(https?:|mailto:|tel:|#)/.test(u) || u.includes(".html") ? u : u;
  const pic = (i, g, fallback) => { const { src, alt } = norm(i); return `<button class="ph" data-g="${g}" data-src="${esc(src)}" aria-label="View photo larger"><img src="${esc(src)}" alt="${esc(alt || fallback || S.brand + " photo")}" loading="lazy" decoding="async" onerror="this.closest('.ph').hidden=true"></button>`; };
  const gallery = (a, g, f) => (a && a.length) ? `<div class="masonry">${a.map(i => pic(i, g, f)).join("")}</div>` : "";
  const cover = it => norm((it.images && it.images[0]) || (it.sections && (it.sections.find(s => s.images && s.images[0]) || {}).images?.[0]) || "");
  const tel = String(S.phone || "").replace(/^0/, "+63");
  const ext = u => /^https?:/.test(u) ? ' target="_blank" rel="noopener"' : "";
  const btn = b => `<a class="btn ${{ mint: "alt", light: "ghost" }[b.style] || ""}" href="${esc(href(b.url))}"${ext(b.url)}>${esc(b.label)}</a>`;
  const params = new URLSearchParams(location.search), cslug = params.get("p");
  const custom = (S.pages || []).filter(p => p.nav !== false);

  const pages = [["home", "Home", "index.html"], ["about", "About", "about.html"], ["projects", "Projects", "projects.html"], ["events", "Events", "events.html"]];
  const nav = () => `<header class="nav"><div class="wrap"><a class="brand" href="index.html">${S.logo ? `<img class="logo" src="${esc(S.logo)}" alt="${esc(S.brand)}">` : esc(S.brand)}</a><nav aria-label="Main"><ul>${
    pages.map(([k, l, h]) => `<li><a href="${h}"${k === page ? ' aria-current="page"' : ""}>${l}</a></li>`).join("") +
    custom.map(p => `<li><a href="page.html?p=${esc(p.slug)}"${page === "page" && cslug === p.slug ? ' aria-current="page"' : ""}>${esc(p.title)}</a></li>`).join("")}</ul></nav></div></header>`;

  const footer = () => `<footer class="foot"><div class="wrap">
    <h2>Need a photographer?</h2>
    <a class="mail" href="mailto:${esc(S.email)}">${esc(S.email)}</a>
    <p class="meta"><a href="tel:${esc(tel)}">${esc(S.phone)}</a></p>
    <div class="btns"><a class="btn" href="${esc(S.instagram.url)}" target="_blank" rel="noopener"><img src="images/icon-instagram.png" alt="" width="22" height="22">Instagram @${esc(S.instagram.handle)}</a><a class="btn alt" href="${esc(S.facebook)}" target="_blank" rel="noopener"><img src="images/icon-facebook.png" alt="" width="22" height="22">Facebook</a></div>
    <small>© ${new Date().getFullYear()} ${esc(S.brand)}. ${esc(S.tagline)}</small></div></footer>`;

  const home = () => {
    const lp = newest(S.projects)[0], le = newest(S.events)[0];
    const feat = (it, kind, h, cls) => it ? `<a class="feat ${cls}" href="${h}#${slug(it.title)}">${cover(it).src ? `<img src="${esc(cover(it).src)}" alt="" loading="lazy" onerror="this.remove()">` : ""}<div><small>Latest ${kind}, ${fmt(it.date)}</small><h3>${esc(it.title)}</h3><p>${esc(it.subtitle || "")}</p></div></a>` : "";
    const run = [...S.roles, ...S.roles].map(r => `<span>${esc(r)}</span>`).join("");
    const hero = (S.hero && S.hero.length ? S.hero : S.highlights || []).slice(0, 3);
    return `<section class="hero"><div class="wrap">
      <div><h1>${esc(S.name)}</h1><p class="lede">${esc(S.tagline)}</p>
      <div class="roles">${S.roles.map(r => `<span>${esc(r)}</span>`).join("")}</div>
      <div class="btns">${(S.heroButtons || []).map(btn).join("")}</div></div>
      ${hero.length ? `<div class="collage${hero.length < 2 ? " solo" : ""}" aria-hidden="true">${hero.map((s, i) => `<img class="c${i}" src="${esc(norm(s).src)}" alt="" onerror="this.remove()">`).join("")}</div>` : ""}
    </div></section>
    <div class="marquee" aria-hidden="true"><div>${run}${run}</div></div>
    <section class="sec"><div class="wrap"><h2>Highlights</h2>${gallery(S.highlights, "hl")}</div></section>
    ${lp || le ? `<section class="sec latest"><div class="wrap"><h2>Latest work</h2><div class="feats">${feat(lp, "project", "projects.html", "p")}${feat(le, "event", "events.html", "e")}</div></div></section>` : ""}`;
  };

  const about = () => {
    const A = S.about, tl = (a, k, t, s) => (a || []).map(e => `<li><time>${k(e)}</time><strong>${esc(e[t])}</strong><span>${esc(e[s] || "")}</span></li>`).join("");
    return `<section class="aboutTop"><div class="wrap about"><div>${A.photo ? `<img class="avatar" src="${esc(A.photo)}" alt="${esc(S.name)}">` : ""}</div><div><h1>About me</h1><h2 class="h-sm">${esc(A.heading || "")}</h2>${paras(A.bio)}</div></div></section>
    <section class="wrap two"><div><h2>Experience</h2><ol class="tl">${tl(newest(A.experience), e => fmt(e.date), "title", "role")}</ol></div>
    <div><h2>Education</h2><ol class="tl">${tl(A.education, e => esc(e.years), "school", "note")}</ol></div></section>`;
  };

  const cycles = { projects: ["mint", "pink", "butter", "tomato"], events: ["pink", "mint", "tomato", "violet"] };
  const stories = kind => {
    const list = newest(S[kind]), c = cycles[kind];
    return `<section class="phead"><div class="wrap"><h1>${kind === "projects" ? "Projects" : "Events"}</h1><p>${esc((S.intro || {})[kind] || "")}</p></div></section>` +
      list.map((it, i) => { const g = kind + i;
        return `<section class="story b-${c[i % c.length]}" id="${slug(it.title)}"><div class="wrap">
        <time>${fmt(it.date)}</time><h2>${esc(it.title)}</h2>${it.subtitle ? `<p class="sub">${esc(it.subtitle)}</p>` : ""}
        <div class="body">${paras(it.text)}</div>${gallery(it.images, g, it.title)}
        ${(it.sections || []).map(s => `<div class="part"><h3>${esc(s.title)}</h3><div class="body">${paras(s.text)}</div>${gallery(s.images, g, s.title)}</div>`).join("")}
        ${it.link ? `<div class="btns"><a class="btn ghost" href="${esc(href(it.link))}"${ext(it.link)}>${esc(it.linkLabel || "View more")}</a></div>` : ""}
        </div></section>`; }).join("");
  };

  const custompage = () => {
    const P = (S.pages || []).find(p => p.slug === cslug);
    if (!P) return `<section class="phead"><div class="wrap"><h1>Page not found</h1><p><a href="index.html">Back to home</a></p></div></section>`;
    document.title = P.title + " – " + S.brand;
    const block = (b, i) => ({ heading: () => `<h2>${esc(b.text)}</h2>`, text: () => `<div class="body">${paras(b.text)}</div>`, photos: () => gallery(b.images, "pg" + i, P.title), button: () => `<div class="btns">${btn({ label: b.label || "Open", url: b.url || "#" })}</div>` }[b.type] || (() => ""))();
    return `<section class="phead"><div class="wrap"><h1>${esc(P.title)}</h1>${P.intro ? `<p>${esc(P.intro)}</p>` : ""}</div></section><section class="sec"><div class="wrap blocks">${(P.blocks || []).map(block).join("")}</div></section>`;
  };

  document.getElementById("root").innerHTML = nav() + `<main>${{ home, about, projects: () => stories("projects"), events: () => stories("events"), page: custompage }[page]()}</main>` + footer();

  /* Photo viewer: click or tap a photo; arrows, keys or swipe to move */
  const lb = document.createElement("div");
  lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-label", "Photo viewer");
  lb.innerHTML = '<button class="x" aria-label="Close">✕</button><button class="p" aria-label="Previous photo">‹</button><img alt=""><button class="n" aria-label="Next photo">›</button>';
  document.body.append(lb);
  let set = [], cur = 0, x0 = null;
  const show = n => { cur = (n + set.length) % set.length; lb.querySelector("img").src = set[cur].dataset.src; };
  const close = () => { lb.classList.remove("on"); document.body.classList.remove("noscroll"); };
  document.addEventListener("click", e => {
    const b = e.target.closest(".ph");
    if (b) { set = [...document.querySelectorAll(`.ph[data-g="${b.dataset.g}"]:not([hidden])`)]; show(set.indexOf(b)); lb.classList.add("on"); document.body.classList.add("noscroll"); lb.querySelector(".x").focus(); return; }
    if (e.target.closest(".lb .x") || e.target === lb) close();
    if (e.target.closest(".lb .p")) show(cur - 1);
    if (e.target.closest(".lb .n")) show(cur + 1);
  });
  lb.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1)); });
  document.addEventListener("keydown", e => {
    if (!lb.classList.contains("on")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(cur - 1);
    if (e.key === "ArrowRight") show(cur + 1);
  });
  if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) setTimeout(() => t.scrollIntoView(), 50); }
})();
