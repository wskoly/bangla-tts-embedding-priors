#!/usr/bin/env bash
# C3 queue (D-046): (a) third seed 4242 for the 10 hypothesis arms, then (b) embedding-LR x3/x30 sweep, seeds 666/1234.
# Sequential and resumable; snapshots pruned after each successful eval.
set -u
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe -X utf8 -W ignore -m src.train.pilot"
run() {  # config version rep seed
  export PILOT_CONFIG=configs/$1.json; mkdir -p runs/$1/logs; tag="$2__s$3"
  echo "=== train $1 $tag $(date +%T)"; $PY train --rep "$2" --seed "$3" >> "runs/$1/logs/train_$tag.log" 2>&1; echo "exit=$?"
  echo "=== eval  $1 $tag $(date +%T)";  $PY eval  --rep "$2" --seed "$3" >> "runs/$1/logs/eval_$tag.log" 2>&1; echo "exit=$?"
}
for rep in LAT-P LAT-P-reinit LAT-P-rand BN-G-matched BN-G-iv BN-G-iv-vm BN-G-iv-vm-asp LAT-G-det LAT-G-det-reinit LAT-G-asp; do
  run pilot_v8a "$rep" 4242
done
for m in 30 3; do for seed in 666 1234; do for arm in BN-G-matched BN-G-iv-vm-asp LAT-P-reinit; do
  run pilot_v8b "$arm-elr$m" "$seed"
done; done; done
echo "=== done $(date +%T)"
