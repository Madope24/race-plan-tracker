"""Single source of truth for the 2027 half-marathon plan: weeks, daily sessions and their full text.

Week 0 = Thu 29 Oct – Sun 1 Nov 2026 (start-up), weeks 1–14 = Mon 2 Nov 2026 – Sun 7 Feb 2027 (race).
Rules: Monday and Thursday are dry-fast days (walk + mobility after iftar only); runs are before 07:00;
swims are in the evening; a run and a swim are never on the same day.
"""
import datetime as dt

START = dt.date(2026, 10, 29)
WEEK1 = dt.date(2026, 11, 2)
RACE = dt.date(2027, 2, 7)

PHASES = {
    0: "Foundation", 1: "Foundation", 2: "Foundation", 3: "Foundation", 4: "Foundation",
    5: "Aerobic development", 6: "Aerobic development", 7: "Aerobic development", 8: "Aerobic development",
    9: "Race-specific endurance", 10: "Race-specific endurance", 11: "Race-specific endurance",
    12: "Peak", 13: "Taper", 14: "Race week",
}

# Run-walk ratio as (run minutes, walk minutes); None = continuous / race strategy
RATIO = {0: (1, 2), 1: (1, 2), 2: (1, 1), 3: (2, 1), 4: (2, 1), 5: (3, 1), 6: (4, 1), 7: (4, 1),
         8: (5, 1), 9: (5, 1), 10: (6, 1), 11: (6, 1), 12: (8, 1), 13: (8, 1), 14: (8, 1)}

# minutes: Tuesday, Friday, Saturday (long). TT = 5 km test session.
RUN = {
    0: (None, 30, 40), 1: (30, 30, 45), 2: (35, 30, 50), 3: (35, 35, 60), 4: (25, "TT", 45),
    5: (40, 35, 70), 6: (40, 40, 80), 7: (45, 40, 90), 8: (35, "TT", 70),
    9: (45, 45, 105), 10: (50, 45, 120), 11: ("TT", 40, 90), 12: (50, 45, 150), 13: (45, 40, 90),
    14: (30, 20, None),
}
TT_MIN = 50  # planned duration of a test session incl. warm-up and cool-down

FRIDAY_TYPE = {
    0: "easy", 1: "easy", 2: "easy", 3: "easy", 4: "test", 5: "strides4", 6: "strides6", 7: "hills_intro",
    8: "test", 9: "steady3x5", 10: "hills8", 11: "easy_strides", 12: "race3x8", 13: "race2x8", 14: "shakeout",
}

# Approximate average pace for distance estimates (min per km, run-walk included) – grows faster with fitness
EST_PACE = {0: 11.5, 1: 11.5, 2: 11.0, 3: 10.8, 4: 10.6, 5: 10.4, 6: 10.2, 7: 10.0, 8: 9.9, 9: 9.8,
            10: 9.6, 11: 9.5, 12: 9.4, 13: 9.3, 14: 9.2}

# Swims (optional): Wednesday repeats, Sunday technique + continuous. metres.
SWIM_WED = {
    0: None, 1: ("8 × 50 m", 50, 8, 40), 2: ("6 × 75 m", 75, 6, 40), 3: ("5 × 100 m", 100, 5, 40),
    4: ("4 × 100 m", 100, 4, 30), 5: ("4 × 150 m", 150, 4, 45), 6: ("3 × 200 m", 200, 3, 45),
    7: ("4 × 200 m", 200, 4, 40), 8: ("3 × 200 m", 200, 3, 40), 9: ("3 × 250 m", 250, 3, 45),
    10: ("2 × 400 m", 400, 2, 60), 11: ("3 × 250 m", 250, 3, 45), 12: ("2 × 400 m", 400, 2, 60),
    13: ("4 × 150 m", 150, 4, 40), 14: ("6 × 50 m easy", 50, 6, 30),
}
SWIM_SUN_CONT = {0: 100, 1: 100, 2: 125, 3: 150, 4: 200, 5: 250, 6: 300, 7: 350, 8: 400,
                 9: 450, 10: 500, 11: 600, 12: 600, 13: 700, 14: None}

