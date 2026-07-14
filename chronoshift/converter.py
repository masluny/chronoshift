"""Core time zone conversion logic."""

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo, available_timezones


def format_compact(source_time: time, from_tz: str, to_tz: str) -> str:
    """One-line compact format: '14:30 WAR → 08:30 NYC (-6h)'.

    Uses the last 3 characters of the city name as a short label.
    """
    result = convert_time(source_time, from_tz, to_tz)
    from_label = from_tz.split("/")[-1][:3].upper()
    to_label = to_tz.split("/")[-1][:3].upper()
    src = datetime.combine(datetime.now().date(), source_time).strftime("%H:%M")
    dst = result.strftime("%H:%M")
    offset = compute_offset_label(from_tz, to_tz)
    return f"{src} {from_label} → {dst} {to_label} ({offset})"


def list_timezones() -> list[str]:
    """Return all available IANA time zone names, sorted."""
    return sorted(available_timezones())


def parse_time(time_str: str) -> time:
    """Parse a time string in HH:MM or HH:MM:SS format.

    Raises:
        ValueError: If the string can't be parsed as a valid time.
    """
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M%p", "%I:%M %p"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse '{time_str}' — expected HH:MM, HH:MM:SS, or 12h format (e.g. 2:30PM)"
    )


def convert_time(
    source_time: time,
    from_tz: str,
    to_tz: str,
    date: datetime | None = None,
) -> datetime:
    """Convert a time from one timezone to another.

    Args:
        source_time: The time to convert.
        from_tz: IANA timezone name for the source (e.g. 'UTC').
        to_tz: IANA timezone name for the target (e.g. 'US/Eastern').
        date: Optional date context for DST accuracy. Defaults to today.

    Returns:
        A timezone-aware datetime in the target zone.

    Raises:
        KeyError: If either timezone name is invalid.
    """
    if date is None:
        date = datetime.now()

    source_dt = datetime.combine(date.date(), source_time, tzinfo=ZoneInfo(from_tz))
    return source_dt.astimezone(ZoneInfo(to_tz))


def format_time(dt: datetime, fmt: str = "24h") -> str:
    """Format a datetime for display.

    Args:
        dt: The datetime to format.
        fmt: Either '24h' or '12h'.

    Returns:
        Formatted time string.
    """
    if fmt == "12h":
        return dt.strftime("%I:%M %p").lstrip("0")
    return dt.strftime("%H:%M")


def compute_offset_label(from_tz: str, to_tz: str) -> str:
    """Compute a human-readable offset label like '6h behind' or '3h ahead'.

    Uses the current moment to determine offset difference.
    """
    now = datetime.now(tz=ZoneInfo("UTC"))
    from_offset = now.astimezone(ZoneInfo(from_tz)).utcoffset()
    to_offset = now.astimezone(ZoneInfo(to_tz)).utcoffset()

    if from_offset is None or to_offset is None:
        return ""

    diff_seconds = (to_offset - from_offset).total_seconds()
    diff_hours = diff_seconds / 3600

    if diff_hours == 0:
        return "same time"
    elif diff_hours > 0:
        return f"{diff_hours:+.0f}h ahead".lstrip("+")
    else:
        return f"{abs(diff_hours):.0f}h behind"


def format_diff(
    source_time: time,
    from_tz: str,
    to_tz: str,
    fmt: str = "24h",
) -> str:
    """Format a rich side-by-side diff between two time zones.

    Returns a multi-line string like:
        ┌─────────────────────────────────────┐
        │  14:30  Europe/Warsaw               │
        │  08:30  America/New_York  (6h behind)│
        └─────────────────────────────────────┘
    """
    result = convert_time(source_time, from_tz, to_tz)
    source_fmt = (
        datetime.combine(datetime.now().date(), source_time).strftime("%H:%M")
        if fmt == "24h"
        else datetime.combine(datetime.now().date(), source_time)
        .strftime("%I:%M %p")
        .lstrip("0")
    )
    target_fmt = format_time(result, fmt)
    offset = compute_offset_label(from_tz, to_tz)

    line1 = f"  {source_fmt}  {from_tz}"
    line2 = f"  {target_fmt}  {to_tz}  ({offset})"
    width = max(len(line1), len(line2)) + 2

    top = "┌" + "─" * width + "┐"
    bot = "└" + "─" * width + "┘"
    row1 = "│" + line1.ljust(width) + "│"
    row2 = "│" + line2.ljust(width) + "│"

    return f"{top}\n{row1}\n{row2}\n{bot}"
