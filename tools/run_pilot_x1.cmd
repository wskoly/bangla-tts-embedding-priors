@echo off
rem Exploratory long-training queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_x1.sh >> runs/pilot_x1_queue.log 2>&1"
