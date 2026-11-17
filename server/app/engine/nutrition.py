# Nutrition content in a Tanzanian context. Per-100 g values are rounded from standard food tables (USDA-style);
# local dishes vary with recipe, so treat them as good estimates for portion sizing.
FOODS = [
    # key, Swahili / local name, English, group, kcal, protein, carbs, fat, typical portion note
    ('wali', 'Wali (cooked)', 'White rice, cooked', 'Starch', 130, 2.7, 28, 0.3, '1 cup = 160 g'),
    ('ugali', 'Ugali (cooked)', 'Maize meal ugali', 'Starch', 118, 2.5, 25.5, 0.6, 'Fist-size piece = 150 g'),
    ('chapati', 'Chapati', 'Chapati', 'Starch', 310, 7.5, 45, 11, '1 chapati = 80 g'),
    ('ndizi_p', 'Ndizi mbichi (boiled)', 'Cooking banana / plantain', 'Starch', 116, 0.8, 31, 0.2, '1 finger = 100 g'),
    ('viazi_v', 'Viazi vitamu (boiled)', 'Sweet potato', 'Starch', 86, 1.6, 20, 0.1, '1 medium = 150 g'),
    ('mihogo', 'Mihogo (boiled)', 'Cassava', 'Starch', 160, 1.4, 38, 0.3, 'Small piece = 100 g'),
    ('viazi', 'Viazi mviringo (boiled)', 'Irish potato', 'Starch', 87, 1.9, 20, 0.1, '1 medium = 150 g'),
    ('oats', 'Oats (uji wa oats)', 'Rolled oats, dry', 'Starch', 389, 17, 66, 7, '4 tbsp = 40 g'),
    ('maharage', 'Maharage (cooked)', 'Kidney / red beans', 'Legume', 127, 8.7, 23, 0.5, '1 cup = 180 g'),
    ('dengu', 'Dengu (cooked)', 'Lentils', 'Legume', 116, 9, 20, 0.4, '1 cup = 200 g'),
    ('choroko', 'Choroko (cooked)', 'Green grams / mung beans', 'Legume', 105, 7, 19, 0.4, '1 cup = 200 g'),
    ('mayai', 'Mayai', 'Eggs (1 egg = 50 g)', 'Protein', 143, 12.6, 0.7, 9.5, '1 egg = 50 g'),
    ('dagaa', 'Dagaa (dried, cooked in stew)', 'Dried silver cyprinid / sardines', 'Protein', 330, 63, 0, 8, '2 handfuls dry = 50 g'),
    ('sato', 'Samaki sato (grilled)', 'Tilapia', 'Protein', 128, 26, 0, 2.7, 'Medium fish edible part = 250 g'),
    ('kuku', 'Kuku kifua (grilled/boiled)', 'Chicken breast, skinless', 'Protein', 165, 31, 0, 3.6, 'Palm-size = 150 g'),
    ('kuku_paja', 'Kuku paja (skinless)', 'Chicken thigh, skinless', 'Protein', 179, 24, 0, 8.5, '2 thighs = 200 g'),
    ('ng_ombe', "Nyama ya ng'ombe (lean, mishkaki style)", 'Lean beef, grilled', 'Protein', 200, 27, 0, 10, '5 mishkaki pieces = 150 g'),
    ('maini', 'Maini', 'Beef liver', 'Protein', 175, 27, 4, 5, 'Once a week, 150 g'),
    ('pweza', 'Pweza (boiled/grilled)', 'Octopus', 'Protein', 164, 30, 4, 2, '200 g'),
    ('sardini', 'Sardini za kopo (drained)', 'Tinned sardines', 'Protein', 208, 25, 0, 11, '1 tin drained = 90 g'),
    ('mtindi', 'Mtindi', 'Plain fermented milk / yoghurt', 'Dairy', 61, 3.3, 4.7, 3.3, '1 glass = 250 g'),
    ('maziwa', 'Maziwa fresh', 'Whole milk', 'Dairy', 61, 3.2, 4.8, 3.3, '1 glass = 250 g'),
    ('mchicha', 'Mchicha (cooked)', 'Amaranth greens', 'Vegetable', 21, 2.1, 4, 0.2, '1 plate side = 150 g'),
    ('sukuma', 'Sukuma wiki (cooked)', 'Kale / collards', 'Vegetable', 36, 2.5, 5.6, 0.5, '150 g'),
    ('kabichi', 'Kabichi (cooked)', 'Cabbage', 'Vegetable', 23, 1.3, 5.5, 0.1, '150 g'),
    ('kachumbari', 'Kachumbari', 'Tomato-onion salad', 'Vegetable', 20, 0.9, 4.5, 0.2, '1 side = 100 g'),
    ('tango', 'Tango', 'Cucumber', 'Vegetable', 15, 0.7, 3.6, 0.1, '1/2 = 150 g'),
    ('karoti', 'Karoti', 'Carrot', 'Vegetable', 41, 0.9, 10, 0.2, '1 = 80 g'),
    ('beet', 'Beetroot', 'Beetroot', 'Vegetable', 43, 1.6, 10, 0.2, '1 small = 100 g'),
    ('parachichi', 'Parachichi', 'Avocado', 'Fat', 160, 2, 8.5, 14.7, 'Half a medium = 80 g'),
    ('ndizi_m', 'Ndizi mbivu', 'Ripe banana', 'Fruit', 89, 1.1, 23, 0.3, '1 = 100 g'),
    ('embe', 'Embe', 'Mango', 'Fruit', 60, 0.8, 15, 0.4, '1 cup = 150 g'),
    ('nanasi', 'Nanasi', 'Pineapple', 'Fruit', 50, 0.5, 13, 0.1, '1 cup = 150 g'),
    ('tikiti', 'Tikiti maji', 'Watermelon', 'Fruit', 30, 0.6, 7.6, 0.2, '1 slice = 250 g'),
    ('papai', 'Papai', 'Papaya', 'Fruit', 43, 0.5, 11, 0.3, '1 cup = 150 g'),
    ('chungwa', 'Chungwa', 'Orange', 'Fruit', 47, 0.9, 12, 0.1, '1 = 130 g'),
    ('tende', 'Tende', 'Dates', 'Fruit', 282, 2.5, 75, 0.4, '3 dates = 25 g'),
    ('karanga', 'Karanga (roasted)', 'Peanuts', 'Nuts', 585, 24, 21, 50, 'Small handful = 25 g'),
    ('korosho', 'Korosho', 'Cashews', 'Nuts', 553, 18, 30, 44, 'Small handful = 25 g'),
    ('lozi', 'Lozi', 'Almonds', 'Nuts', 579, 21, 22, 50, 'Small handful = 25 g'),
    ('walnut', 'Walnuts', 'Walnuts', 'Nuts', 654, 15, 14, 65, '6 halves = 20 g'),
    ('chia', 'Chia seeds', 'Chia seeds', 'Nuts', 486, 17, 42, 31, '1 tbsp = 10 g'),
    ('mafuta', 'Mafuta ya alizeti', 'Sunflower oil', 'Fat', 884, 0, 0, 100, '1 tsp = 5 g'),
    ('nazi', 'Tui la nazi', 'Coconut milk', 'Fat', 197, 2, 3, 21, '3 tbsp = 50 g'),
    ('asali', 'Asali', 'Honey', 'Sugar', 304, 0.3, 82, 0, '1 tsp = 7 g'),
    ('kakao', 'Cocoa powder', 'Unsweetened cocoa', 'Other', 228, 20, 58, 14, '1 tbsp = 6 g'),
    ('tangawizi', 'Tangawizi', 'Fresh ginger', 'Other', 80, 1.8, 18, 0.8, 'Thumb = 10 g'),
    ('kunde', 'Kunde (cooked)', 'Cowpeas', 'Legume', 116, 7.7, 21, 0.5, '1 cup = 170 g'),
    ('dona', 'Ugali wa dona (cooked)', 'Whole-grain maize ugali', 'Starch', 120, 2.9, 25, 1.0, 'Fist-size piece = 150 g'),
    ('matembele', 'Matembele (cooked)', 'Sweet potato leaves', 'Vegetable', 32, 2.5, 6.4, 0.3, '150 g'),
    ('bamia', 'Bamia (cooked)', 'Okra', 'Vegetable', 22, 1.9, 4.5, 0.2, '100 g'),
    ('nyanya', 'Nyanya', 'Tomato', 'Vegetable', 18, 0.9, 3.9, 0.2, '1 = 100 g'),
    ('spinachi', 'Spinachi (cooked)', 'Spinach', 'Vegetable', 23, 3, 3.8, 0.3, '150 g'),
    ('passion', 'Pasheni', 'Passion fruit pulp', 'Fruit', 97, 2.2, 23, 0.7, '3 fruits = 60 g'),
    ('siagi_karanga', 'Siagi ya karanga', 'Peanut butter (no sugar added)', 'Nuts', 588, 25, 20, 50, '1 tbsp = 16 g'),
    ('soya', 'Maziwa ya soya (unsweetened)', 'Unsweetened soy milk', 'Dairy alt.', 33, 2.9, 1.7, 1.8, '1 glass = 250 g'),
    ('ufuta', 'Ufuta', 'Sesame seeds', 'Nuts', 573, 18, 23, 50, '1 tbsp = 9 g'),
    ('mbegu_maboga', 'Mbegu za maboga', 'Pumpkin seeds', 'Nuts', 559, 30, 11, 49, '1 tbsp = 10 g'),
    ('supu', 'Supu ya kuku (clear)', 'Clear chicken soup', 'Protein', 36, 4, 1, 1.5, '1 bowl = 300 g'),
]

