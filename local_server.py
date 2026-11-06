"""Local Own AI web app. Run after starting a llama.cpp server on port 9931."""
from flask import Flask, request, jsonify, send_from_directory, send_file
from pathlib import Path
from io import BytesIO
import requests
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
LLM = "http://127.0.0.1:9931/v1"

@app.get("/")
def home():
    return send_from_directory(ROOT, "local.html")

@app.get("/api/health")
def health():
    try:
        response = requests.get(LLM + "/models", timeout=3)
        response.raise_for_status()
        return jsonify(ready=True, models=response.json().get("data", []))
    except requests.RequestException:
        return jsonify(ready=False, error="Start llama.cpp with: llama serve -hf ggml-org/gemma-3-1b-it-GGUF:Q4_K_M")

@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages or len(messages) > 50:
        return jsonify(error="Provide 1 to 50 messages"), 400
    clean = []
    for item in messages:
        if not isinstance(item, dict) or item.get("role") not in ("user", "assistant") or not isinstance(item.get("content"), str):
            return jsonify(error="Invalid message"), 400
        clean.append({"role": item["role"], "content": item["content"][:12000]})
    try:
        models = requests.get(LLM + "/models", timeout=8).json().get("data", [])
        if not models:
            return jsonify(error="No model loaded in llama.cpp"), 503
        result = requests.post(LLM + "/chat/completions",
            json={"model": models[0]["id"], "messages": [{"role": "system", "content": "You are a helpful, accurate assistant. Say when you are uncertain."}] + clean, "stream": False, "max_tokens": 800},
            timeout=180)
        result.raise_for_status()
        answer = result.json()["choices"][0]["message"]["content"]
        return jsonify(answer=answer)
    except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
        return jsonify(error="Model unavailable or generation failed: " + str(exc)[:200]), 503

@app.post("/api/document")
def document():
    payload = request.get_json(silent=True) or {}
    title = str(payload.get("title", "Untitled"))[:150]
    body = str(payload.get("body", ""))[:100000]
    fmt = payload.get("format")
    output = BytesIO()
    if fmt == "docx":
        doc = Document()
        doc.add_heading(title, 0)
        for line in body.splitlines():
            doc.add_paragraph(line)
        doc.save(output)
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ext = "docx"
    elif fmt == "pdf":
        styles = getSampleStyleSheet()
        story = [Paragraph(escape(title), styles["Title"]), Spacer(1, 12)]
        for line in body.splitlines():
            story.append(Paragraph(escape(line) or " ", styles["BodyText"]))
            story.append(Spacer(1, 5))
        SimpleDocTemplate(output).build(story)
        mimetype = "application/pdf"
        ext = "pdf"
    else:
        return jsonify(error="format must be pdf or docx"), 400
    output.seek(0)
    return send_file(output, mimetype=mimetype, as_attachment=True, download_name="own-ai-document." + ext)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False)
