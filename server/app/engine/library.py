# Exercise library: how to do every exercise in the plan. Fields: category, muscles, setup, how, breathing, mistakes, easier, harder
L = {}


def E(name, cat, mus, setup, how, breath, mistakes, easier, harder):
    L[name] = (cat, mus, setup, how, breath, mistakes, easier, harder)


# ---- legs
E(
    'Backpack goblet squat',
    'Legs',
    'Quads, glutes, core',
    'Feet shoulder-width, toes turned out slightly. Hug the loaded backpack high on your chest.',
    '1) Push the hips back and down between your heels. 2) Keep the chest up and knees tracking over the 2nd toe. 3) Go until the hip crease is below the knee. 4) Drive the floor away and stand tall, squeezing the glutes.',
    'Breathe in at the top, hold it on the way down, breathe out as you pass halfway up.',
    'Heels lifting; knees caving in; back rounding at the bottom.',
    'Bodyweight squat to a chair.',
    'Heavier backpack, or the pause squat.',
)
E(
    'Backpack pause squat',
    'Legs',
    'Quads, glutes',
    'Same as the goblet squat.',
    'Squat down in 3 s, hold the bottom position for a full 3 s without relaxing, then drive up fast.',
    'Hold the breath through the pause, exhale on the way up.',
    'Bouncing out of the bottom; relaxing in the pause.',
    'Shorter pause (1 s).',
    'Heavier backpack.',
)
E(
    'Backpack Bulgarian split squat',
    'Legs',
    'Quads, glutes, balance',
    'Stand about one big step in front of a chair or bed, rear foot laces-down on it, backpack hugged at the chest.',
    '1) Lower straight down until the back knee nearly touches the floor. 2) Front shin stays close to vertical. 3) Push through the front heel to stand. Finish all reps, then switch legs.',
    'In on the way down, out on the way up.',
    'Front knee collapsing inward; leaning far forward; front heel lifting.',
    'No backpack, hands on a wall.',
    'Heavier backpack, 3 s lowering.',
)
E(
    'Jerrycan Romanian deadlift',
    'Legs',
    'Hamstrings, glutes, lower back',
    'Feet hip-width, a jerrycan in each hand (or one held with both hands) in front of the thighs, knees soft.',
    '1) Push the hips back like closing a door with your bum. 2) Slide the jerrycan down the front of the legs to mid-shin, back flat. 3) Feel the hamstrings stretch. 4) Squeeze the glutes to stand.',
    'In on the way down, out on the way up.',
    'Rounding the back; bending the knees into a squat; letting the jerrycan drift away from the legs.',
    'Lighter jerrycan, shorter range.',
    'Fuller jerrycans, 3 s lowering.',
)
E(
    'Single-leg Romanian deadlift',
    'Legs',
    'Hamstrings, glutes, balance',
    'Stand on one leg, jerrycan in the opposite hand, knee soft.',
    'Hinge forward on the standing leg while the free leg reaches straight back, until your body is nearly parallel to the floor. Hips stay square to the floor. Return by squeezing the standing glute.',
    'In on the way down, out on the way up.',
    'Hips twisting open; rounding the back.',
    'Touch the back toe on the floor for balance.',
    'Heavier jerrycan, pause at the bottom.',
)
E(
    'Reverse lunge',
    'Legs',
    'Quads, glutes',
    'Stand tall, feet hip-width.',
    'Step one foot back about 60 to 90 cm, lower until both knees are at about 90 degrees, back knee just above the floor. Push through the front heel to return. Alternate legs.',
    'In on the way down, out on the way up.',
    'Front knee shooting past the toes; leaning forward.',
    'Hold a wall.',
    'Backpack on your back.',
)
E(
    'Backpack reverse lunge',
    'Legs',
    'Quads, glutes',
    'Backpack on both shoulders, straps tight.',
    'As the reverse lunge, with the load.',
    'In down, out up.',
    'As above.',
    'No backpack.',
    'Heavier backpack.',
)
E(
    'Backpack walking lunge',
    'Legs / Hyrox',
    'Quads, glutes, endurance',
    'Backpack on both shoulders, clear 10 m of floor or yard.',
    'Step forward into a lunge, back knee lightly touches (or nearly touches) the floor, drive up and step straight into the next lunge with the other leg. This is the Hyrox sandbag-lunge pattern.',
    'Steady breathing, one breath per step.',
    'Short choppy steps; torso falling forward.',
    'Lunge in place.',
    'Heavier backpack, longer distance.',
)
E(
    'Glute bridge',
    'Legs',
    'Glutes, hamstrings',
    'Lie on your back, knees bent, feet flat, hip-width, heels 20 cm from the bum.',
    'Press through the heels and lift the hips until knees, hips and shoulders are in a line. Squeeze the glutes 2 s at the top. Lower slowly.',
    'Out on the way up.',
    'Arching the lower back instead of using glutes; pushing through the toes.',
    'Smaller range.',
    'Single leg.',
)
E(
    'Single-leg glute bridge',
    'Legs',
    'Glutes, hamstrings',
    'As the glute bridge, one leg straight in the air.',
    'Lift the hips with the working leg only, keep the pelvis level.',
    'Out on the way up.',
    'Hips dropping on one side.',
    'Two legs.',
    'Shoulders on a bed (hip thrust).',
)
E(
    'Backpack hip thrust',
    'Legs',
    'Glutes',
    'Upper back on the edge of a bed or sofa, backpack across the hips (hold it), feet flat.',
    'Drive the hips up until the body is flat like a table, chin tucked, squeeze 2 s, lower under control.',
    'Out on the way up.',
    'Overarching the back; feet too far away.',
    'No backpack.',
    'Single leg, heavier bag.',
)
E(
    'Calf raise on a step',
    'Legs',
    'Calves, Achilles',
    'Balls of the feet on a step, door threshold or thick book, heels hanging off, hand on a wall.',
    'Rise as high as possible, pause 1 s, lower slowly until the heels are below the step.',
    'Normal breathing.',
    'Bouncing; partial range.',
    'Flat floor.',
    'Single leg.',
)
E(
    'Single-leg calf raise',
    'Legs',
    'Calves, Achilles (runner insurance)',
    'As above on one foot.',
    'Full range, 2 s up, 2 s down.',
    'Normal breathing.',
    'Bouncing.',
    'Both feet.',
    'Hold a jerrycan.',
)
E(
    'Wall sit',
    'Legs / Hyrox',
    'Quads endurance',
    'Back flat on a wall, feet 60 cm out.',
    'Slide down until the thighs are parallel to the floor, knees over ankles. Hold.',
    'Slow nasal breathing.',
    'Hips above the knees; hands pushing on the thighs.',
    'Higher position.',
    'Backpack on the lap.',
)