# Approximate Dar es Salaam prices in TZS per kg of the food as eaten (cooked weight for starches and legumes), 2026.
# Edit them in Profile > Nutrition if your market differs. Used for meal costs and the weekly shopping list.
PRICE = {
    'wali': 1300,
    'ugali': 650,
    'chapati': 6250,
    'ndizi_p': 1500,
    'viazi_v': 2000,
    'mihogo': 1500,
    'viazi': 2000,
    'oats': 10000,
    'maharage': 1500,
    'dengu': 1900,
    'choroko': 1700,
    'mayai': 8000,
    'dagaa': 16000,
    'sato': 16000,
    'kuku': 14000,
    'kuku_paja': 10000,
    'ng_ombe': 14000,
    'maini': 12000,
    'pweza': 16000,
    'sardini': 33000,
    'mtindi': 3000,
    'maziwa': 2500,
    'mchicha': 2000,
    'sukuma': 2000,
    'kabichi': 1500,
    'kachumbari': 2500,
    'tango': 2000,
    'karoti': 2500,
    'beet': 3000,
    'parachichi': 3500,
    'ndizi_m': 2000,
    'embe': 2500,
    'nanasi': 2000,
    'tikiti': 1000,
    'papai': 2000,
    'chungwa': 2500,
    'tende': 10000,
    'karanga': 7000,
    'korosho': 25000,
    'lozi': 40000,
    'walnut': 50000,
    'chia': 30000,
    'mafuta': 6000,
    'nazi': 4000,
    'asali': 15000,
    'kakao': 30000,
    'tangawizi': 6000,
    'kunde': 1500,
    'dona': 700,
    'matembele': 2000,
    'bamia': 3000,
    'nyanya': 2500,
    'spinachi': 2500,
    'passion': 3000,
    'siagi_karanga': 15000,
    'soya': 6000,
    'ufuta': 8000,
    'mbegu_maboga': 25000,
    'supu': 5000,
}

