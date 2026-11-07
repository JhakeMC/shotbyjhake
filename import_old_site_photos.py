"""
Downloads every photo from your old Google Site into <website>/images/old-site/
and puts them into content.js (home highlights, projects, events).

Run it once: double-click it, or run  python import_old_site_photos.py
Optional: python import_old_site_photos.py "C:\\path\\to\\website"
Needs only Python. Safe to run again; your content.js is backed up first.
"""
import html, json, os, re, shutil, sys, urllib.request

DEFAULT_ROOT = r"C:\Users\Mary Grace\Documents\GitHub\shotbyjhake"
BASE = "https://sites.google.com/view/jhakedoesphotography/"
PAGES = ["home", "about", "projects", "events"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
# Start of the first photo of each group, used to split the Projects/Events pages correctly.
ANCHORS = {
    "Aliana@XVIII": "AMxu72uwPbBBkWVNrUkuyfaHBrKMwafh6zY06TJ1",
    "Ellen@XVIII": "AMxu72uTWhwR18RUxQ4_7b_0Q1vf4G4AiCvPkbW-",
    "event": "AMxu72sXtO1mNVwM0hG0dQSWvggeHfkKNZsEEW3o",
    "part1": "AMxu72tYvaBcNFYiK9U4nof2MLLEbND7YfNfkeTy",
}
IMG_RE = re.compile(r"https://(?:sites\.google\.com/sitesv-images-rt|lh\d\.googleusercontent\.com/sitesv)/([A-Za-z0-9_\-]{40,})")


def fetch(url, referer=BASE):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


def extract(page_html):
    """Photo ids in the order they appear on the page (no duplicates)."""
    t = html.unescape(page_html).replace("\\u003d", "=").replace("\\u0026", "&").replace("\\/", "/")
    seen, out = set(), []
    for m in IMG_RE.finditer(t):
        tok = m.group(1)
        if tok not in seen:
            seen.add(tok)
            out.append((tok, m.group(0)))
    return out


def host_prefix(full):
    return full.rsplit("/", 1)[0] + "/"


def download(prefix, tok, dest_base):
    for suffix in ("=w2000", "=s0", ""):
        try:
            data, ctype = fetch(prefix + tok + suffix, "https://sites.google.com/")
        except Exception:
            continue
        if ctype.startswith("image/") and len(data) > 2000:
            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(ctype.split(";")[0], ".jpg")
            with open(dest_base + ext, "wb") as f:
                f.write(data)
            return dest_base + ext
    return None


def split_by_anchors(files, tokens, starts):
    """starts: {name: token prefix}. Returns {name: [files...]} using page order."""
    idx = {}
    for name, pre in starts.items():
        for i, tok in enumerate(tokens):
            if tok.startswith(pre):
                idx[name] = i
                break
    order = sorted(idx.items(), key=lambda kv: kv[1])
    out = {}
    for n, (name, i) in enumerate(order):
        j = order[n + 1][1] if n + 1 < len(order) else len(files)
        out[name] = [f for f in files[i:j] if f]
    return out


def load_site(root):
    t = open(os.path.join(root, "content.js"), encoding="utf-8").read()
    i = t.index("const SITE")
    return json.loads(t[t.index("{", i): t.rindex("}") + 1]), t[:i]


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT
    if not os.path.exists(os.path.join(root, "content.js")):
        root = input("Website folder (the one with content.js): ").strip().strip('"')
    site, header = load_site(root)
    outdir = os.path.join(root, "images", "old-site")
    os.makedirs(outdir, exist_ok=True)

    found = {}
    for p in PAGES:
        print("Reading", p, "page...")
        try:
            found[p] = extract(fetch(BASE + p)[0].decode("utf-8", "replace"))
        except Exception as e:
            print("  Could not open the page:", e)
            found[p] = []
        print("  photos found:", len(found[p]))
    if not any(found.values()):
        print("\nNo photos found. The old site may be unpublished or Google changed its page format.")
        input("Press Enter to close.")
        return

    # photos that appear on every page are the site's header/logo, not portfolio photos
    common = set.intersection(*[{t for t, _ in v} for v in found.values() if v]) if sum(1 for v in found.values() if v) > 1 else set()
    files = {}
    for p in PAGES:
        files[p] = []
        items = [(t, u) for t, u in found[p] if t not in common]
        for n, (tok, url) in enumerate(items, 1):
            base = os.path.join(outdir, "%s-%02d" % (p, n))
            existing = [f for f in os.listdir(outdir) if f.startswith(os.path.basename(base) + ".")]
            path = os.path.join(outdir, existing[0]) if existing else download(host_prefix(url), tok, base)
            print("  %s %d/%d %s" % (p, n, len(items), "ok" if path else "FAILED"))
            files[p].append(path)
        files[p + "_tokens"] = [t for t, _ in items]

    rel = lambda f: "images/old-site/" + os.path.basename(f)
    ok = lambda lst: [rel(f) for f in lst if f]

    home = ok(files["home"])
    if home:
        keep = [h for h in site.get("highlights", []) if not h.startswith("images/old-site/")]
        site["highlights"] = keep + home
        site["hero"] = home[:3]

    pr = split_by_anchors(files["projects"], files["projects_tokens"], {k: ANCHORS[k] for k in ("Aliana@XVIII", "Ellen@XVIII")})
    for proj in site.get("projects", []):
        if proj["title"] in pr:
            proj["images"] = ok(pr[proj["title"]])
    ev = split_by_anchors(files["events"], files["events_tokens"], {k: ANCHORS[k] for k in ("event", "part1")})
    for e in site.get("events", []):
        if e["title"].startswith("Canon Wedding") and ev:
            e["images"] = ok(ev.get("event", []))
            if e.get("sections") and "part1" in ev:
                e["sections"][0]["images"] = ok(ev["part1"])
    if not pr or not ev:
        print("\nNote: could not split some Projects/Events photos automatically.")
        print("They are all saved in images/old-site/ and you can add them with the site editor.")

    shutil.copy(os.path.join(root, "content.js"), os.path.join(root, "content.backup.js"))
    with open(os.path.join(root, "content.js"), "w", encoding="utf-8") as f:
        f.write(header + "const SITE = " + json.dumps(site, indent=2, ensure_ascii=False) + ";\n")
    failed = sum(1 for p in PAGES for f in files[p] if not f)
    print("\nDone. %d photos saved in %s" % (sum(1 for p in PAGES for f in files[p] if f), outdir))
    if failed:
        print("%d photos could not be downloaded (Google may be blocking them)." % failed)
    print("Open the site editor or index.html to check the result.")
    input("Press Enter to close.")


if __name__ == "__main__":
    main()
