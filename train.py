import argparse
from pathlib import Path
import torch
from model import TinyGPT

p = argparse.ArgumentParser()
p.add_argument('--steps', type=int, default=500)
p.add_argument('--batch', type=int, default=16)
p.add_argument('--context', type=int, default=128)
p.add_argument('--data', default='data.txt')
a = p.parse_args()
torch.manual_seed(42)
if torch.cuda.is_available(): device = 'cuda'
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(): device = 'mps'
else: device = 'cpu'
raw = Path(a.data).read_bytes()
if len(raw) < a.context + 2: raise ValueError('Add more training text to data.txt')
data = torch.tensor(list(raw), dtype=torch.long)
cut = max(a.context + 2, int(len(data) * 0.9))
train = data[:cut]
valid = data[cut:] if len(data) - cut > a.context + 1 else train
model = TinyGPT(context=a.context).to(device)
optim = torch.optim.AdamW(model.parameters(), lr=3e-4)
def batch(source):
    idx = torch.randint(0, len(source) - a.context - 1, (a.batch,))
    x = torch.stack([source[i:i+a.context] for i in idx]).to(device)
    y = torch.stack([source[i+1:i+a.context+1] for i in idx]).to(device)
    return x, y
for step in range(a.steps):
    model.train()
    x, y = batch(train)
    _, loss = model(x, y)
    optim.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optim.step()
    if step % 50 == 0 or step == a.steps-1:
        model.eval()
        with torch.no_grad():
            vx, vy = batch(valid)
            _, val = model(vx, vy)
        print(f'step {step:4d} train={loss.item():.3f} val={val.item():.3f}', flush=True)
torch.save({'state': model.cpu().state_dict(), 'context': a.context}, 'checkpoint.pt')
print('Saved checkpoint.pt')
