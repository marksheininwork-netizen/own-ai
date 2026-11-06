# Generative image editing backend

The GitHub Pages website is static and cannot run a GPU model itself. This optional backend performs **real prompt-guided image editing** with the open-weight InstructPix2Pix diffusion model.

## Run locally

Use Python 3.11 or 3.12 (recommended), and a machine with Apple Silicon MPS or NVIDIA CUDA and enough memory. On macOS:

```sh
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-ai.txt
python image_server.py
```

First generation downloads model weights (several GB), which can take time. Run a web server for the frontend:

```sh
python3 -m http.server 8000
```

Visit http://localhost:8000, select **Generative AI**, enter backend URL `http://127.0.0.1:7861`, upload or paste an image, enter instructions, and generate.

## Remote / public web deployment

To use the GitHub Pages website, host this backend on a separate HTTPS GPU server, configure `OWN_AI_ALLOWED_ORIGINS=https://marksheininwork-netizen.github.io`, and enter the backend HTTPS URL in the site. Do **not** expose the development Flask server publicly: add authentication, rate limiting, HTTPS, and a production WSGI server first. Browser HTTPS pages cannot reliably access local HTTP endpoints due to mixed-content/private-network restrictions.

## Limitations

- Not a free unlimited hosted AI service. There is **no per-edit API fee** when running your own model, but GPU hardware, bandwidth and electricity cost money.
- InstructPix2Pix changes visual content based on a prompt but is **not reliable for exact text replacement** or maintaining typography.
- On-device inference is resource-intensive, especially on lower-RAM Macs.
- This code has not been end-to-end tested on the user's machine or deployed to a GPU host.
- The backend is a starting point, not a hardened public service.
