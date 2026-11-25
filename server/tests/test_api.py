import datetime as dt
from pathlib import Path

from app import main
from app.main import DEFAULT_PLAN as PLAN


def test_health_and_plan(client):
    h = client.get('/health').json()
    assert h['ok'] and h['days'] == len(PLAN['days']) == 300
    r = client.get('/api/plan')
    assert r.status_code == 200 and r.json()['start'] == '2026-10-27' and r.json()['end'] == '2027-08-22'
    assert client.get('/api/plan', headers={'If-None-Match': r.headers['etag']}).status_code == 304


def test_register_login_me(client, auth):
    assert client.get('/api/auth/me', headers=auth).json()['email'] == 'salum@example.com'
    assert client.post('/api/auth/login', json={'email': 'SALUM@example.com', 'password': 'strong-pass-1'}).status_code == 200
    assert client.post('/api/auth/login', json={'email': 'salum@example.com', 'password': 'wrong-pass-1'}).status_code == 401
    assert client.get('/api/auth/me').status_code == 401


def test_first_only_registration(client, monkeypatch):
    monkeypatch.setattr(main, 'REGISTRATION_MODE', 'first-only')
    assert client.post('/api/auth/register', json={'email': 'a@x.com', 'password': 'password-1'}).status_code == 201
    assert client.post('/api/auth/register', json={'email': 'b@x.com', 'password': 'password-1'}).status_code == 403


def test_day_log_validation_and_last_write_wins(client, auth):
    ok = {'weight': 87.2, 'sleep_h': 7.5, 'am_done': True, 'done': ['1-STR-B:9'], 'sets': {'1-STR-B:9': [{'kg': 0, 'reps': 12}]}, 'notes': 'good'}
    r = client.put('/api/days/2026-10-27', json={'data': ok, 'updated_at': '2026-10-27T18:00:00Z'}, headers=auth)
    assert r.status_code == 200 and r.json()['applied']
    old = client.put('/api/days/2026-10-27', json={'data': {'weight': 99}, 'updated_at': '2026-10-27T10:00:00Z'}, headers=auth).json()
    assert old['applied'] is False and old['data']['weight'] == 87.2
    assert client.put('/api/days/2026-10-27', json={'data': {'weight': 5}}, headers=auth).status_code == 422
    assert client.put('/api/days/2026-10-27', json={'data': {'hack': 1}}, headers=auth).status_code == 422
    assert client.put('/api/days/2030-01-01', json={'data': {}}, headers=auth).status_code == 404


def test_users_cannot_see_each_other(client, auth):
    client.put('/api/days/2026-10-28', json={'data': {'weight': 87}}, headers=auth)
    r = client.post('/api/auth/register', json={'email': 'other@example.com', 'password': 'strong-pass-2'})
    other = {'Authorization': 'Bearer ' + r.json()['token']}
    assert client.get('/api/days/2026-10-28', headers=other).status_code == 404
    assert client.get('/api/sync', headers=other).json()['days'] == []


def test_results_and_sync(client, auth):
    assert client.put('/api/results/base:pushups', json={'value': 12}, headers=auth).status_code == 200
    assert client.put('/api/results/goal:Goal 3', json={'value': 96}, headers=auth).status_code == 200
    assert client.put('/api/results/nope:1', json={'value': 1}, headers=auth).status_code == 404
    s1 = client.get('/api/sync', headers=auth).json()
    assert {r['key'] for r in s1['results']} == {'base:pushups', 'goal:Goal 3'}
    s2 = client.get('/api/sync', params={'since': s1['server_time']}, headers=auth).json()
    assert s2['results'] == [] and s2['days'] == []


