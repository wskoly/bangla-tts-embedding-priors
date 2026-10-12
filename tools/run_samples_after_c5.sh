#!/usr/bin/env bash
# D-068: wait for the C5 queue to finish (GPU free), then synthesize the sample-page stress sentences.
set -u
cd "$(dirname "$0")/.."
until grep -q "=== done" runs/pilot_c5_queue.log 2>/dev/null; do sleep 120; done
echo "=== samples start $(date +%T)"
.venv/Scripts/python.exe -X utf8 -W ignore tools/samples_synth.py; echo "exit=$?"
echo "=== samples done $(date +%T)"