# ---- core
E(
    'Dead bug',
    'Core',
    'Deep abs',
    'Lie on your back, arms straight up, knees bent at 90 degrees above the hips.',
    'Press the lower back into the floor. Slowly lower the opposite arm and leg towards the floor, return, switch sides. The lower back never lifts.',
    'Breathe out as the limbs lower.',
    'Lower back arching off the floor; moving fast.',
    'Move only the legs.',
    'Hold a water bottle in each hand.',
)
E(
    'Front plank',
    'Core',
    'Abs, shoulders, glutes',
    'Forearms on the floor under the shoulders, legs straight, toes tucked.',
    'Squeeze glutes and thighs, pull the ribs down, hold a straight line from head to heels.',
    'Short steady breaths.',
    'Hips sagging or piking.',
    'Knees down.',
    'Lift one foot, or shoulder taps from a high plank.',
)
E(
    'Side plank',
    'Core',
    'Obliques, hips',
    'Lie on one side, forearm under the shoulder, feet stacked.',
    'Lift the hips so the body is straight. Hold, then switch sides (time is per side).',
    'Steady breathing.',
    'Hips sagging.',
    'Bottom knee down.',
    'Lift the top leg.',
)
E(
    'Bird dog',
    'Core',
    'Deep core, back',
    'Hands under shoulders, knees under hips.',
    'Reach one arm forward and the opposite leg back until level. Hold 2 s, return, switch. Hips stay level (imagine a cup of chai on your back).',
    'Out as you reach.',
    'Hips rotating; arching the back.',
    'Move the leg only.',
    '3 s hold.',
)
E(
    'Hollow hold',
    'Core',
    'Abs',
    'Lie on your back, arms overhead.',
    'Press the lower back down, lift shoulders and legs a few cm off the floor into a banana shape. Hold.',
    'Short breaths, ribs down.',
    'Lower back lifting.',
    'Knees bent, arms by the sides.',
    'Arms and legs lower.',
)

# ---- upper body
E(
    'Incline push-up',
    'Upper body',
    'Chest, shoulders, triceps',
    'Hands slightly wider than shoulders on a bed, table or wall, body straight.',
    'Lower the chest to the edge in 3 s, elbows at about 45 degrees from the body, press back up to straight arms.',
    'In down, out up.',
    'Hips sagging; elbows flaring wide.',
    'Higher surface (wall).',
    'Lower surface, then the floor.',
)
E(
    'Push-up',
    'Upper body',
    'Chest, shoulders, triceps, core',
    'Hands under the shoulders on the floor, body in a straight line.',
    'Lower until the chest is a fist from the floor, elbows 45 degrees, press back to straight arms. Squeeze glutes the whole time.',
    'In down, out up.',
    'Head dropping; hips sagging; half reps.',
    'Incline push-up.',
    'Feet elevated, or backpack on.',
)
E(
    'Feet-elevated push-up',
    'Upper body',
    'Upper chest, shoulders',
    'Feet on a chair, hands on the floor.',
    'As a push-up.',
    'In down, out up.',
    'Hips piking up.',
    'Floor push-up.',
    'Backpack on.',
)
E(
    'Backpack bent-over row',
    'Upper body',
    'Upper back, lats, biceps',
    'Hold the backpack by the top handle or both straps, hinge forward to about 45 degrees, flat back, knees soft.',
    'Pull the bag to your belly button, squeezing the shoulder blades together, lower in 2 s.',
    'Out as you pull.',
    'Shrugging; jerking with the back.',
    'Lighter bag.',
    'Heavier bag, pause at the top.',
)
E(
    'Single-arm jerrycan row',
    'Upper body',
    'Lats, upper back, grip',
    'One hand and knee on a chair or bed, back flat, jerrycan in the other hand.',
    'Pull the jerrycan up to the hip (elbow travels towards the back pocket), squeeze 1 s, lower until the arm is straight. This is your pull-up substitute.',
    'Out as you pull.',
    'Twisting the torso; pulling to the chest.',
    'Less water.',
    'More water, 3 s lowering.',
)
E(
    'Pike push-up',
    'Upper body',
    'Shoulders, triceps',
    'Hands on the floor, hips high so the body makes an upside-down V.',
    'Bend the elbows and lower the top of the head towards the floor between the hands, then press back up.',
    'In down, out up.',
    'Elbows flaring out sideways.',
    'Hands on a bed.',
    'Feet on a chair.',
)
E(
    'Backpack overhead press',
    'Upper body',
    'Shoulders, triceps, core',
    'Stand tall, backpack held at chest level by the sides or straps.',
    'Press it straight overhead, biceps by the ears, then lower to the chest. Ribs down, glutes tight.',
    'Out on the press.',
    'Leaning back.',
    'Lighter bag.',
    'Heavier bag.',
)
E(
    'Feet-elevated pike push-up',
    'Upper body',
    'Shoulders',
    'Feet on a chair, hands on the floor, hips stacked high.',
    'As the pike push-up.',
    'In down, out up.',
    'Neck craning.',
    'Floor pike push-up.',
    'Slower lowering.',
)
E(
    'Chair dip',
    'Upper body',
    'Triceps, chest',
    'Hands on the edge of a sturdy chair behind you, fingers forward.',
    'Lower until the upper arms are parallel to the floor, shoulders down away from the ears, press back up.',
    'In down, out up.',
    'Shoulders rolling forward; going too deep.',
    'Knees bent.',
    'Feet on a second chair.',
)
E(
    'Jerrycan biceps curl',
    'Upper body',
    'Biceps, forearms',
    'Stand tall, jerrycan handle in one hand (or two smaller ones).',
    'Curl up with the elbow pinned to your side, lower in 3 s.',
    'Out as you curl.',
    'Swinging the body.',
    'Less water.',
    'More water.',
)
E(
    'Prone Y-T-W raise',
    'Upper body',
    'Rear shoulders, upper back',
    'Lie face down on a mat or khanga, forehead on a towel.',
    'Lift both arms into a Y (overhead), then T (out to the side), then W (elbows bent, squeeze the shoulder blades). Thumbs up. 2 s hold each.',
    'Steady breathing.',
    'Lifting the head; shrugging.',
    'Fewer reps.',
    'Hold small water bottles.',
)

