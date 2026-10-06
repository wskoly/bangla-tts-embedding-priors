import sys, time
sys.path.insert(0, r"D:\Personal\Research\tts-research")
from torch.utils.data import DataLoader, SequentialSampler
from f5_tts.model.dataset import CustomDataset, DynamicBatchSampler, collate_fn
from src.train.f5_train import build_dataset, load_vocab, MEL

if __name__ == "__main__":
    nw = int(sys.argv[1])
    vm, _ = load_vocab("BN-G")
    hf, dur = build_dataset("BN-G", "train_1h", vm)
    ds = CustomDataset(hf, durations=dur, preprocessed_mel=False, **MEL)
    bs = DynamicBatchSampler(SequentialSampler(ds), 4000, max_samples=64, random_seed=666, drop_residual=False)
    dl = DataLoader(ds, collate_fn=collate_fn, num_workers=nw, pin_memory=True, persistent_workers=nw > 0, batch_sampler=bs)
    for ep in range(2):
        bs.set_epoch(ep)
        t0 = time.time(); last = t0; gaps = []
        for i, b in enumerate(dl):
            now = time.time(); gaps.append(now - last); last = now
        print(f"workers={nw} epoch {ep}: batches {i+1} total {time.time()-t0:.1f}s first-batch {gaps[0]:.1f}s median {sorted(gaps)[len(gaps)//2]:.3f}s max-after-first {max(gaps[1:]):.2f}s", flush=True)


def bench_accelerate(nw: int) -> None:
    """Same pipeline, but prepared by accelerate like the F5 Trainer does."""
    from accelerate import Accelerator
    vm, _ = load_vocab("BN-G")
    hf, dur = build_dataset("BN-G", "train_1h", vm)
    ds = CustomDataset(hf, durations=dur, preprocessed_mel=False, **MEL)
    bs = DynamicBatchSampler(SequentialSampler(ds), 4000, max_samples=64, random_seed=666, drop_residual=False)
    dl = DataLoader(ds, collate_fn=collate_fn, num_workers=nw, pin_memory=True, persistent_workers=True, batch_sampler=bs)
    acc = Accelerator()
    acc.even_batches = False
    pdl = acc.prepare(dl)
    print("prepared persistent_workers:", getattr(pdl, "persistent_workers", None), type(pdl).__name__, flush=True)
    for ep in range(3):
        if hasattr(pdl, "batch_sampler") and hasattr(pdl.batch_sampler, "set_epoch"):
            pdl.batch_sampler.set_epoch(ep)
        t0 = time.time()
        gaps, last = [], t0
        for b in pdl:
            now = time.time(); gaps.append(now - last); last = now
        print(f"accelerate workers={nw} epoch {ep}: total {time.time()-t0:.1f}s first-batch {gaps[0]:.1f}s", flush=True)
