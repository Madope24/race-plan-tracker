"""Training-plan business rules (the safety-critical ones from the product brief)."""

import copy
import datetime as dt

import pytest

from app.engine import howto as HT
from app.engine import sessions as S
from app.engine.build import build_plan
from app.engine.config import DEFAULT_CONFIG

PLAN = build_plan()
DAYS = {d['date']: d for d in PLAN['days']}
SES = PLAN['sessions']
RUNS = S.RUN_CODES
HEAVY = ('STR-A', 'STR-B', 'STR-D', 'HX-S', 'HX-SIM', 'RUN-I', 'RUN-L', 'BRICK', 'BIKE-I', 'BIKE-L', 'SWIM-T')


def codes(d):
    return [SES[k]['code'] for k in (d['am'], d['pm']) if k]


def test_plan_covers_the_calendar():
    assert PLAN['start'] == '2026-10-27' and PLAN['end'] == '2027-08-22'
    assert DAYS['2026-12-05']['race'].startswith('10 KM RACE')
    assert DAYS['2027-02-07']['race'].startswith('KILIMANJARO HALF MARATHON')
    assert DAYS['2027-06-12']['race'].startswith('HYROX')
    assert DAYS['2027-07-11']['race'].startswith('OLYMPIC TRIATHLON')
    assert DAYS['2027-08-22']['race'].startswith('IRONMAN 70.3')
    assert '35 km' not in ' '.join(d['race'] or '' for d in PLAN['days'])  # undated race is not placed


def test_runs_morning_swims_evening():
    for d in PLAN['days']:
        if d['pm']:
            assert SES[d['pm']]['code'] not in RUNS, d['date']
        if d['am']:
            assert not SES[d['am']]['code'].startswith('SWIM'), d['date']


def test_run_and_swim_never_share_a_day_when_the_athlete_forbids_it():
    p = build_plan({'preferences': {'no_run_and_swim_same_day': True}})
    ses = p['sessions']
    for d in p['days']:
        c = [ses[k]['code'] for k in (d['am'], d['pm']) if k]
        assert not (any(x in RUNS for x in c) and any(x.startswith('SWIM') for x in c)), d['date']


def test_hard_days_together_and_legs_fresh_for_the_long_session():
    by_date = {d['date']: d for d in PLAN['days']}
    for d in PLAN['days']:
        if d['am'] and SES[d['am']]['code'] in ('RUN-L', 'BRICK', 'HX-SIM'):
            day = dt.date.fromisoformat(d['date'])
            for back in (1, 2):  # no leg strength in the 2 days before the long session
                prev = by_date.get((day - dt.timedelta(days=back)).isoformat())
                if prev:
                    assert not any(x in ('STR-A', 'STR-C', 'HX-S') for x in codes(prev)), d['date']
    # three strength sessions in a normal run week: two lower body, one upper
    week = [codes(DAYS[(dt.date(2026, 12, 14) + dt.timedelta(days=i)).isoformat()]) for i in range(7)]
    flat = [c for day in week for c in day]
    assert flat.count('STR-A') == 1 and flat.count('STR-C') == 1 and flat.count('STR-B') == 1
    assert sum(1 for c in flat if c in ('RUN-I', 'RUN-E', 'RUN-S', 'RUN-L')) == 4
    assert sum(1 for c in flat if c.startswith('SWIM')) == 3
    sunday = week[6]
    assert not any(c.startswith('SWIM') or c in S.RUN_CODES for c in sunday)  # Sundays: home workouts only
    assert any(any(c.startswith('RUN') for c in day) and any(c.startswith('SWIM') for c in day) for day in week)


def test_knee_care_while_the_niggle_is_active():
    assert PLAN['injury']['area'] == 'knee' and len(PLAN['injury']['advice']) >= 4
    for d in PLAN['days']:
        inside = '2026-11-14' <= d['date'] <= '2026-12-05'
        assert d['knee_care'] == inside, d['date']
        assert ('KNEE' in d['mobility']) == inside and 'AM-MOB' in d['mobility']
        if not inside or d['date'] < '2026-11-16':
            continue
        for k in (d['am'], d['pm']):
            if not k:
                continue
            s = SES[k]
            names = ' '.join(r['ex'].lower() for r in s['rows'] if r['block'] in ('Main', 'Accessory', 'Core', 'Kegel finisher'))
            if s['strength']:
                for bad in ('bulgarian', 'lunge', 'goblet', 'pause squat', 'deep squat', 'nordic'):
                    assert bad not in names, (d['date'], bad)
            if s['code'] == 'RUN-I':
                assert 'hard' not in s['summary'].lower() and 'sprint' not in s['summary'].lower().replace('no sprints', '')
            if s['code'] in ('RUN-I', 'RUN-E', 'RUN-L'):
                assert any(r['block'] == 'Knee check' for r in s['rows']), d['date']
    # the long run is held, not increased, while the knee settles
    assert [w['long_run_km'] for w in PLAN['weeks'] if '2026-11-09' <= w['start'] <= '2026-11-16'] == [8.0, 8.0]
    healthy = build_plan({'injury': None})
    assert not any(d['knee_care'] for d in healthy['days'])
    assert any('Bulgarian' in r['ex'] for r in healthy['sessions']['4-STR-C']['rows'])


