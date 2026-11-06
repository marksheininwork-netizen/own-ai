import argparse
from pathlib import Path
import torch
from model import TinyGPT

p = argparse.ArgumentParser(description="Train Own AI's byte-level Transformer")
p.add_argument("--steps", type=int, default=2000)
p.add_argument("--batch", type=int, default=16)
p.add_argument("--context", type=int, default=128)
p.add_argument("--data", default="data.txt")
p.add_argument("--eval-interval", type=int, default=100)
p.add_argument("--eval-batches", type=int, default=10)
p.add_argument("--output", default="checkpoint.pt")
a = p.parse_args()
if a.steps < 1 or a.batch < 1 or a.context < 8 or a.eval_batches < 1 or a.eval_interval < 1:
    p.error("Steps, batch, evaluation settings must be positive; context >= 8")
torch.manual_seed(42)
device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
raw = Path(a.data).read_bytes()
minimum = 2 * (a.context + 2)
if len(raw) < minimum:
    raise ValueError(f"Dataset too small for independent validation. Need at least {minimum} bytes, got {len(raw)}.")
data = torch.tensor(list(raw), dtype=torch.long)
cut = int(len(data) * .9)
cut = min(max(cut, a.context + 2), len(data) - a.context - 2)
train_data, valid_data = data[:cut], data[cut:]
print(f"device={device} training_bytes={len(train_data)} validation_bytes={len(valid_data)}", flush=True)
model = TinyGPT(context=a.context).to(device)
optim = torch.optim.AdamW(model.parameters(), lr=3e-4)

def batch(source):
    high = len(source) - a.context
    if high < 1:
        raise ValueError("Not enough data for context length")
    idx = torch.randint(0, high, (a.batch,))
    x = torch.stack([source[int(i):int(i)+a.context] for i in idx]).to(device)
    y = torch.stack([source[int(i)+1:int(i)+a.context+1] for i in idx]).to(device)
    return x, y

@torch.no_grad()
def evaluate():
    model.eval()
    results = {}
    for name, source in (("train", train_data), ("valid", valid_data)):
        losses = []
        for _ in range(a.eval_batches):
            x, y = batch(source)
            _, loss = model(x, y)
            losses.append(loss.item())
        results[name] = sum(losses) / len(losses)
    return results

best = float("inf")
for step in range(1, a.steps + 1):
    model.train()
    x, y = batch(train_data)
    _, loss = model(x, y)
    optim.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
    optim.step()
    if step % a.eval_interval == 0 or step == 1 or step == a.steps:
        scores = evaluate()
        print(f"step={step} train={scores['train']:.4f} valid={scores['valid']:.4f}", flush=True)
        if scores["valid"] < best:
            best = scores["valid"]
            torch.save({"state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                        "context": a.context, "step": step, "validation_loss": best}, a.output)
            print(f"Saved best checkpoint to {a.output}", flush=True)
print(f"Training complete. Best validation loss: {best:.4f}")
