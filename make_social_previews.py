"""
Makes the glass-style link-preview pictures (1200x630) shown when your site link is shared on
Instagram, Facebook, Discord, etc. Saves og-home.jpg, og-about.jpg, og-projects.jpg, og-events.jpg
into <website>/images. Needs Pillow (pip install pillow). Edit PAGES below to change the words.
Usage: python make_social_previews.py ["C:\\path\\to\\website"]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

DEFAULT_ROOT = r"C:\Users\Mary Grace\Documents\GitHub\shotbyjhake"
PHOTO = "images/portrait-01.jpg"      # photo shown on the right
LOGO = "images/logo.png"
RED, VIOLET, ROSE, LILAC, INK, MUTED = (237, 32, 36), (124, 58, 237), (255, 92, 138), (167, 139, 250), (43, 22, 70), (106, 87, 132)
CHIPS = [("Portrait", RED), ("Event", VIOLET), ("Street", (192, 32, 127))]
PAGES = {
    "home": ("Jhake\nTogonon", "Capturing moments. Telling stories."),
    "about": ("About\nme", "Self-taught photographer. Portrait, event and street."),
    "projects": ("Projects", "Shoots and productions I have been part of."),
    "events": ("Events", "Workshops and events I have shot or joined."),
}
FONTS_B = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONTS_M = [r"C:\Windows\Fonts\segoeuisb.ttf", r"C:\Windows\Fonts\segoeui.ttf", "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def background(W, H):
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    for y in range(H):
        for x in range(W):
            t = (x / W + y / H) / 2
            px[x, y] = (round(255 - 13 * t), round(242 - 8 * t), round(243 + 12 * t))
    blobs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(blobs)
    for cx, cy, r, c, a in ((60, 40, 330, RED, 190), (1150, 90, 360, VIOLET, 200), (900, 690, 330, ROSE, 170), (40, 640, 320, LILAC, 210)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c + (a,))
    blobs = blobs.filter(ImageFilter.GaussianBlur(95))
    return Image.alpha_composite(bg.convert("RGBA"), blobs)


def glass(base, box, radius, tint=95):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 14, x1, y1 + 14), radius, fill=VIOLET + (70,))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(26)))
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius, fill=255)
    frosted = base.crop(box).filter(ImageFilter.GaussianBlur(22))
    layer = Image.new("RGBA", base.size)
    layer.paste(frosted, box[:2])
    base = Image.composite(layer, base, mask)
    ov = Image.new("RGBA", base.size, (255, 255, 255, 0))
    od = ImageDraw.Draw(ov)
    od.rounded_rectangle(box, radius, fill=(255, 255, 255, tint), outline=(255, 255, 255, 215), width=3)
    return Image.alpha_composite(base, ov)


def gradient_text(img, xy, text, f, spacing=-6):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).multiline_text(xy, text, font=f, fill=255, spacing=spacing)
    bb = mask.getbbox()
    grad = Image.new("RGBA", img.size)
    gp = grad.load()
    x0, x1 = bb[0], bb[2]
    for x in range(bb[0], bb[2] + 1):
        t = (x - x0) / max(1, x1 - x0)
        c = tuple(round(RED[i] * (1 - t) + VIOLET[i] * t) for i in range(3))
        c = tuple(round(c[i] * 0.9 + (214, 36, 159)[i] * 0.1 * (1 - abs(2 * t - 1))) for i in range(3))
        for y in range(bb[1], bb[3] + 1):
            gp[x, y] = c + (255,)
    out = Image.new("RGBA", img.size)
    out.paste(grad, mask=mask)
    return Image.alpha_composite(img, out), bb


def photo_card(base, root, center, size, angle):
    p = ImageOps.exif_transpose(Image.open(os.path.join(root, PHOTO))).convert("RGB")
    w, h = size
    ch = p.height
    cw = round(ch * w / h)
    left = max(0, min(p.width - cw, round(p.width * 0.47 - cw / 2)))
    p = p.crop((left, 0, left + cw, ch)).resize((w, h), Image.LANCZOS)
    pad = 12
    card = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 34, fill=(255, 255, 255, 205))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=255)
    card.paste(p, (pad, pad), m)
    M = 90  # extra room so the blurred shadow is never cut off
    shadow = Image.new("RGBA", (card.width + 2 * M, card.height + 2 * M), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((M, M, M + card.width - 1, M + card.height - 1), 34, fill=VIOLET + (150,))
    shadow = shadow.rotate(angle, resample=Image.BICUBIC, expand=True).filter(ImageFilter.GaussianBlur(22))
    card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(shadow, (center[0] - shadow.width // 2, center[1] - shadow.height // 2 + 18)) if False else None
    sx, sy = center[0] - shadow.width // 2, center[1] - shadow.height // 2 + 18
    layer.paste(shadow, (sx, sy), shadow)
    base = Image.alpha_composite(base, layer)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(card, (center[0] - card.width // 2, center[1] - card.height // 2), card)
    return Image.alpha_composite(base, layer)


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def make(root, key):
    W, H = 1200, 630
    title, sub = PAGES[key]
    img = background(W, H)
    img = glass(img, (56, 52, 1144, 578), 58)
    logo = Image.open(os.path.join(root, LOGO)).convert("RGBA")
    lh = 72
    img.alpha_composite(logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS), (104, 90))
    two = "\n" in title
    img, bb = gradient_text(img, (108, 170), title, font(FONTS_B, 104 if two else 124), spacing=-20 if two else 0)
    d = ImageDraw.Draw(img)
    sf = font(FONTS_M, 30)
    y = bb[3] + 24
    for line in wrap(d, sub, sf, 590):
        d.text((112, y), line, font=sf, fill=INK)
        y += 40
    cf = font(FONTS_B, 25)
    x, cy = 112, y + 18
    chip = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip)
    pos = []
    for label, col in CHIPS:
        tw = d.textlength(label, font=cf)
        cd.rounded_rectangle((x, cy, x + tw + 40, cy + 48), 24, fill=(255, 255, 255, 215), outline=(255, 255, 255, 255), width=2)
        pos.append((x + 20, cy + 7, label, col))
        x += tw + 40 + 12
    img = Image.alpha_composite(img, chip)
    d = ImageDraw.Draw(img)
    for px_, py_, label, col in pos:
        d.text((px_, py_), label, font=cf, fill=col)
    img = photo_card(img, root, (935, 316), (330, 430), -5)
    return img.convert("RGB")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT
    if not os.path.exists(os.path.join(root, "images")):
        root = input("Website folder: ").strip().strip('"')
    for key in PAGES:
        out = os.path.join(root, "images", "og-%s.jpg" % key)
        make(root, key).save(out, "JPEG", quality=88, optimize=True, progressive=True)
        print("saved", out)


if __name__ == "__main__":
    main()
