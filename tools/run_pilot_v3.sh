#!/usr/bin/env bash
# Pilot v3 queue (D-032): LAT-G-det-reinit x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v3.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v3/logs
for seed in 666 1234; do
  for rep in LAT-G-det-reinit; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" >> "runs/pilot_v3/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" >> "runs/pilot_v3/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
