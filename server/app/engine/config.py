"""Athlete configuration: the only input the plan engine needs.

Everything the athlete can change in the app (profile, race calendar, fasting, Ramadan, bike start, baseline)
lives here. The server stores a per-user copy; `merge()` fills anything missing from DEFAULT_CONFIG.
Changing a race date and rebuilding the plan moves every phase, taper and recovery week with it.
"""

from __future__ import annotations

import copy
import datetime as dt
from typing import Any

RACE_TYPES = ('run', 'hyrox', 'triathlon')
PRIORITIES = ('A', 'B', 'C')  # A = goal race, B = tune-up, C = optional (only placed on the calendar, never shapes it)

DEFAULT_CONFIG: dict[str, Any] = {
    'start': '2026-10-27',  # first training day (week 1 is the Monday of that week)
    'profile': {
        'name': 'Salum',
        'sex': 'male',
        'age': 26,
        'height_cm': 162,
        'location': 'Dar es Salaam, Tanzania',
        'start_weight': 87.5,
        'goal_weight': 82.0,
        'goal_weight_date': '2027-01-09',
        'end_weight': 77.0,
        'experience': 'New to racing. Started running in October 2026; already swimming.',
        'injuries': '',
        'medical': '',
        'allergies': '',
        'diet': 'No breakfast. At most one smoothie a day, not every day. No whey protein. No testosterone-booster blends.',
        'sleep_h': 7.5,
        'max_hr': 194,
        'hours_per_week': 9,
    },
    'equipment': ['Pool', 'Loaded backpack', 'Jerrycans', 'Water bottles', 'Sturdy chair', 'Bed or sofa'],
    'preferences': {
        'two_sessions': True,  # two sessions a day where the plan allows it (never on fasting days)
        'runs': 'morning',
        'swims': 'evening',
        'no_run_and_swim_same_day': False,  # run in the morning and swim in the evening may share a day
        'meals': 'two meals, no breakfast',
        'theme': 'dark',
    },
    # No weekly fasting since 25 Nov 2026. Add weekdays here (for example ['Thu']) to bring a fast day back.
    'fasting': {'weekdays': [], 'type': 'dry', 'break_time': '18:50'},
    # Expected Ramadan 1448 dates (the start depends on the moon sighting, about 7 or 8 Feb 2027). Set to null if not fasting.
    'ramadan': {'start': '2027-02-08', 'end': '2027-03-09'},
    'bike_start': '2027-03-15',  # cycling starts after Ramadan; nothing on a bike before this date
    'swim_test': '2027-03-12',  # 1,500 m non-stop test (first Friday after Ramadan; Sundays are home-workout days)
    'swim_test_target_min': 60,  # goal time for the 1,500 m: within 1 hour, without stopping
    # Baseline from Activities.csv (Garmin, 3 to 14 Nov 2026; the export is in miles, converted here). Update it any time.
    'baseline': {
        'long_run_km': 8.0,
        'long_run_date': '2026-11-14',
        'run_pace_min_km': 9.6,  # easy pace on 25 Nov 2026 (9:34 per km)
        'run_avg_hr': 149,
        'run_max_hr': 184,
        'swim_cont_m': 100,
        'swim_cont_date': '2026-10-29',
        'swim_pace_100m': 3.03,
        'swim_swolf': 35.4,
        'swim_session_m': 900,
    },
    # A current niggle. While it is active the plan holds the long run, swaps hard intervals for controlled race-pace work
    # on flat ground, uses knee-friendly strength exercises and adds a daily knee-care routine. Set to null when it has settled.
    'injury': {
        'area': 'knee',
        'since': '2026-11-14',
        'until': '2026-12-05',
        'note': 'A small pinch in the knee joint during the 8 km run in Dodoma on 14 Nov.',
    },
    # Phone reminders (the app schedules them on the phone; nothing is sent from the server).
    'reminders': {
        'checkin': '05:20',
        'workout_am': '05:30',
        'workout_pm': '17:15',
        'mobility': '06:45',
        'meal_1': '12:50',
        'meal_2': '19:50',
        'supplements': '13:15',
        'water_every_h': 2,
        'kegels': '21:00',
        'sleep': '21:30',
        'race_days_before': [7, 3, 1],
    },
    'races': [
        {
            'id': 'r10k',
            'name': '10 km race',
            'type': 'run',
            'date': '2026-12-05',
            'priority': 'A',
            'run_km': 10.0,
            'target_min': 100,
            'goal_id': 'Goal 2',
            'note': 'Target: under 1 h 40 (10:00 per km). If the knee is sore on the day, run 10:30 per km and finish around 1 h 45.',
        },
        {
            'id': 'rhalf',
            'name': 'Kilimanjaro half marathon',
            'type': 'run',
            'date': '2027-02-07',
            'priority': 'A',
            'run_km': 21.1,
            'target_min': 180,
            'goal_id': 'Goal 11',
            'note': 'Moshi: cooler than Dar, but hilly.',
        },
        {
            'id': 'rhyrox',
            'name': 'HYROX',
            'type': 'hyrox',
            'date': '2027-06-12',
            'priority': 'A',
            'division': 'Men Open',
            'target_min': 115,
            'goal_id': 'Goal 3',
            'note': 'Placeholder date in June: set the real event date when you book.',
        },
        {
            'id': 'rolympic',
            'name': 'Olympic triathlon (tune-up)',
            'type': 'triathlon',
            'date': '2027-07-11',
            'priority': 'B',
            'swim_m': 1500,
            'bike_km': 40,
            'run_km': 10.0,
            'target_min': 225,
            'goal_id': 'Goal 5',
            'note': 'Rehearsal for the 70.3.',
        },
        {
            'id': 'r703',
            'name': 'Ironman 70.3',
            'type': 'triathlon',
            'date': '2027-08-22',
            'priority': 'A',
            'swim_m': 1900,
            'bike_km': 90,
            'run_km': 21.1,
            'target_min': 510,
            'goal_id': 'Goal 4',
            'note': 'Placeholder date in August: set the real event date.',
        },
        {
            'id': 'r35',
            'name': '35 km run',
            'type': 'run',
            'date': None,
            'priority': 'C',
            'run_km': 35.0,
            'target_min': None,
            'note': 'Date not set. Coach advice: after the 70.3, not before it.',
        },
    ],
}


