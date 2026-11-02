from datetime import date

import pytest

import tracker


def sample_assignments():
    return [
        {"course": "PROG 101", "title": "Later", "due": "2026-11-20"},
        {"course": "MATH 102", "title": "Soon", "due": "2026-11-05"},
        {"course": "PHYS 103", "title": "Past", "due": "2026-10-01"},
    ]


def titles(assignments):
    return [a["title"] for a in assignments]


def test_filter_hides_past_assignments():
    result = tracker.filter_upcoming(sample_assignments(), date(2026, 11, 2), week_only=False)
    assert "Past" not in titles(result)


def test_filter_sorts_by_due_date():
    result = tracker.filter_upcoming(sample_assignments(), date(2026, 11, 2), week_only=False)
    assert titles(result) == ["Soon", "Later"]


def test_week_only_limits_to_seven_days():
    result = tracker.filter_upcoming(sample_assignments(), date(2026, 11, 2), week_only=True)
    assert titles(result) == ["Soon"]


def test_days_until_counts_correctly():
    assignment = {"course": "X", "title": "Y", "due": "2026-11-05"}
    assert tracker.days_until(assignment, date(2026, 11, 2)) == 3


def test_add_assignment_saves_to_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tracker, "DATA_FILE", str(tmp_path / "test.json"))
    tracker.add_assignment("PROG 101", "Lab", "2026-12-01")
    assert tracker.load_assignments() == [
        {"course": "PROG 101", "title": "Lab", "due": "2026-12-01"}
    ]


def test_add_assignment_rejects_bad_date(tmp_path, monkeypatch):
    monkeypatch.setattr(tracker, "DATA_FILE", str(tmp_path / "test.json"))
    with pytest.raises(SystemExit):
        tracker.add_assignment("PROG 101", "Lab", "12/01")
    assert tracker.load_assignments() == []

def test_remove_by_title_ignores_case():
    result = tracker.remove_by_title(sample_assignments(), "soon")
    assert titles(result) == ["Later", "Past"]


def test_done_removes_from_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tracker, "DATA_FILE", str(tmp_path / "test.json"))
    tracker.add_assignment("PROG 101", "Lab", "2026-12-01")
    tracker.add_assignment("MATH 102", "Quiz", "2026-12-02")
    tracker.done_assignment("Lab")
    assert titles(tracker.load_assignments()) == ["Quiz"]


def test_done_unknown_title_exits(tmp_path, monkeypatch):
    monkeypatch.setattr(tracker, "DATA_FILE", str(tmp_path / "test.json"))
    tracker.add_assignment("PROG 101", "Lab", "2026-12-01")
    with pytest.raises(SystemExit):
        tracker.done_assignment("Nonexistent")
    assert titles(tracker.load_assignments()) == ["Lab"]