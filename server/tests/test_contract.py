"""API contract: the routes the mobile app depends on must not disappear or change method without a deliberate update.

If you change the API on purpose, regenerate tests/api_contract.json (see docs/api/README.md)."""

import json
from pathlib import Path

from app.main import app

CONTRACT = json.loads((Path(__file__).parent / 'api_contract.json').read_text())
APP_NEEDS = [
    '/api/v1/auth/login',
    '/api/v1/auth/register',
    '/api/v1/days/{iso}',
    '/api/v1/results/{key}',
    '/api/v1/sync',
    '/api/v1/plan',
    '/api/v1/config',
    '/api/v1/activities',
    '/api/v1/activities/import',
    '/health',
]


def current():
    return {p: sorted(m.upper() for m in ops) for p, ops in app.openapi()['paths'].items()}


def test_contract_matches():
    now = current()
    missing = {p: m for p, m in CONTRACT.items() if now.get(p) != m}
    assert not missing, f'API changed: {missing}'
    assert set(now) == set(CONTRACT), f'New routes not in the contract: {set(now) - set(CONTRACT)}'


def test_app_routes_exist():
    now = current()
    for p in APP_NEEDS:
        assert p in now, p


def test_error_shape_is_detail(client):
    r = client.get('/api/v1/days/2026-11-10')
    assert r.status_code == 401 and 'detail' in r.json()
