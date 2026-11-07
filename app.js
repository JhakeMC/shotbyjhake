/* Builds every page from content.js. You normally never need to edit this file. */
(() => {
  const S = SITE, page = document.body.dataset.page;
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = i => typeof i === "string" ? { src: i, alt: "" } : i;
  const fmt = d => new Date(d + "T00:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  const newest = a => [...a].sort((x, y) => String(y.date).localeCompare(String(x.date)));
  const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const paras = t => [].concat(t || []).map(p => `<p>${esc(p)}</p>`).join("");
  const pic = (i, g, fallback) => { const { src, alt } = norm(i); return `<button class="ph" data-g="${g}" data-src="${esc(src)}" aria-label="View photo larger"><img src="${esc(src)}" alt="${esc(alt || fallback || S.brand + " photo")}" loading="lazy"></button>`; };
  const gallery = (a, g, f) => (a && a.length) ? `<div class="masonry">${a.map(i => pic(i, g, f)).join("")}</div>` : "";
  const cover = it => norm((it.images && it.images[0]) || (it.sections && it.sections[0] && it.sections[0].images[0]) || "");
  const tel = S.phone.replace(/^0/, "+63");

  const pages = [["home", "Home", "index.html"], ["about", "About", "about.html"], ["projects", "Projects", "projects.html"], ["events", "Events", "events.html"]];
  const nav = () => `<header class="nav"><div class="wrap"><a class="brand" href="index.html">${esc(S.brand)}</a><nav aria-label="Main"><ul>${pages.map(([k, l, h]) => `<li><a href="${h}"${k === page ? ' aria-current="page"' : ""}>${l}</a></li>`).join("")}</ul></nav></div></header>`;

  const footer = () => `<footer class="foot"><div class="wrap">
    <h2>Need a photographer?</h2>
    <a class="mail" href="mailto:${esc(S.email)}">${esc(S.email)}</a>
    <p class="meta"><a href="tel:${esc(tel)}">${esc(S.phone)}</a></p>
    <div class="btns"><a class="btn" href="${esc(S.instagram.url)}" target="_blank" rel="noopener">Instagram @${esc(S.instagram.handle)}</a><a class="btn alt" href="${esc(S.facebook)}" target="_blank" rel="noopener">Facebook</a></div>
    <small>© ${new Date().getFullYear()} ${esc(S.brand)}. ${esc(S.tagline)}</small></div></footer>`;

  const home = () => {
    const lp = newest(S.projects)[0], le = newest(S.events)[0];
    const feat = (it, kind, href, cls) => it ? `<a class="feat ${cls}" href="${href}#${slug(it.title)}"><img src="${esc(cover(it).src)}" alt="" loading="lazy"><div><small>Latest ${kind}, ${fmt(it.date)}</small><h3>${esc(it.title)}</h3><p>${esc(it.subtitle || "")}</p></div></a>` : "";
    const run = [...S.roles, ...S.roles].map(r => `<span>${esc(r)}</span>`).join("");
    return `<section class="hero"><div class="wrap">
      <div><h1>${esc(S.name)}</h1><p class="lede">${esc(S.tagline)}</p>
      <div class="roles">${S.roles.map(r => `<span>${esc(r)}</span>`).join("")}</div>
      <div class="btns"><a class="btn" href="projects.html">See projects</a><a class="btn alt" href="events.html">See events</a>${S.midnightSuite ? `<a class="btn ghost" href="${esc(S.midnightSuite)}" target="_blank" rel="noopener">The Midnight Suite</a>` : ""}</div></div>
      <div class="collage" aria-hidden="true">${S.hero.slice(0, 3).map((s, i) => `<img class="c${i}" src="${esc(norm(s).src)}" alt="">`).join("")}</div>
    </div></section>
    <div class="marquee" aria-hidden="true"><div>${run}${run}</div></div>
    <section class="sec"><div class="wrap"><h2>Highlights</h2>${gallery(S.highlights, "hl")}</div></section>
    <section class="sec latest"><div class="wrap"><h2>Latest work</h2><div class="feats">${feat(lp, "project", "projects.html", "p")}${feat(le, "event", "events.html", "e")}</div></div></section>`;
  };

  const about = () => {
    const A = S.about;
    return `<section class="aboutTop"><div class="wrap about"><div>${pic(A.photo, "ab", S.name)}</div><div><h1>About me</h1><h2 class="h-sm">${esc(A.heading || "")}</h2>${paras(A.bio)}</div></div></section>
    <section class="wrap two"><div><h2>Experience</h2><ol class="tl">${newest(A.experience).map(e => `<li><time>${fmt(e.date)}</time><strong>${esc(e.title)}</strong><span>${esc(e.role || "")}</span></li>`).join("")}</ol></div>
    <div><h2>Education</h2><ol class="tl">${A.education.map(e => `<li><time>${esc(e.years)}</time><strong>${esc(e.school)}</strong><span>${esc(e.note || "")}</span></li>`).join("")}</ol></div></section>`;
  };

  const cycles = { projects: ["mint", "pink", "butter", "tomato"], events: ["pink", "mint", "tomato", "violet"] };
  const stories = kind => {
    const list = newest(S[kind]), c = cycles[kind];
    return `<section class="phead"><div class="wrap"><h1>${kind === "projects" ? "Projects" : "Events"}</h1><p>${esc(S.intro[kind] || "")}</p></div></section>` +
      list.map((it, i) => { const g = kind + i;
        return `<section class="story b-${c[i % c.length]}" id="${slug(it.title)}"><div class="wrap">
        <time>${fmt(it.date)}</time><h2>${esc(it.title)}</h2>${it.subtitle ? `<p class="sub">${esc(it.subtitle)}</p>` : ""}
        <div class="body">${paras(it.text)}</div>${gallery(it.images, g, it.title)}
        ${(it.sections || []).map(s => `<div class="part"><h3>${esc(s.title)}</h3><div class="body">${paras(s.text)}</div>${gallery(s.images, g, s.title)}</div>`).join("")}
        ${it.link ? `<div class="btns"><a class="btn ghost" href="${esc(it.link)}" target="_blank" rel="noopener">${esc(it.linkLabel || "View more")}</a></div>` : ""}
        </div></section>`; }).join("");
  };

  document.getElementById("root").innerHTML = nav() + `<main>${{ home, about, projects: () => stories("projects"), events: () => stories("events") }[page]()}</main>` + footer();

  /* Photo viewer */
  const lb = document.createElement("div");
  lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-label", "Photo viewer");
  lb.innerHTML = '<button class="x" aria-label="Close">✕</button><button class="p" aria-label="Previous photo">‹</button><img alt=""><button class="n" aria-label="Next photo">›</button>';
  document.body.append(lb);
  let set = [], cur = 0;
  const show = n => { cur = (n + set.length) % set.length; lb.querySelector("img").src = set[cur].dataset.src; };
  const close = () => lb.classList.remove("on");
  document.addEventListener("click", e => {
    const b = e.target.closest(".ph");
    if (b) { set = [...document.querySelectorAll(`.ph[data-g="${b.dataset.g}"]`)]; show(set.indexOf(b)); lb.classList.add("on"); lb.querySelector(".x").focus(); return; }
    if (e.target.closest(".lb .x") || e.target === lb) close();
    if (e.target.closest(".lb .p")) show(cur - 1);
    if (e.target.closest(".lb .n")) show(cur + 1);
  });
  document.addEventListener("keydown", e => {
    if (!lb.classList.contains("on")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(cur - 1);
    if (e.key === "ArrowRight") show(cur + 1);
  });
  if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) setTimeout(() => t.scrollIntoView(), 50); }
})();
