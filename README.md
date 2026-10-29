# Race Plan — Kilimanjaro Half Marathon tracker

A simple workout app (Flutter, Android) for the plan from Thursday 29 October 2026 (week 0) to the Kilimanjaro Half Marathon on Sunday 7 February 2027, with your own server as the single endpoint for every update. Monday and Thursday are dry-fast days (evening walk and mobility only); a run and a swim are never on the same day.

```
race-plan-tracker/
├── app/                  Flutter app (Home dashboard, Workouts, Track, Guide, Settings)
├── backend/              FastAPI + SQLite API, Dockerfile, tests
│   └── data/             plan.json (143 sessions, weeks 0–14) + reference.json (the in-app Guide)
├── deploy/               docker-compose.yml, Caddyfile (optional HTTPS), .env.example
├── scripts/              plan_data.py + meals.py (the plan), build_workbook.py (Excel), export_plan.py (JSON)
└── .github/workflows/    build-apk.yml (APK) and deploy-backend.yml (test + deploy to your server)
```

## What the app does

| Tab | What you see |
|---|---|
| **Home** | Days to race, week and phase, fast-day banner, today's workouts, **the weekly decision** (green = progress, amber = repeat the week, red = step back, with the reasons), completion ring, streak, 7-day average weight, run minutes and swim metres this week, **race outlook** from your latest 5 km test, weight vs expected range chart, weekly completion bars, 7-day sleep/energy/resting pulse. Refreshes itself after every sync. |
| **Workouts** | Pick a week (0–14), see each day (fast days marked), tap a workout for full instructions, a workout timer, rest timers and the log form (done / partial / skipped, minutes, distance, effort 1–10, notes). |
| **Track** | The 2-minute daily log (weight, resting pulse, sleep and quality, soreness, pain and where, energy, mood, motivation, eating to plan, protein, water; fast kept, fasting tolerance and warning signs on fast days) and the Sunday check-in (waist, long session, longest non-stop swim, 5 km test). |
| **Guide** | Strength A and B, swimming, nutrition and fast days, the 7-day meal plan, fuelling, race plan and pacing, weekly rules. |

The weekly decision follows the plan's rules: **red** if pain reached 4/10, under 60% of sessions were done, sleep averaged under 6 h or fast-day warning signs were logged; **amber** if 60–84% were done, runs averaged RPE 5+, pain reached 3/10, sleep averaged 6–6.4 h, or energy or mood averaged under 3; otherwise **green**. Today's sessions only count once they are done.

## How syncing works

- Every change is saved on the phone first, then queued for the server, so the app works offline.
- **Automatic sync every 4 minutes** while the app is open. It also syncs as soon as you open the app, 3 seconds after any change, on pull-to-refresh, and from the cloud button.
- A sync pushes waiting changes, then pulls the full state (plan, logs, habits, check-ins and the dashboard the server calculates).
- If you edit on two phones, the newest edit wins (based on when it was made, not when it reached the server).
- Android does not allow apps to run every 4 minutes in the background once they are closed. When you open the app it syncs immediately, so nothing is lost.

## Workout reminders

Reminders are scheduled **on the phone, in advance, for every remaining day of the plan** (about 320). They live in Android's alarm system, so they fire with the app closed, with no internet, and after a reboot.

| Reminder | When | Notes |
|---|---|---|
| Today's plan + weigh-in prompt | 05:00 (you choose); fast days 04:10, before suhoor | Lists the day's workouts; fast days remind you not to exercise until after 18:50 |
| Before each workout | Morning 05:30 · Afternoon 16:15 · Any time 16:30 · Evening 17:30 · After iftar 19:40 · Before bed 21:30 | Tap it to open that workout |
| Log reminder | 22:00 | Only if a run, swim or strength session from that day isn't logged |

Logging a workout cancels its reminders. The schedule is rebuilt after any change (a sync, a log, a settings change), and only when something actually changed. Manage everything from the bell icon on Home or **Settings → Workout reminders**, including a test notification. On first launch the app asks for notification permission. Reminder times use East Africa Time.

---

## 1. Server setup (once)

On your server (for example `ssh root@164.68.97.148`), install Docker if it isn't there yet. Then:

```bash
mkdir -p /root/race-plan/deploy
```
Creates the folder the deploy workflow copies into.

```bash
openssl rand -hex 32
```
Prints a long random secret. Copy it: this is your **API token**.

```bash
nano /root/race-plan/deploy/.env
```
Opens the settings file. Paste the following, putting your token after `API_TOKEN=`, then save:

```
API_TOKEN=paste-the-token-here
API_PORT=7070
HTTP_PORT=70
HTTPS_PORT=773
TZ_NAME=Africa/Dar_es_Salaam
DOMAIN=plan.example.com
```

```bash
ufw allow 7070/tcp
```
Opens the API port in the firewall. Only needed if you use `ufw` and plain HTTP.

## 2. GitHub setup (once)

Push this folder to a GitHub repository (the default branch must be `main`). In the repository, go to **Settings → Secrets and variables → Actions** and add these secrets:

