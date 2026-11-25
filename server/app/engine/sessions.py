"""Date-driven training calendar. Everything is computed from the athlete config (races, fasting, Ramadan, bike start,
baseline), so changing a race date moves every phase, taper and recovery week.

Hard rules (enforced here and tested):
  * runs in the morning only, swims in the evening only (a run and a swim may share a day unless the athlete forbids it)
  * hard days together, easy days easy: no heavy leg session within 72 hours before the long run
  * an active knee niggle holds the long run, removes hard intervals and swaps in knee-friendly strength work
  * fasting weekdays (Thursday by default, dry fast): only an easy walk and mobility after breaking the fast
  * Ramadan days: one session at most, light, timed around suhoor and iftar
  * no cycling before the bike start date
  * every strength session has a warm-up, a kegel finisher and a cool-down stretch
  * progression is gradual: long run +1.5 km (+2 km above 10 km) and never more than +35% a week; an easier week every 4th week
"""

from __future__ import annotations

import datetime as dt

from . import howto as HT
from . import hyrox as HX
from . import library as LB
from .config import D

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

NAMES = {
    'STR-C': 'Strength: lower body, single-leg (moderate)',
    'RUN-E': 'Easy run',
    'RUN-S': 'Short easy run with strides',
    'RUN-I': 'Run: quality session',
    'RUN-L': 'Long run',
    'RUN-RAM': 'Easy run before suhoor (Ramadan)',
    'RUN-RAM-L': 'Longer easy run before suhoor (Ramadan)',
    'SWIM-T': 'Swim: technique and intervals',
    'SWIM-E': 'Swim: non-stop endurance',
    'SWIM-R': 'Swim: easy',
    'SWIM-RAM-T': 'Swim: technique after iftar (Ramadan)',
    'SWIM-RAM-E': 'Swim: easy non-stop after iftar (Ramadan)',
    'STR-A': 'Strength: lower body (heavier)',
    'STR-B': 'Strength: upper body and core',
    'STR-D': 'Strength: hamstrings, shoulders and arms',
    'STR-R': 'Home workout: core, hips, arms and kegels (light, the day after the long run)',
    'STR-RAM': 'Strength: full body maintenance after iftar (Ramadan)',
    'HX-S': 'HYROX stations: strength endurance',
    'HX-SIM': 'HYROX simulation',
    'BIKE-I': 'Bike: intervals',
    'BIKE-L': 'Bike: long endurance ride',
    'BRICK': 'Brick: bike then run',
    'MOB': 'Easy walk, mobility and kegels',
    'REST': 'Rest day: walk and mobility',
    'TEST': 'Baseline tests',
    'SHAKE': 'Shake-out jog',
    'FAST': 'Fasting day: easy walk, mobility and kegels after breaking the fast',
}
STRENGTH_CODES = ('STR-A', 'STR-B', 'STR-C', 'STR-D', 'STR-R', 'STR-RAM', 'HX-S')
RUN_CODES = ('RUN-E', 'RUN-S', 'RUN-I', 'RUN-L', 'RUN-RAM', 'RUN-RAM-L', 'BRICK', 'HX-SIM', 'SHAKE', 'TEST')
BIKE_CODES = ('BIKE-I', 'BIKE-L', 'BRICK')
HARD_CODES = ('RUN-I', 'RUN-L', 'STR-A', 'STR-B', 'STR-C', 'STR-D', 'HX-S', 'HX-SIM', 'BRICK', 'BIKE-I', 'BIKE-L', 'SWIM-T')


def r05(x: float) -> float:
    return max(0.5, round(x * 2) / 2)


def kind_label(kind: str, race: dict | None) -> str:
    return {
        'run5': 'Speed: the 5 km and a 12 km long run',
        'run10': 'Foundation: the 10 km',
        'runhalf': 'Endurance: the half marathon',
        'runlong': 'Endurance: long run',
        'runbase': 'Run and strength base',
        'ramadan': 'Ramadan: maintain and recover',
        'tribase': 'Triathlon development',
        'hyrox': 'HYROX preparation',
        'olympic': 'Olympic triathlon tune-up',
        'half_ironman': 'Ironman 70.3 preparation',
    }[kind]


KIND_PURPOSE = {
    'run5': 'Pace work for a faster 5 km, the long run growing to 12 km, leg strength and kegels three times a week, and four swims a week for technique, breathing and SWOLF.',
    'run10': 'Consistent running habits, run/walk efficiency, basic strength and swim endurance, ready for the 10 km.',
    'runhalf': 'Long run grows step by step with easier weeks, aerobic base, muscular endurance and a longer non-stop swim.',
    'runlong': 'Long aerobic running with recovery weeks.',
    'runbase': 'Running and strength while the bike has not started yet.',
    'ramadan': 'One light session a day around suhoor and iftar: keep the habit, keep strength, recover from the half marathon. No hard training while dry-fasting.',
    'tribase': 'Cycling comes in after Ramadan: bike handling, cadence and easy endurance, first brick sessions, 1.5 km swims, strength still a priority.',
    'hyrox': 'Race-specific HYROX work: stations, running under fatigue, sled-style pushing and pulling, grip and wall-ball technique.',
    'olympic': 'Swim, bike and run together at Olympic distance, plus race nutrition practice.',
    'half_ironman': 'Long rides towards 90 km, long swims, long runs off the bike, race-day fuelling practice, then a two-week taper. Strength stays, at lower volume.',
}

# block peaks: long run km, non-stop swim m, long ride min
PEAK_LONG = {'run5': 12, 'run10': 10, 'runhalf': 18, 'runlong': 28, 'runbase': 12, 'tribase': 14, 'hyrox': 12, 'olympic': 14, 'half_ironman': 18}
PEAK_SWIM = {
    'run5': 1500,
    'run10': 1500,
    'runhalf': 1500,
    'runlong': 1500,
    'runbase': 1500,
    'tribase': 1800,
    'hyrox': 1800,
    'olympic': 1900,
    'half_ironman': 2300,
}
PEAK_RIDE = {'tribase': 150, 'hyrox': 150, 'olympic': 180, 'half_ironman': 240}


def race_kind(r: dict) -> str:
    if r['type'] == 'run':
        km = r.get('run_km') or 10
        if km <= 6:
            return 'run5'
        return 'run10' if km <= 12 else ('runhalf' if km <= 25 else 'runlong')
    if r['type'] == 'hyrox':
        return 'hyrox'
    return 'half_ironman' if (r.get('bike_km') or 0) >= 60 else 'olympic'


def race_title(r: dict) -> str:
    t = r.get('target_min')
    goal = ''
    if t:
        h, m = divmod(int(t), 60)
        goal = f' (target under {m} min)' if not h else (f' (target under {h} h {m:02d})' if m else f' (target under {h} hours)')
    if r['type'] == 'triathlon':
        return f'{r["name"].upper()}: {r.get("swim_m", 0):,} m swim, {r.get("bike_km", 0):g} km bike, {r.get("run_km", 0):g} km run{goal}'
    if r['type'] == 'hyrox':
        return f'{r["name"].upper()} ({r.get("division", "Men Open")}): 8 x (1 km run + 1 station){goal}'
    return f'{r["name"].upper()}: {r.get("run_km", 0):g} km{goal}'


