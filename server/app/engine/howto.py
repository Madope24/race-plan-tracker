# Full how-to details for swim drills, swim strokes, stretches, warm-up drills, shoulder care,
# and the rules that keep running and swimming injury-free. Registered into the exercise library
# (library.L) so every row in a session can show its full instructions in the app.
from __future__ import annotations

from . import library as LB

PURPOSE: dict[str, str] = {}
CUES: dict[str, str] = {}
DOSE: dict[str, str] = {}


def H(name, cat, focus, purpose, setup, steps, breathing, cues, mistakes, easier, harder, dose):
    """Register one exercise. steps is a list; it is stored as '1) ... 2) ...' like the rest of the library."""
    how = ' '.join(f'{i}) {s}' for i, s in enumerate(steps, 1))
    LB.E(name, cat, focus, setup, how, breathing, mistakes, easier, harder)
    PURPOSE[name] = purpose
    CUES[name] = cues
    DOSE[name] = dose


# ============================================================================ swim drills
H(
    'Streamline push and glide',
    'Swim drill',
    'Body position, streamline, push-off',
    'Teaches the long, narrow body line every length starts with. A good glide saves energy on every wall.',
    'Stand in the shallow end with your back to the wall, one foot flat on the wall behind you.',
    [
        'Arms straight overhead, one hand on top of the other, upper arms squeezing your ears.',
        'Take a breath, sink under the water and push off gently with both feet together.',
        'Face looks straight down at the floor, body long and tight like an arrow, toes pointed.',
        'Glide without kicking until you slow down. Note how far you got.',
        'Stand up, walk back and repeat. Try to glide further each time by being longer and tighter.',
    ],
    'Breathe in before you push off; let bubbles out slowly through the nose while you glide.',
    'Squeeze the ears with the arms. Look at the floor, not forward. Tight belly and glutes.',
    'Lifting the head (the legs sink). Arms apart or bent. Pushing off with one foot or twisting the knee.',
    'Hold the pool edge with one hand first and practise lying flat face-down.',
    'Add 3 to 4 gentle flutter kicks at the end of the glide, then 3 strokes of freestyle.',
    '6 to 8 glides',
)
H(
    'Bubble breathing',
    'Swim drill',
    'Breathing out under water, relaxation',
    'Most beginners hold their breath under water, so they get breathless fast. This drill teaches you to breathe out fully under water so the breath in is quick and easy.',
    'Stand in chest-deep water holding the edge.',
    [
        'Breathe in through the mouth above the water.',
        'Sink your face (or whole head) under the water.',
        'Breathe out steadily through the nose and mouth: a long stream of bubbles, humming helps.',
        'Come up only when the air is out, take a quick breath in and go down again.',
        'Keep a calm rhythm: about 3 s out under water, 1 s in.',
    ],
    'This drill is the breathing: out under water, in above it. Never hold your breath.',
    'Hum "mmmm" under water. Empty the lungs before you lift your head.',
    'Holding the breath and blowing it all out at the surface. Lifting the head high to breathe.',
    'Just the face in the water, holding the edge with both hands.',
    'Do it while kicking on your side, then while swimming freestyle.',
    '3 x 10 breaths',
)
H(
    'Kick on your side',
    'Swim drill',
    'Body rotation, balance, breathing position, kick',
    'Freestyle is swum on your side, not flat. This drill teaches balance on your side and the head position for breathing.',
    'Push off on your side: bottom arm stretched forward, top arm resting on your hip, one goggle in the water.',
    [
        'Lie on your side with the bottom arm reaching forward and the top arm on your thigh.',
        'Kick gently from the hips with long, relaxed legs and loose ankles (small, fast kicks).',
        'Keep your face looking down at the floor; roll your head only to breathe, with one goggle still in the water.',
        'Breathe out under water, roll the mouth up to breathe in, roll back down.',
        'Swim one length on your right side, the next on your left side.',
    ],
    'Out under water, roll the head with the body to breathe in. Keep the bottom ear on the arm.',
    'Hips high, shoulder of the top arm pointing at the ceiling. Kick from the hips, not the knees.',
    'Bending the knees a lot (cycling kick). Lifting the head forward. Sinking hips.',
    'Use a kickboard under the front arm, or wear fins if the pool allows.',
    'Hold your side for 9 kicks, then take 3 strokes and roll onto the other side.',
    '4 x 25 m',
)
H(
    '6-3-6 drill',
    'Swim drill',
    'Rotation, timing, breathing to both sides',
    'Joins the side position to the stroke and teaches you to rotate from hip to hip.',
    'Push off on your right side as in the side-kick drill.',
    [
        'Kick 6 times on your right side, bottom arm forward.',
        'Take 3 freestyle strokes, which rolls you onto your left side.',
        'Kick 6 times on your left side.',
        'Take 3 strokes back to the right side, and so on.',
        'Breathe during the side kick, not during the strokes.',
    ],
    'Breathe during the 6 kicks with one goggle in the water; breathe out during the strokes.',
    'Roll the whole body, not just the shoulders. Reach long with each stroke.',
    'Staying flat during the strokes. Rushing the 3 strokes. Lifting the head to breathe.',
    '9 kicks instead of 6 to give yourself more time.',
    '6 kicks, 1 stroke, 6 kicks (6-1-6).',
    '4 x 25 m',
)
H(
    'Catch-up freestyle',
    'Swim drill',
    'Long reach, timing, front of the stroke',
    'Stops short, rushed strokes. You learn to reach long and pull with one arm at a time.',
    'Push off in streamline, both arms out in front.',
    [
        'Keep one arm stretched out in front at all times.',
        'Pull with the other arm all the way back to the thigh, recover it over the water and place it on top of the front hand.',
        'Only when the hands touch does the front arm start its pull.',
        'Breathe to the side of the pulling arm, every 2 or 3 strokes.',
        'Keep a steady flutter kick the whole way.',
    ],
    'Breathe to the side of the arm that is pulling; one goggle stays in the water.',
    'Touch hands in front, then go. Long reach, finish the push past the hip.',
    'Dropping the front arm while waiting. Crossing the hand over the middle line. Stopping the kick.',
    'Hold a kickboard in front and swap hands on it after each stroke.',
    'Three-quarter catch-up: start the pull when the recovering hand passes your head.',
    '4 x 25 m',
)
H(
    'Single-arm freestyle',
    'Swim drill',
    'Pull path, rotation, breathing timing',
    'Lets you focus on one arm at a time: the catch, the pull and the body roll that powers it.',
    'Push off with one arm stretched forward (or resting by your side) and the other arm doing the work.',
    [
        'Swim freestyle with the right arm only; the left arm stays out in front.',
        'Rotate your body toward the pulling arm as it pulls.',
        'Breathe to the side of the working arm, as it finishes the pull.',
        'Swim 25 m with the right arm, then 25 m with the left arm.',
    ],
    'Breathe to the working-arm side as the hand passes your hip.',
    'Elbow high, fingertips down at the start of the pull. Hips roll with the arm.',
    'Pulling with a straight arm. Swinging the arm wide. Flat body.',
    'Do it with fins, or with the resting arm on a kickboard.',
    'Resting arm by your side instead of in front: much harder to balance.',
    '4 x 25 m (2 each arm)',
)
H(
    'Fingertip drag',
    'Swim drill',
    'High-elbow recovery, relaxed shoulders',
    'A high, relaxed elbow over the water protects the shoulder and keeps the stroke narrow.',
    'Normal freestyle.',
    [
        'As each arm comes forward over the water, bend the elbow and let the fingertips drag along the surface.',
        'The elbow is the highest point of the arm; the hand passes close to your side and your ear.',
        'Enter the water in front of your shoulder, not in front of your head.',
        'Keep everything else as normal freestyle.',
    ],
    'Normal breathing pattern, every 2 or 3 strokes.',
    'Elbow high, hand relaxed. Drag a line on the water from hip to head.',
    'Swinging the arm wide and straight. Tense hand. Entering across the middle.',
    'Touch your armpit with your thumb on the way forward (zipper drill).',
    'Drag the fingertips more slowly while keeping the kick steady.',
    '4 x 25 m',
)
H(
    'Fist drill',
    'Swim drill',
    'Forearm catch, feel for the water',
    'With a closed fist you must pull with the forearm. When you open the hands again, the pull feels much stronger.',
    'Normal freestyle with both hands in a loose fist.',
    [
        'Make loose fists with both hands.',
        'Swim freestyle: bend the elbow early so the forearm faces back and pushes water.',
        'Swim 25 m with fists.',
        'Swim the next 25 m with open hands and feel the extra grip.',
    ],
    'Normal breathing pattern.',
    'Elbow high and in front, forearm vertical, push the water back to your feet.',
    'Pulling with a straight arm. Slipping and rushing the strokes.',
    'Alternate 4 strokes fists, 4 strokes open hands.',
    'Fists for a full 50 m, then compare stroke count with open hands.',
    '4 x 25 m (alternate fists and open hands)',
)
H(
    'Sculling',
    'Swim drill',
    'Feel for the water, catch position',
    'Teaches the hand and forearm angle that holds the water at the start of the pull.',
    'Face-down in the water, arms straight out in front, a gentle kick (or a float between the legs).',
    [
        'Point your fingertips slightly down, hands just below the surface, shoulder-width apart.',
        'Sweep both hands outward a little, pitched outward like a windscreen wiper.',
        'Sweep them back inward, pitched inward.',
        'Keep the sweeps small and quick: you should move forward slowly.',
        'Lift your head to breathe when needed, or roll to the side.',
    ],
    'Breathe out under water; lift or roll to breathe in every 4 to 6 sweeps.',
    'Small figure-8 with the hands, wrists firm, elbows near the surface.',
    'Big wide sweeps. Bending the wrists. Sinking the elbows.',
    'Stand in chest-deep water and scull with the hands at hip level to feel the pressure.',
    'Scull with the hands under the shoulders (mid-scull) or by the hips.',
    '4 x 20 m',
)
H(
    'Bilateral breathing ladder',
    'Swim drill',
    'Breathing to both sides, even stroke',
    'Breathing to both sides keeps the stroke even and shares the work between both shoulders, which helps prevent shoulder pain.',
    'Normal freestyle.',
    [
        'First length: breathe every 3 strokes (left, right, left).',
        'Second length: breathe every 5 strokes.',
        'Third length: back to every 3.',
        'Fourth length: every 2 strokes, as you would when tired in a race.',
    ],
    'Breathe out steadily under water through the strokes so the breath in is short.',
    'Same head roll on both sides; one goggle stays in the water.',
    'Lifting the head forward to breathe. Shortening the stroke on the weak side.',
    'Every 3 for 25 m, then every 2 for 25 m.',
    'Every 3, 5, 7 for one length each.',
    '4 x 25 m',
)
H(
    'Kick on your back',
    'Swim drill',
    'Kick, hip position, relaxed breathing',
    'An easy way to train the kick without breathing problems, and it rests the shoulders.',
    'Float on your back, arms by your sides, ears in the water, looking at the ceiling.',
    [
        'Push off on your back, arms by your sides.',
        'Kick from the hips with long legs; knees stay just under the surface.',
        'Keep your hips and tummy high, chin slightly in.',
        'Breathe normally all the way.',
    ],
    'Breathe normally; the face is out of the water.',
    'Toes just break the surface, little splash. Hips up.',
    'Sitting in the water (hips sink). Big bent-knee kicks. Lifting the head to look at your feet.',
    'Hold a kickboard on your chest.',
    'Arms overhead in streamline.',
    '4 x 25 m',
)
H(
    'Stroke-count lengths',
    'Swim drill',
    'Efficiency (SWOLF)',
    'Fewer strokes per length at the same effort means a longer, more efficient stroke. Your watch shows this as SWOLF (strokes + seconds).',
    'Normal freestyle at easy effort.',
    [
        'Swim a length counting each hand entry.',
        'Note the number (for example 22).',
        'Swim the next length trying to take 1 or 2 fewer strokes at the same effort: reach further, glide a little.',
        'Rest 20 s between lengths.',
    ],
    'Your normal pattern; do not hold your breath to save strokes.',
    'Long reach, full push past the hip, push off the wall well.',
    'Gliding so long that you lose speed and sink. Kicking harder to cheat.',
    'Count only every other length.',
    'Keep the same count while swimming faster.',
    '4 x 25 m',
)
H(
    'Sighting drill',
    'Swim drill',
    'Open-water navigation',
    'In the sea there is no black line. You lift your eyes briefly to see where you are going without breaking the stroke.',
    'Normal freestyle; pick a target at the end of the pool.',
    [
        'Every 6 strokes, as your arm presses down at the front, lift the eyes just above the water (crocodile eyes).',
        'Look forward at the target for a moment.',
        'Turn the head to the side to breathe as normal; do not breathe forward.',
        'Put the face back down and keep swimming.',
    ],
    'Sight forward, then breathe to the side in the same stroke.',
    'Only the eyes come up. Quick look, then back down. Press down with the front hand.',
    'Lifting the whole head and chest (the legs sink). Breathing forward.',
    'Sight every 10 strokes.',
    'Sight every 4 strokes, at race pace.',
    '4 x 25 m',
)

