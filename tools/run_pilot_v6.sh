#!/usr/bin/env bash
# Pilot v6 queue (D-039): data-size curves, 4 arms x 3 new subsets x 2 seeds (train_1h reused from v1_1/v4).
# Sequential and resumable; snapshots pruned after each successful eval (prune_after_eval).
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v6.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v6/logs
for seed in 666 1234; do
  for subset in train_0.25h train_0.5h train_full; do
    for rep in BN-G LAT-G-det LAT-P BN-G-iv-vm-asp; do
      tag="${rep}__${subset}__s${seed}"
      echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" --subset "$subset" >> "runs/pilot_v6/logs/train_$tag.log" 2>&1; echo "exit=$?"
      echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" --subset "$subset" >> "runs/pilot_v6/logs/eval_$tag.log" 2>&1; echo "exit=$?"
    done
  done
done
echo "=== done $(date +%T)"
