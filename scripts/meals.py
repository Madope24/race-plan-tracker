"""Seven-day Tanzanian meal plan with computed calories and macros.

Food values are typical per-portion estimates (USDA FoodData Central-style values for the closest
equivalent food; local preparations vary by +/-15%). Totals are computed, never typed.
"""

# name: (kcal, protein g, carbs g, fat g) per 1 gram or per 1 unit, with a unit label
F = {  # per 100 g unless unit noted
    "ugali": (115, 2.5, 25, 0.5),            # stiff maize porridge (sembe), cooked
    "rice": (130, 2.7, 28, 0.3),             # white rice, cooked
    "sweet_potato": (86, 1.6, 20, 0.1),      # viazi vitamu, boiled
    "potato": (87, 1.9, 20, 0.1),            # Irish potato, boiled
    "plantain": (116, 0.8, 31, 0.2),         # ndizi (cooking banana), boiled
    "beans": (127, 8.7, 23, 0.5),            # maharage, cooked
    "lentils": (116, 9.0, 20, 0.4),          # dengu / ndengu (green gram) cooked
    "chicken": (165, 31, 0, 3.6),            # skinless, cooked
    "tilapia": (128, 26, 0, 2.7),            # sato, grilled/steamed
    "beef": (200, 28, 0, 9),                 # lean, stewed
    "dagaa": (330, 60, 0, 9),                # dried small fish
    "sardines": (208, 25, 0, 11),            # tinned, drained
    "greens": (25, 2.5, 4, 0.3),             # mchicha / spinach / cabbage, cooked without oil
    "kachumbari": (25, 1, 5, 0.2),
    "avocado": (160, 2, 9, 15),
    "groundnuts": (567, 26, 16, 49),
    "pumpkin_seeds": (559, 30, 11, 49),
    "oats": (380, 13, 66, 7),                # dry
    "uji_flour": (360, 9, 74, 3.5),          # millet/sorghum flour, dry
    "bread": (250, 10, 44, 3.5),             # brown bread
    "watermelon": (30, 0.6, 8, 0.2),
    "papaya": (43, 0.5, 11, 0.3),
    "mango": (60, 0.8, 15, 0.4),
    "pineapple": (50, 0.5, 13, 0.1),
    "orange": (47, 0.9, 12, 0.1),
    "tomato_onion": (25, 1, 5, 0.2),          # tomato-onion base for stews/eggs
}
U = {  # per unit
    "egg": (72, 6.3, 0.4, 4.8),              # 1 large egg
    "banana": (105, 1.3, 27, 0.4),           # 1 medium sweet banana (ndizi mbivu)
    "date": (23, 0.2, 6, 0),                 # 1 small date (tende)
    "milk_250": (150, 8, 12, 8),             # 250 ml whole milk
    "mtindi_250": (150, 8.5, 11, 8),         # 250 ml plain mtindi / maziwa lala
    "oil_tsp": (40, 0, 0, 4.5),              # 1 teaspoon cooking oil
    "sugar_tsp": (16, 0, 4, 0),
    "honey_tsp": (21, 0, 6, 0),
    "pb_tbsp": (95, 4, 3, 8),                # peanut butter, 1 tablespoon
    "soup_bowl": (60, 4, 6, 2),              # clear vegetable or bone broth, 300 ml
}


def item(name, qty):
    """qty: grams for F foods, units for U foods."""
    if name in F:
        k, p, c, f = F[name]
        r = qty / 100
    else:
        k, p, c, f = U[name]
        r = qty
    return (k * r, p * r, c * r, f * r)


LABEL = {
    "ugali": "ugali", "rice": "rice (cooked)", "sweet_potato": "viazi vitamu (boiled)", "potato": "Irish potato (boiled)",
    "plantain": "ndizi (boiled)", "beans": "maharage (cooked)", "lentils": "dengu (cooked)", "chicken": "chicken, skinless",
    "tilapia": "sato (tilapia)", "beef": "lean beef", "dagaa": "dagaa (dried)", "sardines": "sardines (tinned, drained)",
    "greens": "mchicha / greens", "kachumbari": "kachumbari", "avocado": "avocado", "groundnuts": "karanga (groundnuts)",
    "pumpkin_seeds": "pumpkin seeds", "oats": "oats (dry)", "uji_flour": "millet/sorghum uji flour", "bread": "brown bread",
    "watermelon": "watermelon", "papaya": "papai", "mango": "embe", "pineapple": "nanasi", "orange": "chungwa",
    "tomato_onion": "tomato + onion", "egg": "egg", "banana": "banana", "date": "date (tende)", "milk_250": "milk 250 ml",
    "mtindi_250": "mtindi 250 ml", "oil_tsp": "oil (tsp)", "sugar_tsp": "sugar (tsp)", "honey_tsp": "honey (tsp)",
    "pb_tbsp": "peanut butter (tbsp)", "soup_bowl": "clear soup, 300 ml bowl",
}


