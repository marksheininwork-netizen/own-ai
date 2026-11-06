"""Own AI generative image editing backend. Run on a machine with a supported GPU.
Never expose Flask development server to the public internet.
"""
import io
import os
import threading
from flask import Flask, jsonify, request, send_file
from PIL import Image, ImageOps

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
_lock = threading.Lock()
_pipe = None

def pipeline():
    global _pipe
    if _pipe is not None:
        return _pipe
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline, EulerAncestralDiscreteScheduler
    if torch.cuda.is_available():
        device, dtype = "cuda", torch.float16
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device, dtype = "mps", torch.float32
    else:
        raise RuntimeError("A CUDA or Apple Silicon MPS GPU is required for this backend.")
    model = os.getenv("OWN_AI_IMAGE_MODEL", "timbrooks/instruct-pix2pix")
    pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        model, torch_dtype=dtype, safety_checker=None
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    pipe = pipe.to(device)
    _pipe = pipe
    return _pipe

@app.after_request
def cors(response):
    origin = request.headers.get("Origin", "")
    allowed = {x.strip() for x in os.getenv("OWN_AI_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")}
    if origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(ok=True, engine="instruct-pix2pix", model_loaded=_pipe is not None)

@app.route("/api/edit", methods=["OPTIONS", "POST"])
def edit():
    if request.method == "OPTIONS":
        return ("", 204)
    origin = request.headers.get("Origin", "")
    allowed = {x.strip() for x in os.getenv("OWN_AI_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")}
    if origin and origin not in allowed:
        return jsonify(error="Origin not allowed"), 403
    prompt = request.form.get("prompt", "").strip()
    uploaded = request.files.get("image")
    if not prompt or not uploaded:
        return jsonify(error="Image and instructions are required"), 400
    if len(prompt) > 2000:
        return jsonify(error="Instructions are too long"), 400
    if not _lock.acquire(blocking=False):
        return jsonify(error="Model is busy; try again shortly"), 429
    try:
        im = Image.open(uploaded.stream)
        if im.width * im.height > 25000000:
            return jsonify(error="Image exceeds 25 megapixels"), 400
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((512, 512))
        # This model expects dimensions divisible by 8.
        w, h = max(64, (im.width // 8) * 8), max(64, (im.height // 8) * 8)
        im = im.resize((w, h))
        result = pipeline()(prompt=prompt, image=im, num_inference_steps=12,
                            image_guidance_scale=1.5, guidance_scale=7.5).images[0]
        output = io.BytesIO()
        result.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png", as_attachment=False,
                         download_name="own-ai-edited.png")
    except Exception as exc:
        app.logger.exception("Image edit failed")
        return jsonify(error=str(exc)), 500
    finally:
        _lock.release()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7861, debug=False)