# ---- Hyrox / conditioning
E(
    'Backpack thruster',
    'Hyrox',
    'Legs, shoulders, lungs',
    'Backpack held at the chest by the sides, feet shoulder-width.',
    'Squat down, then drive up hard and use that momentum to press the bag overhead in one movement. Lower to the chest as you go into the next squat. This is the wall-ball pattern.',
    'Out on the drive up.',
    'Pressing with the arms only; half squats.',
    'Lighter bag.',
    'Heavier bag.',
)
E(
    'Burpee',
    'Hyrox',
    'Full body',
    'Stand with feet hip-width.',
    'Squat, hands down, jump or step back to a plank, chest to the floor, push up, feet back in, stand and jump.',
    'Out as you push up.',
    'Hips sagging; landing loudly.',
    'Step back instead of jumping.',
    'Burpee broad jump.',
)
E(
    'Burpee broad jump',
    'Hyrox',
    'Full body, power',
    'Clear floor or yard in front.',
    'Do a burpee, then jump forward as far as you can, land softly, go straight into the next burpee.',
    'Rhythm: one breath per movement.',
    'Over-reaching the jump and losing rhythm.',
    'Step-back burpee + small jump.',
    'Faster pace.',
)
E(
    'Farmer carry',
    'Hyrox',
    'Grip, traps, core',
    'A full jerrycan in each hand, stand tall.',
    'Walk with short quick steps, shoulders back and down, ribs down. Walk a loop of your compound or march in place if space is short.',
    'Steady breathing.',
    'Leaning to one side; shrugging.',
    'Lighter cans.',
    'Fuller cans, longer distance.',
)
E(
    'Bear crawl',
    'Hyrox',
    'Shoulders, quads, core',
    'Hands under the shoulders, knees under the hips, knees hovering 2 cm off the floor.',
    'Crawl forward moving the opposite hand and foot together, back flat. Turn and crawl back. Replaces the sled push.',
    'Steady breathing.',
    'Hips high in the air.',
    'Bear plank hold.',
    'Backpack on your back.',
)
E(
    'Jerrycan swing',
    'Hyrox',
    'Glutes, hamstrings, lats',
    'Jerrycan held by the handle with both hands, feet wider than the hips.',
    'Hinge and swing it back between the legs, then snap the hips forward so it floats to chest height. Arms are ropes; the hips do the work. Replaces the SkiErg.',
    'Sharp breath out at the top.',
    'Squatting it up; lifting with the arms.',
    'Less water.',
    'More water.',
)
E(
    'Squat thrust',
    'Hyrox',
    'Full body',
    'Stand tall.',
    'Squat, hands down, jump the feet back to plank, jump them back in, stand.',
    'Out as you stand.',
    'Sagging plank.',
    'Step back.',
    'Faster.',
)


# ---- added: hamstrings, shoulders, arms
E(
    'Hamstring walkout',
    'Legs',
    'Hamstrings',
    'Lie on your back in a bridge position, heels on the floor, hips lifted.',
    'Keeping the hips up, walk the heels out in small steps until the legs are nearly straight, then walk them back in. That is 1 rep.',
    'Steady breathing.',
    'Hips dropping to the floor.',
    'Smaller steps, shorter range.',
    'Single leg.',
)
E(
    'Nordic hamstring lower',
    'Legs',
    'Hamstrings (best exercise for preventing hamstring tears in runners)',
    'Kneel on a folded towel, heels hooked under a heavy bed or held by a partner.',
    'Keep a straight line from knees to head and lower your body forward as slowly as you can. Catch yourself with your hands, then push back up to the start.',
    'Breathe out slowly as you lower.',
    'Bending at the hips; dropping fast.',
    'Lower only halfway, then catch.',
    'Lower slower, 5 s or more.',
)
E(
    'Backpack good morning',
    'Legs',
    'Hamstrings, glutes, lower back',
    'Backpack on both shoulders, feet hip-width, knees soft.',
    'Push the hips back and bow forward with a flat back until you feel the hamstrings stretch (about chest parallel to the floor), then squeeze the glutes to stand.',
    'In on the way down, out on the way up.',
    'Rounding the back; bending the knees into a squat.',
    'No backpack.',
    'Heavier backpack, 3 s lowering.',
)
E(
    'Water-bottle lateral raise',
    'Upper body',
    'Side shoulders (shoulder width)',
    'Stand tall, a full 1.5 L water bottle in each hand at your sides.',
    'Raise the arms out to the sides to shoulder height, elbows slightly bent, pinkies slightly up. Lower in 3 s.',
    'Out on the way up.',
    'Swinging; shrugging the shoulders up to the ears.',
    'Smaller bottles.',
    'Fuller bottles or a 2-s pause at the top.',
)
E(
    'Jerrycan hammer curl',
    'Upper body',
    'Biceps, forearms',
    'Stand tall, jerrycan handle gripped with the thumb pointing up (or a bottle in each hand).',
    'Curl up with the elbow pinned to your side and the palm facing in, lower in 3 s.',
    'Out as you curl.',
    'Swinging the body.',
    'Less water.',
    'More water.',
)
E(
    'Diamond push-up',
    'Upper body',
    'Triceps, inner chest',
    'Hands together under the chest, thumbs and index fingers forming a diamond.',
    'Lower the chest to your hands with the elbows brushing the ribs, press back up to straight arms.',
    'In down, out up.',
    'Elbows flaring; hips sagging.',
    'On the knees, or hands on a bed.',
    '2-s pause at the bottom.',
)