# ============================================================================ the calendar
class Calendar:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.first_day = D(cfg['start'])
        self.monday = self.first_day - dt.timedelta(days=self.first_day.weekday())
        self.races = sorted([r for r in cfg['races'] if r.get('date')], key=lambda r: r['date'])
        self.key_races = [r for r in self.races if r.get('priority', 'A') in ('A', 'B')]
        self.last_day = D(self.key_races[-1]['date'])
        self.nweeks = (self.last_day - self.monday).days // 7 + 1
        ram = cfg.get('ramadan')
        self.ram = (D(ram['start']), D(ram['end'])) if ram else None
        self.bike_start = D(cfg.get('bike_start')) if cfg.get('bike_start') else None
        self.swim_test = D(cfg.get('swim_test')) if cfg.get('swim_test') else None
        self.fast_days = tuple(cfg.get('fasting', {}).get('weekdays', []))
        self.two = cfg.get('preferences', {}).get('two_sessions', True)
        self.race_on = {D(r['date']): r for r in self.races}
        inj = cfg.get('injury')
        self.injury = (inj.get('area', ''), D(inj['since']), D(inj['until'])) if inj else None
        self.no_run_swim = cfg.get('preferences', {}).get('no_run_and_swim_same_day', False)
        self.weeks = [self._week_ctx(w) for w in range(1, self.nweeks + 1)]
        for c in self.weeks:
            c['knee'] = any(self.knee_care(c['monday'] + dt.timedelta(days=i)) for i in range(7))
        self._progress()

    def week_monday(self, w: int) -> dt.date:
        return self.monday + dt.timedelta(days=7 * (w - 1))

    def is_ramadan(self, d: dt.date) -> bool:
        return bool(self.ram) and self.ram[0] <= d <= self.ram[1]

    def knee_care(self, d: dt.date) -> bool:
        return bool(self.injury) and self.injury[0] == 'knee' and self.injury[1] <= d <= self.injury[2]

    def bike_ok(self, d: dt.date) -> bool:
        return self.bike_start is not None and d >= self.bike_start

    def _week_ctx(self, w: int) -> dict:
        mon = self.week_monday(w)
        sun = mon + dt.timedelta(days=6)
        in_week = [r for r in self.key_races if mon <= D(r['date']) <= sun]
        nxt = next((r for r in self.key_races if D(r['date']) >= mon), self.key_races[-1])
        prev = [r for r in self.key_races if D(r['date']) < mon]
        prev = prev[-1] if prev else None
        weeks_to = (D(nxt['date']) - mon).days // 7
        kind = race_kind(nxt)
        if kind == 'hyrox' and weeks_to > 7:
            kind = 'tribase' if self.bike_ok(mon) else 'runbase'
        if kind in ('olympic', 'half_ironman') and not self.bike_ok(mon):
            kind = 'runbase'
        ram_days = sum(1 for i in range(7) if self.is_ramadan(mon + dt.timedelta(days=i)))
        if ram_days >= 4:
            kind_shown = 'ramadan'
        else:
            kind_shown = kind
        if in_week:
            wtype = 'race'
        elif prev and (mon - D(prev['date'])).days < 7:
            wtype = 'recovery'
        elif weeks_to == 1 or (weeks_to == 2 and race_kind(nxt) == 'half_ironman'):
            wtype = 'taper'
        else:
            wtype = 'build'
        return dict(
            w=w,
            monday=mon,
            kind=kind,
            phase_kind=kind_shown,
            wtype=wtype,
            next_race=nxt,
            prev_race=prev,
            weeks_to=weeks_to,
            race=in_week[0] if in_week else None,
            ramadan_days=ram_days,
            block_week=0,
        )

    def _progress(self):
        """Forward simulation of the long run, the non-stop swim and the long ride, week by week."""
        b = self.cfg.get('baseline', {})
        L = float(b.get('long_run_km') or 3.0)
        anchor = D(b.get('long_run_date')) if b.get('long_run_date') else self.first_day
        C = float(b.get('swim_cont_m') or 100)
        R = 45.0
        build_count = 0
        alt = 0
        was_ramadan = False
        for c in self.weeks:
            mon = c['monday']
            kind, wt = c['kind'], c['wtype']
            ramadan = c['ramadan_days'] >= 4
            if was_ramadan and not ramadan and wt == 'build':
                wt = c['wtype'] = 'easy'  # first week back after Ramadan: ease in
            was_ramadan = ramadan
            if wt == 'build' and not ramadan:
                build_count += 1
                if build_count % 4 == 0 and c['weeks_to'] > 2:
                    wt = c['wtype'] = 'easy'
            elif wt in ('race', 'recovery'):
                build_count = 0
            c['block_week'] = build_count
            # ---- long run
            peak = PEAK_LONG[kind]
            before_anchor = mon + dt.timedelta(days=6) < anchor
            if before_anchor:
                c['long_km'] = r05(L)
            elif ramadan:
                L = L * 0.86  # short runs only during Ramadan: the long run shrinks, rebuilt after
                c['long_km'] = None
            elif wt == 'build':
                if mon > anchor and not c['knee']:  # the anchor week is the baseline; an active niggle holds the distance
                    step = 1.5 if L < 10 else 2.0
                    L = L if L >= peak else min(peak, L + step, L * 1.35)
                c['long_km'] = r05(min(L, peak))
            elif wt == 'easy':
                c['long_km'] = r05(min(L, peak) * 0.75)
            elif wt == 'taper':
                # a 5 km needs little taper: the long run stays, easy, so the 12 km habit holds
                c['long_km'] = r05(min(L, peak) * (1.0 if kind == 'run5' else 0.75 if c['weeks_to'] == 1 else 0.85))
            elif wt == 'race':
                c['long_km'] = None
                rk = c['race'].get('run_km') or 0
                if c['race']['type'] == 'run':
                    L = max(L, 0.8 * rk)
            else:  # recovery
                c['long_km'] = r05(min(0.6 * L, 8))
            # ---- non-stop swim
            speak = PEAK_SWIM[kind]
            if ramadan:
                C = min(speak, C + 50)
                c['swim_cont'] = int(round(C * 0.9 / 50) * 50)
            elif wt in ('build', 'recovery'):
                step = 100 if C < 600 else (150 if C < 1300 else 100)
                C = C if C >= speak else min(speak, C + step)
                c['swim_cont'] = int(round(C / 50) * 50)
            else:
                c['swim_cont'] = int(round(C * 0.75 / 50) * 50)
            # ---- bike
            if self.bike_ok(mon) and kind in PEAK_RIDE:
                rpeak = PEAK_RIDE[kind]
                if wt == 'build':
                    R = R if R >= rpeak else min(rpeak, R + 15, R * 1.25)
                    c['ride_min'] = int(round(R / 5) * 5)
                elif wt == 'easy':
                    c['ride_min'] = int(round(R * 0.7 / 5) * 5)
                elif wt == 'taper':
                    c['ride_min'] = int(round(R * (0.5 if c['weeks_to'] == 1 else 0.7) / 5) * 5)
                else:
                    c['ride_min'] = int(round(min(R, 60) * 0.6 / 5) * 5)
            else:
                c['ride_min'] = None
            if wt == 'build':
                alt += 1
            c['alt'] = alt % 2 == 0
            c['level'] = 1 if c['w'] <= 5 else (2 if c['w'] <= 13 else 3)

    # ------------------------------------------------------------------ one day
    def day_codes(self, d: dt.date) -> tuple[str | None, str | None]:
        w = (d - self.monday).days // 7 + 1
        c = self.weeks[w - 1]
        wd = DAYS[d.weekday()]
        kind, wt = c['kind'], c['wtype']
        if d in self.race_on:
            return ('RACE', None)
        if wd in self.fast_days:
            return (None, 'FAST')
        if self.is_ramadan(d):
            return {
                'Mon': (None, 'STR-RAM'),
                'Tue': ('RUN-RAM', None),
                'Wed': (None, 'SWIM-RAM-T'),
                'Thu': (None, 'SWIM-RAM-E'),
                'Fri': (None, 'STR-RAM'),
                'Sat': ('RUN-RAM-L', None),
                'Sun': ('REST', 'MOB'),
            }.get(wd, (None, 'MOB'))
        if d == self.swim_test:
            return ('REST', 'SWIM-E')
        # Hard days together (Monday: quality run + heavier legs), Tuesday rests the legs, Wednesday is moderate,
        # Friday is light so the Saturday long session starts fresh.
        # No fast day. Legs are trained Monday and Wednesday, so they have three days before the Saturday long run.
        # Thursday pairs a short run with a technique swim; Friday is the non-stop swim; Sunday is a light home workout only.
        if kind in ('run5', 'run10', 'runhalf', 'runlong', 'runbase'):
            T = {
                'Mon': ('RUN-I', 'STR-A'),
                'Tue': ('STR-B', 'SWIM-T'),
                'Wed': ('RUN-E', 'STR-C'),
                'Thu': ('RUN-S', 'SWIM-T'),
                'Fri': ('MOB', 'SWIM-E'),
                'Sat': ('RUN-L', None),
                'Sun': ('MOB', 'STR-R'),
            }
        elif kind == 'hyrox':
            T = {
                'Mon': ('RUN-I', 'STR-A'),
                'Tue': ('STR-B', 'SWIM-T'),
                'Wed': ('BIKE-I', 'HX-S'),
                'Thu': ('MOB', 'STR-D'),
                'Fri': ('RUN-E', 'SWIM-R'),
                'Sat': ('HX-SIM' if c['alt'] and wt == 'build' else 'RUN-L', None),
                'Sun': ('BIKE-L', 'SWIM-E'),
            }
        else:  # tribase, olympic, half_ironman
            T = {
                'Mon': ('RUN-I', 'STR-A'),
                'Tue': ('STR-B', 'SWIM-T'),
                'Wed': ('BIKE-I', 'STR-C'),
                'Thu': ('MOB', 'STR-D'),
                'Fri': ('RUN-E', 'SWIM-R'),
                'Sat': ('BRICK' if c['alt'] or wt != 'build' else 'RUN-L', None),
                'Sun': ('BIKE-L', 'SWIM-E'),
            }
        am, pm = T.get(wd, (None, None))
        if c['w'] == 1 and wd == 'Tue' and d >= self.first_day:
            am, pm = 'TEST', None
        # ---- around races
        nxt = D(c['next_race']['date'])
        days_to = (nxt - d).days
        rtype = c['next_race']['type']
        if 0 < days_to <= 6 and wt == 'race':
            if pm in ('STR-C', 'HX-S'):
                pm = 'MOB'  # no second leg session in race week
            if days_to == 2:
                am, pm = (None, 'MOB')
            if days_to == 1:
                am, pm = ('SHAKE', None) if rtype == 'hyrox' or d.weekday() == 5 else (None, 'MOB')
        prev = [x for x in self.race_on if x < d]
        if prev:
            since = (d - max(prev)).days
            last = self.race_on[max(prev)]
            if since == 1:
                am, pm = ('REST', None) if last['type'] != 'run' else ('REST', 'SWIM-R')
            elif since == 2:
                am, pm = (None, 'MOB')
        # ---- the athlete's rule: Sundays are home workouts only (no pool, no road run)
        if wd == 'Sun':
            am = None if am and (am.startswith('SWIM') or am in RUN_CODES) else am
            pm = None if pm and (pm.startswith('SWIM') or pm in RUN_CODES) else pm
        # ---- the athlete's own rule, if set: never a run and a swim on one day (the swim moves out)
        if self.no_run_swim and am in RUN_CODES and pm and pm.startswith('SWIM'):
            pm = None
        # ---- safety: no bike before the bike start
        if not self.bike_ok(d):
            am = {'BIKE-I': 'RUN-E', 'BIKE-L': 'REST', 'BRICK': 'RUN-L'}.get(am, am)
            pm = {'BIKE-I': None, 'HX-S': 'STR-C'}.get(pm, pm)
        # ---- one session a day if the athlete turned two-a-days off
        if not self.two and am and pm:
            order = [
                'RACE',
                'RUN-L',
                'BRICK',
                'HX-SIM',
                'SWIM-E',
                'STR-A',
                'RUN-I',
                'STR-C',
                'STR-B',
                'HX-S',
                'SWIM-T',
                'BIKE-L',
                'BIKE-I',
                'STR-D',
                'RUN-E',
                'RUN-S',
                'SWIM-R',
                'STR-R',
                'MOB',
                'REST',
            ]
            keep = min((am, pm), key=lambda x: order.index(x) if x in order else 99)
            am, pm = (keep, None) if keep == am else (None, keep)
        return am, pm


