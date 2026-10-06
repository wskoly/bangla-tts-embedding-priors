#!/usr/bin/env bash
# Pilot v1_1 queue: 3 arms x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v1_1/logs
for seed in 666 1234; do
  for rep in BN-G LAT-G-det LAT-P; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" > "runs/pilot_v1_1/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" > "runs/pilot_v1_1/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
