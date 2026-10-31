"""Command-line interface for chronoshift."""

from __future__ import annotations

import argparse
import sys
from zoneinfo import ZoneInfo

from chronoshift import __version__
from chronoshift.converter import (
    calendar_day_delta,
    compute_offset_label,
    convert_time,
    format_compact,
    format_diff,
    format_time,
    list_timezones,
    parse_time,
    suggest_timezone,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chronoshift",
        description="Convert times between time zones, fast.",
    )
    parser.add_argument(
        "time",
        nargs="?",
        help="Time to convert (e.g. 14:30, 09:00:00, 2:30PM)",
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Use the current local time as input",
    )
    parser.add_argument(
        "--from",
        dest="from_tz",
        default="UTC",
        help="Source time zone (default: UTC)",
    )
    parser.add_argument(
        "--to",
        dest="to_tz",
        nargs="+",
        help="Target time zone(s)",
    )
    parser.add_argument(
        "--date",
        help="Calendar day for the conversion, YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["12h", "24h"],
        default="24h",
        help="Output format (default: 24h)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (useful for scripting)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="One line per zone, with a short city label",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Draw a box around the source and target times",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available time zones",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        for tz in list_timezones():
            print(tz)
        return 0

    if args.now:
        from datetime import datetime

        now = datetime.now(tz=ZoneInfo(args.from_tz))
        args.time = now.strftime("%H:%M")

    if not args.time:
        parser.print_help()
        return 1

    if not args.to_tz:
        print("error: --to is required when converting a time", file=sys.stderr)
        return 1

    try:
        source = parse_time(args.time)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    when = None
    if args.date:
        from datetime import datetime

        try:
            when = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("error: --date must be YYYY-MM-DD", file=sys.stderr)
            return 1

    chosen = [name for name in ("json", "compact", "diff") if getattr(args, name)]
    if len(chosen) > 1:
        print("error: use only one of --json, --compact, --diff", file=sys.stderr)
        return 1

    results = []
    for target_tz in args.to_tz:
        try:
            result = convert_time(source, args.from_tz, target_tz, date=when)
            formatted = format_time(result, args.fmt)
            offset = compute_offset_label(args.from_tz, target_tz)
            delta = calendar_day_delta(result.astimezone(ZoneInfo(args.from_tz)), result)
            results.append({
                "time": formatted,
                "zone": target_tz,
                "offset": offset,
                "iso": result.isoformat(),
                "day_delta": delta,
            })
        except KeyError:
            suggestions = suggest_timezone(target_tz)
            msg = f"error: unknown time zone '{target_tz}'"
            if suggestions:
                msg += f" — did you mean: {', '.join(suggestions)}?"
            print(msg, file=sys.stderr)
            return 1

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    elif args.compact:
        for target_tz in args.to_tz:
            print(format_compact(source, args.from_tz, target_tz, args.fmt, date=when))
    elif args.diff:
        for target_tz in args.to_tz:
            print(format_diff(source, args.from_tz, target_tz, args.fmt, date=when))
    else:
        for r in results:
            day = "" if r["day_delta"] == 0 else f" {r['day_delta']:+d}d"
            print(f"{r['time']}{day} ({r['zone']}) — {r['offset']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