# How to cook each food (joined into a meal's preparation steps)
PREP = {
    'wali': 'Wali: 1 cup rice to 2 cups water and a pinch of salt; weigh the cooked portion.',
    'ugali': 'Ugali: stir the unga into boiling water until firm; weigh or use a fist-size piece.',
    'dona': 'Ugali wa dona: as normal ugali, with whole-grain dona flour.',
    'chapati': 'Chapati: one only, cooked with a brushed (not poured) teaspoon of oil.',
    'ndizi_p': 'Ndizi: peel and boil 15 min with salt, or steam in the curry.',
    'viazi_v': 'Viazi vitamu: boil or steam with the skin on, 20 min.',
    'viazi': 'Viazi: boil with the skin on, 20 min.',
    'mihogo': 'Mihogo: boil until soft, 25 min; never eat it raw.',
    'maharage': 'Maharage: soak overnight, boil 60 to 90 min (batch-cook on Sunday), then simmer with nyanya and kitunguu.',
    'dengu': 'Dengu: rinse, simmer 25 min with nyanya, kitunguu, tangawizi and a pinch of curry powder.',
    'choroko': 'Choroko: soak 4 h, simmer 30 min with nyanya and kitunguu.',
    'kunde': 'Kunde: soak overnight, simmer 45 min.',
    'mayai': 'Mayai: boil 9 min (batch-boil 10 on Sunday) or scramble with a teaspoon of oil and nyanya.',
    'dagaa': 'Dagaa: rinse, soak 10 min, fry lightly with a teaspoon of oil, then simmer in nyanya and kitunguu.',
    'sato': 'Samaki: grill or bake with ndimu, kitunguu saumu, salt and pilipili; not deep-fried.',
    'kuku': 'Kuku: skinless, grill or boil, season with ndimu, kitunguu saumu and pilipili.',
    'kuku_paja': 'Kuku paja: skin off, grill or stew.',
    'ng_ombe': 'Nyama: lean cuts as mishkaki on the grill, or a stew with the fat skimmed.',
    'maini': 'Maini: slice and fry 3 min a side in a teaspoon of oil with kitunguu.',
    'pweza': 'Pweza: boil 40 min until tender, then grill or simmer in a light coconut curry.',
    'sardini': 'Sardini: drain the oil, eat with kachumbari.',
    'mchicha': 'Mchicha: wash, chop, cook 3 min with nyanya and kitunguu.',
    'sukuma': 'Sukuma: slice thin, cook 5 min with kitunguu.',
    'matembele': 'Matembele: cook 5 min with nyanya and a little tui la nazi.',
    'spinachi': 'Spinachi: wilt 2 min in the pan.',
    'kabichi': 'Kabichi: shred and stir-fry 5 min with karoti.',
    'bamia': 'Bamia: slice and simmer 8 min with nyanya.',
    'kachumbari': 'Kachumbari: nyanya, kitunguu, tango, pilipili hoho, ndimu and salt.',
    'parachichi': 'Parachichi: half on the side.',
    'supu': 'Supu: clear chicken broth, little oil, salt and ndimu.',
}


def meal_cost(items):
    return int(round(sum(PRICE.get(k, 0) * g / 1000 for k, g in items) / 50) * 50)


def meal_prep(keys):
    seen, out = set(), []
    for k in keys:
        if k in PREP and k not in seen:
            seen.add(k)
            out.append(PREP[k])
    return ' '.join(out) or 'No cooking: wash and cut the fruit, then blend or mix. Measure the nuts and seeds.'


# Meal plans: (day, meal, time, food key, grams). Two meals + an afternoon snack or smoothie. No breakfast.
# Saturday: first meal at 10:30 after the long run (the window moves earlier that day only).
SMOOTHIE_DAYS = ['Wed', 'Fri', 'Sat']  # at most one a day, not every day; never on fasting days


def plan(spec):
    out = []
    for day, meals in spec:
        for meal, time, items in meals:
            for k, g in items:
                out.append((day, meal, time, k, g))
    return out