# ============================================================================ session content
def stretch_rows(code, block):
    WU = {k: items for k, label, items in LB.WARMUPS}
    return [(block, n, 1, amt, '', 'Slow and controlled') for n, amt in WU[code]]


def warmup_text(code):
    WU = {k: items for k, label, items in LB.WARMUPS}
    return '; '.join(f'{n} {amt}' for n, amt in WU[code])


KEGEL_CIRCUIT = [
    ('Slow kegel holds', 2, '8', 'Lying down: squeeze and lift for 5 s (8 s from the second week), then relax fully for 10 s'),
    ('Quick kegel squeezes', 2, '10', 'A strong 1 s squeeze, then 2 s of full relaxation'),
    ('Kegel glute bridge', 2, '10', 'Lift the pelvic floor first, then the hips; hold 3 s at the top; lower and relax fully'),
    ('Deep squat hold with kegel', 2, '20 s', 'Deepest comfortable squat, gentle half-strength squeeze, breathing normally'),
    ('Relaxation breathing', 1, '6 slow breaths', 'Let the pelvic floor drop and relax on every breath in'),
]
# while a knee niggle is active the deep squat hold is swapped for a floor exercise
KEGEL_CIRCUIT_KNEE = [
    x if x[0] != 'Deep squat hold with kegel' else ('Bird dog with kegel', 2, '8 per side', 'Hold the squeeze 3 s at full reach, then relax completely')
    for x in KEGEL_CIRCUIT
]
KEGEL = [('Kegel circuit (10 min)', KEGEL_CIRCUIT), ('Kegel circuit, knee-friendly (10 min)', KEGEL_CIRCUIT_KNEE)]
KEGEL_DAILY = 'Kegels twice a day, 5 min each (morning and evening): 1 x 10 slow holds (5 s squeeze, 10 s relax), 1 x 10 quick squeezes, 6 relaxation breaths. Relax fully between squeezes.'


def kegel_for(code, w, knee=False):
    return KEGEL[1 if knee else 0]


def kegel_text(circuit):
    return '; '.join(f'{n} {s} x {r}' for n, s, r, note in circuit[1])


def scheme(role, c, light=False):
    easy = light or c['wtype'] in ('easy', 'taper', 'race', 'recovery')
    lv = c['level']
    sets = 2 if easy else (4 if c['block_week'] % 4 == 3 and c['kind'] not in ('half_ironman',) else 3)
    eff = (
        'Effort 6 out of 10 (easy week)'
        if easy
        else ('Effort 7 out of 10: 3 reps left in the tank' if lv == 1 else 'Effort 8 out of 10: 2 reps left in the tank')
    )
    return {
        'main': (sets, {1: '10 to 12', 2: '8 to 10', 3: '6 to 8'}[lv], '90 s', eff),
        'sec': (sets, {1: '12', 2: '10 to 12', 3: '8 to 10'}[lv], '75 s', eff),
        'acc': (sets, '12 to 15', '45 s', eff),
        'ham': (sets, {1: '8', 2: '5', 3: '6'}[lv], '90 s', 'Slow lowering, 4 s'),
        'core': (sets, {1: '30 s', 2: '40 s', 3: '50 s'}[lv], '30 s', 'Full tension, keep breathing'),
    }[role]