def test_summary_goals_and_minis(client, auth):
    w = 87.5
    for i in range(14):
        d = (dt.date(2026, 10, 27) + dt.timedelta(days=i)).isoformat()
        w -= 0.12
        client.put(
            f'/api/days/{d}',
            json={
                'data': {
                    'weight': round(w, 1),
                    'sleep_h': 7.8,
                    'protein': 165,
                    'am_done': True,
                    'pm_done': True,
                    'run_km': 6.0 if i == 4 else 0,
                    'swim_cont_m': 650 if i == 1 else 0,
                }
            },
            headers=auth,
        )
    client.put('/api/results/base:pushups', json={'value': 12}, headers=auth)
    sm = client.get('/api/summary', params={'today': '2026-11-09'}, headers=auth).json()
    g = {x['id']: x for x in sm['goals']}
    assert g['Goal 1']['status'] == 'On track' and 85 < g['Goal 1']['current'] < 87
    assert g['Goal 2']['status'] == 'In progress' and g['Goal 2']['longest_run_km'] == 6.0 and abs(g['Goal 2']['progress'] - 0.6) < 1e-9
    assert g['Goal 11']['progress'] == 6.0 / 21.1
    assert g['Goal 6']['current'] == 650
    assert g['Goal 9']['current'] == 1.0 and g['Goal 9']['status'] == 'Achieved'
    assert g['Goal 8']['baseline'] == 12
    m = {x['text']: x for x in sm['mini_goals']}
    assert m['Long run 8 km']['due'] == '2026-11-14' and m['Long run 8 km']['status'] != 'Hit'
    assert m['Push-ups: baseline + 5']['target'] == 17
    assert m['GOAL: 30 push-ups (or double the baseline)']['target'] == 24
    first = next(x for x in sm['mini_goals'] if x['goal'] == 'Goal 1' and x['due'] == '2026-11-08')
    assert first['due'] == '2026-11-08' and first['status'] in ('Hit', 'Missed') and first['actual'] is not None
    assert sm['weeks'][0]['planned'] > 0 and sm['weeks'][0]['done'] > 0
    csv = client.get('/api/export/days.csv', headers=auth)
    assert csv.status_code == 200 and csv.text.splitlines()[0].startswith('date,week')


def test_race_goal_with_result(client, auth):
    client.put('/api/days/2026-11-07', json={'data': {'run_km': 5.5}}, headers=auth)
    client.put('/api/results/goal:Goal 2', json={'value': 96}, headers=auth)
    g = {x['id']: x for x in client.get('/api/summary', params={'today': '2026-12-05'}, headers=auth).json()['goals']}
    assert g['Goal 2']['status'] == 'Achieved' and g['Goal 2']['progress'] == 1.0
    client.put('/api/results/goal:Goal 2', json={'value': 130}, headers=auth)
    g = {x['id']: x for x in client.get('/api/summary', params={'today': '2026-12-06'}, headers=auth).json()['goals']}
    assert g['Goal 2']['status'] == 'Missed' and abs(g['Goal 2']['progress'] - 100 / 130) < 1e-9


def test_v1_prefix_and_public_plan(client):
    assert client.get('/api/v1/health').json()['ok']
    assert client.get('/api/v1/plan').json()['version'] == PLAN['version']