WEEK_GOAL = {
    0: "Start the habit: first run-walks, first swim, learn the routines.",
    1: "Get the legs used to regular impact with short run intervals.",
    2: "Run 1 minute, walk 1 minute; long session to 50 minutes.",
    3: "Double the run intervals to 2 minutes; first 60-minute session.",
    4: "Easier week and the first 5 km test.",
    5: "Run 3 minutes at a time; first relaxed strides.",
    6: "Run 4 minutes at a time; long session to 80 minutes.",
    7: "Introduce hill walking and jogging; long session to 90 minutes.",
    8: "Easier week and the second 5 km test.",
    9: "First steady (moderate) running; long session over 100 minutes.",
    10: "Hill repeats for the 8 km climb; long session to 2 hours.",
    11: "Easier week and the deciding 5 km test.",
    12: "Longest session: 2 h 30 min at race rhythm, with race fuelling.",
    13: "Cut volume; keep a little race-effort running.",
    14: "Rest, travel, race.",
}
RECOVERY = {
    4: "Cutback week: about 15% less running, strength at 2 sets.",
    8: "Cutback week: strength at 2 sets; Christmas week is a good time for it.",
    11: "Cutback week: strength at 2 sets.",
    12: "Sleep 8+ hours around the long run; Sunday swim very easy.",
    13: "Strength once, light; no new foods or shoes.",
    14: "No strength after Tuesday; travel to Moshi by Friday.",
}


def week_of(d):
    if d < WEEK1:
        return 0
    return (d - WEEK1).days // 7 + 1


def fmt_ratio(r):
    return f"run {r[0]} min / walk {r[1]} min"


def mins(x):
    return TT_MIN if x == "TT" else (x or 0)


def week_summary(w):
    t, f, s = RUN[w]
    total = mins(t) + mins(f) + mins(s)
    longest = s or 0
    return total, longest


# ---------------- session text ----------------
RUN_WARM = ("Warm-up: 5 min brisk walk, then leg swings 10 per leg each way, walking lunges 8 per leg, "
            "ankle rocks 10 per side, 2 × 20 m easy skipping.")
RUN_COOL = ("Cool-down: 5 min easy walk, then calf stretch 45 s per leg, standing quad stretch 45 s per leg, "
            "hamstring stretch 45 s per leg, figure-four glute stretch 45 s per side.")
TALK_EASY = "Intensity: easy, RPE 3–4 out of 10. You can talk in full sentences. If you cannot, walk more."
MODIFY_RUN = ("If unusually tired, sore, dizzy or you slept under 6 hours: do the same time as brisk walking only, "
              "or swap for 20–30 min walking. Pain that changes your stride: stop and walk home.")
HEAT = "Start before 06:30. Carry water. On hot, humid mornings, slow down rather than speed up."


def run_session(w, day, minutes, kind):
    r = RATIO[w]
    if kind == "test":
        return ("5 km test", TT_MIN, "min", (
            "5 km test. Purpose: measure progress and choose your race plan (section 1 table). "
            f"{RUN_WARM} Then 5 min of your normal run-walk at easy effort. "
            "Test: 5 km on a flat, measured route (use a phone map or a known road). Use whatever run-walk mix gives your best "
            "time; start controlled and finish strongest. Effort RPE 7–8: only a few words possible. Record the time in the tracker. "
            f"{RUN_COOL} Total about 50–60 min. "
            "If unwell, very tired or in pain: postpone the test by a week and run an easy session instead. " + HEAT))
    if kind == "race_rehearsal":
        pass
    run_min, walk_min = r
    reps = max(1, round((minutes - 10) / (run_min + walk_min)))
    base = (f"Main: {fmt_ratio(r)}, repeated {reps} times (about {reps * (run_min + walk_min)} min). "
            f"{TALK_EASY} Running form: short quick steps, tall posture, relaxed shoulders.")
    extra = ""
    title = f"Run-walk {minutes} min"
    if kind == "strides4" or kind == "strides6" or kind == "easy_strides":
        n = 6 if kind == "strides6" else 4
        extra = (f" After the main set: {n} strides of 15–20 s (relaxed, quick, NOT a sprint, RPE 6), "
                 "each followed by 60–90 s walking.")
        title = f"Run-walk {minutes} min + {n} strides"
    elif kind == "hills_intro":
        extra = (" In the middle of the session, on a gentle slope (a road, bridge or ramp): 6 × 60 s brisk uphill walk "
                 "with strong arm swing (RPE 5–6), walk back down to recover. Purpose: prepare for the 8 km race climb.")
        title = f"Run-walk {minutes} min with hill walks"
    elif kind == "steady3x5":
        base = ("Main: 10 min easy run-walk, then 3 × 5 min steady running (RPE 5–6: short sentences only) with 2 min walking "
                "between, then easy run-walk to fill the time. Steady is a little faster than easy, never a race.")
        title = f"Steady run {minutes} min (3 × 5 min)"
    elif kind == "hills8":
        base = ("Main: 10 min easy run-walk to a gentle hill, then 8 × 60–90 s uphill: jog if you can at RPE 6, otherwise a "
                "powerful walk; walk down slowly to recover (2–3 min). Then easy run-walk home. Purpose: strength and "
                "confidence for the first 8 km of the race (290 m of climbing).")
        title = f"Hill repeats {minutes} min (8 × 60–90 s)"
    elif kind == "race3x8":
        base = ("Main: 10 min easy run-walk, then 3 × 8 min at planned race effort (RPE 5–6, using your race run-walk "
                "ratio) with 2 min easy walking between, then easy to finish. Practise the race drink and one date.")
        title = f"Race-effort run {minutes} min (3 × 8 min)"
    elif kind == "race2x8":
        base = ("Main: 10 min easy, then 2 × 8 min at race effort (RPE 5–6) with 2 min walking, then easy to finish.")
        title = f"Race-effort run {minutes} min (2 × 8 min)"
    elif kind == "shakeout":
        base = ("Main: 15 min very easy run-walk (RPE 2–3) plus 4 × 15 s relaxed strides. Legs should feel springy, "
                "not tired. Keep it short even if you feel great.")
        title = "Shake-out run 20 min"
    text = (f"Purpose: build aerobic endurance and impact tolerance. {RUN_WARM} {base}{extra} {RUN_COOL} "
            f"Total about {minutes} min. {MODIFY_RUN} {HEAT}")
    return title, minutes, "min", text