CUT = plan(
    [
        (
            'Mon',
            [
                ('Lunch', '13:00', [('kuku', 200), ('mayai', 100), ('wali', 180), ('mchicha', 150), ('kachumbari', 100), ('mafuta', 5)]),
                ('Smoothie: Mtindi-embe recovery', '16:00', [('mtindi', 250), ('embe', 100), ('oats', 20), ('chia', 10)]),
                ('Dinner', '19:30', [('sato', 250), ('viazi_v', 220), ('sukuma', 150), ('parachichi', 50), ('mafuta', 5)]),
            ],
        ),
        (
            'Tue',
            [
                ('Lunch', '13:00', [('mayai', 200), ('maharage', 180), ('kachumbari', 120), ('ndizi_p', 150), ('mafuta', 5)]),
                ('Snack', '16:00', [('mtindi', 250), ('chungwa', 130), ('lozi', 15)]),
                ('Dinner', '19:30', [('kuku', 250), ('ugali', 200), ('mchicha', 200), ('mafuta', 5)]),
            ],
        ),
        (
            'Wed',
            [
                ('Lunch', '13:00', [('dagaa', 70), ('mayai', 100), ('dengu', 150), ('wali', 150), ('kabichi', 150), ('mafuta', 7)]),
                ('Smoothie: Green focus', '16:00', [('mtindi', 250), ('sukuma', 50), ('nanasi', 120), ('tango', 80), ('chia', 10), ('tangawizi', 5)]),
                ('Dinner', '19:30', [('ng_ombe', 220), ('viazi_v', 180), ('kachumbari', 150), ('parachichi', 60)]),
            ],
        ),
        (
            'Thu',
            [
                ('Lunch', '13:00', [('kuku', 200), ('choroko', 150), ('viazi_v', 220), ('tango', 100), ('karoti', 80), ('mafuta', 5)]),
                ('Snack', '16:00', [('mtindi', 200), ('ndizi_m', 100), ('karanga', 25)]),
                ('Dinner', '19:30', [('sato', 250), ('ugali', 220), ('mchicha', 150), ('mafuta', 5)]),
            ],
        ),
        (
            'Fri',
            [
                ('Lunch', '13:00', [('sardini', 90), ('mayai', 150), ('maharage', 120), ('viazi', 200), ('kachumbari', 120)]),
                ('Smoothie: Beet booster', '16:00', [('beet', 100), ('chungwa', 130), ('mtindi', 250), ('tangawizi', 5), ('chia', 10)]),
                ('Dinner', '19:30', [('kuku', 250), ('wali', 170), ('sukuma', 150), ('parachichi', 50), ('mafuta', 5)]),
            ],
        ),
        (
            'Sat',
            [
                ('Brunch after the long run', '10:30', [('mayai', 200), ('dagaa', 30), ('maharage', 150), ('ndizi_p', 150), ('kachumbari', 100)]),
                ('Smoothie: Long-run refuel', '15:00', [('maziwa', 250), ('ndizi_m', 100), ('tende', 25), ('karanga', 15), ('oats', 20)]),
                ('Dinner', '19:30', [('pweza', 250), ('wali', 160), ('mchicha', 150), ('nazi', 30)]),
            ],
        ),
        (
            'Sun',
            [
                ('Lunch', '13:00', [('maini', 150), ('mayai', 100), ('viazi_v', 220), ('kabichi', 150), ('mafuta', 5)]),
                ('Snack', '16:00', [('mtindi', 250), ('papai', 150), ('walnut', 15)]),
                ('Dinner', '19:30', [('sato', 300), ('dengu', 120), ('sukuma', 150), ('parachichi', 50)]),
            ],
        ),
    ]
)

FUEL = plan(
    [
        (
            'Mon',
            [
                ('Lunch', '13:00', [('kuku', 220), ('mayai', 100), ('wali', 250), ('mchicha', 150), ('kachumbari', 100), ('mafuta', 7)]),
                ('Smoothie: Mtindi-embe recovery', '16:00', [('mtindi', 300), ('embe', 150), ('oats', 30), ('chia', 10)]),
                ('Dinner', '19:30', [('sato', 250), ('viazi_v', 300), ('sukuma', 150), ('parachichi', 60), ('mafuta', 5)]),
            ],
        ),
        (
            'Tue',
            [
                ('Lunch', '13:00', [('mayai', 200), ('maharage', 220), ('kachumbari', 120), ('ndizi_p', 250), ('mafuta', 5)]),
                ('Snack', '16:00', [('mtindi', 250), ('ndizi_m', 100), ('lozi', 25)]),
                ('Dinner', '19:30', [('kuku', 250), ('ugali', 280), ('mchicha', 200), ('mafuta', 5)]),
            ],
        ),
        (
            'Wed',
            [
                ('Lunch', '13:00', [('dagaa', 70), ('mayai', 100), ('dengu', 200), ('wali', 220), ('kabichi', 150), ('mafuta', 7)]),
                (
                    'Smoothie: Green focus',
                    '16:00',
                    [('mtindi', 300), ('sukuma', 50), ('nanasi', 150), ('tango', 80), ('chia', 10), ('tangawizi', 5), ('asali', 7)],
                ),
                ('Dinner', '19:30', [('ng_ombe', 220), ('viazi_v', 280), ('kachumbari', 150), ('parachichi', 60)]),
            ],
        ),
        (
            'Thu',
            [
                ('Lunch', '13:00', [('kuku', 220), ('choroko', 200), ('chapati', 80), ('tango', 100), ('karoti', 80)]),
                ('Snack', '16:00', [('mtindi', 250), ('ndizi_m', 100), ('karanga', 25)]),
                ('Dinner', '19:30', [('sato', 250), ('ugali', 280), ('mchicha', 150), ('mafuta', 5)]),
            ],
        ),
        (
            'Fri',
            [
                ('Lunch', '13:00', [('sardini', 90), ('mayai', 150), ('maharage', 150), ('viazi', 300), ('kachumbari', 120)]),
                ('Smoothie: Beet booster', '16:00', [('beet', 100), ('chungwa', 130), ('mtindi', 250), ('tangawizi', 5), ('chia', 10), ('ndizi_m', 80)]),
                ('Dinner', '19:30', [('kuku', 250), ('wali', 250), ('sukuma', 150), ('parachichi', 60), ('mafuta', 5)]),
            ],
        ),
        (
            'Sat',
            [
                ('Brunch after the long session', '10:30', [('mayai', 200), ('dagaa', 30), ('maharage', 200), ('ndizi_p', 250), ('kachumbari', 100)]),
                ('Smoothie: Long-run refuel', '15:00', [('maziwa', 300), ('ndizi_m', 120), ('tende', 30), ('karanga', 20), ('oats', 30)]),
                ('Dinner', '19:30', [('pweza', 250), ('wali', 250), ('mchicha', 150), ('nazi', 40)]),
            ],
        ),
        (
            'Sun',
            [
                ('Lunch', '13:00', [('maini', 150), ('mayai', 100), ('viazi_v', 300), ('kabichi', 150), ('mafuta', 5)]),
                ('Snack', '16:00', [('mtindi', 250), ('papai', 200), ('walnut', 20)]),
                ('Dinner', '19:30', [('sato', 300), ('dengu', 180), ('sukuma', 150), ('parachichi', 60), ('mafuta', 5)]),
            ],
        ),
    ]
)

