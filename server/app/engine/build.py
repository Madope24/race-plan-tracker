"""Builds the complete plan document (days, sessions, goals, libraries, nutrition) from an athlete config."""

from __future__ import annotations

import datetime as dt
import hashlib
import json

import os

from . import extras as X
from . import garmin as GA
from . import howto as HT
from . import hyrox as HX
from . import library as LB
from . import nutrition as N
from . import sessions as S
from .config import D, merge, validate
from .goals import build_goals

ENGINE_VERSION = '2.3.0'
FOOD = {f[0]: f for f in N.FOODS}
_SEED_CSV = os.path.join(os.path.dirname(__file__), 'data', 'Activities.csv')
SEED = GA.parse(open(_SEED_CSV, encoding='utf-8').read()) if os.path.exists(_SEED_CSV) else []


def food_item(key, g):
    f = FOOD[key]
    return dict(
        food=f[1],
        key=key,
        grams=g,
        kcal=round(f[4] * g / 100),
        p=round(f[5] * g / 100, 1),
        c=round(f[6] * g / 100, 1),
        f=round(f[7] * g / 100, 1),
        tzs=int(round(N.PRICE.get(key, 0) * g / 1000)),
    )


def meal_plans():
    out = {}
    for name, rows in (('CUT', N.CUT), ('FUEL', N.FUEL), ('FAST', N.FAST), ('RAMADAN', N.RAMADAN)):
        plan = {}
        for day in S.DAYS:
            meals = []
            for d, meal, time, key, g in rows:
                if d != day:
                    continue
                if not meals or meals[-1]['meal'] != meal:
                    meals.append(dict(meal=meal, time=time, items=[]))
                meals[-1]['items'].append(food_item(key, g))
            for m in meals:
                m['totals'] = {k: round(sum(i[k] for i in m['items']), 1) for k in ('kcal', 'p', 'c', 'f')}
                m['tzs'] = N.meal_cost([(i['key'], i['grams']) for i in m['items']])
                m['how'] = N.meal_prep([i['key'] for i in m['items']])
            tot = {k: round(sum(i[k] for m in meals for i in m['items'])) for k in ('kcal', 'p', 'c', 'f')}
            tot['tzs'] = sum(m['tzs'] for m in meals)
            plan[day] = dict(meals=meals, totals=tot)
        out[name] = plan
    return out


def shopping_list(plans, cfg):
    """Weekly shopping list from the meal plans actually used in a typical week."""
    fast = cfg.get('fasting', {}).get('weekdays', [])
    out = {}
    for name in ('CUT', 'FUEL', 'RAMADAN'):
        grams = {}
        for day in S.DAYS:
            src = 'FAST' if (day in fast and name != 'RAMADAN') else name
            for m in plans[src][day]['meals']:
                for i in m['items']:
                    grams[i['key']] = grams.get(i['key'], 0) + i['grams']
        rows = []
        for k, g in sorted(grams.items(), key=lambda kv: (FOOD[kv[0]][3], kv[0])):
            f = FOOD[k]
            where = (
                'Fish / butcher'
                if f[3] == 'Protein' and k not in ('mayai', 'sardini', 'supu')
                else 'Soko / market'
                if f[3] in ('Vegetable', 'Fruit', 'Fat') or k in ('viazi_v', 'viazi', 'ndizi_p', 'mihogo')
                else 'Supermarket / duka'
            )
            rows.append(
                dict(
                    where=where,
                    item=f[1],
                    key=k,
                    grams=g,
                    amount=(f'{g / 1000:.1f} kg' if g >= 1000 else f'{g} g') + ' as eaten',
                    tzs=int(round(N.PRICE.get(k, 0) * g / 1000 / 100) * 100),
                )
            )
        rows.sort(key=lambda r: (r['where'], r['item']))
        out[name] = dict(rows=rows, total=sum(r['tzs'] for r in rows))
    return out


def bmr(cfg, w):
    p = cfg['profile']
    return 10 * w + 6.25 * p['height_cm'] - 5 * p['age'] + (5 if p.get('sex', 'male') == 'male' else -161)


def target_weight(cfg, cal, d):
    p = cfg['profile']
    s, g, e = cal.first_day, D(p['goal_weight_date']), cal.last_day
    sw, gw, ew = p['start_weight'], p['goal_weight'], p.get('end_weight') or p['goal_weight']
    if d <= g:
        v = sw - (sw - gw) * (d - s).days / max(1, (g - s).days)
    else:
        v = gw - (gw - ew) * (d - g).days / max(1, (e - g).days)
    return round(v, 1)