BACKPACK = 'Backpack 6 to 15 kg (books, water bottles or sand in bags)'
JERRY = 'Jerrycan 10 to 20 L (1 L of water = 1 kg)'
STR = {
    'STR-A': [
        ('main', ['Backpack goblet squat', 'Backpack pause squat', 'Backpack Bulgarian split squat'], BACKPACK + '. Quads and glutes'),
        ('main', ['Jerrycan Romanian deadlift', 'Single-leg Romanian deadlift', 'Single-leg Romanian deadlift'], JERRY + '. Hamstrings'),
        ('ham', ['Hamstring walkout', 'Towel hamstring curl', 'Nordic hamstring lower'], 'Hamstrings. For the Nordic, hook the heels under a heavy bed'),
        ('sec', ['Reverse lunge', 'Backpack reverse lunge', 'Backpack walking lunge'], 'Reps per leg'),
        ('sec', ['Glute bridge', 'Single-leg glute bridge', 'Backpack hip thrust'], 'Glutes and hamstrings'),
        ('acc', ['Calf raise on a step', 'Single-leg calf raise', 'Single-leg calf raise'], 'Calves and Achilles. Step, door threshold or thick book'),
        ('acc', ['Farmer carry', 'Farmer carry', 'Farmer carry'], JERRY + ' in each hand. Grip, forearms, shoulders and legs: the HYROX farmers carry'),
        ('core', ['Front plank', 'Side plank', 'Pallof press'], 'Core and lower back. Pallof press needs a band; Side plank if you have none'),
    ],
    'STR-B': [
        ('main', ['Pike push-up', 'Backpack overhead press', 'Feet-elevated pike push-up'], 'Shoulders first while you are fresh'),
        ('main', ['Incline push-up', 'Push-up', 'Feet-elevated push-up'], 'Chest, shoulders, triceps'),
        ('main', ['Backpack bent-over row', 'Single-arm jerrycan row', 'Single-arm jerrycan row'], JERRY + '. Back and biceps (replaces pull-ups)'),
        ('sec', ['Water-bottle lateral raise', 'Water-bottle lateral raise', 'Water-bottle front raise'], '1.5 L bottles. Shoulder width'),
        ('sec', ['Chair dip', 'Overhead triceps extension', 'Chair dip'], 'Triceps'),
        ('acc', ['Jerrycan biceps curl', 'Jerrycan hammer curl', 'Jerrycan hammer curl'], JERRY + '. Biceps and forearms'),
        ('acc', ['Wrist curls (palms up and down)'] * 3, 'Forearms and grip for HYROX carries and the sled pull'),
        ('acc', ['Bent-over rear-delt raise'] * 3, '1.5 L bottles. Rear shoulders: balances the pressing and the swim pull'),
        ('acc', ['Prone Y-T-W raise', 'Prone Y-T-W raise', 'Prone Y-T-W raise'], 'Rear shoulders; protects the shoulders for swimming'),
    ],
    'STR-D': [
        ('main', ['Backpack good morning', 'Backpack good morning', 'Single-leg Romanian deadlift'], BACKPACK + '. Hamstrings'),
        ('ham', ['Single-leg glute bridge', 'Hamstring walkout', 'Nordic hamstring lower'], 'Hamstrings'),
        ('main', ['Backpack overhead press', 'Backpack overhead press', 'Backpack overhead press'], BACKPACK + '. Shoulders'),
        ('sec', ['Water-bottle lateral raise', 'Water-bottle lateral raise', 'Water-bottle lateral raise'], 'Shoulder width'),
        ('acc', ['Jerrycan hammer curl', 'Jerrycan biceps curl', 'Jerrycan biceps curl'], 'Arms'),
        ('acc', ['Chair dip', 'Diamond push-up', 'Overhead triceps extension'], 'Triceps'),
        ('core', ['Dead bug', 'Side plank', 'Reverse crunch'], 'Core'),
    ],
    'STR-R': [
        ('sec', ['Single-leg glute bridge'] * 3, 'Hips and hamstrings, light'),
        ('acc', ['Single-leg calf raise'] * 3, 'Calves and Achilles: protects you on the long run'),
        ('acc', ['Water-bottle lateral raise'] * 3, 'Shoulders'),
        ('acc', ['Bent-over rear-delt raise'] * 3, 'Rear shoulders'),
        ('acc', ['Jerrycan hammer curl'] * 3, 'Arms and forearms'),
        ('acc', ['Wrist curls (palms up and down)'] * 3, 'Forearms and grip'),
        ('core', ['Dead bug', 'Dead bug', 'Mountain climber'], 'Core'),
        ('core', ['Side plank'] * 3, 'Time per side'),
        ('core', ['Bird dog'] * 3, 'Back and hips'),
    ],
    'STR-RAM': [
        ('main', ['Backpack goblet squat'] * 3, BACKPACK + '. Legs'),
        ('main', ['Jerrycan Romanian deadlift'] * 3, JERRY + '. Hamstrings'),
        ('main', ['Push-up', 'Push-up', 'Push-up'], 'Chest and arms'),
        ('main', ['Single-arm jerrycan row'] * 3, 'Back and biceps'),
        ('sec', ['Water-bottle lateral raise'] * 3, 'Shoulders'),
        ('core', ['Side plank'] * 3, 'Core'),
    ],
}


STR['STR-C'] = [
    ('sec', ['Backpack Bulgarian split squat'] * 3, 'Back foot on a chair. Bodyweight first; add the backpack when 3 x 8 is easy. Reps per leg'),
    ('main', ['Single-leg Romanian deadlift'] * 3, 'Hold a chair for balance. Reps per leg. Hamstrings and balance'),
    ('ham', ['Towel hamstring curl', 'Towel hamstring curl', 'Nordic hamstring lower'], 'Hamstrings'),
    ('sec', ['Step-up', 'Step-up', 'Step-up'], 'Sturdy chair or step, knee height. Backpack from level 2. Reps per leg: drive through the front heel'),
    ('sec', ['Backpack thruster'] * 3, BACKPACK + '. Squat into an overhead press: legs and shoulders together, the HYROX wall-ball movement'),
    ('sec', ['Single-leg glute bridge'] * 3, 'Reps per leg. Glutes'),
    ('acc', ['Single-leg calf raise'] * 3, 'Reps per leg. Calves and Achilles'),
    ('acc', ['Side-lying clam with kegel'] * 3, 'Reps per side. Hip strength keeps the knees stable'),
    ('core', ['Side plank'] * 3, 'Time per side'),
]
# knee-friendly versions used while a knee niggle is active: no deep or loaded knee bending
STR['STR-A-KNEE'] = [
    ('sec', ['Chair squat'] * 3, 'Only as deep as is pain-free; no extra load'),
    ('main', ['Jerrycan Romanian deadlift'] * 3, JERRY + '. Hamstrings and glutes: the knee barely bends'),
    ('sec', ['Glute bridge', 'Single-leg glute bridge', 'Backpack hip thrust'], 'Glutes and hamstrings'),
    ('core', ['Wall sit'] * 3, 'Isometric hold with thighs above parallel. Only if the knee is 0 to 2 out of 10; skip it otherwise'),
    ('acc', ['Calf raise on a step', 'Single-leg calf raise', 'Single-leg calf raise'], 'Calves and Achilles'),
    ('acc', ['Farmer carry'] * 3, JERRY + ' in each hand. Grip, forearms and shoulders; walk tall and slowly, knee-friendly'),
    ('core', ['Front plank', 'Side plank', 'Side plank'], 'Core'),
]
STR['STR-C-KNEE'] = [
    ('main', ['Single-leg Romanian deadlift'] * 3, 'Hold a chair for balance. Reps per leg'),
    ('ham', ['Towel hamstring curl'] * 3, 'Hamstrings'),
    ('sec', ['Single-leg glute bridge'] * 3, 'Reps per leg. Glutes'),
    ('acc', ['Side-lying leg raise'] * 3, 'Reps per side. Outer hip: keeps the knee tracking straight'),
    ('acc', ['Straight-leg raise'] * 3, 'Reps per leg. Quads without bending the knee'),
    ('acc', ['Single-leg calf raise'] * 3, 'Reps per leg'),
    ('acc', ['Side-lying clam with kegel'] * 3, 'Reps per side'),
    ('core', ['Side plank'] * 3, 'Time per side'),
]


def strength_core(code, c):
    rows = []
    lv = c['level']
    knee = c.get('knee') and code in ('STR-A', 'STR-C')
    table = STR[code + '-KNEE'] if knee else STR[code]
    for role, var, load in table:
        s, r, rest, eff = scheme(role, c, light=code in ('STR-R', 'STR-RAM'))
        ex = var[lv - 1]
        if ex == 'Chair dip':
            load = ['Knees bent', 'Legs straight', 'Feet on a second chair'][lv - 1] + '. Triceps'
        if ex in ('Hamstring walkout', 'Towel hamstring curl'):
            r = '8'
        if ex == 'Single-leg glute bridge' and role == 'ham':
            r = '12 per leg'
        if ex in ('Mountain climber',):
            r = '20 per leg'
        if ex == 'Wall sit':
            r = '30 s'
        if ex == 'Farmer carry':
            r, rest = {1: '30 m', 2: '40 m', 3: '50 m'}[lv], '60 s'
        if ex == 'Wrist curls (palms up and down)':
            r = '15 up + 12 down'
        if ex in ('Side-lying leg raise', 'Straight-leg raise', 'Side-lying clam with kegel'):
            r = '12'
        if code == 'STR-R':
            s, eff = 2, 'Light home session: effort 6 out of 10, the day after the long run'
        if code == 'STR-RAM':
            s, eff = 2, 'Maintenance while fasting: effort 6 out of 10, 60 to 90 min after iftar, water first'
        if code == 'STR-C' and c['wtype'] == 'build':
            s, eff = 3, 'Moderate: effort 7 out of 10, the long session is in 3 days'
        if knee:
            s = min(s, 3)
            eff = 'Knee care: effort 6 to 7 out of 10, pain-free range only (0 to 2 out of 10). Stop any exercise that brings on the pinch'
        if c['kind'] == 'half_ironman' and code in ('STR-A', 'STR-B', 'STR-C', 'STR-D') and c['wtype'] == 'build':
            s = min(s, 3)
        tempo = '. Tempo: 3 s down, 1 s pause, 1 s up' if role in ('main', 'sec') else ''
        blk = 'Main' if role in ('main', 'ham') else ('Core' if role == 'core' else 'Accessory')
        rows.append((blk, ex, s, r, rest, f'{eff}. {load}{tempo}'))
    return rows


