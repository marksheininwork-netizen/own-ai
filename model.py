import torch
from torch import nn
import torch.nn.functional as F

class Attention(nn.Module):
    def __init__(self, width, heads, dropout):
        super().__init__()
        assert width % heads == 0
        self.heads, self.dim = heads, width // heads
        self.qkv = nn.Linear(width, 3 * width)
        self.proj = nn.Linear(width, width)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        b, t, c = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q, k, v = [a.view(b, t, self.heads, self.dim).transpose(1, 2) for a in (q, k, v)]
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=self.drop.p if self.training else 0)
        return self.proj(y.transpose(1, 2).contiguous().view(b, t, c))

class Block(nn.Module):
    def __init__(self, width, heads, dropout):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(width), nn.LayerNorm(width)
        self.attn = Attention(width, heads, dropout)
        self.ff = nn.Sequential(nn.Linear(width, 4 * width), nn.GELU(), nn.Linear(4 * width, width), nn.Dropout(dropout))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        return x + self.ff(self.ln2(x))

class TinyGPT(nn.Module):
    def __init__(self, vocab_size=256, context=128, width=128, heads=4, layers=3, dropout=0.1):
        super().__init__()
        self.context = context
        self.token = nn.Embedding(vocab_size, width)
        self.pos = nn.Embedding(context, width)
        self.blocks = nn.Sequential(*(Block(width, heads, dropout) for _ in range(layers)))
        self.norm = nn.LayerNorm(width)
        self.head = nn.Linear(width, vocab_size, bias=False)

    def forward(self, ids, targets=None):
        b, t = ids.shape
        if t > self.context:
            raise ValueError('Sequence exceeds context window')
        positions = torch.arange(t, device=ids.device)
        x = self.blocks(self.token(ids) + self.pos(positions))
        logits = self.head(self.norm(x))
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1)) if targets is not None else None
        return logits, loss

    @torch.no_grad()
    def generate(self, ids, max_new_tokens=120, temperature=0.8):
        self.eval()
        for _ in range(max_new_tokens):
            logits, _ = self(ids[:, -self.context:])
            probs = F.softmax(logits[:, -1, :] / max(temperature, 0.05), dim=-1)
            nxt = torch.multinomial(probs, 1)
            ids = torch.cat((ids, nxt), dim=1)
        return ids
