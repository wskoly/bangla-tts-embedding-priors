#!/usr/bin/env bash
# Pilot v5 queue (D-036): LAT-G-asp x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v5.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v5/logs
for seed in 666 1234; do
  for rep in LAT-G-asp; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" >> "runs/pilot_v5/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" >> "runs/pilot_v5/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
