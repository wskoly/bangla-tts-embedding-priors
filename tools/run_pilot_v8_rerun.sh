#!/usr/bin/env bash
# C3 reruns (D-054): repeat runs that failed mid-training, from scratch, after the main v8 queue finishes.
set -u
cd "$(dirname "$0")/.."
until grep -q "=== done" runs/pilot_v8_queue.log; do sleep 60; done
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
for spec in "pilot_v8b BN-G-matched-elr30 666"; do
  set -- $spec; tag="$2__s$3"; d="runs/$1/${2}__train_1h__s$3"
  if [ -f "$d/eval_summary.json" ]; then continue; fi
  if [ ! -f "$d/train_done.json" ]; then rm -rf "$d"; fi
  export PILOT_CONFIG=configs/$1.json
  echo "=== rerun train $1 $tag $(date +%T)"; $PY train --rep "$2" --seed "$3" >> "runs/$1/logs/train_${tag}_rerun.log" 2>&1; echo "exit=$?"
  echo "=== rerun eval  $1 $tag $(date +%T)";  $PY eval  --rep "$2" --seed "$3" >> "runs/$1/logs/eval_${tag}_rerun.log" 2>&1; echo "exit=$?"
done
echo "=== rerun done $(date +%T)"
