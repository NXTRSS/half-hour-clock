"""When to dispatch pvhp-tick — must match pvhp-optimizer ``pvhp.tick_schedule``."""
from __future__ import annotations

import datetime as dt
import sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Warsaw")
NIGHT_2H_HOURS = frozenset({22, 0, 2, 4})


def is_day_hour(h: int) -> bool:
    return 6 <= h < 22


def should_dispatch(now: dt.datetime) -> tuple[bool, str]:
    loc = now.astimezone(TZ) if now.tzinfo else now.replace(tzinfo=TZ)
    h, m = loc.hour, loc.minute
    if m not in (0, 30):
        return False, f"not :00/:30 Warsaw ({loc:%H:%M})"
    if is_day_hour(h):
        return True, f"day {loc:%H:%M}"
    if m == 30:
        return False, f"night: no :30 ({loc:%H:%M})"
    if h in NIGHT_2H_HOURS:
        return True, f"night {loc:%H:%M}"
    return False, f"night: skip hour {h:02d}:00 (2 h cadence)"


def main() -> int:
    now = dt.datetime.now(TZ)
    ok, why = should_dispatch(now)
    print("dispatch" if ok else "skip", why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
