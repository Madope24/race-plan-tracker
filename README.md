# EnduraForge

A personal endurance, strength and performance coach: a Flutter Android app (offline first) plus a FastAPI and Postgres backend on your own server, with GitHub CI/CD.

It takes one athlete from the November 2026 baseline through a 10 km (5 Dec), the Kilimanjaro half marathon (7 Feb), HYROX (June), an Olympic tune-up (July) and an Ironman 70.3 (August). Strength stays a priority throughout, around Monday and Thursday dry fasts and Ramadan.

```
app/          Flutter app: Home, Training, Nutrition, Progress, Profile. Works offline, syncs when signed in.
server/       FastAPI API (/api/v1) and the plan engine (server/app/engine): races + settings -> full plan.
plan/         gen_plan.py writes the bundled default plan into the app (CI checks it is current).
deploy/       docker-compose.yml, deploy.sh (health + smoke tests + automatic rollback), backup.sh.
docs/         Product requirements, architecture, database, design system, API, coaching season, deploy guide.
.github/      ci (every PR), deploy (staging -> approval -> production), rollback, release (APK), codeql, dependabot.
docker-compose.yml   Local development stack.
```

## What it does
- **Plan engine:** a date-driven calendar built from your race calendar, fasting days, Ramadan, bike start and baseline. Move a race and the phases, tapers, recovery weeks and goals move with it.
- **Hard rules, tested:**
  - Runs are mornings only and swims evenings only, never both on one day.
  - Fasting days are walk and mobility only, and Ramadan days have one light session.
  - No cycling before the bike start.
  - Every strength session has a warm-up, a kegel finisher and a cool-down.
  - Progression is gradual.
- **Daily coach:**
  - Readiness from several signals (never from one number alone), and sessions that only ever get easier.
  - Persistent pain pauses progression and recommends an assessment.
  - Strength progression changes load or reps, never both.
  - A training-load warning and a streak.
- **Workouts:** step-by-step player with instructions, set logging (kg, reps, RPE), rest timer, pause, skip, finish and feedback. Missed sessions can be moved.
- **Libraries:** exercise library with equipment, difficulty, regressions and progressions; mobility library and routines; pelvic floor guide; all 8 HYROX stations with division standards and home substitutes; bike checklists.
- **Nutrition:** Tanzanian foods with prices, and cutting, fuelling, fasting-day and Ramadan meal plans with grams, macros, TZS cost and preparation. Also a weekly shopping list, smoothies, sports nutrition and a race-fuelling progression.
- **Supplements:** purpose, evidence, studied dose ranges, cautions and a daily intake log. No boosters.
- **Data:** Garmin Activities.csv import (seeded with your November history), progress charts, and CSV export. History is kept when plans change.

Start with [docs/user-guides/deploy.md](docs/user-guides/deploy.md). The coaching overview is in [docs/coaching/season.md](docs/coaching/season.md).