def long_session(w, minutes):
    r = RATIO[w]
    km = minutes / EST_PACE[w]
    if minutes >= 90:
        fuel = ("Fuel: water to thirst (carry 500–750 ml); from 45 min, 2 dates or half a banana every 25–30 min "
                "(about 30 g carbohydrate per hour), more in later weeks if your stomach copes. Weigh yourself before "
                "and after to learn your sweat loss.")
    elif minutes >= 60:
        fuel = "Fuel: water to thirst; carry 500 ml. Food during the session is optional at this length."
    else:
        fuel = "Fuel: water before and after is enough."
    hills = ""
    if w >= 9:
        hills = " Choose a route with some uphill in the first half, like the race; walk every steep part."
    if w == 12:
        hills += (" This is your race rehearsal: same breakfast, shoes, clothes, run-walk ratio and fuel as race day.")
    title = f"Long run-walk {minutes} min (≈ {km:.0f} km)"
    text = (f"Purpose: build the endurance to cover 21.1 km. Start at first light (about 05:45). {RUN_WARM} "
            f"Main: {fmt_ratio(r)} for {minutes} min, effort RPE 3–4 the whole way: the last 20 minutes should feel as easy "
            f"as the first. {fuel}{hills} {RUN_COOL} "
            "Progress next week only if you finished with no pain and felt recovered within 24 hours; otherwise repeat this "
            f"week's length. {MODIFY_RUN} {HEAT}")
    return title, minutes, "min", text


STRENGTH_A = ("Strength A — legs, hips and trunk (about 30 min). Warm-up 5 min: march on the spot 1 min, hip circles 10 each way, "
              "bodyweight squats 10, glute bridges 10, inchworms 5. Then: "
              "1) Sit-to-stand from a chair, progressing to bodyweight squat then backpack squat — {sets} × 8–12, rest 60–90 s. "
              "2) Glute bridge, progressing to single-leg bridge — {sets} × 10–12 (2-second squeeze at top). "
              "3) Step-ups on a safe 20–30 cm step, or reverse lunges holding a wall — {sets} × 8 per leg. "
              "4) Hip hinge: hands-on-hips good morning, progressing to single-leg Romanian deadlift with a hand on a wall, then holding the backpack — {sets} × 10 (per leg when single-leg). "
              "5) Calf raises on a step edge: both legs, progressing to single-leg; 3-second lowering — {sets} × 12–15. "
              "6) Bent-knee calf raise (soleus) — 2 × 15. "
              "7) Dead bug — {sets} × 8 per side; side plank — {sets} × 20–40 s per side. "
              "Finish: pelvic-floor block — glute bridge with a 5-second pelvic-floor squeeze, 10 reps. "
              "Effort: stop each set with 2–3 reps left (RPE 7). Never to failure. Cool-down: quad, hamstring and calf stretches 30–45 s each.")
