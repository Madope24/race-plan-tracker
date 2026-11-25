"""EnduraForge API: accounts, athlete config and race calendar, generated plans, daily logs with history, results,
activity import, the daily coach, the goal summary and CSV export.

Every route is served under /api/v1 and (for the existing app versions) under /api.
"""

import csv
import hashlib
import io
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, UTC
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import ai, logic
from .db import Activity, DayLog, DayLogVersion, PlanVersion, Profile, Result, SessionLocal, User, init_db, now
from .engine import coach, garmin
from .engine.build import build_plan
from .engine.config import merge, validate
from .security import OptionalUserId, UserId, hash_password, make_token, verify_password

REGISTRATION_MODE = os.environ.get('REGISTRATION_MODE', 'first-only')  # first-only | open | closed
APP_VERSION = '2.3.0'

log = logging.getLogger('enduraforge')
logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'), format='%(message)s')


# ------------------------------------------------------------------ plans (built from each athlete's config, cached)
class PlanCache:
    def __init__(self):
        self._by_hash: dict[str, tuple[dict, str]] = {}

    def get(self, cfg: dict | None) -> tuple[dict, str]:
        h = hashlib.sha256(json.dumps(cfg or {}, sort_keys=True).encode()).hexdigest()
        if h not in self._by_hash:
            plan = build_plan(cfg)
            if len(self._by_hash) > 32:
                self._by_hash.clear()
            self._by_hash[h] = (plan, json.dumps(plan, ensure_ascii=False, separators=(',', ':')))
        return self._by_hash[h]


PLANS = PlanCache()
DEFAULT_PLAN, _ = PLANS.get(None)


@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(
    title='EnduraForge API',
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url='/api/docs',
    openapi_url='/api/openapi.json',
    description='Personal endurance, strength and performance platform. Plan rules are deterministic; see docs/architecture.',
)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


@app.middleware('http')
async def access_log(request: Request, call_next):
    t = time.perf_counter()
    try:
        resp = await call_next(request)
    except Exception:
        log.exception(json.dumps({'event': 'error', 'method': request.method, 'path': request.url.path}))
        raise
    if request.url.path not in ('/health', '/api/health'):
        log.info(
            json.dumps(
                {
                    'event': 'request',
                    'method': request.method,
                    'path': request.url.path,
                    'status': resp.status_code,
                    'ms': round((time.perf_counter() - t) * 1000, 1),
                }
            )
        )
    return resp


def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def user_config(uid: str | None, s: Session) -> dict | None:
    if not uid:
        return None
    row = s.get(Profile, uid)
    return json.loads(row.config) if row else None


def user_plan(uid: str | None, s: Session) -> tuple[dict, str]:
    return PLANS.get(user_config(uid, s))


# ------------------------------------------------------------------ validation of a day log
NUMERIC = {
    'weight': (20, 300),
    'waist': (30, 250),
    'sleep_h': (0, 24),
    'sleep_q': (1, 5),
    'run_km': (0, 200),
    'swim_m': (0, 20000),
    'swim_cont_m': (0, 20000),
    'bike_km': (0, 500),
    'kcal': (0, 10000),
    'protein': (0, 1000),
    'carbs': (0, 2000),
    'fat': (0, 1000),
    'water': (0, 20),
    'energy': (1, 5),
    'soreness': (1, 5),
    'stress': (1, 5),
    'rhr': (25, 220),
    'hrv': (0, 400),
    'run_min': (0, 1440),
    'run_hr': (40, 230),
    'swim_min': (0, 600),
    'swim_strokes': (0, 100000),
    'swolf': (5, 200),
    'bike_min': (0, 1440),
    'knee_pain': (0, 10),
}
BOOLS = {'am_done', 'pm_done', 'supps', 'kegels', 'smoothie', 'fasting', 'pain_today', 'skip_am', 'skip_pm', 'mobility'}
STR_LISTS = {'pain_areas': (10, 40), 'supps_taken': (20, 60), 'meals_eaten': (10, 60), 'extra': (4, 60)}
FEEDBACK = {'done': ('yes', 'partly', 'no')}


