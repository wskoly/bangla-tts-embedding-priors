#!/usr/bin/env bash
# Pilot v7 queue (D-043): embedding-LR x10 arms (3) x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v7.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v7/logs
for seed in 666 1234; do
  for rep in BN-G-matched-elr10 BN-G-iv-vm-asp-elr10 LAT-P-reinit-elr10; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" >> "runs/pilot_v7/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" >> "runs/pilot_v7/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
