"""Export the 2027 plan (plan_data.py + meals.py) into the JSON files the API seeds from.

Usage (from the repository root):
    python scripts/export_plan.py backend/data

Writes plan.json (sessions, weeks, settings) and reference.json (the in-app Guide).
"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meals as M  # noqa: E402
import plan_data as P  # noqa: E402

START_WEIGHT = 87.0
SLOW_LOSS, FAST_LOSS = 0.3, 0.5  # expected healthy range, kg per week


def weeks():
    out = []
    for w in range(16):
        if w == 0:
            date = P.START
        else:
            date = P.WEEK1 + dt.timedelta(weeks=w - 1)
        long_run = None
        if w <= 14:
            s = P.RUN[w][2]
            long_run = s if s else None
        out.append({
            "week": w,
            "label": "Final" if w == 15 else f"Week {w}",
            "date": date.isoformat(),
            "target_weight": round(START_WEIGHT - SLOW_LOSS * w, 1),
            "stretch_weight": round(START_WEIGHT - FAST_LOSS * w, 1),
            "planned_long_run": long_run,  # minutes
            "planned_swim": P.SWIM_SUN_CONT.get(w),
        })
    return out


def row(*pairs):
    return [{"label": k, "value": str(v)} for k, v in pairs if v not in (None, "")]


def guides():
    g = []
    # Strength
    a = [
        ("Sit-to-stand → squat", "3 × 8–12", "60–90 s", "Feet hip-width, knees over toes, chest up, sit back", "Chair → no chair → backpack → 3 s lowering"),
        ("Glute bridge", "3 × 10–12", "60 s", "Ribs down, push through heels, 2 s squeeze", "Two legs → single leg"),
        ("Step-up or reverse lunge", "3 × 8 per leg", "60–90 s", "Safe 20–30 cm step; no step: reverse lunge holding a wall", "Add the backpack"),
        ("Hip hinge", "3 × 10", "60 s", "Soft knees, flat back, hips back", "Good morning → single-leg RDL (hand on wall) → with backpack"),
        ("Calf raise", "3 × 12–15", "45–60 s", "Step edge, full range, 3 s down", "Two legs → single leg → with backpack"),
        ("Bent-knee calf raise", "2 × 15", "45 s", "Knees bent 30°", "Single leg"),
        ("Dead bug", "3 × 8 per side", "45 s", "Lower back pressed down", "Slower, straighter legs"),
        ("Side plank", "3 × 20–40 s per side", "45 s", "Straight line ear-hip-ankle", "Knees → feet → top-leg lift"),
        ("Pelvic-floor finisher", "1 × 10", "", "Glute bridge with 5 s pelvic-floor squeeze", "Hold 8 s"),
    ]
    b = [
        ("Push-up", "3 × 8–12", "60 s", "Body straight, elbows about 45°", "Wall → table → knees → full"),
        ("Backpack bent-over row", "3 × 10–12", "60 s", "Hinge, flat back, bag to lower ribs", "Heavier bag, 2 s squeeze"),
        ("Overhead press or pike push-up", "3 × 8–10", "60 s", "Ribs down, press straight up", "Heavier bag; feet raised"),
        ("Single-leg balance", "3 × 30 s per leg", "30 s", "Soft knee, hips level", "Eyes closed → folded towel"),
        ("Single-leg calf lowering", "2 × 10 per leg", "45 s", "Up on two legs, down on one over 3 s", "Add the backpack"),
        ("Towel scrunch + tibialis raise", "2 × 20 + 2 × 15", "30 s", "Scrunch a towel with the toes; back to a wall, lift the toes", "More reps, slower"),
        ("Bird dog", "3 × 8 per side", "45 s", "Hips level, reach long", "Hold 3 s"),
        ("Front plank", "3 × 20–45 s", "45 s", "Squeeze glutes, no sag", "Longer → shoulder taps"),
        ("Pelvic-floor finisher", "10 squeezes", "", "5 s squeeze in a deep squat hold", "Hold 8 s"),
    ]
    to_rows = lambda lst: [row(("Exercise", e), ("Sets × reps", s), ("Rest", r), ("How", h), ("Progression", p)) for e, s, r, h, p in lst]
    g.append({"id": "strength", "title": "Strength", "icon": "strength", "sections": [
        {"title": "Strength A — legs, hips, trunk (Wednesday, 30 min)", "rows": to_rows(a)},
        {"title": "Strength B — upper body, feet, balance (Tuesday evening, 25 min)", "rows": to_rows(b)},
        {"title": "Rules", "rows": [
            row(("Effort", "Stop each set with 2–3 reps left (RPE 7). Never to failure.")),
            row(("Progress", "One step up after hitting the top of the rep range at RPE 7 or easier in two sessions.")),
            row(("Cutback weeks", "Weeks 4, 8, 11: 2 sets. Week 13: Strength A only. Week 14: upper body only.")),
            row(("Normal soreness", "Dull, spread across a muscle, peaks 24–48 h later, eases as you warm up.")),
            row(("Warning signs", "Sharp or pinpoint pain, pain on a bone, swelling, limping, pain at night, pain lasting 3+ days.")),
            row(("Pain rule", "Up to 3/10 and stable: OK. Above 3 or rising: stop; 3 days walking and swimming only; physio if it lasts a week.")),
        ]},
    ]})
    # Swim
    swim_rows = []
    for w in range(15):
        wed = P.SWIM_WED.get(w)
        sun = P.SWIM_SUN_CONT.get(w)
        swim_rows.append(row(("Week", w), ("Wednesday", f"{wed[0]}, {wed[3]} s rest" if wed else "—"),
                             ("Sunday continuous", f"{sun} m, very easy" if sun is not None else "Race day")))
    g.append({"id": "swim", "title": "Swimming", "icon": "swim", "sections": [
        {"title": "Weekly progression (optional)", "rows": swim_rows},
        {"title": "Every swim", "rows": [
            row(("Warm-up", "4 × 25 m easy, 20–30 s rest")),
            row(("Drills", "4 × 25 m: side kick, catch-up freestyle, fingertip drag, six-kick switch")),
            row(("Cool-down", "50–100 m easy backstroke or breaststroke")),
            row(("Breathing", "Breathe out slowly under water; roll to breathe; every 2 or 3 strokes")),
            row(("Goal", "600–700 m continuous by race week; 1,500 m non-stop in March 2027")),
        ]},
    ]})
    # Nutrition
    tgt = [row(("Day", d), ("Calories", f"{t[0]:,} kcal"), ("Protein", f"{t[1]} g"), ("Carbs", f"{t[2]} g"), ("Fat", f"{t[3]} g"))
           for d, t in ((d, v["target"]) for d, v in M.DAYS.items())]
    g.append({"id": "nutrition", "title": "Nutrition", "icon": "nutrition", "sections": [
        {"title": "Targets by day (weeks 0–8)", "rows": tgt},
        {"title": "Adjust every 2 weeks (7-day average weight)", "rows": [
            row(("Lost more than 1.6 kg", "Add 200 kcal a day, mostly carbohydrate around runs")),
            row(("Lost 0.6–1.6 kg", "On track: change nothing")),
            row(("Lost under 0.6 kg, training good", "Remove 150 kcal a day from oil, sugar or snacks")),
            row(("Lost under 0.6 kg, tired", "Keep calories, fix sleep, reassess in 2 weeks")),
            row(("From week 9", "Add about 150 kcal on Tue and Fri, 250 kcal on Sat")),
        ]},
        {"title": "Dry-fast days (Mon, Thu)", "rows": [
            row(("04:15–04:45", "Suhoor + 600–800 ml water sipped through the meal")),
            row(("Daytime", "No training. Stay cool. 20-minute nap is fine")),
            row(("18:50", "500 ml water slowly, 3 dates, clear soup")),
            row(("19:20", "Main meal")),
            row(("20:15", "Easy walk 20–30 min, mobility 15 min, slow breathing 5 min")),
            row(("Until bed", "About 1.5–2 litres in total, 250 ml every 20–30 min")),
            row(("Warning signs", "Dizziness, fainting, confusion, racing heart, very dark or no urine: rest in shade and drink")),
        ]},
    ]})
    # Meals
    secs = []
    for dname, day in M.DAYS.items():
        rows_, tot = M.day_totals(day)
        r = [row(("Time", t), ("Meal", n), ("Foods", f), ("Estimate", f"{m[0]} kcal · P {m[1]} g · C {m[2]} g · F {m[3]} g"), ("Note", note))
             for t, n, f, m, note in rows_]
        r.append(row(("Total", f"{tot[0]:,} kcal · protein {tot[1]} g · carbs {tot[2]} g · fat {tot[3]} g")))
        secs.append({"title": dname, "rows": r})
    g.append({"id": "meals", "title": "Meal plan", "icon": "meals", "sections": secs})
    # Fuel
    g.append({"id": "fuel", "title": "Fuelling", "icon": "fuel", "sections": [
        {"title": "By session length", "rows": [
            row(("Under 60 min", "Banana + 300–400 ml water before; water to thirst")),
            row(("60–90 min", "Water to thirst (carry 500 ml); 1–2 dates if hot or after a fast day")),
            row(("Over 90 min", "From 30–45 min: 30 g carbohydrate per hour, building to 45–60 g by week 12")),
        ]},
        {"title": "Carbohydrate in foods", "rows": [
            row(("1 small date", "about 6 g")), row(("1 medium banana", "about 27 g")),
            row(("100 ml Coke", "about 10 g")), row(("Homemade drink 500 ml", "2 tbsp sugar or honey + pinch of salt + lime: about 25 g")),
        ]},
        {"title": "Hydration", "rows": [
            row(("Rule", "Drink to thirst. Gaining weight during a run means you drank too much.")),
            row(("Sweat rate", "Weigh before and after two long runs: 1 kg lost ≈ 1 litre")),
            row(("Stop and get help", "Dizziness, confusion, vomiting, chills in heat, throbbing headache with swollen hands, chest pain")),
        ]},
    ]})
    # Race
    D = 21.0975
    up, flat = 1.15, 1.0
    fd = (D - 8 * up - 2 * flat) / (D - 10)

    def t_at(km, p):
        t = min(km, 8) * up * p
        if km > 8:
            t += min(km - 8, 2) * flat * p
        if km > 10:
            t += (km - 10) * fd * p
        return t

    def hm(m):
        h, mm = int(m // 60), int(round(m % 60))
        if mm == 60:
            h, mm = h + 1, 0
        return f"{h}:{mm:02d}"
    def pace(minutes_per_km):
        s = round(minutes_per_km * 60)
        return f"{s // 60}:{s % 60:02d}"

    plan_rows = []
    for name, mins, cond in (("3:00", 180, "36 min or faster"), ("3:15", 195, "37–40 min"), ("3:30", 210, "41–43 min"),
                             ("3:45", 225, "44–47 min"), ("Finish strong 4:00", 240, "48 min or slower")):
        p = mins / D
        plan_rows.append(row(("Plan", name), ("Use if 5 km test", cond),
                             ("Checkpoints", " · ".join(f"{k} km {hm(t_at(k, p))}" for k in (5, 10, 15, 20))),
                             ("Paces", f"climb {pace(up * p)} · return {pace(fd * p)} per km")))
    g.append({"id": "race", "title": "Race plan", "icon": "race", "sections": [
        {"title": "Kilimanjaro Half Marathon — 7 Feb 2027", "rows": [
            row(("Start", "07:00, MoCU Gate, Sokoine Road, Moshi")), row(("Cut-off", "12:30")),
            row(("Course", "First 8 km climb about 290 m, about 2 km dirt road, then mostly downhill")),
            row(("Water", "About every 4 km; some points also serve Coke")),
        ]},
        {"title": "Pacing plans", "rows": plan_rows},
        {"title": "Race morning", "rows": [
            row(("03:45", "Wake, toilet, water")),
            row(("04:00", "Bread + honey + 1 tbsp peanut butter, 1 banana, sweet tea or uji (100–120 g carbohydrate)")),
            row(("06:30", "10 min easy walk, leg swings, ankle rocks")),
            row(("06:50", "Line up in the back half")),
            row(("During", "Run-walk from km 1; walk steep climbs; carbohydrate every 20–25 min; drink to thirst")),
        ]},
    ]})
    # Rules
    g.append({"id": "rules", "title": "Weekly rules", "icon": "rules", "sections": [
        {"title": "The Sunday decision", "rows": [
            row(("Green: progress", "≥ 85% done; runs at RPE ≤ 4; pain ≤ 2 and gone next day; sleep ≥ 6.5 h; energy and mood ≥ 3")),
            row(("Amber: repeat", "60–84% done; runs at RPE 5; pain 3 that settles in 24 h; sleep 6–6.4 h; energy or mood < 3")),
            row(("Red: step back", "Pain ≥ 4 or changing your stride; < 60% done; sleep < 6 h; illness; fast weight loss with fatigue")),
        ]},
        {"title": "Stop and get medical help", "rows": [
            row(("Heart", "Chest pain, fainting, racing or irregular heartbeat, unusual breathlessness")),
            row(("Bone", "Pinpoint bone pain, pain at rest or night, swelling: possible stress fracture")),
            row(("Heat or fluid", "Confusion, staggering, chills in heat, throbbing headache with swollen hands")),
            row(("Fast days", "Fainting, confusion, no urine for 8+ hours")),
        ]},
    ]})
    return g


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sessions = P.build_sessions()
    plan = {
        "start_date": P.START.isoformat(),
        "week1_date": P.WEEK1.isoformat(),
        "race_date": P.RACE.isoformat(),
        "start_weight": START_WEIGHT,
        "realistic_loss_per_week": SLOW_LOSS,
        "stretch_weight": round(START_WEIGHT - FAST_LOSS * 14, 1),
        "fast_days": ["Monday", "Thursday"],
        "fast_until": "18:50",
        "sessions": sessions,
        "weeks": weeks(),
    }
    (out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    ref = {"version": "2027-plan-" + dt.date.today().isoformat(), "guides": guides()}
    (out / "reference.json").write_text(json.dumps(ref, indent=1, ensure_ascii=False))
    print(f"sessions {len(sessions)}, weeks {len(plan['weeks'])}, guides {[x['id'] for x in ref['guides']]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "backend/data")
