# 1-hour F5 memory/throughput probe (v1)

Hardware: RTX 5070 Ti 16 GB (WDDM, ~2 GB used by the desktop), torch 2.11 cu128, bf16 (accelerate), AdamW (fused), official F5 Trainer, frame batching, `train_1h` subset. Steady-state timing excludes the first 5 micro-batches; s/update is the MEDIAN; one-off stalls (> 5 s, the second DataLoader worker pool spawned by the F5 Trainer at the first epoch boundary) are listed separately. Updates/epoch counted with F5's DynamicBatchSampler (micro-batches; divide by grad-accum for updates).

| run | arm | frames/micro-batch | grad-accum | act. ckpt | updates | median s/update (p90 s/micro) | one-off stalls s | micro-batches/epoch (1 h) | audio h per wall-h | peak VRAM alloc / reserved GB | nvidia-smi peak GB | GPU util % | power W | CPU % | host RSS GB | time to 1st update s | full ckpt GB / save s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ~~p1_bn-g_b2000~~ (superseded by p1b_bn-g_b2000_rerun) | BN-G | 2000 | 1 | no | 300 | 0.273 (0.307) | 75 | 203 | 68.4 | 8.28 / 8.66 | 10.99 | 16 | 73 | 44 | 9.17 | 63 | 5.02 / 52 |
| p1b_bn-g_b2000_rerun | BN-G | 2000 | 1 | no | 300 | 0.133 (0.151) | 21 | 203 | 140.5 | 8.28 / 8.66 | 9.36 | 41 | 110 | 50 | 9.57 | 23 | 5.02 / 41 |
| ~~p2_bn-g_b4000~~ (superseded by p2b_bn-g_b4000_rerun) | BN-G | 4000 | 1 | no | 300 | 0.267 (0.302) | 31 | 95 | 149.5 | 11.15 / 14.07 | 15.40 | 39 | 121 | 62 | 9.31 | 35 | 5.02 / 44 |
| p2b_bn-g_b4000_rerun | BN-G | 4000 | 1 | no | 300 | 0.200 (0.213) | 21 | 95 | 199.6 | 11.15 / 14.07 | 14.77 | 87 | 206 | 86 | 9.61 | 23 | 5.02 / 47 |
| p3_bn-g_b8000 | BN-G | 8000 | 1 | no | 120 | 0.615 (0.673) | 294 | 46 | 134.0 | 15.68 / 19.66 | 15.57 | 92 | 93 | 102 | 15.17 | 43 | 5.02 / 43 |
| p4_bn-g_b8000_ckpt | BN-G | 8000 | 1 | yes | 200 | 0.484 (0.524) | 21 | 46 | 170.3 | 7.39 / 7.76 | 8.46 | 75 | 189 | 54 | 10.35 | 25 | 5.02 / 47 |
| p5_lat-p_b4000 | LAT-P | 4000 | 1 | no | 300 | 0.199 (0.212) | 21 | 95 | 200.6 | 11.15 / 14.07 | 14.78 | 91 | 210 | 84 | 9.64 | 23 | 5.02 / 50 |
| p6_bn-g_b4000_ga2 | BN-G | 4000 | 2 | no | 150 | 0.386 (0.209) | 21 | 95 | 206.8 | 12.43 / 14.98 | 15.54 | 92 | 207 | 86 | 9.70 | 23 | 5.02 / 48 |

## Cost per subset (training only, at the measured median rate)

Fixed per-run overhead (not included below): time to first update + one-off worker-pool stall + checkpoint saves (full checkpoint ≈ 5 GB, ~45 s each).

| run config | subset | audio h (trimmed) | updates / epoch | min / epoch | min / 1k updates |
|---|---|---|---|---|---|
| p1b_bn-g_b2000_rerun | train_0.25h | 0.265 | 51 | 0.11 | 2.2 |
| p1b_bn-g_b2000_rerun | train_0.5h | 0.527 | 102 | 0.23 | 2.2 |
| p1b_bn-g_b2000_rerun | train_1h | 1.053 | 203 | 0.45 | 2.2 |
| p1b_bn-g_b2000_rerun | train_full | 1.659 | 321 | 0.71 | 2.2 |
| p2b_bn-g_b4000_rerun | train_0.25h | 0.265 | 24 | 0.08 | 3.3 |
| p2b_bn-g_b4000_rerun | train_0.5h | 0.527 | 48 | 0.16 | 3.3 |
| p2b_bn-g_b4000_rerun | train_1h | 1.053 | 95 | 0.32 | 3.3 |
| p2b_bn-g_b4000_rerun | train_full | 1.659 | 149 | 0.50 | 3.3 |
| p3_bn-g_b8000 | train_0.25h | 0.265 | 12 | 0.12 | 10.3 |
| p3_bn-g_b8000 | train_0.5h | 0.527 | 23 | 0.24 | 10.3 |
| p3_bn-g_b8000 | train_1h | 1.053 | 46 | 0.47 | 10.3 |
| p3_bn-g_b8000 | train_full | 1.659 | 73 | 0.75 | 10.3 |
| p4_bn-g_b8000_ckpt | train_0.25h | 0.265 | 12 | 0.10 | 8.1 |
| p4_bn-g_b8000_ckpt | train_0.5h | 0.527 | 23 | 0.19 | 8.1 |
| p4_bn-g_b8000_ckpt | train_1h | 1.053 | 46 | 0.37 | 8.1 |
| p4_bn-g_b8000_ckpt | train_full | 1.659 | 73 | 0.59 | 8.1 |
| p6_bn-g_b4000_ga2 | train_0.25h | 0.265 | 12 | 0.08 | 6.4 |
| p6_bn-g_b4000_ga2 | train_0.5h | 0.527 | 24 | 0.15 | 6.4 |
| p6_bn-g_b4000_ga2 | train_1h | 1.053 | 48 | 0.31 | 6.4 |
| p6_bn-g_b4000_ga2 | train_full | 1.659 | 75 | 0.48 | 6.4 |
