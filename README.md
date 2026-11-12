# Jhake Does Photography: website

Plain HTML/CSS/JS. No build step. Content lives in `content.js`.

## Easiest way to edit: the Site Editor
Use `site_editor.pyw` (a separate file, keep it OUTSIDE this folder so it is not published).
Double-click it. It edits `content.js` and copies photos into `images/uploads/` in your website folder.
Tabs: Site (name, contacts, logo), Home (collage, highlights, buttons), About, Projects, Events, Pages (make new pages with headings, text, photos and buttons).
Buttons: Save, Preview site (opens it in your browser), Publish to GitHub.

## Get your photos back from the old Google Site (run once)
Double-click `import_old_site_photos.py`. It downloads the photos into `images/old-site/` and fills the home highlights, projects and events.

## Bookings
`booking.html` has the booking form and the availability calendar. The calendar reads `bookings.json`: every entry there is a day marked as booked, so add a booking there when you confirm one (copy an existing entry and change `"date"` to `YYYY-MM-DD`). Set `"status": "cancelled"` to open the day again.

A static site cannot write to `bookings.json` by itself, so a request is not added automatically: the client fills the form, and the page gives them a ready-made email to you plus keeps the request saved on their device. Booking details in `bookings.json` are public, so put dates in it rather than your clients' personal details.

If you later want requests to land in a form service automatically (Formspree and similar accept a JSON POST), put its URL in `data-endpoint` on the form, in `app.js`.

## Editing by hand
Open `content.js` in Notepad. Keep it valid JSON (double quotes, commas between items, none after the last).

## Publish
Commit and push the folder with GitHub Desktop (or the editor's Publish button if git is installed). GitHub Pages updates in about a minute.
