@echo off
rem Pilot v2 (controls) queue launcher for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_pilot_v2.sh >> runs/pilot_v2_queue.log 2>&1"
