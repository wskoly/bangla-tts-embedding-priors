#!/usr/bin/env bash
# 1-hour memory/throughput probe grid (D4 5.8). Sequential so measurements do not compete for the GPU.
# Runs whose probe_stats.json already exists are skipped (resumable after interruption).
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.f5_train --subset train_1h --probe --num-workers 4"
run() {
  name=$1; shift
  if [ -f "runs/probe/$name/probe_stats.json" ]; then echo "=== $name already done"; return; fi
  echo "=== $name $(date +%T)"; $PY --run "runs/probe/$name" "$@" > "runs/probe/$name.log" 2>&1; echo "exit=$? $(date +%T)"
}
mkdir -p runs/probe
run p1_bn-g_b2000      --rep BN-G  --batch-frames 2000 --max-updates 300
run p2_bn-g_b4000      --rep BN-G  --batch-frames 4000 --max-updates 300
run p3_bn-g_b8000      --rep BN-G  --batch-frames 8000 --max-updates 120
run p4_bn-g_b8000_ckpt --rep BN-G  --batch-frames 8000 --max-updates 200 --checkpoint-activations
run p5_lat-p_b4000     --rep LAT-P --batch-frames 4000 --max-updates 300
run p6_bn-g_b4000_ga2  --rep BN-G  --batch-frames 4000 --max-updates 150 --grad-accum 2
