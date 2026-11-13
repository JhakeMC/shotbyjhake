# Jhake Does Photography: website

Plain HTML/CSS/JS. No build step. Content lives in `content.js`.

## Easiest way to edit: the Site Editor
Double-click `site_editor.pyw`. It now sits in this folder, so it arrives with every pull. It is harmless on the live site (a browser only downloads it if you ask for it), and you can move or delete it later if you want it out of the repository.

Two files travel together: **`site_editor.pyw`** and **`ui_glass.py`**, which paints the window's frosted glass. Keep them side by side. If `ui_glass.py` is missing the editor still runs, just without the glass.

**It pulls the latest commit from GitHub every time it opens**, so you always start from what is live. If there are unsaved edits it will not pull over them.

Tabs: **Site** (name, contacts, logo), **Home** (top collage, buttons), **About**, **Projects**, **Events**, **Pages**, **Highlights** (the photo wall), **Bookings** (days that are taken).

Every photo list is a board. Drag a photo onto another to move it, drop photos from Explorer straight onto the board to add them, or use the "Add photos" button. Photos are copied into `images/highlights/` or `images/uploads/` untouched, at full quality: nothing is resized or re-compressed.

Buttons: **Save** (Ctrl+S), **Preview** (opens this folder in your browser), **Pull latest**, and **Publish live** (saves, commits and pushes; the live site updates in about a minute).

Two optional extras make it nicer; the window tells you if they are missing:
```
pip install pillow tkinterdnd2
```
Pillow draws the photo previews, and tkinterdnd2 makes dropping files from Explorer work. Without tkinterdnd2 you can still add photos with the button.

## Highlights (the photo wall on the home page)
The wall is the photos inside `images/highlights/`. `highlights.json` lists them in the order they appear, with each photo's pixel size so the wall can be laid out before the photos download. `.github/highlights_manifest.py` rebuilds that file, sorting by the newest date in each photo's metadata (the shot date, or the date the edited file was saved), so the newest is always first.

To arrange the wall by hand, use the editor's **Highlights** tab: drag the tiles into the order you want and save. That order is stored in `images/highlights/layout.json`, and the script respects it. A photo that is not in that file yet still jumps to the top, newest first. The **Automatic (newest first)** button forgets the hand order and goes back to sorting by date.

The GitHub Action in `.github/workflows/highlights.yml` re-runs the script whenever photos change and commits the new list.

## Get your photos back from the old Google Site (run once)
Double-click `import_old_site_photos.py`. It downloads the photos into `images/old-site/` and fills the home highlights, projects and events.

## Bookings
`booking.html` has the booking form and the availability calendar. The calendar reads `bookings.json`: every entry there is a day marked as booked, so add a booking when you confirm one. The editor's **Bookings** tab edits that file directly: press "+ Add", set the date, and the day is blocked. Set the status to `cancelled` to open the day again.

A static site cannot write to `bookings.json` by itself, so a request is not added automatically: the client fills the form, and the page gives them a ready-made email to you plus keeps the request saved on their device. Booking details in `bookings.json` are public, so put dates in it rather than your clients' personal details.

The booking page also offers other ways in: call or text, an Instagram DM, and a message to the Facebook page. Those read from the phone, Instagram and Facebook fields on the editor's **Site** tab.

If you later want requests to land in a form service automatically (Formspree and similar accept a JSON POST), put its URL in `data-endpoint` on the form, in `app.js`.

## Light and dark
The site follows the visitor's device colour scheme on a first visit, and the small sun/moon button beside the logo overrides it and remembers the choice.

## Editing by hand
Open `content.js` in Notepad. Keep it valid JSON (double quotes, commas between items, none after the last).

## Publish
Use the editor's **Publish live** button, or commit and push the folder with GitHub Desktop. GitHub Pages updates in about a minute.
