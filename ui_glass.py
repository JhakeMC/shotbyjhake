#!/usr/bin/env python3
"""
The frosted glass look for the Site Editor window.

Tkinter cannot blur what is behind a widget, so the window paints its own
backdrop and draws the glass itself, using the same recipe as style.css:

    background   linear-gradient(160deg,#fff2f3,#f2eaff) plus four soft
                 radial glows in red, violet, rose and lilac
    glass        white at 42% over that, blurred 20px and saturate(180%)
    edge         1px white hairline at 72%
    shadow       0 10px 36px rgba(124,58,237,.16) and 0 2px 8px rgba(237,32,36,.08)
    corners      24-36px radius

Every colour below is taken from the website so the two match. Change them
here and the whole window follows. Needs Pillow; without it the window keeps a
plain pastel background.
"""
try:
    import tkinter as tk
    _Base = tk.Canvas
    _NO_TK = None
except Exception:                      # lets the drawing code be tested on its own
    tk = None
    _Base = object
    _NO_TK = "tkinter is not available"

try:
    from PIL import Image, ImageDraw, ImageFilter
except Exception:
    Image = ImageDraw = ImageFilter = None
try:
    from PIL import ImageTk
except Exception:
    ImageTk = None

# ---- palette, straight from style.css
RED, RED_D = "#ed2024", "#c9141c"
VIOLET, VIOLET_D = "#7c3aed", "#6d28d9"
ROSE, LILAC = "#ff5c8a", "#b79cff"
INK, MUTED = "#2b1646", "#6a5784"
BG = "#fbeef9"                 # the page colour, used before the glass is painted
CARD = "#fafafe"               # the clean middle of a panel, where the controls sit
LINE = "#e8dff8"               # input borders, rgba(124,58,237,.22) on light glass
SOFT = "#f3ecfe"               # quiet button and tab fill
ACC, ACC_D = VIOLET, VIOLET_D
GO, GO_D = RED, RED_D          # the site's main button is red, so Publish is too

# ---- the same numbers as the stylesheet
BLUR = 8                       # CSS blurs 20px, but the backdrop is already smooth
GLASS_WHITE = 0.42             # --glass: rgba(255,255,255,.42)
EDGE_WHITE = 0.72              # --glass-line: rgba(255,255,255,.72)
PAD = 15                       # the visible ring of glass around each panel
GLOWS = ((0.06, 0.08, 1.00, (237, 32, 36, 107)),      # 42vmax at 6% 8%, .42 red
         (0.96, 0.18, 1.10, (124, 58, 237, 117)),     # 46vmax at 96% 18%, .46 violet
         (0.72, 0.96, 0.95, (255, 92, 138, 97)),      # 40vmax at 72% 96%, .38 rose
         (0.04, 0.92, 0.90, (167, 139, 250, 128)))    # 38vmax at 4% 92%, .50 lilac

_EDGE_ALPHA = int(round(GLASS_WHITE * 255))
_CORE_ALPHA = 250
_CACHE = {}


