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


def test_same_day_has_no_marker(capsys):
    code = main(["12:00", "--from", "UTC", "--to", "UTC"])
    assert code == 0
    out = capsys.readouterr().out
    assert "+1d" not in out
    assert "-1d" not in out
    assert "12:00 (UTC)" in out