def test_mobility_and_kegels_every_day():
    for d in PLAN['days']:
        assert d['mobility'] and d['kegels'], d['date']
    circuit = [r['ex'] for r in SES['8-STR-A']['rows'] if r['block'] == 'Kegel finisher']
    assert circuit == ['Slow kegel holds', 'Quick kegel squeezes', 'Kegel glute bridge', 'Deep squat hold with kegel', 'Relaxation breathing']


def test_garmin_miles_are_detected_and_converted():
    from app.engine import garmin

    runs = [a for a in PLAN['seed_activities'] if a['type'] == 'run']
    assert all(a['recorded_unit'] == 'mi' for a in runs)
    dodoma = next(a for a in runs if a['date'] == '2026-11-14')
    assert dodoma['distance_km'] == 8.01 and 630 <= dodoma['pace_s_km'] <= 645  # 4.98 mi at 17:06 per mile
    assert garmin.run_unit(8.0, 11320, 0.69) == 'km' and garmin.run_unit(4.98, 11320, 0.69) == 'mi'
    assert garmin.parse(open(garmin.__file__.replace('garmin.py', 'data/Activities.csv')).read(), unit='km')[0]['distance_km'] in (2.88, 1.79)


def test_no_weekly_fast_by_default_and_a_fast_day_still_works_when_set():
    assert any(codes(d) == ['RUN-I', 'STR-A'] for d in PLAN['days'] if d['weekday'] == 'Mon')
    assert not any(d['fasting'] for d in PLAN['days'] if not d['ramadan'])
    thu = [d for d in PLAN['days'] if d['weekday'] == 'Thu' and not d['race'] and not d['ramadan'] and '2026-12-07' <= d['date'] <= '2027-01-10']
    assert thu and all(codes(d) == ['RUN-S', 'SWIM-T'] for d in thu)  # Thursday: easy run in the morning, technique swim in the evening
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg['fasting']['weekdays'] = ['Thu']
    p = build_plan(cfg)
    for d in p['days']:
        if d['weekday'] == 'Thu' and not d['race']:
            assert [p['sessions'][k]['code'] for k in (d['am'], d['pm']) if k] == ['FAST'], d['date']
            assert d['fasting']


def test_ramadan_days_have_at_most_one_light_session():
    ram = [d for d in PLAN['days'] if d['ramadan'] and not d['race']]
    assert ram and ram[0]['date'] == '2027-02-08' and ram[-1]['date'] == '2027-03-09'
    for d in ram:
        c = [x for x in codes(d) if x not in ('REST', 'MOB')]
        assert len(c) <= 1, d['date']
        assert not any(x in HEAVY for x in c), d['date']


def test_no_cycling_before_the_bike_start():
    for d in PLAN['days']:
        if d['date'] < '2027-03-15':
            assert not any(x in S.BIKE_CODES for x in codes(d)), d['date']
    assert any(x == 'BIKE-L' for d in PLAN['days'] if d['date'] >= '2027-03-15' for x in codes(d))


def test_kegels_warmup_and_cooldown_in_every_strength_workout():
    n = 0
    for s in SES.values():
        if s['strength']:
            n += 1
            blocks = {r['block'] for r in s['rows']}
            assert {'Warm-up', 'Kegel finisher', 'Cool-down stretch'} <= blocks, s['key']
            assert 'Kegel finisher' in s['summary']
    assert n > 50


def test_every_exercise_has_sets_reps_and_instructions():
    lib = {e['name'] for e in PLAN['library']}
    for s in SES.values():
        if s['strength']:
            for r in s['rows']:
                if r['block'] in ('Main', 'Accessory', 'Core'):
                    assert r['sets'] and r['reps'] and r['rest'], (s['key'], r['ex'])
                    assert r['ex'] in lib, r['ex']
    for name in (
        'Bodyweight squat',
        'Walking lunge',
        'Step-up',
        'Towel hamstring curl',
        'Pallof press',
        'Mountain climber',
        'Reverse crunch',
        'Lying leg raise',
        'Water-bottle front raise',
        'Resistance-band row',
        'Overhead triceps extension',
        'Diamond push-up',
        'Pike push-up',
    ):
        assert name in lib
    for e in PLAN['library']:
        assert e['how'] and e['breathing'] and e['mistakes'] and e['equipment'] and e['difficulty'], e['name']
        if e['cat'] in ('Legs', 'Legs / Hyrox', 'Upper body', 'Core', 'Hyrox', 'Swim drill'):
            assert e['easier'] and e['harder'], e['name']


