"""
Feed formula generation algorithm.
Calculates grain mixes based on purpose and target protein.
"""

PURPOSE_TARGETS = {
    'racing':      {'protein': 14.0, 'fat': 4.0,  'energy': 'high'},
    'breeding':    {'protein': 16.0, 'fat': 5.0,  'energy': 'high'},
    'molting':     {'protein': 18.0, 'fat': 4.5,  'energy': 'medium'},
    'maintenance': {'protein': 12.0, 'fat': 3.0,  'energy': 'low'},
    'young':       {'protein': 17.0, 'fat': 4.5,  'energy': 'high'},
}

# ── Nutritional data per 100g (approximate values) ──────────────────────────
GRAIN_NUTRITION = {
    # Cereals
    'Maize (Corn)':     {'protein': 8.5,  'fat': 3.8,  'carbs': 74.0, 'fiber': 2.7,  'cal': 365, 'category': 'cereal'},
    'Wheat':            {'protein': 13.2, 'fat': 2.5,  'carbs': 70.0, 'fiber': 2.7,  'cal': 340, 'category': 'cereal'},
    'Barley':           {'protein': 12.5, 'fat': 2.1,  'carbs': 73.0, 'fiber': 3.9,  'cal': 354, 'category': 'cereal'},
    'Sorghum':          {'protein': 10.6, 'fat': 3.3,  'carbs': 75.0, 'fiber': 1.8,  'cal': 329, 'category': 'cereal'},
    'Millet':           {'protein': 11.0, 'fat': 4.2,  'carbs': 73.0, 'fiber': 1.3,  'cal': 378, 'category': 'cereal'},
    'Rice (Broken)':    {'protein': 7.5,  'fat': 0.5,  'carbs': 80.0, 'fiber': 0.4,  'cal': 360, 'category': 'cereal'},
    'Oats':             {'protein': 16.9, 'fat': 6.9,  'carbs': 66.0, 'fiber': 10.6, 'cal': 389, 'category': 'cereal'},
    'Buckwheat':        {'protein': 13.3, 'fat': 3.4,  'carbs': 72.0, 'fiber': 10.0, 'cal': 343, 'category': 'cereal'},
    'Canary Seed':      {'protein': 18.0, 'fat': 7.0,  'carbs': 55.0, 'fiber': 6.5,  'cal': 360, 'category': 'cereal'},

    # Legumes
    'Peas':             {'protein': 23.0, 'fat': 1.2,  'carbs': 60.0, 'fiber': 8.3,  'cal': 310, 'category': 'legume'},
    'Lentils':          {'protein': 25.0, 'fat': 1.0,  'carbs': 60.0, 'fiber': 7.9,  'cal': 352, 'category': 'legume'},
    'Chickpeas':        {'protein': 20.5, 'fat': 6.0,  'carbs': 61.0, 'fiber': 12.2, 'cal': 378, 'category': 'legume'},
    'Cowpea':           {'protein': 23.5, 'fat': 1.3,  'carbs': 57.0, 'fiber': 6.3,  'cal': 336, 'category': 'legume'},
    'Gram (Chana)':     {'protein': 22.5, 'fat': 5.0,  'carbs': 58.0, 'fiber': 8.0,  'cal': 364, 'category': 'legume'},
    'Mung Beans':       {'protein': 24.0, 'fat': 1.2,  'carbs': 63.0, 'fiber': 7.6,  'cal': 347, 'category': 'legume'},
    'Vetch':            {'protein': 26.0, 'fat': 1.5,  'carbs': 55.0, 'fiber': 7.0,  'cal': 340, 'category': 'legume'},

    # Seeds & Oilseeds
    'Sunflower Seed':   {'protein': 20.8, 'fat': 51.5, 'carbs': 20.0, 'fiber': 8.6,  'cal': 584, 'category': 'seed'},
    'Safflower Seed':   {'protein': 16.2, 'fat': 38.0, 'carbs': 34.0, 'fiber': 14.0, 'cal': 517, 'category': 'seed'},
    'Flaxseed':         {'protein': 18.3, 'fat': 42.2, 'carbs': 29.0, 'fiber': 27.3, 'cal': 534, 'category': 'seed'},
    'Sesame Seed':      {'protein': 17.7, 'fat': 49.7, 'carbs': 23.0, 'fiber': 11.8, 'cal': 573, 'category': 'seed'},
    'Mustard Seed':     {'protein': 26.1, 'fat': 36.2, 'carbs': 29.0, 'fiber': 12.2, 'cal': 508, 'category': 'seed'},
    'Rapeseed':         {'protein': 21.5, 'fat': 48.5, 'carbs': 20.0, 'fiber': 8.0,  'cal': 562, 'category': 'seed'},
    'Niger Seed':       {'protein': 21.0, 'fat': 38.5, 'carbs': 15.0, 'fiber': 15.0, 'cal': 503, 'category': 'seed'},
}

