# own-ai

A tiny browser-only PDF annotation tool. No GPU, AI backend, server, accounts, or paid API.

## Use
Open `index.html` in a browser (or enable GitHub Pages from the repository root). Upload a PNG/JPG/PDF, enter `Add text: Your note`, and click **Generate PDF**.

The tool adds a visible note to the first page and downloads the PDF. It never modifies existing text. PDF export uses pdf-lib from a CDN, so the library needs an internet connection unless bundled locally.

## Limits
Rule-based prompts only. No OCR, no semantic image editing, no underlying text replacement. Not intended for altering government credentials. Uploaded files are processed locally in the browser.

## Development
Edit `index.html` directly. No build step.
