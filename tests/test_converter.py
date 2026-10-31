"""Tests for chronoshift.converter."""

from datetime import time

import pytest

from chronoshift.converter import (
    compute_offset_label,
    convert_time,
    format_time,
    list_timezones,
    parse_time,
)


class TestParseTime:
    def test_24h_format(self):
        assert parse_time("14:30") == time(14, 30)

    def test_24h_with_seconds(self):
        assert parse_time("09:15:30") == time(9, 15, 30)

    def test_invalid_input(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            parse_time("not-a-time")

    def test_midnight(self):
        assert parse_time("00:00") == time(0, 0)

    def test_end_of_day(self):
        assert parse_time("23:59") == time(23, 59)

    def test_12h_lowercase(self):
        assert parse_time("2:30pm") == time(14, 30)

    def test_12h_with_space_and_seconds(self):
        assert parse_time("2:30:05 pm") == time(14, 30, 5)

    def test_12h_midnight(self):
        assert parse_time("12:00am") == time(0, 0)


class TestConvertTime:
    def test_utc_to_eastern(self):
        result = convert_time(time(12, 0), "UTC", "US/Eastern")
        assert result.tzname() in ("EST", "EDT")

    def test_same_zone(self):
        result = convert_time(time(10, 0), "UTC", "UTC")
        assert result.hour == 10
        assert result.minute == 0

    def test_invalid_zone_raises(self):
        with pytest.raises(KeyError):
            convert_time(time(12, 0), "UTC", "Fake/Zone")


class TestFormatTime:
    def test_24h_format(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        dt = datetime(2026, 1, 15, 14, 30, tzinfo=ZoneInfo("UTC"))
        assert format_time(dt, "24h") == "14:30"

    def test_12h_format(self):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        dt = datetime(2026, 1, 15, 14, 30, tzinfo=ZoneInfo("UTC"))
        assert format_time(dt, "12h") == "2:30 PM"


class TestListTimezones:
    def test_returns_sorted_list(self):
        zones = list_timezones()
        assert isinstance(zones, list)
        assert len(zones) > 100
        assert zones == sorted(zones)

    def test_contains_common_zones(self):
        zones = list_timezones()
        assert "UTC" in zones
        assert "Europe/Warsaw" in zones
        assert "US/Eastern" in zones


class TestOffsetLabel:
    def test_same_zone(self):
        label = compute_offset_label("UTC", "UTC")
        assert label == "same time"

    def test_returns_string(self):
        label = compute_offset_label("UTC", "US/Eastern")
        assert isinstance(label, str)
        assert "h" in label

    def test_half_hour_zone_keeps_minutes(self):
        assert compute_offset_label("UTC", "Asia/Kolkata") == "5h 30m ahead"

    def test_three_quarter_hour_zone_keeps_minutes(self):
        assert compute_offset_label("UTC", "Asia/Kathmandu") == "5h 45m ahead"

    def test_forty_five_minute_zone_keeps_minutes(self):
        assert compute_offset_label("Australia/Eucla", "UTC") == "8h 45m behind"
