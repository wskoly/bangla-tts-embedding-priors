@echo off
rem Pilot v6 queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_v6.sh >> runs/pilot_v6_queue.log 2>&1"
