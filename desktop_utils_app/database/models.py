from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    id: int
    title: str
    start_ts: int
    end_ts: int | None
    notes: str | None


@dataclass(frozen=True)
class Alarm:
    id: int
    label: str
    ts: int
    enabled: bool
    kind: str  # "alarm" | "reminder"
    fired: bool

