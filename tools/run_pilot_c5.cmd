@echo off
rem C5 causal-controls queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_c5.sh >> runs/pilot_c5_queue.log 2>&1"
