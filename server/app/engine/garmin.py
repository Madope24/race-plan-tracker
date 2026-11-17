"""Garmin Connect "Activities.csv" import. Missing values ("--") stay missing: nothing is invented."""

from __future__ import annotations

import csv
import io


def _num(v):
    if v is None:
        return None
    v = str(v).replace(',', '').strip()
    if v in ('', '--'):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _secs(v):
    """'00:59:05' or '00:05:58.6' or '17:16' (pace) -> seconds"""
    if not v or v.strip() in ('', '--'):
        return None
    parts = v.strip().split(':')
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        return None
    s = 0.0
    for p in parts:
        s = s * 60 + p
    return s


def kind_of(t: str) -> str:
    t = (t or '').lower()
    if 'swim' in t:
        return 'swim'
    if 'run' in t or 'walk' in t and 'hik' not in t:
        return 'run' if 'run' in t else 'walk'
    if 'cycl' in t or 'bik' in t or 'ride' in t:
        return 'bike'
    if 'strength' in t:
        return 'strength'
    return 'other'


MI = 1.609344


def run_unit(dist, steps, stride_m):
    """Garmin's CSV carries no unit. Steps x stride length gives the real distance in km: if that is about 1.6 times the
    Distance column, the export is in miles."""
    if not dist or not steps or not stride_m:
        return None
    ratio = steps * stride_m / 1000 / dist
    if 1.35 <= ratio <= 1.95:
        return 'mi'
    if 0.8 <= ratio <= 1.25:
        return 'km'
    return None


def parse(text: str, unit: str = 'auto') -> list[dict]:
    """unit: 'auto' (detect from steps and stride), 'km' or 'mi'. Run distances and paces are always stored in km."""
    rows = list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'))))
    out = []
    if unit == 'auto':
        votes = [run_unit(_num(r.get('Distance')), _num(r.get('Steps')), _num(r.get('Avg Stride Length'))) for r in rows]
        votes = [v for v in votes if v]
        unit = 'mi' if votes and votes.count('mi') > len(votes) / 2 else 'km'
    k_dist = MI if unit == 'mi' else 1.0
    for r in rows:
        typ = r.get('Activity Type', '')
        k = kind_of(typ)
        start = (r.get('Date') or '').strip()
        if not start:
            continue
        dist = _num(r.get('Distance'))
        a = dict(
            id=f'garmin-{start.replace(" ", "T")}-{k}',
            source='garmin_csv',
            type=k,
            garmin_type=typ,
            title=r.get('Title', ''),
            start=start,
            date=start[:10],
            duration_s=_secs(r.get('Time')),
            moving_s=_secs(r.get('Moving Time')),
            elapsed_s=_secs(r.get('Elapsed Time')),
            avg_hr=_num(r.get('Avg HR')),
            max_hr=_num(r.get('Max HR')),
            calories=_num(r.get('Calories')),
            aerobic_te=_num(r.get('Aerobic TE')),
        )
        if k == 'swim':
            # Garmin exports pool swims in metres, runs in kilometres
            a['distance_m'] = dist
            a['pace_100m_s'] = _secs(r.get('Avg Pace'))
            a['strokes'] = _num(r.get('Total Strokes'))
            a['swolf'] = _num(r.get('Avg. Swolf'))
            a['stroke_rate'] = _num(r.get('Avg Stroke Rate'))
            a['laps'] = _num(r.get('Number of Laps'))
            a['best_lap_s'] = _secs(r.get('Best Lap Time'))
        else:
            a['distance_km'] = round(dist * k_dist, 2) if dist is not None else None
            a['recorded_unit'] = unit
            pace, best = _secs(r.get('Avg Pace')), _secs(r.get('Best Pace'))
            a['pace_s_km'] = round(pace / k_dist) if pace else None
            a['best_pace_s_km'] = round(best / k_dist) if best else None
            a['cadence'] = _num(r.get('Avg Run Cadence'))
            a['ascent_m'] = _num(r.get('Total Ascent'))
            a['steps'] = _num(r.get('Steps'))
        out.append(a)
    out.sort(key=lambda a: a['start'])
    return out


def baseline(acts: list[dict]) -> dict:
    """Summary used to seed the plan. Only measured values; anything not in the file stays None."""
    runs = [a for a in acts if a['type'] == 'run' and a.get('distance_km')]
    swims = [a for a in acts if a['type'] == 'swim' and a.get('distance_m')]
    out: dict = {'activities': len(acts), 'runs': len(runs), 'swims': len(swims)}
    if acts:
        first, last = acts[0]['date'], acts[-1]['date']
        import datetime as dt

        span = max(1, (dt.date.fromisoformat(last) - dt.date.fromisoformat(first)).days + 1)
        out.update(first=first, last=last, sessions_per_week=round(len(acts) / span * 7, 1))
    if runs:
        longest = max(runs, key=lambda a: a['distance_km'])
        tot_km = sum(a['distance_km'] for a in runs)
        tot_s = sum(a.get('duration_s') or 0 for a in runs)
        hrs = [a['avg_hr'] for a in runs if a.get('avg_hr')]
        out.update(
            long_run_km=longest['distance_km'],
            long_run_date=longest['date'],
            run_km_total=round(tot_km, 2),
            run_pace_min_km=round(tot_s / 60 / tot_km, 1) if tot_km and tot_s else None,
            run_avg_hr=round(sum(hrs) / len(hrs)) if hrs else None,
            run_max_hr=max((a['max_hr'] for a in runs if a.get('max_hr')), default=None),
            run_best_pace_min_km=round(min(a['best_pace_s_km'] for a in runs if a.get('best_pace_s_km')) / 60, 2)
            if any(a.get('best_pace_s_km') for a in runs)
            else None,
        )
    if swims:
        tot_m = sum(a['distance_m'] for a in swims)
        moving = sum(a.get('moving_s') or 0 for a in swims)
        sw = [a['swolf'] for a in swims if a.get('swolf')]
        out.update(
            swim_session_m=round(tot_m / len(swims)),
            swim_longest_session_m=max(a['distance_m'] for a in swims),
            swim_pace_100m=round(moving / 60 / (tot_m / 100), 2) if moving else None,
            swim_swolf=round(sum(sw) / len(sw), 1) if sw else None,
            swim_strokes_avg=round(sum(a['strokes'] for a in swims if a.get('strokes')) / len(swims)),
            swim_cont_m=None,
        )  # not in the file: log your longest non-stop swim in the app
    return out
