"""Goal, mini-goal and weekly-review calculations. Mirrors app/lib/logic.dart so the phone and the server agree."""

from __future__ import annotations

import datetime as dt
from typing import Any

D = dt.date.fromisoformat


def num(v: Any) -> float | None:
    if isinstance(v, bool) or v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def wavg(days: dict[str, dict], at: dt.date) -> float | None:
    vals = [num(d.get('weight')) for iso, d in days.items() if at - dt.timedelta(days=7) < D(iso) <= at]
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


def last_weigh_date(days: dict[str, dict]) -> dt.date | None:
    ds = [D(iso) for iso, d in days.items() if num(d.get('weight')) is not None]
    return max(ds) if ds else None


def current_weight(days):
    last = last_weigh_date(days)
    return wavg(days, last) if last else None


def max_of(days, field, upto: dt.date | None = None):
    vals = [num(d.get(field)) for iso, d in days.items() if upto is None or D(iso) <= upto]
    vals = [v for v in vals if v is not None and v > 0]
    return max(vals) if vals else None


def baseline(results, key):
    return num(results.get(f'base:{key}'))


def weekly(plan, days):
    by_week: dict[int, list[dict]] = {}
    for d in plan['days']:
        by_week.setdefault(d['week'], []).append(d)
    out, prev_avg = [], None
    for w in sorted(by_week):
        pds = by_week[w]
        logs = [(pd, days.get(pd['date'], {})) for pd in pds]
        weights = [num(l.get('weight')) for _, l in logs if num(l.get('weight')) is not None]
        avg_w = round(sum(weights) / len(weights), 1) if weights else None
        tgt = round(sum(pd['target_weight'] for pd in pds) / len(pds), 1)
        planned = sum((1 if (pd['am'] or pd['race']) else 0) + (1 if pd['pm'] else 0) for pd in pds)
        done = sum((1 if (pd['am'] or pd['race']) and l.get('am_done') else 0) + (1 if pd['pm'] and l.get('pm_done') else 0) for pd, l in logs)
        sleeps = [num(l.get('sleep_h')) for _, l in logs if num(l.get('sleep_h')) is not None]
        avg_sleep = round(sum(sleeps) / len(sleeps), 1) if sleeps else None
        prot = [(num(l.get('protein')), pd['protein']) for pd, l in logs if num(l.get('protein')) is not None]
        kcal = [num(l.get('kcal')) for _, l in logs if num(l.get('kcal')) is not None]
        gap = round(avg_w - tgt, 1) if avg_w is not None else None
        adherence = done / planned if planned else None
        if avg_w is None:
            status = '' if done == 0 else ('Training on track' if (adherence or 0) >= 0.8 else 'Train more consistently')
        elif gap > 1:
            status = 'BEHIND: apply the catch-up rule'
        elif gap < -1.5:
            status = 'TOO FAST: eat 150 kcal more'
        elif (adherence or 0) < 0.8:
            status = 'Weight OK, adherence low'
        else:
            status = 'ON TRACK'
        out.append(
            dict(
                week=w,
                start=pds[0]['date'] if w > 1 else plan['weeks'][0]['start'],
                phase=pds[0]['phase'],
                avg_weight=avg_w,
                target_weight=tgt,
                gap=gap,
                change=round(avg_w - prev_avg, 1) if (avg_w is not None and prev_avg is not None) else None,
                planned=planned,
                done=done,
                adherence=adherence,
                run_km=round(sum(num(l.get('run_km')) or 0 for _, l in logs), 1),
                swim_m=round(sum(num(l.get('swim_m')) or 0 for _, l in logs)),
                bike_km=round(sum(num(l.get('bike_km')) or 0 for _, l in logs), 1),
                avg_sleep=avg_sleep,
                sleep_ok=(avg_sleep >= 7.5) if avg_sleep is not None else None,
                protein_hit=sum(1 for v, t in prot if v >= t),
                protein_days=len(prot),
                avg_kcal=round(sum(kcal) / len(kcal)) if kcal else None,
                status=status,
            )
        )
        if avg_w is not None:
            prev_avg = avg_w
    return out


def planned_weight(plan, at: dt.date):
    for d in plan['days']:
        if d['date'] == at.isoformat():
            return d['target_weight']
    return None


def goal_current(plan, g, days, results, weeks):
    auto = g['auto']
    manual = num(results.get(f'goal:{g["id"]}'))
    if auto == 'race':
        return manual
    if auto == 'wavg':
        return current_weight(days)
    if auto == 'maxrun':
        return manual if manual is not None else max_of(days, 'run_km')
    if auto == 'maxswim':
        return max_of(days, 'swim_cont_m')
    if auto == 'maxbike':
        return max_of(days, 'bike_km')
    if auto == 'sleep':
        ws = [w for w in weeks if w['avg_sleep'] is not None]
        return (sum(1 for w in ws if w['sleep_ok']) / len(ws)) if ws else None
    if auto == 'protein':
        tot = sum(w['protein_days'] for w in weeks)
        return (sum(w['protein_hit'] for w in weeks) / tot) if tot else None
    return manual


def goal_baseline(g, results):
    if g['baseline'] is not None:
        return g['baseline']
    return {'Goal 6': baseline(results, 'swim'), 'Goal 8': baseline(results, 'pushups')}.get(g['id'])


