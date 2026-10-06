"""Train and evaluate the OOV G2P on the Google bn lexicon (D4 step 3.4).

Split: words 90/5/5 (seed 20261006), first listed pronunciation per word.
Metrics on the held-out test words (greedy decoding):
  WER      = % words whose predicted phoneme sequence (incl. syllable dots) is not exact
  WER-nodot= same, ignoring syllable boundaries
  PER      = phoneme edit distance / reference length, ignoring syllable boundaries

Usage:
    python -m src.bnrep.g2p.train --out runs/g2p/v1 --report docs/reports/g2p_v1.md \
        --oov-out data/derived/g2p/slr37_oov_g2p_v1.tsv
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import random
import time
from pathlib import Path

import torch
import torch.nn.functional as F

from ..lexicon import LEX_DIR, ROOT
from ..normalize import normalize_word
from ..reps import convert, pron_to_ipa, pron_to_lat_p
from .model import BOS, EOS, G2P, G2PTransformer, Vocab, decode_rows, tokens_to_pron

SEED = 20261006
MODEL_CFG = {"d": 256, "heads": 4, "layers": 3, "ff": 1024, "dropout": 0.1}


def load_pairs() -> list[tuple[str, list[str]]]:
    seen, pairs = set(), []
    for line in (LEX_DIR / "lexicon.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 2:
            continue
        w = normalize_word(cols[0])
        if w in seen:
            continue
        seen.add(w)
        pairs.append((w, cols[1].split()))
    return pairs


def edit_distance(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def batches(data, src_v, tgt_v, bs, shuffle, rng):
    idx = list(range(len(data)))
    if shuffle:
        rng.shuffle(idx)
    for i in range(0, len(idx), bs):
        chunk = [data[j] for j in idx[i:i + bs]]
        src = [src_v.encode(list(w)) for w, _ in chunk]
        tgt = [[tgt_v.stoi[BOS]] + tgt_v.encode(p) + [tgt_v.stoi[EOS]] for _, p in chunk]
        ns, nt = max(map(len, src)), max(map(len, tgt))
        yield (torch.tensor([s + [0] * (ns - len(s)) for s in src]),
               torch.tensor([t + [0] * (nt - len(t)) for t in tgt]), chunk)


def evaluate(model, data, src_v, tgt_v, device):
    errs = errs_nodot = ph_err = ph_ref = 0
    preds = []
    for src, _, chunk in batches(data, src_v, tgt_v, 512, False, None):
        rows = model.greedy(src.to(device), tgt_v.stoi[BOS], tgt_v.stoi[EOS]).tolist()
        for (w, ref), hyp in zip(chunk, decode_rows(rows, tgt_v)):
            r_nd, h_nd = [x for x in ref if x != "."], [x for x in hyp if x != "."]
            errs += hyp != ref
            errs_nodot += h_nd != r_nd
            ph_err += edit_distance(r_nd, h_nd)
            ph_ref += len(r_nd)
            preds.append((w, ref, hyp))
    n = len(data)
    return {"n": n, "WER": 100 * errs / n, "WER_nodot": 100 * errs_nodot / n, "PER": 100 * ph_err / ph_ref}, preds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--oov-out", type=Path, required=True)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--lr", type=float, default=5e-4)
    args = ap.parse_args()

    rng = random.Random(SEED)
    torch.manual_seed(SEED)
    pairs = load_pairs()
    rng.shuffle(pairs)
    n = len(pairs)
    train, dev, test = pairs[: int(.9 * n)], pairs[int(.9 * n): int(.95 * n)], pairs[int(.95 * n):]
    src_v = Vocab([c for w, _ in pairs for c in w])
    tgt_v = Vocab([t for _, p in pairs for t in p])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = G2PTransformer(len(src_v), len(tgt_v), **MODEL_CFG).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.98), weight_decay=0.01)
    steps = args.epochs * ((len(train) + args.bs - 1) // args.bs)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=steps, pct_start=0.05)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "config.json").write_text(json.dumps(
        {"src_symbols": src_v.itos, "tgt_symbols": tgt_v.itos, "model": MODEL_CFG, "seed": SEED,
         "split_sizes": [len(train), len(dev), len(test)]}, ensure_ascii=False), encoding="utf-8")

    best, best_ep, log = float("inf"), -1, []
    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train()
        tot = cnt = 0
        for src, tgt, _ in batches(train, src_v, tgt_v, args.bs, True, rng):
            src, tgt = src.to(device), tgt.to(device)
            with torch.autocast(device, dtype=torch.bfloat16, enabled=device == "cuda"):
                logits = model(src, tgt[:, :-1])
            loss = F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), tgt[:, 1:].reshape(-1),
                                   ignore_index=0, label_smoothing=0.1)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            tot, cnt = tot + loss.item(), cnt + 1
        if ep % 5 == 0 or ep == args.epochs:
            m, _ = evaluate(model, dev, src_v, tgt_v, device)
            log.append({"epoch": ep, "train_loss": tot / cnt, **{f"dev_{k}": v for k, v in m.items()}})
            print(f"ep {ep:3d} loss {tot / cnt:.3f} dev WER {m['WER']:.2f} WER_nodot {m['WER_nodot']:.2f} "
                  f"PER {m['PER']:.2f}  ({time.time() - t0:.0f}s)", flush=True)
            if m["WER"] < best:
                best, best_ep = m["WER"], ep
                torch.save(model.state_dict(), args.out / "model.pt")

    g2p = G2P(args.out, device=device)
    test_m, test_preds = evaluate(g2p.model, test, src_v, tgt_v, device)
    errors = [(w, " ".join(r), " ".join(h)) for w, r, h in test_preds if r != h][:40]

    # predictions for SLR37 out-of-lexicon words (for human verification)
    manifest = ROOT / "data" / "derived" / "slr37_bn_bd" / "manifest.tsv"
    with open(manifest, encoding="utf-8", newline="") as f:
        texts = [r["text"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)]
    oov = collections.Counter(w for t in texts for w in convert("LAT-P", t).oov)
    words = [w for w, _ in oov.most_common()]
    toks = g2p.predict_tokens(words) if words else []
    args.oov_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.oov_out, "w", encoding="utf-8", newline="\n") as f:
        f.write("word\tcount\tg2p_google\tLAT-P\tIPA-P\tverified_google\tnote\n")
        for w, tk in zip(words, toks):
            pron = tokens_to_pron(tk)
            f.write(f"{w}\t{oov[w]}\t{' '.join(tk)}\t{pron_to_lat_p(pron)}\t{pron_to_ipa(pron)}\t\t\n")

    lines = ["# G2P v1 (character transformer on the Google bn lexicon)", "",
             f"Split (words): train {len(train)}, dev {len(dev)}, test {len(test)}; seed {SEED}; "
             f"model {MODEL_CFG}; best dev epoch {best_ep}; device {device}.", "",
             "| set | words | WER % | WER (ignore syllable dots) % | PER % |", "|---|---|---|---|---|",
             f"| test | {test_m['n']} | {test_m['WER']:.2f} | {test_m['WER_nodot']:.2f} | {test_m['PER']:.2f} |", "",
             "Dev curve:", "", "| epoch | train loss | dev WER | dev WER_nodot | dev PER |", "|---|---|---|---|---|",
             *[f"| {r['epoch']} | {r['train_loss']:.3f} | {r['dev_WER']:.2f} | {r['dev_WER_nodot']:.2f} | {r['dev_PER']:.2f} |"
               for r in log],
             "", f"SLR37 out-of-lexicon words: {len(words)} types / {sum(oov.values())} tokens; "
                 f"predictions in `{args.oov_out.as_posix()}` (column `verified_google` for human review).", "",
             "Sample test errors (word | reference | prediction):", "",
             *[f"- {w} | `{r}` | `{h}`" for w, r, h in errors]]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(test_m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
