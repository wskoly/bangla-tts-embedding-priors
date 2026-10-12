#!/usr/bin/env bash
# Exploratory long-training check (D-064): SLR37 train_full, 15k updates, LAT-P + LAT-G-det, seed 666.
# Sequential and resumable (train_done / eval_summary gates); snapshots pruned after each successful eval.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
export PILOT_CONFIG=configs/pilot_x1.json HF_HUB_DISABLE_SYMLINKS_WARNING=1
mkdir -p runs/pilot_x1/logs
for arm in LAT-P LAT-G-det; do
  tag="${arm}__s666"
  echo "=== train pilot_x1 $tag $(date +%T)"; $PY train --rep "$arm" --seed 666 --subset train_full >> "runs/pilot_x1/logs/train_$tag.log" 2>&1; echo "exit=$?"
  echo "=== eval  pilot_x1 $tag $(date +%T)";  $PY eval  --rep "$arm" --seed 666 --subset train_full >> "runs/pilot_x1/logs/eval_$tag.log" 2>&1; echo "exit=$?"
done
echo "=== done $(date +%T)"