| Secret | Value |
|---|---|
| `SERVER_HOST` | `164.68.97.148` |
| `SERVER_USER` | The SSH user, for example `root` |
| `SERVER_SSH_KEY` | A private SSH key whose public key is in the server's `~/.ssh/authorized_keys` |
| `SERVER_PORT` | Optional, defaults to 22 |
| `DEBUG_KEYSTORE_BASE64` | Optional but recommended, see "Signing key" below |

Optional variables: `DEPLOY_DIR` (default `/root/race-plan`; set `/home/YOUR_USER/race-plan` if you don't deploy as root) and `USE_HTTPS` = `true` to also start Caddy with HTTPS on `DOMAIN:773`. Point the domain's DNS A record at the server first. Let's Encrypt only checks domains on port 80, so port 80 must reach Caddy's port 70 for the certificate: see the note in `deploy/Caddyfile`.

### Signing key (so updates install over the old app)

Run these on any computer with Java:

```bash
keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Race Plan,O=Personal,C=TZ"
```
Creates a signing key that never changes, so every new build installs over the previous one.

```bash
base64 -w0 debug.keystore
```
Prints the key as text. Paste that into the `DEBUG_KEYSTORE_BASE64` secret. Keep the file safe and don't commit it.

## 3. Deploy and build

Push to `main`. Two workflows run:

- **Backend — test and deploy** runs the API tests, builds the Docker image, copies `backend/` and `deploy/` to `/root/race-plan` on the server, restarts the containers and checks `/api/health`.
- **Build Android APK** analyzes and tests the Flutter code, builds a release APK and publishes it as a GitHub Release named "Race Plan build N".

Each workflow only runs when its own folder changes. Both can also be started by hand from the **Actions** tab ("Run workflow").

## 4. Install on your phone

1. On your phone, open the repository's **Releases** page and download the latest `race-plan-N.apk`.
2. Open it and allow "install unknown apps" for your browser when Android asks.
3. In the app, tap **Settings** and enter the server address (`http://164.68.97.148:7070`, or `https://your-domain:773` if you use HTTPS) and your API token. Tap **Test**, then **Save**.

Your plan downloads, and from then on everything syncs on its own.

---

## Check the server by hand

```bash
curl http://164.68.97.148:7070/api/health
```
Should print `{"status":"ok",...}`. No token is needed for this one.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://164.68.97.148:7070/api/dashboard
```
Shows the live dashboard numbers the app displays.

```bash
docker compose -f /root/race-plan/deploy/docker-compose.yml logs -f api
```
Follows the API logs on the server.

The database is backed up every 6 hours to `/root/race-plan/deploy/backups/` (the last 7 days are kept).

## API

All endpoints except `/api/health` need `Authorization: Bearer <API_TOKEN>`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness check |
| GET | `/api/sync` | Everything in one call: sessions with logs, habits, check-ins, dashboard |
| GET | `/api/dashboard` | Calculated progress: countdown, completion, streak, 7-day average weight, weekly totals, weekly decision, 5 km test projection |
| GET | `/api/reference` | Guide content (strength, swimming, nutrition, meal plan, fuelling, race plan, rules) |
| GET | `/api/sessions?week=N` or `?date=YYYY-MM-DD` | Sessions |
| PUT | `/api/sessions/{id}/log` | `{status: done|partial|skipped, actual, effort, duration_min, notes, updated_at}` |
| DELETE | `/api/sessions/{id}/log` | Clear a log |
| PUT | `/api/habits/{YYYY-MM-DD}` | Daily log: weight, resting_hr, sleep_hours, sleep_quality, soreness, pain, pain_where, energy, mood, motivation, nutrition, fast_tolerance, warning_signs, fast_kept, water, protein … |
| PUT | `/api/checkins/{week}` | Weekly check-in, weeks 0–14: waist, long_run_actual (min), swim_nonstop_actual (m), tt_5k_min, energy, notes |

Interactive docs are at `http://SERVER:7070/docs`.

## Changing the plan

1. Edit `scripts/plan_data.py` (sessions, weeks, run-walk ratios, swims) or `scripts/meals.py` (meal plan).
2. Regenerate the workbook and the JSON:

```bash
cd scripts
```
Moves into the scripts folder.

```bash
python build_workbook.py Half_Marathon_Plan_2027.xlsx
```
Rebuilds the Excel tracker.

```bash
cd ..
```
Goes back to the project folder.

```bash
python scripts/export_plan.py backend/data
```
Rewrites `plan.json` and `reference.json` for the server.

3. Commit and push. The server reloads the plan on restart and keeps your daily logs, check-ins, and the workout logs of sessions that are still on the same day and type.

## Run locally (optional)

```bash
cd backend
```
Moves into the API folder.

```bash
pip install -r requirements-dev.txt
```
Installs the API and test libraries.

```bash
python -m pytest -q
```
Runs the API tests.

```bash
API_TOKEN=dev DB_PATH=./dev.db uvicorn app.main:app --reload --port 7070
```
Starts the API on your computer at http://localhost:7070.

## Security notes

- Plain `http://` sends your token unencrypted. That's fine to get started, but switch to HTTPS (set `USE_HTTPS=true` with a domain, then use `https://your-domain:773` in the app) for everyday use. Then remove the `usesCleartextTraffic` line from `app/tool/setup_android.sh`.
- Change the token at any time by editing `.env` on the server, running `docker compose up -d` in `/root/race-plan/deploy`, and updating it in the app's Settings.