def _num_ok(k, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise HTTPException(422, f'{k} must be a number')
    if not lo <= v <= hi:
        raise HTTPException(422, f'{k} must be between {lo} and {hi}')
    return v


def clean_feedback(k, v):
    if not isinstance(v, dict):
        raise HTTPException(422, f'{k} must be an object')
    out = {}
    for fk, fv in v.items():
        if fv is None:
            continue
        if fk == 'done':
            if fv not in FEEDBACK['done']:
                raise HTTPException(422, f'{k}.done must be yes, partly or no')
            out[fk] = fv
        elif fk in ('rpe',):
            out[fk] = _num_ok(f'{k}.rpe', fv, 1, 10)
        elif fk in ('energy',):
            out[fk] = _num_ok(f'{k}.energy', fv, 1, 5)
        elif fk == 'minutes':
            out[fk] = _num_ok(f'{k}.minutes', fv, 0, 1440)
        elif fk == 'pain':
            if not isinstance(fv, bool):
                raise HTTPException(422, f'{k}.pain must be true or false')
            out[fk] = fv
        elif fk in ('pain_area', 'notes', 'difficulty'):
            if not isinstance(fv, str) or len(fv) > 500:
                raise HTTPException(422, f'{k}.{fk} must be text up to 500 characters')
            out[fk] = fv
        else:
            raise HTTPException(422, f'Unknown feedback field: {fk}')
    return out


def clean_day(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in data.items():
        if v is None or v == '':
            continue
        if k in NUMERIC:
            out[k] = _num_ok(k, v, *NUMERIC[k])
        elif k in BOOLS:
            if not isinstance(v, bool):
                raise HTTPException(422, f'{k} must be true or false')
            out[k] = v
        elif k == 'notes':
            if not isinstance(v, str) or len(v) > 2000:
                raise HTTPException(422, 'notes must be text up to 2,000 characters')
            out[k] = v
        elif k in STR_LISTS:
            n, ln = STR_LISTS[k]
            if not isinstance(v, list) or len(v) > n or not all(isinstance(x, str) and len(x) <= ln for x in v):
                raise HTTPException(422, f'{k} must be a list of up to {n} short texts')
            out[k] = v
        elif k in ('am_fb', 'pm_fb'):
            out[k] = clean_feedback(k, v)
        elif k == 'planned':
            if not isinstance(v, dict) or len(v) > 6 or not all(isinstance(x, str) and len(x) <= 120 for x in v.values()):
                raise HTTPException(422, 'planned must map am/pm to session names')
            out[k] = v
        elif k == 'done':
            if not isinstance(v, list) or len(v) > 400 or not all(isinstance(x, str) and len(x) < 60 for x in v):
                raise HTTPException(422, 'done must be a list of exercise ids')
            out[k] = sorted(set(v))
        elif k == 'sets':
            if not isinstance(v, dict) or len(v) > 200:
                raise HTTPException(422, 'sets must map exercise ids to set lists')
            sets = {}
            for item, lst in v.items():
                if not isinstance(lst, list) or len(lst) > 20:
                    raise HTTPException(422, 'each exercise can have at most 20 sets')
                rows = []
                for st in lst:
                    if not isinstance(st, dict):
                        raise HTTPException(422, 'a set is {"kg": number, "reps": number}')
                    row = {}
                    for name, hi in (('kg', 500), ('reps', 1000), ('rpe', 10)):
                        val = st.get(name)
                        if val is not None and (isinstance(val, bool) or not isinstance(val, (int, float)) or not 0 <= val <= hi):
                            raise HTTPException(422, f'set {name} must be between 0 and {hi}')
                        row[name] = val
                    if st.get('ex') is not None:
                        if not isinstance(st['ex'], str) or len(st['ex']) > 80:
                            raise HTTPException(422, 'set ex must be an exercise name')
                        row['ex'] = st['ex']
                    rows.append(row)
                sets[str(item)[:60]] = rows
            out[k] = sets
        else:
            raise HTTPException(422, f'Unknown field: {k}')
    return out


def parse_ts(s: str | None) -> datetime:
    if not s:
        return now()
    try:
        t = datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(422, 'updated_at must be an ISO date-time')
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def aware(t: datetime) -> datetime:
    return t if t.tzinfo else t.replace(tzinfo=UTC)


api = APIRouter()


# ------------------------------------------------------------------ health and plan
@app.get('/health')
@api.get('/health')
def health():
    return {'ok': True, 'version': APP_VERSION, 'plan_version': DEFAULT_PLAN['version'], 'days': len(DEFAULT_PLAN['days'])}


@api.get('/plan/version')
def plan_version(uid: str | None = OptionalUserId, s: Session = Depends(db)):
    return {'version': user_plan(uid, s)[0]['version']}


@api.get('/plan')
def plan(request: Request, uid: str | None = OptionalUserId, s: Session = Depends(db)):
    p, text = user_plan(uid, s)
    etag = f'"{p["version"]}"'
    if request.headers.get('if-none-match') == etag:
        return Response(status_code=304, headers={'ETag': etag})
    return Response(content=text, media_type='application/json', headers={'ETag': etag})


# ------------------------------------------------------------------ accounts
class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=200)

    @field_validator('email')
    @classmethod
    def norm(cls, v: str) -> str:
        v = v.strip().lower()
        if '@' not in v:
            raise ValueError('Enter a valid email address')
        return v


@api.post('/auth/register', status_code=201)
def register(body: Credentials, s: Session = Depends(db)):
    if REGISTRATION_MODE == 'closed':
        raise HTTPException(403, 'Registration is closed on this server')
    if REGISTRATION_MODE == 'first-only' and s.scalar(select(func.count()).select_from(User)) > 0:
        raise HTTPException(403, 'This server already has its account. Sign in instead.')
    if s.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(409, 'That email is already registered. Sign in instead.')
    u = User(id=str(uuid.uuid4()), email=body.email, pw_hash=hash_password(body.password))
    s.add(u)
    s.commit()
    return {'token': make_token(u.id), 'email': u.email}


@api.post('/auth/login')
def login(body: Credentials, s: Session = Depends(db)):
    u = s.scalar(select(User).where(User.email == body.email))
    if not u or not verify_password(body.password, u.pw_hash):
        raise HTTPException(401, 'Wrong email or password')
    return {'token': make_token(u.id), 'email': u.email}


@api.get('/auth/me')
def me(uid: str = UserId, s: Session = Depends(db)):
    u = s.get(User, uid)
    if not u:
        raise HTTPException(401, 'Account not found. Sign in again.')
    return {'email': u.email, 'created_at': u.created_at.isoformat()}


# ------------------------------------------------------------------ athlete config and race calendar
class ConfigIn(BaseModel):
    config: dict[str, Any]
    updated_at: str | None = None


def save_config(uid: str, cfg: dict, s: Session, ts: datetime | None = None) -> dict:
    full = merge(cfg)
    errs = validate(full)
    if errs:
        raise HTTPException(422, '; '.join(errs))
    try:
        p, _ = PLANS.get(cfg)
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(422, f'Could not build a plan from these settings: {e}')
    row = s.get(Profile, uid)
    ts = ts or now()
    if row:
        row.config, row.updated_at, row.server_at = json.dumps(cfg), ts, now()
    else:
        s.add(Profile(user_id=uid, config=json.dumps(cfg), updated_at=ts, server_at=now()))
    last = s.scalar(select(PlanVersion).where(PlanVersion.user_id == uid).order_by(PlanVersion.id.desc()))
    if not last or last.version != p['version']:
        s.add(PlanVersion(user_id=uid, version=p['version'], config=json.dumps(cfg)))
    s.commit()
    return {'config': full, 'plan_version': p['version'], 'days': len(p['days']), 'start': p['start'], 'end': p['end']}


@api.get('/config')
def get_config(uid: str = UserId, s: Session = Depends(db)):
    row = s.get(Profile, uid)
    cfg = json.loads(row.config) if row else {}
    p, _ = PLANS.get(cfg or None)
    return {'config': merge(cfg), 'custom': cfg, 'updated_at': aware(row.updated_at).isoformat() if row else None, 'plan_version': p['version']}


@api.put('/config')
def put_config(body: ConfigIn, uid: str = UserId, s: Session = Depends(db)):
    ts = parse_ts(body.updated_at)
    row = s.get(Profile, uid)
    if row and aware(row.updated_at) > ts:
        cfg = json.loads(row.config)
        return {'config': merge(cfg), 'applied': False, 'plan_version': PLANS.get(cfg)[0]['version']}
    return {**save_config(uid, body.config, s, ts), 'applied': True}


class RaceIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    type: str
    date: str | None = None
    priority: str = 'A'
    run_km: float | None = Field(default=None, ge=0, le=250)
    swim_m: float | None = Field(default=None, ge=0, le=10000)
    bike_km: float | None = Field(default=None, ge=0, le=1000)
    target_min: float | None = Field(default=None, ge=1, le=3000)
    division: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=300)
    goal_id: str | None = Field(default=None, max_length=20)