# Dry-fast days (Mon and Thu): nothing until the fast breaks at about 18:50, then two meals.
FAST = plan(
    [
        (
            d,
            [
                ('Break the fast', '18:50', [('tende', 25), ('supu', 300), ('tikiti', 250), ('mtindi', 200)]),
                ('Dinner', '20:00', [('kuku', 220), ('mayai', 100), ('wali', 160), ('mchicha', 150), ('kachumbari', 100), ('parachichi', 50), ('mafuta', 5)]),
            ],
        )
        for d in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ]
)
# Ramadan: iftar, a protein dinner, and suhoor before dawn.
RAMADAN = plan(
    [
        (
            d,
            [
                ('Iftar', '18:40', [('tende', 25), ('supu', 300), ('tikiti', 250), ('ndizi_m', 100)]),
                ('Dinner', '20:00', [('sato' if i % 2 else 'kuku', 250), ('dengu', 150), ('wali', 180), ('sukuma', 150), ('parachichi', 50), ('mafuta', 5)]),
                ('Suhoor', '04:30', [('oats', 60), ('maziwa', 300), ('mayai', 150), ('ndizi_m', 100), ('karanga', 20)]),
            ],
        )
        for i, d in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    ]
)

SMOOTHIES = [
    (
        'SM7',
        'Banana oats and peanut',
        'Before a long session if you have 90 min to digest, or after strength',
        'Easy carbs plus some protein and fat. Not low-calorie.',
        [('ndizi_m', 120), ('oats', 30), ('siagi_karanga', 16), ('mtindi', 150)],
        'Blend with 150 ml water and ice. Thick: add more water.',
    ),
    (
        'SM8',
        'Avocado banana soy',
        'Rest days or a light dinner partner',
        'Healthy fats and potassium. High in calories: keep the avocado to half.',
        [('parachichi', 70), ('ndizi_m', 100), ('soya', 250)],
        'Unsweetened soy milk. Blend 45 s with ice.',
    ),
    (
        'SM9',
        'Mango passion protein',
        'After a hot session (it is not a low-sugar drink)',
        'Carbs to refuel plus mtindi protein.',
        [('embe', 150), ('passion', 60), ('mtindi', 250), ('chia', 10)],
        'Sieve the passion seeds if you prefer.',
    ),
    (
        'SM10',
        'Banana cocoa groundnut',
        'After a long run or HYROX session',
        'Carbs and protein; cocoa for taste and magnesium.',
        [('ndizi_m', 120), ('kakao', 6), ('karanga', 20), ('maziwa', 250)],
        'Unsweetened cocoa only. Blend the karanga first.',
    ),
    (
        'SM11',
        'Pineapple ginger soy',
        'Hot afternoons',
        'Light and refreshing, still contains natural sugar.',
        [('nanasi', 150), ('tangawizi', 5), ('soya', 250), ('chia', 10)],
        'Fresh ginger, peeled. Add ice.',
    ),
    (
        'SM1',
        'Long-run refuel',
        'Sat after the long run or brick (15:00)',
        'Carbs + protein to refill after the longest session',
        [('maziwa', 250), ('ndizi_m', 100), ('tende', 25), ('karanga', 15), ('oats', 20)],
        'Blend the oats dry first, add everything, 45 s. Pinch of salt in the heat.',
    ),
    (
        'SM2',
        'Mtindi-embe recovery',
        'Mon 16:00, between the morning strength session and the evening swim',
        'Protein from mtindi, slow carbs from oats, omega-3 fats from chia',
        [('mtindi', 250), ('embe', 100), ('oats', 20), ('chia', 10)],
        'Soak chia in the mtindi 5 min, then blend. Swap embe for papai when mango is out of season.',
    ),
    (
        'SM3',
        'Beet booster',
        'Fri 16:00, after the morning strength session',
        'Beetroot nitrate supports blood flow and endurance (best 2 to 3 h before effort)',
        [('beet', 100), ('chungwa', 130), ('mtindi', 200), ('tangawizi', 5), ('chia', 10)],
        'Peel and chop raw beetroot small; blend 60 s. It colours everything red; that is normal.',
    ),
    (
        'SM4',
        'Green focus',
        'Wed 16:00 (desk afternoon)',
        'Light, high fibre, keeps you full on fewer calories',
        [('mtindi', 250), ('sukuma', 50), ('nanasi', 120), ('tango', 80), ('chia', 10), ('tangawizi', 5)],
        'Raw sukuma, stems removed. Blend greens with the mtindi first, then the fruit.',
    ),
    (
        'SM5',
        'Cocoa-nut strength',
        'Swap it in for the Mtindi-embe recovery any week',
        'Healthy fats from nuts, magnesium from cocoa',
        [('maziwa', 250), ('ndizi_m', 100), ('kakao', 6), ('korosho', 15), ('walnut', 10)],
        'Unsweetened cocoa only (not drinking chocolate). Blend 45 s.',
    ),
    (
        'SM6',
        'Tikiti hydrator',
        'Swap-in on very hot days after a long session',
        'Fluid, potassium and a little salt to replace sweat',
        [('tikiti', 300), ('chungwa', 130), ('mtindi', 150), ('tangawizi', 5)],
        'Add a pinch of salt and ice. Drink slowly.',
    ),
]

