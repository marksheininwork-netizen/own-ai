# Own AI: local mode

This is a local web application. It does not use a paid API. It uses an existing downloaded instruction model through llama.cpp, **not** your untrained TinyGPT weights.

On a Mac, install llama.cpp using Homebrew:

```sh
brew install llama.cpp
git clone https://github.com/marksheininwork-netizen/own-ai.git
cd own-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r local_requirements.txt
```

In terminal window 1, start a local model (first run downloads model weights; check llama.cpp compatibility with the selected GGUF model):

```sh
llama-server -hf ggml-org/gemma-3-1b-it-GGUF:Q4_K_M --port 9931
```

In terminal window 2, from the repo with the venv activated:

```sh
python local_server.py
```

Open **http://127.0.0.1:7860** in a browser on the same Mac.

This provides actual local chat inference, plus PDF and DOCX document creation. The self-coded TinyGPT remains experimental. Image generation is implemented as an optional Stable Diffusion Turbo endpoint. Install additional packages with `pip install torch diffusers transformers accelerate safetensors` before starting the Flask server. It requires a supported GPU and downloads large model files. This path is **not tested** on your Mac, and some Apple Silicon configurations may encounter memory or compatibility issues. Running on a phone or publicly accessible website requires a separately secured deployment; do not expose the local server to the internet without authentication and access controls.

If the model download fails, choose a supported GGUF repository from the llama.cpp documentation and replace the `-hf` argument. No automatic model testing has been performed.