def test_config_races_and_plan_regeneration(client, auth):
    c = client.get('/api/config', headers=auth).json()
    assert c['plan_version'] == PLAN['version'] and c['config']['fasting']['weekdays'] == []
    r = client.put(
        '/api/races/rhyrox', json={'name': 'HYROX Cape Town', 'type': 'hyrox', 'date': '2027-06-26', 'target_min': 110, 'division': 'Men Open'}, headers=auth
    )
    assert r.status_code == 200, r.text
    v2 = r.json()['plan_version']
    assert v2 != PLAN['version']
    plan = client.get('/api/plan', headers=auth).json()
    days = {d['date']: d for d in plan['days']}
    assert days['2027-06-26']['race'].startswith('HYROX CAPE TOWN') and days['2027-06-12']['race'] is None
    g3 = next(g for g in plan['goals'] if g['id'] == 'Goal 3')
    assert g3['deadline'] == '2027-06-26' and g3['target'] == 110
    add = client.post('/api/races', json={'name': 'Dar 5 km fun run', 'type': 'run', 'date': '2026-11-28', 'priority': 'C', 'run_km': 5}, headers=auth)
    assert add.status_code == 201
    rid = add.json()['race']['id']
    assert client.delete(f'/api/races/{rid}', headers=auth).status_code == 200
    assert client.put('/api/races/rhyrox', json={'name': 'x', 'type': 'swimrun', 'date': '2027-06-26'}, headers=auth).status_code == 422
    assert client.put('/api/races/nope', json={'name': 'x', 'type': 'run'}, headers=auth).status_code == 404
    assert len(client.get('/api/plan/history', headers=auth).json()['versions']) >= 2
    # the public default plan is unchanged
    assert client.get('/api/plan').json()['version'] == PLAN['version']


def test_history_is_kept_when_a_day_changes(client, auth):
    client.put(
        '/api/days/2026-11-10', json={'data': {'am_done': True, 'planned': {'am': 'Run: quality session'}}, 'updated_at': '2026-11-10T06:00:00Z'}, headers=auth
    )
    client.put('/api/days/2026-11-10', json={'data': {'am_done': False}, 'updated_at': '2026-11-10T08:00:00Z'}, headers=auth)
    h = client.get('/api/days/2026-11-10/history', headers=auth).json()
    assert h['versions'][0]['data']['planned']['am'] == 'Run: quality session'


def test_feedback_readiness_and_coach(client, auth):
    fb = {'done': 'yes', 'rpe': 7, 'pain': True, 'pain_area': 'knee', 'energy': 3, 'notes': 'ok'}
    for d in ('2026-11-08', '2026-11-10'):
        assert client.put(f'/api/days/{d}', json={'data': {'pm_fb': fb, 'sleep_h': 5, 'soreness': 4}}, headers=auth).status_code == 200
    assert client.put('/api/days/2026-11-10', json={'data': {'am_fb': {'done': 'maybe'}}}, headers=auth).status_code == 422
    t = client.get('/api/coach/today', params={'day': '2026-11-10'}, headers=auth).json()
    assert t['readiness']['level'] == 'amber' and t['persistent_pain'] == ['knee'] and 'pain_advice' in t
    sets = {'3-STR-A:8': [{'kg': 10, 'reps': 12, 'rpe': 7, 'ex': 'Backpack goblet squat'}] * 3}
    client.put('/api/days/2026-11-03', json={'data': {'sets': sets}}, headers=auth)
    p = client.get('/api/coach/progression', params={'exercise': 'Backpack goblet squat', 'reps': '10 to 12', 'day': '2026-11-11'}, headers=auth).json()
    assert p['action'] == 'hold'  # knee pain is persistent, so no progression


def test_garmin_import_sets_the_baseline(client, auth):
    text = (Path(__file__).resolve().parents[1] / 'app' / 'engine' / 'data' / 'Activities.csv').read_text()
    r = client.post('/api/activities/import', json={'csv': text, 'apply_baseline': True}, headers=auth).json()
    assert r['imported'] == 7 and r['new'] == 7 and r['baseline']['long_run_km'] == 8.01  # 4.98 miles, detected and converted
    again = client.post('/api/activities/import', json={'csv': text}, headers=auth).json()
    assert again['new'] == 0
    acts = client.get('/api/activities', headers=auth).json()['activities']
    swim = next(a for a in acts if a['type'] == 'swim')
    assert swim['distance_m'] == 854 and swim['swolf'] == 34
    assert client.get('/api/sync', headers=auth).json()['activities']
    assert client.post('/api/activities/import', json={'csv': 'a,b\n1,2'}, headers=auth).status_code == 422
    assert 'distance_km' in client.get('/api/export/activities.csv', headers=auth).text