# name, purpose, evidence, studied dose range, timing, side effects, contraindications / medical notes, in your plan?
SUPPLEMENTS = [
    (
        'Creatine monohydrate',
        'More strength and repeat power, better recovery between hard sets.',
        'Strong',
        '3 to 5 g a day (studied range; no loading needed)',
        'Any time, daily; in water or the smoothie',
        'Water weight of 1 to 2 kg in the first weeks; stomach upset if taken in big doses at once',
        'Kidney disease or kidney medicines: ask a doctor first. Drink 3+ L of water a day.',
        True,
    ),
    (
        'Omega-3 (EPA + DHA)',
        'Heart health, joints, may help recovery.',
        'Moderate',
        '1 to 2 g EPA + DHA a day',
        'With a meal containing fat',
        'Fishy burps, loose stools',
        'Blood thinners or a bleeding disorder: ask a doctor. Oily fish (dagaa, sardini) days can replace it.',
        True,
    ),
    (
        'Vitamin D3',
        'Bone, muscle and immune health when you are low.',
        'Strong if deficient, weak otherwise',
        '1,000 to 2,000 IU a day; do not exceed 4,000 IU without a doctor',
        'With your main meal',
        'Very rare at these doses; too much raises blood calcium',
        'Best: test 25-OH vitamin D first. Kidney stones or high calcium: doctor first.',
        True,
    ),
    (
        'Vitamin K2 (MK-7)',
        'Often paired with vitamin D for calcium handling in bones.',
        'Limited',
        '90 to 180 mcg a day',
        'With vitamin D',
        'Rare',
        'Do NOT take with warfarin or other vitamin K antagonist blood thinners.',
        False,
    ),
    (
        'Magnesium (glycinate)',
        'Sleep quality, cramps; you lose some in sweat.',
        'Moderate if low',
        '200 to 400 mg elemental magnesium',
        'Evening, about 21:00',
        'Loose stools (more with citrate or oxide forms)',
        'Kidney disease: ask a doctor first.',
        True,
    ),
    (
        'Zinc',
        'Immune function; only helps if your diet is low.',
        'Only if deficient',
        '8 to 15 mg (upper limit 40 mg a day from all sources)',
        'With dinner, not with iron',
        'Nausea on an empty stomach; long-term high doses lower copper',
        'Dagaa, maini, nyama and seeds already supply it. Not a testosterone booster.',
        False,
    ),
    (
        'Electrolytes / ORS',
        'Prevents cramping, headaches and the late-session fade in the heat.',
        'Strong in hot weather',
        'About 300 to 800 mg sodium per hour of sweaty exercise; 1 ORS sachet per 500 ml to 1 L',
        'Sessions over 60 min, long hot days, after breaking a dry fast if you trained the day before',
        'Bloating if too concentrated',
        'High blood pressure or heart or kidney disease: ask a doctor about sodium.',
        True,
    ),
    (
        'Protein powder (non-whey)',
        'Convenience when food protein falls short.',
        'Strong for total protein, not better than food',
        '20 to 30 g per serving',
        'After training if a meal is more than 2 h away',
        'Bloating with some types',
        'You chose no whey. Food covers your target, so it is not in your plan; a plant protein is an option if you ever need it.',
        False,
    ),
    (
        'Caffeine (kahawa / chai)',
        'Better effort in intervals and races.',
        'Strong',
        '1 to 3 mg per kg (about 100 to 200 mg, 1 to 2 cups coffee)',
        '45 min before hard sessions; nothing after 12:00',
        'Poor sleep, jitters, stomach upset',
        'High blood pressure, anxiety or palpitations: keep it low.',
        True,
    ),
]
SUPPLEMENT_NOTE = 'Ranges are the doses studied in research, not prescriptions. Start low, one new supplement at a time, and check with a doctor or pharmacist if you take any medicine or have a medical condition.'
HORMONE_HEALTH = [
    ('Eat enough', 'Long, deep deficits and under-fuelling lower testosterone. After 1 Jan the deficit is small, and training days get more carbs.'),
    ('Dietary fat', 'At least 0.8 g fat per kg a day (about 65 g): avocado, karanga, ufuta, eggs, fish.'),
    ('Protein', 'About 160 g a day spread over your meals.'),
    ('Resistance training', 'Progressive strength training three times a week.'),
    ('Sleep', '7 to 9 hours; poor sleep is one of the fastest ways to lower testosterone.'),
    ('Stress and recovery', 'Easy weeks, rest days and not stacking hard sessions.'),
    ('Endurance balance', 'Very high endurance volume with too little food suppresses hormones: the plan raises volume gradually and fuels long sessions.'),
    (
        'What the app will not do',
        'No testosterone boosters, no hormone products. Foods, kegels and supplements do not guarantee higher testosterone. If you have symptoms, see a doctor for a blood test.',
    ),
]
NOT_NEEDED = 'Not in the plan: protein powder (your protein comes from mayai, dagaa, samaki, kuku, maharage and mtindi), fat burners, and "testosterone booster" blends. They add cost without reliable benefit.'

