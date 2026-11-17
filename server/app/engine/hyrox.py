"""HYROX: the eight stations, division standards and home substitutes for a Tanzania-based athlete."""

# name, race amount, gym equipment, home substitute, what it trains, technique cue
STATIONS = [
    (
        'SkiErg',
        '1,000 m',
        'SkiErg machine',
        'Jerrycan swings x 20 + 10 burpees per 250 m',
        'Lats, triceps, core, lungs',
        'Hinge from the hips and drive the handles down past the thighs; arms finish, legs do not squat deep.',
    ),
    (
        'Sled push',
        '50 m',
        'Sled with plates',
        'Bear crawl 2 x 12 m, or push a loaded backpack on a towel across tiles',
        'Quads, calves, drive',
        'Arms straight or slightly bent, low body angle, short powerful steps on the balls of the feet.',
    ),
    (
        'Sled pull',
        '50 m',
        'Sled with rope',
        'Hand-over-hand towel pull of a loaded jerrycan along the floor, then walk it back',
        'Back, grip, hamstrings',
        'Sit low, lean back, pull the rope hand over hand to the hip and keep the feet still in the box.',
    ),
    (
        'Burpee broad jumps',
        '80 m',
        'None',
        'The same, outside on grass or a clear yard',
        'Full body, power',
        'Chest to the floor, jump forward from both feet, land softly and step into the next one: rhythm beats speed.',
    ),
    (
        'Rowing',
        '1,000 m',
        'Rowing machine',
        'Backpack bent-over rows x 30 + squat thrusts x 15 per 250 m',
        'Legs, back, lungs',
        'Legs, body, arms on the way back; arms, body, legs on the way forward. Damper about 5 to 6.',
    ),
    (
        'Farmers carry',
        '200 m',
        'Two kettlebells',
        'Two full 20 L jerrycans, walk a loop of the compound',
        'Grip, traps, core',
        'Tall posture, shoulders down, short quick steps. Put them down before your grip fails, not after.',
    ),
    (
        'Sandbag lunges',
        '100 m',
        'Sandbag on the shoulders',
        'Backpack walking lunges (rice or sand bags in the backpack)',
        'Quads, glutes, endurance',
        'Back knee touches the floor each step, torso upright, steady breathing: one breath per step.',
    ),
    (
        'Wall balls',
        '100 reps',
        'Medicine ball and target',
        'Backpack thrusters, or a sand-filled ball thrown at a mark on a strong wall',
        'Legs, shoulders, lungs',
        'Full squat, drive up and release at the top in one movement. Break into sets of 10 to 15 from the start.',
    ),
]

# Singles divisions (season 2025/26 rulebook). Check the current HYROX rulebook before race day: standards can change each season.
DIVISIONS = {
    'Men Open': {
        'sled_push': '152 kg incl. sled',
        'sled_pull': '103 kg incl. sled',
        'farmers': '2 x 24 kg',
        'sandbag': '20 kg',
        'wall_ball': '6 kg to a 3.0 m target',
    },
    'Men Pro': {
        'sled_push': '202 kg incl. sled',
        'sled_pull': '153 kg incl. sled',
        'farmers': '2 x 32 kg',
        'sandbag': '30 kg',
        'wall_ball': '9 kg to a 3.0 m target',
    },
    'Women Open': {
        'sled_push': '102 kg incl. sled',
        'sled_pull': '78 kg incl. sled',
        'farmers': '2 x 16 kg',
        'sandbag': '10 kg',
        'wall_ball': '4 kg to a 2.7 m target',
    },
    'Women Pro': {
        'sled_push': '152 kg incl. sled',
        'sled_pull': '103 kg incl. sled',
        'farmers': '2 x 24 kg',
        'sandbag': '20 kg',
        'wall_ball': '6 kg to a 2.7 m target',
    },
}
FORMAT = 'Eight rounds of 1 km run + 1 station, in the order above. The clock never stops; transitions are part of your time.'

SKILLS = [
    ('Running under fatigue', 'Compromised runs: 1 km straight after a station, at an even effort. The first 200 m always feels worst.'),
    ('Grip strength', 'Farmer carries, towel-pull holds and dead hangs (a strong door frame or tree branch if safe). Chalk or a dry towel helps.'),
    ('Wall-ball technique', 'Squat depth, catch high, use the legs. Plan the breaks before the start: for example 25, 25, 20, 15, 15.'),
    ('Burpee efficiency', 'Step back instead of jumping when tired, keep the broad jump short and consistent, breathe on every landing.'),
    ('Transitions', 'Walk into each station with a plan, start straight away, and run out of the station: practise the change in every simulation.'),
    ('Sled-specific conditioning', 'Heavy bear crawls, backpack pushes on tiles and hill walks with the backpack until you can reach a gym with a sled.'),
]
GYM_NOTE = 'From the HYROX block (6 to 7 weeks out), try to visit a gym with a SkiErg, rower and sled once a week. Every session also has a home version.'