def goal_status(plan, g, days, results, weeks, today: dt.date):
    cur = goal_current(plan, g, days, results, weeks)
    base = goal_baseline(g, results)
    tgt = g['target']
    manual = num(results.get(f'goal:{g["id"]}'))
    longest = None
    if g['auto'] == 'race':
        longest = max_of(days, 'run_km')
        met = manual is not None and manual <= tgt
        if manual is not None:
            prog = 1.0 if met else tgt / manual
        else:
            prog = None if longest is None else max(0.0, min(1.0, longest / g['distance_km']))
    else:
        met = cur is not None and (cur <= tgt if g['better'] == 'Lower' else cur >= tgt)
        if cur is None:
            prog = None
        elif base is not None and base != tgt:
            raw = (base - cur) / (base - tgt) if g['better'] == 'Lower' else (cur - base) / (tgt - base)
            prog = max(0.0, min(1.0, raw))
        elif g['better'] == 'Lower':
            prog = 1.0 if cur <= tgt else tgt / cur
        else:
            prog = max(0.0, min(1.0, cur / tgt)) if tgt else None
    deadline = D(g['deadline'])
    if met:
        status = 'Achieved'
    elif today > deadline:
        status = 'Log the result' if cur is None else 'Missed'
    elif g['auto'] == 'race' and manual is None:
        status = 'In progress' if longest is not None else 'Not started'
    elif cur is None:
        status = 'Not started'
    elif g['auto'] == 'wavg':
        last = last_weigh_date(days)
        pw = planned_weight(plan, last) if last else None
        status = 'On track' if pw is None or cur <= pw + 0.5 else 'Behind'
    else:
        status = 'In progress'
    return dict(
        id=g['id'],
        name=g['name'],
        deadline=g['deadline'],
        unit=g['unit'],
        baseline=base,
        target=tgt,
        current=cur,
        progress=prog,
        status=status,
        days_left=max(0, (deadline - today).days),
        longest_run_km=longest,
    )


def mini_target(plan, m, results):
    rule = m.get('rule')
    if not rule:
        return m['target']
    if rule['rule'] == 'weight_line':
        t = plan['targets']
        s, g = D(t['start_date']), D(t['goal_date'])
        due = D(m['due'])
        return round(t['start_weight'] - (t['start_weight'] - t['goal_weight']) * (due - s).days / (g - s).days, 1)
    b = baseline(results, rule['base'])
    if rule['rule'] == 'baseline_add':
        return None if b is None else b + rule['add']
    if rule['rule'] == 'double_or_30':
        return 30 if b is None else (b * 2 if b < 15 else 30)
    return m['target']


def mini_status(plan, m, days, results, today: dt.date):
    due = D(m['due'])
    manual = num(results.get(f'mini:{m["id"]}'))
    auto = None
    if m['auto'] == 'wavg':
        auto = wavg(days, due)
    elif m['auto'] in ('maxrun', 'maxswim', 'maxbike'):
        auto = max_of(days, {'maxrun': 'run_km', 'maxswim': 'swim_cont_m', 'maxbike': 'bike_km'}[m['auto']], due)
    actual = manual if manual is not None else auto
    tgt = mini_target(plan, m, results)
    if actual is None:
        status = 'Overdue: log it' if today > due else ('Due this week' if (due - today).days <= 7 else 'Upcoming')
    elif tgt is None:
        status = 'Logged'
    elif (m['better'] == 'Lower' and actual <= tgt) or (m['better'] == 'Higher' and actual >= tgt):
        status = 'Hit'
    else:
        status = 'Missed' if today > due else 'In progress'
    return dict(
        id=m['id'],
        goal=m['goal'],
        due=m['due'],
        text=m['text'],
        unit=m['unit'],
        target=tgt,
        from_log=auto,
        result=manual,
        actual=actual,
        status=status,
        days_left=max(0, (due - today).days),
    )


def summary(plan: dict, days: dict[str, dict], results: dict[str, Any], today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    weeks = weekly(plan, days)
    goals = [goal_status(plan, g, days, results, weeks, today) for g in plan['goals']]
    minis = [mini_status(plan, m, days, results, today) for m in plan['mini_goals']]
    cur = current_weight(days)
    t = plan['targets']
    return dict(
        today=today.isoformat(),
        current_weight=cur,
        lost=round(t['start_weight'] - cur, 1) if cur is not None else None,
        to_go=round(max(0.0, cur - t['goal_weight']), 1) if cur is not None else None,
        planned_weight_today=planned_weight(plan, today) or (t['start_weight'] if today < D(t['start_date']) else None),
        goals=goals,
        mini_goals=minis,
        weeks=weeks,
        totals=dict(
            run_km=round(sum(w['run_km'] for w in weeks), 1),
            swim_m=sum(w['swim_m'] for w in weeks),
            bike_km=round(sum(w['bike_km'] for w in weeks), 1),
            sessions_done=sum(w['done'] for w in weeks),
        ),
        mini_counts={s: sum(1 for m in minis if m['status'] == s) for s in ('Hit', 'Missed', 'Overdue: log it', 'In progress', 'Upcoming')},
    )
