import os
import sys
from pathlib import Path

os.environ['DATABASE_URL'] = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + str(Path(__file__).parent / 'test.db')  # CI also runs against Postgres
os.environ['JWT_SECRET'] = 'test-secret-test-secret-test-secret-1234'
os.environ['REGISTRATION_MODE'] = 'open'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    r = client.post('/api/auth/register', json={'email': 'salum@example.com', 'password': 'strong-pass-1'})
    assert r.status_code == 201, r.text
    return {'Authorization': 'Bearer ' + r.json()['token']}
