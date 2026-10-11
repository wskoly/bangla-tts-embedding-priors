@echo off
rem C1 full replication queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_c1b.sh >> runs/pilot_c1b_queue.log 2>&1"
