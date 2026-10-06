"""Aggregate the 1-hour F5 probe runs into a cost table (D4 5.8, decision D-020).

Reads runs/probe/*/probe_stats.json + config.json; writes docs/reports/probe_v1.md.
Updates per epoch are counted exactly with F5's own DynamicBatchSampler over each subset's
real (trimmed, 24 kHz) durations, so no packing-efficiency assumption is needed.

Usage: python tools/summarize_probe_v1.py
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

from torch.utils.data import SequentialSampler

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "runs/probe"
SPLITS = ROOT / "data/derived/splits/v1"
AUDIO_INDEX = ROOT / "data/derived/audio24k_v1/index.tsv"
FRAMES_PER_S = 24000 / 256
SUBSETS = ["train_0.25h", "train_0.5h", "train_1h", "train_full"]
# Runs measured while other GPU work was active (earlier session: ASR runs / downloads; lower power and
# clocks, 39 % util). Superseded by the *_rerun runs under the same conditions as p3-p6; kept for transparency.
SUPERSEDED = {"p1_bn-g_b2000": "p1b_bn-g_b2000_rerun", "p2_bn-g_b4000": "p2b_bn-g_b4000_rerun"}


class _Frames:
    """Minimal data source exposing get_frame_len, as DynamicBatchSampler expects."""

    def __init__(self, durations: list[float]):
        self.d = durations

    def __len__(self):
        return len(self.d)

    def get_frame_len(self, i):
        return self.d[i] * FRAMES_PER_S


def subset_durations() -> dict[str, list[float]]:
    with open(AUDIO_INDEX, encoding="utf-8") as f:
        dur = {r["utt_id"]: float(r["duration_s"]) for r in csv.DictReader(f, delimiter="\t")}
    out = {}
    for s in SUBSETS:
        with open(SPLITS / f"{s}.tsv", encoding="utf-8") as f:
            out[s] = [dur[r["utt_id"]] for r in csv.DictReader(f, delimiter="\t")]
    return out


def updates_per_epoch(durations: list[float], batch_frames: int, max_samples: int = 64, seed: int = 666) -> int:
    from f5_tts.model.dataset import DynamicBatchSampler
    sampler = SequentialSampler(_Frames(durations))
    return len(DynamicBatchSampler(sampler, batch_frames, max_samples=max_samples, random_seed=seed,
                                   drop_residual=False))


def update_timing(run_dir: Path, grad_accum: int) -> dict:
    """Robust per-update timing from probe_updates.tsv (one row per micro-batch).

    The F5 Trainer iterates a separate skip_first_batches DataLoader in epoch 0 and the original one
    from epoch 1, so a second worker pool is spawned once at the first epoch boundary (Windows spawn:
    tens of seconds). That one-off stall is reported separately instead of being averaged in.
    """
    with open(run_dir / "probe_updates.tsv", encoding="utf-8") as f:
        t = [float(r["t"]) for r in csv.DictReader(f, delimiter="\t")]
    gaps = [b - a for a, b in zip(t, t[1:])][5:]  # skip the first few (allocator / cudnn warm-up)
    stalls = [g for g in gaps if g > 5.0]
    normal = sorted(g for g in gaps if g <= 5.0)
    med = normal[len(normal) // 2] if normal else float("nan")
    return {"median_s_per_micro": med, "median_s_per_update": med * grad_accum,
            "p90_s_per_micro": normal[int(.9 * (len(normal) - 1))] if normal else float("nan"),
            "stall_s_total": sum(stalls), "n_stalls": len(stalls)}


def main() -> int:
    runs = []
    for d in sorted(PROBE.iterdir()):
        st, cf = d / "probe_stats.json", d / "config.json"
        if d.is_dir() and st.exists() and cf.exists():
            runs.append((d.name, json.loads(cf.read_text(encoding="utf-8")), json.loads(st.read_text(encoding="utf-8"))))
    durs = subset_durations()
    lines = ["# 1-hour F5 memory/throughput probe (v1)", "",
             "Hardware: RTX 5070 Ti 16 GB (WDDM, ~2 GB used by the desktop), torch 2.11 cu128, bf16 (accelerate), "
             "AdamW (fused), official F5 Trainer, frame batching, `train_1h` subset. Steady-state timing excludes the "
             "first 5 micro-batches; s/update is the MEDIAN; one-off stalls (> 5 s, the second DataLoader worker pool "
             "spawned by the F5 Trainer at the first epoch boundary) are listed separately. Updates/epoch counted with "
             "F5's DynamicBatchSampler (micro-batches; divide by grad-accum for updates).", "",
             "| run | arm | frames/micro-batch | grad-accum | act. ckpt | updates | median s/update (p90 s/micro) | "
             "one-off stalls s | micro-batches/epoch (1 h) | audio h per wall-h | "
             "peak VRAM alloc / reserved GB | nvidia-smi peak GB | GPU util % | power W | CPU % | host RSS GB | "
             "time to 1st update s | full ckpt GB / save s |", "|" + "---|" * 18]
    timing = {}
    for name, cf, st in runs:
        tm = timing[name] = update_timing(PROBE / name, cf["grad_accum"])
        spu = tm["median_s_per_update"]
        mpe = updates_per_epoch(durs["train_1h"], cf["batch_frames"])
        aph = (sum(durs["train_1h"]) / mpe * cf["grad_accum"]) / spu  # audio s per update / s per update
        label = f"~~{name}~~ (superseded by {SUPERSEDED[name]})" if name in SUPERSEDED else name
        lines.append(
            f"| {label} | {cf['rep']} | {cf['batch_frames']} | {cf['grad_accum']} | "
            f"{'yes' if cf['checkpoint_activations'] else 'no'} | {st['updates']} | {spu:.3f} ({tm['p90_s_per_micro']:.3f}) | "
            f"{tm['stall_s_total']:.0f} | {mpe} | {aph:.1f} | "
            f"{st['peak_vram_allocated_gb']:.2f} / {st['peak_vram_reserved_gb']:.2f} | "
            f"{st['nvidia_smi_peak_mem_gb']:.2f} | {st['gpu_util_mean']:.0f} | {st['power_w_mean']:.0f} | "
            f"{st['cpu_pct_mean']:.0f} | {st['host_rss_peak_gb']:.2f} | {st['time_to_first_update_s']:.0f} | "
            f"{st['checkpoint_file_gb']:.2f} / {st['checkpoint_save_s']:.0f} |")
    lines += ["", "## Cost per subset (training only, at the measured median rate)", "",
              "Fixed per-run overhead (not included below): time to first update + one-off worker-pool stall + "
              "checkpoint saves (full checkpoint ≈ 5 GB, ~45 s each).", "",
              "| run config | subset | audio h (trimmed) | updates / epoch | min / epoch | min / 1k updates |",
              "|---|---|---|---|---|---|"]
    for name, cf, st in runs:
        if cf["rep"] != "BN-G" or name in SUPERSEDED:
            continue
        spu = timing[name]["median_s_per_update"]
        for s in SUBSETS:
            upe = math.ceil(updates_per_epoch(durs[s], cf["batch_frames"]) / cf["grad_accum"])
            lines.append(f"| {name} | {s} | {sum(durs[s]) / 3600:.3f} | {upe} | {upe * spu / 60:.2f} | "
                         f"{1000 * spu / 60:.1f} |")
    out = ROOT / "docs/reports/probe_v1.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