def D(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s) if s else None


def merge(user: dict[str, Any] | None) -> dict[str, Any]:
    """User settings on top of the defaults (one level deep for dict sections; lists replace)."""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    for k, v in (user or {}).items():
        if k not in cfg:
            continue
        if isinstance(cfg[k], dict) and isinstance(v, dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    return cfg


def validate(cfg: dict[str, Any]) -> list[str]:
    """Return a list of problems (empty = valid). Kept dependency-free so the engine can run anywhere."""
    errs: list[str] = []
    try:
        start = D(cfg['start'])
    except (TypeError, ValueError, KeyError):
        return ['start must be a date (YYYY-MM-DD)']
    ids = set()
    for r in cfg.get('races', []):
        if not isinstance(r, dict) or not r.get('id') or not r.get('name'):
            errs.append('every race needs an id and a name')
            continue
        if r['id'] in ids:
            errs.append(f'duplicate race id {r["id"]}')
        ids.add(r['id'])
        if r.get('type') not in RACE_TYPES:
            errs.append(f'{r["name"]}: type must be one of {", ".join(RACE_TYPES)}')
        if r.get('priority', 'A') not in PRIORITIES:
            errs.append(f'{r["name"]}: priority must be A, B or C')
        if r.get('date'):
            try:
                d = D(r['date'])
            except ValueError:
                errs.append(f'{r["name"]}: date must be YYYY-MM-DD')
                continue
            if d < start:
                errs.append(f'{r["name"]}: date is before the plan start')
            if (d - start).days > 420:
                errs.append(f'{r["name"]}: date is more than 60 weeks after the plan start')
    if not any(r.get('date') and r.get('priority', 'A') in ('A', 'B') for r in cfg.get('races', [])):
        errs.append('at least one dated A or B race is needed to build a plan')
    ram = cfg.get('ramadan')
    if ram:
        try:
            if D(ram['end']) < D(ram['start']):
                errs.append('Ramadan end is before its start')
        except (KeyError, TypeError, ValueError):
            errs.append('ramadan needs start and end dates, or null')
    t = cfg.get('swim_test_target_min')
    if t is not None and not (isinstance(t, (int, float)) and 15 <= t <= 120):
        errs.append('swim_test_target_min must be between 15 and 120, or null')
    for k in ('bike_start', 'swim_test'):
        if cfg.get(k):
            try:
                D(cfg[k])
            except ValueError:
                errs.append(f'{k} must be a date')
    inj = cfg.get('injury')
    if inj:
        try:
            if D(inj['until']) < D(inj['since']):
                errs.append('injury until is before since')
        except (KeyError, TypeError, ValueError):
            errs.append('injury needs area, since and until, or null')
    days = cfg.get('fasting', {}).get('weekdays', [])
    if not all(d in ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun') for d in days):
        errs.append('fasting weekdays must be Mon..Sun')
    b = cfg.get('baseline', {})
    for k, lo, hi in (('long_run_km', 0, 60), ('swim_cont_m', 0, 10000), ('run_pace_min_km', 3, 25)):
        v = b.get(k)
        if v is not None and not (isinstance(v, (int, float)) and lo <= v <= hi):
            errs.append(f'baseline {k} must be between {lo} and {hi}')
    return errs
