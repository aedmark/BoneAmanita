# Portfolio site (Neocities)

A static portfolio and resume for Andrew Edmark / Oopis McGoopis LLC. Plain HTML, CSS and a
few lines of JavaScript. No build step, no frameworks, no external requests, so it runs
unchanged on Neocities' free tier.

## Files

| File | What it is |
|---|---|
| `index.html` | Home: intro, seven project spotlights, approach, other repos, about and contact. |
| `resume.html` | Print-friendly resume. Use the "Print / save as PDF" button for a PDF. |
| `style.css` | All styling. Colour tokens are at the top; dark by default, light via system preference or the toggle. |
| `script.js` | Theme toggle and footer year. The site works with JavaScript disabled. |
| `favicon.svg` | Tab icon. |
| `not_found.html` | Custom 404. Neocities serves this file automatically for missing pages. |

## Uploading to Neocities

1. Sign in at <https://neocities.org> and open the site dashboard.
2. Drag every file in this folder into the file manager (or use "Upload").
   Upload the files themselves, not the `portfolio` folder, so `index.html` sits at the site root.
3. That's it. The site is live at `https://<yourname>.neocities.org`.

To update later, re-upload the changed files. If you prefer the command line, the
[neocities CLI](https://github.com/neocities/neocities-node) can push the folder:

```bash
npm install -g neocities
neocities push ./portfolio
```

## Editing

- **Project text** lives in `index.html`, one `<article class="spot">` per project.
- **Resume entries** are the `<div class="entry">` blocks in `resume.html`; add or remove them
  freely. The `.todo` style is available for any "edit me" notes and is hidden when printing.
- **Colours and fonts** are CSS custom properties at the top of `style.css`.
- **Contact details** appear in the About section of `index.html` and the header of `resume.html`.
