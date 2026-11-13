#!/usr/bin/env python3
"""Rebuilds images/highlights/highlights.json from the photos in images/highlights/.

Newest first: each photo is placed by the newest date it carries in its metadata
(the shot date or the date the edited file was saved), so the latest photo is
always the first one on the page. Photos with no dates fall back to their file
date, then their name.

Each entry also records the photo's width and height, which lets the page lay the
wall out in Pinterest-style columns before the images have downloaded.

Run this after adding photos, or let the GitHub Action in
.github/workflows/highlights.yml run it on push.
"""
import json
import os
import time

FOLDER = "images/highlights"
MANIFEST = os.path.join(FOLDER, "highlights.json")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
SHOT = (0x9003, 0x9004)   # DateTimeOriginal, DateTimeDigitized (in the Exif block)
SAVED = 0x0132            # DateTime (in the main block)


def photos():
    if not os.path.isdir(FOLDER):
        return []
    return [
        f for f in os.listdir(FOLDER)
        if os.path.splitext(f)[1].lower() in EXTS and os.path.isfile(os.path.join(FOLDER, f))
    ]


def tiff_dates(tiff):
    """Every date stamp in an EXIF block, as 'YYYY:MM:DD HH:MM:SS' strings."""
    if len(tiff) < 8:
        return []
    order = {b"II": "little", b"MM": "big"}.get(tiff[:2])
    if not order:
        return []

    def u16(at):
        return int.from_bytes(tiff[at:at + 2], order)

    def u32(at):
        return int.from_bytes(tiff[at:at + 4], order)

    def entry(offset, tag):
        if offset <= 0 or offset + 2 > len(tiff):
            return None
        for k in range(u16(offset)):
            at = offset + 2 + k * 12
            if at + 12 > len(tiff):
                return None
            if u16(at) == tag:
                return at
        return None

    def text(at):
        count = u32(at + 4)
        start = at + 8 if count <= 4 else u32(at + 8)
        raw = tiff[start:start + count]
        value = raw.split(b"\x00")[0].decode("ascii", "ignore").strip()
        return value if len(value) >= 19 else ""

    found = []
    main = u32(4)
    saved = entry(main, SAVED)
    if saved:
        found.append(text(saved))
    exif = entry(main, 0x8769)
    if exif:
        block = u32(exif + 8)
        for tag in SHOT:
            at = entry(block, tag)
            if at:
                found.append(text(at))
    return [d for d in found if d]


def exif_dates(path):
    """The APP1/EXIF block sits near the start of a JPEG; pull the dates out of it."""
    try:
        with open(path, "rb") as fh:
            data = fh.read(4_000_000)
    except OSError:
        return []
    i = 2
    while i < len(data) - 4:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:
            i += 2
            continue
        if marker in (0xDA, 0xD9):
            break
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if marker == 0xE1 and data[i + 4:i + 10] == b"Exif\x00\x00":
            return tiff_dates(data[i + 10:i + 2 + length])
        i += 2 + length
    return []


def stamp(name):
    """The newest date the file carries, so a fresh edit outranks an older shot."""
    path = os.path.join(FOLDER, name)
    dates = exif_dates(path)
    if dates:
        return max(dates)
    try:
        return time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
    except OSError:
        return ""


def size(name):
    """Pixel width and height, straight from the file header."""
    path = os.path.join(FOLDER, name)
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
                    if fh.tell() >= 4_000_000:
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


def main():
    order = sorted(photos(), key=lambda f: (stamp(f), os.path.splitext(f)[0]), reverse=True)
    entries = []
    for name in order:
        width, height = size(name)
        entries.append({"file": name, "w": width, "h": height})
    with open(MANIFEST, "w") as fh:
        json.dump(entries, fh, indent=2)
        fh.write("\n")
    print("%d highlights, newest first: %s" % (len(entries), order[0] if order else "-"))


if __name__ == "__main__":
    main()
