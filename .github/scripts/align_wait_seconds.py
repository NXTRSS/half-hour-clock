"""Seconds to sleep until next :04 or :34 Europe/Warsaw (max 900 for one job)."""
from __future__ import annotations

import datetime as dt
import sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Warsaw")
MAX = 900


def wait_seconds(now: dt.datetime | None = None) -> int:
    now = now or dt.datetime.now(TZ)
    loc = now.astimezone(TZ) if now.tzinfo else now.replace(tzinfo=TZ)
    m, s = loc.minute, loc.second
    if m < 4:
        wait = (4 - m) * 60 - s
    elif m < 34:
        wait = (34 - m) * 60 - s
    else:
        wait = (60 - m + 4) * 60 - s
    if wait > MAX:
        return 0
    return max(0, wait)


if __name__ == "__main__":
    print(wait_seconds())