# ============================================================================ strokes
H(
    'Freestyle (front crawl)',
    'Swim stroke',
    'Shoulders, back (lats), core, legs',
    'The stroke for every main set and for triathlon.',
    'Face-down, body long and flat near the surface, arms forward.',
    [
        'Head: look at the floor just ahead; water line at the top of the head.',
        'Entry: the hand enters in front of the shoulder, fingertips first, and reaches forward.',
        'Catch: bend the elbow early so the forearm and hand face back.',
        'Pull: push the water back past the hip with the whole forearm, rolling the hips with the stroke.',
        'Recovery: elbow leads out of the water, relaxed hand swings forward close to the body.',
        'Kick: small, steady kicks from the hips with relaxed ankles.',
        'Breathing: roll the head with the body to the side, breathe in, roll back; breathe out under water.',
    ],
    'Breathe out under water all the time; quick breath in at the side every 2 or 3 strokes.',
    'Long, relaxed, rotate. Hands in front of the shoulders, not across the middle.',
    'Lifting the head forward. Crossing the hands over the middle line (pinches the shoulder). Holding the breath. Big kicks.',
    'Stop at each wall; breathe every 2 strokes.',
    'Breathe every 3 strokes; tumble turns; swim at an even pace for longer.',
    'As in the session',
)
H(
    'Backstroke',
    'Swim stroke',
    'Shoulders, back, core',
    'An easy cool-down and a good balance to freestyle for the shoulders.',
    'On your back, ears in the water, eyes up.',
    [
        'Body long, hips near the surface.',
        'One arm leaves the water thumb-first, straight, passing your ear.',
        'It enters little-finger-first above the shoulder.',
        'Bend the elbow under the water and push the water down to your thigh.',
        'Roll the shoulders a little with each stroke; steady kick.',
    ],
    'Breathe normally: in on one arm, out on the other.',
    'Still head, hips up, long arms.',
    'Sitting in the water. Head lifted. Arms entering behind the head.',
    'Kick on your back with a slow arm every few kicks.',
    'Steady 100 m without stopping.',
    'As in the session',
)

