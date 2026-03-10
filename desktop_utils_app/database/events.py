from __future__ import annotations

import calendar as _cal
from datetime import date, datetime, timedelta

from database.db import Database
from database.models import Event


def _to_ts(dt: datetime) -> int:
    # For app UX, treat naive datetimes as local time.
    return int(dt.timestamp())


def _from_ts(ts: int) -> datetime:
    return datetime.fromtimestamp(int(ts))


def add_event(db: Database, *, title: str, start: datetime, end: datetime | None, notes: str | None) -> int:
    start_ts = _to_ts(start)
    end_ts = _to_ts(end) if end else None
    with db.session() as conn:
        cur = conn.execute(
            "INSERT INTO events(title, start_ts, end_ts, notes) VALUES(?, ?, ?, ?);",
            (title.strip(), start_ts, end_ts, notes),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_event(
    db: Database,
    *,
    event_id: int,
    title: str,
    start: datetime,
    end: datetime | None,
    notes: str | None,
) -> None:
    start_ts = _to_ts(start)
    end_ts = _to_ts(end) if end else None
    with db.session() as conn:
        conn.execute(
            "UPDATE events SET title=?, start_ts=?, end_ts=?, notes=? WHERE id=?;",
            (title.strip(), start_ts, end_ts, notes, int(event_id)),
        )
        conn.commit()


def delete_event(db: Database, *, event_id: int) -> None:
    with db.session() as conn:
        conn.execute("DELETE FROM events WHERE id=?;", (int(event_id),))
        conn.commit()


def get_event(db: Database, *, event_id: int) -> Event | None:
    with db.session() as conn:
        row = conn.execute("SELECT id, title, start_ts, end_ts, notes FROM events WHERE id=?;", (int(event_id),)).fetchone()
    if not row:
        return None
    return Event(int(row["id"]), str(row["title"]), int(row["start_ts"]), int(row["end_ts"]) if row["end_ts"] is not None else None, row["notes"])


def list_events_for_day(db: Database, *, day: date) -> list[Event]:
    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)
    start_ts = int(start.timestamp())
    end_ts = int(end.timestamp())

    with db.session() as conn:
        rows = conn.execute(
            """
            SELECT id, title, start_ts, end_ts, notes
            FROM events
            WHERE start_ts >= ? AND start_ts < ?
            ORDER BY start_ts ASC;
            """,
            (start_ts, end_ts),
        ).fetchall()

    return [
        Event(
            int(r["id"]),
            str(r["title"]),
            int(r["start_ts"]),
            int(r["end_ts"]) if r["end_ts"] is not None else None,
            r["notes"],
        )
        for r in rows
    ]


def event_days_in_month(db: Database, *, year: int, month: int) -> set[date]:
    first = date(year, month, 1)
    last_day = _cal.monthrange(year, month)[1]
    last = date(year, month, last_day)

    start_ts = int(datetime(first.year, first.month, first.day).timestamp())
    end_ts = int(datetime(last.year, last.month, last.day).timestamp()) + 86400

    with db.session() as conn:
        rows = conn.execute(
            "SELECT start_ts FROM events WHERE start_ts >= ? AND start_ts < ?;",
            (start_ts, end_ts),
        ).fetchall()

    days: set[date] = set()
    for r in rows:
        dt = _from_ts(int(r["start_ts"]))
        days.add(dt.date())
    return days


def next_event(db: Database, *, after_ts: int | None = None) -> Event | None:
    after_ts = int(after_ts) if after_ts is not None else int(datetime.now().timestamp())
    with db.session() as conn:
        row = conn.execute(
            """
            SELECT id, title, start_ts, end_ts, notes
            FROM events
            WHERE start_ts >= ?
            ORDER BY start_ts ASC
            LIMIT 1;
            """,
            (after_ts,),
        ).fetchone()

    if not row:
        return None
    return Event(
        int(row["id"]),
        str(row["title"]),
        int(row["start_ts"]),
        int(row["end_ts"]) if row["end_ts"] is not None else None,
        row["notes"],
    )