# ---- kegel exercises
E(
    'Kegel glute bridge',
    'Pelvic floor',
    'Pelvic floor, glutes',
    'Lie on your back, knees bent, feet flat.',
    'Lift the pelvic floor (as if stopping wind and urine), then lift the hips. Hold 3 s at the top, lower, and relax the pelvic floor fully.',
    'Breathe out as you lift.',
    'Holding the breath; clenching the buttocks instead of the pelvic floor.',
    'Smaller lift.',
    'Single leg.',
)
E(
    'Bridge march with kegel',
    'Pelvic floor',
    'Pelvic floor, glutes, core',
    'Hold a glute bridge.',
    'Keep a gentle pelvic-floor lift and march: lift one foot a few cm, put it down, switch. Hips stay level.',
    'Keep breathing normally.',
    'Hips dropping.',
    'Lower bridge.',
    'Pause 2 s on each lift.',
)
E(
    'Child pose belly breathing',
    'Pelvic floor',
    'Pelvic floor relaxation',
    'Kneel, sit back on your heels, arms forward, forehead down.',
    'Breathe slowly into the belly and lower back. On each breath in, let the pelvic floor drop and relax.',
    'This drill is the breathing.',
    'Squeezing instead of relaxing.',
    '',
    '',
)
E(
    'Deep squat kegel pulses',
    'Pelvic floor',
    'Pelvic floor, hips',
    'Sit in a deep squat, heels down (hold a door frame if needed).',
    'Squeeze the pelvic floor for 5 s, then fully relax for 5 s.',
    'Keep breathing.',
    'Holding the breath.',
    'Squat onto a low stool.',
    'Longer holds.',
)
E(
    'Wall sit with kegel',
    'Pelvic floor',
    'Pelvic floor, quads',
    'Back flat on a wall, thighs parallel to the floor.',
    'Hold the wall sit with a gentle 50% pelvic-floor lift, then relax the floor before standing.',
    'Normal breathing throughout.',
    'Clenching everything.',
    'Higher wall sit.',
    'Longer hold.',
)
E(
    'Diaphragm breathing',
    'Pelvic floor',
    'Diaphragm, pelvic floor',
    'Lie on your back, knees bent, one hand on the belly.',
    'Breathe in through the nose: belly rises, pelvic floor relaxes. Breathe out slowly: pelvic floor lifts gently.',
    'This drill is the breathing.',
    'Forcing the breath.',
    '',
    'Do it seated, then standing.',
)
E(
    'Dead bug with kegel',
    'Pelvic floor',
    'Pelvic floor, deep abs',
    'Dead bug start position.',
    'Lift the pelvic floor as the opposite arm and leg lower; release as they return.',
    'Out as the limbs lower.',
    'Lower back arching.',
    'Legs only.',
    'Slower.',
)
E(
    'Bird dog with kegel',
    'Pelvic floor',
    'Pelvic floor, core',
    'Hands under shoulders, knees under hips.',
    'Lift the pelvic floor and reach the opposite arm and leg; hold 3 s; return and relax.',
    'Out as you reach.',
    'Hips rotating.',
    'Leg only.',
    'Longer hold.',
)
E(
    'Happy baby breathing',
    'Pelvic floor',
    'Pelvic floor relaxation, hips',
    'Lie on your back, knees to the armpits, hold the outside of your feet.',
    'Rock gently and breathe slowly, letting the pelvic floor relax completely on each breath in.',
    'This drill is the breathing.',
    'Tensing the shoulders.',
    'Hold behind the knees.',
    '',
)
E(
    'Split-squat hold with kegel',
    'Pelvic floor',
    'Pelvic floor, legs',
    'Split stance, lower into the bottom of a lunge.',
    'Hold the bottom position: squeeze the pelvic floor 5 s, relax 5 s.',
    'Keep breathing.',
    'Front knee collapsing in.',
    'Higher position.',
    'Hold a backpack.',
)
E(
    'Side-lying clam with kegel',
    'Pelvic floor',
    'Pelvic floor, outer hips',
    'Lie on your side, knees bent, feet together.',
    'Lift the pelvic floor as you open the top knee, keeping the feet together; close and relax.',
    'Out as the knee opens.',
    'Rolling the hips back.',
    'Smaller opening.',
    '2-s hold at the top.',
)
E(
    'Elevator kegel in tall kneeling',
    'Pelvic floor',
    'Pelvic floor control',
    'Kneel upright, hips over knees.',
    'Lift the pelvic floor in 3 stages like a lift going up floors, holding 2 s at each. Lower stage by stage, then relax fully.',
    'Breathe at each stage.',
    'Squeezing the glutes or abs.',
    'Two stages.',
    'Five stages.',
)