STRENGTH_B = ("Strength B — upper body, feet and balance (about 25 min). Warm-up 5 min: arm circles 10 each way, cat-cow 8, "
              "bodyweight squats 10, single-leg stands 20 s per leg. Then: "
              "1) Push-up progression: wall → table (incline) → knees → full — {sets} × 8–12. "
              "2) Backpack bent-over row (5–10 kg of books or bottles) — {sets} × 10–12. "
              "3) Backpack overhead press, or pike push-up — {sets} × 8–10. "
              "4) Single-leg balance: 30 s per leg, then eyes closed, then on a folded towel — 3 rounds. "
              "5) Slow single-leg calf lowering (up on two legs, down on one over 3 s) — 2 × 10 per leg. "
              "6) Foot strength: towel scrunches 2 × 20 and tibialis raises (back to a wall, lift toes) 2 × 15. "
              "7) Bird dog — {sets} × 8 per side; front plank — {sets} × 20–45 s. "
              "Finish: pelvic-floor block — 10 slow squeezes held 5 s in a deep squat hold. "
              "Effort RPE 6–7; legs stay fresh for Friday and Saturday.")
STRENGTH_MOD = (" If sore or tired: do 1 set of each and skip anything that hurts. Pain above 3/10 that rises during a set: stop that exercise.")

SWIM_WARM = "Warm-up: 4 × 25 m easy (any stroke), 20–30 s rest at the wall."
SWIM_DRILLS = ("Drills: 4 × 25 m — side kick with one arm forward, catch-up freestyle, fingertip drag, six-kick switch "
               "(rest 20–30 s each). Breathe out steadily under water; roll to breathe.")
SWIM_COOL = "Cool-down: 50–100 m very easy backstroke or breaststroke, then shoulder and chest stretches 30 s each."
SWIM_MOD = " Optional session: skip it if the pool is unavailable or you feel run-down. Never swim alone where there is no lifeguard."


def swim_wed(w):
    spec = SWIM_WED[w]
    label, dist, reps, rest = spec
    total = 100 + 100 + dist * reps + 100
    text = (f"Purpose: low-impact aerobic fitness and relaxed breathing. {SWIM_WARM} {SWIM_DRILLS} "
            f"Main: {label} freestyle at easy-to-steady effort (RPE 4–5), {rest} s rest between. {SWIM_COOL} "
            f"Total about {total} m, 30–40 min.{SWIM_MOD}")
    return f"Swim — {label} repeats", total, "m", text


def swim_sun(w):
    c = SWIM_SUN_CONT[w]
    total = 100 + 100 + c + 4 * 50 + 100
    text = (f"Purpose: recovery from the long run and longer continuous swimming. {SWIM_WARM} {SWIM_DRILLS} "
            f"Main: {c} m continuous, very easy (RPE 3–4): stop and rest 20–30 s if you must, then finish the distance; "
            "record the longest distance you swam without stopping. Then 4 × 50 m relaxed with 30 s rest. "
            f"{SWIM_COOL} Total about {total} m.{SWIM_MOD}")
    return f"Swim — {c} m continuous (easy)", total, "m", text


FAST_EVENING = ("Dry-fast day: NO exercise while fasting. 18:50 break the fast (500 ml water, 3 dates, soup), 19:20 main meal. "
                "About 20:15: easy walk {walk} min (RPE 2, flat, conversational) then fast-day mobility 15 min: cat-cow 8, "
                "thread the needle 6 per side, 90/90 hip switches 10, couch stretch 45 s per side, calf stretch 45 s per leg, "
                "child's pose 60 s. Finish with 5 min slow breathing: in through the nose 4 s, out 6 s. "
                "Keep sipping water until bed. Skip the walk if you feel dizzy, have a headache or are very tired; do the "
                "mobility and breathing only.")


