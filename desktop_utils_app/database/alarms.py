from __future__ import annotations

from datetime import datetime

from database.db import Database
from database.models import Alarm


def add_alarm(db: Database, *, label: str, when: datetime, kind: str = "alarm", enabled: bool = True) -> int:
    ts = int(when.timestamp())
    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO alarms(label, ts, enabled, kind, fired) VALUES(?, ?, ?, ?, 0);",
            (label.strip(), ts, 1 if enabled else 0, kind),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_alarm(
    db: Database,
    *,
    alarm_id: int,
    label: str,
    when: datetime,
    kind: str,
    enabled: bool,
) -> None:
    ts = int(when.timestamp())
    with db.session() as conn:
        conn.execute(
            "UPDATE alarms SET label=?, ts=?, enabled=?, kind=?, fired=0 WHERE id=?;",
            (label.strip(), ts, 1 if enabled else 0, kind, int(alarm_id)),
        )
        conn.commit()


def delete_alarm(db: Database, *, alarm_id: int) -> None:
    with db.session() as conn:
        conn.execute("DELETE FROM alarms WHERE id=?;", (int(alarm_id),))
        conn.commit()


def set_alarm_enabled(db: Database, *, alarm_id: int, enabled: bool) -> None:
    with db.session() as conn:
        conn.execute("UPDATE alarms SET enabled=? WHERE id=?;", (1 if enabled else 0, int(alarm_id)))
        conn.commit()


def mark_alarm_fired(db: Database, *, alarm_id: int, fired: bool = True) -> None:
    with db.session() as conn:
        conn.execute("UPDATE alarms SET fired=? WHERE id=?;", (1 if fired else 0, int(alarm_id)))
        conn.commit()


def list_alarms(db: Database) -> list[Alarm]:
    with db.session() as conn:
        rows = conn.execute(
            "SELECT id, label, ts, enabled, kind, fired FROM alarms ORDER BY ts ASC;",
        ).fetchall()

    return [
        Alarm(
            id=int(r["id"]),
            label=str(r["label"]),
            ts=int(r["ts"]),
            enabled=bool(int(r["enabled"])),
            kind=str(r["kind"]),
            fired=bool(int(r["fired"])),
        )
        for r in rows
    ]


def get_alarm(db: Database, *, alarm_id: int) -> Alarm | None:
    with db.session() as conn:
        r = conn.execute("SELECT id, label, ts, enabled, kind, fired FROM alarms WHERE id=?;", (int(alarm_id),)).fetchone()
    if not r:
        return None
    return Alarm(
        id=int(r["id"]),
        label=str(r["label"]),
        ts=int(r["ts"]),
        enabled=bool(int(r["enabled"])),
        kind=str(r["kind"]),
        fired=bool(int(r["fired"])),
    )


def due_alarms(db: Database, *, now_ts: int) -> list[Alarm]:
    with db.session() as conn:
        rows = conn.execute(
            """
            SELECT id, label, ts, enabled, kind, fired
            FROM alarms
            WHERE enabled=1 AND fired=0 AND ts <= ?
            ORDER BY ts ASC;
            """,
            (int(now_ts),),
        ).fetchall()

    return [
        Alarm(
            id=int(r["id"]),
            label=str(r["label"]),
            ts=int(r["ts"]),
            enabled=True,
            kind=str(r["kind"]),
            fired=bool(int(r["fired"])),
        )
        for r in rows
    ]


def next_alarm(db: Database, *, after_ts: int) -> Alarm | None:
    with db.session() as conn:
        r = conn.execute(
            """
            SELECT id, label, ts, enabled, kind, fired
            FROM alarms
            WHERE enabled=1 AND fired=0 AND ts >= ?
            ORDER BY ts ASC
            LIMIT 1;
            """,
            (int(after_ts),),
        ).fetchone()

    if not r:
        return None
    return Alarm(
        id=int(r["id"]),
        label=str(r["label"]),
        ts=int(r["ts"]),
        enabled=bool(int(r["enabled"])),
        kind=str(r["kind"]),
        fired=bool(int(r["fired"])),
    )
