"""Deterministic daily coach. Safety-critical rules live here, not in an AI model:

* readiness never changes the plan on one number alone: it needs at least two signals that agree
* the coach only ever makes a session easier; it never adds load beyond the planned progression
* persistent pain (same area on 2 of the last 7 days, or 3 of the last 14) stops progression for exercises
  that load that area and recommends a professional assessment
* strength progression changes one variable at a time (load OR reps), by at most 2.5 kg or 2 reps
Mirrored in app/lib/coach.dart so the phone gives the same answer offline.
"""

from __future__ import annotations

import datetime as dt
import re
from statistics import median
from typing import Any

PAIN_AREAS = {
    'knee': ('squat', 'lunge', 'split squat', 'step-up', 'wall sit', 'thruster', 'run'),
    'shin': ('run', 'calf', 'jump', 'burpee'),
    'calf or achilles': ('calf', 'run', 'jump', 'burpee'),
    'foot': ('run', 'calf', 'jump', 'burpee'),
    'hip': ('squat', 'lunge', 'deadlift', 'bridge', 'thrust', 'swing', 'run'),
    'hamstring': ('deadlift', 'good morning', 'nordic', 'hamstring', 'bridge', 'swing', 'run'),
    'lower back': ('deadlift', 'good morning', 'row', 'swing', 'carry', 'thruster', 'squat'),
    'shoulder': ('press', 'push-up', 'raise', 'dip', 'row', 'swim', 'pike', 'y-t-w', 'thruster'),
    'elbow or wrist': ('curl', 'push-up', 'dip', 'extension', 'row'),
    'other': (),
}


