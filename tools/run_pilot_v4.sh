#!/usr/bin/env bash
# Pilot v4 queue (D-034): BN-G encoding-path arms (3) x 2 seeds on train_1h, train then eval, sequential and resumable.
set -u
cd "$(dirname "$0")/.."
export PILOT_CONFIG=configs/pilot_v4.json
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
mkdir -p runs/pilot_v4/logs
for seed in 666 1234; do
  for rep in BN-G-iv BN-G-iv-vm BN-G-iv-vm-asp; do
    tag="${rep}__s${seed}"
    echo "=== train $tag $(date +%T)"; $PY train --rep "$rep" --seed "$seed" >> "runs/pilot_v4/logs/train_$tag.log" 2>&1; echo "exit=$?"
    echo "=== eval  $tag $(date +%T)";  $PY eval  --rep "$rep" --seed "$seed" >> "runs/pilot_v4/logs/eval_$tag.log" 2>&1; echo "exit=$?"
  done
done
echo "=== done $(date +%T)"
