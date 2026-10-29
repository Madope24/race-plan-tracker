import importlib
import sqlite3

import pytest
from fastapi.testclient import TestClient

TOKEN = "test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def make_client(tmp_path, monkeypatch, today="2026-11-04"):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("API_TOKEN", TOKEN)
    monkeypatch.setenv("TODAY_OVERRIDE", today)  # Wednesday of week 1 by default
    from app import db, main
    importlib.reload(db)
    importlib.reload(main)
    return TestClient(main.app)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch) as c:
        yield c


def test_health_is_public(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_auth_required(client):
    assert client.get("/api/sync").status_code == 401
    assert client.get("/api/sync", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_sync_contains_full_plan(client):
    data = client.get("/api/sync", headers=AUTH).json()
    assert len(data["sessions"]) == 143
    assert data["sessions"][0]["date"] == "2026-10-29"
    assert len(data["checkins"]) == 16
    d = data["dashboard"]
    assert d["current_week"] == 1
    assert d["days_to_race"] == 95
    assert d["is_fast_day"] is False
    assert d["weight"]["race_range"] == [80.0, 82.8]


def test_week_zero(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch, today="2026-10-29") as c:
        d = c.get("/api/dashboard", headers=AUTH).json()
        assert d["current_week"] == 0
        assert d["is_fast_day"] is True
        today = c.get("/api/sessions", params={"date": "2026-10-29"}, headers=AUTH).json()
        assert [s["type"] for s in today] == ["Mobility"]


def test_plan_rules(client):
    sessions = client.get("/api/sessions", headers=AUTH).json()
    by_date = {}
    for s in sessions:
        by_date.setdefault(s["date"], set()).add(s["type"])
        if s["day"] in ("Monday", "Thursday"):
            assert s["type"] == "Mobility", s  # dry-fast days: walk + mobility only
    assert not [d for d, t in by_date.items() if {"Run", "Swim"} <= t]
    assert sessions[-1]["title"].startswith("RACE")


def test_session_log_updates_dashboard(client):
    monday = client.get("/api/sessions", params={"date": "2026-11-02"}, headers=AUTH).json()
    tuesday = client.get("/api/sessions", params={"date": "2026-11-03"}, headers=AUTH).json()
    for s in monday + tuesday:
        body = {"status": "done", "effort": 4}
        if s["type"] == "Run":
            body.update(duration_min=32, actual=3.1)
        r = client.put(f"/api/sessions/{s['id']}/log", headers=AUTH, json=body)
        assert r.status_code == 200 and r.json()["applied"]
    d = client.get("/api/dashboard", headers=AUTH).json()
    assert d["sessions"]["done_total"] == len(monday) + len(tuesday) == 3
    assert d["streak_days"] == 2
    assert d["longest_run_min"] == 32
    assert d["longest_run_km"] == 3.1
    assert d["this_week"]["run_min_done"] == 32
    assert d["this_week"]["run_min_planned"] == 105
    assert d["decision_this_week"]["status"] == "green"


def test_decision_turns_red_on_pain(client):
    tue = client.get("/api/sessions", params={"date": "2026-11-03"}, headers=AUTH).json()
    client.put(f"/api/sessions/{tue[0]['id']}/log", headers=AUTH, json={"status": "done", "effort": 4})
    client.put("/api/habits/2026-11-03", headers=AUTH, json={"pain": 5, "pain_where": "left shin", "sleep_hours": 7})
    d = client.get("/api/dashboard", headers=AUTH).json()["decision_this_week"]
    assert d["status"] == "red"
    assert any("pain" in r for r in d["reasons"])


def test_decision_amber_on_hard_runs(client):
    tue = client.get("/api/sessions", params={"date": "2026-11-03"}, headers=AUTH).json()
    mon = client.get("/api/sessions", params={"date": "2026-11-02"}, headers=AUTH).json()
    for s in tue + mon:
        client.put(f"/api/sessions/{s['id']}/log", headers=AUTH, json={"status": "done", "effort": 6})
    d = client.get("/api/dashboard", headers=AUTH).json()["decision_this_week"]
    assert d["status"] == "amber"


def test_last_write_wins(client):
    newer = {"status": "done", "actual": 5, "updated_at": "2026-11-03T10:00:00Z"}
    older = {"status": "skipped", "updated_at": "2026-11-03T09:00:00Z"}
    assert client.put("/api/sessions/3/log", headers=AUTH, json=newer).json()["applied"] is True
    r = client.put("/api/sessions/3/log", headers=AUTH, json=older).json()
    assert r["applied"] is False
    assert r["session"]["log"]["status"] == "done"


def test_daily_weights_and_test_projection(client):
    for i, w in enumerate([87.0, 86.8, 86.9, 86.6]):
        client.put(f"/api/habits/2026-11-0{i + 1}", headers=AUTH, json={"weight": w, "sleep_hours": 7.5, "energy": 4})
    r = client.put("/api/checkins/4", headers=AUTH, json={"tt_5k_min": 46.5, "swim_nonstop_actual": 220, "waist": 104})
    assert r.json()["checkin"]["tt_5k_min"] == 46.5
    d = client.get("/api/dashboard", headers=AUTH).json()
    assert d["weight"]["latest"] == 86.8  # 7-day average of 87.0, 86.8, 86.9, 86.6
    assert d["weight"]["latest_is_7day_avg"] is True
    assert d["test"]["plan"] == "3:45"
    assert 230 <= d["test"]["course_min"] <= 232
    assert d["longest_swim_m"] == 220
    by_week = {p["week"]: p["actual"] for p in d["weight_series"]}
    assert by_week[0] == 87.0  # 1 Nov is in week 0
    assert by_week[1] == 86.8  # 2–4 Nov average


def test_validation(client):
    assert client.put("/api/sessions/1/log", headers=AUTH, json={"status": "maybe"}).status_code == 422
    assert client.put("/api/sessions/9999/log", headers=AUTH, json={"status": "done"}).status_code == 404
    assert client.put("/api/habits/2026-11-02", headers=AUTH, json={"pain": 11}).status_code == 422
    assert client.put("/api/checkins/99", headers=AUTH, json={"waist": 100}).status_code == 404


def test_reference(client):
    ref = client.get("/api/reference", headers=AUTH).json()
    assert [g["id"] for g in ref["guides"]] == ["strength", "swim", "nutrition", "meals", "fuel", "race", "rules"]


def test_reseed_keeps_matching_logs(client):
    client.put("/api/sessions/1/log", headers=AUTH, json={"status": "done"})
    from app import db
    db.init_db()
    s = client.get("/api/sessions", params={"date": "2026-10-29"}, headers=AUTH).json()
    assert s[0]["log"]["status"] == "done"


def test_migrates_old_database(tmp_path, monkeypatch):
    """A database from the first release (no new columns, old plan) upgrades in place."""
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE habits (date TEXT PRIMARY KEY, sleep_hours REAL, water_litres REAL, protein_g INTEGER,
          calories INTEGER, veg_servings INTEGER, sunlight INTEGER, kegel_1 INTEGER, kegel_2 INTEGER,
          fast_kept INTEGER, energy INTEGER, notes TEXT, updated_at TEXT NOT NULL);
        INSERT INTO habits (date, sleep_hours, updated_at) VALUES ('2026-10-20', 7, '2026-10-20T00:00:00Z');
        CREATE TABLE checkins (week INTEGER PRIMARY KEY, weight REAL, waist REAL, long_run_actual REAL,
          swim_nonstop_actual REAL, energy INTEGER, notes TEXT, updated_at TEXT NOT NULL);
    """)
    conn.commit()
    conn.close()
    with make_client(tmp_path, monkeypatch) as c:
        assert c.put("/api/habits/2026-11-02", headers=AUTH, json={"weight": 86.9, "mood": 4}).status_code == 200
        hab = c.get("/api/habits", headers=AUTH).json()
        assert hab[0]["date"] == "2026-10-20" and hab[0]["sleep_hours"] == 7