def build_sessions():
    """Return list of dict sessions for every day from START to RACE."""
    out = []
    d = START
    while d <= RACE:
        w = week_of(d)
        dow = d.weekday()
        day = d.strftime("%A")
        ph = PHASES[w]
        t, f, s = RUN[w]
        sets = 2 if w in (4, 8, 11, 13) else 3
        def add(slot, typ, title, planned, unit, text):
            out.append(dict(date=d.isoformat(), week=w, day=day, phase=ph, time_slot=slot, type=typ, title=title,
                            planned=float(planned), unit=unit, details=text))
        if dow in (0, 3):  # fast days
            walk = 20 if w < 5 else 30
            if w == 14 and dow == 3:
                walk = 20
            add("After iftar (about 20:15)", "Mobility", f"FAST DAY — Easy walk {walk} min + mobility",
                walk + 20, "min", FAST_EVENING.format(walk=walk))
        elif dow == 1:  # Tuesday
            if t == "TT":
                add("Morning", "Run", *run_session(w, day, TT_MIN, "test"))
            elif t:
                kind = "race_effort_short" if w == 14 else "easy"
                title, m, u, text = run_session(w, day, t, "easy")
                if w == 14:
                    title = "Run-walk 30 min + 4 × 1 min race effort"
                    text = text.replace("Main:", "Main: easy run-walk, with 4 × 1 min at race effort in the middle (2 min walk between). Base:")
                add("Morning", "Run", title, m, u, text)
            if w <= 13 or w == 14:
                if w == 14:
                    add("Evening", "Strength", "Strength B — light (upper body and balance only)", 20, "min",
                        STRENGTH_B.format(sets=1) + " Race week: one set each, upper body and balance only.")
                elif w in (0, 13):
                    pass
                else:
                    add("Evening", "Strength", "Strength B — upper body, feet, balance", 25, "min",
                        STRENGTH_B.format(sets=sets) + STRENGTH_MOD)
        elif dow == 2:  # Wednesday
            if w == 13:
                add("Afternoon", "Strength", "Strength A — light (2 sets)", 25, "min", STRENGTH_A.format(sets=2) + STRENGTH_MOD)
            elif w == 14:
                add("Any time", "Mobility", "Mobility 20 min (race week)", 20, "min",
                    "Race week: no leg strength. 20 min of the fast-day mobility routine plus the pre-run warm-up drills. Sleep early.")
            elif w >= 1:
                add("Afternoon", "Strength", "Strength A — legs, hips, trunk", 30, "min", STRENGTH_A.format(sets=sets) + STRENGTH_MOD)
            if SWIM_WED.get(w):
                add("Evening", "Swim", *swim_wed(w))
        elif dow == 4:  # Friday
            if f == "TT":
                add("Morning", "Run", *run_session(w, day, TT_MIN, "test"))
            elif f:
                add("Morning", "Run", *run_session(w, day, f, FRIDAY_TYPE[w]))
        elif dow == 5:  # Saturday
            if s:
                add("Morning", "Run", *long_session(w, s))
            elif w == 14:
                add("Any time", "Rest", "Rest + travel to Moshi", 0, "min",
                    "Day before the race: rest. 10–15 min easy walk to loosen up. Collect your race number. "
                    "Carbohydrate-rich, low-fibre meals (section 15). Lay out kit, set two alarms, bed by 21:00.")
        elif dow == 6:  # Sunday
            if d == RACE:
                add("Morning", "Run", "RACE — Kilimanjaro Half Marathon 21.1 km", 21.1, "km",
                    "Race day: start 07:00 at MoCU Gate, Sokoine Road, Moshi; cut-off 12:30. Follow the race plan in "
                    "section 15: breakfast at about 04:00, start slower than feels right, walk the steep parts of the "
                    "8 km climb, carbohydrate every 20–25 min, drink to thirst at every water point. Enjoy it.")
            elif SWIM_SUN_CONT.get(w) is not None:
                add("Evening", "Swim", *swim_sun(w))
                add("Any time", "Mobility", "Recovery walk + mobility", 30, "min",
                    "Recovery after the long run: 20 min easy walk plus 10 min of the fast-day mobility routine. "
                    "No extra training for calories.")
        d += dt.timedelta(days=1)
    for i, s in enumerate(out, 1):
        s["id"] = i
    return out


if __name__ == "__main__":
    ss = build_sessions()
    print(len(ss), "sessions")
    for w in range(15):
        tot, lon = week_summary(w)
        print(w, PHASES[w], tot, lon, round(lon / EST_PACE[w], 1) if lon else "-")
    from collections import defaultdict
    by = defaultdict(set)
    for s in ss:
        by[s["date"]].add(s["type"])
    print("run+swim clashes", [d for d, t in by.items() if {"Run", "Swim"} <= t])
    print("fast-day runs/swims/strength", [s["date"] for s in ss if s["day"] in ("Monday", "Thursday") and s["type"] in ("Run", "Swim", "Strength")])
