# Working on this repo

## Pull first, always
Before changing anything, run `git fetch origin main` and fast-forward to it:

```
git fetch origin main
git merge --ff-only FETCH_HEAD
```

Then tell the owner what moved since the last session before you edit. Jhake edits
the site by hand (content.js, photos in `images/highlights/`) and pushes with
GitHub Desktop, so the repository can change between sessions.

- Only **pushed** work is visible here. If something seems missing, say it may be
  unpushed rather than assuming it was lost.
- Never overwrite the owner's manual edits with an older copy. If the tree is dirty
  and the remote has moved, stop and ask before merging or discarding anything.
- Do not commit or push unless the owner asks. When they do, push to `main` and
  verify the live site afterwards.

## The site
Static HTML/CSS/JS on GitHub Pages, no build step, no server at runtime.
Live: <https://jhakemc.github.io/shotbyjhake/> (rebuilds in roughly 40–80 seconds).

- `content.js` holds all text and photo lists. `app.js` renders every page.
  `style.css` is the whole look. Booking lives in `booking.html` + `booking.js`,
  availability in `bookings.json`.
- Other useful files: `sound.js`, `page.html` (custom pages), `site_editor.pyw`
  and `ui_glass.py` (the desktop editor; they must travel together).

### Photos
The owner shoots and edits at full resolution and uploads the edited files.
**Never downscale, re-compress or convert their photos.** Add lazy loading,
`fetchpriority` and size hints instead.

### Highlights
`images/highlights/` is the photo wall. `.github/highlights_manifest.py` writes
`highlights.json`: newest first by the newest date in each photo's metadata, with
each photo's pixel size so the wall can be laid out before images load.

`images/highlights/layout.json` (`{"order": [...]}`) is a hand-made order from the
editor and wins over the date sort; photos missing from it go on top, newest first.
A GitHub Action re-runs the script whenever `images/highlights/**` changes.

### Style
Light and dark themes, switched by `data-theme` on `<html>`: the device decides on
a first visit, the sun/moon button beside the logo overrides it and remembers.
Glassmorphism throughout: translucent white cards, blurred backdrop, coloured
glows. The editor copies the same recipe in `ui_glass.py` — when a colour or
radius changes in `style.css`, mirror it there.

## Bookings
`bookings.json` is public, so it holds dates and shoot details, not client
personal data. A request is not stored automatically: the visitor gets a ready-made
email and the day is added by the owner. The booking page also offers call/text,
Instagram DM and Messenger, built from the phone and Facebook fields in `content.js`.

## Git identity
The repo has no configured identity. Commit as the last author so the history stays
consistent:

```
NAME=$(git log -1 --format='%an'); EMAIL=$(git log -1 --format='%ae')
GIT_AUTHOR_NAME="$NAME" GIT_AUTHOR_EMAIL="$EMAIL" \
GIT_COMMITTER_NAME="$NAME" GIT_COMMITTER_EMAIL="$EMAIL" \
git commit -m "..."
```

Keep the `.pyw` extension on `site_editor.pyw`; Windows runs it without a console.