def _gradient(width, height):
    """The page background: a pale diagonal wash with four coloured glows on top."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    top, bottom = (255, 242, 243), (242, 234, 255)
    for y in range(height):
        t = y / max(height - 1, 1)
        draw.line([(0, y), (width, y)],
                  fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glows = ImageDraw.Draw(overlay)
    span = max(width, height)
    for cx, cy, size, colour in GLOWS:
        x, y, r = int(width * cx), int(height * cy), int(0.42 * span * size)
        glows.ellipse([x - r, y - r, x + r, y + r], fill=colour)
    overlay = overlay.filter(ImageFilter.GaussianBlur(max(24, span // 18)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def backdrop(width, height):
    """Cached, because the gradient never changes for a given size."""
    key = (width, height)
    if key not in _CACHE:
        if len(_CACHE) > 3:
            _CACHE.clear()
        _CACHE[key] = _gradient(width, height)
    return _CACHE[key].copy()


def panel(img, x, y, w, h, radius):
    """Draw one frosted panel: shadow, glass, hairline edge."""
    width, height = img.size
    box = (max(0, x - PAD), max(0, y - PAD), min(width, x + w + PAD), min(height, y + h + PAD))
    if box[2] - box[0] < 70 or box[3] - box[1] < 50:
        return img
    margin = 36
    rx0, ry0 = max(0, box[0] - margin), max(0, box[1] - margin)
    rx1, ry1 = min(width, box[2] + margin), min(height, box[3] + margin)
    region = img.crop((rx0, ry0, rx1, ry1)).convert("RGBA")
    local = (box[0] - rx0, box[1] - ry0, box[2] - rx0, box[3] - ry0)
    shape = (local[0], local[1], local[2], local[3])

    # --shadow: violet below, a hint of red just under the edge
    shadows = Image.new("RGBA", region.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadows)
    sd.rounded_rectangle((local[0], local[1] + 10, local[2], local[3] + 10),
                         radius=radius, fill=(124, 58, 237, 42))
    sd.rounded_rectangle((local[0], local[1] + 2, local[2], local[3] + 2),
                         radius=radius, fill=(237, 32, 36, 20))
    region = Image.alpha_composite(region, shadows.filter(ImageFilter.GaussianBlur(12)))

    # --glass: white over what is behind, so the wallpaper tints the edges
    under = region.convert("RGB").filter(ImageFilter.GaussianBlur(BLUR))
    mask = Image.new("L", under.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle(shape, radius=radius, fill=_EDGE_ALPHA)
    inner = (local[0] + PAD, local[1] + PAD, local[2] - PAD, local[3] - PAD)
    md.rounded_rectangle(inner, radius=max(8, radius - PAD), fill=_CORE_ALPHA)
    mask = mask.filter(ImageFilter.GaussianBlur(BLUR))
    frost = Image.composite(Image.new("RGB", under.size, (255, 255, 255)), under, mask).convert("RGBA")
    opaque = Image.new("L", under.size, 0)
    ImageDraw.Draw(opaque).rounded_rectangle(shape, radius=radius, fill=255)
    frost.putalpha(opaque)
    region = Image.alpha_composite(region, frost)

    # --the bright hairline that makes it read as glass
    edge = Image.new("RGBA", region.size, (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(shape, radius=radius,
                                           outline=(255, 255, 255, int(EDGE_WHITE * 255)), width=1)
    region = Image.alpha_composite(region, edge)

    img.paste(region.convert("RGB"), (rx0, ry0))
    return img


def compose(width, height, boxes):
    """The whole window background: gradient, then every panel in order."""
    img = backdrop(width, height)
    for x, y, w, h, radius in boxes:
        img = panel(img, x, y, w, h, radius)
    return img


class Backdrop(_Base):
    """Wallpaper plus glass. Widgets are drawn over this by tkinter."""

    def __init__(s, parent):
        if _NO_TK:
            raise RuntimeError(_NO_TK)
        super().__init__(parent, highlightthickness=0, bd=0, bg=BG)
        s.panels = []          # [(widget, corner radius), ...]
        s._item = None
        s._photo = None
        s._job = None

    def schedule(s, delay=150):
        """Repaint once the layout has settled, not on every resize step."""
        if s._job:
            try:
                s.after_cancel(s._job)
            except Exception:
                pass
        s._job = s.after(delay, s.redraw)

    def _boxes(s):
        out = []
        for widget, radius in s.panels:
            try:
                if not widget.winfo_ismapped():
                    continue
                out.append((widget.winfo_rootx() - s.winfo_rootx(),
                            widget.winfo_rooty() - s.winfo_rooty(),
                            widget.winfo_width(), widget.winfo_height(), radius))
            except Exception:
                continue
        return out

    def redraw(s):
        s._job = None
        width, height = s.winfo_width(), s.winfo_height()
        if width < 60 or height < 60:
            return
        if not (Image and ImageDraw and ImageFilter and ImageTk):
            return
        try:
            img = compose(width, height, s._boxes())
            s._photo = ImageTk.PhotoImage(img)
        except Exception:
            return
        if s._item is None:
            s._item = s.create_image(0, 0, anchor="nw", image=s._photo)
        else:
            s.itemconfigure(s._item, image=s._photo)
        s.tag_lower(s._item)