def test_swim_drills_have_full_details_and_rotate():
    lib = {e['name']: e for e in PLAN['library']}
    for name in PLAN['swim_drills']:
        e = lib[name]
        assert e['cat'] == 'Swim drill'
        for k in ('purpose', 'setup', 'how', 'breathing', 'cues', 'mistakes', 'easier', 'harder', 'dose'):
            assert e[k], (name, k)
        assert e['how'].count(') ') >= 2, name
    used = {r['ex'] for s in SES.values() for r in s['rows'] if r['block'] == 'Drills'}
    assert len(used) >= 12
    assert used <= set(PLAN['swim_drills'])


def test_every_warm_up_stretch_and_swim_row_links_to_instructions():
    lib = {e['name'] for e in PLAN['library']}
    blocks = ('Warm-up', 'Warm-up on the pool deck', 'Warm-up in the water', 'Cool-down stretch', 'Cool-down in the water', 'Mobility', 'Drills')
    for s in SES.values():
        for r in s['rows']:
            if r['block'] in blocks:
                assert r['lib'] in lib, (s['key'], r['ex'])
    for w in PLAN['warmups']:
        for i in w['items']:
            assert HT.link(i['name']) or i['name'] == 'First exercise, light', i['name']


def test_injury_prevention_and_knee_safe_swimming():
    ip = PLAN['injury_prevention']
    assert len(ip['running']) >= 8 and len(ip['swimming']) >= 8 and ip['stop_signs']
    knee_swims = [s for d in PLAN['days'] if d['knee_care'] for k in (d['am'], d['pm']) if k and (s := SES[k])['code'].startswith('SWIM')]
    assert knee_swims
    for s in knee_swims:
        assert any('no breaststroke kick' in r['ex'] for r in s['rows']), s['key']
    for d in PLAN['days']:
        codes = [SES[k]['code'] for k in (d['am'], d['pm']) if k]
        if any(c in ('SWIM-T', 'SWIM-E') for c in codes):
            assert 'SHOULDER' in d['mobility'], d['date']
        if any(c in ('RUN-E', 'RUN-L', 'RUN-I') for c in codes):
            run = SES[d['am']] if d['am'] and SES[d['am']]['code'].startswith('RUN') else None
            if run:
                assert any(r['block'] == 'Form' for r in run['rows']), d['date']


def test_progression_is_gradual():
    prev = None
    for w in PLAN['weeks']:
        km = w['long_run_km']
        if km and prev and w['type'].startswith('Build'):
            assert km <= prev + 2.0 + 1e-9 or km <= prev * 1.35, w  # never more than +2 km or +35 % a week
        if km:
            prev = km if w['type'].startswith('Build') else prev
        if w['type'].startswith('Race week'):  # the race itself counts as the longest run so far
            r = next(
                r for r in PLAN['races'] if r.get('date') and w['start'] <= r['date'] <= (dt.date.fromisoformat(w['start']) + dt.timedelta(days=6)).isoformat()
            )
            prev = max(prev or 0, 0.8 * (r.get('run_km') or 0))
    ws = PLAN['weeks']
    assert all(b['swim_cont_m'] - a['swim_cont_m'] <= 150 for a, b in zip(ws, ws[1:]) if a['type'] == b['type'] == 'Build')
    # an easier week at least every 5 weeks of build
    run = 0
    for w in PLAN['weeks']:
        run = run + 1 if w['type'] == 'Build' else 0
        assert run <= 4, w


def test_long_run_reaches_the_race_needs():
    before_10k = max(w['long_run_km'] or 0 for w in PLAN['weeks'] if w['start'] < '2026-11-30')
    before_half = max(w['long_run_km'] or 0 for w in PLAN['weeks'] if '2026-12-07' <= w['start'] < '2027-02-01')
    assert 8 <= before_10k <= 9.5  # 8 km done on 14 Nov, held while the knee settles
    assert before_half >= 12
    jan = max(w['long_run_km'] or 0 for w in PLAN['weeks'] if '2026-12-07' <= w['start'] < '2027-01-11')
    assert jan >= 12  # 12 km long run before the 15 Jan 5 km time trial
    assert any('1,500 m NON-STOP TEST' in r['ex'] for r in SES[DAYS['2027-03-12']['pm']]['rows'])


