#!/usr/bin/env bash
# C1 feasibility pilot (D-055/D-057): Rasa Bengali, 5 arms, seed 666, recipe identical to pilot_v8a.
# Sequential and resumable (train_done / eval_summary gates); snapshots pruned after each successful eval.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
export PILOT_CONFIG=configs/pilot_c1a.json HF_HUB_DISABLE_SYMLINKS_WARNING=1
mkdir -p runs/pilot_c1a/logs
for arm in LAT-P LAT-P-reinit LAT-P-rand BN-G-matched BN-G-iv-vm-asp; do
  tag="${arm}__s666"
  echo "=== train pilot_c1a $tag $(date +%T)"; $PY train --rep "$arm" --seed 666 >> "runs/pilot_c1a/logs/train_$tag.log" 2>&1; echo "exit=$?"
  echo "=== eval  pilot_c1a $tag $(date +%T)";  $PY eval  --rep "$arm" --seed 666 >> "runs/pilot_c1a/logs/eval_$tag.log" 2>&1; echo "exit=$?"
done
echo "=== done $(date +%T)"