# ============================================================================ warm-up drills (dry land)
H(
    'Brisk walk',
    'Warm-up drill',
    'Whole body, heart rate',
    'Raises the heart rate and warms the muscles before stretching or running.',
    'Flat path or the compound.',
    ['Walk fast with a purpose, arms swinging.', 'Stand tall and land softly heel to toe.'],
    'Normal breathing.',
    'Faster than a stroll, slower than a jog.',
    'Starting to run straight away.',
    '',
    '',
    '3 min',
)
H(
    'Leg swings front to back',
    'Warm-up drill',
    'Hip flexors, hamstrings',
    'Loosens the hips through the running range.',
    'Stand side-on to a wall or tree, one hand on it.',
    [
        'Swing the outside leg forward and back like a pendulum.',
        'Start small and let the swing grow to a comfortable height.',
        'Keep the standing knee soft and the body upright.',
        'Swap legs.',
    ],
    'Relaxed breathing.',
    'Loose, controlled swing; the trunk stays still.',
    'Kicking hard or leaning back.',
    'Smaller swings.',
    'Faster swings.',
    '10 each leg',
)
H(
    'Leg swings side to side',
    'Warm-up drill',
    'Inner and outer thigh, hips',
    'Opens the hips sideways and wakes up the glutes that keep the knee in line.',
    'Face a wall, both hands on it.',
    ['Swing one leg across the front of the body and out to the side.', 'Let the swing grow gradually.', 'Swap legs.'],
    'Relaxed breathing.',
    'Hips face the wall; move from the hip.',
    'Twisting the body with the leg.',
    'Smaller swings.',
    '',
    '10 each leg',
)
H(
    'Walking lunge with a twist',
    'Warm-up drill',
    'Hips, quads, glutes, upper back',
    'Warms the legs through a big range and frees the upper back.',
    'Clear path of about 10 m.',
    [
        'Step forward into a lunge; back knee lowers toward the ground.',
        'Turn the chest toward the front leg, arms out.',
        'Turn back to the middle and step through into the next lunge.',
    ],
    'Breathe out as you turn.',
    'Front knee over the middle of the foot; tall chest.',
    'Front knee caving in. Stepping too short.',
    'Smaller step; hold something for balance. During knee care keep the lunge shallow.',
    'Reach the arms overhead at the bottom.',
    '6 each leg',
)
H(
    'Ankle bounces',
    'Warm-up drill',
    'Calves, Achilles, feet',
    'Prepares the calves and Achilles for the impact of running.',
    'Stand tall, feet hip-width.',
    ['Bounce lightly on the balls of the feet, heels just off the ground.', 'Keep the knees almost straight and the contacts quick and quiet.'],
    'Relaxed breathing.',
    'Quick, quiet, springy.',
    'Landing heavily on the heels. Bending the knees a lot.',
    'Calf raises instead.',
    'Small forward hops.',
    '20 bounces',
)
H(
    'A-skips',
    'Warm-up drill',
    'Hip flexors, calves, running form',
    'Teaches a quick foot strike under the hips, the action that reduces braking and knee load.',
    'Flat 15 m.',
    [
        'Skip forward: drive one knee up to hip height while the other foot taps down under the hip.',
        'Swing the arms like running.',
        'Keep the contacts light and quick.',
    ],
    'Relaxed breathing.',
    'Tall, knee up, foot down under you.',
    'Leaning back. Landing in front of the body.',
    'Marching version (no skip).',
    'Faster rhythm.',
    '2 x 15 m',
)
H(
    'High knees',
    'Warm-up drill',
    'Hip flexors, calves',
    'Raises the heart rate and wakes up a quick running rhythm.',
    'Flat 15 m.',
    ['Run slowly forward with fast, short steps, lifting the knees toward hip height.', 'Land on the balls of the feet; pump the arms.'],
    'Relaxed breathing.',
    'Quick feet, tall body.',
    'Leaning back; stamping.',
    'March with high knees.',
    'Faster cadence.',
    '2 x 15 m',
)
H(
    'Butt kicks',
    'Warm-up drill',
    'Hamstrings, quads',
    'Warms the hamstrings and loosens the front of the thighs.',
    'Flat 15 m.',
    ['Jog slowly, flicking each heel up toward the buttock.', 'Keep the knees pointing down.'],
    'Relaxed breathing.',
    'Quick, light flicks.',
    'Leaning forward; knees swinging forward.',
    'On the spot.',
    '',
    '2 x 15 m',
)
H(
    'Arm circles forward and back',
    'Warm-up drill',
    'Shoulders',
    'Warms the shoulder joint before swimming or upper-body work.',
    'Stand tall, arms out to the sides.',
    ['Make small circles forward, growing to big circles.', 'Repeat backward.'],
    'Relaxed breathing.',
    'Smooth, no pain.',
    'Shrugging the shoulders up.',
    'Smaller circles.',
    'Big swimming-style windmills.',
    '10 each way',
)
H(
    'Towel shoulder pass-through',
    'Warm-up drill',
    'Shoulders, chest',
    'Opens the shoulders through the swimming range.',
    'Hold a towel (or band) wide with straight arms in front of your hips.',
    ['Lift the towel up over your head and down behind you, arms straight.', 'Bring it back the same way.', 'Move the hands closer only if there is no pain.'],
    'Breathe out as the arms go overhead.',
    'Slow, ribs down, arms straight.',
    'Bending the elbows; arching the back.',
    'Wider grip.',
    'Narrower grip.',
    '10 slow reps',
)
H(
    'Doorway chest stretch',
    'Stretch',
    'Chest, front of the shoulders',
    'Undoes the hunched posture of desk work and the tight chest that pinches the shoulder in swimming.',
    'Stand in a doorway (or next to a wall), forearm on the frame with the elbow at shoulder height.',
    ['Step through with the same-side foot until you feel a stretch across the chest.', 'Hold, breathing slowly.', 'Swap sides.'],
    'Slow breaths; relax a little more on each breath out.',
    'Gentle stretch, never pain in the shoulder.',
    'Pushing into pain. Shrugging.',
    'Elbow lower.',
    'Elbow slightly higher.',
    '30 to 60 s each side',
)
H(
    'Thoracic open book',
    'Mobility',
    'Upper back (thoracic spine), chest',
    'A mobile upper back lets you rotate to breathe in swimming and stand tall when running.',
    'Lie on your side, knees bent to 90 degrees and stacked, arms straight out in front together.',
    [
        'Keep the knees together on the floor.',
        'Lift the top arm and open it across to the other side, following the hand with your eyes.',
        'Pause, then close the book again.',
        'Do all reps, then turn to the other side.',
    ],
    'Breathe out as you open.',
    'Knees stay down; move from the upper back.',
    'Knees lifting. Forcing the arm to the floor.',
    'Smaller movement.',
    'Pause 3 s open.',
    '6 to 8 each side',
)
H(
    'Streamline reach',
    'Warm-up drill',
    'Shoulders, lats, posture',
    'Rehearses the long streamline position before you get in the water.',
    'Stand tall.',
    ['Reach both arms overhead, one hand on top of the other, arms squeezing the ears.', 'Stretch tall through the fingertips for 5 s, then relax.'],
    'Breathe out as you reach.',
    'Ribs down, belly tight.',
    'Arching the back.',
    'Hands apart.',
    'Rise onto the toes.',
    '5 x 5 s',
)
H(
    'Cat-cow',
    'Mobility',
    'Spine',
    'Moves the whole spine gently: good after sleep, sitting and long runs.',
    'On all fours, hands under shoulders, knees under hips.',
    ['Round the back up toward the ceiling, chin to chest.', 'Then let the belly drop and lift the chest and eyes.', 'Move slowly with the breath.'],
    'In as the belly drops, out as you round.',
    'Slow, full range, no pain.',
    'Rushing. Moving only the neck.',
    'Smaller range.',
    '',
    '8 to 10 slow reps',
)
H(
    "World's greatest stretch",
    'Mobility',
    'Hips, hamstrings, upper back',
    'One move that opens the hips, hamstrings and upper back before strength work.',
    'Step into a long lunge, both hands on the floor inside the front foot.',
    [
        'Drop the back knee if needed.',
        'Lower the inside elbow toward the front foot.',
        'Rotate and reach the same arm up to the ceiling, eyes following.',
        'Return, then step to the other side.',
    ],
    'Breathe out as you rotate.',
    'Long lunge, hips low.',
    'Front knee caving in.',
    'Back knee down.',
    'Straighten the front leg at the end for the hamstring.',
    '3 each side',
)
H(
    'Hip 90/90 switches',
    'Mobility',
    'Hip rotation',
    'Frees the hips in both directions of rotation.',
    'Sit on the floor, both knees bent at 90 degrees and dropped to one side.',
    ['Sit tall.', 'Lift both knees and rotate them to the other side.', 'Use your hands behind you for support if needed.'],
    'Relaxed breathing.',
    'Tall chest, slow and controlled.',
    'Slumping. Forcing the knees down.',
    'Hands on the floor behind you.',
    'Hands off the floor.',
    '6 to 8 each side',
)
H(
    'Hip 90/90 hold',
    'Mobility',
    'Hip rotation, glutes',
    'A longer hold of the 90/90 position to open the hips.',
    'Sit in the 90/90 position.',
    ['Sit tall over the front shin.', 'Lean the chest forward slightly until you feel the front hip.', 'Hold, then switch sides.'],
    'Slow breaths.',
    'Tall back.',
    'Rounding the back.',
    'Sit on a cushion.',
    'Lean further.',
    '1 min each side',
)
H(
    'Inchworm',
    'Warm-up drill',
    'Hamstrings, shoulders, core',
    'Warms the hamstrings and shoulders together.',
    'Stand tall.',
    [
        'Bend down and put your hands on the floor (bend the knees if needed).',
        'Walk the hands out to a push-up position.',
        'Walk the feet in toward the hands.',
        'Stand up and repeat.',
    ],
    'Breathe out as you walk out.',
    'Slow; tight belly in the plank.',
    'Sagging hips.',
    'Bend the knees more.',
    'Add a push-up.',
    '5 reps',
)
H(
    'Scapular push-up',
    'Shoulder care',
    'Shoulder blades (serratus), shoulder stability',
    'Strengthens the muscles that hold the shoulder blade in place: key for healthy swimming shoulders.',
    'Push-up position (on the knees is fine), arms straight.',
    [
        'Keep the arms straight the whole time.',
        'Let the chest sink so the shoulder blades come together.',
        'Push the floor away so the shoulder blades spread apart and the upper back rounds slightly.',
    ],
    'Out as you push away.',
    'Arms straight; only the shoulder blades move.',
    'Bending the elbows. Sagging hips.',
    'Against a wall.',
    'Feet on a chair.',
    '2 x 10',
)
H(
    'First exercise, light',
    'Warm-up drill',
    'Whatever the first exercise trains',
    'A light practice set grooves the movement before the real sets.',
    'Set up for the first exercise of the session.',
    ['Do one set of 8 with about half the load (or bodyweight).', 'Focus on perfect form.'],
    'As for the exercise.',
    'Easy and smooth.',
    'Going heavy.',
    '',
    '',
    '1 set of 8',
)
H(
    'Child pose',
    'Stretch',
    'Lower back, lats, hips',
    'Relaxes the lower back and the pelvic floor.',
    'Kneel, big toes together, knees apart.',
    ['Sit back on your heels.', 'Reach the arms forward and rest the forehead on the floor.', 'Breathe slowly into the belly and lower back.'],
    'Slow breaths into the back.',
    'Let everything relax.',
    'Forcing the hips down.',
    'Pillow under the hips or forehead.',
    'Walk the hands to one side for the side of the back.',
    '45 s to 1 min',
)
H(
    'Child pose with side reach',
    'Stretch',
    'Lats, side of the body',
    'Stretches the big back muscles used in swimming.',
    'Child pose.',
    ['Walk both hands over to the right; hold.', 'Walk them to the left; hold.'],
    'Breathe into the stretched side.',
    'Hips stay back.',
    'Lifting the hips.',
    '',
    '',
    '1 min',
)
H(
    'Lying hamstring stretch with a towel',
    'Stretch',
    'Hamstrings',
    'Keeps the hamstrings long without loading the back.',
    'Lie on your back, towel around one foot.',
    ['Straighten that leg up toward the ceiling until you feel the back of the thigh.', 'Keep the other leg flat on the floor.', 'Hold, then swap.'],
    'Slow breaths.',
    'Gentle stretch; knee almost straight.',
    'Pulling hard; lifting the hips.',
    'Bend the other knee.',
    '',
    '45 s each leg',
)
H(
    'Half-kneeling hip flexor stretch',
    'Stretch',
    'Hip flexors',
    'Tight hip flexors from sitting pull on the pelvis and the knee. This is one of the most useful stretches for runners.',
    'Kneel on one knee (cushion under it), other foot forward.',
    [
        'Tuck the tailbone under and squeeze the glute of the kneeling leg.',
        'Shift the hips forward until the front of the hip stretches.',
        'Keep the ribs down. Reach the arm on the kneeling side overhead for more.',
    ],
    'Slow breaths.',
    'Glute squeezed; small movement.',
    'Arching the lower back instead of stretching the hip.',
    'Smaller forward shift.',
    'Arm overhead and lean away.',
    '30 to 60 s each side',
)
H(
    'Standing quad stretch',
    'Stretch',
    'Quadriceps',
    'Eases the front of the thigh, which pulls on the kneecap when tight.',
    'Stand tall next to a wall for balance.',
    ['Bend one knee and hold the ankle behind you.', 'Bring the heel gently toward the buttock, knees together.', 'Tuck the hips slightly.'],
    'Slow breaths.',
    'Knees together, hips forward.',
    'Arching the back. Pulling hard on a sore knee.',
    'Lie on your side and hold the ankle; or use a towel.',
    '',
    '30 s each side',
)
H(
    'Cross-body shoulder stretch',
    'Stretch',
    'Back of the shoulder',
    'Stretches the back of the shoulder after swimming.',
    'Stand or sit tall.',
    ['Bring one arm across the chest.', 'Hold it above the elbow with the other hand and pull gently.'],
    'Slow breaths.',
    'Shoulder stays down.',
    'Shrugging; twisting the body.',
    '',
    '',
    '30 s each arm',
)
H(
    'Overhead triceps stretch',
    'Stretch',
    'Triceps, lats',
    'Stretches the back of the arm and the side of the back.',
    'Stand tall.',
    ['Reach one arm up and bend the elbow so the hand drops behind the head.', 'Gently push the elbow with the other hand.'],
    'Slow breaths.',
    'Ribs down.',
    'Arching the back.',
    '',
    '',
    '30 s each arm',
)
H(
    'Standing calf stretch on a wall',
    'Stretch',
    'Calves, Achilles',
    'Tight calves are linked to Achilles and shin pain in runners.',
    'Hands on a wall, one foot back.',
    [
        'Back leg straight, heel down, lean into the wall: upper calf.',
        'Then bend the back knee a little, heel still down: lower calf and Achilles.',
        'Swap legs.',
    ],
    'Slow breaths.',
    'Heel stays down; toes point forward.',
    'Heel lifting; foot turned out.',
    '',
    'Stand on a step and drop the heel.',
    '30 s each, straight and bent',
)
H(
    'Standing hamstring stretch',
    'Stretch',
    'Hamstrings',
    'Stretches the back of the thigh after running.',
    'Heel on a low step or kerb, leg straight.',
    ['Keep the back flat and hinge forward from the hips.', 'Stop when you feel the back of the thigh.'],
    'Slow breaths.',
    'Flat back.',
    'Rounding the back to reach the toes.',
    'Lower step.',
    '',
    '30 s each side',
)
H(
    'Figure-4 glute stretch, lying',
    'Stretch',
    'Glutes, outer hip',
    'Relaxes the glutes and outer hip, which affect the line of the knee.',
    'Lie on your back, knees bent.',
    ['Cross one ankle over the opposite knee.', 'Pull that thigh toward your chest until the buttock stretches.'],
    'Slow breaths.',
    'Head and shoulders relaxed on the floor.',
    'Lifting the head; forcing.',
    'Keep the foot on the floor.',
    '',
    '30 to 45 s each side',
)
H(
    'Couch stretch',
    'Stretch',
    'Quadriceps, hip flexors',
    'A deep stretch for the front of the hip and thigh.',
    'Back knee on a cushion against a wall, shin up the wall, other foot forward.',
    ['Lift the chest tall.', 'Squeeze the glute of the back leg.', 'Hold, then swap.'],
    'Slow breaths.',
    'Tall chest, glute squeezed.',
    'Arching the back. Forcing it when the knee is sore.',
    'Knee further from the wall; hands on a chair. Skip during knee care if it pinches.',
    'Torso upright.',
    '1 min each side',
)
H(
    'Pigeon stretch',
    'Stretch',
    'Glutes, outer hip',
    'Opens the hip and glute.',
    'From all fours, bring one knee forward behind the same-side wrist, back leg long.',
    ['Square the hips.', 'Fold forward over the front shin.', 'Hold, then swap.'],
    'Slow breaths.',
    'No pain in the knee.',
    'Twisting the front knee. If the knee complains, use the figure-4 stretch instead.',
    'Figure-4 stretch lying.',
    '',
    '1 min each side',
)
H(
    'Ankle rocks',
    'Mobility',
    'Ankles, calves',
    'Better ankle bend means less strain on the knee when running and squatting.',
    'Kneel half-kneeling facing a wall, front foot 5 to 10 cm from it.',
    ['Push the front knee forward to touch the wall, heel down.', 'Return and repeat.', 'Move the foot back as you improve.'],
    'Relaxed breathing.',
    'Heel stays down; knee over the middle toes.',
    'Heel lifting; knee caving in.',
    'Foot closer to the wall.',
    'Foot further away.',
    '10 each side',
)
H(
    'Deep squat hold',
    'Mobility',
    'Hips, ankles',
    'Opens the hips and ankles.',
    'Feet a bit wider than hips, toes turned out.',
    ['Sit down into your deepest squat with the heels down.', 'Push the knees out with the elbows.', 'Hold a door frame if needed.'],
    'Slow breaths; let the pelvic floor relax.',
    'Heels down, chest up.',
    'Forcing depth. During knee care sit only as deep as is pain-free.',
    'Sit on a low stool.',
    '',
    '1 to 2 min',
)
H(
    'Legs up the wall',
    'Stretch',
    'Relaxation, legs',
    'Relaxes the legs and the nervous system on recovery days.',
    'Lie on your back with the buttocks near a wall.',
    ['Rest the legs straight up the wall.', 'Arms relaxed; breathe slowly.'],
    'Slow belly breathing.',
    'Let everything go.',
    'Holding tension in the legs, neck or jaw.',
    '',
    '',
    '3 min',
)
H(
    'Sleeper stretch',
    'Stretch',
    'Back of the shoulder (rotator cuff)',
    'Gentle stretch for the back of the shoulder that tightens in swimmers.',
    'Lie on one side, lower arm out in front at 90 degrees, elbow bent so the hand points up.',
    ['Use the top hand to press the lower forearm gently toward the floor.', 'Stop at a light stretch. Swap sides.'],
    'Slow breaths.',
    'Very gentle.',
    'Forcing it; any pinching pain.',
    'Smaller range.',
    '',
    '30 s each side',
)
H(
    'Knees-to-chest rock',
    'Stretch',
    'Lower back',
    'Relaxes the lower back.',
    'Lie on your back.',
    ['Hug both knees to the chest.', 'Rock gently side to side.'],
    'Slow breaths.',
    'Relaxed.',
    'Pulling hard on the knees or lifting the head.',
    '',
    '',
    '30 to 60 s',
)
H(
    'Supine spinal twist',
    'Stretch',
    'Lower back, hips',
    'Releases the lower back after riding and long runs.',
    'Lie on your back, knees bent, arms out.',
    ['Drop both knees to one side.', 'Turn the head the other way.', 'Hold, then swap.'],
    'Slow breaths.',
    'Shoulders stay on the floor.',
    'Forcing the knees down.',
    '',
    '',
    '30 s each side',
)
H(
    'Outer-thigh roll on a full water bottle',
    'Knee care',
    'Outer thigh (IT band area), quads',
    'Eases tight tissue on the outside of the thigh that can pull on the outside of the knee.',
    'Lie on your side with a full, closed 1.5 L bottle under the outer thigh.',
    [
        'Support yourself on your forearm and the top foot.',
        'Roll slowly from just above the knee to just below the hip.',
        'Pause on tender spots for a few breaths. Then do the front of the thigh.',
    ],
    'Slow breaths; relax over the bottle.',
    'Tender is fine, sharp is not.',
    'Rolling right over the knee joint.',
    'Less body weight on the bottle.',
    '',
    '1 min each side',
)

