# Own AI — self-coded Transformer

A small GPT-style neural network implemented with PyTorch tensor operations. The Transformer layers and training loop are written in this repository. No Ollama, pretrained model, or paid AI API is used.

**Status:** Experimental source code. This model has not been trained or benchmarked as part of this repository upload. The included tiny dataset is a smoke test, not enough for a useful assistant.

## Quick start (macOS / Linux)

Install Python 3.10+ and Git.

```bash
git clone https://github.com/marksheininwork-netizen/own-ai.git
cd own-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python train.py --steps 500
python chat.py
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.

## Files

- `model.py` — decoder-only Transformer with causal multi-head attention
- `train.py` — training loop, validation-loss reporting, checkpoint saving
- `chat.py` — interactive terminal text generation
- `data.txt` — tiny sample corpus
- `requirements.txt` — PyTorch dependency
- `.gitignore` — excludes local checkpoints and environments

## How it learns

The model predicts the next UTF-8 byte from previous bytes. Its tokenizer is byte-level with 256 possible values. Parameters start randomly initialized and are trained on the provided corpus.

Replace `data.txt` with a much larger text dataset you have rights to use. Longer training and better data are necessary for coherent responses.

## Hosting

GitHub hosts the source code, not model inference. Run the model on your own computer. A public chat website requires a continuously running backend with enough compute.

## License

No license has been added. All rights reserved by default unless the repository owner later chooses a license.