def fmt_item(name, qty):
    if name in F:
        return f"{LABEL[name]} {qty:g} g"
    q = int(qty) if float(qty).is_integer() else qty
    words = {
        "egg": ("egg", "eggs"), "banana": ("banana", "bananas"), "date": ("date (tende)", "dates (tende)"),
        "oil_tsp": ("tsp oil", "tsp oil"), "sugar_tsp": ("tsp sugar", "tsp sugar"), "honey_tsp": ("tsp honey", "tsp honey"),
        "pb_tbsp": ("tbsp peanut butter", "tbsp peanut butter"), "soup_bowl": ("bowl clear soup (300 ml)", "bowls clear soup (300 ml)"),
    }
    if name in words:
        one, many = words[name]
        return f"{q} {one if q == 1 else many}"
    if name == "milk_250":
        return f"milk {int(250 * qty)} ml"
    if name == "mtindi_250":
        return f"mtindi {int(250 * qty)} ml"
    return f"{LABEL[name]} × {q}"


# Each day: list of meals (time, meal name, [(food, qty)], note)
DAYS = {
    "Monday (fast day)": dict(target=(1800, 125, 190, 62), meals=[
        ("04:30", "Suhoor", [("oats", 50), ("milk_250", 1), ("egg", 3), ("banana", 1), ("groundnuts", 15)],
         "Oats cooked in the milk. Drink 600–800 ml water, sipped through the meal. Little salt."),
        ("18:50", "Break the fast", [("date", 3), ("soup_bowl", 1)], "500 ml water first, slowly over 15 minutes."),
        ("19:20", "Main meal", [("rice", 140), ("chicken", 170), ("beans", 100), ("greens", 150), ("kachumbari", 100), ("oil_tsp", 2)],
         "Then the easy walk and mobility at about 20:15."),
        ("21:15", "Evening snack", [("mtindi_250", 1), ("papaya", 100)], "Keep sipping water until bed."),
    ]),
    "Tuesday (run + strength B)": dict(target=(2050, 140, 230, 65), meals=[
        ("05:20", "Before the run", [("banana", 1)], "300–400 ml water."),
        ("07:30", "Breakfast", [("egg", 3), ("tomato_onion", 80), ("sweet_potato", 150), ("orange", 130)], "Eggs cooked with tomato and onion."),
        ("10:30", "Snack", [("mtindi_250", 1), ("groundnuts", 20)], ""),
        ("13:00", "Lunch", [("rice", 150), ("tilapia", 170), ("greens", 150), ("kachumbari", 100), ("oil_tsp", 2)], ""),
        ("16:30", "Before strength", [("banana", 1)], "Strength B at about 18:00."),
        ("19:30", "Dinner", [("ugali", 200), ("beef", 120), ("greens", 150), ("avocado", 30)], ""),
    ]),
    "Wednesday (strength A + swim)": dict(target=(2000, 140, 220, 65), meals=[
        ("07:00", "Breakfast", [("uji_flour", 40), ("milk_250", 1), ("egg", 2), ("banana", 1)], "Uji made with the milk, 1 tsp sugar at most."),
        ("10:30", "Snack", [("pumpkin_seeds", 15), ("mango", 100)], ""),
        ("13:00", "Lunch", [("rice", 140), ("chicken", 150), ("lentils", 150), ("greens", 150), ("oil_tsp", 2)], ""),
        ("16:00", "Before strength / swim", [("mtindi_250", 1)], "Strength A at about 16:45, swim at about 18:00."),
        ("19:30", "Dinner", [("sweet_potato", 200), ("sardines", 100), ("greens", 150), ("kachumbari", 100)], ""),
    ]),
    "Thursday (fast day)": dict(target=(1800, 125, 190, 62), meals=[
        ("04:30", "Suhoor", [("bread", 40), ("pb_tbsp", 1), ("egg", 3), ("mtindi_250", 1), ("banana", 1), ("groundnuts", 10)],
         "600–800 ml water sipped through the meal."),
        ("18:50", "Break the fast", [("date", 3), ("soup_bowl", 1)], "500 ml water first, slowly."),
        ("19:20", "Main meal", [("ugali", 220), ("tilapia", 200), ("beans", 100), ("greens", 150), ("oil_tsp", 2)],
         "A bit more starch tonight: tomorrow morning is a run."),
        ("21:15", "Evening snack", [("milk_250", 1), ("watermelon", 150)], "Keep sipping water until bed."),
    ]),
    "Friday (run)": dict(target=(2000, 140, 220, 65), meals=[
        ("05:20", "Before the run", [("banana", 1)], "400 ml water: you are coming off a dry fast."),
        ("07:30", "Breakfast", [("oats", 40), ("milk_250", 1), ("egg", 3), ("papaya", 100)], ""),
        ("10:30", "Snack", [("groundnuts", 15), ("orange", 130)], ""),
        ("13:00", "Lunch", [("plantain", 150), ("beef", 120), ("greens", 150), ("kachumbari", 100), ("oil_tsp", 1)], "Ndizi stew with beef."),
        ("16:30", "Snack", [("mtindi_250", 1)], ""),
        ("19:30", "Dinner", [("rice", 100), ("chicken", 120), ("lentils", 100), ("greens", 150), ("oil_tsp", 1)], "Carbs at dinner fuel tomorrow's long run."),
    ]),
    "Saturday (long run)": dict(target=(2300, 135, 310, 60), meals=[
        ("05:00", "Before the long run", [("bread", 60), ("pb_tbsp", 1), ("banana", 1)], "400–500 ml water."),
        ("during", "During runs over 90 minutes", [("date", 6)], "Counted here; see the fueling protocol for timing."),
        ("09:00", "Recovery breakfast", [("egg", 2), ("potato", 200), ("milk_250", 1), ("mango", 150), ("oil_tsp", 1)], "Within 60 minutes of finishing."),
        ("13:30", "Lunch", [("rice", 160), ("tilapia", 150), ("greens", 150), ("kachumbari", 100), ("oil_tsp", 1)], ""),
        ("16:30", "Snack", [("mtindi_250", 1), ("pineapple", 100)], ""),
        ("19:30", "Dinner", [("ugali", 150), ("chicken", 100), ("beans", 100), ("greens", 150)], ""),
    ]),
    "Sunday (swim + recovery)": dict(target=(1950, 140, 205, 65), meals=[
        ("07:30", "Breakfast", [("egg", 3), ("bread", 60), ("avocado", 50), ("tomato_onion", 80), ("orange", 100)], ""),
        ("11:00", "Snack", [("mtindi_250", 1), ("pumpkin_seeds", 10)], ""),
        ("13:30", "Lunch", [("rice", 120), ("beef", 120), ("beans", 120), ("greens", 150), ("kachumbari", 100), ("oil_tsp", 1)], ""),
        ("16:30", "Before the swim", [("banana", 1)], "Easy swim at about 17:30."),
        ("19:30", "Dinner", [("sweet_potato", 200), ("dagaa", 30), ("chicken", 80), ("greens", 150), ("oil_tsp", 1)], "Dagaa cooked with tomato and greens."),
    ]),
}


def day_totals(day):
    tot = [0, 0, 0, 0]
    rows = []
    for time, name, foods, note in day["meals"]:
        m = [0, 0, 0, 0]
        for f, q in foods:
            v = item(f, q)
            for i in range(4):
                m[i] += v[i]
        rows.append((time, name, ", ".join(fmt_item(f, q) for f, q in foods), [round(x) for x in m], note))
        for i in range(4):
            tot[i] += m[i]
    return rows, [round(x) for x in tot]


if __name__ == "__main__":
    for d, day in DAYS.items():
        rows, tot = day_totals(day)
        t = day["target"]
        print(f"{d}: {tot}  target {t}  diff kcal {tot[0]-t[0]:+} P {tot[1]-t[1]:+} C {tot[2]-t[2]:+} F {tot[3]-t[3]:+}")
