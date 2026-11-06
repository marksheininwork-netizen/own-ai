# Own AI Local — macOS, Windows and Linux

This is a local web application, not a public cloud deployment. It uses **llama.cpp** with a downloaded instruction model for actual text generation. The self-coded TinyGPT is a separate experimental project.

## 1. Install prerequisites

Install Python 3.10+ and Git. Install **llama.cpp** and make sure the `llama-server` executable is on your PATH.

- **macOS (Apple Silicon or Intel):** install Homebrew, then `brew install llama.cpp`.
- **Windows:** download a llama.cpp release appropriate for your CPU/GPU from https://github.com/ggml-org/llama.cpp/releases and add its folder to PATH. Install Python from python.org and Git for Windows. If GPU support fails, use a CPU build.
- **Linux:** install a llama.cpp build for your hardware from its official instructions at https://github.com/ggml-org/llama.cpp and add `llama-server` to PATH.

On an **M4 MacBook Air**, llama.cpp should use Apple Metal when installed with compatible support. NVIDIA PCs can use CUDA-enabled builds. Other devices can use CPU inference, which is slower. The launch script doesn't force a GPU backend.

## 2. Download and install the app

In macOS/Linux Terminal:

```sh
git clone https://github.com/marksheininwork-netizen/own-ai.git
cd own-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r local_requirements.txt
python start_local.py
```

In Windows PowerShell:

```powershell
git clone https://github.com/marksheininwork-netizen/own-ai.git
cd own-ai
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r local_requirements.txt
.venv\Scripts\python.exe start_local.py
```

The launcher starts llama.cpp and the local web server, then opens **http://127.0.0.1:7860**. First model download may take several minutes. Keep the terminal window running while using the app.

If llama-server isn't on PATH, set `OWN_AI_LLAMA_SERVER` to the full executable path. To select a different compatible Hugging Face GGUF model, pass `--model OWNER/REPO:QUANTIZATION` or set `OWN_AI_MODEL`. For a pre-running model server, use `python start_local.py --no-model`.

## 3. Optional local image generation

Image generation uses Stable Diffusion Turbo through Diffusers. Install:

```sh
python -m pip install -r requirements-images.txt
```

The image pipeline downloads additional model files. CUDA GPUs and Apple Silicon MPS may work depending on memory and package versions. **CPU-only image generation is not supported by the current endpoint.** 8 GB machines may run out of memory; 16–24 GB or more is preferable. The image model may have separate license and usage conditions.

## 4. Tests and troubleshooting

Run `python -m unittest test_local.py` after installing the base requirements. These tests exercise HTTP routes, PDF/DOCX export and validation; they do **not** verify model inference or image quality.

If startup fails, run `llama-server --help` to check installation. If model download fails, choose a supported GGUF model and check the llama.cpp version. If the model server takes more than two minutes to load, start it separately and then run `python start_local.py --no-model`.

This app binds only to 127.0.0.1 and has no authentication. **Do not expose it directly to the internet.** Phone access and account synchronization are not included.

### Current status

Code is committed, but real end-to-end execution on an M4 Mac, Windows PC and Linux PC has not been verified. Chat quality depends on the downloaded model. PDF and Word export generate real files; image generation is optional and hardware-dependent.
