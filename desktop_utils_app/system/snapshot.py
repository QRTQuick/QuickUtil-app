from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CpuInfo:
    model: str
    percent: float
    freq_mhz: float | None
    cores_logical: int
    cores_physical: int | None


@dataclass(frozen=True)
class GpuInfo:
    name: str
    load_percent: float | None
    memory_used_mb: float | None
    memory_total_mb: float | None


@dataclass(frozen=True)
class MemoryInfo:
    used_gb: float
    total_gb: float
    percent: float


@dataclass(frozen=True)
class DiskInfo:
    mount: str
    used_gb: float
    total_gb: float
    percent: float


@dataclass(frozen=True)
class SystemSnapshot:
    os_name: str
    hostname: str
    uptime_seconds: int
    cpu: CpuInfo
    gpu: GpuInfo | None
    memory: MemoryInfo
    disk: DiskInfo

