# Recreate the project environment on Windows (tested 2026-10-06, RTX 5070 Ti, driver 610.88).
# Usage (from repo root):  powershell -ExecutionPolicy Bypass -File tools\setup_env.ps1

$ErrorActionPreference = "Stop"

# 1. FFmpeg. The static build gives the CLI; the shared build provides the DLLs torchcodec needs.
#    torchaudio >= 2.9 loads audio through torchcodec, which requires shared FFmpeg 4-9 DLLs on PATH.
winget install --id Gyan.FFmpeg -e --silent --accept-source-agreements --accept-package-agreements
winget install --id Gyan.FFmpeg.Shared -e --silent --accept-source-agreements --accept-package-agreements

# 2. Python 3.11 venv + PyTorch built for CUDA 12.8 (Blackwell / sm_120 support).
uv venv -p 3.11 .venv
uv pip install --python .venv\Scripts\python.exe torch torchaudio --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv\Scripts\python.exe f5-tts

# 3. Make the shared-FFmpeg DLL folder visible to every Python process in the venv (.pth hook).
$ffbin = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Directory |
    Where-Object Name -like "Gyan.FFmpeg.Shared*" |
    ForEach-Object { Get-ChildItem $_.FullName -Recurse -Filter "avcodec-*.dll" | Select-Object -First 1 } |
    ForEach-Object { $_.DirectoryName }
if (-not $ffbin) { throw "Shared FFmpeg DLLs not found" }
$pth = ".venv\Lib\site-packages\zz_ffmpeg_shared_path.pth"
"import os; _d=r`"$ffbin`"; os.environ[`"PATH`"]=_d+os.pathsep+os.environ.get(`"PATH`",`"`") if os.path.isdir(_d) and _d not in os.environ.get(`"PATH`",`"`") else os.environ.get(`"PATH`",`"`")" |
    Out-File -Encoding ascii $pth

# 4. Sanity checks
.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
.venv\Scripts\f5-tts_infer-cli.exe --model F5TTS_v1_Base --gen_text "The quick brown fox jumps over the lazy dog." --output_dir runs\sanity --output_file en_sanity.wav
