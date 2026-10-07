"""Opt running processes (by name) out of Windows 11 power throttling / EcoQoS (no admin needed).

Background / scheduled-task processes can be placed on efficiency cores at low clocks, which halves
F5 training throughput here (Python per-update overhead is single-threaded). This is a wall-clock fix
only; it does not change any computation. Usage: python tools/disable_power_throttling.py [name ...]
"""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys

PROCESS_SET_INFORMATION, PROCESS_QUERY_LIMITED_INFORMATION = 0x0200, 0x1000
PROCESS_POWER_THROTTLING_CURRENT_VERSION, EXECUTION_SPEED = 1, 0x1
ProcessPowerThrottling = 4


class PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
    _fields_ = [("Version", wt.ULONG), ("ControlMask", wt.ULONG), ("StateMask", wt.ULONG)]


def disable(pid: int) -> bool:
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    h = k32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    st = PROCESS_POWER_THROTTLING_STATE(PROCESS_POWER_THROTTLING_CURRENT_VERSION, EXECUTION_SPEED, 0)
    ok = k32.SetProcessInformation(h, ProcessPowerThrottling, ctypes.byref(st), ctypes.sizeof(st))
    k32.CloseHandle(h)
    return bool(ok)


def pids(name: str) -> list[int]:
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return [int(line.split('","')[1]) for line in out.strip().splitlines() if line.startswith('"')]


if __name__ == "__main__":
    for name in (sys.argv[1:] or ["python", "bash"]):
        for pid in pids(name):
            print(name, pid, "ok" if disable(pid) else "failed")
