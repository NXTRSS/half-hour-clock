"""When to dispatch pvhp-tick — must match pvhp-optimizer ``pvhp.tick_schedule``."""
from __future__ import annotations

import datetime as dt
import sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Warsaw")
NIGHT_2H_HOURS = frozenset({22, 0, 2, 4})


def should_dispatch(now: dt.datetime) -> tuple[bool, str]:
    loc = now.astimezone(TZ) if now.tzinfo else now.replace(tzinfo=TZ)
    h, m = loc.hour, loc.minute
    if m not in (4, 34):
        return False, f"not :04/:34 Warsaw ({loc:%H:%M})"
    if 6 <= h < 22:
        return True, f"day slot {loc:%H:%M}"
    if m == 34:
        return False, f"night: no :34 ({loc:%H:%M})"
    if h in NIGHT_2H_HOURS:
        return True, f"night slot {loc:%H:%M}"
    return False, f"night: skip hour {h:02d}:04 (2 h cadence)"


def main() -> int:
    ok, why = should_dispatch(dt.datetime.now(dt.timezone.utc))
    print(why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