def _races(uid, s):
    cfg = user_config(uid, s) or {}
    return cfg, list(merge(cfg)['races'])


@api.get('/races')
def list_races(uid: str = UserId, s: Session = Depends(db)):
    return {'races': _races(uid, s)[1]}


@api.post('/races', status_code=201)
def add_race(body: RaceIn, uid: str = UserId, s: Session = Depends(db)):
    cfg, races = _races(uid, s)
    r = {k: v for k, v in body.model_dump().items() if v is not None}
    r['id'] = 'r' + uuid.uuid4().hex[:8]
    races.append(r)
    cfg['races'] = races
    return {**save_config(uid, cfg, s), 'race': r}


@api.put('/races/{rid}')
def edit_race(rid: str, body: RaceIn, uid: str = UserId, s: Session = Depends(db)):
    cfg, races = _races(uid, s)
    for i, r in enumerate(races):
        if r['id'] == rid:
            new = {k: v for k, v in body.model_dump().items() if v is not None}
            if body.date is None:
                new['date'] = None
            races[i] = {**{k: v for k, v in r.items() if k == 'goal_id'}, **new, 'id': rid}
            cfg['races'] = races
            return {**save_config(uid, cfg, s), 'race': races[i]}
    raise HTTPException(404, 'No race with that id')