SLEEP = [
    ('05:30', 'Wake at the same time every day, weekends included', 'A fixed wake time is the strongest anchor for your body clock.'),
    ('05:35', 'Toilet, weigh, glass of water with a pinch of salt', 'Same conditions every morning makes the weight trend honest.'),
    ('05:45', 'Outdoor light 5 to 10 min (the morning run counts)', 'Morning daylight sets your sleep timer for tonight. No sunglasses for this.'),
    ('07:30 to 12:00', 'Caffeine window', 'After 12:00 caffeine is still in your blood at 22:00.'),
    ('13:00 to 20:00', 'Eating window (Saturday from 10:30)', 'Last big meal at least 2 h before bed so digestion does not disturb sleep.'),
    ('14:00 (optional)', '10 to 20 min NSDR / power nap', 'On two-session days. Longer naps make night sleep worse.'),
    ('20:30', 'Screens dimmed; warm lights only', 'Bright overhead light and phone glare delay melatonin.'),
    ('21:00', "Magnesium; shower; prepare tomorrow's kit", 'A cool shower helps your core temperature drop, which triggers sleep.'),
    (
        '21:30',
        'Phone on charge outside the bedroom; 5 min physiological sighs (two inhales through the nose, one long exhale)',
        'Calms the nervous system fast.',
    ),
    ('22:00', 'Lights out. Target 7.5 h asleep, 8 h in bed', 'Sleep is when fat loss, muscle repair and hormone balance happen.'),
]
BEDROOM = [
    ('Cool', 'Fan on and aimed at you, window open with a mosquito net or screens. Ideal room around 24 to 26 C if you have AC.'),
    ('Dark', 'Blackout curtain or a cheap eye mask. Cover standby lights with tape.'),
    ('Quiet', 'Foam ear plugs for dogs, bajaji, music or the mosque/church loudspeaker at dawn.'),
    ('Safe', 'Treated mosquito net every night. Malaria costs 1 to 3 weeks of training.'),
    ('Bed = sleep', 'No work or scrolling in bed. If awake 20 min, get up, read in dim light, return when sleepy.'),
]

EATING_RULES = [
    (
        'Plate rule',
        'Half the plate vegetables (mchicha, sukuma, kabichi, kachumbari), a quarter protein (palm-size or bigger), a quarter starch (fist-size wali, ugali, ndizi or viazi vitamu).',
    ),
    ('Protein every meal', '40 to 60 g protein per meal: e.g. 200 g kuku, 250 g samaki, 3 mayai + 1 cup maharage, or 50 g dagaa + 1 cup dengu.'),
    (
        'No breakfast',
        'Your window is 13:00 to 20:00. Water, black coffee or chai without sugar in the morning. Saturday: brunch at 10:30 after the long session.',
    ),
    ('Drinks', 'No soda, juice boxes, energy drinks or sugared chai. Fresh juice counts as sugar: eat the fruit instead. Water 3 to 4 L a day.'),
    ('Oil', 'Measure: 1 tsp (5 g) per person per dish. Most extra calories in Tanzanian home cooking come from oil.'),
    ('Fried foods', 'Chips mayai, maandazi, sambusa, vitumbua and chips: once a week at most, and count them.'),
    (
        'Street food that works',
        'Mishkaki (no chips), grilled samaki, ndizi choma, mahindi choma, fruit from the market, supu ya pweza or kuku (go easy on the fat on top).',
    ),
    ('Ugali and wali', 'Weigh them for the first 2 weeks so your eye learns what 150 g looks like. Seconds are where the deficit disappears.'),
    ('Alcohol', 'Zero for the cut to 1 Jan. After that, at most 2 drinks a week, never the night before a key session.'),
    ('Social meals', 'Eat protein and vegetables first, one small starch, no second plate. Weddings and sendoffs: plan them into the week.'),
    ('Weigh your food', 'Use a kitchen scale for the first 2 weeks. After that, use the portion notes in the Foods sheet.'),
    ('Batch cook Sunday', 'Boil maharage and dengu, 10 eggs, cook dagaa, chop kachumbari. Plans fail on busy weekdays when nothing is ready.'),
]