# ---- warm-ups and cool-downs (named stretches with time / reps)
WARMUPS = [
    (
        'W-RUN',
        'Before every run (8 min)',
        [
            ('Brisk walk', '3 min'),
            ('Leg swings front to back', '10 each leg'),
            ('Leg swings side to side', '10 each leg'),
            ('Walking lunge with a twist', '6 each leg'),
            ('Ankle bounces (pogo)', '20'),
            ('A-skips', '2 x 15 m'),
            ('High knees', '2 x 15 m'),
            ('Butt kicks', '2 x 15 m'),
        ],
    ),
    (
        'W-SWIM',
        'Before every swim, on the pool deck (6 min)',
        [
            ('Arm circles forward and back', '10 each way'),
            ('Towel shoulder pass-through (hold a towel wide, take it over the head and back)', '10'),
            ('Doorway or wall chest stretch', '30 s each side'),
            ('Thoracic rotation (side-lying open book)', '6 each side'),
            ('Streamline reach: stand tall, arms overhead, one hand on the other', '5 x 5 s'),
            ('Bodyweight squats', '10'),
        ],
    ),
    (
        'W-STR',
        'Before every strength or Hyrox session (6 min)',
        [
            ('Cat-cow', '8 slow reps'),
            ("World's greatest stretch", '3 each side'),
            ('Hip 90/90 switches', '6 each side'),
            ('Bodyweight squat', '10'),
            ('Glute bridge', '10'),
            ('Inchworm', '5'),
            ('Scapular push-up', '10'),
            ('First exercise, light', '1 set of 8'),
        ],
    ),
    (
        'W-BIKE',
        'Before every ride (5 min, then 10 min easy spinning)',
        [('Half-kneeling hip flexor stretch', '30 s each side'), ('Leg swings front to back', '10 each leg'), ('Bodyweight squat', '10'), ('Cat-cow', '8')],
    ),
    (
        'C-STR',
        'Cool-down after every strength session (5 min)',
        [
            ('Child pose', '45 s'),
            ('Lying hamstring stretch with a towel around the foot', '45 s each leg'),
            ('Half-kneeling hip flexor stretch', '30 s each side'),
            ('Standing quad stretch', '30 s each side'),
            ('Doorway chest and shoulder stretch', '30 s each side'),
            ('Cross-body shoulder stretch', '30 s each arm'),
            ('Overhead triceps stretch', '30 s each arm'),
        ],
    ),
    (
        'C-RUN',
        'After runs, rides and bricks (5 min)',
        [
            ('Standing calf stretch on a wall', '30 s each side'),
            ('Standing hamstring stretch (foot on a step)', '30 s each side'),
            ('Standing quad stretch', '30 s each side'),
            ('Half-kneeling hip flexor stretch', '30 s each side'),
            ('Figure-4 glute stretch, lying', '30 s each side'),
        ],
    ),
    (
        'M-FLOW',
        'Recovery-day mobility (20 min): fasting days, rest days and the day before a race',
        [
            ('Cat-cow', '1 min'),
            ('Child pose with side reach', '1 min'),
            ('Half-kneeling hip flexor stretch', '1 min each side'),
            ('Couch stretch (back foot up a wall)', '1 min each side'),
            ('Hip 90/90 hold', '1 min each side'),
            ('Pigeon stretch', '1 min each side'),
            ('Thoracic open book', '8 each side'),
            ('Doorway chest stretch', '1 min'),
            ('Ankle rocks (knee to wall)', '10 each side'),
            ('Deep squat hold', '1 to 2 min'),
            ('Legs up the wall', '3 min'),
        ],
    ),
    (
        'AM-MOB',
        'Morning mobility (7 min, any day, before work)',
        [
            ('Cat-cow', '8 slow reps'),
            ('Thoracic open book', '6 each side'),
            ('Half-kneeling hip flexor stretch', '30 s each side'),
            ('Ankle rocks (knee to wall)', '10 each side'),
            ('Deep squat hold', '1 min'),
            ('Arm circles forward and back', '10 each way'),
        ],
    ),
    (
        'C-SWIM',
        'After the swim: shoulders (4 min)',
        [
            ('Cross-body shoulder stretch', '30 s each arm'),
            ('Doorway chest stretch', '30 s each side'),
            ('Overhead triceps stretch', '30 s each arm'),
            ('Sleeper stretch (lying on your side)', '30 s each side'),
        ],
    ),
    (
        'C-BIKE',
        'After the ride: hips and lower back (5 min)',
        [
            ('Half-kneeling hip flexor stretch', '45 s each side'),
            ('Figure-4 glute stretch, lying', '45 s each side'),
            ('Child pose', '45 s'),
            ('Knees-to-chest rock', '30 s'),
            ('Supine spinal twist', '30 s each side'),
        ],
    ),
]


