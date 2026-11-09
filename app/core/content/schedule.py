"""P1: the content calendar. Dates are plain calendar dates; "today" is the date in America/Jamaica (UTC-5, no daylight saving),
never the server's UTC date. Weeks start on Monday (the same week the growth log uses).
The serverless entry passes only the URL path, so the month/week is part of the path: /calendar/month/2026-11."""

import re
from datetime import date, datetime, timedelta, timezone

from core.content.common import Invalid, iso_date

TZ_NAME = "America/Jamaica"
try:
    from zoneinfo import ZoneInfo
    JAMAICA = ZoneInfo(TZ_NAME)
except Exception:                                   # no tz database on the host: Jamaica has been UTC-5 all year since 1983
    JAMAICA = timezone(timedelta(hours=-5), TZ_NAME)

_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_CLOSED = ("PUBLISHED", "ARCHIVED")
clock = lambda: datetime.now(timezone.utc)          # replaced in tests


def today() -> date:
    return clock().astimezone(JAMAICA).date()


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _epi(r, now_day: date):
    d = dict(r)
    pd = d["planned_date"]
    d["planned_date"] = pd.isoformat() if pd else None
    d["overdue"] = bool(pd and pd < now_day and d["status"] not in _CLOSED)
    return d


def _days(conn, start: date, end: date, month: int | None):
    """Every date from start to end inclusive, each with its episodes."""
    now_day = today()
    rows = conn.execute("SELECT id, series_id, code, title, status, planned_date FROM episodes "
                        "WHERE planned_date BETWEEN ? AND ? ORDER BY planned_date, id", (start, end)).fetchall()
    by_day = {}
    for r in rows:
        by_day.setdefault(r["planned_date"], []).append(_epi(r, now_day))
    out, d = [], start
    while d <= end:
        out.append({"date": d.isoformat(), "in_month": month is None or d.month == month, "is_today": d == now_day,
                    "episodes": by_day.get(d, [])})
        d += timedelta(days=1)
    return out


def _unscheduled(conn):
    rows = conn.execute("SELECT id, series_id, code, title, status FROM episodes "
                        "WHERE planned_date IS NULL AND status NOT IN ('PUBLISHED','ARCHIVED') ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def current() -> dict:
    t = today()
    return {"today": t.isoformat(), "timezone": TZ_NAME, "month": t.strftime("%Y-%m"), "week_start": monday(t).isoformat()}


def month(conn, ym: str) -> dict:
    m = _MONTH.match(ym or "")
    if not m or not 2000 <= int(m.group(1)) <= 2100 or not 1 <= int(m.group(2)) <= 12:
        raise Invalid("month must be YYYY-MM (years 2000 to 2100)")
    y, mo = int(m.group(1)), int(m.group(2))
    first = date(y, mo, 1)
    last = (date(y + (mo == 12), mo % 12 + 1, 1)) - timedelta(days=1)
    start, end = monday(first), last + timedelta(days=6 - last.weekday())
    return {"view": "month", "month": ym, "timezone": TZ_NAME, "today": today().isoformat(), "start": start.isoformat(), "end": end.isoformat(),
            "days": _days(conn, start, end, mo), "unscheduled": _unscheduled(conn)}


def week(conn, day: str) -> dict:
    d = iso_date(day, "week")
    if d is None or not 2000 <= d.year <= 2100:
        raise Invalid("week must be a date YYYY-MM-DD (years 2000 to 2100)")
    start = monday(d)
    return {"view": "week", "week_start": start.isoformat(), "timezone": TZ_NAME, "today": today().isoformat(),
            "start": start.isoformat(), "end": (start + timedelta(days=6)).isoformat(),
            "days": _days(conn, start, start + timedelta(days=6), None), "unscheduled": _unscheduled(conn)}