@api.delete('/races/{rid}')
def delete_race(rid: str, uid: str = UserId, s: Session = Depends(db)):
    cfg, races = _races(uid, s)
    keep = [r for r in races if r['id'] != rid]
    if len(keep) == len(races):
        raise HTTPException(404, 'No race with that id')
    cfg['races'] = keep
    return save_config(uid, cfg, s)


@api.get('/plan/history')
def plan_history(uid: str = UserId, s: Session = Depends(db)):
    rows = s.scalars(select(PlanVersion).where(PlanVersion.user_id == uid).order_by(PlanVersion.id.desc()).limit(50)).all()
    return {'versions': [{'version': r.version, 'created_at': aware(r.created_at).isoformat()} for r in rows]}


# ------------------------------------------------------------------ day logs (history is kept)
class DayIn(BaseModel):
    data: dict[str, Any]
    updated_at: str | None = None


def day_out(r: DayLog) -> dict:
    return {'date': r.date, 'data': json.loads(r.data), 'updated_at': aware(r.updated_at).isoformat(), 'server_at': aware(r.server_at).isoformat()}


def valid_date(iso: str) -> date:
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        raise HTTPException(422, 'Use a date like 2026-11-10')
    if not date(2025, 1, 1) <= d <= date(2029, 12, 31):
        raise HTTPException(404, f'{iso} is outside the supported range')
    return d


@api.put('/days/{iso}')
def put_day(iso: str, body: DayIn, uid: str = UserId, s: Session = Depends(db)):
    valid_date(iso)
    data = clean_day(body.data)
    ts = parse_ts(body.updated_at)
    row = s.get(DayLog, (uid, iso))
    if row and aware(row.updated_at) > ts:
        return {**day_out(row), 'applied': False}  # the server already has a newer copy
    if row:
        s.add(DayLogVersion(user_id=uid, date=iso, data=row.data, updated_at=row.updated_at))
        row.data, row.updated_at, row.server_at = json.dumps(data), ts, now()
    else:
        row = DayLog(user_id=uid, date=iso, data=json.dumps(data), updated_at=ts, server_at=now())
        s.add(row)
    s.commit()
    return {**day_out(row), 'applied': True}


@api.get('/days/{iso}')
def get_day(iso: str, uid: str = UserId, s: Session = Depends(db)):
    row = s.get(DayLog, (uid, iso))
    if not row:
        raise HTTPException(404, 'Nothing logged for that day')
    return day_out(row)


@api.get('/days/{iso}/history')
def day_history(iso: str, uid: str = UserId, s: Session = Depends(db)):
    rows = s.scalars(select(DayLogVersion).where(DayLogVersion.user_id == uid, DayLogVersion.date == iso).order_by(DayLogVersion.id)).all()
    return {'date': iso, 'versions': [{'data': json.loads(r.data), 'updated_at': aware(r.updated_at).isoformat()} for r in rows]}


# ------------------------------------------------------------------ results: baselines, goal and mini-goal results
class ResultIn(BaseModel):
    value: float | None
    updated_at: str | None = None


def valid_key(key: str, plan: dict) -> bool:
    prefix, _, rest = key.partition(':')
    if prefix == 'base':
        return rest in {b['key'] for b in plan['baselines']}
    if prefix == 'goal':
        return rest in {g['id'] for g in plan['goals']}
    if prefix == 'mini':
        return 0 < len(rest) <= 110  # mini ids move with the plan; old results are kept, not rejected
    return False


