@echo off
rem D-068 sample synthesis after C5 for Windows Task Scheduler (survives terminal session end).
"C:\Program Files\Git\usr\bin\bash.exe" -lc "cd /d/Personal/Research/tts-research && bash tools/run_samples_after_c5.sh >> runs/samples_queue.log 2>&1"
