"""IANA timezone choices for the notification preferences form
(Milestone 15.1, Phase 1) - replaces the free-text timezone field with
a constrained dropdown while still storing/validating a real IANA
identifier internally (`NotificationPreference.timezone` is unchanged).
"""

import zoneinfo
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

# `zoneinfo.available_timezones()` includes deprecated aliases and
# non-geographic buckets (Etc/GMT+12, posix/..., right/..., Factory)
# that would clutter a dropdown meant for humans to search - keep
# "Region/City" names plus the one bare "UTC".
_EXCLUDED_PREFIXES = ("Etc/", "posix/", "right/", "SystemV/")


def _offset_label(tz_name):
    now = datetime.now(ZoneInfo(tz_name))
    offset = now.utcoffset()
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"UTC{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@lru_cache(maxsize=1)
def get_timezone_choices():
    """[(iana_name, "iana_name (UTC+06:00)")], sorted by name. Cached
    for the process lifetime - the *set* of IANA zone names doesn't
    change at runtime, only their current UTC offset would (DST), and
    a dropdown refreshing that twice a year is an acceptable tradeoff
    against recomputing ~400 offsets on every page render."""
    names = sorted(
        name
        for name in zoneinfo.available_timezones()
        if name == "UTC" or ("/" in name and not name.startswith(_EXCLUDED_PREFIXES))
    )
    return [(name, f"{name} ({_offset_label(name)})") for name in names]
