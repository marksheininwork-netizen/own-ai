# Own AI Studio

A free, static, browser-based editor: **upload → edit → download**.

## Website
https://marksheininwork-netizen.github.io/own-ai/

## Implemented
- Upload PNG, JPEG, WebP, SVG (up to 25 MB and 25 megapixels) and preview in canvas.
- Paste an image from the clipboard (Cmd/Ctrl+V), or upload an image.\n- Drag to select existing text, cover it with a sampled flat background color, and add replacement text. Undo the last replacement.\n- Adjust brightness, contrast, saturation, grayscale; rotate, mirror, overlay centered text.
- Download rendered PNG or JPEG.
- Upload and edit TXT, MD, JSON, CSV, HTML, CSS, JS, TS, PY, XML, YAML and LOG.
- Download edited text, export HTML, or use browser print to save a PDF.
- Limited instruction parsing for common image and text transformations.
- Client-side processing: no account, API key, or paid inference required.

## Not implemented
- **Generative AI editing** (arbitrary natural-language image or document changes).
- DOCX, XLSX, PPTX, and PDF import/edit/export.
- AI image generation, object removal, OCR, background removal, and automatic text recognition/font matching.\n- Text replacement over complex backgrounds (current replacement uses a flat sampled fill).
- Cross-browser automated testing.

This project does **not** claim to be an unlimited hosted generative AI. GitHub Pages serves static files and provides no GPU inference. A future version may offer optional on-device WebGPU models, subject to hardware/browser limits, or an opt-in external provider.

## Development
Open `index.html` in a browser or run a static server:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Privacy
Editing is performed in your browser; files are not uploaded to a server by this application. Avoid opening untrusted SVG files in other tools without inspection.

## Safety
Original files are not overwritten. Downloads receive an `-edited` suffix. This is an early version: keep backups of important documents.
