"""Race Plan API — the single source of truth for the Race Plan app.

Every device pushes its changes here and pulls the latest state (the app does this every 4 minutes).
Writes are last-write-wins on the client's `updated_at`, so an old offline edit never overwrites a newer one.
"""
import datetime as dt
import os
import secrets
from contextlib import asynccontextmanager
from typing import Literal, Optional
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import db

TZ = ZoneInfo(os.environ.get("TZ_NAME", "Africa/Dar_es_Salaam"))
API_TOKEN = os.environ.get("API_TOKEN", "")
TRAINING_TYPES = ("Run", "Swim", "Strength", "Mobility")
RIEGEL = (21.0975 / 5) ** 1.06  # 5 km → half-marathon factor
COURSE_ALLOWANCE = 1.08  # hills, heat and beginner fatigue (planning assumption)
PLAN_TIERS = [(36.0, "3:00"), (40.0, "3:15"), (43.0, "3:30"), (47.0, "3:45")]


@asynccontextmanager
async def lifespan(_app):
    db.init_db()
    yield


app = FastAPI(title="Race Plan API", version="2.0.0", lifespan=lifespan)


# ---------- auth ----------
def require_token(authorization: str = Header(default="")):
    if not API_TOKEN:
        raise HTTPException(500, "Server has no API_TOKEN configured")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token, API_TOKEN):
        raise HTTPException(401, "Invalid or missing token")


def today() -> dt.date:
    override = os.environ.get("TODAY_OVERRIDE")  # for tests
    return dt.date.fromisoformat(override) if override else dt.datetime.now(TZ).date()


def utc_iso(value: Optional[dt.datetime]) -> str:
    value = value or dt.datetime.now(dt.timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# ---------- models ----------
class SessionLogIn(BaseModel):
    status: Literal["done", "partial", "skipped"]
    actual: Optional[float] = Field(default=None, ge=0)  # distance: km for runs, m for swims
    effort: Optional[int] = Field(default=None, ge=1, le=10)
    duration_min: Optional[float] = Field(default=None, ge=0, le=600)
    notes: Optional[str] = Field(default=None, max_length=2000)
    updated_at: Optional[dt.datetime] = None


class HabitIn(BaseModel):
    weight: Optional[float] = Field(default=None, ge=30, le=250)
    resting_hr: Optional[int] = Field(default=None, ge=25, le=150)
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=5)
    soreness: Optional[int] = Field(default=None, ge=0, le=10)
    pain: Optional[int] = Field(default=None, ge=0, le=10)
    pain_where: Optional[str] = Field(default=None, max_length=200)
    energy: Optional[int] = Field(default=None, ge=1, le=5)
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    motivation: Optional[int] = Field(default=None, ge=1, le=5)
    nutrition: Optional[int] = Field(default=None, ge=1, le=5)
    fast_tolerance: Optional[int] = Field(default=None, ge=1, le=5)
    warning_signs: Optional[bool] = None
    water_litres: Optional[float] = Field(default=None, ge=0, le=15)
    protein_g: Optional[int] = Field(default=None, ge=0, le=600)
    calories: Optional[int] = Field(default=None, ge=0, le=10000)
    veg_servings: Optional[int] = Field(default=None, ge=0, le=30)
    sunlight: Optional[bool] = None
    kegel_1: Optional[bool] = None
    kegel_2: Optional[bool] = None
    fast_kept: Optional[bool] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    updated_at: Optional[dt.datetime] = None


BOOL_HABITS = ("sunlight", "kegel_1", "kegel_2", "fast_kept", "warning_signs")


class CheckinIn(BaseModel):
    weight: Optional[float] = Field(default=None, ge=30, le=250)
    waist: Optional[float] = Field(default=None, ge=30, le=250)
    long_run_actual: Optional[float] = Field(default=None, ge=0, le=600)  # minutes
    swim_nonstop_actual: Optional[float] = Field(default=None, ge=0, le=10000)
    tt_5k_min: Optional[float] = Field(default=None, ge=15, le=120)
    energy: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = Field(default=None, max_length=2000)
    updated_at: Optional[dt.datetime] = None


# ---------- helpers ----------
def is_newer(conn, table, key_col, key, incoming):
    row = conn.execute(f"SELECT updated_at FROM {table} WHERE {key_col} = ?", (key,)).fetchone()
    return row is None or incoming >= row["updated_at"]


