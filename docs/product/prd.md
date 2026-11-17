# EnduraForge: product requirements

## Vision
A personal coach in a phone app for one athlete in Dar es Salaam: it prescribes every session (sets, reps, distances, paces, heart rate), explains it, records what was actually done, and adjusts the next days within safe limits. It covers strength (a priority), running, swimming, cycling, HYROX, mobility, pelvic floor, nutrition with Tanzanian foods, supplements, sleep and recovery, around a fasting schedule and a race calendar.

## Athlete and season (starting profile)
| | |
|---|---|
| Athlete | Male, 26, 162 cm, 87.5 kg at the start (27 Oct 2026); target 80 kg by 1 Jan 2027, 77 kg by the 70.3 |
| Baseline (Activities.csv, 3 to 7 Nov) | Runs 1.79 and 3.42 km at about 17:10 per km (walking included), average HR 133 to 154, max 184. Pool swims about 860 m, 3:00 per 100 m, SWOLF 33 to 34, 20 strokes a minute |
| Fasting | Dry fast Monday and Thursday until about 18:50; Ramadan (expected 8 Feb to 9 Mar 2027) |
| Rules from the athlete | Runs mornings only; swims evenings only; never a run and a swim on the same day; no breakfast; at most one smoothie a day and not every day; no whey, no testosterone-booster blends; exercises written out in full |
| Equipment | Pool, loaded backpack, jerrycans, water bottles, chair, bed; no stairs, no pull-up bar; bike from March |

| Race | Date | Goal |
|---|---|---|
| 10 km | Sat 5 Dec 2026 | Under 2 hours (1:45 is the spring goal; see coaching notes) |
| Kilimanjaro half marathon | Sun 7 Feb 2027 | Under 4 hours |
| HYROX (Men Open) | Sat 12 Jun 2027 (placeholder until booked) | Finish in 1 h 55 or less |
| Olympic triathlon (tune-up) | Sun 11 Jul 2027 | Finish in 3 h 45 or less |
| Ironman 70.3 | Sun 22 Aug 2027 (placeholder until booked) | Finish within 8 h 30 |
| 35 km run | Not set | After the 70.3, not before it |

## User stories
- As the athlete I open the app and start today's workout in two taps (Home > Start).
- I see each exercise with sets, reps, rest, how to do it, breathing, common mistakes, and easier and harder versions, without searching elsewhere.
- I log load, reps and effort for every set and see the suggested load for next time.
- I do a 30-second morning check-in (sleep, soreness, energy, stress, resting HR, HRV, pain) and the coach adjusts today only if several signs agree.
- After a session I answer: completed? how hard? any pain? energy? notes.
- I mark a day as fasting and demanding sessions become a walk and mobility.
- I move a missed session to another day, or skip it.
- I add, edit or remove races and the whole plan moves with them.
- I see today's meals with grams, calories, macros, cost in TZS and how to prepare them, tick what I ate, and get a weekly shopping list.
- I record the supplements I actually took and read the evidence, studied doses and cautions for each.
- I see running, swimming, cycling, strength, weight, consistency and recovery trends.
- Everything works offline; it syncs to my own server when I have a connection.

## Functional requirements
1. **Plan engine**: a daily, weekly and phase calendar generated from the race calendar, fasting days, Ramadan, bike start and baseline. Phases: Foundation (10 km), Endurance (half), Ramadan maintenance, Triathlon development, HYROX preparation, Olympic tune-up, Ironman 70.3 preparation. Taper and recovery weeks around races, an easier week every 4th build week.
2. **Hard rules**: runs AM, swims PM, never a run and a swim on one day; fasting days walk and mobility only; Ramadan one light session; no cycling before the bike start; kegel finisher, warm-up and cool-down in every strength session; progression limits (long run +1.5 to 2 km and at most +35% a week; swim +100 to 150 m).
3. **Strength**: specific exercises with sets, reps, rest, tempo, effort and progression rule; exercise library with every field in the brief; progression engine (one variable at a time).
4. **Running, swimming, cycling, HYROX** modules with targets, heart-rate guidance, hydration and fuelling, swim drills and tests, bike checklists, all 8 HYROX stations with division standards and home substitutes.
5. **Mobility and pelvic floor**: mobility library and routines (morning, pre-run, post-workout, recovery day, swimmer shoulders, cyclist hips); pelvic floor identification, slow, short and relaxation drills, breathing, progression levels and rules.
6. **Coach**: readiness from several signals, session adjustments that only reduce load, persistent-pain handling with referral, training-load warning, streak.
7. **Nutrition**: daily targets that follow training and fasting; four meal plans (cutting, fuelling, fasting day, Ramadan); per-meal grams, kcal, protein, carbs, fat, TZS and preparation; weekly shopping list; smoothies with honest calorie notes; sports-nutrition guide and a gut-training progression for the 70.3.
8. **Supplements**: purpose, evidence, studied dose range, timing, side effects, contraindications; daily intake log; no automatic high doses; hormonal-health guidance with no booster claims.
9. **Races**: event management (add, edit, remove) that regenerates the plan and the goals.
10. **Goals**: SMART goals and mini goals generated from the races and the plan, with live status.
11. **Data**: Garmin CSV import (missing values stay missing), CSV export of days and activities, history kept when plans change.

## Non-functional requirements
- Offline first: the phone keeps the plan, all instructions and every log; sync is background, last-write-wins per day, with a visible sync status.
- Safety-critical rules are deterministic and tested; AI can only phrase explanations.
- Privacy: data lives on the phone and the athlete's own server only. No third-party analytics.
- Performance: one plan download per change (ETag), no network calls to open a screen.
- Accessibility: large touch targets (48 dp+), high-contrast dark theme, optional light theme.
- Maintainability: modular monolith, versioned API (/api/v1), migrations, structured logs, CI on every change.

## Roadmap
| Release | Scope |
|---|---|
| 2.0 (this release) | Plan engine from race dates, coach, readiness, feedback, pain rules, progression, 5-tab app, nutrition with costs, supplements log, Garmin CSV import, staging and approved production deploys |
| 2.1 | Phone reminders (local notifications) using the saved preferences; exercise illustrations |
| 2.2 | Health Connect and Strava adapters on the server; automatic activity import |
| 2.3 | Weekly AI-written summary (optional provider), coach notes on the progress screen |
| Later | Multi-athlete coaching, web dashboard |
