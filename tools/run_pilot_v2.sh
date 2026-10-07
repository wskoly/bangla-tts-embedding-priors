#!/usr/bin/env bash
# Pilot v2 queue (controls, D-028): 3 control arms x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v2.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v2/logs
for seed in 666 1234; do
  for rep in BN-G-matched LAT-P-reinit LAT-P-rand; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" >> "runs/pilot_v2/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" >> "runs/pilot_v2/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