def build_plan(user_cfg: dict | None = None) -> dict:
    cfg = merge(user_cfg)
    errs = validate(cfg)
    if errs:
        raise ValueError('; '.join(errs))
    cal = S.Calendar(cfg)
    p = cfg['profile']
    gdate = D(p['goal_weight_date'])
    sessions: dict[str, dict] = {}
    lib_rx: dict[str, tuple] = {}

    def add(code, c, d):
        if code is None:
            return None
        key = f'{c["w"]}-{code}' + (f'-{d.isoformat()}' if code in ('RACE', 'SWIM-E') and (d in cal.race_on or d == cal.swim_test) else '')
        if key not in sessions:
            rows = S.session_rows(code, c, cal, d)
            for r in rows:
                if r[1] in LB.L and r[1] not in lib_rx and r[2] not in ('', None):
                    lib_rx[r[1]] = (r[2], str(r[3]), r[4])
            sessions[key] = dict(
                key=key,
                code=code,
                week=c['w'],
                name=S.session_name(code, c, cal, d),
                summary=S.summary(code, rows, c),
                strength=code in S.STRENGTH_CODES,
                meta=S.session_meta(code, rows, c, cfg),
                rows=[
                    dict(id=f'{key}:{i}', block=r[0], ex=r[1], lib=HT.row_link(code, r[0], r[1]), sets=r[2], reps=str(r[3]), rest=r[4], note=r[5])
                    for i, r in enumerate(rows)
                ],
            )
        return key

    days = []
    d = cal.first_day
    i = 0
    fast_days = cal.fast_days
    while d <= cal.last_day:
        w = (d - cal.monday).days // 7 + 1
        c = cal.weeks[w - 1]
        wd = S.DAYS[d.weekday()]
        am, pm = cal.day_codes(d)
        race = cal.race_on.get(d)
        ramadan = cal.is_ramadan(d)
        fasting = (wd in fast_days or ramadan) and not race
        strc = [x for x in (am, pm) if x in S.STRENGTH_CODES]
        knee = cal.knee_care(d)
        kegel = ('At the end of the strength session (10 min): ' + S.kegel_text(S.kegel_for(strc[0], w, knee))) if strc else S.KEGEL_DAILY
        swim_hard = any(x in ('SWIM-T', 'SWIM-E', 'SWIM-RAM-T', 'SWIM-RAM-E') for x in (am, pm))
        mob_codes = ['AM-MOB'] + (['KNEE'] if knee else []) + (['SHOULDER'] if swim_hard else [])
        # energy target: BMR x activity - deficit, adjusted for the day's training and fasting
        wt_now = target_weight(cfg, cal, d)
        deficit = ((p['start_weight'] - p['goal_weight']) * 7700 / max(1, (gdate - cal.first_day).days)) if d <= gdate else 300
        deficit = min(deficit, 900)
        base = bmr(cfg, wt_now) * 1.5 - deficit
        add_k = 0
        for code in (am, pm):
            if code == 'RUN-L':
                add_k += int(60 * (c['long_km'] or 5) * 0.6)
            elif code == 'BIKE-L':
                add_k += int((c['ride_min'] or 45) * 5)
            elif code in ('BRICK', 'HX-SIM'):
                add_k += 300
        if race:
            add_k += 500
        if am and pm:
            add_k += 150
        if fasting and not ramadan:
            add_k -= 300
        kcal = int(round(max(1500, base + add_k) / 10) * 10)
        protein = 130 if fasting else 160
        fat = int(max(65, kcal * 0.25 / 9))
        carbs = int(max(100, (kcal - protein * 4 - fat * 9) / 4))
        mp = 'RAMADAN' if ramadan else ('FAST' if wd in fast_days and not race else ('CUT' if d <= gdate else 'FUEL'))
        smoothie = None
        if mp in ('CUT', 'FUEL') and wd in N.SMOOTHIE_DAYS:
            smoothie = {'Wed': 'Green focus', 'Fri': 'Beet booster', 'Sat': 'Long-run refuel'}[wd]
        when_am = 'Before suhoor, about 04:15' if ramadan else 'Morning, 05:45'
        when_pm = 'After iftar, about 20:00' if ramadan else ('After breaking the fast, about 19:30' if wd in fast_days else 'Evening, 17:30')
        days.append(
            dict(
                date=d.isoformat(),
                day=i + 1,
                week=w,
                phase=S.kind_label(c['phase_kind'], c['next_race']),
                phase_id=c['phase_kind'],
                weekday=wd,
                week_type=c['wtype'],
                am=add(am, c, d),
                pm=add(pm, c, d),
                race=S.race_title(race) if race else None,
                race_id=race['id'] if race else None,
                when_am=when_am,
                when_pm=when_pm,
                fasting=fasting,
                ramadan=ramadan,
                warmup=S.warmups_for(am, pm),
                kegels=kegel,
                mobility=mob_codes,
                knee_care=knee,
                meal_plan=mp,
                smoothie=smoothie,
                smoothie_time='16:00' if smoothie else None,
                kcal=kcal,
                protein=protein,
                carbs=carbs,
                fat=fat,
                water_l=3.5 if (am or pm) and not fasting else 3.0,
                target_weight=wt_now,
            )
        )
        d += dt.timedelta(days=1)
        i += 1

    weeks = []
    for c in cal.weeks:
        weeks.append(
            dict(
                week=c['w'],
                start=c['monday'].isoformat(),
                phase=S.kind_label(c['phase_kind'], c['next_race']),
                kind=c['phase_kind'],
                type={'build': 'Build', 'easy': 'Easy week', 'taper': 'Taper', 'race': 'Race week', 'recovery': 'Recovery week'}[c['wtype']]
                + (' (Ramadan)' if c['ramadan_days'] >= 4 else ''),
                long_run_km=c['long_km'],
                swim_cont_m=c['swim_cont'],
                ride_min=c['ride_min'],
                next_race=c['next_race']['name'],
                weeks_to_race=c['weeks_to'],
            )
        )
    phases = []
    for wk in weeks:
        if phases and phases[-1]['name'] == wk['phase']:
            phases[-1]['last_week'] = wk['week']
        else:
            phases.append(dict(id=f'P{len(phases) + 1}', name=wk['phase'], first_week=wk['week'], last_week=wk['week'], purpose=S.KIND_PURPOSE[wk['kind']]))

    goals, minis = build_goals(cfg, cal)
    baselines = [
        dict(key='waist', label='Waist at the navel (cm)', when='Week 1 test day'),
        dict(key='pushups', label='Max push-ups', when='Week 1 test day'),
        dict(key='run5k', label='5 km run/walk time (min)', when='First long run'),
        dict(key='swim', label='Longest non-stop swim (m)', when='First Friday swim'),
        dict(key='plank', label='Plank hold (s)', when='Week 1 test day'),
        dict(key='wallsit', label='Wall sit (s)', when='Week 1 test day'),
        dict(key='row', label='Single-arm 20 L jerrycan row, weaker arm (reps)', when='Week 1 test day'),
        dict(key='rhr', label='Resting heart rate on waking (bpm)', when='Any morning'),
    ]
    library = []
    for n, v in LB.L.items():
        rx = lib_rx.get(n)
        library.append(
            dict(
                name=n,
                cat=v[0],
                muscles=v[1],
                setup=v[2],
                how=v[3],
                breathing=v[4],
                mistakes=v[5],
                easier=v[6],
                harder=v[7],
                equipment=LB.equipment(n),
                difficulty=LB.difficulty(n, v[0]),
                also=LB.ALSO_CALLED.get(n, ''),
                sets=rx[0] if rx else None,
                reps=rx[1] if rx else '',
                rest=rx[2] if rx else '',
                purpose=HT.PURPOSE.get(n, ''),
                cues=HT.CUES.get(n, ''),
                dose=HT.DOSE.get(n, ''),
            )
        )
    warmups = [dict(code=code, title=label, items=[dict(name=n, amount=a, lib=HT.link(n)) for n, a in items]) for code, label, items in LB.WARMUPS]
    kegels = [dict(name=n, items=[dict(name=e, sets=s, reps=r, how=h) for e, s, r, h in items]) for n, items in S.KEGEL]
    smoothies = []
    for code, name, when, why, ings, how in N.SMOOTHIES:
        items = [food_item(k, g) for k, g in ings]
        smoothies.append(
            dict(
                name=name,
                when=when,
                why=why,
                how=how,
                items=items,
                totals={k: round(sum(i[k] for i in items)) for k in ('kcal', 'p', 'c', 'f')},
                tzs=N.meal_cost(ings),
            )
        )
    plans = meal_plans()
    plan = dict(
        title='EnduraForge plan',
        engine=ENGINE_VERSION,
        athlete=p.get('name', ''),
        start=days[0]['date'],
        end=days[-1]['date'],
        config=cfg,
        targets=dict(
            start_date=cal.first_day.isoformat(),
            start_weight=p['start_weight'],
            goal_weight=p['goal_weight'],
            goal_date=p['goal_weight_date'],
            end_weight=p.get('end_weight'),
            height_cm=p['height_cm'],
            age=p['age'],
            protein_g=160,
        ),
        races=[dict(r, title=S.race_title(r)) for r in cfg['races']],
        phases=phases,
        weeks=weeks,
        days=days,
        sessions=sessions,
        goals=goals,
        mini_goals=minis,
        baselines=baselines,
        library=library,
        warmups=warmups,
        kegels=kegels,
        mobility=[dict(name=a, area=b, how=c, dose=d) for a, b, c, d in LB.MOBILITY],
        mobility_routines=[dict(code=a, title=b, when=c) for a, b, c in LB.MOBILITY_ROUTINES],
        pelvic=LB.PELVIC,
        swim_drills=HT.SWIM_DRILLS,
        injury_prevention=HT.as_plan(),
        hyrox=dict(
            format=HX.FORMAT,
            stations=[dict(name=a, race=b, gym=c, home=d, trains=e, cue=f) for a, b, c, d, e, f in HX.STATIONS],
            divisions=HX.DIVISIONS,
            skills=[dict(skill=a, how=b) for a, b in HX.SKILLS],
            gym_note=HX.GYM_NOTE,
        ),
        bike_checklists=dict(
            equipment=[
                'Road or hybrid bike that fits you (saddle height: slight knee bend at the bottom)',
                'Helmet (always)',
                'Front white and rear red lights',
                'Two bottle cages and bottles',
                'Spare tube, tyre levers, mini pump or CO2',
                'Bright top; sunglasses',
                'Cycling shorts with a pad',
                'Phone, ID and some cash',
            ],
            before_every_ride=[
                'Tyres pumped (check the pressure on the tyre wall)',
                'Brakes grip firmly',
                'Chain clean and oiled',
                'Quick-release or thru-axles closed',
                'Lights charged',
                'Two full bottles; fuel for rides over 75 min',
            ],
            weekly=['Wipe and oil the chain', 'Check the tyres for cuts and glass', 'Check the brake pads'],
            monthly=['Gear and brake cable check', 'Bolt check (stem, seat post, cleats)', 'Professional service every 3 months or before the 70.3'],
        ),
        nutrition=dict(
            foods=[
                dict(key=f[0], name=f[1], english=f[2], group=f[3], kcal=f[4], p=f[5], c=f[6], f=f[7], portion=f[8], tzs_kg=N.PRICE.get(f[0])) for f in N.FOODS
            ],
            meal_plans=plans,
            smoothies=smoothies,
            rules=[dict(rule=a, detail=b) for a, b in N.EATING_RULES],
            swaps=[dict(instead=a, have=b, saves=c) for a, b, c in N.SWAPS],
            shopping=shopping_list(plans, cfg),
            sports=[dict(topic=a, detail=b) for a, b in N.SPORTS_NUTRITION],
            fuel_progression=[dict(when=a, carbs=b) for a, b in N.FUEL_PROGRESSION],
            hormone=[dict(topic=a, detail=b) for a, b in N.HORMONE_HEALTH],
            smoothie_rule='At most one smoothie a day, and not every day. Fruit smoothies are not automatically low-calorie or low-sugar: they count as a meal or a snack.',
        ),
        supplements=[dict(name=a, purpose=b, evidence=c, dose=d, when=e, side_effects=f, cautions=g, in_plan=h) for a, b, c, d, e, f, g, h in N.SUPPLEMENTS],
        supplements_note=N.SUPPLEMENT_NOTE + ' ' + N.NOT_NEEDED,
        sleep=[dict(time=a, what=b, why=c) for a, b, c in N.SLEEP],
        bedroom=[dict(area=a, what=b) for a, b in N.BEDROOM],
        recovery=[dict(tool=a, how=b, when=c) for a, b, c in X.RECOVERY],
        tanzania=[dict(factor=a, meaning=b, todo=c) for a, b, c in X.TZ_NOTES],
        injury=(
            dict(
                cfg['injury'],
                advice=[
                    'A small pinch that stays at 0 to 2 out of 10 and settles within a day is usually an overload sign after a jump in distance, not damage.',
                    'Until it settles: flat routes, no sprints or hills, no deep or loaded knee bends, the long run held at its current distance, and the knee-care routine every day.',
                    'Stop a run if the pain reaches 3 out of 10 or changes how you run. Swap the next run for a swim.',
                    'See a physiotherapist or doctor if it hurts on two runs in a row, if the knee swells, locks, gives way or hurts at night, or if it is not clearly better in 7 to 10 days.',
                    'The app is a coach, not a diagnosis. When in doubt, get it checked before race day.',
                ],
            )
            if cfg.get('injury')
            else None
        ),
        reminders=cfg.get('reminders', {}),
        seed_activities=SEED,
        import_baseline=GA.baseline(SEED),
        weekly_rule='ON TRACK: change nothing. BEHIND (7-day average more than 1 kg above the target line): check your logging first (oil, chapati, sugar in chai, weekends), then remove one fist of starch a day for 7 days. TOO FAST (more than 1.5 kg below): add 150 kcal a day. Adherence under 80%: fix consistency before changing anything else.',
    )
    body = json.dumps(plan, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    plan['version'] = hashlib.sha256(body.encode()).hexdigest()[:12]
    return plan


def plan_text(user_cfg: dict | None = None) -> str:
    return json.dumps(build_plan(user_cfg), ensure_ascii=False, separators=(',', ':'))