# ============================================================================ shoulder care (prevents swimmer's shoulder)
H(
    'Prone Y-T-W raise',
    'Shoulder care',
    'Lower trapezius, rear shoulder, rotator cuff',
    'Strengthens the muscles at the back of the shoulder that balance all the pulling in swimming.',
    'Lie face-down on the floor or a bed, forehead on a folded towel. Empty or small water bottles optional.',
    [
        'Y: arms overhead in a Y, thumbs up; lift them a few cm, hold 2 s, lower.',
        'T: arms straight out to the sides, thumbs up; lift, hold 2 s, lower.',
        'W: elbows bent and tucked, hands by the shoulders; squeeze the shoulder blades back and down, hold 2 s.',
    ],
    'Breathe out as you lift.',
    'Shoulder blades down and back. Small lifts.',
    'Shrugging; arching the lower back to lift higher.',
    'No weight; fewer reps.',
    '0.5 L bottles in the hands.',
    '2 x 6 of each letter',
)
H(
    'Side-lying external rotation',
    'Shoulder care',
    'Rotator cuff (infraspinatus, teres minor)',
    'The rotator cuff keeps the shoulder joint centred. Swimmers who train it get far less shoulder pain.',
    'Lie on your side, top elbow bent at 90 degrees and tucked to your side on a rolled towel, holding a 0.5 to 1.5 L water bottle.',
    ['Keep the elbow on your side.', 'Rotate the forearm up toward the ceiling.', 'Lower slowly over 3 s.', 'Do all reps, then swap sides.'],
    'Breathe out as you lift.',
    'Elbow glued to the side; slow lowering.',
    'Elbow lifting off the body. Rolling backward.',
    'Empty bottle.',
    'Fuller bottle.',
    '2 x 12 each arm',
)
H(
    'Wall slide',
    'Shoulder care',
    'Shoulder blades, upper back, posture',
    'Trains the shoulder blades to move well overhead, the position of every swim stroke.',
    'Stand with your back to a wall, feet a little forward, forearms on the wall in a goal-post shape.',
    [
        'Keep the lower back, head and forearms near the wall.',
        'Slide the arms up as far as you can without losing contact.',
        'Slide back down, squeezing the shoulder blades down.',
    ],
    'Breathe out as you slide up.',
    'Ribs down, slow.',
    'Arching the back. Shrugging.',
    'Smaller range.',
    'Lift the hands off the wall at the top.',
    '2 x 10',
)