@api.put('/results/{key}')
def put_result(key: str, body: ResultIn, uid: str = UserId, s: Session = Depends(db)):
    if not valid_key(key, user_plan(uid, s)[0]):
        raise HTTPException(404, 'Unknown result key. Use base:<baseline>, goal:<goal id> or mini:<mini id>.')
    if body.value is not None and not -100000 <= body.value <= 100000:
        raise HTTPException(422, 'value out of range')
    ts = parse_ts(body.updated_at)
    row = s.get(Result, (uid, key))
    if row and aware(row.updated_at) > ts:
        return {'key': key, 'value': json.loads(row.value), 'applied': False}
    if row:
        row.value, row.updated_at, row.server_at = json.dumps(body.value), ts, now()
    else:
        s.add(Result(user_id=uid, key=key, value=json.dumps(body.value), updated_at=ts, server_at=now()))
    s.commit()
    return {'key': key, 'value': body.value, 'applied': True}


# ------------------------------------------------------------------ activities (Garmin CSV now; other adapters later)
class ImportIn(BaseModel):
    csv: str = Field(min_length=10, max_length=5_000_000)
    apply_baseline: bool = False


def upsert_activities(uid: str, acts: list[dict], s: Session) -> int:
    n = 0
    for a in acts:
        if not isinstance(a, dict) or not a.get('id') or not a.get('date') or len(str(a['id'])) > 80:
            raise HTTPException(422, 'each activity needs an id and a date')
        valid_date(str(a['date'])[:10])
        row = s.get(Activity, (uid, a['id']))
        if row:
            row.data, row.type, row.date, row.server_at = json.dumps(a), str(a.get('type', 'other'))[:20], a['date'][:10], now()
        else:
            s.add(
                Activity(
                    user_id=uid,
                    id=a['id'],
                    date=a['date'][:10],
                    type=str(a.get('type', 'other'))[:20],
                    source=str(a.get('source', 'app'))[:30],
                    data=json.dumps(a),
                    server_at=now(),
                )
            )
            n += 1
    s.commit()
    return n


@api.post('/activities/import')
def import_activities(body: ImportIn, uid: str = UserId, s: Session = Depends(db)):
    try:
        acts = garmin.parse(body.csv)
    except Exception:
        raise HTTPException(422, 'That does not look like a Garmin Activities.csv export')
    if not acts:
        raise HTTPException(422, 'No activities found in the file')
    added = upsert_activities(uid, acts, s)
    base = garmin.baseline(acts)
    out = {'imported': len(acts), 'new': added, 'baseline': base}
    if body.apply_baseline:
        cfg = user_config(uid, s) or {}
        b = dict(merge(cfg)['baseline'])
        for k in ('long_run_km', 'long_run_date', 'run_pace_min_km', 'run_avg_hr', 'run_max_hr', 'swim_pace_100m', 'swim_swolf', 'swim_session_m'):
            if base.get(k) is not None:
                b[k] = base[k]
        cfg['baseline'] = b
        out['plan'] = save_config(uid, cfg, s)
    return out


@api.put('/activities')
def put_activities(acts: list[dict[str, Any]], uid: str = UserId, s: Session = Depends(db)):
    if len(acts) > 1000:
        raise HTTPException(422, 'Send at most 1,000 activities at a time')
    return {'new': upsert_activities(uid, acts, s)}