def session_rows(conn, where="1=1", params=()):
    rows = conn.execute(
        f"""SELECT s.*, l.status, l.actual, l.effort, l.duration_min, l.notes, l.updated_at
            FROM sessions s LEFT JOIN session_logs l ON l.session_id = s.id
            WHERE {where} ORDER BY s.date, s.id""",
        params,
    ).fetchall()
    out = []
    for r in rows:
        d = {k: r[k] for k in ("id", "date", "week", "day", "phase", "time_slot", "type", "title", "details", "planned", "unit")}
        d["log"] = None if r["status"] is None else {
            "status": r["status"], "actual": r["actual"], "effort": r["effort"],
            "duration_min": r["duration_min"], "notes": r["notes"], "updated_at": r["updated_at"],
        }
        out.append(d)
    return out


def habit_dict(r):
    d = dict(r)
    for k in BOOL_HABITS:
        if k in d:
            d[k] = None if d[k] is None else bool(d[k])
    return d


def checkin_rows(conn):
    rows = conn.execute(
        """SELECT w.*, c.weight, c.waist, c.long_run_actual, c.swim_nonstop_actual, c.tt_5k_min, c.energy, c.notes, c.updated_at
           FROM weeks w LEFT JOIN checkins c ON c.week = w.week ORDER BY w.week"""
    ).fetchall()
    return [dict(r) for r in rows]