# ---- added for the EnduraForge exercise library: the remaining exercises from the brief (home versions)
E(
    'Bodyweight squat',
    'Legs',
    'Quads, glutes',
    'Feet shoulder-width, toes turned out slightly, arms forward for balance.',
    '1) Sit the hips back and down. 2) Knees follow the toes. 3) Go as low as you can with heels down and chest up. 4) Stand, squeezing the glutes.',
    'In on the way down, out on the way up.',
    'Heels lifting; knees caving in; rounding the back.',
    'Squat to a chair.',
    'Backpack goblet squat.',
)
E(
    'Walking lunge',
    'Legs',
    'Quads, glutes, balance',
    'Clear 10 m of floor or yard, hands on the hips.',
    'Step forward, lower until the back knee nearly touches the floor, drive up and step straight into the next lunge with the other leg.',
    'One breath per step.',
    'Short choppy steps; front knee caving in.',
    'Lunge in place holding a wall.',
    'Backpack walking lunge.',
)
E(
    'Towel hamstring curl',
    'Legs',
    'Hamstrings',
    'Lie on your back on a tiled floor, heels on a towel (or socks), knees bent, hips lifted in a bridge.',
    'Keep the hips up and slide the heels away until the legs are nearly straight, then pull them back in with the hamstrings. That is the home version of the machine hamstring curl.',
    'Out as you pull the heels in.',
    'Hips dropping; going too fast on the way out.',
    'Only slide out (lower the hips to come back).',
    'Single leg.',
)
E(
    'Step-up',
    'Legs',
    'Quads, glutes, balance',
    'A sturdy chair, bench or low wall about knee height that cannot slip (you have no stairs: test it first).',
    'Place the whole foot on the step, drive through that heel to stand on top, control the way down. Finish all reps on one leg, then switch.',
    'Out on the way up.',
    'Pushing off the back foot; knee caving in.',
    'Lower step.',
    'Backpack on; slower lowering.',
)
E(
    'Water-bottle front raise',
    'Upper body',
    'Front shoulders',
    'Stand tall, a 1.5 L bottle in each hand in front of the thighs.',
    'Raise the arms straight in front to shoulder height, thumbs up, then lower in 3 s.',
    'Out on the way up.',
    'Swinging; leaning back.',
    'One arm at a time.',
    'Fuller bottles, 2 s pause.',
)
E(
    'Resistance-band row',
    'Upper body',
    'Upper back, lats, biceps',
    'Loop a resistance band round a strong door handle or pole at chest height (band costs about 15,000 to 30,000 TZS).',
    'Step back until the band is tight, pull the handles to your ribs squeezing the shoulder blades, return in 2 s.',
    'Out as you pull.',
    'Shrugging; leaning back to cheat.',
    'Step closer.',
    'Step further away, pause 2 s.',
)
E(
    'Overhead triceps extension',
    'Upper body',
    'Triceps',
    'Stand or sit tall, a 1.5 L water bottle or the backpack held with both hands overhead.',
    'Bend the elbows and lower the weight behind your head, elbows pointing up, then straighten the arms.',
    'In down, out up.',
    'Elbows flaring wide; arching the back.',
    'Lighter bottle.',
    'Heavier backpack, slower lowering.',
)
E(
    'Reverse crunch',
    'Core',
    'Lower abs',
    'Lie on your back, hands by your sides, knees bent at 90 degrees above the hips.',
    'Curl the hips off the floor towards the ribs, then lower slowly. Use the abs, not momentum.',
    'Out as you curl.',
    'Swinging the legs; lifting the head.',
    'Smaller range.',
    '3 s lowering.',
)
E(
    'Lying leg raise',
    'Core',
    'Lower abs, hip flexors',
    'Lie on your back, hands under the hips, legs straight.',
    'Lift the legs to vertical, lower them slowly until just above the floor without the lower back arching.',
    'Out as you lift.',
    'Lower back arching.',
    'Bent knees.',
    'Slower, pause at the bottom.',
)
E(
    'Mountain climber',
    'Core',
    'Core, shoulders, heart rate',
    'High plank, hands under the shoulders.',
    'Drive one knee towards the chest, switch legs in a running rhythm. Hips stay level.',
    'Steady rhythm.',
    'Hips high; bouncing.',
    'Step the feet in slowly.',
    'Faster, or cross the knee to the opposite elbow.',
)
E(
    'Pallof press',
    'Core',
    'Anti-rotation core',
    'Band anchored at chest height to your side; stand side-on, hands at the chest holding the band.',
    'Press the hands straight out, resist the band pulling you round for 2 s, bring them back. Do all reps, then face the other way.',
    'Out as you press.',
    'Twisting towards the anchor.',
    'Stand closer.',
    'Step further away; half kneeling.',
)

# Other names the brief uses for exercises that already exist in the library
ALSO_CALLED = {
    'Backpack goblet squat': 'Goblet squat',
    'Backpack Bulgarian split squat': 'Bulgarian split squat',
    'Jerrycan Romanian deadlift': 'Romanian deadlift',
    'Backpack hip thrust': 'Hip thrust',
    'Calf raise on a step': 'Calf raise',
    'Feet-elevated push-up': 'Decline push-up',
    'Push-up': 'Standard push-up',
    'Backpack overhead press': 'Shoulder press',
    'Water-bottle lateral raise': 'Lateral raise',
    'Backpack bent-over row': 'Bent-over row',
    'Jerrycan biceps curl': 'Biceps curl',
    'Jerrycan hammer curl': 'Hammer curl',
    'Front plank': 'Plank',
    'Towel hamstring curl': 'Hamstring curl',
}
ADVANCED = {
    'Nordic hamstring lower',
    'Feet-elevated pike push-up',
    'Burpee broad jump',
    'Single-leg Romanian deadlift',
    'Backpack Bulgarian split squat',
    'Lying leg raise',
    'Feet-elevated push-up',
}
BEGINNER = {
    'Bodyweight squat',
    'Glute bridge',
    'Reverse lunge',
    'Calf raise on a step',
    'Wall sit',
    'Dead bug',
    'Bird dog',
    'Front plank',
    'Incline push-up',
    'Water-bottle lateral raise',
    'Water-bottle front raise',
    'Jerrycan biceps curl',
    'Jerrycan hammer curl',
    'Reverse crunch',
    'Walking lunge',
}


def equipment(name):
    n = name.lower()
    if 'backpack' in n:
        return 'Loaded backpack (6 to 15 kg)'
    if 'jerrycan' in n or name == 'Farmer carry':
        return 'Jerrycan (1 L of water = 1 kg)'
    if 'water-bottle' in n or name == 'Overhead triceps extension':
        return '1.5 L water bottles'
    if 'band' in n or name == 'Pallof press':
        return 'Resistance band'
    if name in ('Chair dip', 'Step-up', 'Feet-elevated push-up', 'Feet-elevated pike push-up'):
        return 'Sturdy chair or bench'
    if name in ('Towel hamstring curl',):
        return 'Towel on a smooth floor'
    return 'Bodyweight'


