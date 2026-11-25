"""SMART goals and their mini goals, generated from the config and the calendar so they move when race dates move.

auto: how the current value is computed
  wavg = 7-day average weight        maxrun / maxswim / maxbike = longest logged run (km) / non-stop swim (m) / ride (km)
  race = longest run vs race distance until you type your time, then your time vs the target
  manual = you type the result       sleep / protein = share of weeks / days on target
"""

from __future__ import annotations

import datetime as dt
import re

from .config import D


def hm(minutes):
    h, m = divmod(int(minutes), 60)
    if not h:
        return f'{m} min'
    return f'{h} h {m:02d}' if m else f'{h} hours'


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:28]


def build_goals(cfg, cal):
    p = cfg['profile']
    start = cal.first_day
    end = cal.last_day
    goals, minis = [], []

    def G(gid, area, name, spec, meas, ach, rel, deadline, unit, base, target, better, auto, distance_km=None):
        goals.append(
            dict(
                id=gid,
                area=area,
                name=name,
                specific=spec,
                measurable=meas,
                achievable=ach,
                relevant=rel,
                deadline=deadline.isoformat(),
                unit=unit,
                baseline=base,
                target=target,
                better=better,
                auto=auto,
                distance_km=distance_km,
            )
        )

    def M(gid, due, text, unit, target, better, auto, rule=None):
        minis.append(
            dict(
                id=f'm-{slug(gid)}-{due.isoformat()}-{slug(text)}',
                goal=gid,
                due=due.isoformat(),
                text=text,
                unit=unit,
                target=target,
                rule=rule,
                better=better,
                auto=auto,
            )
        )

    # ---- weight
    sw, gw, gdate = p['start_weight'], p['goal_weight'], D(p['goal_weight_date'])
    weeks = max(1, (gdate - start).days / 7)
    G(
        'Goal 1',
        'Weight',
        f'Reach {gw:.1f} kg',
        f'Bring my 7-day average body weight from {sw} kg to {gw:.1f} kg by {gdate:%d %b %Y}.',
        '7-day average of morning weigh-ins (after the toilet, before food).',
        f'{sw - gw:.1f} kg in {weeks:.0f} weeks is about {(sw - gw) / weeks:.2f} kg a week with a moderate deficit, three strength sessions and 160 g protein a day.',
        'Lighter = easier running and racing; better blood pressure and blood sugar.',
        gdate,
        'kg',
        sw,
        gw,
        'Lower',
        'wavg',
    )
    d = start + dt.timedelta(days=12)
    while d < gdate:
        M('Goal 1', d, 'Weigh-in average on track', 'kg', None, 'Lower', 'wavg', {'rule': 'weight_line'})
        d += dt.timedelta(days=14)
    M('Goal 1', gdate, f'GOAL: {gw:.1f} kg 7-day average', 'kg', gw, 'Lower', 'wavg')
    M(
        'Goal 1',
        start + dt.timedelta(days=26),
        'Waist down 3 cm from baseline (enter waist in cm)',
        'cm',
        None,
        'Lower',
        'manual',
        {'rule': 'baseline_add', 'base': 'waist', 'add': -3},
    )
    M('Goal 1', gdate, 'Waist down 7 cm from baseline', 'cm', None, 'Lower', 'manual', {'rule': 'baseline_add', 'base': 'waist', 'add': -7})
    ew = p.get('end_weight')
    if ew:
        G(
            'Goal 7',
            'Weight',
            'Keep it off and lean out further',
            f'After {gdate:%d %b}, keep a 7-day average under {gw + 1:.0f} kg and reach {ew:.1f} kg by {end:%d %b %Y}.',
            'Same daily weigh-ins.',
            'Small deficit (250 to 400 kcal) while training volume rises; never under-fuel long sessions.',
            'Power-to-weight for racing without hurting recovery or hormones.',
            end,
            'kg',
            gw,
            ew,
            'Lower',
            'wavg',
        )

    # ---- races
    for r in cal.races:
        gid = r.get('goal_id')
        if not gid or r.get('priority') == 'C':
            continue
        rd = D(r['date'])
        t = r.get('target_min')
        if r['type'] == 'run':
            km = r['run_km']
            G(
                gid,
                'Running',
                f'{r["name"]} in under {hm(t)}',
                f'Finish the {km:g} km {r["name"]} on {rd:%a %d %b %Y} in under {hm(t)} ({t} minutes).',
                'Official or watch time. Type it in Your result.',
                f'Needs {t / km:.1f} min per km with walk breaks. The long run builds gradually with easier weeks; progress shows your longest run against {km:g} km until race day.',
                'A key race on the way to the 70.3.',
                rd,
                'min',
                None,
                t,
                'Lower',
                'race',
                distance_km=km,
            )
            prev_race = max([D(x['date']) for x in cal.key_races if D(x['date']) < rd], default=start - dt.timedelta(days=1))
            best = 0.0
            anchor = D(cfg.get('baseline', {}).get('long_run_date')) if cfg.get('baseline', {}).get('long_run_date') else start
            for c in cal.weeks:
                sat = c['monday'] + dt.timedelta(days=5)
                if prev_race < sat < rd and sat >= anchor and c['wtype'] == 'build' and c['long_km'] and c['long_km'] >= best + 1.5 and c['long_km'] >= 5:
                    best = c['long_km']
                    M(gid, sat, f'Long run {best:g} km', 'km', best, 'Higher', 'maxrun')
            M(gid, rd, f'GOAL: {r["name"]} under {hm(t)} (enter minutes)', 'min', t, 'Lower', 'manual')
        elif r['type'] == 'hyrox':
            G(
                gid,
                'HYROX',
                f'Finish HYROX ({r.get("division", "Men Open")})',
                f'Complete HYROX {r.get("division", "Men Open")} singles on {rd:%d %b %Y} in {hm(t)} or less.',
                'Official result, or your stopwatch for a full simulation at race weights.',
                '7 weeks of station work, compromised runs and simulations on top of the run and triathlon base. First-timer finishes are commonly 1 h 30 to 2 h.',
                'Functional strength-endurance that also makes you a stronger triathlete.',
                rd,
                'min',
                None,
                t,
                'Lower',
                'manual',
            )
            for c in cal.weeks:
                sat = c['monday'] + dt.timedelta(days=5)
                if c['kind'] == 'hyrox' and c['wtype'] == 'build' and c['alt'] and sat < rd:
                    M(gid, sat, 'HYROX simulation done (enter minutes)', 'min', None, 'Lower', 'manual')
            M(gid, rd, 'GOAL: HYROX finish (enter minutes)', 'min', t, 'Lower', 'manual')
        else:
            full = (r.get('bike_km') or 0) >= 60
            G(
                gid,
                'Triathlon',
                f'Finish the {r["name"]}',
                f'Complete {r.get("swim_m", 0):,} m swim, {r.get("bike_km", 0):g} km bike and {r.get("run_km", 0):g} km run on {rd:%d %b %Y} in {hm(t)} or less.',
                'Official result.',
                (
                    'Cycling from March, long rides building to about 3 h 15, long swims to 2.3 km and runs off the bike, then a two-week taper. '
                    '8 h 30 is the usual 70.3 cut-off.'
                    if full
                    else 'A rehearsal of pacing, transitions and fuelling 6 weeks before the 70.3.'
                ),
                'The season goal.' if full else 'Builds confidence and race skills for the 70.3.',
                rd,
                'min',
                None,
                t,
                'Lower',
                'manual',
            )
            if full:
                for km in (40, 60, 80):
                    due = None
                    for c in cal.weeks:
                        if c['ride_min'] and c['ride_min'] * 24 / 60 >= km and c['wtype'] == 'build':
                            due = c['monday'] + dt.timedelta(days=6)
                            break
                    if due and due < rd:
                        M(gid, due, f'Ride {km} km non-stop', 'km', km, 'Higher', 'maxbike')
                M(gid, rd - dt.timedelta(days=70), 'Open-water swim 1,500 m with a buddy', 'm', 1500, 'Higher', 'manual')
                M(gid, rd - dt.timedelta(days=20), 'Race-fuelling rehearsal: 60 g carbs an hour for a full long ride', 'rides', 1, 'Higher', 'manual')
            M(gid, rd, f'GOAL: {r["name"]} finish (enter minutes)', 'min', t, 'Lower', 'manual')

    # ---- swim 1.5 km
    st = cal.swim_test or end
    G(
        'Goal 6',
        'Swimming',
        'Swim 1,500 m non-stop' + (f' in under {cfg["swim_test_target_min"]} min' if cfg.get('swim_test_target_min') else ''),
        f'Swim 1,500 m of continuous freestyle without stopping by {st:%a %d %b %Y}'
        + (
            f', in under {cfg["swim_test_target_min"]} minutes ({cfg["swim_test_target_min"] * 60 / 15 // 60:.0f}:{cfg["swim_test_target_min"] * 60 / 15 % 60:02.0f} per 100 m).'
            if cfg.get('swim_test_target_min')
            else '.'
        ),
        'Longest non-stop swim (m), logged after every endurance swim. Test swim on the day.',
        'Three evening swims a week: technique swims on Tuesday and Thursday (drills, breathing, sighting, even-pace 50s) and the Friday non-stop swim, which grows about 100 to 150 m in normal weeks. Sundays are home workouts only.',
        'The Olympic swim distance, reached early, so the 1.9 km 70.3 swim is the next step.',
        st,
        'm',
        None,
        1500,
        'Higher',
        'maxswim',
    )
    M('Goal 6', start + dt.timedelta(days=(4 - start.weekday()) % 7), 'Baseline: longest non-stop swim (Friday evening test)', 'm', None, 'Higher', 'maxswim')
    last = 0
    for c in cal.weeks:
        sun = c['monday'] + dt.timedelta(days=4)  # the Friday non-stop swim
        if sun >= st:
            break
        v = c['swim_cont'] or 0
        if c['wtype'] in ('build', 'recovery') and v >= last + 200 and v >= 400:
            last = v
            M('Goal 6', sun, f'Swim {v:,} m non-stop', 'm', v, 'Higher', 'maxswim')
    M(
        'Goal 6',
        st,
        'GOAL: swim 1,500 m non-stop' + (f' within {cfg["swim_test_target_min"]} min' if cfg.get('swim_test_target_min') else '') + ' (test day)',
        'm',
        1500,
        'Higher',
        'maxswim',
    )

    # ---- strength, sleep, protein
    s_due = min(end, start + dt.timedelta(days=180))
    G(
        'Goal 8',
        'Strength',
        'Double my push-ups',
        f'Do at least 30 full push-ups in one set (or double your baseline if it is under 15) by {s_due:%d %b %Y}.',
        'Max push-ups test: chest to a fist from the floor, full lockout.',
        'Push-ups twice a week, from incline to feet-elevated, with tempo and load.',
        'Upper-body strength for HYROX, swimming and the physique you want.',
        s_due,
        'reps',
        None,
        30,
        'Higher',
        'manual',
    )
    M('Goal 8', start, 'Baseline: max push-ups (enter reps)', 'reps', None, 'Higher', 'manual')
    M(
        'Goal 8',
        start + dt.timedelta(days=38),
        'Push-ups: baseline + 5',
        'reps',
        None,
        'Higher',
        'manual',
        {'rule': 'baseline_add', 'base': 'pushups', 'add': 5},
    )
    M(
        'Goal 8',
        start + dt.timedelta(days=122),
        'Push-ups: baseline + 10',
        'reps',
        None,
        'Higher',
        'manual',
        {'rule': 'baseline_add', 'base': 'pushups', 'add': 10},
    )
    M('Goal 8', s_due, 'GOAL: 30 push-ups (or double the baseline)', 'reps', 30, 'Higher', 'manual', {'rule': 'double_or_30', 'base': 'pushups'})
    G(
        'Goal 12',
        'Strength',
        'Strong hamstrings',
        f'Complete 3 x 5 controlled Nordic hamstring lowers (at least 3 s each, full range) by {s_due:%d %b %Y}.',
        'Reps with a 3-s lower, logged in the strength session.',
        'Hamstring work every week: walkouts, towel curls, then Nordics from February.',
        'Hamstrings protect you from the most common running injury and power the HYROX sled and lunges.',
        s_due,
        'reps',
        None,
        15,
        'Higher',
        'manual',
    )
    G(
        'Goal 9',
        'Sleep',
        'Sleep 7.5 h',
        'Average 7.5 h of sleep or more in at least 80% of weeks.',
        'Hours slept logged daily.',
        'Fixed wake time, lights out by 22:00, caffeine only before 12:00, phone outside the bedroom.',
        'Sleep drives fat loss, recovery, hormones and mood.',
        end,
        '% of weeks',
        0,
        0.8,
        'Higher',
        'sleep',
    )
    M('Goal 9', start + dt.timedelta(days=12), 'Two weeks of lights out by 22:00 on 6 of 7 nights', 'nights', 12, 'Higher', 'manual')
    G(
        'Goal 10',
        'Nutrition',
        'Hit protein daily',
        'Eat at least your daily protein target on at least 85% of logged days.',
        'Protein grams logged daily.',
        'Every meal in the meal plan is built on 40 to 60 g protein from local foods.',
        'Protects muscle while losing fat and speeds recovery.',
        end,
        '% of days',
        0,
        0.85,
        'Higher',
        'protein',
    )
    if any(r['type'] == 'triathlon' for r in cal.key_races):
        r703 = next((r for r in cal.key_races if (r.get('bike_km') or 0) >= 60), None)
        if r703:
            due = D(r703['date']) - dt.timedelta(days=14)
            G(
                'Goal 13',
                'Cycling',
                'Ride 80 km non-stop',
                f'Ride 80 km in one go at easy endurance effort by {due:%d %b %Y}.',
                'Longest ride (km) from your logs or watch.',
                'Long rides grow about 15 min a week from mid-March, with easier weeks.',
                'The 70.3 bike is 90 km: 80 km in training means race day is within reach.',
                due,
                'km',
                None,
                80,
                'Higher',
                'maxbike',
            )
    minis.sort(key=lambda m: (m['due'], m['goal']))
    return goals, minis