SWAPS = [
    ('Chai with 3 sugars', 'Chai with milk, no sugar, cinnamon or tangawizi for flavour', 'About 50 kcal per cup'),
    ('Soda 500 ml', 'Water with lime and ice, or sparkling water', 'About 210 kcal'),
    ('Chips mayai', '3 boiled eggs + kachumbari + 1 ndizi choma', 'About 500 kcal'),
    ('2 maandazi', 'Banana + small handful of karanga', 'About 250 kcal'),
    ('2 chapati with dinner', '1 fist of wali or ugali', 'About 300 kcal'),
    ('Pilau with lots of oil', 'Wali + beans + kachumbari, oil measured', 'About 250 kcal'),
    ('Fried fish', 'Grilled samaki', 'About 200 kcal'),
    ('Peanut butter by the spoon', '20 g measured karanga, korosho, lozi or walnuts', 'About 150 kcal'),
]

SHOPPING = [
    ('Soko / market', 'Mchicha, sukuma wiki, kabichi', '6 bunches', 3000),
    ('Soko / market', 'Nyanya, vitunguu, tango, karoti (for kachumbari)', '3 kg total', 6000),
    ('Soko / market', 'Viazi vitamu', '2 kg', 4000),
    ('Soko / market', 'Ndizi mbichi + ndizi mbivu', '1 bunch each', 6000),
    ('Soko / market', 'Parachichi', '4', 2000),
    ('Soko / market', 'Fruit for smoothies: embe, nanasi, chungwa, papai, beetroot', 'as in the meal plan', 8000),
    ('Soko / market', 'Tangawizi, ndimu', 'small', 1500),
    ('Fish / butcher', 'Samaki sato', '3 fish (about 750 g edible)', 18000),
    ('Fish / butcher', 'Dagaa (dried)', '250 g', 4000),
    ('Fish / butcher', 'Pweza', '400 g', 8000),
    ('Fish / butcher', 'Kuku (breast or thighs)', '1.5 kg', 15000),
    ('Fish / butcher', "Nyama ya ng'ombe (lean) + maini", '200 g each', 6000),
    ('Supermarket / duka', 'Mayai', '1 tray (30)', 11000),
    ('Supermarket / duka', 'Mtindi', '3 L', 9000),
    ('Supermarket / duka', 'Maziwa fresh', '1 L', 2500),
    ('Supermarket / duka', 'Maharage, dengu, choroko (dry)', '1.5 kg total', 6000),
    ('Supermarket / duka', 'Wali (rice), unga wa ugali, oats', 'as needed', 6000),
    ('Supermarket / duka', 'Sardini za kopo', '2 tins', 6000),
    ('Supermarket / duka', 'Nuts: karanga, korosho, lozi, walnuts; chia', 'small packs', 10000),
    ('Supermarket / duka', 'Sunflower oil, tui la nazi, salt', 'as needed', 3000),
    ('Pharmacy (monthly)', 'Creatine, vitamin D3, omega-3, magnesium; ORS sachets', '1 month', 0),
]


SPORTS_NUTRITION = [
    (
        'Pre-workout',
        'Morning runs on an empty stomach are fine up to 60 min easy. For longer or hard sessions eat 30 to 60 g carbs 60 to 90 min before (a banana and 2 dates), or the evening meal does the job.',
    ),
    (
        'Post-workout',
        'Your next meal is the recovery meal: 40 to 60 g protein plus a fist or two of starch within about 2 h. On a two-session day, the smoothie (if it is a smoothie day) or mtindi bridges the gap.',
    ),
    ('Protein distribution', 'Two or three meals of 40 to 60 g protein each (no breakfast). On fasting days get 120 g or more in the two evening meals.'),
    (
        'Carbohydrate timing',
        'More starch on the day of and the day after long or hard sessions; less on rest and fasting days. The calorie target already moves with training.',
    ),
    ('Long-run fuelling', 'Over 75 min: 30 to 45 g carbs per hour (2 dates = about 36 g), water every 20 min, salt or ORS.'),
    (
        'Long-ride fuelling',
        'From the first hour: 30 g/h, rising to 60 g/h by June and practising 60 to 90 g/h in July. Mix of drink and food: ndizi, dates, homemade drink.',
    ),
    ('Race-day nutrition', 'Familiar breakfast 2 to 3 h before; nothing new on race day; the exact products you practised. Never dry-fast on a race day.'),
    ('Electrolytes', 'Dar sweat rates are high: 300 to 800 mg sodium per hour in long sessions. ORS sachets or a pinch of salt and a squeeze of lime.'),
    ('Hydration', '3 to 4 L a day on training days; urine pale yellow. After a dry fast, drink 500 ml to 1 L slowly before eating a big meal.'),
]
# Gut training before the 70.3: carbs per hour practised on long sessions, by month
FUEL_PROGRESSION = [
    ('Nov to Feb (long runs over 75 min)', '30 to 45 g per hour'),
    ('Mar to Apr (first long rides)', '30 to 45 g per hour'),
    ('May to Jun (rides 2 to 2.5 h)', '45 to 60 g per hour'),
    ('Jul to Aug (rides 2.5 to 3.5 h, race rehearsal)', '60 to 90 g per hour'),
]
