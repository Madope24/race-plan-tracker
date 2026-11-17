from app.engine import coach
from app.engine.build import build_plan

PLAN = build_plan()


def test_one_bad_metric_alone_never_changes_the_plan():
    r = coach.readiness({'2026-11-10': {'sleep_h': 5}}, '2026-11-10')
    assert r['level'] == 'green' and r['signals']
    r = coach.readiness({'2026-11-10': {'soreness': 5}}, '2026-11-10')
    assert r['level'] == 'green'


def test_poor_sleep_and_sore_legs_reduce_the_hard_session():
    r = coach.readiness({'2026-11-10': {'sleep_h': 5.5, 'soreness': 4}}, '2026-11-10')
    assert r['level'] == 'amber'
    s = PLAN['sessions']['3-RUN-I']
    a = coach.adjust(s, r['level'], [])
    assert a['action'] == 'reduce'


def test_many_signals_make_a_recovery_day():
    days = {f'2026-11-0{i}': {'rhr': 58} for i in range(1, 8)}
    days['2026-11-10'] = {'sleep_h': 5, 'soreness': 5, 'energy': 1, 'rhr': 67, 'stress': 5}
    r = coach.readiness(days, '2026-11-10')
    assert r['level'] == 'red'
    assert coach.adjust(PLAN['sessions']['3-STR-A'], 'red', [])['action'] == 'swap'


def test_coach_never_adds_load():
    for s in list(PLAN['sessions'].values())[:400]:
        for lvl in ('green', 'amber', 'red'):
            assert coach.adjust(s, lvl, [])['action'] in ('as planned', 'reduce', 'swap')


def test_persistent_pain_stops_progression():
    days = {'2026-11-08': {'pm_fb': {'pain': True, 'pain_area': 'knee'}}, '2026-11-10': {'pain_areas': ['knee']}}
    pain = coach.persistent_pain(days, '2026-11-11')
    assert pain == ['knee']
    assert coach.loads_area('Backpack goblet squat', pain) == ['knee']
    p = coach.progression([{'date': 'x', 'sets': [{'kg': 10, 'reps': 12}] * 3}], '10 to 12', pain_blocked=True)
    assert p['action'] == 'hold'
    a = coach.adjust(PLAN['sessions']['3-RUN-L'], 'green', pain)
    assert a['action'] == 'swap' and 'physiotherapist' in a['note']
    assert 'pain_advice' in coach.today(PLAN, days, '2026-11-11')
    assert coach.persistent_pain({'2026-11-10': {'pain_areas': ['knee']}}, '2026-11-11') == []  # once is not persistent


def test_progression_changes_one_variable_at_a_time():
    hit = [{'date': 'a', 'sets': [{'kg': 12, 'reps': 12, 'rpe': 8}] * 3}]
    p = coach.progression(hit, '10 to 12')
    assert p['action'] == 'add_load' and p['kg'] == 14.0 and 'Do not change anything else' in p['text']
    bw = [{'date': 'a', 'sets': [{'kg': 0, 'reps': 12}] * 3}]
    assert coach.progression(bw, '10 to 12')['action'] == 'add_reps'
    hard = [{'date': 'a', 'sets': [{'kg': 12, 'reps': 12, 'rpe': 10}] * 3}]
    assert coach.progression(hard, '10 to 12')['action'] == 'repeat'
    miss = [{'date': 'a', 'sets': [{'kg': 20, 'reps': 6}]}, {'date': 'b', 'sets': [{'kg': 20, 'reps': 7}]}]
    assert coach.progression(miss, '8 to 10')['action'] == 'reduce'
    heavy = [{'date': 'a', 'sets': [{'kg': 60, 'reps': 10}] * 3}]
    assert coach.progression(heavy, '8 to 10')['kg'] - 60 <= 2.5


def test_fasting_toggle_swaps_demanding_sessions():
    a = coach.adjust(PLAN['sessions']['3-STR-A'], 'green', [], fasting_today=True)
    assert a['action'] == 'swap'


def test_run_load_warning_and_streak():
    days = {'2026-11-03': {'run_km': 6}, '2026-11-10': {'run_km': 6}, '2026-11-17': {'run_km': 6}, '2026-11-24': {'run_km': 12}}
    assert coach.run_load_warning(days, '2026-11-24')
    logs = {d['date']: {'am_done': True, 'pm_done': True} for d in PLAN['days'][:10]}
    assert coach.streak(PLAN['days'], logs, PLAN['days'][9]['date']) > 3


def test_explanations_work_without_any_ai_provider(monkeypatch):
    from app import ai

    for k in ('AI_BASE_URL', 'AI_API_KEY', 'AI_MODEL'):
        monkeypatch.delenv(k, raising=False)
    facts = coach.today(PLAN, {'2026-11-10': {'sleep_h': 5.5, 'soreness': 4}}, '2026-11-10')
    out = ai.explain(facts)
    assert out['source'] == 'rules' and 'easier' in out['text']
    monkeypatch.setenv('AI_BASE_URL', 'http://127.0.0.1:9')
    monkeypatch.setenv('AI_API_KEY', 'x')
    monkeypatch.setenv('AI_MODEL', 'm')
    assert ai.explain(facts)['source'].startswith('rules')  # provider down: falls back, never fails
