#!/usr/bin/env bash
# C5 causal controls (D-067): C5b derangements (2 x 2 seeds) then C5a initialization seeds (6 runs, seed 666).
# Sequential and resumable (train_done / eval_summary gates); snapshots pruned after each successful eval.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
export PILOT_CONFIG=configs/pilot_c5.json HF_HUB_DISABLE_SYMLINKS_WARNING=1
mkdir -p runs/pilot_c5/logs
SPECS="LAT-P-rand2:666 LAT-P-rand2:1234 LAT-P-rand3:666 LAT-P-rand3:1234"
for k in 1001 1002; do for a in LAT-P-reinit BN-G-matched BN-G-iv-vm-asp; do SPECS="$SPECS $a-is$k:666"; done; done
for spec in $SPECS; do
  arm="${spec%%:*}"; seed="${spec##*:}"; tag="${arm}__s${seed}"
  if [ -f "runs/pilot_c5/${arm}__train_1h__s${seed}/eval_summary.json" ]; then echo "=== skip $tag (done)"; continue; fi
  echo "=== train pilot_c5 $tag $(date +%T)"; $PY train --rep "$arm" --seed "$seed" >> "runs/pilot_c5/logs/train_$tag.log" 2>&1; echo "exit=$?"
  echo "=== eval  pilot_c5 $tag $(date +%T)";  $PY eval  --rep "$arm" --seed "$seed" >> "runs/pilot_c5/logs/eval_$tag.log" 2>&1; echo "exit=$?"
done
echo "=== done $(date +%T)"
