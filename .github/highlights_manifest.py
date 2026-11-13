#!/usr/bin/env python3
"""Rebuilds images/highlights/highlights.json from the photos in images/highlights/.

Newest first: photos that are already listed keep the order they have, and photos
that are new to the folder go to the front. Run this after adding photos, or let
the GitHub Action in .github/workflows/highlights.yml run it on push.
"""
import json
import os
import subprocess

FOLDER = "images/highlights"
MANIFEST = os.path.join(FOLDER, "highlights.json")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}


def photos():
    if not os.path.isdir(FOLDER):
        return set()
    return {
        f for f in os.listdir(FOLDER)
        if os.path.splitext(f)[1].lower() in EXTS and os.path.isfile(os.path.join(FOLDER, f))
    }


def age(name):
    """Last commit time of the file, so fresh uploads sort first even in a fresh clone."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", os.path.join(FOLDER, name)],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        if out:
            return int(out)
    except (OSError, ValueError):
        pass
    try:
        return int(os.path.getmtime(os.path.join(FOLDER, name)))
    except OSError:
        return 0


def main():
    files = photos()
    try:
        with open(MANIFEST) as fh:
            previous = [f for f in json.load(fh) if isinstance(f, str)]
    except (OSError, ValueError):
        previous = []

    kept = [f for f in previous if f in files]
    fresh = sorted(files - set(kept), key=lambda f: (age(f), os.path.splitext(f)[0]), reverse=True)
    order = fresh + kept

    with open(MANIFEST, "w") as fh:
        json.dump(order, fh, indent=2)
        fh.write("\n")
    print("%d highlights, %d new at the front" % (len(order), len(fresh)))


if __name__ == "__main__":
    main()