def num(v: Any) -> float | None:
    if isinstance(v, bool) or v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def D(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


# ---------------------------------------------------------------------------- readiness
def readiness(days: dict[str, dict], iso: str) -> dict:
    log = days.get(iso, {})
    t = D(iso)
    past = [d for k, d in days.items() if t - dt.timedelta(days=15) < D(k) < t]
    rhrs = [num(d.get('rhr')) for d in past if num(d.get('rhr'))]
    hrvs = [num(d.get('hrv')) for d in past if num(d.get('hrv'))]
    signals: list[tuple[str, int]] = []
    sh, sq, so, en, stv, rhr, hrv = (num(log.get(k)) for k in ('sleep_h', 'sleep_q', 'soreness', 'energy', 'stress', 'rhr', 'hrv'))
    if sh is not None:
        if sh < 6:
            signals.append((f'Short sleep ({sh:g} h)', 2))
        elif sh < 7:
            signals.append((f'Sleep under 7 h ({sh:g} h)', 1))
    if sq is not None and sq <= 2:
        signals.append(('Poor sleep quality', 1))
    if so is not None:
        if so >= 4:
            signals.append(('Heavy muscle soreness', 2))
        elif so >= 3:
            signals.append(('Moderate soreness', 1))
    if en is not None and en <= 2:
        signals.append(('Low energy', 1))
    if stv is not None and stv >= 4:
        signals.append(('High stress', 1))
    if rhr is not None and len(rhrs) >= 3:
        base = median(rhrs)
        if rhr >= base + 7:
            signals.append((f'Resting heart rate {rhr - base:.0f} bpm above your normal', 2))
        elif rhr >= base + 4:
            signals.append((f'Resting heart rate {rhr - base:.0f} bpm above your normal', 1))
    if hrv is not None and len(hrvs) >= 3 and hrv <= median(hrvs) * 0.85:
        signals.append(('HRV well below your normal', 1))
    if log.get('pain_today'):
        signals.append(('Pain reported today', 2))
    pts = sum(p for _, p in signals)
    n = len(signals)
    checked_in = any(log.get(k) is not None for k in ('sleep_h', 'sleep_q', 'soreness', 'energy', 'stress', 'rhr', 'hrv'))
    if n >= 3 and pts >= 5:
        level = 'red'
    elif n >= 2 and pts >= 3:
        level = 'amber'
    else:
        level = 'green'
    score = max(0, min(100, 100 - pts * 12)) if checked_in else None
    msg = {
        'green': 'Ready: train as planned.' if checked_in else 'Do the morning check-in so the coach can adjust today if needed.',
        'amber': "Take it easier today: the hard parts of today's sessions are reduced.",
        'red': "Recovery day: today's demanding sessions are swapped for easy movement and mobility.",
    }[level]
    if level == 'green' and n == 1:
        msg = f'Mostly ready. One sign to watch ({signals[0][0].lower()}): train as planned but keep easy parts truly easy.'
    return dict(level=level, score=score, signals=[s for s, _ in signals], message=msg, checked_in=checked_in)


# ---------------------------------------------------------------------------- pain
def persistent_pain(days: dict[str, dict], iso: str) -> list[str]:
    t = D(iso)
    counts7: dict[str, int] = {}
    counts14: dict[str, int] = {}
    for k, d in days.items():
        age = (t - D(k)).days
        if not 0 <= age < 14:
            continue
        areas = set(d.get('pain_areas') or [])
        if (num(d.get('knee_pain')) or 0) >= 3:
            areas.add('knee')
        for fb in ('am_fb', 'pm_fb'):
            f = d.get(fb) or {}
            if f.get('pain') and f.get('pain_area'):
                areas.add(f['pain_area'])
        for a in areas:
            counts14[a] = counts14.get(a, 0) + 1
            if age < 7:
                counts7[a] = counts7.get(a, 0) + 1
    return sorted(a for a in counts14 if counts7.get(a, 0) >= 2 or counts14[a] >= 3)


def loads_area(exercise: str, areas: list[str]) -> list[str]:
    e = exercise.lower()
    return [a for a in areas if any(w in e for w in PAIN_AREAS.get(a, ()))]


# ---------------------------------------------------------------------------- adjusting a session
def adjust(session: dict | None, level: str, pain: list[str], fasting_today: bool = False) -> dict | None:
    """What to do with a planned session today. Only ever makes it easier."""
    if not session:
        return None
    meta = session.get('meta') or {}
    disc = meta.get('discipline', '')
    code = session.get('code', '')
    hard = bool(meta.get('hard'))
    out = dict(key=session['key'], name=session['name'], action='as planned', note='')
    if code in ('FAST', 'REST', 'MOB', 'RACE'):
        return out
    if fasting_today:
        out.update(action='swap', note='You marked today as a fasting day: only an easy walk and mobility after breaking the fast. No demanding session.')
        return out
    run_pain = [a for a in pain if 'run' in PAIN_AREAS.get(a, ())]
    if disc in ('run', 'brick', 'hyrox') and run_pain:
        out.update(
            action='swap',
            note=f'Persistent {", ".join(run_pain)} pain: replace this run with an easy swim or a 30 min walk if pain-free, and book a physiotherapist or doctor assessment.',
        )
        return out
    if level == 'red' and (hard or disc in ('run', 'strength', 'hyrox', 'brick', 'bike')):
        out.update(
            action='swap', note='Recovery day: 20 to 30 min easy walk or an easy swim, plus the mobility routine and kegels. The session is not made up later.'
        )
    elif level == 'amber' and hard:
        if disc == 'strength':
            out.update(action='reduce', note='One set fewer on every exercise, same load, effort no more than 7 out of 10. Keep the kegel finisher.')
        elif disc == 'swim':
            out.update(action='reduce', note='Swim the drills and an easy continuous swim; skip the faster repeats.')
        else:
            out.update(action='reduce', note='Cut the main set by a third and keep the effort at 6 out of 10 or less (easy heart rate).')
    elif level == 'amber':
        out.update(action='as planned', note='Keep it truly easy today.')
    if pain and disc == 'strength' and out['action'] == 'as planned':
        out['note'] = (
            out['note'] + ' ' if out['note'] else ''
        ) + f'Persistent {", ".join(pain)} pain: do not add load to exercises that hurt; skip any that cause pain.'
    return out


# ---------------------------------------------------------------------------- strength progression
def rep_range(reps: str) -> tuple[int, int] | None:
    nums = [int(x) for x in re.findall(r'\d+', reps or '')]
    if not nums or ' s' in (reps or '') or 'm' in (reps or '').replace('min', ''):
        return None
    return (nums[0], nums[1] if len(nums) > 1 else nums[0])


def progression(history: list[dict], reps: str, pain_blocked: bool = False) -> dict:
    """history: logged sessions for one exercise, newest last: [{'date':..,'sets':[{'kg':..,'reps':..,'rpe':..}]}]"""
    rr = rep_range(reps)
    if pain_blocked:
        return dict(
            action='hold', text='Hold: you reported persistent pain in an area this exercise loads. Keep the load, skip it if it hurts, and get it assessed.'
        )
    if not history:
        return dict(action='start', text='First time: choose a load where the last 2 reps feel hard but clean (effort 7 out of 10). Log it.')
    if rr is None:
        return dict(action='repeat', text='Timed or distance exercise: add 5 s (or a few metres) once every set feels controlled.')
    last = [s for s in history[-1].get('sets', []) if num(s.get('reps')) is not None]
    if not last:
        return dict(action='repeat', text='Log reps for each set to get a suggestion.')
    lo, hi = rr
    reps_done = [num(s['reps']) for s in last]
    rpes = [num(s.get('rpe')) for s in last if num(s.get('rpe')) is not None]
    kg = max((num(s.get('kg')) or 0) for s in last)
    avg_rpe = sum(rpes) / len(rpes) if rpes else None
    if min(reps_done) < lo or (avg_rpe is not None and avg_rpe >= 9.5):
        missed_twice = len(history) >= 2 and any((num(s.get('reps')) or 0) < lo for s in history[-2].get('sets', []))
        if missed_twice and kg > 0:
            return dict(
                action='reduce', kg=round(kg * 0.9 * 2) / 2, text=f'Missed reps two sessions in a row: drop to {round(kg * 0.9 * 2) / 2:g} kg and rebuild.'
            )
        return dict(action='repeat', kg=kg, text=f'Repeat {kg:g} kg and aim for {lo} to {hi} clean reps on every set.')
    if min(reps_done) >= hi and (avg_rpe is None or avg_rpe <= 8):
        if kg > 0:
            inc = 1.0 if kg < 10 else (2.0 if kg < 40 else 2.5)
            return dict(
                action='add_load',
                kg=kg + inc,
                text=f'Every set hit {hi} reps: add {inc:g} kg (to {kg + inc:g} kg) and start again at {lo} reps. Do not change anything else.',
            )
        return dict(action='add_reps', text=f'Every set hit {hi} reps with bodyweight: add 1 to 2 reps per set, OR move to the harder version. Not both.')
    return dict(action='repeat', kg=kg, text=f'Same load ({kg:g} kg). Add a rep where you can until every set reaches {hi}.')


def exercise_history(days: dict[str, dict], plan_sessions: dict, exercise: str, before: str) -> list[dict]:
    out = []
    for iso in sorted(days):
        if iso >= before:
            continue
        sets = days[iso].get('sets') or {}
        for rid, lst in sets.items():
            name = None
            if lst and isinstance(lst[0], dict) and lst[0].get('ex'):
                name = lst[0]['ex']
            else:
                skey = rid.split(':')[0]
                try:
                    name = plan_sessions[skey]['rows'][int(rid.split(':')[1])]['ex']
                except (KeyError, IndexError, ValueError):
                    name = None
            if name == exercise:
                out.append({'date': iso, 'sets': lst})
    return out


# ---------------------------------------------------------------------------- load guard and streak
def run_load_warning(days: dict[str, dict], iso: str) -> str | None:
    t = D(iso)

    def week_km(k):
        a = t - dt.timedelta(days=7 * (k + 1))
        return sum(num(d.get('run_km')) or 0 for i, d in days.items() if a < D(i) <= a + dt.timedelta(days=7))

    this = week_km(0)
    prev = [week_km(k) for k in (1, 2, 3)]
    avg = sum(prev) / 3
    if avg >= 5 and this > avg * 1.3:
        return f'Your running this week ({this:.0f} km) is more than 30% above your recent average ({avg:.0f} km). Keep the rest of the week easy.'
    return None


def streak(plan_days: list[dict], days: dict[str, dict], iso: str) -> int:
    n = 0
    for pd in reversed([d for d in plan_days if d['date'] <= iso]):
        if not (pd.get('am') or pd.get('pm')):
            continue
        log = days.get(pd['date'], {})
        done = (pd.get('am') and log.get('am_done')) or (pd.get('pm') and log.get('pm_done'))
        if done:
            n += 1
        elif pd['date'] == iso:
            continue  # today is not over yet
        else:
            break
    return n


def today(plan: dict, days: dict[str, dict], iso: str) -> dict:
    pd = next((d for d in plan['days'] if d['date'] == iso), None)
    if not pd:
        return dict(date=iso, in_plan=False)
    log = days.get(iso, {})
    r = readiness(days, iso)
    pain = persistent_pain(days, iso)
    marked_fast = bool(log.get('fasting')) and not pd.get('fasting')
    sess = plan['sessions']
    out = dict(
        date=iso,
        in_plan=True,
        readiness=r,
        persistent_pain=pain,
        am=adjust(sess.get(pd['am']), r['level'], pain, marked_fast),
        pm=adjust(sess.get(pd['pm']), r['level'], pain, marked_fast),
        nutrition=dict(kcal=pd['kcal'], protein=pd['protein'], carbs=pd['carbs'], fat=pd['fat'], water_l=pd['water_l'], meal_plan=pd['meal_plan']),
        sleep='Target 7 to 9 hours: lights out by 22:00.',
        streak=streak(plan['days'], days, iso),
        load_warning=run_load_warning(days, iso),
    )
    if pain:
        out['pain_advice'] = (
            f'You have reported {", ".join(pain)} pain on several days. Progression is paused for exercises that load it. '
            'Please see a physiotherapist or doctor if it does not settle within a week, or straight away if it is sharp, swollen or getting worse.'
        )
    return out
