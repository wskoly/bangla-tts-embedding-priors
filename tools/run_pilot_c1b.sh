#!/usr/bin/env bash
# C1 full replication (D-061): Rasa Bengali, 8 arms. Order: new arms at seed 666, then all 8 arms at 1234, then 4242
# (seed 666 of the 5 pilot arms comes from pilot_c1a). Sequential and resumable (train_done / eval_summary gates);
# snapshots pruned after each successful eval.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
export PILOT_CONFIG=configs/pilot_c1b.json HF_HUB_DISABLE_SYMLINKS_WARNING=1
mkdir -p runs/pilot_c1b/logs
ALL="LAT-P LAT-P-reinit LAT-P-rand BN-G-matched BN-G-iv-vm-asp LAT-G-det LAT-G-det-reinit LAT-G-asp"
SPECS="$(for a in LAT-G-det LAT-G-det-reinit LAT-G-asp; do echo "$a:666"; done)
$(for s in 1234 4242; do for a in $ALL; do echo "$a:$s"; done; done)"
for spec in $SPECS; do
  arm="${spec%%:*}"; seed="${spec##*:}"; tag="${arm}__s${seed}"
  if [ -f "runs/pilot_c1b/${arm}__train_1h__s${seed}/eval_summary.json" ]; then echo "=== skip $tag (done)"; continue; fi
  echo "=== train pilot_c1b $tag $(date +%T)"; $PY train --rep "$arm" --seed "$seed" >> "runs/pilot_c1b/logs/train_$tag.log" 2>&1; echo "exit=$?"
  echo "=== eval  pilot_c1b $tag $(date +%T)";  $PY eval  --rep "$arm" --seed "$seed" >> "runs/pilot_c1b/logs/eval_$tag.log" 2>&1; echo "exit=$?"
done
echo "=== done $(date +%T)"