def difficulty(name, cat):
    if cat == 'Pelvic floor' or name in BEGINNER:
        return 'Beginner'
    if name in ADVANCED:
        return 'Advanced'
    return 'Intermediate'


# ---- mobility library (by area)
MOBILITY = [
    # name, area, how, dose
    (
        'Half-kneeling hip flexor stretch',
        'Hip flexors',
        'Kneel on one knee, other foot forward. Squeeze the glute of the kneeling leg and shift the hips forward until the front of the hip stretches. Ribs down.',
        '30 to 60 s each side',
    ),
    (
        'Couch stretch',
        'Quadriceps and hip flexors',
        'Back knee on a cushion against a wall, shin up the wall, front foot forward. Tall chest, squeeze the glute.',
        '1 min each side',
    ),
    (
        'Hip 90/90 switches',
        'Hips',
        'Sit with both knees bent at 90 degrees to one side. Rotate both knees to the other side without using your hands, sitting tall.',
        '6 to 8 each side',
    ),
    (
        'Pigeon stretch',
        'Glutes',
        'From all fours, bring one knee forward behind the wrist, back leg long. Fold forward over the front shin.',
        '1 min each side',
    ),
    ('Figure-4 glute stretch, lying', 'Glutes', 'On your back, ankle over the other knee, pull that thigh towards you.', '30 to 45 s each side'),
    (
        'Ankle rocks (knee to wall)',
        'Ankles',
        'Foot 5 to 10 cm from a wall, push the knee forward to touch the wall with the heel down. Move the foot back as you improve.',
        '10 each side',
    ),
    (
        'Standing calf stretch on a wall',
        'Calves',
        'Hands on a wall, one leg back straight with the heel down; then bend that knee a little for the lower calf.',
        '30 s each, straight and bent',
    ),
    (
        'Lying hamstring stretch with a towel',
        'Hamstrings',
        'On your back, towel round one foot, straight leg up until you feel the back of the thigh. Other leg flat.',
        '45 s each leg',
    ),
    (
        'Thoracic open book',
        'Thoracic spine',
        'Lie on your side, knees bent, arms forward together. Open the top arm across to the other side, following it with your eyes.',
        '8 each side',
    ),
    ('Cat-cow', 'Spine', 'On all fours: round the back up slowly, then let the belly drop and lift the chest. Move with the breath.', '8 to 10 slow reps'),
    (
        'Towel shoulder pass-through',
        'Shoulders',
        'Hold a towel wide with straight arms, take it over your head and down behind you, then back.',
        '10 slow reps',
    ),
    (
        'Sleeper stretch (lying on your side)',
        'Shoulders (swimmers)',
        'Lie on one side, upper arm out at 90 degrees, elbow bent. Gently press the forearm down towards the floor with the other hand.',
        '30 s each side',
    ),
    (
        'Doorway chest stretch',
        'Chest and shoulders',
        'Forearm on a door frame at shoulder height, step through until the chest stretches.',
        '30 to 60 s each side',
    ),
    (
        'Deep squat hold',
        'Hips and ankles',
        'Sit in your deepest squat with heels down, elbows pushing the knees out. Hold a door frame if needed.',
        '1 to 2 min',
    ),
    ('Knees-to-chest rock', 'Lower back', 'On your back, hug both knees and rock gently side to side.', '30 to 60 s'),
    ('Supine spinal twist', 'Lower back and hips (cyclists)', 'On your back, drop both knees to one side, arms out, look the other way.', '30 s each side'),
]
MOBILITY_ROUTINES = [
    ('AM-MOB', 'Morning, 5 to 10 min', 'Any day before work. Wakes up hips, ankles and spine.'),
    ('W-RUN', 'Pre-run dynamic warm-up', 'Before every run, hard or easy.'),
    ('W-SWIM', 'Swimming shoulders, on the pool deck', 'Before every swim.'),
    ('C-SWIM', 'Swimming shoulders, after the swim', 'After every swim.'),
    ('W-BIKE', 'Before the ride', 'From the bike start in March.'),
    ('C-BIKE', 'Cycling hips and lower back', 'After every ride and brick.'),
    ('C-STR', 'Post-strength stretching', 'After every strength session.'),
    ('C-RUN', 'Post-run stretching', 'After runs and bricks.'),
    ('M-FLOW', 'Recovery-day routine', 'Fasting days, rest days and the day before a race.'),
]

