#!/usr/bin/env python3
"""
Jhake Site Editor: edit the website without an IDE.

Double-click to open (on Windows, keep the .pyw ending so no console appears).

What it does
    * Pulls the latest commit from GitHub every time it opens, so you always
      start from what is live.
    * Edits content.js, bookings.json and the photos in images/highlights.
    * Every photo list is a board: drag photos around to arrange them, and drop
      photos straight from Explorer (or Finder) onto a board to add them.
    * Publish saves, commits and pushes to GitHub, which is what puts the
      change on the live site.

Needs Python 3.9+. Two optional extras make it nicer, and the editor tells you
if they are missing:
    pip install pillow tkinterdnd2

Pillow gives photo previews and paints the frosted glass, and tkinterdnd2 makes
dropping files from Explorer work. Without tkinterdnd2 you can still add photos
with the "Add photos" button.

Keep ui_glass.py next to this file: it holds the window's glass look, copied
from the website's style.css.
"""
import datetime, functools, json, os, re, shutil, subprocess, sys, threading, traceback, webbrowser
import tkinter as tk
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    from PIL import Image, ImageOps
except Exception:
    Image = ImageOps = None
try:
    from PIL import ImageTk
except Exception:
    ImageTk = None
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    DND_FILES, TkinterDnD, HAS_DND = None, None, False

DEFAULT_ROOT = r"C:\Users\Mary Grace\Documents\GitHub\shotbyjhake"
SITE_URL = "https://jhakemc.github.io/shotbyjhake/"

# The window's colours and its frosted glass live in ui_glass.py, which copies
# the recipe from the website's style.css. Keep the two files side by side.
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.path.dirname(os.path.abspath(sys.argv[0] or os.getcwd()))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
try:
    from ui_glass import Backdrop, BG, CARD, INK, MUTED, ACC, ACC_D, GO, GO_D, LINE, SOFT
except ImportError:
    Backdrop = None          # no ui_glass.py: the editor still runs, plain and pale
    BG, CARD, INK, MUTED = "#fbeef9", "#fafafe", "#2b1646", "#6a5784"
    ACC, ACC_D, GO, GO_D = "#7c3aed", "#6d28d9", "#12a150", "#0d8442"
    LINE, SOFT = "#e8dff8", "#f3ecfe"

if Backdrop is None:
    class Backdrop(tk.Canvas):
        """Fallback: the window keeps a flat pastel background."""

        def __init__(s, parent):
            super().__init__(parent, bg=BG, highlightthickness=0, bd=0)
            s.panels = []

        def schedule(s, delay=150):
            pass
FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
TITLE = ("Segoe UI", 17, "bold")
SMALL = ("Segoe UI", 9)

ROOT_DIR = ""          # set once the folder is chosen; the widgets read it
THUMBS = {}            # cache of preview images


# --------------------------------------------------------------------------
# Small helpers for reading and writing the site data
# --------------------------------------------------------------------------
def get_path(o, key, default=None):
    for part in key.split("."):
        if not isinstance(o, dict) or part not in o:
            return default
        o = o[part]
    return o


def set_path(o, key, value):
    parts = key.split(".")
    for part in parts[:-1]:
        o = o.setdefault(part, {})
    o[parts[-1]] = value


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def abs_path(path):
    """A web path from content.js turned into a path on this computer."""
    path = str(path or "")
    if not path or path.startswith(("http://", "https://")):
        return ""
    return path if os.path.isabs(path) else os.path.join(ROOT_DIR, path.replace("/", os.sep))


def backup_dir():
    d = os.path.join(os.path.expanduser("~"), ".jhake-site-editor", "backups")
    os.makedirs(d, exist_ok=True)
    return d


HEADER = "/* This file is written by site_editor.pyw. You can also edit it by hand: keep everything " \
         "between the braces valid JSON (double quotes, no trailing commas). */\n"


def load_site(root):
    text = open(os.path.join(root, "content.js"), encoding="utf-8").read()
    start = text.index("const SITE")
    return json.loads(text[text.index("{", start): text.rindex("}") + 1])


def save_site(root, data):
    """Write content.js and keep a dated copy of the old one outside the site folder."""
    path = os.path.join(root, "content.js")
    if os.path.exists(path):
        try:
            stamp = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True, timeout=20).stdout.strip() or "manual"
        except (OSError, subprocess.SubprocessError):
            stamp = "manual"
        try:
            shutil.copy(path, os.path.join(backup_dir(), "content-%s.js" % stamp))
        except OSError:
            pass
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEADER + "const SITE = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n")


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# --------------------------------------------------------------------------
# Photos
# --------------------------------------------------------------------------
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
IMG_TYPES = [("Photos", "*.jpg *.jpeg *.png *.webp *.gif *.avif"), ("All files", "*.*")]


