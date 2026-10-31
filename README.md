# ⏱ chronoshift

A fast, no-nonsense CLI tool for converting times between time zones.

```bash
$ chronoshift 14:30 --from Europe/Warsaw --to America/New_York
08:30 AM (America/New_York) — 6h behind
```

## Why?

Because Googling "what time is it in Tokyo" for the hundredth time gets old. `chronoshift` works offline, handles DST automatically, and lives where you already are — your terminal.

## Installation

```bash
pip install chronoshift
```

Or install from source:

```bash
git clone https://github.com/masluny/chronoshift.git
cd chronoshift
pip install -e .
```

## Usage

### Basic conversion

```bash
chronoshift 09:00 --from UTC --to Europe/London
chronoshift 14:30 --from warsaw --to nyc
```

City names such as `warsaw`, `london`, `tokyo`, `nyc`, and `sydney` map to their IANA zones. Full zone names are also case-insensitive.

When the converted clock falls on another calendar day, the line says so:

```bash
$ chronoshift 23:00 --from UTC --to Asia/Tokyo
08:00 +1d (Asia/Tokyo) — 9h ahead
```

### Compact and boxed output

```bash
chronoshift 14:30 --from Europe/Warsaw --to America/New_York --compact
chronoshift 14:30 --from Europe/Warsaw --to America/New_York --diff
```

`--json`, `--compact`, and `--diff` cannot be combined.

### Multiple target zones

```bash
chronoshift 15:00 --from Asia/Tokyo --to America/New_York Europe/Berlin
```

### List available time zones

```bash
chronoshift --list
chronoshift --list Warsaw
```

### A specific day

DST depends on the date. The default is today.

```bash
chronoshift 12:00 --from UTC --to America/New_York --date 2026-01-15
```

### Use 24h format (default) or 12h

```bash
chronoshift 22:00 --from UTC --to US/Pacific --format 12h
```

## Supported Zones

All IANA time zone names are supported (powered by Python's `zoneinfo`). Run `chronoshift --list` to see them all.

## Development

```bash
git clone https://github.com/masluny/chronoshift.git
cd chronoshift
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