# ── Base mixes by purpose ────────────────────────────────────────────────────
# Each list is (grain_name, percentage). Must sum to 100.
BASE_MIXES = {
    'racing': [
        ('Maize (Corn)',   35),
        ('Wheat',          20),
        ('Barley',         10),
        ('Peas',           15),
        ('Vetch',           5),
        ('Sorghum',         5),
        ('Lentils',         5),
        ('Flaxseed',        3),
        ('Sunflower Seed',  2),
    ],
    'breeding': [
        ('Maize (Corn)',   25),
        ('Wheat',          15),
        ('Peas',           18),
        ('Chickpeas',       8),
        ('Lentils',         8),
        ('Mung Beans',      8),
        ('Gram (Chana)',    6),
        ('Sunflower Seed',  6),
        ('Safflower Seed',  4),
        ('Flaxseed',        2),
    ],
    'molting': [
        ('Peas',           20),
        ('Wheat',          15),
        ('Lentils',        15),
        ('Vetch',          10),
        ('Oats',           10),
        ('Sunflower Seed', 10),
        ('Sesame Seed',     5),
        ('Canary Seed',     5),
        ('Niger Seed',      5),
        ('Flaxseed',        5),
    ],
    'maintenance': [
        ('Maize (Corn)',   40),
        ('Wheat',          25),
        ('Barley',         15),
        ('Sorghum',         8),
        ('Millet',          7),
        ('Rice (Broken)',   5),
    ],
    'young': [
        ('Wheat',          25),
        ('Peas',           20),
        ('Maize (Corn)',   15),
        ('Millet',         10),
        ('Lentils',        10),
        ('Mung Beans',      8),
        ('Canary Seed',     5),
        ('Oats',            4),
        ('Buckwheat',       3),
    ],
}


def generate_feed(purpose, target_protein=None):
    """
    Generate a feed formula and calculate full nutritional values.
    Returns a dict with items list and totals.
    """
    if purpose not in BASE_MIXES:
        purpose = 'maintenance'

    mix     = list(BASE_MIXES[purpose])
    targets = PURPOSE_TARGETS[purpose]

    if target_protein:
        mix = _adjust_for_protein(mix, float(target_protein))

    # ── Calculate weighted nutritional totals ────────────────────────────────
    total_protein = 0.0
    total_fat     = 0.0
    total_carbs   = 0.0
    total_fiber   = 0.0
    total_cal     = 0.0
    items         = []

    for grain, pct in mix:
        nutrition = GRAIN_NUTRITION.get(grain, {
            'protein': 12, 'fat': 3, 'carbs': 70,
            'fiber': 2,    'cal': 350, 'category': 'cereal'
        })
        weight         = pct / 100
        contrib_protein = nutrition['protein'] * weight
        contrib_fat     = nutrition['fat']     * weight
        contrib_carbs   = nutrition['carbs']   * weight
        contrib_fiber   = nutrition['fiber']   * weight
        contrib_cal     = nutrition['cal']     * weight

        total_protein += contrib_protein
        total_fat     += contrib_fat
        total_carbs   += contrib_carbs
        total_fiber   += contrib_fiber
        total_cal     += contrib_cal

        items.append({
            'grain':        grain,
            'category':     nutrition['category'],
            'percentage':   pct,
            'protein':      nutrition['protein'],
            'fat':          nutrition['fat'],
            'grams_per_kg': pct * 10,
            'contrib_protein': round(contrib_protein, 2),
        })

    # Sort items by percentage descending for display
    items.sort(key=lambda x: x['percentage'], reverse=True)

    return {
        'purpose':        purpose,
        'items':          items,
        'total_protein':  round(total_protein, 1),
        'total_fat':      round(total_fat,     1),
        'total_carbs':    round(total_carbs,   1),
        'total_fiber':    round(total_fiber,   1),
        'total_cal':      round(total_cal,     0),
        'targets':        targets,
    }


def _adjust_for_protein(mix, target):
    """
    Shift legume/cereal ratio to approach target protein %.
    Increases high-protein grains (Peas/Lentils) and reduces
    low-protein grains (Maize/Barley) to meet the target.
    """
    adjusted = {grain: pct for grain, pct in mix}

    # Calculate current protein level
    current = sum(
        GRAIN_NUTRITION.get(g, {}).get('protein', 12) * p / 100
        for g, p in adjusted.items()
    )

    diff  = target - current
    if abs(diff) < 0.5:
        return list(adjusted.items())

    # Protein boosters (high protein grains)
    boosters  = ['Peas', 'Lentils', 'Vetch', 'Mung Beans', 'Cowpea']
    # Protein reducers (low protein grains)
    reducers  = ['Maize (Corn)', 'Rice (Broken)', 'Barley', 'Sorghum']

    shift = min(abs(diff) * 2.5, 20)

    if diff > 0:
        # Need more protein — boost legumes, reduce cereals
        for booster in boosters:
            if booster in adjusted:
                adjusted[booster] = adjusted.get(booster, 0) + shift / len(
                    [b for b in boosters if b in adjusted]
                )
                break
        for reducer in reducers:
            if reducer in adjusted and adjusted[reducer] > shift:
                adjusted[reducer] -= shift
                break
    else:
        # Need less protein — boost cereals, reduce legumes
        for reducer in reducers:
            if reducer in adjusted:
                adjusted[reducer] = adjusted.get(reducer, 0) + shift
                break
        for booster in boosters:
            if booster in adjusted and adjusted[booster] > shift:
                adjusted[booster] -= shift
                break

    # Normalize to 100%
    total = sum(adjusted.values()) or 100
    normalized = [
        (g, round(p * 100 / total))
        for g, p in adjusted.items()
        if p > 0
    ]

    # Fix any rounding drift so it always sums to exactly 100
    current_sum = sum(p for _, p in normalized)
    if current_sum != 100 and normalized:
        grain, pct = normalized[0]
        normalized[0] = (grain, pct + (100 - current_sum))

    return normalized