# ---- pelvic floor: dedicated section
PELVIC = {
    'intro': 'The pelvic floor is the sling of muscle under your pelvis that controls urine, wind and erections, and stabilises the core. Like any muscle it gets stronger with training, and it also has to relax fully. Being able to relax it matters as much as squeezing it.',
    'find': [
        'Lie on your back with your knees bent and breathe normally.',
        'Imagine stopping the flow of urine and holding in wind at the same time: draw the area between your legs up and in. The base of the penis pulls in slightly and the testicles lift a little.',
        'Glutes, thighs and belly stay soft. You should be able to keep breathing and talking.',
        'Do not practise by stopping your urine on the toilet: it can stop the bladder emptying properly. Use it once only to find the muscle if you are unsure.',
    ],
    'drills': [
        ('Slow contractions', 'Squeeze and lift for 5 s (build to 10 s), then relax completely for at least as long (5 to 10 s).', '8 to 10 reps'),
        ('Short contractions', 'Quick strong squeeze for 1 s, full relax for 2 s.', '10 reps'),
        (
            'Relaxation drop',
            'Breathe in slowly through the nose and let the pelvic floor drop and widen, as if letting the belly fill down to the pelvis.',
            '6 slow breaths',
        ),
        (
            'Breathing coordination',
            'Breathe in: belly, ribs and pelvic floor relax. Breathe out through pursed lips: gently lift the pelvic floor. Never hold your breath while squeezing.',
            '8 breaths',
        ),
        (
            'Lift with effort',
            'Light lift just before and during the hard part of a movement (standing up from a squat, a bridge, a carry), relax at the top.',
            'Built into the kegel finisher',
        ),
    ],
    'levels': [
        (
            'Level 1: lying down (weeks 1 to 3)',
            '2 x 8 slow (5 s hold, 5 to 10 s relax) + 1 x 10 short, then 6 relaxation breaths, once or twice a day.',
            'Move on when you can do every rep with full relaxation and no breath holding.',
        ),
        (
            'Level 2: sitting and standing (weeks 4 to 8)',
            '2 x 10 slow (8 to 10 s hold, 10 s relax) + 2 x 10 short in sitting and standing.',
            'Move on when the holds feel steady and the relax is complete.',
        ),
        (
            'Level 3: with movement (week 9 on)',
            'The kegel finisher after strength sessions: lifts during bridges, squats, lunges and carries, with relaxation breaths at the end.',
            'Keep this for maintenance. More is not better.',
        ),
    ],
    'rules': [
        'Relax completely between every contraction. Never hold the pelvic floor tight all day.',
        'Two short practice sessions a day is enough. Overtraining causes tension, pain and urgency.',
        'Stop and see a doctor or pelvic-floor physiotherapist if you get pelvic, testicular or back pain, pain when urinating, or new leaking.',
        'Kegels improve control, continence and pelvic-floor strength. There is no good evidence that they raise testosterone, so the app makes no such claim.',
    ],
}


# ---- added 17 Nov 2026: knee-friendly exercises, the kegel circuit and the knee-care routine
E(
    'Chair squat',
    'Legs',
    'Quads, glutes (knee-friendly)',
    'Stand in front of a sturdy chair, feet shoulder-width.',
    'Sit back until you touch the chair lightly, then stand. Only go as deep as is pain-free; shins stay close to vertical.',
    'In on the way down, out on the way up.',
    'Knees pushing far forward; dropping onto the chair.',
    'Higher seat (add a cushion).',
    'Lower seat, then the backpack goblet squat when pain-free.',
)
E(
    'Side-lying leg raise',
    'Legs',
    'Outer hip (glute medius): keeps the knee tracking straight',
    'Lie on your side, bottom knee bent, top leg straight and slightly behind you.',
    'Lift the top leg about 40 cm with the toes pointing forward, hold 1 s, lower in 3 s.',
    'Out as you lift.',
    'Rolling the hips back; toes turning up.',
    'Smaller lift.',
    'Hold 3 s at the top.',
)
E(
    'Straight-leg raise',
    'Legs',
    'Quads without bending the knee',
    'Lie on your back, one knee bent, the other leg straight.',
    'Tighten the thigh of the straight leg, lift it to the height of the other knee, hold 2 s, lower slowly.',
    'Out as you lift.',
    'Knee bending; lower back arching.',
    'Fewer reps.',
    '3 s hold, then a light ankle weight.',
)
E(
    'Slow kegel holds',
    'Pelvic floor',
    'Pelvic floor endurance',
    'Lie on your back with your knees bent, breathing normally.',
    'Squeeze and lift the pelvic floor for 5 s (8 s from the second week, 10 s later), then relax completely for 10 s.',
    'Keep breathing; never hold your breath.',
    'Squeezing glutes or thighs; not relaxing fully.',
    '3 s holds.',
    'Sitting, then standing.',
)
E(
    'Quick kegel squeezes',
    'Pelvic floor',
    'Pelvic floor speed',
    'Lie on your back with your knees bent.',
    'One strong squeeze for 1 s, then 2 s of complete relaxation. Quality over speed.',
    'Breathe normally.',
    'Rushing without relaxing between squeezes.',
    '5 reps.',
    'Sitting or standing.',
)
E(
    'Deep squat hold with kegel',
    'Pelvic floor',
    'Pelvic floor, hips',
    'Sit in your deepest comfortable squat, holding a door frame if needed.',
    'Hold the squat with a gentle half-strength pelvic floor squeeze, breathing normally; relax fully before standing.',
    'Slow nose breathing.',
    'Holding the breath; heels lifting.',
    'Sit on a low stool.',
    'Longer holds.',
)
E(
    'Relaxation breathing',
    'Pelvic floor',
    'Pelvic floor release',
    'Lie on your back, knees bent, one hand on your belly.',
    'Breathe in slowly through the nose and let the belly and pelvic floor drop and widen; breathe out gently.',
    'Slow: 4 s in, 6 s out.',
    'Squeezing during the breath in.',
    '',
    '',
)
BEGINNER |= {'Chair squat', 'Side-lying leg raise', 'Straight-leg raise'}
WARMUPS.append(
    (
        'KNEE',
        'Knee care (8 min, every day while the knee settles)',
        [
            ('Straight-leg raise', '2 x 12 each leg'),
            ('Side-lying leg raise', '2 x 12 each side'),
            ('Glute bridge', '2 x 12, 2 s squeeze'),
            ('Half-kneeling hip flexor stretch', '45 s each side'),
            ('Standing quad stretch (heel to glute)', '30 s each side'),
            ('Standing calf stretch on a wall', '30 s each side'),
            ('Outer-thigh roll on a full water bottle', '1 min each side'),
        ],
    )
)
MOBILITY_ROUTINES.append(('KNEE', 'Knee care', 'Every day while a knee niggle is active: strengthens the muscles that hold the knee steady.'))