# Shoulder-care routine and the updated warm-up routines
LB.WARMUPS.append(
    (
        'SHOULDER',
        'Shoulder care (6 min, at home on swim days)',
        [
            ('Scapular push-up', '2 x 10'),
            ('Prone Y-T-W raise', '2 x 6 each letter'),
            ('Side-lying external rotation', '2 x 12 each arm'),
            ('Wall slide', '2 x 10'),
            ('Sleeper stretch', '30 s each side'),
        ],
    )
)
LB.MOBILITY_ROUTINES.append(('SHOULDER', "Shoulder care (prevents swimmer's shoulder)", 'At home on the two harder swim days, morning or before you leave.'))

# Names used in session rows that point to a library entry with a different name
LINK = {
    'Towel shoulder pass-through (hold a towel wide, take it over the head and back)': 'Towel shoulder pass-through',
    'Doorway or wall chest stretch': 'Doorway chest stretch',
    'Doorway chest and shoulder stretch': 'Doorway chest stretch',
    'Thoracic rotation (side-lying open book)': 'Thoracic open book',
    'Streamline reach: stand tall, arms overhead, one hand on the other': 'Streamline reach',
    'Bodyweight squats': 'Bodyweight squat',
    'Lying hamstring stretch with a towel around the foot': 'Lying hamstring stretch with a towel',
    'Standing hamstring stretch (foot on a step)': 'Standing hamstring stretch',
    'Couch stretch (back foot up a wall)': 'Couch stretch',
    'Standing quad stretch (heel to glute)': 'Standing quad stretch',
    'Sleeper stretch (lying on your side)': 'Sleeper stretch',
    'Ankle rocks (knee to wall)': 'Ankle rocks',
    'Ankle bounces (pogo)': 'Ankle bounces',
    'Easy freestyle, any breathing pattern': 'Freestyle (front crawl)',
    'Non-stop freestyle': 'Freestyle (front crawl)',
    'Freestyle repeats': 'Freestyle (front crawl)',
    'Race-pace freestyle': 'Freestyle (front crawl)',
    'Freestyle, breathing every 3 strokes': 'Freestyle (front crawl)',
    'Steady freestyle intervals': 'Freestyle (front crawl)',
    'Endurance repeats': 'Freestyle (front crawl)',
    'Relaxed freestyle, any breathing pattern; stop at the wall when you need to': 'Freestyle (front crawl)',
    'Non-stop swim test: as far as you can without stopping, up to 1,500 m': 'Freestyle (front crawl)',
    '1,500 m NON-STOP TEST': 'Freestyle (front crawl)',
    'Easy backstroke': 'Backstroke',
    'Sighting: lift your eyes forward every 6 strokes': 'Sighting drill',
    'Kegels lying down, 10 min': 'Slow kegel holds',
    'Kegels lying down, 5 min': 'Slow kegel holds',
}


