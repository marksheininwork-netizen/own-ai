"""Cross-platform launcher for the local Own AI web UI and llama.cpp."""
import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "ggml-org/gemma-3-1b-it-GGUF:Q4_K_M"

def executable():
    override = os.environ.get("OWN_AI_LLAMA_SERVER")
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"OWN_AI_LLAMA_SERVER does not exist: {path}")
        return str(path)
    for name in ("llama-server", "llama-server.exe"):
        found = shutil.which(name)
        if found:
            return found
    raise FileNotFoundError(
        "llama-server not found. Install llama.cpp and add llama-server to PATH, "
        "or set OWN_AI_LLAMA_SERVER to the executable path. See LOCAL_SETUP.md."
    )

def server_ready():
    try:
        with urllib.request.urlopen("http://127.0.0.1:9931/v1/models", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("OWN_AI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--no-model", action="store_true", help="Connect to an existing llama.cpp server")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    print(f"Own AI | {platform.system()} {platform.machine()} | Python {platform.python_version()}", flush=True)
    child = None
    try:
        if not server_ready() and not args.no_model:
            binary = executable()
            command = [binary, "-hf", args.model, "--port", "9931", "--host", "127.0.0.1"]
            print("Starting llama.cpp. First launch may download a model.", flush=True)
            child = subprocess.Popen(command, cwd=str(ROOT))
            for _ in range(120):
                if server_ready():
                    break
                if child.poll() is not None:
                    raise RuntimeError(f"llama-server exited with code {child.returncode}")
                time.sleep(1)
            if not server_ready():
                raise TimeoutError("Model server did not become ready within 120 seconds. Model download may need more time; check the server output.")
        elif args.no_model and not server_ready():
            print("Warning: model server not detected. Documents will work, chat will not.", flush=True)
        if not args.no_browser:
            import webbrowser
            webbrowser.open("http://127.0.0.1:7860")
        from local_server import app
        print("Open http://127.0.0.1:7860", flush=True)
        app.run(host="127.0.0.1", port=7860, debug=False, use_reloader=False)
    finally:
        if child and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                child.kill()

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, TimeoutError) as exc:
        print("Startup error:", exc, file=sys.stderr)
        sys.exit(1)