@api.get('/activities')
def get_activities(since: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    q = select(Activity).where(Activity.user_id == uid)
    if since:
        q = q.where(Activity.server_at > parse_ts(since))
    return {'activities': [json.loads(r.data) for r in s.scalars(q.order_by(Activity.date)).all()]}


# ------------------------------------------------------------------ sync: everything changed since a server time
@api.get('/sync')
def sync(since: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    t = parse_ts(since) if since else datetime(2000, 1, 1, tzinfo=UTC)
    stamp = now()
    days = s.scalars(select(DayLog).where(DayLog.user_id == uid, DayLog.server_at > t)).all()
    res = s.scalars(select(Result).where(Result.user_id == uid, Result.server_at > t)).all()
    acts = s.scalars(select(Activity).where(Activity.user_id == uid, Activity.server_at > t)).all()
    prof = s.get(Profile, uid)
    out = {
        'server_time': stamp.isoformat(),
        'days': [day_out(r) for r in days],
        'results': [{'key': r.key, 'value': json.loads(r.value), 'updated_at': aware(r.updated_at).isoformat()} for r in res],
        'activities': [json.loads(r.data) for r in acts],
        'plan_version': user_plan(uid, s)[0]['version'],
    }
    if prof and aware(prof.server_at) > t:
        out['config'] = {'config': json.loads(prof.config), 'updated_at': aware(prof.updated_at).isoformat()}
    return out


def load_user(uid: str, s: Session):
    days = {r.date: json.loads(r.data) for r in s.scalars(select(DayLog).where(DayLog.user_id == uid))}
    results = {r.key: json.loads(r.value) for r in s.scalars(select(Result).where(Result.user_id == uid))}
    return days, results


@api.get('/summary')
def summary(today: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    days, results = load_user(uid, s)
    t = date.fromisoformat(today) if today else None
    return logic.summary(user_plan(uid, s)[0], days, results, t)


# ------------------------------------------------------------------ the daily coach
@api.get('/coach/today')
def coach_today(day: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    days, _ = load_user(uid, s)
    iso = day or date.today().isoformat()
    valid_date(iso)
    return coach.today(user_plan(uid, s)[0], days, iso)


@api.get('/coach/explain')
def coach_explain(day: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    """Today's recommendation in words. The facts come from the deterministic coach; AI (if configured) only phrases them."""
    days, _ = load_user(uid, s)
    iso = day or date.today().isoformat()
    valid_date(iso)
    facts = coach.today(user_plan(uid, s)[0], days, iso)
    return {'facts': facts, **ai.explain(facts)}


@api.get('/coach/progression')
def coach_progression(exercise: str, reps: str = '8 to 10', day: str | None = None, uid: str = UserId, s: Session = Depends(db)):
    days, _ = load_user(uid, s)
    iso = day or date.today().isoformat()
    plan_ = user_plan(uid, s)[0]
    hist = coach.exercise_history(days, plan_['sessions'], exercise, iso)
    blocked = bool(coach.loads_area(exercise, coach.persistent_pain(days, iso)))
    return {'exercise': exercise, 'history': hist[-5:], **coach.progression(hist, reps, blocked)}


# ------------------------------------------------------------------ export
def safe(v):
    return "'" + v if isinstance(v, str) and v[:1] in '=+-@' else v  # no spreadsheet formulas from notes


@api.get('/export/days.csv')
def export_csv(uid: str = UserId, s: Session = Depends(db)):
    days, _ = load_user(uid, s)
    p = user_plan(uid, s)[0]
    pdays = {d['date']: d for d in p['days']}
    cols = [
        'weight',
        'waist',
        'sleep_h',
        'sleep_q',
        'soreness',
        'energy',
        'stress',
        'rhr',
        'am_done',
        'pm_done',
        'run_km',
        'run_min',
        'swim_m',
        'swim_cont_m',
        'swolf',
        'bike_km',
        'kcal',
        'protein',
        'carbs',
        'fat',
        'water',
        'supps',
        'kegels',
        'fasting',
    ]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['date', 'week', 'phase', 'planned_am', 'planned_pm', 'target_weight', 'kcal_target'] + cols + ['exercises_done', 'notes'])
    for iso in sorted(days):
        d, pd = days[iso], pdays.get(iso, {})
        planned = d.get('planned') or {}
        row = [iso, pd.get('week', ''), pd.get('phase', ''), planned.get('am', ''), planned.get('pm', ''), pd.get('target_weight', ''), pd.get('kcal', '')]
        row += [d.get(c, '') for c in cols] + [len(d.get('done', [])), d.get('notes', '')]
        w.writerow([safe(v) for v in row])
    return Response(content=buf.getvalue(), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="enduraforge-days.csv"'})


@api.get('/export/activities.csv')
def export_activities(uid: str = UserId, s: Session = Depends(db)):
    rows = [json.loads(r.data) for r in s.scalars(select(Activity).where(Activity.user_id == uid).order_by(Activity.date)).all()]
    cols = ['date', 'type', 'title', 'distance_km', 'distance_m', 'duration_s', 'avg_hr', 'max_hr', 'pace_s_km', 'pace_100m_s', 'strokes', 'swolf', 'source']
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for a in rows:
        w.writerow([safe(a.get(c, '')) for c in cols])
    return Response(content=buf.getvalue(), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="enduraforge-activities.csv"'})


app.include_router(api, prefix='/api/v1')
app.include_router(api, prefix='/api')