def hx_s_rows(c):
    f = 1.0 if c['block_week'] <= 2 else 1.5
    sets = 2 if c['wtype'] != 'build' else 3
    out = []
    for name, race, gym, home, trains, cue in HX.STATIONS:
        amount = {
            'SkiErg': f'{int(250 * f)} m (or 20 swings)',
            'Sled push': f'{int(25 * f)} m',
            'Sled pull': f'{int(25 * f)} m',
            'Burpee broad jumps': f'{int(20 * f)} m',
            'Rowing': f'{int(250 * f)} m (or the substitute)',
            'Farmers carry': f'{int(50 * f)} m',
            'Sandbag lunges': f'{int(25 * f)} m',
            'Wall balls': f'{int(20 * f)} reps',
        }[name]
        out.append(('Station', f'{name}: gym {gym}; home: {home}', sets, amount, '60 s', f'7 to 8 out of 10. {cue}'))
    return out


def strength_rows(code, c):
    rows = stretch_rows('W-STR', 'Warm-up')
    rows += hx_s_rows(c) if code == 'HX-S' else strength_core(code, c)
    rows += [('Kegel finisher', n, s, r, '20 s', note) for n, s, r, note in kegel_for(code, c['w'], c.get('knee'))[1]]
    rows += stretch_rows('C-STR', 'Cool-down stretch')
    rows.append(
        (
            'Progress',
            'Progression rule',
            '',
            '',
            '',
            "The app suggests next week's load from your logged sets: if every set reached the top of the rep range at effort 8 or less and with no pain, add 1 to 2 kg OR 1 to 2 reps (never both). Missed reps, effort 9 or more, or pain: repeat the same load.",
        )
    )
    return rows


# ---------------------------------------------------------------------------- running
def hr(cfg, zone):
    mx = cfg['profile'].get('max_hr') or 194
    z = {'easy': (0.67, 0.75), 'steady': (0.75, 0.82), 'hard': (0.82, 0.89), 'race10': (0.78, 0.84)}[zone]
    return f'{int(mx * z[0])} to {int(mx * z[1])} bpm'


def fmt_pace(p):
    m = int(p)
    return f'{m}:{int(round((p - m) * 60)):02d}/km'


RUNI = {
    'run5': [
        '8 x (400 m at 5 km pace{rp} / 90 s walk)',
        '5 x (800 m at 5 km pace{rp} / 2 min jog)',
        'Tempo: 10 min easy, 15 min comfortably hard (about 15 s per km slower than 5 km pace), 5 min easy',
        '3 x (1 km at 5 km pace{rp} / 2 min jog)',
        '6 x (1 min fast / 1 min jog), then 4 x 200 m quick and relaxed / 200 m walk',
        '2 x (1.5 km at 5 km pace{rp} / 3 min jog)',
    ],
    'run10': [
        '6 x (1 min brisk run / 2 min walk)',
        '8 x (1 min brisk run / 1.5 min walk)',
        '6 x (2 min brisk run / 1.5 min walk)',
        '5 x (3 min at 10 km effort / 2 min walk)',
        '3 x (5 min at 10 km effort / 2 min walk)',
    ],
    'runhalf': [
        '2 x (10 min steady / 3 min walk)',
        '4 x (1 km at 10 km effort / 2 min walk)',
        '3 x (2 km at half-marathon effort / 2 min walk)',
        '45 min with the middle 20 min at half-marathon effort',
        '5 x (1 km at 10 km effort / 90 s walk)',
        '3 x (3 km at half-marathon effort / 2 min walk)',
        '50 min with the middle 25 min at half-marathon effort',
        '4 x (2 km at half-marathon effort / 2 min walk)',
    ],
    'runbase': ['6 x (2 min brisk / 1 min walk)', '4 x (1 km steady / 2 min walk)', '30 min with 6 x 30 s faster', '5 x (3 min hard / 2 min easy)'],
    'tribase': [
        '6 x (400 m hard / 90 s walk)',
        '4 x (800 m hard / 2 min jog)',
        '3 x (1 km at 5 km effort / 2 min jog)',
        '30 min steady-hard',
        '5 x (1 km at 10 km effort / 90 s jog)',
        '2 x (2 km at 10 km effort / 3 min jog)',
    ],
    'hyrox': [
        'Compromised run: 4 x (1 km run + 20 backpack thrusters), no rest',
        '6 x (400 m hard / 60 s rest)',
        'Compromised run: 4 x (1 km run + 20 walking lunges + 10 burpees)',
        '5 x (1 km at HYROX race effort / 1 min rest)',
        'Compromised run: 6 x (1 km run + 1 station at 50%)',
        '8 x (500 m hard / 60 s rest)',
    ],
    'olympic': [
        '6 x 800 m at 10 km effort / 2 min jog',
        '4 x 1.5 km at 10 km effort / 2 min jog',
        '3 x 2 km at 10 km effort / 3 min jog',
        '35 min with the middle 20 min at 10 km effort',
    ],
    'half_ironman': [
        '3 x 3 km at half-marathon effort / 3 min jog',
        '50 min with the middle 30 min at half-marathon effort',
        '4 x 2 km at half-marathon effort / 2 min jog',
        '2 x 5 km at half-marathon effort / 4 min jog',
        '60 min steady',
    ],
    'runlong': ['4 x 2 km at marathon effort / 2 min jog', '60 min steady'],
}


def race_pace(c):
    """Target pace (min per km) for the next run race, or None."""
    r = c.get('next_race') or {}
    if r.get('type') == 'run' and r.get('target_min') and r.get('run_km'):
        return r['target_min'] / r['run_km']
    return None


KNEE_RULE = 'Knee rule: flat, even ground. A pinch of 0 to 2 out of 10 that does not grow is fine. If it reaches 3 or changes how you run, stop, walk home and swap the next run for a swim'


def run_main(code, c):
    kind, wt = c['kind'], c['wtype']
    knee = c.get('knee')
    rp = race_pace(c)
    rp_txt = f' ({fmt_pace(rp)})' if rp else ''
    if code == 'RUN-RAM':
        return '20 to 30 min very easy run/walk', 'Optional. Before suhoor (about 04:15), then eat and drink at least 1 L. Skip it if you slept badly'
    if code == 'RUN-RAM-L':
        return '35 to 45 min easy run/walk', 'Before suhoor. Walk breaks every 5 min. Never run in the daytime heat while fasting'
    if code == 'RUN-L':
        km = c['long_km'] or 5
        if wt == 'taper' and kind == 'run5':
            return f'{km:g} km easy, 1 min walk every 10 min; last 1 km steady (not 5 km pace)', 'Easy and slow: conversation pace'
        if wt == 'taper' and rp and c['weeks_to'] == 1:
            mid = max(2, round(km / 2))
            return (
                f'{km:g} km: {max(1, round((km - mid) * 0.6)):g} km easy, {mid:g} km at race pace{rp_txt}, then easy to the end. Rehearse race food and kit',
                'Race pace should feel controlled',
            )
        walk = ', 1 min walk every 10 min' if km >= 9 else (', walk breaks allowed' if km >= 6 else '')
        extra = ''
        if km >= 16:
            extra = '. Practise race-day food and water'
        if knee:
            return f'{km:g} km easy on a flat route{walk} (distance held while the knee settles)', 'Easy and slow: conversation pace'
        return f'{km:g} km easy{walk}{extra}', 'Easy and slow: conversation pace'
    if code == 'RUN-S':
        if wt == 'recovery':
            return '20 min very easy', 'Recovery week: very easy'
        return '20 to 25 min easy + 4 x 20 s strides', 'Easy; strides quick and relaxed, full recovery between them. Short on purpose: the swim is this evening'
    if code == 'RUN-E':
        if wt == 'recovery':
            return '25 min very easy', 'Recovery week: very easy'
        if wt in ('taper', 'race'):
            return '20 min easy + 4 x 20 s strides', 'Easy, strides relaxed and quick'
        mins = min(30 + 5 * (c['level'] - 1) + 5 * (c['block_week'] % 4), 50)
        if wt == 'easy':
            mins = 25
        if knee:
            return f'{min(mins, 35)} min easy on flat ground', 'Easy: you can talk in full sentences'
        return f'{mins} min easy', 'Easy: you can talk in full sentences'
    # RUN-I
    if wt == 'recovery':
        return '25 min very easy (recovery week, no intervals)', 'Easy'
    if wt == 'taper' and rp and c['weeks_to'] == 1:
        return (
            f'Race-pace practice: 10 min easy, 2 x (8 min at race pace{rp_txt}, 3 min walk), 5 min easy',
            'Controlled, 6 to 7 out of 10: learn what race pace feels like'
            + ('. Flat ground; skip the race-pace parts if the knee is above 2 out of 10' if knee else ''),
        )
    if wt in ('taper', 'race'):
        return f'20 min easy + 4 x 1 min at race pace{rp_txt}', 'Race pace feels controlled, not hard'
    if knee:
        return (
            f'Race-pace practice: 10 min easy, 3 x (5 min at race pace{rp_txt}, 2 min walk), 5 min easy. No sprints or hills while the knee settles',
            'Controlled, 6 to 7 out of 10. If the knee is above 2 out of 10 before you start, walk 30 min or swim instead',
        )
    if wt == 'easy':
        return '30 min easy with 4 x 20 s strides (easy week)', 'Easy'
    lst = RUNI.get(kind, RUNI['runbase'])
    main = lst[(c['block_week'] - 1) % len(lst)].replace('{rp}', rp_txt)
    if kind == 'run5':
        return main, 'Hard parts at 8 out of 10, even pace on every repeat (the last as fast as the first); recoveries easy. Lap button at each repeat'
    return main, 'Hard parts at 7 to 8 out of 10; recoveries easy'