def test_breakfast_is_never_forced():
    for name, plan in PLAN['nutrition']['meal_plans'].items():
        for day, p in plan.items():
            assert not any('breakfast' in m['meal'].lower() for m in p['meals']), (name, day)
            for m in p['meals']:
                assert m['tzs'] > 0 and m['how'] and m['totals']['kcal'] > 0
    fast = PLAN['nutrition']['meal_plans']['FAST']['Mon']['meals']
    assert min(m['time'] for m in fast) >= '18:50'  # nothing before the fast breaks


def test_at_most_one_smoothie_and_not_every_day():
    sm = [d for d in PLAN['days'] if d['smoothie']]
    assert 0 < len(sm) < len(PLAN['days']) / 2
    assert not any(d['fasting'] for d in sm)


def test_supplements_have_full_information_and_no_boosters():
    names = ' '.join(s['name'].lower() for s in PLAN['supplements'])
    for need in ('creatine', 'omega-3', 'vitamin d', 'k2', 'magnesium', 'zinc', 'electrolytes', 'protein powder'):
        assert need in names
    for bad in ('tongkat', 'fadogia', 'tribulus', 'whey ', 'booster'):
        assert bad not in names
    for s in PLAN['supplements']:
        assert s['purpose'] and s['evidence'] and s['dose'] and s['when'] and s['side_effects'] and s['cautions']
    assert 'no good evidence' in ' '.join(PLAN['pelvic']['rules'])


def test_hyrox_has_all_stations_and_divisions():
    assert [s['name'] for s in PLAN['hyrox']['stations']] == [
        'SkiErg',
        'Sled push',
        'Sled pull',
        'Burpee broad jumps',
        'Rowing',
        'Farmers carry',
        'Sandbag lunges',
        'Wall balls',
    ]
    assert set(PLAN['hyrox']['divisions']) == {'Men Open', 'Men Pro', 'Women Open', 'Women Pro'}
    assert all(s['home'] for s in PLAN['hyrox']['stations'])


def test_moving_a_race_moves_the_calendar():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    for r in cfg['races']:
        if r['id'] == 'rhyrox':
            r['date'] = '2027-06-26'
    p = build_plan({'races': cfg['races']})
    days = {d['date']: d for d in p['days']}
    assert days['2027-06-26']['race'].startswith('HYROX')
    assert days['2027-06-12']['race'] is None
    hy = [w for w in p['weeks'] if w['kind'] == 'hyrox']
    assert hy[-1]['start'] == '2027-06-21'
    assert p['version'] != PLAN['version']


def test_turning_off_two_a_days_and_ramadan():
    p = build_plan({'preferences': {'two_sessions': False}, 'ramadan': None})
    ses = p['sessions']
    real = lambda k: k and ses[k]['code'] not in ('REST', 'MOB')
    assert all(not (real(d['am']) and real(d['pm'])) for d in p['days'])
    assert not any(d['ramadan'] for d in p['days'])
    assert any(ses[d['am']]['code'] == 'RUN-L' for d in p['days'] if d['am'] and d['date'] == '2027-02-20')


def test_invalid_config_is_rejected():
    with pytest.raises(ValueError):
        build_plan({'races': [{'id': 'x', 'name': 'x', 'type': 'swimrun', 'date': '2027-01-01'}]})
    with pytest.raises(ValueError):
        build_plan({'races': []})


def test_goals_follow_the_races():
    g = {x['id']: x for x in PLAN['goals']}
    assert g['Goal 2']['deadline'] == '2026-12-05' and g['Goal 2']['target'] == 100 and g['Goal 2']['auto'] == 'race'
    assert g['Goal 11']['deadline'] == '2027-02-07' and g['Goal 11']['target'] == 180
    assert g['Goal 4']['name'] == 'Finish the Ironman 70.3' and g['Goal 6']['deadline'] == '2027-03-12'
    for x in PLAN['goals']:
        assert x['specific'] and x['measurable'] and x['achievable'] and x['relevant'] and x['deadline']
    ids = [m['id'] for m in PLAN['mini_goals']]
    assert len(ids) == len(set(ids))


def test_weight_line():
    assert DAYS['2027-01-09']['target_weight'] == 82.0 and DAYS['2027-08-22']['target_weight'] == 77.0
    assert all(d['kcal'] >= 1500 and d['fat'] >= 65 for d in PLAN['days'])


def test_seeded_history_from_activities_csv():
    assert len(PLAN['seed_activities']) == 7
    b = PLAN['import_baseline']
    assert b['long_run_km'] == 8.01 and b['swim_swolf'] == 34.7 and b['swim_cont_m'] is None


def test_day_after_each_race_is_easy():
    for iso, d in DAYS.items():
        if d['race']:
            nxt = DAYS.get((dt.date.fromisoformat(iso) + dt.timedelta(days=1)).isoformat())
            if nxt:
                assert not any(x in HEAVY for x in codes(nxt)), iso