def header_size(path):
    """Pixel size straight from the file header, no libraries needed."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
            if head[:2] != b"\xff\xd8":
                return 0, 0
            fh.seek(2)
            while True:
                if fh.read(1) != b"\xff":
                    if fh.tell() > 4_000_000:
                        return 0, 0
                    continue
                marker = fh.read(1)
                while marker == b"\xff":
                    marker = fh.read(1)
                if not marker:
                    return 0, 0
                code = marker[0]
                if code == 0x01 or 0xD0 <= code <= 0xD8:
                    continue
                if code in (0xD9, 0xDA):
                    return 0, 0
                length = int.from_bytes(fh.read(2), "big")
                if 0xC0 <= code <= 0xCF and code not in (0xC4, 0xC8, 0xCC):
                    data = fh.read(5)
                    return int.from_bytes(data[3:5], "big"), int.from_bytes(data[1:3], "big")
                fh.seek(length - 2, 1)
    except OSError:
        return 0, 0


def image_size(path):
    if not path or not os.path.exists(path):
        return 0, 0
    if Image:
        try:
            with Image.open(path) as im:
                return im.width, im.height
        except Exception:
            pass
    return header_size(path)


def thumb(path, box=124):
    """A preview for a tile, or None when Pillow is missing or the file is gone."""
    if not (Image and ImageTk):
        return None
    full = abs_path(path)
    if not full or not os.path.exists(full):
        return None
    try:
        key = (full, os.path.getmtime(full), box)
    except OSError:
        return None
    if key in THUMBS:
        return THUMBS[key]
    try:
        im = ImageOps.exif_transpose(Image.open(full))
        im.thumbnail((box, box))
        photo = ImageTk.PhotoImage(im)
    except Exception:
        return None
    if len(THUMBS) > 400:
        THUMBS.clear()
    THUMBS[key] = photo
    return photo


def add_images(paths, root, dest_dir):
    """Copy photos into <root>/<dest_dir> untouched, and return their web paths."""
    dest = os.path.join(root, dest_dir.replace("/", os.sep))
    os.makedirs(dest, exist_ok=True)
    out = []
    for src in paths:
        src = os.path.abspath(src)
        if not os.path.isfile(src) or os.path.splitext(src)[1].lower() not in IMG_EXTS:
            continue
        root_c = os.path.normcase(os.path.abspath(root)) + os.sep
        if os.path.normcase(src).startswith(root_c):
            out.append(os.path.relpath(src, root).replace("\\", "/"))
            continue
        stem = slugify(os.path.splitext(os.path.basename(src))[0]) or "photo"
        ext = os.path.splitext(src)[1].lower()
        target, n = None, 1
        while True:
            target = os.path.join(dest, stem + ("" if n == 1 else "-%d" % n) + ext)
            if not os.path.exists(target):
                break
            n += 1
        shutil.copy2(src, target)          # full quality, no resizing
        out.append(os.path.relpath(target, root).replace("\\", "/"))
    return out


# --------------------------------------------------------------------------
# Git: pull on start, push on publish
# --------------------------------------------------------------------------
def git(root, *args, timeout=180):
    try:
        done = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                              timeout=timeout, creationflags=0x08000000 if os.name == "nt" else 0)
        return done.returncode, ((done.stdout or "") + (done.stderr or "")).strip()
    except FileNotFoundError:
        return 127, "Git is not installed (or not on PATH)."
    except subprocess.TimeoutExpired:
        return 124, "Git took too long and was stopped."


def has_repo(root):
    return os.path.isdir(os.path.join(root, ".git"))


def is_clean(root):
    code, out = git(root, "status", "--porcelain")
    return code == 0 and not out.strip()


def sync_repo(root):
    """Fetch and fast-forward to origin. Returns (ok, message)."""
    if not has_repo(root):
        return False, "This folder is not a git repository, so nothing was pulled."
    before = git(root, "rev-parse", "--short", "HEAD")[1]
    code, out = git(root, "fetch", "--prune", "origin")
    if code != 0:
        return False, "Could not reach GitHub: " + (out or "no answer")[:300]
    code, out = git(root, "pull", "--ff-only")
    after = git(root, "rev-parse", "--short", "HEAD")[1]
    if code != 0:
        return False, ("the pull was skipped, so your files were left untouched: " + (out or "unknown reason")[:200])
    if before and after and before != after:
        return True, "Pulled the latest commit (%s → %s)." % (before, after)
    return True, "Already up to date (%s)." % (after or "?")


def branch_name(root):
    return git(root, "rev-parse", "--abbrev-ref", "HEAD")[1] or "main"


def last_author(root):
    name = git(root, "log", "-1", "--format=%an")[1]
    email = git(root, "log", "-1", "--format=%ae")[1]
    return name, email


def publish_repo(root, message):
    """Save, commit and push. Returns (ok, text) with every step listed."""
    if not has_repo(root):
        return False, "This folder is not a git repository. Use GitHub Desktop to push it once."
    steps = []

    def step(title, code, out):
        steps.append("%s: %s%s" % (title, "ok" if code == 0 else "FAILED", ("\n    " + out) if out else ""))
        return code

    code, out = git(root, "pull", "--ff-only")
    step("Refresh from GitHub", code, out)
    if code != 0:
        return False, "\n\n".join(steps) + "\n\nPull the latest commit first (open GitHub Desktop and pull), then publish again."

    step("Collect changes", *git(root, "add", "-A"))
    code, out = git(root, "commit", "-m", message)
    if code != 0 and "identity" in out.lower():
        name, email = last_author(root)
        if name and email:
            code, out = git(root, "-c", "user.name=" + name, "-c", "user.email=" + email, "commit", "-m", message)
    nothing = code != 0 and ("nothing to commit" in out.lower() or "no changes added" in out.lower())
    step("Commit", 0 if nothing else code, "Nothing new to commit." if nothing else out)
    if code != 0 and not nothing:
        return False, "\n\n".join(steps)

    code, out = git(root, "push", "origin", branch_name(root))
    step("Push to GitHub", code, out)
    if code != 0:
        return False, "\n\n".join(steps) + "\n\nThe site was not updated. GitHub Desktop can push with your saved sign-in."
    return True, "\n\n".join(steps) + "\n\nLive in about a minute: " + SITE_URL


# --------------------------------------------------------------------------
# Highlights: the folder, the order file the site reads, the manual override
# --------------------------------------------------------------------------
HL_FOLDER = "images/highlights"


def hl_dir(root):
    return os.path.join(root, *HL_FOLDER.split("/"))


def hl_files(root):
    d = hl_dir(root)
    if not os.path.isdir(d):
        return []
    return [f for f in sorted(os.listdir(d))
            if os.path.splitext(f)[1].lower() in IMG_EXTS and os.path.isfile(os.path.join(d, f))]


def hl_manifest(root):
    """The order the site shows: layout.json first, then anything new on top."""
    d = hl_dir(root)
    names = hl_files(root)
    manual = load_json(os.path.join(d, "layout.json"), {})
    order = manual.get("order") if isinstance(manual, dict) else manual
    shown, seen = [], set()
    for name in order if isinstance(order, list) else []:
        if isinstance(name, str) and name in names and name not in seen:
            shown.append(name)
            seen.add(name)
    for name in names:
        if name not in seen:
            shown.insert(0, name)     # a photo that is not in the arrangement yet goes on top
    return shown


def hl_write_manifest(root, order):
    d = hl_dir(root)
    os.makedirs(d, exist_ok=True)
    entries = []
    for name in order:
        width, height = image_size(os.path.join(d, name))
        entries.append({"file": name, "w": width, "h": height})
    save_json(os.path.join(d, "highlights.json"), entries)
    return entries


def hl_regenerate(root):
    """Let the repository script do it (it reads the dates); returns True when it ran."""
    script = os.path.join(root, ".github", "highlights_manifest.py")
    if not os.path.exists(script):
        return False
    try:
        done = subprocess.run([sys.executable, script], cwd=root, capture_output=True, text=True,
                              timeout=180, creationflags=0x08000000 if os.name == "nt" else 0)
        return done.returncode == 0
    except Exception:
        return False


# --------------------------------------------------------------------------
# Form fields for content.js
# --------------------------------------------------------------------------
class TextField:
    def __init__(s, parent, extra, obj=None):
        s.v = tk.StringVar()
        s.widget = ttk.Entry(parent, textvariable=s.v)

    def get(s):
        return s.v.get().strip()

    def set(s, v):
        s.v.set("" if v is None else str(v))


class LongField:
    paras = False

    def __init__(s, parent, extra, obj=None):
        s.widget = tk.Text(parent, height=extra[0] if extra else 5, wrap="word", font=FONT,
                           relief="flat", bd=1, undo=True, bg="#fdfbff", highlightthickness=1,
                           highlightbackground=LINE, highlightcolor=ACC, padx=8, pady=6)

    def get(s):
        text = s.widget.get("1.0", "end").strip()
        return [x.strip() for x in re.split(r"\n\s*\n", text) if x.strip()] if s.paras else text

    def set(s, v):
        if isinstance(v, list):
            v = "\n\n".join(v)
        s.widget.delete("1.0", "end")
        s.widget.insert("1.0", v or "")


class ParasField(LongField):
    paras = True


class CsvField(TextField):
    def get(s):
        return [x.strip() for x in s.v.get().split(",") if x.strip()]

    def set(s, v):
        s.v.set(", ".join(v or []))


class ChoiceField:
    def __init__(s, parent, extra, obj=None):
        s.v = tk.StringVar()
        s.widget = ttk.Combobox(parent, textvariable=s.v, values=extra[0], state="readonly", width=22)

    def get(s):
        return s.v.get()

    def set(s, v):
        s.v.set(v or "")


class BoolField:
    def __init__(s, parent, extra, obj=None):
        s.v = tk.BooleanVar(value=True)
        s.widget = ttk.Checkbutton(parent, variable=s.v, text="Yes")

    def get(s):
        return bool(s.v.get())

    def set(s, v):
        s.v.set(True if v is None else bool(v))


class ImageField:
    """One photo with a preview and a Browse button that accepts a drop too."""

    def __init__(s, parent, extra, obj=None):
        s.v = tk.StringVar()
        s.widget = ttk.Frame(parent)
        s.entry = ttk.Entry(s.widget, textvariable=s.v)
        s.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(s.widget, text="Choose photo", command=s.browse).pack(side="left", padx=(6, 0))
        s.preview = ttk.Label(s.widget)
        s.preview.pack(side="left", padx=(8, 0))
        s.v.trace_add("write", lambda *a: s.show())

    def browse(s):
        f = filedialog.askopenfilename(title="Choose a photo", initialdir=os.path.join(ROOT_DIR, "images"),
                                       filetypes=IMG_TYPES)
        if f:
            s.v.set(add_images([f], ROOT_DIR, "images/uploads")[0])

    def show(s):
        img = thumb(s.v.get(), 54)
        if img:
            s.preview.configure(image=img)
            s.preview.image = img
        else:
            s.preview.configure(image="", text="")

    def get(s):
        return s.v.get().strip()

    def set(s, v):
        s.v.set(v or "")


class PhotoBoard(ttk.Frame):
    """Photos as tiles you arrange by dragging. Also accepts dropped files."""

    def __init__(s, parent, items=None, rows=3, dest="images/uploads", on_change=None):
        super().__init__(parent)
        s.items = [str(i) for i in (items or [])]
        s.dest, s.on_change = dest, on_change
        s.sel, s._drag, s._hover = None, None, None
        s.tiles = []
        s._cols_cached = 0
        s.columnconfigure(0, weight=1)
        s.canvas = tk.Canvas(s, bg=CARD, highlightthickness=0, height=132 * rows + 8)
        bar = ttk.Scrollbar(s, orient="vertical", command=s.canvas.yview)
        s.canvas.configure(yscrollcommand=bar.set)
        bar.grid(row=0, column=1, sticky="ns")
        s.canvas.grid(row=0, column=0, sticky="nsew")
        s.rowconfigure(0, weight=1)
        s.body = tk.Frame(s.canvas, bg=CARD)
        s.win = s.canvas.create_window((0, 0), window=s.body, anchor="nw")
        s.body.bind("<Configure>", lambda e: s.canvas.configure(scrollregion=s.canvas.bbox("all")))
        s.canvas.bind("<Configure>", s._on_resize)
        for target in (s.canvas, s.body):
            target.bind("<MouseWheel>", s._wheel)
        s._drop_setup()
        s.refresh()

    # ---- photos in and out
    def _drop_setup(s):
        if not HAS_DND:
            return
        for target in (s.canvas, s.body):
            try:
                target.drop_target_register(DND_FILES)
                target.dnd_bind("<<Drop>>", s._drop)
            except Exception:
                pass

    def _drop(s, event):
        try:
            paths = list(s.tk.splitlist(event.data))
        except Exception:
            paths = [event.data]
        added = add_images(paths, ROOT_DIR, s.dest)
        if added:
            s.items += added
            s.refresh()
            s.changed()
            return "break"

    def add(s):
        fs = filedialog.askopenfilenames(title="Choose photos", initialdir=os.path.join(ROOT_DIR, "images"),
                                         filetypes=IMG_TYPES)
        if fs:
            s.items += add_images(list(fs), ROOT_DIR, s.dest)
            s.refresh()
            s.changed()

    def remove(s):
        if s.sel is None or s.sel >= len(s.items):
            return
        name = os.path.basename(s.items[s.sel])
        if not messagebox.askyesno("Remove photo", "Take “%s” off this list?\n\nThe file stays in your images folder." % name):
            return
        del s.items[s.sel]
        s.sel = None
        s.refresh()
        s.changed()

    def move(s, delta):
        if s.sel is None:
            return
        j = s.sel + delta
        if 0 <= j < len(s.items):
            s.items[s.sel], s.items[j] = s.items[j], s.items[s.sel]
            s.sel = j
            s.refresh()
            s.changed()

    def changed(s):
        if s.on_change:
            s.on_change()

    # ---- drawing
    def _columns(s):
        width = max(s.canvas.winfo_width(), 260)
        return max(1, int(width // 134))

    def _on_resize(s, event):
        s.canvas.itemconfigure(s.win, width=event.width)
        cols = max(1, int(max(event.width, 260) // 134))
        if cols != s._cols_cached:
            s._cols_cached = cols
            s.after_idle(s.refresh)

    def refresh(s):
        try:
            for w in s.body.winfo_children():
                w.destroy()
        except tk.TclError:
            return          # the window is closing
        s.tiles = []
        if not s.items:
            tk.Label(s.body, text="Drop photos here, or use “Add photos”.", bg=CARD, fg=MUTED,
                     font=SMALL, pady=30).grid(row=0, column=0, columnspan=4, padx=14)
            return
        cols = s._columns()
        s._cols_cached = cols
        for i, path in enumerate(s.items):
            tile = tk.Frame(s.body, bg=CARD, highlightthickness=2,
                            highlightbackground=ACC if i == s.sel else LINE, bd=0, cursor="hand2")
            tile.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nw")
            img = thumb(path, 118)
            if img:
                pic = tk.Label(tile, image=img, bg=CARD, bd=0)
                pic.image = img
            else:
                pic = tk.Label(tile, text=os.path.basename(str(path))[:16], bg=SOFT, fg=MUTED,
                               width=17, height=7, wraplength=112)
            pic.pack()
            tk.Label(tile, text=str(i + 1), bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack()
            for w in (tile, pic) + tuple(tile.winfo_children()):
                w.bind("<Button-1>", lambda e, idx=i: s._press(idx))
                w.bind("<B1-Motion>", s._motion)
                w.bind("<ButtonRelease-1>", s._release)
            if HAS_DND:
                try:
                    tile.drop_target_register(DND_FILES)
                    tile.dnd_bind("<<Drop>>", s._drop)
                except Exception:
                    pass
            s.tiles.append(tile)

    def _press(s, i):
        s.sel, s._drag, s._hover = i, i, None
        for k, tile in enumerate(s.tiles):
            tile.configure(highlightbackground=ACC if k == i else LINE)

    def _tile_at(s, event):
        w = s.winfo_containing(event.x_root, event.y_root)
        while w is not None:
            if w in s.tiles:
                return s.tiles.index(w)
            w = getattr(w, "master", None)
        return None

    def _motion(s, event):
        """Only move the highlight while dragging: rebuilding tiles mid-drag would drop the grab."""
        if s._drag is None:
            return
        idx = s._tile_at(event)
        if idx == s._hover:
            return
        s._hover = None if idx == s._drag else idx
        for k, tile in enumerate(s.tiles):
            tile.configure(highlightbackground=ACC if k == s.sel else LINE)
        if s._hover is not None and 0 <= s._hover < len(s.tiles):
            s.tiles[s._hover].configure(highlightbackground=GO)

    def _release(s, event):
        if s._drag is None:
            return
        idx = s._hover if s._hover is not None else s._tile_at(event)
        was = s._drag
        s._drag, s._hover = None, None
        if idx is not None and idx != was and 0 <= idx < len(s.items):
            item = s.items.pop(was)
            s.items.insert(idx, item)
            s.sel = idx
            s.changed()
        s.refresh()

    def _wheel(s, event):
        try:
            s.canvas.yview_scroll(int(-event.delta / 120), "units")
        except Exception:
            pass

    def get(s):
        return list(s.items)

    def set(s, v):
        s.items = [x if isinstance(x, str) else (x or {}).get("src", "") for x in (v or [])]
        s.sel = None
        s.refresh()


class BoardField:
    """A PhotoBoard dropped inside a normal form row."""

    def __init__(s, parent, extra, obj=None):
        s.widget = ttk.Frame(parent, style="Card.TFrame")
        s.board = PhotoBoard(s.widget, rows=extra[0] if extra else 2)
        s.board.pack(fill="both", expand=True)
        bar = ttk.Frame(s.widget, style="Card.TFrame")
        bar.pack(fill="x", pady=(4, 0))
        for text, cmd in (("Add photos", s.board.add), ("Remove", s.board.remove),
                          ("◀ Move", lambda: s.board.move(-1)), ("Move ▶", lambda: s.board.move(1))):
            ttk.Button(bar, text=text, command=cmd).pack(side="left", padx=(0, 4))

    def get(s):
        return s.board.get()

    def set(s, v):
        s.board.set(v)


class ItemsField:
    """A nested list editor (the parts of an event, the buttons under your name)."""

    def __init__(s, parent, extra, obj):
        schema, lab, new = extra
        s.widget = ListEditor(parent, obj, schema, lab, new, height=6)

    def get(s):
        s.widget.flush()
        return s.widget.items

    def set(s, v):
        pass


KINDS = {"text": TextField, "long": LongField, "paras": ParasField, "csv": CsvField, "choice": ChoiceField,
         "bool": BoolField, "image": ImageField, "images": BoardField, "items": ItemsField}


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
class Scrolled(ttk.Frame):
    def __init__(s, parent):
        super().__init__(parent, style="Card.TFrame")
        s.c = tk.Canvas(s, highlightthickness=0, bg=CARD)
        bar = ttk.Scrollbar(s, command=s.c.yview)
        s.body = ttk.Frame(s.c, style="Card.TFrame")
        s.body.bind("<Configure>", lambda e: s.c.configure(scrollregion=s.c.bbox("all")))
        w = s.c.create_window((0, 0), window=s.body, anchor="nw")
        s.c.bind("<Configure>", lambda e: s.c.itemconfigure(w, width=e.width))
        s.c.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        s.c.pack(side="left", fill="both", expand=True)
        for target in (s.c, s.body):
            target.bind("<Enter>", lambda e: s.c.bind_all("<MouseWheel>", s.wheel))
            target.bind("<Leave>", lambda e: s.c.unbind_all("<MouseWheel>"))

    def wheel(s, event):
        s.c.yview_scroll(int(-event.delta / 120), "units")


class Form(ttk.Frame):
    def __init__(s, parent, schema, obj):
        super().__init__(parent, padding=4, style="Card.TFrame")
        s.obj, s.fields = obj, []
        s.columnconfigure(1, weight=1)
        for r, (key, label, kind, *extra) in enumerate(schema):
            ttk.Label(s, text=label, wraplength=190, justify="left", style="Field.TLabel").grid(
                row=r, column=0, sticky="nw", padx=(0, 14), pady=7)
            sub = obj
            if kind == "items":
                lst = get_path(obj, key)
                if not isinstance(lst, list):
                    lst = []
                    set_path(obj, key, lst)
                sub = lst
            field = KINDS[kind](s, extra, sub)
            field.widget.grid(row=r, column=1, sticky="ew", pady=7)
            if kind != "items":
                field.set(get_path(obj, key))
            s.fields.append((key, field))

    def flush(s):
        for key, field in s.fields:
            set_path(s.obj, key, field.get())


class ListEditor(ttk.Frame):
    def __init__(s, parent, items, schema, lab, new, height=14, empty_text="Nothing here yet. Press “+ Add”."):
        super().__init__(parent, padding=4)
        s.items, s.schema, s.lab, s.new = items, schema, lab, new
        s.cur, s.form, s.empty_text = None, None, empty_text
        left = ttk.Frame(s, style="Card.TFrame")
        left.pack(side="left", fill="y", padx=(0, 12))
        s.count = ttk.Label(left, text="", style="Muted.TLabel")
        s.count.pack(anchor="w", pady=(0, 4))
        s.lb = tk.Listbox(left, width=28, height=height, exportselection=False, font=FONT, activestyle="none",
                          relief="flat", bd=0, highlightthickness=1, highlightbackground=LINE,
                          highlightcolor=ACC, bg=CARD, selectbackground=ACC, selectforeground="white")
        s.lb.pack(fill="y", expand=True)
        s.lb.bind("<<ListboxSelect>>", lambda e: s.on_select())
        bar = ttk.Frame(left, style="Card.TFrame")
        bar.pack(fill="x", pady=5)
        for text, cmd in (("+ Add", s.add), ("Delete", s.delete), ("▲", lambda: s.move(-1)), ("▼", lambda: s.move(1))):
            ttk.Button(bar, text=text, command=cmd, width=7 if len(text) > 1 else 3).pack(side="left", padx=1)
        s.sc = Scrolled(s)
        s.sc.pack(side="left", fill="both", expand=True)
        s.refresh()
        if items:
            s.select(0)
        else:
            ttk.Label(s.sc.body, text=empty_text, style="Muted.TLabel").pack(padx=10, pady=30)

    def refresh(s):
        s.lb.delete(0, "end")
        for it in s.items:
            s.lb.insert("end", (s.lab(it) or "(untitled)")[:60])
        s.count.configure(text="%d item%s" % (len(s.items), "" if len(s.items) == 1 else "s"))

    def on_select(s):
        sel = s.lb.curselection()
        if sel and sel[0] != s.cur:
            s.flush()
            s.show(sel[0])

    def show(s, i):
        for w in s.sc.body.winfo_children():
            w.destroy()
        s.cur = i
        s.form = Form(s.sc.body, s.schema, s.items[i])
        s.form.pack(fill="both", expand=True)

    def select(s, i):
        s.lb.selection_clear(0, "end")
        s.lb.selection_set(i)
        s.lb.see(i)
        s.show(i)

    def flush(s):
        if s.form is not None and s.cur is not None and s.cur < len(s.items):
            s.form.flush()
            s.lb.delete(s.cur)
            s.lb.insert(s.cur, (s.lab(s.items[s.cur]) or "(untitled)")[:60])
            s.lb.selection_set(s.cur)

    def add(s):
        s.flush()
        s.items.append(s.new())
        s.refresh()
        s.select(len(s.items) - 1)

    def delete(s):
        if s.cur is None or not messagebox.askyesno("Delete", "Delete this item? Photos stay in your images folder."):
            return
        del s.items[s.cur]
        s.form, s.cur = None, None
        for w in s.sc.body.winfo_children():
            w.destroy()
        s.refresh()
        if s.items:
            s.select(0)

    def move(s, delta):
        if s.cur is None:
            return
        s.flush()
        j = s.cur + delta
        if 0 <= j < len(s.items):
            s.items[s.cur], s.items[j] = s.items[j], s.items[s.cur]
            s.refresh()
            s.select(j)


# --------------------------------------------------------------------------
# What each tab edits
# --------------------------------------------------------------------------
BTN = [("label", "Button text", "text"), ("url", "Link (a page or a web address)", "text"),
       ("style", "Colour", "choice", ["primary", "mint", "light"])]
SITE_F = [("name", "Your name", "text"), ("brand", "Site name", "text"), ("tagline", "Tagline", "text"),
          ("roles", "Roles (separate with commas)", "csv"), ("email", "Email", "text"), ("phone", "Phone", "text"),
          ("instagram.handle", "Instagram name (no @)", "text"), ("instagram.url", "Instagram link", "text"),
          ("facebook", "Facebook page link (also used for the Messenger button)", "text"),
          ("logo", "Logo (top of every page)", "image"),
          ("intro.projects", "Projects page intro line", "text"), ("intro.events", "Events page intro line", "text")]
HOME_F = [("hero", "Top collage photos (up to 3, blank = first highlights)", "images", 2),
          ("heroButtons", "Buttons under your name", "items", BTN, lambda b: b.get("label"),
           lambda: {"label": "New button", "url": "", "style": "primary"})]
ABOUT_F = [("about.photo", "Your photo", "image"), ("about.heading", "Heading", "text"),
           ("about.bio", "Bio (blank line between paragraphs)", "paras", 9),
           ("about.experience", "Experience", "items",
            [("date", "Date (YYYY-MM-DD)", "text"), ("title", "What", "text"), ("role", "Your role", "text")],
            lambda x: x.get("title"), lambda: {"date": "2026-01-01", "title": "New experience", "role": ""}),
           ("about.education", "Education", "items",
            [("years", "Years", "text"), ("school", "School", "text"), ("note", "Note", "text")],
            lambda x: x.get("school"), lambda: {"years": "", "school": "New school", "note": ""})]
PROJECT_F = [("title", "Title", "text"), ("subtitle", "Short subtitle", "text"), ("date", "Date (YYYY-MM-DD)", "text"),
             ("text", "Description (blank line between paragraphs)", "paras", 6), ("images", "Photos", "images", 3)]
LINK_F = [("link", "Button link (optional)", "text"), ("linkLabel", "Button text (optional)", "text")]
SECTION_F = [("title", "Part title", "text"), ("text", "Description", "paras", 4), ("images", "Photos", "images", 2)]
EVENT_F = PROJECT_F + [("sections", "Parts (optional, each with its own photos)", "items", SECTION_F,
                        lambda x: x.get("title"), lambda: {"title": "New part", "text": [], "images": []})] + LINK_F
BLOCK_F = [("type", "Block type", "choice", ["heading", "text", "photos", "button"]),
           ("text", "Text (heading or text block)", "long", 4), ("images", "Photos (photos block)", "images", 2),
           ("label", "Button text (button block)", "text"), ("url", "Button link (button block)", "text")]
PAGE_F = [("title", "Page title", "text"), ("slug", "Web name (letters only, blank = automatic)", "text"),
          ("intro", "Intro line", "text"), ("nav", "Show in the top menu", "bool"),
          ("blocks", "Content, top to bottom", "items", BLOCK_F,
           lambda b: "%s: %s" % (b.get("type", "?"), (b.get("text") or b.get("label") or "")[:24]),
           lambda: {"type": "text", "text": "", "images": [], "label": "", "url": ""})]
BOOKING_F = [("date", "Date (YYYY-MM-DD)", "text"), ("status", "Status", "choice", ["booked", "requested", "cancelled"]),
             ("type", "Shoot type", "text"), ("name", "Client name", "text"), ("email", "Email", "text"),
             ("phone", "Phone", "text"), ("location", "Location", "text"), ("notes", "Notes", "long", 4)]


class Server:
    """A tiny local web server so Preview shows the real site."""

    def __init__(s, root):
        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def end_headers(self):
                self.send_header("Cache-Control", "no-store")
                super().end_headers()

        s.root = root
        s.httpd = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=root))
        s.port = s.httpd.server_address[1]
        threading.Thread(target=s.httpd.serve_forever, daemon=True).start()


class AppWin(TkinterDnD.Tk if HAS_DND else tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("Jhake Site Editor")
        s.geometry("1280x860")
        s.minsize(1024, 700)
        s.configure(bg=BG)
        s._style()
        s.backdrop = Backdrop(s)
        s.backdrop.pack(fill="both", expand=True)
        s.backdrop.bind("<Configure>", lambda e: s._layout())

        s.server = None
        s.root_dir = s.pick_root()
        globals()["ROOT_DIR"] = s.root_dir
        s.sync_msg = sync_repo(s.root_dir)         # always start from the live commit
        s.build()
        s.bind("<Control-s>", lambda e: s.save())
        s.bind("<Control-p>", lambda e: s.publish())
        s.protocol("WM_DELETE_WINDOW", s.on_close)

    # ---- look and feel
    def _style(s):
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure(".", background=BG, foreground=INK, font=FONT)
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=CARD)
        st.configure("TLabel", background=BG, foreground=INK)
        st.configure("Card.TLabel", background=CARD)
        st.configure("Field.TLabel", background=CARD, foreground=INK, font=FONT_B)
        st.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=SMALL)
        st.configure("Small.TLabel", background=CARD, foreground=MUTED, font=SMALL)
        st.configure("Title.TLabel", background=CARD, foreground=INK, font=TITLE)
        st.configure("Sub.TLabel", background=CARD, foreground=MUTED, font=SMALL)
        st.configure("TNotebook", background=CARD, borderwidth=0)
        st.configure("TNotebook.Tab", padding=(18, 9), font=FONT_B, background=SOFT, foreground=MUTED,
                     borderwidth=0)
        st.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", ACC)],
               expand=[("selected", (0, 0, 0, 0))])
        st.configure("TButton", padding=(13, 7), background="#ffffff", foreground=INK, font=FONT,
                     borderwidth=0, relief="flat", bordercolor="#ffffff")
        st.map("TButton", background=[("active", SOFT)], foreground=[("active", ACC)])
        st.configure("Go.TButton", background=GO, foreground="white", font=FONT_B, padding=(18, 8), borderwidth=0)
        st.map("Go.TButton", background=[("active", GO_D)])
        st.configure("Acc.TButton", background=ACC, foreground="white", font=FONT_B, padding=(18, 8), borderwidth=0)
        st.map("Acc.TButton", background=[("active", ACC_D)])
        st.configure("TEntry", fieldbackground="#ffffff", bordercolor=LINE, padding=5, lightcolor=LINE,
                     darkcolor=LINE)
        st.configure("TCombobox", fieldbackground="#ffffff", padding=4, bordercolor=LINE)
        st.map("TCombobox", fieldbackground=[("readonly", "#ffffff")])
        st.configure("TCheckbutton", background=CARD, foreground=INK)
        st.map("TCheckbutton", background=[("active", CARD)])

    def pick_root(s, force=False):
        if not force:
            for candidate in (DEFAULT_ROOT, os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
                if os.path.exists(os.path.join(candidate, "content.js")):
                    return candidate
        while True:
            d = filedialog.askdirectory(title="Choose your website folder (the one containing content.js)")
            if not d:
                sys.exit()
            if os.path.exists(os.path.join(d, "content.js")):
                return os.path.abspath(d)
            messagebox.showwarning("Not found", "That folder has no content.js. Pick the website folder.")

    # ---- build the window
    def build(s):
        for part in (getattr(s, "head", None), getattr(s, "body", None), getattr(s, "foot", None)):
            if part is not None:
                part.destroy()
        s.data = load_site(s.root_dir)
        s.bookings = load_json(os.path.join(s.root_dir, "bookings.json"), [])
        s.snapshot = json.dumps(s.data, sort_keys=True)
        # three glass panels: title and buttons, the tabs, the status line
        s.head = tk.Frame(s.backdrop, bg=CARD)
        s.body = tk.Frame(s.backdrop, bg=CARD)
        s.foot = tk.Frame(s.backdrop, bg=CARD)
        s.backdrop.panels = [(s.head, 28), (s.body, 34), (s.foot, 30)]
        s.build_header()
        s.build_tabs()
        s.build_footer()
        s.after_idle(s._layout)

    def _layout(s):
        """Place the three panels, then repaint the glass behind them."""
        width, height = s.backdrop.winfo_width(), s.backdrop.winfo_height()
        if width < 400 or height < 400 or not hasattr(s, "head"):
            return
        margin, gap, head_h, foot_h = 26, 18, 92, 38
        inner = width - 2 * margin
        s.head.place(x=margin, y=margin, width=inner, height=head_h)
        s.foot.place(x=margin, y=height - margin - foot_h, width=inner, height=foot_h)
        s.body.place(x=margin, y=margin + head_h + gap, width=inner,
                     height=max(180, height - 2 * margin - head_h - foot_h - 2 * gap))
        s.backdrop.schedule()

    def build_header(s):
        left = ttk.Frame(s.head, style="Card.TFrame")
        left.pack(side="left", padx=(22, 0), pady=14)
        ttk.Label(left, text="Jhake Site Editor", style="Title.TLabel").pack(anchor="w")
        ttk.Label(left, text=s.root_dir, style="Sub.TLabel").pack(anchor="w", pady=(2, 0))

        right = ttk.Frame(s.head, style="Card.TFrame")
        right.pack(side="right", padx=(0, 20))
        ttk.Button(right, text="Publish live", style="Go.TButton", command=s.publish).pack(side="right", padx=(6, 0))
        ttk.Button(right, text="Preview", style="Acc.TButton", command=s.preview).pack(side="right", padx=6)
        ttk.Button(right, text="Save", command=s.save).pack(side="right")
        ttk.Button(right, text="Pull latest", command=s.pull_now).pack(side="right", padx=6)

    def build_tabs(s):
        s.nb = ttk.Notebook(s.body)
        s.nb.pack(fill="both", expand=True, padx=8, pady=8)
        s.editors = []

        for title, schema in (("Site", SITE_F), ("Home", HOME_F), ("About", ABOUT_F)):
            card = ttk.Frame(s.nb, style="Card.TFrame")
            sc = Scrolled(card)
            sc.pack(fill="both", expand=True, padx=6, pady=6)
            form = Form(sc.body, schema, s.data)
            form.pack(fill="both", expand=True, padx=14, pady=12)
            s.nb.add(card, text=title)
            s.editors.append(form)

        for title, key, schema, lab, new in (
                ("Projects", "projects", PROJECT_F + LINK_F, lambda x: x.get("title"),
                 lambda: {"title": "New project", "subtitle": "", "date": "2026-01-01", "text": [], "images": []}),
                ("Events", "events", EVENT_F, lambda x: x.get("title"),
                 lambda: {"title": "New event", "subtitle": "", "date": "2026-01-01", "text": [], "images": [],
                          "sections": []}),
                ("Pages", "pages", PAGE_F, lambda x: x.get("title"),
                 lambda: {"title": "New page", "slug": "", "intro": "", "nav": True, "blocks": []})):
            card = ttk.Frame(s.nb, style="Card.TFrame")
            s.data.setdefault(key, [])
            le = ListEditor(card, s.data[key], schema, lab, new)
            le.pack(fill="both", expand=True, padx=10, pady=10)
            s.nb.add(card, text=title)
            s.editors.append(le)

        s.build_highlights_tab()
        s.build_bookings_tab()

    def build_highlights_tab(s):
        card = ttk.Frame(s.nb, style="Card.TFrame")
        s.nb.add(card, text="Highlights")

        bar = ttk.Frame(card, style="Card.TFrame")
        bar.pack(fill="x", padx=14, pady=(12, 4))
        ttk.Label(bar, text="The photo wall on the home page", style="Field.TLabel").pack(side="left")
        ttk.Button(bar, text="Automatic (newest first)", command=s.hl_automatic).pack(side="right", padx=4)
        ttk.Button(bar, text="Sort by name", command=lambda: s.hl_sort(named=True)).pack(side="right", padx=4)

        ttk.Label(card, text="Drag photos to rearrange them. Drop photos from Explorer anywhere on this board to add them.",
                  style="Muted.TLabel").pack(anchor="w", padx=16)

        s.hl_manual = False
        s.hl_board = PhotoBoard(card, rows=3, dest="images/highlights", on_change=s.hl_changed)
        s.hl_board.pack(fill="both", expand=True, padx=14, pady=10)

        tools = ttk.Frame(card, style="Card.TFrame")
        tools.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Button(tools, text="Add photos", command=s.hl_board.add).pack(side="left", padx=(0, 4))
        ttk.Button(tools, text="Remove selected", command=s.hl_board.remove).pack(side="left", padx=4)
        ttk.Button(tools, text="◀ Move", command=lambda: s.hl_board.move(-1)).pack(side="left", padx=4)
        ttk.Button(tools, text="Move ▶", command=lambda: s.hl_board.move(1)).pack(side="left", padx=4)

        order = hl_manifest(s.root_dir)
        s.hl_board.set(["images/highlights/" + name for name in order])

    def build_bookings_tab(s):
        card = ttk.Frame(s.nb, style="Card.TFrame")
        s.nb.add(card, text="Bookings")
        head = ttk.Frame(card, style="Card.TFrame")
        head.pack(fill="x", padx=14, pady=(12, 2))
        ttk.Label(head, text="Days marked booked are blocked on the booking page", style="Field.TLabel").pack(side="left")
        s.bk_count = ttk.Label(head, text="", style="Muted.TLabel")
        s.bk_count.pack(side="right")

        def new_booking():
            taken = {b.get("date") for b in s.bookings if b.get("status") != "cancelled"}
            today = datetime.date.today()
            day = today.isoformat()
            while day in taken:
                today += datetime.timedelta(days=1)
                day = today.isoformat()
            return {"id": "bk-editor-%d" % (len(s.bookings) + 1), "date": day, "status": "booked", "type": "",
                    "name": "", "email": "", "phone": "", "location": "", "notes": ""}

        s.bk_editor = ListEditor(card, s.bookings, BOOKING_F,
                                 lambda b: "%s  %s%s" % (b.get("date", "?"),
                                                         (b.get("type") or b.get("name") or "Shoot"),
                                                         "  (cancelled)" if b.get("status") == "cancelled" else ""),
                                 new_booking, height=12,
                                 empty_text="No bookings yet. Press “+ Add” when you confirm a date.")
        s.bk_editor.pack(fill="both", expand=True, padx=10, pady=10)
        s.refresh_booking_count()

    def build_footer(s):
        foot = ttk.Frame(s.foot, style="Card.TFrame")
        foot.pack(fill="both", expand=True, padx=(22, 20))
        s.status = ttk.Label(foot, text="", style="Sub.TLabel")
        s.status.pack(side="left")
        ok, msg = s.sync_msg
        s.set_status("GitHub: " + msg)
        notes = []
        if not Image:
            notes.append("Install Pillow for previews:  pip install pillow")
        if not HAS_DND:
            notes.append("Install tkinterdnd2 to drop photos:  pip install tkinterdnd2")
        if notes:
            ttk.Label(foot, text="   ·   ".join(notes), style="Sub.TLabel").pack(side="right")

    # ---- status and dirty tracking
    def set_status(s, text):
        try:
            s.status.configure(text=text)
        except tk.TclError:
            pass

    def mark_dirty(s, note="Unsaved changes."):
        s.set_status(note + "  Press Save (Ctrl+S) to keep them, Publish to go live.")

    def refresh_booking_count(s):
        if not hasattr(s, "bk_count"):
            return
        live = [b for b in s.bookings if b.get("status") != "cancelled" and b.get("date")]
        s.bk_count.configure(text="%d booked day%s" % (len(live), "" if len(live) == 1 else "s"))

    # ---- highlights actions
    def hl_changed(s):
        s.hl_manual = True
        s.mark_dirty("Highlights rearranged.")

    def hl_collect(s):
        names = [os.path.basename(p) for p in s.hl_board.items]
        present = [n for n in names if os.path.exists(os.path.join(hl_dir(s.root_dir), n))]
        s.data["highlights"] = ["images/highlights/" + n for n in present]
        return present

    def hl_save(s, write=True):
        present = s.hl_collect()
        if not write:
            return len(present)
        if s.hl_manual:
            # A hand-arranged order is kept in layout.json, which the site's own
            # script respects; new photos still arrive on top, newest first.
            save_json(os.path.join(hl_dir(s.root_dir), "layout.json"), {"order": present})
        hl_write_manifest(s.root_dir, present)
        return len(present)

    def hl_automatic(s):
        if not messagebox.askyesno("Newest first", "Go back to the automatic order? "
                                                 "Your hand-arranged order is forgotten and photos sort by date, newest first."):
            return
        layout = os.path.join(hl_dir(s.root_dir), "layout.json")
        if os.path.exists(layout):
            os.remove(layout)
        if not hl_regenerate(s.root_dir):
            order = hl_files(s.root_dir)[::-1]
            hl_write_manifest(s.root_dir, order)
        order = [e.get("file") for e in load_json(os.path.join(hl_dir(s.root_dir), "highlights.json"), []) if e.get("file")]
        s.hl_board.set(["images/highlights/" + n for n in order])
        s.hl_manual = False
        s.mark_dirty("Highlights set back to newest first.")

    def hl_sort(s, named=False):
        paths = s.hl_board.items
        if named:
            s.hl_board.items = sorted(paths, key=lambda p: os.path.basename(p).lower())
        else:
            s.hl_board.items = sorted(paths, key=lambda p: image_size(abs_path(p))[0] * image_size(abs_path(p))[1],
                                      reverse=True)
        s.hl_board.refresh()
        s.mark_dirty()

    # ---- saving
    def flush(s, write=True):
        for editor in s.editors:
            editor.flush()
        if hasattr(s, "bk_editor"):
            s.bk_editor.flush()
        for page in s.data.get("pages", []):
            page["slug"] = slugify(page.get("slug") or page.get("title") or "page")
        s.hl_save(write)

    def validate(s):
        bad = []
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for kind in ("projects", "events"):
            for item in s.data.get(kind, []):
                if not pattern.match(item.get("date", "")):
                    bad.append("%s “%s” needs a date like 2026-12-25" % (kind[:-1], item.get("title")))
        for item in get_path(s.data, "about.experience", []):
            if not pattern.match(item.get("date", "")):
                bad.append("experience “%s” needs a date like 2026-12-25" % item.get("title"))
        for b in s.bookings:
            if not pattern.match(str(b.get("date", ""))):
                bad.append("booking “%s” needs a date like 2026-12-25" % (b.get("name") or b.get("type") or b.get("id")))
        return bad

    def save(s):
        s.flush()
        bad = s.validate()
        if bad:
            messagebox.showwarning("Check the dates", "\n".join(bad))
            return False
        save_site(s.root_dir, s.data)
        save_json(os.path.join(s.root_dir, "bookings.json"), s.bookings)
        s.refresh_booking_count()
        s.snapshot = json.dumps(s.data, sort_keys=True)
        s.set_status("Saved. Photos are in images/highlights and images/uploads; the old content.js is backed up in your home folder.")
        return True

    # ---- git and preview
    def pull_now(s):
        s.flush()
        if json.dumps(s.data, sort_keys=True) != s.snapshot:
            if not messagebox.askyesno("Pull latest", "Reloading from GitHub forgets the edits you have not saved. "
                                                    "Save them first?"):
                return
            if not s.save():
                return
        ok, msg = sync_repo(s.root_dir)
        if ok:
            s.build()
            s.set_status("GitHub: " + msg + "  Reloaded.")
        else:
            s.set_status("GitHub: " + msg)

    def preview(s):
        if not s.save():
            return
        if not s.server or s.server.root != s.root_dir:
            s.server = Server(s.root_dir)
        webbrowser.open("http://127.0.0.1:%d/index.html" % s.server.port)
        s.set_status("Preview opened in your browser (it shows what is in the folder right now).")

    def publish(s):
        if not s.save():
            return
        msg = simpledialog.askstring("Publish live", "What changed?", initialvalue="Update site", parent=s)
        if not msg:
            return
        s.set_status("Pushing to GitHub…")
        s.update_idletasks()
        ok, text = publish_repo(s.root_dir, msg)
        s.set_status(("Published. " if ok else "Not published. ") + "Live: " + SITE_URL)
        detail = tk.Toplevel(s)
        detail.title("Publish: " + ("done" if ok else "needs attention"))
        detail.geometry("720x420")
        detail.configure(bg=BG)
        tk.Label(detail, text="Published. The live site updates in about a minute." if ok
                 else "Could not publish. The details are below.",
                 bg=BG, fg=GO if ok else "#b42318", font=FONT_B, anchor="w").pack(fill="x", padx=16, pady=(14, 6))
        box = tk.Text(detail, wrap="word", font=("Consolas", 9), bg=CARD, relief="flat",
                      highlightthickness=1, highlightbackground=LINE, padx=10, pady=8)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        box.insert("1.0", text)
        box.configure(state="disabled")
        row = ttk.Frame(detail, style="Card.TFrame")
        row.pack(fill="x", padx=16, pady=(0, 14))
        if ok:
            ttk.Button(row, text="Open the live site", command=lambda: webbrowser.open(SITE_URL)).pack(side="left")
        ttk.Button(row, text="Close", command=detail.destroy).pack(side="right")

    def change_root(s):
        s.flush()
        s.root_dir = s.pick_root(force=True)
        globals()["ROOT_DIR"] = s.root_dir
        s.sync_msg = sync_repo(s.root_dir)
        s.build()

    def on_close(s):
        try:
            s.flush(write=False)          # change nothing on disk unless they say save
            if json.dumps(s.data, sort_keys=True) != s.snapshot:
                answer = messagebox.askyesnocancel("Unsaved changes", "Save your changes before closing?")
                if answer is None:
                    return
                if answer and not s.save():
                    return
        except Exception:
            pass
        s.destroy()


def main():
    try:
        AppWin().mainloop()
    except SystemExit:
        pass
    except Exception:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Site Editor crashed", traceback.format_exc()[-1800:])
        except Exception:
            pass


if __name__ == "__main__":
    main()
