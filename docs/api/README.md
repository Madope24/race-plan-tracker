# API

- Interactive docs: `http://<server>:8090/api/docs`. Full spec: `docs/api/openapi.json`.
- All routes are under `/api/v1` and, for older app versions, also under `/api`.
- Errors are JSON in the form `{"detail": "..."}`.

| Area | Routes |
|---|---|
| Health | `GET /health` |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Plan | `GET /plan` (your plan if signed in, with an ETag), `GET /plan/version`, `GET /plan/history` |
| Config and races | `GET/PUT /config`, `GET/POST /races`, `PUT/DELETE /races/{id}` |
| Days | `PUT/GET /days/{date}`, `GET /days/{date}/history` |
| Results | `PUT /results/{base:..., goal:..., mini:...}` |
| Activities | `POST /activities/import` (Garmin CSV text), `PUT /activities`, `GET /activities` |
| Sync | `GET /sync?since=` |
| Coach | `GET /coach/today?day=`, `GET /coach/progression?exercise=&reps=`, `GET /coach/explain?day=` |
| Summary and export | `GET /summary`, `GET /export/days.csv`, `GET /export/activities.csv` |

## Contract test
`server/tests/api_contract.json` lists every route and method the app depends on, and CI fails if one changes. After a deliberate change, regenerate it from the `server` folder:

```
python -c "import json,os; os.environ.setdefault('JWT_SECRET','x'*40); from app.main import app; s=app.openapi(); open('tests/api_contract.json','w').write(json.dumps({p: sorted(m.upper() for m in o) for p,o in sorted(s['paths'].items())}, indent=1)); open('../docs/api/openapi.json','w').write(json.dumps(s, indent=1, sort_keys=True))"
```
This rewrites the contract file and the OpenAPI document from the running code.
