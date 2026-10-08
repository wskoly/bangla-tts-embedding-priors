@echo off
rem Pilot v4 queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_v4.sh >> runs/pilot_v4_queue.log 2>&1"
