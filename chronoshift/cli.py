"""Command-line interface for chronoshift."""

from __future__ import annotations

import argparse
import sys

from chronoshift import __version__
from chronoshift.converter import (
    compute_offset_label,
    convert_time,
    format_time,
    list_timezones,
    parse_time,
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
        from zoneinfo import ZoneInfo

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

    results = []
    for target_tz in args.to_tz:
        try:
            result = convert_time(source, args.from_tz, target_tz)
            formatted = format_time(result, args.fmt)
            offset = compute_offset_label(args.from_tz, target_tz)
            results.append({
                "time": formatted,
                "zone": target_tz,
                "offset": offset,
                "iso": result.isoformat(),
            })
        except KeyError:
            print(f"error: unknown time zone '{target_tz}'", file=sys.stderr)
            return 1

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['time']} ({r['zone']}) — {r['offset']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