def link(name: str) -> str | None:
    """The library entry that explains a session row, or None."""
    n = LINK.get(name, name)
    return n if n in LB.L else None


# Drill pairs for the technique swim, by week (week number % len)
DRILL_PAIRS = [
    ('Streamline push and glide', 'Bubble breathing'),
    ('Kick on your side', '6-3-6 drill'),
    ('Catch-up freestyle', 'Fingertip drag'),
    ('Single-arm freestyle', 'Fist drill'),
    ('Sculling', 'Bilateral breathing ladder'),
    ('Kick on your back', 'Stroke-count lengths'),
]
SWIM_DRILLS = [n for pair in DRILL_PAIRS for n in pair] + ['Sighting drill']


def drill_row(name: str, light: bool):
    """(block, ex, sets, reps, rest, note) for a drill. light = easy or taper week."""
    dose = DOSE[name]
    sets, reps = 1, dose
    if ' x ' in dose:
        a, b = dose.split(' x ', 1)
        if a.strip().isdigit():
            sets, reps = int(a), b
            if light:
                sets = max(2, sets // 2)
    note = CUES[name]
    if '(' in reps:
        reps, extra = reps.split('(', 1)
        reps, note = reps.strip(), extra.rstrip(')').strip().capitalize() + '. ' + note
    return ('Drills', name, sets, reps, '20 s', note)


# ============================================================================ injury prevention
INJURY_PREVENTION = {
    'running': [
        (
            'Build slowly',
            'The long run grows by at most 1 to 1.5 km a week, total running by about 10% a week, and every 4th week is easier. Most running injuries come from doing too much too soon.',
        ),
        ('Easy means easy', 'About 80% of your running is at conversation pace. Walk breaks are allowed and planned.'),
        ('Never two hard days in a row', 'Intervals, long runs and leg strength are spread out so the same tissues get 48 h to recover.'),
        (
            'Short, quick steps',
            'Land with the foot under your hips, knee slightly bent, quiet feet. Taking about 5% more steps a minute than feels natural lowers the load on the knee. Do not overstride.',
        ),
        (
            'Flat, even ground',
            'Avoid steep downhills (they load the kneecap hard), uneven or very cambered roads and broken paths. Run on the flattest part of the road.',
        ),
        ('Shoes', 'Cushioned running shoes that fit, replaced every 600 to 800 km. Never race in new shoes; wear them on 2 to 3 runs first.'),
        ('Warm up and cool down', 'The 8-minute warm-up before every run and the 5-minute stretch afterwards are part of the session, not extras.'),
        ('Strength protects the knees', 'Three strength sessions a week, with glute, hip, quad, hamstring and calf work, are your main injury insurance.'),
        ('Heat and fluids', 'Run before 06:30, drink with a pinch of salt, and go by effort, not pace. Dehydration makes muscles cramp and form fall apart.'),
        ('Sleep and recovery', 'Under 6 hours of sleep, or a resting heart rate 7+ bpm above normal, means an easy day instead of a hard one.'),
        (
            'The pain rule',
            'Pain 0 to 2 out of 10 that does not grow during the run and is gone the next morning: carry on. 3 or more, or it changes how you run: stop, walk home, and swap the next run for a swim.',
        ),
    ],
    'swimming': [
        ('Build slowly', 'Add no more than about 10% (or 200 m) to your weekly swim distance. The shoulders adapt more slowly than the heart and lungs.'),
        ('Warm up the shoulders', 'Do the 6-minute pool-deck warm-up every time, and the shoulder-care routine at home on the two harder swim days.'),
        (
            'Hands in front of the shoulders',
            'Each hand enters the water in line with its shoulder, never across the middle of your head. Crossing over pinches the front of the shoulder.',
        ),
        (
            'Breathe to both sides',
            'Breathing every 3 strokes shares the work between both shoulders and keeps the stroke even. Breathing only to one side overloads one shoulder and the neck.',
        ),
        ('Rotate the body', 'Roll from hip to hip with each stroke. A flat body makes the shoulder do all the work.'),
        ('High, relaxed elbow', 'Lead the arm forward with a bent, relaxed elbow (fingertip drag). Big straight-arm swings strain the shoulder.'),
        ('Look down', 'Keep your face down and turn your head with the body to breathe. Lifting the head forward strains the neck and lower back.'),
        (
            'Protect the knee',
            'While knee care is on: freestyle and backstroke only, no breaststroke kick (its whip kick twists the inside of the knee), and push off the wall gently with both feet.',
        ),
        ('Kicking', 'Kick from the hips with relaxed ankles. Kick on your side rather than with a kickboard if your lower back aches.'),
        (
            'Cramp',
            'Calf or foot cramp in the water: stop at the wall, pull the toes toward you and stretch the calf. Drink well before you swim; you sweat in the pool too.',
        ),
        (
            'The pain rule',
            'A pinch at the front or top of the shoulder: switch to kick and backstroke for the rest of the session. If it is there on two swims in a row, see a physiotherapist.',
        ),
        ('Eyes, ears and skin', 'Goggles every time. Tilt the head to drain the ears and dry them after. Shower after the pool.'),
        ('Safety', 'Open water only with a buddy and a bright tow-float, close to shore, never at dusk. Never swim on the Thursday dry fast.'),
    ],
    'stop_signs': [
        'Swelling, locking or the knee giving way',
        'Pain at night or at rest, or pain that is worse the morning after',
        'Limping, or pain that changes how you run or swim',
        'Pain in the same place on two sessions in a row',
        'Not clearly better after 7 to 10 days of easier training',
    ],
    'stop_action': 'Any of these: stop that activity and see a physiotherapist or doctor. Keep training what does not hurt (swim if the knee hurts, run or bike if the shoulder hurts).',
}


def as_plan() -> dict:
    """What build.py exports to the app."""
    return dict(
        running=[dict(rule=a, detail=b) for a, b in INJURY_PREVENTION['running']],
        swimming=[dict(rule=a, detail=b) for a, b in INJURY_PREVENTION['swimming']],
        stop_signs=INJURY_PREVENTION['stop_signs'],
        stop_action=INJURY_PREVENTION['stop_action'],
    )