def run_rows(code, c, cfg):
    main, eff = run_main(code, c)
    pace = cfg['baseline'].get('run_pace_min_km') or 12
    zone = 'hard' if code == 'RUN-I' else 'easy'
    target = ''
    if code == 'RUN-L' and c['long_km']:
        mins = int(c['long_km'] * pace)
        target = (
            f'{c["long_km"]:g} km, about {mins // 60} h {mins % 60:02d} min at your current pace ({fmt_pace(pace)}; it will drop as you get fitter)'
            if mins >= 60
            else f'{c["long_km"]:g} km, about {mins} min at your current pace ({fmt_pace(pace)})'
        )
    long_session = code == 'RUN-L' and (c['long_km'] or 0) * pace >= 60
    rows = stretch_rows('W-RUN', 'Warm-up')
    rows.append(
        (
            'Targets',
            f'Effort: {eff}. Heart rate: {hr(cfg, zone)} for the {"hard parts" if code == "RUN-I" else "whole run"}' + (f'. {target}' if target else ''),
            1,
            '',
            '',
            'Run by effort and heart rate, not pace: Dar heat makes you 30 to 60 s/km slower at the same effort',
        )
    )
    rows.append(('Main', main, 1, '', '', 'Start before 06:30 to beat the heat. ' + eff))
    if 'strides' in main:
        n = int(main.split(' x 20 s strides')[0].split()[-1]) if ' x 20 s strides' in main else 4
        rows.append(('Strides', 'Strides', n, '20 s', 'walk back', 'After the easy part: fast and relaxed, about 85%, full recovery between them'))
    if code != 'SHAKE':
        rows.append(
            (
                'Form',
                'Short, quick, quiet steps',
                1,
                '',
                '',
                'Land with the foot under your hips and the knee slightly bent. About 5% more steps a minute than feels natural; no overstriding and no steep downhills',
            )
        )
    if c.get('knee'):
        rows.append(
            ('Knee check', KNEE_RULE, 1, '', '', 'After the run: ice or a cold cloth for 10 min if it aches, then the knee-care routine later in the day')
        )
    if long_session:
        rows.append(
            (
                'Fuel',
                'During the run: water every 20 min; 2 dates or half a banana every 40 min after the first hour',
                1,
                '30 to 45 g carbs per hour',
                '',
                'Carry ORS or a pinch of salt in your bottle. Practise what you will use on race day',
            )
        )
    rows.append(
        (
            'Hydration',
            'Water with a pinch of salt before and after',
            1,
            '500 ml',
            '',
            'Over 60 min: ORS afterwards. Weigh yourself before and after a long run: each kg lost = 1 L to drink back',
        )
    )
    rows += stretch_rows('C-RUN', 'Cool-down stretch')
    return rows


# ---------------------------------------------------------------------------- swimming
DRILLS = HT.SWIM_DRILLS


def swim_rows(code, c, d, cal):
    kind, wt = c['kind'], c['wtype']
    easy = wt in ('easy', 'taper', 'race')
    rows = stretch_rows('W-SWIM', 'Warm-up on the pool deck')
    rows.append(
        (
            'Warm-up in the water',
            'Easy freestyle, any breathing pattern',
            1,
            '200 m',
            '',
            'Easy, long strokes. Hands enter in front of the shoulders; breathe to both sides to share the load between the shoulders',
        )
    )
    if c.get('knee'):
        rows.append(
            (
                'Knee care',
                'Freestyle and backstroke only: no breaststroke kick',
                1,
                '',
                '',
                'The breaststroke whip kick twists the inside of the knee. Push off the wall gently with both feet and kick from the hips',
            )
        )
    if not code.startswith('SWIM-RAM') and code != 'SWIM-R':
        rows.append(
            (
                'Breathing (pumzi)',
                'Bubble breathing',
                2,
                '10 breaths',
                '20 s',
                'Hum out through the nose under water until the air is gone, then turn and take a quick breath in. Never hold your breath',
            )
        )
    C = c['swim_cont'] or 300
    if code in ('SWIM-E', 'SWIM-RAM-E'):
        if c['w'] == 1:
            rows.append(
                (
                    'Test',
                    'Non-stop swim test: as far as you can without stopping, up to 1,500 m',
                    1,
                    'max',
                    '',
                    'Steady pace you can hold. Log the metres as Longest non-stop swim.',
                )
            )
        elif d == cal.swim_test:
            rows.append(('Test', '1,500 m NON-STOP TEST', 1, '1,500 m', '', 'Even pace, breathe every 2 or 3 strokes. Log the metres and the time.'))
        else:
            rows.append(('Main', 'Non-stop freestyle', 1, f'{C:,} m', '', 'Steady, 5 to 6 out of 10. Do not stop at the wall: touch and go'))
            if not easy and code == 'SWIM-E':
                rows.append(
                    (
                        'SWOLF check',
                        'Count strokes on each length; note SWOLF on the watch',
                        4,
                        '1 length',
                        '30 s',
                        'Same easy effort each time. Try to take 1 fewer stroke per length by reaching further. A lower SWOLF than last week is progress',
                    )
                )
            if not easy and code == 'SWIM-E':
                n = 2 if kind in ('run10', 'runhalf') else 4
                rows.append(('Main', 'Freestyle repeats', n, '100 m', '15 s', '7 out of 10. Same time on each'))
            if kind in ('tribase', 'olympic', 'half_ironman', 'hyrox') and not easy:
                rows.append(('Skill', 'Sighting: lift your eyes forward every 6 strokes', 4, '25 m', '15 s', 'You need this in open water'))
    elif code in ('SWIM-T', 'SWIM-RAM-T'):
        n = 2 if (easy or code == 'SWIM-RAM-T') else {'run10': 4, 'runhalf': 6}.get(kind, 6)
        a, b = HT.DRILL_PAIRS[(c['w'] - 1) % len(HT.DRILL_PAIRS)]
        rows += [HT.drill_row(a, n <= 2), HT.drill_row(b, n <= 2)]
        if kind in ('run5', 'run10', 'runhalf', 'tribase', 'olympic', 'half_ironman') and not easy:
            rows.append(HT.drill_row('Sighting drill', True))  # open-water skill for the Ironman swim, practised early
        if kind in ('run5', 'run10', 'ramadan') or code == 'SWIM-RAM-T':
            rows.append(
                ('Main', 'Freestyle, breathing every 3 strokes', n, '100 m', '20 s', '6 out of 10. Count strokes per length; try to take 1 fewer each repeat')
            )
            if kind in ('run5', 'run10') and not easy:
                rows.append(
                    (
                        'Main',
                        'Even-pace freestyle',
                        4,
                        '50 m',
                        '30 s',
                        'Same time on each, at your normal pace (about 1:30). The 1,500 m in 1 hour needs only 2:00 per 50 m: the goal is to swim it without stopping',
                    )
                )
        elif kind == 'runhalf':
            rows.append(('Main', 'Steady freestyle intervals', n, '100 m', '15 s', '7 out of 10. Same time on each repeat: pacing practice'))
            if not easy:
                rows.append(('Main', 'Endurance repeats', 2, '200 m', '30 s', '6 out of 10'))
        else:
            rows.append(('Main', 'Race-pace freestyle', n, '200 m', '20 s', '7 out of 10. Even splits; sight every 6th stroke on the last 50 m'))
    else:  # SWIM-R
        rows.append(
            (
                'Main',
                'Relaxed freestyle, any breathing pattern; stop at the wall when you need to',
                1,
                '400 m' if c['wtype'] in ('race', 'recovery') else '600 m',
                '',
                '3 out of 10. Loosens the legs and keeps them fresh for the long session',
            )
        )
    rows.append(('Cool-down in the water', 'Easy backstroke', 1, '100 m', '', 'Very easy'))
    rows += stretch_rows('C-SWIM', 'Cool-down stretch')
    if code == 'SWIM-E' and kind in ('olympic', 'half_ironman') and not easy and c['w'] % 2 == 0:
        rows.append(
            (
                'Option',
                'Swim this in the sea instead of the pool',
                1,
                'same distance',
                '',
                'Calm water close to shore, with a buddy and a bright tow-float, before sunset. Never alone.',
            )
        )
    if code.startswith('SWIM-RAM'):
        rows.insert(
            0,
            ('Ramadan', 'Swim 60 to 90 min after iftar, once you have had water, dates and a light meal', 1, '', '', 'Drink 500 ml in the pool. Stop if dizzy'),
        )
    return rows


