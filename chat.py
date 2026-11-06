import torch
from model import TinyGPT

checkpoint = torch.load('checkpoint.pt', map_location='cpu', weights_only=True)
model = TinyGPT(context=checkpoint['context'])
model.load_state_dict(checkpoint['state'])
model.eval()
print('Self-coded AI ready. Type quit to exit.')
while True:
    prompt = input('You: ')
    if prompt.strip().lower() in ('quit', 'exit'): break
    tokens = list(prompt.encode('utf-8')) or [32]
    ids = torch.tensor([tokens], dtype=torch.long)
    out = model.generate(ids, max_new_tokens=120)
    print('AI:', bytes(out[0, len(tokens):].tolist()).decode('utf-8', errors='replace'))
