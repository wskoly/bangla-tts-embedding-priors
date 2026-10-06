"""Small character -> Google-phoneme transformer G2P (trained on the Google bn lexicon).

Output tokens are Google ASCII phonemes plus "." (syllable boundary), so predictions
plug directly into `reps.pron_to_lat_p` / `pron_to_ipa` via `tokens_to_pron`.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch
import torch.nn as nn

from ..lexicon import Pron
from ..normalize import normalize_word

PAD, BOS, EOS, UNK = "<pad>", "<s>", "</s>", "<unk>"


class Vocab:
    def __init__(self, symbols: list[str]):
        self.itos = [PAD, BOS, EOS, UNK] + sorted(set(symbols) - {PAD, BOS, EOS, UNK})
        self.stoi = {s: i for i, s in enumerate(self.itos)}

    def encode(self, seq: list[str]) -> list[int]:
        return [self.stoi.get(s, self.stoi[UNK]) for s in seq]

    def __len__(self) -> int:
        return len(self.itos)


def tokens_to_pron(toks: list[str]) -> Pron:
    sylls, cur = [], []
    for t in toks:
        if t == ".":
            if cur:
                sylls.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        sylls.append(cur)
    return sylls


class PositionalEncoding(nn.Module):
    def __init__(self, d: int, max_len: int = 256):
        super().__init__()
        pe = torch.zeros(max_len, d)
        pos = torch.arange(max_len).unsqueeze(1)
        div = torch.exp(torch.arange(0, d, 2) * (-math.log(10000.0) / d))
        pe[:, 0::2], pe[:, 1::2] = torch.sin(pos * div), torch.cos(pos * div)
        self.register_buffer("pe", pe)

    def forward(self, x):
        return x + self.pe[: x.size(1)]


class G2PTransformer(nn.Module):
    def __init__(self, n_src: int, n_tgt: int, d: int = 256, heads: int = 4, layers: int = 3, ff: int = 1024,
                 dropout: float = 0.1):
        super().__init__()
        self.src_emb, self.tgt_emb = nn.Embedding(n_src, d), nn.Embedding(n_tgt, d)
        self.pos = PositionalEncoding(d)
        self.tf = nn.Transformer(d, heads, layers, layers, ff, dropout, batch_first=True)
        self.out = nn.Linear(d, n_tgt)
        self.d = d

    def forward(self, src, tgt_in):
        src_pad = src == 0
        tgt_mask = self.tf.generate_square_subsequent_mask(tgt_in.size(1), device=src.device)
        h = self.tf(self.pos(self.src_emb(src) * math.sqrt(self.d)), self.pos(self.tgt_emb(tgt_in) * math.sqrt(self.d)),
                    tgt_mask=tgt_mask, src_key_padding_mask=src_pad, tgt_key_padding_mask=tgt_in == 0,
                    memory_key_padding_mask=src_pad)
        return self.out(h)

    @torch.no_grad()
    def greedy(self, src, bos: int, eos: int, max_len: int = 64):
        self.eval()
        ys = torch.full((src.size(0), 1), bos, dtype=torch.long, device=src.device)
        done = torch.zeros(src.size(0), dtype=torch.bool, device=src.device)
        for _ in range(max_len):
            nxt = self.forward(src, ys)[:, -1].argmax(-1)
            nxt = torch.where(done, torch.full_like(nxt, eos), nxt)
            ys = torch.cat([ys, nxt[:, None]], 1)
            done |= nxt == eos
            if done.all():
                break
        return ys[:, 1:]


def decode_rows(rows: list[list[int]], vocab: Vocab) -> list[list[str]]:
    eos = vocab.stoi[EOS]
    out = []
    for row in rows:
        toks = []
        for i in row:
            if i == eos:
                break
            toks.append(vocab.itos[i])
        out.append(toks)
    return out


class G2P:
    """Callable wrapper used by `reps.convert(..., g2p=...)`."""

    def __init__(self, ckpt_dir: Path, device: str | None = None):
        cfg = json.loads((Path(ckpt_dir) / "config.json").read_text(encoding="utf-8"))
        self.src_vocab, self.tgt_vocab = Vocab(cfg["src_symbols"]), Vocab(cfg["tgt_symbols"])
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = G2PTransformer(len(self.src_vocab), len(self.tgt_vocab), **cfg["model"]).to(self.device)
        self.model.load_state_dict(torch.load(Path(ckpt_dir) / "model.pt", map_location=self.device))
        self.cache: dict[str, Pron] = {}

    def predict_tokens(self, words: list[str], batch: int = 512) -> list[list[str]]:
        out = []
        for i in range(0, len(words), batch):
            seqs = [self.src_vocab.encode(list(normalize_word(w))) for w in words[i:i + batch]]
            n = max(len(s) for s in seqs)
            src = torch.tensor([s + [0] * (n - len(s)) for s in seqs], device=self.device)
            rows = self.model.greedy(src, self.tgt_vocab.stoi[BOS], self.tgt_vocab.stoi[EOS]).tolist()
            out += decode_rows(rows, self.tgt_vocab)
        return out

    def __call__(self, word: str) -> Pron:
        if word not in self.cache:
            self.cache[word] = tokens_to_pron(self.predict_tokens([word])[0])
        return self.cache[word]
