from __future__ import annotations

import os
import platform
import subprocess
import time

import psutil

from system.snapshot import CpuInfo, DiskInfo, GpuInfo, MemoryInfo, SystemSnapshot

try:  # optional
    import GPUtil  # type: ignore
except Exception:  # pragma: no cover
    GPUtil = None


def _bytes_to_gb(value: float) -> float:
    return value / (1024**3)


def _cpu_model() -> str:
    system = platform.system().lower()

    if system == "windows":
        try:
            out = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=3,
            ).strip()
            if out:
                return out
        except Exception:
            pass

    if system == "darwin":
        try:
            out = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=3,
            ).strip()
            if out:
                return out
        except Exception:
            pass

    if system == "linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "model name" in line.lower():
                        _, value = line.split(":", 1)
                        value = value.strip()
                        if value:
                            return value
        except Exception:
            pass

    return platform.processor() or platform.machine() or "Unknown CPU"


def _gpu_info() -> GpuInfo | None:
    if GPUtil is None:
        return None

    try:
        gpus = GPUtil.getGPUs()
    except Exception:
        return None

    if not gpus:
        return None

    g = gpus[0]
    load = None
    try:
        load = float(g.load) * 100.0
    except Exception:
        load = None

    mem_used = None
    mem_total = None
    try:
        mem_used = float(getattr(g, "memoryUsed", None))
        mem_total = float(getattr(g, "memoryTotal", None))
    except Exception:
        mem_used, mem_total = None, None

    return GpuInfo(
        name=str(getattr(g, "name", "GPU")),
        load_percent=load,
        memory_used_mb=mem_used,
        memory_total_mb=mem_total,
    )


def _disk_mount() -> str:
    if os.name == "nt":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


def collect_snapshot() -> SystemSnapshot:
    cpu_percent = float(psutil.cpu_percent(interval=None))
    freq = psutil.cpu_freq()
    freq_mhz = float(freq.current) if freq and freq.current else None

    vm = psutil.virtual_memory()
    mem_total_gb = _bytes_to_gb(float(vm.total))
    mem_used_gb = _bytes_to_gb(float(vm.total - vm.available))
    mem_percent = float(vm.percent)

    mount = _disk_mount()
    du = psutil.disk_usage(mount)
    disk_total_gb = _bytes_to_gb(float(du.total))
    disk_used_gb = _bytes_to_gb(float(du.used))
    disk_percent = float(du.percent)

    uptime_seconds = max(0, int(time.time() - float(psutil.boot_time())))

    uname = platform.uname()
    os_name = f"{uname.system} {uname.release}".strip()

    return SystemSnapshot(
        os_name=os_name,
        hostname=uname.node,
        uptime_seconds=uptime_seconds,
        cpu=CpuInfo(
            model=_cpu_model(),
            percent=cpu_percent,
            freq_mhz=freq_mhz,
            cores_logical=int(psutil.cpu_count(logical=True) or 0),
            cores_physical=int(psutil.cpu_count(logical=False) or 0) or None,
        ),
        gpu=_gpu_info(),
        memory=MemoryInfo(
            used_gb=mem_used_gb,
            total_gb=mem_total_gb,
            percent=mem_percent,
        ),
        disk=DiskInfo(
            mount=mount,
            used_gb=disk_used_gb,
            total_gb=disk_total_gb,
            percent=disk_percent,
        ),
    )


def collect_hardware_report(max_lines: int = 220) -> str:
    """
    Best-effort hardware and driver summary.
    """

    snap = collect_snapshot()
    lines: list[str] = []
    lines.append("QuickUtil — System Report")
    lines.append("")
    lines.append(f"OS: {snap.os_name}")
    lines.append(f"Hostname: {snap.hostname}")
    lines.append(f"CPU: {snap.cpu.model}")
    lines.append(f"Cores: {snap.cpu.cores_physical or '—'} physical / {snap.cpu.cores_logical} logical")
    if snap.gpu:
        lines.append(f"GPU: {snap.gpu.name}")
    else:
        lines.append("GPU: Not detected (or unsupported)")
    lines.append(
        f"Memory: {snap.memory.used_gb:.1f} / {snap.memory.total_gb:.1f} GB ({snap.memory.percent:.0f}%)"
    )
    lines.append(f"Disk ({snap.disk.mount}): {snap.disk.used_gb:.1f} / {snap.disk.total_gb:.1f} GB ({snap.disk.percent:.0f}%)")
    lines.append("")

    system = platform.system().lower()
    cmd: list[str] | None = None
    title = None
    if system == "windows":
        title = "Active Drivers (driverquery)"
        cmd = ["driverquery", "/FO", "TABLE"]
    elif system == "linux":
        title = "Loaded Kernel Modules (lsmod)"
        cmd = ["lsmod"]
    elif system == "darwin":
        title = "Loaded Extensions (kextstat)"
        cmd = ["kextstat"]

    if cmd and title:
        lines.append(title + ":")
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=6)
            out_lines = [ln.rstrip() for ln in out.splitlines() if ln.strip()]
            if out_lines:
                lines.extend(out_lines[: max_lines - len(lines)])
            else:
                lines.append("No data returned.")
        except Exception as e:
            lines.append(f"Failed to collect driver info: {e}")

    return "\n".join(lines[:max_lines])

