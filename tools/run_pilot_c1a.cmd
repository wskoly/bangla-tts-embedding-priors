@echo off
rem C1 pilot queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_c1a.sh >> runs/pilot_c1a_queue.log 2>&1"
