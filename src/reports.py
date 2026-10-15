from datetime import date, timedelta, datetime
from src.github_store import load_month


def _parse(hhmm: str) -> datetime:
    h, m = hhmm.split(":")
    return datetime(2000, 1, 1, int(h), int(m))


def shift_minutes(s: dict) -> int:
    return max(0, int((_parse(s["eind"]) - _parse(s["begin"])).total_seconds() // 60))


def fmt_hm(minutes: int) -> str:
    sign = "-" if minutes < 0 else ""
    m = abs(int(minutes))
    return f"{sign}{m // 60}:{m % 60:02d}"


def period_bounds(mode, ref=None, start=None, end=None):
    if mode == "Dag":
        return ref, ref
    if mode == "Week":
        mon = ref - timedelta(days=ref.weekday())
        return mon, mon + timedelta(days=6)
    if mode == "Maand":
        first = ref.replace(day=1)
        nxt = first.replace(year=first.year + 1, month=1) if first.month == 12 \
            else first.replace(month=first.month + 1)
        return first, nxt - timedelta(days=1)
    return start, end


def load_range(start: date, end: date):
    out = []
    cache = {}
    d = start
    while d <= end:
        key = (d.year, d.month)
        if key not in cache:
            cache[key] = load_month(d)
        day = cache[key].get(d.isoformat())
        if day:
            for s in day.get("shifts", []):
                out.append((d, s))
        d += timedelta(days=1)
    return out


def aggregate(rows, group_by: str):
    buckets: dict = {}
    for d, s in rows:
        if group_by == "Dag":
            key = d.strftime("%d/%m/%Y")
            sort = d
        elif group_by == "Week":
            iso = d.isocalendar()
            key = f"{iso[0]}-W{iso[1]:02d}"
            sort = d - timedelta(days=d.weekday())
        elif group_by == "Maand":
            key = d.strftime("%m/%Y")
            sort = d.replace(day=1)
        else:
            key = s.get("type", "Standaard")
            sort = key
        b = buckets.setdefault(key, {"key": key, "minutes": 0, "count": 0, "sort": sort})
        b["minutes"] += shift_minutes(s)
        b["count"] += 1
    return [buckets[k] for k in sorted(buckets, key=lambda x: buckets[x]["sort"])]