def _avg(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


def _done(x):
    return x["log"] is not None and x["log"]["status"] in ("done", "partial")


def _run_minutes(x):
    """Minutes actually run: logged duration, else the plan's minutes when marked done."""
    if not _done(x):
        return 0.0
    if x["log"]["duration_min"] is not None:
        return float(x["log"]["duration_min"])
    return float(x["planned"]) if x["unit"] == "min" else 0.0


def week_bounds(s, w):
    start = dt.date.fromisoformat(s["start_date"])
    week1 = dt.date.fromisoformat(s.get("week1_date", s["start_date"]))
    if w == 0:
        return start, week1 - dt.timedelta(days=1)
    a = week1 + dt.timedelta(weeks=w - 1)
    return a, a + dt.timedelta(days=6)


def week_decision(training, habits, s, w, upto):
    """The Sunday rule from plan section 14. Returns None when there is nothing to judge yet."""
    a, b = week_bounds(s, w)
    b = min(b, upto)
    if b < a:
        return None
    # Today's sessions only count once done, so the morning view isn't amber for workouts still to come.
    items = [x for x in training if x["week"] == w and
             (x["date"] < upto.isoformat() or (x["date"] == upto.isoformat() and _done(x)))
             and x["date"] <= b.isoformat()]
    days = [h for h in habits if a.isoformat() <= h["date"] <= b.isoformat()]
    done = sum(1 for x in items if _done(x))
    if not items or (done == 0 and not days):
        return None
    completion = done / len(items)
    rpes = [x["log"]["effort"] for x in items if x["type"] == "Run" and _done(x) and x["log"]["effort"]]
    avg_rpe = _avg(rpes)
    pains = [h.get("pain") for h in days if h.get("pain") is not None]
    max_pain = max(pains) if pains else None
    sleep = _avg([h.get("sleep_hours") for h in days])
    energy = _avg([h.get("energy") for h in days])
    mood = _avg([h.get("mood") for h in days])
    warnings = any(h.get("warning_signs") for h in days)

    red, amber = [], []
    if max_pain is not None and max_pain >= 4:
        red.append(f"pain reached {max_pain}/10")
    if completion < 0.6:
        red.append(f"only {round(completion * 100)}% of sessions done")
    if sleep is not None and sleep < 6:
        red.append(f"sleep averaged {sleep} h")
    if warnings:
        red.append("fast-day warning signs logged")
    if 0.6 <= completion < 0.85:
        amber.append(f"{round(completion * 100)}% of sessions done")
    if avg_rpe is not None and avg_rpe >= 5:
        amber.append(f"runs averaged RPE {avg_rpe}")
    if max_pain == 3:
        amber.append("pain reached 3/10")
    if sleep is not None and 6 <= sleep < 6.5:
        amber.append(f"sleep averaged {sleep} h")
    if energy is not None and energy < 3:
        amber.append(f"energy averaged {energy}/5")
    if mood is not None and mood < 3:
        amber.append(f"mood averaged {mood}/5")
    if red:
        status, action = "red", "Step back: repeat last week's volume or take an early cutback week."
        reasons = red + amber
    elif amber:
        status, action = "amber", "Repeat this week before moving on."
        reasons = amber
    else:
        status, action = "green", "Progress to the next week."
        reasons = []
    return {
        "week": w, "status": status, "action": action, "reasons": reasons,
        "completion": round(completion, 3), "avg_run_rpe": avg_rpe, "max_pain": max_pain,
        "avg_sleep": sleep, "avg_energy": energy, "avg_mood": mood, "through": b.isoformat(),
    }


def seven_day_weight(habits, end):
    lo = (end - dt.timedelta(days=6)).isoformat()
    return _avg([h.get("weight") for h in habits if lo <= h["date"] <= end.isoformat()])


def dashboard(conn):
    s = db.settings(conn)
    t = today()
    start = dt.date.fromisoformat(s["start_date"])
    week1 = dt.date.fromisoformat(s.get("week1_date", s["start_date"]))
    race = dt.date.fromisoformat(s["race_date"])
    sessions = session_rows(conn)
    training = [x for x in sessions if x["type"] in TRAINING_TYPES]
    habits = [habit_dict(r) for r in conn.execute("SELECT * FROM habits ORDER BY date")]
    checkins = checkin_rows(conn)
    weeks_present = sorted({x["week"] for x in sessions})

    week = 0 if t < week1 else min(max(weeks_present), (t - week1).days // 7 + 1)
    phase = next((x["phase"] for x in sessions if x["week"] == week), sessions[0]["phase"] if sessions else "")

    to_date = [x for x in training if x["date"] <= t.isoformat()]
    this_week = [x for x in training if x["week"] == week]

    def planned_sum(items, kind, unit):
        return round(sum(x["planned"] for x in items if x["type"] == kind and x["unit"] == unit), 1)

    runs_done = [x for x in training if x["type"] == "Run" and _done(x)]
    longest_run_min = max((_run_minutes(x) for x in runs_done), default=0)
    longest_run_km = max(((x["log"]["actual"] if x["unit"] == "min" else x["planned"]) or 0 for x in runs_done), default=0)
    swims_done = [x for x in this_week if x["type"] == "Swim" and _done(x)]

    # Weight: 7-day average of daily weigh-ins (weekly check-in weights are a fallback)
    weighed = [h for h in habits if h.get("weight") is not None]
    latest_avg = seven_day_weight(habits, dt.date.fromisoformat(weighed[-1]["date"])) if weighed else None
    if latest_avg is None:
        legacy = [c for c in checkins if c["weight"] is not None]
        latest_avg = legacy[-1]["weight"] if legacy else None
    week_targets = {c["week"]: c for c in checkins}
    series = []
    for c in checkins:
        a, b = week_bounds(s, c["week"]) if c["week"] <= max(weeks_present, default=0) else (
            dt.date.fromisoformat(c["date"]), dt.date.fromisoformat(c["date"]))
        avg = _avg([h.get("weight") for h in habits if a.isoformat() <= h["date"] <= b.isoformat()])
        series.append({"week": c["week"], "label": c["label"], "target": c["target_weight"],
                       "stretch": c["stretch_weight"], "actual": avg if avg is not None else c["weight"]})

    # Streak: consecutive days (ending today, or yesterday if today isn't finished) with every session done.
    by_date = {}
    for x in training:
        by_date.setdefault(x["date"], []).append(x)
    day = t
    if day.isoformat() in by_date and not all(_done(x) for x in by_date[day.isoformat()]):
        day -= dt.timedelta(days=1)
    streak = 0
    while day >= start:
        items = by_date.get(day.isoformat(), [])
        if items and not all(_done(x) for x in items):
            break
        if items:
            streak += 1
        day -= dt.timedelta(days=1)

    last7 = [h for h in habits if (t - dt.timedelta(days=6)).isoformat() <= h["date"] <= t.isoformat()]

    tests = [c for c in checkins if c.get("tt_5k_min") is not None]
    latest_test = tests[-1] if tests else None
    projection = None
    if latest_test:
        tt = latest_test["tt_5k_min"]
        projection = {
            "week": latest_test["week"], "test_min": tt,
            "flat_min": round(tt * RIEGEL, 1), "course_min": round(tt * RIEGEL * COURSE_ALLOWANCE, 1),
            "plan": next((name for limit, name in PLAN_TIERS if tt <= limit), "Finish strong (4:00)"),
        }

    weekly = []
    for w in weeks_present:
        items = [x for x in training if x["week"] == w]
        weekly.append({"week": w, "planned": len(items), "done": sum(1 for x in items if _done(x))})

    upcoming = [x for x in training if x["date"] >= t.isoformat() and x["log"] is None]

    return {
        "today": t.isoformat(),
        "start_date": s["start_date"],
        "week1_date": s.get("week1_date", s["start_date"]),
        "race_date": s["race_date"],
        "days_to_race": max(0, (race - t).days),
        "plan_started": t >= start,
        "current_week": week,
        "last_week": max(weeks_present) if weeks_present else 14,
        "phase": phase,
        "is_fast_day": t.strftime("%A") in s["fast_days"],
        "fast_until": s["fast_until"],
        "weight": {
            "start": s["start_weight"],
            "latest": latest_avg,
            "latest_is_7day_avg": bool(weighed),
            "lost": round(s["start_weight"] - latest_avg, 1) if latest_avg is not None else 0,
            "target_this_week": week_targets.get(week, {}).get("target_weight"),
            "range_this_week": [week_targets.get(week, {}).get("stretch_weight"), week_targets.get(week, {}).get("target_weight")],
            "race_range": [week_targets[max(weeks_present)]["stretch_weight"], week_targets[max(weeks_present)]["target_weight"]]
            if weeks_present and max(weeks_present) in week_targets else None,
        },
        "sessions": {
            "total": len(training),
            "done_total": sum(1 for x in training if _done(x)),
            "planned_to_date": len(to_date),
            "done_to_date": sum(1 for x in to_date if _done(x)),
            "completion_to_date": round(sum(1 for x in to_date if _done(x)) / len(to_date), 3) if to_date else 0,
        },
        "this_week": {
            "planned": len(this_week),
            "done": sum(1 for x in this_week if _done(x)),
            "run_min_planned": planned_sum(this_week, "Run", "min"),
            "run_min_done": round(sum(_run_minutes(x) for x in this_week if x["type"] == "Run"), 1),
            "run_km_done": round(sum((x["log"]["actual"] or 0) for x in this_week if x["type"] == "Run" and _done(x) and x["unit"] == "min"), 1),
            "swim_m_planned": planned_sum(this_week, "Swim", "m"),
            "swim_m_done": round(sum((x["log"]["actual"] if x["log"]["actual"] is not None else x["planned"]) for x in swims_done), 1),
        },
        "longest_run_min": longest_run_min,
        "longest_run_km": longest_run_km,
        "longest_swim_m": max((c["swim_nonstop_actual"] or 0 for c in checkins), default=0),
        "streak_days": streak,
        "habits_7d": {
            "days_logged": len(last7),
            "sleep_hours": _avg([h.get("sleep_hours") for h in last7]),
            "sleep_quality": _avg([h.get("sleep_quality") for h in last7]),
            "energy": _avg([h.get("energy") for h in last7]),
            "mood": _avg([h.get("mood") for h in last7]),
            "resting_hr": _avg([h.get("resting_hr") for h in last7]),
            "water_litres": _avg([h.get("water_litres") for h in last7]),
            "protein_g": _avg([h.get("protein_g") for h in last7]),
        },
        "decision_this_week": week_decision(training, habits, s, week, t),
        "decision_last_week": week_decision(training, habits, s, week - 1, t) if week >= 1 else None,
        "test": projection,
        "weekly_completion": weekly,
        "weight_series": series,
        "next_session_id": upcoming[0]["id"] if upcoming else None,
    }


# ---------- routes ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "time": utc_iso(None)}


@app.get("/api/sync", dependencies=[Depends(require_token)])
def sync():
    """Everything the app needs in one call."""
    with db.get_conn() as conn:
        return {
            "server_time": utc_iso(None),
            "sessions": session_rows(conn),
            "habits": [habit_dict(r) for r in conn.execute("SELECT * FROM habits ORDER BY date")],
            "checkins": checkin_rows(conn),
            "dashboard": dashboard(conn),
            "reference_version": db.reference()["version"],
        }


@app.get("/api/dashboard", dependencies=[Depends(require_token)])
def get_dashboard():
    with db.get_conn() as conn:
        return dashboard(conn)


@app.get("/api/reference", dependencies=[Depends(require_token)])
def get_reference():
    return db.reference()


@app.get("/api/sessions", dependencies=[Depends(require_token)])
def list_sessions(week: Optional[int] = None, date: Optional[str] = None):
    with db.get_conn() as conn:
        if week is not None:
            return session_rows(conn, "s.week = ?", (week,))
        if date is not None:
            return session_rows(conn, "s.date = ?", (date,))
        return session_rows(conn)


@app.put("/api/sessions/{session_id}/log", dependencies=[Depends(require_token)])
def put_session_log(session_id: int, body: SessionLogIn):
    stamp = utc_iso(body.updated_at)
    with db.get_conn() as conn:
        if not conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone():
            raise HTTPException(404, "Session not found")
        applied = is_newer(conn, "session_logs", "session_id", session_id, stamp)
        if applied:
            conn.execute(
                """INSERT INTO session_logs (session_id, status, actual, effort, duration_min, notes, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(session_id) DO UPDATE SET status=excluded.status, actual=excluded.actual,
                     effort=excluded.effort, duration_min=excluded.duration_min, notes=excluded.notes,
                     updated_at=excluded.updated_at""",
                (session_id, body.status, body.actual, body.effort, body.duration_min, body.notes, stamp),
            )
        return {"applied": applied, "session": session_rows(conn, "s.id = ?", (session_id,))[0]}


@app.delete("/api/sessions/{session_id}/log", dependencies=[Depends(require_token)])
def delete_session_log(session_id: int):
    with db.get_conn() as conn:
        conn.execute("DELETE FROM session_logs WHERE session_id = ?", (session_id,))
        rows = session_rows(conn, "s.id = ?", (session_id,))
        if not rows:
            raise HTTPException(404, "Session not found")
        return {"applied": True, "session": rows[0]}


@app.get("/api/habits", dependencies=[Depends(require_token)])
def list_habits():
    with db.get_conn() as conn:
        return [habit_dict(r) for r in conn.execute("SELECT * FROM habits ORDER BY date")]


@app.put("/api/habits/{date}", dependencies=[Depends(require_token)])
def put_habit(date: dt.date, body: HabitIn):
    stamp = utc_iso(body.updated_at)
    key = date.isoformat()
    vals = body.model_dump(exclude={"updated_at"})
    for k in BOOL_HABITS:
        vals[k] = None if vals[k] is None else int(vals[k])
    with db.get_conn() as conn:
        applied = is_newer(conn, "habits", "date", key, stamp)
        if applied:
            cols = list(vals)
            conn.execute(
                f"""INSERT INTO habits (date, {', '.join(cols)}, updated_at)
                    VALUES (?, {', '.join('?' for _ in cols)}, ?)
                    ON CONFLICT(date) DO UPDATE SET {', '.join(f'{c}=excluded.{c}' for c in cols)}, updated_at=excluded.updated_at""",
                (key, *vals.values(), stamp),
            )
        return {"applied": applied, "habit": habit_dict(conn.execute("SELECT * FROM habits WHERE date = ?", (key,)).fetchone())}


@app.get("/api/checkins", dependencies=[Depends(require_token)])
def list_checkins():
    with db.get_conn() as conn:
        return checkin_rows(conn)


@app.put("/api/checkins/{week}", dependencies=[Depends(require_token)])
def put_checkin(week: int, body: CheckinIn):
    stamp = utc_iso(body.updated_at)
    with db.get_conn() as conn:
        if not conn.execute("SELECT 1 FROM weeks WHERE week = ?", (week,)).fetchone():
            raise HTTPException(404, "Week not found")
        applied = is_newer(conn, "checkins", "week", week, stamp)
        if applied:
            conn.execute(
                """INSERT INTO checkins (week, weight, waist, long_run_actual, swim_nonstop_actual, tt_5k_min, energy, notes, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(week) DO UPDATE SET weight=excluded.weight, waist=excluded.waist,
                     long_run_actual=excluded.long_run_actual, swim_nonstop_actual=excluded.swim_nonstop_actual,
                     tt_5k_min=excluded.tt_5k_min, energy=excluded.energy, notes=excluded.notes, updated_at=excluded.updated_at""",
                (week, body.weight, body.waist, body.long_run_actual, body.swim_nonstop_actual, body.tt_5k_min,
                 body.energy, body.notes, stamp),
            )
        row = [c for c in checkin_rows(conn) if c["week"] == week][0]
        return {"applied": applied, "checkin": row}
