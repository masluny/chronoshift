"""Tests for the chronoshift command line."""

from chronoshift.cli import main


def test_marks_next_calendar_day(capsys):
    code = main(["23:00", "--from", "UTC", "--to", "Asia/Tokyo"])
    assert code == 0
    out = capsys.readouterr().out
    assert "08:00 +1d" in out
    assert "Asia/Tokyo" in out


def test_marks_previous_calendar_day(capsys):
    code = main(["02:00", "--from", "Asia/Tokyo", "--to", "UTC"])
    assert code == 0
    out = capsys.readouterr().out
    assert "17:00 -1d" in out


def test_date_uses_standard_time_in_winter(capsys):
    code = main(["12:00", "--from", "UTC", "--to", "America/New_York", "--date", "2026-01-15"])
    assert code == 0
    assert "07:00" in capsys.readouterr().out


def test_date_uses_daylight_time_in_summer(capsys):
    code = main(["12:00", "--from", "UTC", "--to", "America/New_York", "--date", "2026-07-15"])
    assert code == 0
    assert "08:00" in capsys.readouterr().out


def test_bad_date_is_an_error(capsys):
    code = main(["12:00", "--from", "UTC", "--to", "UTC", "--date", "yesterday"])
    assert code == 1
    assert "YYYY-MM-DD" in capsys.readouterr().err


def test_now_uses_the_clock_in_the_source_zone(capsys):
    code = main(["--now", "--from", "UTC", "--to", "UTC"])
    assert code == 0
    out = capsys.readouterr().out
    assert "(UTC)" in out
    assert "same time" in out


def test_same_day_has_no_marker(capsys):
    code = main(["12:00", "--from", "UTC", "--to", "UTC"])
    assert code == 0
    out = capsys.readouterr().out
    assert "+1d" not in out
    assert "-1d" not in out
    assert "12:00 (UTC)" in out