def swim_metres(rows):
    total = 0
    for r in rows:
        reps = str(r[3]).replace(',', '')
        if reps.endswith(' m') and reps.split(' ')[0].isdigit() and r[0] not in ('Option',):
            total += int(reps.split(' ')[0]) * (r[2] if isinstance(r[2], int) else 1)
    return total


# ---------------------------------------------------------------------------- cycling
BIKE_I = [
    '6 x 1 min fast pedalling (100+ turns a minute) / 2 min easy: cadence drill',
    '5 x 2 min hard / 2 min easy',
    '4 x 4 min hard / 3 min easy',
    '3 x 8 min hard / 3 min easy',
    '2 x 12 min tempo / 4 min easy',
    '5 x 3 min hill or big gear / 3 min easy',
    '3 x 15 min at 70.3 effort / 5 min easy',
]


def bike_rows(code, c):
    R = c['ride_min'] or 45
    if code == 'BIKE-L':
        main = (f'{R} min steady ride', 'Easy, 4 to 5 out of 10: you can talk. Pedal 80 to 90 turns a minute. Quiet roads early, or a spin bike')
        if R >= 120:
            main = (main[0] + ' (practise 70.3 pacing and fuelling)', main[1])
    else:
        if c['wtype'] != 'build' or c['block_week'] <= 1:
            main = ('40 min easy with 4 x 30 s fast pedalling', 'Bike handling: practise drinking, looking back and signalling')
        else:
            main = (
                BIKE_I[min(len(BIKE_I) - 1, (c['block_week'] - 1) // 2 + (2 if c['kind'] == 'half_ironman' else 0))],
                '"Hard" = 7 out of 10. 10 min easy before, 5 min easy after',
            )
    rows = stretch_rows('W-BIKE', 'Warm-up') + [('Main', main[0], 1, '', '', main[1])]
    if code == 'BIKE-L' and R >= 75:
        g = 30 if R < 120 else (45 if R < 180 else 60)
        rows.append(
            (
                'Fuel',
                f'Eat and drink on the bike from 30 min: {g} g carbs per hour',
                1,
                f'{g} g/h',
                '',
                '1 g of carbs: about 1 date = 18 g, 1 banana = 23 g, 500 ml homemade drink (30 g sugar or honey + pinch of salt) = 30 g. Raise it gradually to train your gut',
            )
        )
    rows.append(
        (
            'Safety',
            'Helmet, front and rear lights, bright top, two bottles, puncture kit',
            1,
            '',
            '',
            'Ride with the traffic; avoid daladala routes at rush hour',
        )
    )
    return rows + stretch_rows('C-BIKE', 'Cool-down stretch')


def brick_rows(c):
    R = c['ride_min'] or 45
    b = int(round(max(30, R * 0.6) / 5) * 5)
    km = max(2, min(10, round((c['long_km'] or 6) * 0.4)))
    if c['wtype'] in ('taper', 'race', 'easy', 'recovery'):
        b, km = int(round(b * 0.7 / 5) * 5), max(2, km // 2)
    rows = stretch_rows('W-BIKE', 'Warm-up') + [
        ('Main', f'Bike {b} min steady', 1, f'{b} min', '', '5 out of 10. Drink every 15 min'),
        (
            'Main',
            f'Straight into a {km} km run',
            1,
            f'{km} km',
            'Under 2 min to change',
            '5 out of 10. Heavy legs for 5 to 10 min is normal: that is what you are training',
        ),
        ('Skill', 'Transition practice: lay out shoes, belt, cap and gel; change in under 2 min', 1, '', '', 'Racked bike, helmet off last'),
    ]
    return rows + stretch_rows('C-RUN', 'Cool-down stretch')


# ---------------------------------------------------------------------------- HYROX simulation
def hx_sim_rows(c):
    n = min(8, 4 + c['block_week'] // 2)
    f = min(1.0, 0.5 + 0.1 * c['block_week'])
    rows = stretch_rows('W-RUN', 'Warm-up')
    for k in range(n):
        name, race, gym, home, trains, cue = HX.STATIONS[k % 8]
        rows.append(
            (
                f'Round {k + 1}',
                f'Run 1 km, then {name} (gym: {gym}; home: {home})',
                1,
                f'{int(f * 100)}% of the race amount ({race})',
                'none',
                '7 out of 10. Fast transitions',
            )
        )
    rows += stretch_rows('C-RUN', 'Cool-down stretch')
    rows.append(('Fuel', 'Water between rounds; eat a normal meal 2 to 3 h before', 1, '', '', ''))
    rows.append(('Log', 'Log the total time in the session feedback', 1, '', '', ''))
    return rows


# ---------------------------------------------------------------------------- other days
def fast_rows(cfg):
    t = cfg.get('fasting', {}).get('break_time', '18:50')
    return (
        [
            (
                'Fasting day',
                f'Break the fast at {t}: water first, then dates and a light meal',
                1,
                '',
                '',
                'Drink 500 ml to 1 L slowly before any activity. No running, swimming or strength today.',
            ),
            ('Main', 'Easy walk after eating', 1, '20 to 30 min', '', 'Very easy, conversation pace. Skip it if you feel dizzy or weak'),
        ]
        + stretch_rows('M-FLOW', 'Mobility')
        + [
            (
                'Kegels',
                'Kegels lying down, 10 min',
                1,
                '2 x 8 slow holds, 2 x 10 quick squeezes, 6 relaxation breaths',
                '',
                'Gentle, full relaxation between reps',
            )
        ]
    )


def rest_rows():
    return (
        [('Recovery', 'Easy walk outside in the morning sun', 1, '30 to 45 min', '', 'Conversation pace')]
        + stretch_rows('M-FLOW', 'Mobility')
        + [
            (
                'Planning',
                'Weekly review and meal prep',
                1,
                '45 min',
                '',
                'Check the weekly review; cook maharage and dengu, boil eggs, cook dagaa or fish, chop kachumbari',
            )
        ]
    )


def test_rows():
    return [
        ('Test', 'Weigh-in (after the toilet, before food), waist at the navel, front and side photos', 1, '', '', 'Log them in Profile > Baselines'),
        ('Test', 'Push-ups: as many as possible in one set', 1, 'max', '3 min', 'Note whether on knees or toes'),
        ('Test', 'Plank hold', 1, 'max', '3 min', ''),
        ('Test', 'Wall sit hold', 1, 'max', '3 min', ''),
        ('Test', 'Single-arm jerrycan row with a full 20 L jerrycan, weaker arm', 1, 'max', '', ''),
        ('Easy', 'Easy run/walk after the tests', 1, '15 min', '', 'Easy'),
    ]


def race_rows(r, cfg):
    t = r.get('target_min')
    rows = []
    if r['type'] == 'run':
        km = r.get('run_km') or 10
        pace = t / km if t else None
        plan = (
            (f'Target pace {fmt_pace(pace)}. Start 30 s/km slower for the first 2 km, then settle. ' if pace else '')
            + ('A 1 min walk every 9 to 10 min or at every water station is fine. ' if km >= 8 else '')
            + ('Water at every station, 2 dates or a gel every 40 min. ' if km >= 15 else '')
            + f'Heart rate mostly {hr(cfg, "race10")}.'
        )
        rows.append(('Race', race_title(r), 1, f'{km:g} km', '', plan))
    elif r['type'] == 'hyrox':
        div = r.get('division', 'Men Open')
        std = HX.DIVISIONS.get(div, HX.DIVISIONS['Men Open'])
        rows.append(
            (
                'Race',
                race_title(r),
                1,
                '8 x (1 km + station)',
                '',
                f'Start the runs easy; break the wall balls into sets from the start. {div}: sled push {std["sled_push"]}, sled pull {std["sled_pull"]}, '
                f'farmers {std["farmers"]}, sandbag {std["sandbag"]}, wall balls {std["wall_ball"]}.',
            )
        )
    else:
        rows.append(
            ('Race', race_title(r), 1, '', '', 'Start at the back of the swim, even pace. On the bike eat and drink every 20 min. Run the first 2 km easy.')
        )
        if (r.get('bike_km') or 0) >= 60:
            rows.append(
                (
                    'Fuel',
                    'Race fuelling plan',
                    1,
                    '60 to 90 g carbs per hour on the bike, 30 to 60 g on the run',
                    '',
                    'Exactly what you practised on long rides. 500 to 750 ml fluid an hour with electrolytes',
                )
            )
    rows.append(
        (
            'Before',
            'Breakfast 2 to 3 h before the start: familiar food (ndizi, wali, bread with honey), plus 500 ml water',
            1,
            '',
            '',
            'Do not dry-fast on race day. Nothing new on race day.',
        )
    )
    if r.get('note'):
        rows.append(('Note', r['note'], 1, '', '', ''))
    return rows


def shake_rows():
    return [('Main', 'Easy jog with 4 short pick-ups of 15 s', 1, '15 min', '', 'Very easy. Lay out your kit, eat familiar food, sleep early')]


def session_rows(code, c, cal, d):
    cfg = cal.cfg
    if code in STRENGTH_CODES:
        return strength_rows(code, c)
    if code in ('RUN-E', 'RUN-S', 'RUN-I', 'RUN-L', 'RUN-RAM', 'RUN-RAM-L'):
        return run_rows(code, c, cfg)
    if code.startswith('SWIM'):
        return swim_rows(code, c, d, cal)
    if code in ('BIKE-I', 'BIKE-L'):
        return bike_rows(code, c)
    if code == 'BRICK':
        return brick_rows(c)
    if code == 'HX-SIM':
        return hx_sim_rows(c)
    if code == 'MOB':
        return (
            [('Main', 'Easy walk', 1, '20 to 30 min', '', 'Conversation pace. Keeps the legs loose without loading them')]
            + stretch_rows('M-FLOW', 'Mobility')
            + [
                ('Kegels', 'Slow kegel holds', 1, '10', '', 'Lying down: squeeze and lift for 5 s, then relax fully for 10 s'),
                ('Kegels', 'Quick kegel squeezes', 1, '10', '', 'A strong 1 s squeeze, then 2 s of full relaxation'),
                ('Kegels', 'Relaxation breathing', 1, '6 slow breaths', '', 'Let the pelvic floor drop and relax on every breath in'),
            ]
        )
    if code == 'REST':
        return rest_rows()
    if code == 'TEST':
        return test_rows()
    if code == 'SHAKE':
        return shake_rows()
    if code == 'FAST':
        return fast_rows(cfg)
    if code == 'RACE':
        return race_rows(cal.race_on[d], cfg)
    raise KeyError(code)


def summary(code, rows, c):
    if code in STRENGTH_CODES:
        main = [r for r in rows if r[0] in ('Main', 'Accessory', 'Core', 'Station')]
        if code == 'HX-S':
            txt = f'8 HYROX stations, {main[0][2]} sets each at part distance (gym machines if you can, home versions if not)'
        else:
            txt = '; '.join(f'{r[1]} {r[2]} x {r[3]}' for r in main)
        return txt + '. Kegel finisher: ' + kegel_text(kegel_for(code, c['w'], c.get('knee')))
    if code.startswith('SWIM'):
        parts = [r for r in rows if r[0] in ('Drills', 'Main', 'Test', 'Skill')]
        body = '; '.join(r[1] if r[0] == 'Test' else (f'{r[2]} x {r[3]} ' if r[2] not in ('', 1) else (f'{r[3]} ' if r[3] else '')) + r[1] for r in parts)
        if any(r[0] == 'Test' for r in parts):
            return '200 m easy warm-up, then ' + body + ', then 100 m easy'
        return f'{swim_metres(rows):,} m total: ' + body
    if code == 'HX-SIM':
        n = sum(1 for r in rows if r[0].startswith('Round'))
        return f'{n} rounds of: run 1 km, then one HYROX station. No rest. Time it.'
    if code == 'MOB':
        return 'Easy walk 20 to 30 min, then mobility and stretching (20 min) and 5 min of kegels: ' + warmup_text('M-FLOW')
    if code == 'FAST':
        return 'Dry fast. After breaking the fast: easy walk 20 to 30 min, 20 min mobility and 10 min of kegels. No run, no swim, no strength.'
    if code == 'REST':
        return 'Walk 30 to 45 min; mobility and stretching (20 min); weekly review; meal prep'
    if code == 'RACE':
        return rows[0][1]
    main = [r for r in rows if r[0] in ('Main', 'Test', 'Race')]
    return '; '.join((f'{r[2]} x {r[3]} ' if r[2] not in ('', 1) else (f'{r[3]} ' if r[3] and r[3] != 'max' else '')) + r[1] for r in main)


def session_meta(code, rows, c, cfg):
    """Structured numbers for the coach and the progress charts."""
    m = {
        'discipline': (
            'strength'
            if code in STRENGTH_CODES
            else 'run'
            if code in RUN_CODES and code not in ('BRICK', 'HX-SIM')
            else 'swim'
            if code.startswith('SWIM')
            else 'bike'
            if code in ('BIKE-I', 'BIKE-L')
            else 'brick'
            if code == 'BRICK'
            else 'hyrox'
            if code == 'HX-SIM'
            else 'race'
            if code == 'RACE'
            else 'recovery'
        ),
        'hard': code in HARD_CODES and c['wtype'] == 'build',
    }
    if code == 'RUN-L':
        m['km'] = c['long_km']
        m['min'] = int((c['long_km'] or 0) * (cfg['baseline'].get('run_pace_min_km') or 12))
    if code.startswith('SWIM'):
        m['m'] = swim_metres(rows)
    if code in ('BIKE-L',):
        m['min'] = c['ride_min']
    return m


def warmups_for(am, pm):
    out = []
    for code in (am, pm):
        if not code:
            continue
        key = (
            'W-STR'
            if code in STRENGTH_CODES
            else 'W-RUN'
            if code in RUN_CODES and code != 'BRICK'
            else 'W-SWIM'
            if code.startswith('SWIM')
            else 'W-BIKE'
            if code in BIKE_CODES
            else None
        )
        if key and key not in [k for k, _ in out]:
            out.append((key, {'W-STR': 'Before strength', 'W-RUN': 'Before the run', 'W-SWIM': 'Before the swim', 'W-BIKE': 'Before the ride'}[key]))
    return '\n'.join(f'{label}: {warmup_text(k)}' for k, label in out)


def session_name(code, c, cal, d):
    if code == 'RACE':
        return cal.race_on[d]['name']
    return NAMES[code]
