# plans.py
# Auto-generated plans module for workout-recommender
# Expects data/exercises_reduced.csv (columns: name,equipment_cat,body_part,difficulty,gif_url)
# If that CSV is missing, a tiny fallback set of exercises is used.

import os
import pandas as pd
from collections import OrderedDict

DATA_EXERCISES = os.path.join("data", "exercises_reduced.csv")

# ---- Plan metadata: keep plan_ids consistent with templates.csv ----
PLAN_META = {
    'P1': {'name':'4-day Upper/Lower Hypertrophy','goal':'build_muscle','equipment':'gym','experience':'intermediate','time_per_day':60,'tags':['strength']},
    'P2': {'name':'3-day Full Body Beginner','goal':'build_muscle','equipment':'none','experience':'beginner','time_per_day':40,'tags':['strength']},
    'P3': {'name':'5-day Cardio + HIIT','goal':'lose_weight','equipment':'basic','experience':'intermediate','time_per_day':40,'tags':['cardio']},
    'P4': {'name':'4-day Strength (compound focus)','goal':'build_muscle','equipment':'gym','experience':'advanced','time_per_day':60,'tags':['strength']},
    'P5': {'name':'Bodyweight Conditioning 4-day','goal':'lose_weight','equipment':'none','experience':'intermediate','time_per_day':30,'tags':['conditioning']},
    'P6': {'name':'5-day Muscle Endurance','goal':'endurance','equipment':'basic','experience':'intermediate','time_per_day':40,'tags':['endurance']},
    'P7': {'name':'3-day Minimal Time (20 min HIIT)','goal':'lose_weight','equipment':'none','experience':'beginner','time_per_day':20,'tags':['cardio']},
    'P8': {'name':'Yoga & Mobility 5-day','goal':'flexibility','equipment':'none','experience':'beginner','time_per_day':30,'tags':['mobility']},
    'P9': {'name':'Push/Pull/Legs 3-day Split','goal':'build_muscle','equipment':'basic','experience':'intermediate','time_per_day':50,'tags':['strength']},
    'P10':{'name':'Advanced Strength + Accessory 5-day','goal':'build_muscle','equipment':'gym','experience':'advanced','time_per_day':60,'tags':['strength']}
}

# ---- Helpers to load exercise DB and pick exercises ----
def load_exercises(path=DATA_EXERCISES):
    if os.path.exists(path):
        df = pd.read_csv(path)
        # ensure required columns exist
        req = {'name','equipment_cat','body_part','difficulty'}
        if not req.issubset(set(df.columns)):
            raise RuntimeError(f"exercises CSV missing required cols: {req - set(df.columns)}")
        return df
    # fallback small list if CSV missing
    fallback = [
        {"name":"Push Up","equipment_cat":"none","body_part":"chest","difficulty":"beginner","gif_url":""},
        {"name":"Bodyweight Squat","equipment_cat":"none","body_part":"legs","difficulty":"beginner","gif_url":""},
        {"name":"Plank","equipment_cat":"none","body_part":"core","difficulty":"beginner","gif_url":""},
        {"name":"Jumping Jacks","equipment_cat":"none","body_part":"cardio","difficulty":"beginner","gif_url":""},
        {"name":"Dumbbell Row","equipment_cat":"basic","body_part":"back","difficulty":"intermediate","gif_url":""},
        {"name":"Barbell Back Squat","equipment_cat":"gym","body_part":"legs","difficulty":"advanced","gif_url":""},
        {"name":"Bench Press","equipment_cat":"gym","body_part":"chest","difficulty":"advanced","gif_url":""},
        {"name":"Bicycle Crunch","equipment_cat":"none","body_part":"core","difficulty":"beginner","gif_url":""},
        {"name":"Kettlebell Swing","equipment_cat":"basic","body_part":"full body","difficulty":"intermediate","gif_url":""},
        {"name":"Burpee","equipment_cat":"none","body_part":"full body","difficulty":"intermediate","gif_url":""}
    ]
    return pd.DataFrame(fallback)

def allowed_equipment_for(plan_equipment):
    if plan_equipment == 'gym':
        return ['gym','basic','none']   # gym plans may include basic-bodyweight variations
    if plan_equipment == 'basic':
        return ['basic','none']
    return ['none','basic']

# Map high-level tag -> preferred body parts
TAG_TO_PARTS = {
    'strength': ['chest','back','legs','shoulders','arms','core','full body'],
    'cardio': ['cardio','full body','core'],
    'conditioning': ['full body','legs','cardio'],
    'mobility': ['mobility','core','full body'],
    'endurance': ['cardio','legs','full body']
}

def pick_exercises_for_plan(df, plan_meta, n_per_day=4, seed_base=42):
    allowed = allowed_equipment_for(plan_meta['equipment'])
    parts = []
    for t in plan_meta.get('tags', []):
        parts += TAG_TO_PARTS.get(t, [])
    parts = list(OrderedDict.fromkeys(parts))  # unique and keep order
    # filter pool
    pool = df[df['equipment_cat'].isin(allowed)].copy()
    if parts:
        pool2 = pool[pool['body_part'].isin(parts)]
        if not pool2.empty:
            pool = pool2
    # deterministic ordering and sample
    # use seed derived from plan_id name for reproducible selection
    pool = pool.drop_duplicates(subset=['name']).reset_index(drop=True)
    seed = seed_base + sum(ord(c) for c in plan_meta['name']) % 1000
    # if pool smaller than needed, allow repeats by tiling
    needed = 7 * n_per_day
    if len(pool) == 0:
        return []
    if len(pool) >= needed:
        chosen = pool.sample(n=needed, random_state=seed)['name'].tolist()
    else:
        # repeat but keep unique order
        names = pool['name'].tolist()
        reps = (needed // len(names)) + 1
        chosen = (names * reps)[:needed]
    # split to 7 days
    week = []
    idx = 0
    for d in range(7):
        day_exs = []
        for _ in range(n_per_day):
            name = chosen[idx]
            # find metadata row if available
            r = pool[pool['name']==name]
            if not r.empty:
                r0 = r.iloc[0]
                ex_meta = {"name": name, "sets": "3", "reps": "8-12", "equipment": r0.get('equipment_cat',''), "body_part": r0.get('body_part',''), "gif_url": r0.get('gif_url','')}
            else:
                ex_meta = {"name": name, "sets": "3", "reps": "8-12", "equipment": "", "body_part": "", "gif_url": ""}
            day_exs.append(ex_meta)
            idx += 1
        week.append({"day": d+1, "focus": plan_meta.get('tags', ['general'])[0] + f" (day {d+1})", "exercises": day_exs})
    return week

# ---- Build PLANS dict on import ----
PLANS = {}

def build_plans():
    df = load_exercises()
    for pid, meta in PLAN_META.items():
        week = pick_exercises_for_plan(df, meta, n_per_day=4, seed_base=42)
        PLANS[pid] = {
            "plan_id": pid,
            "meta": meta,
            "week": week
        }

# Build on import
build_plans()

# Convenience getters
def get_plan(plan_id):
    return PLANS.get(plan_id)

def list_plans():
    return list(PLANS.keys())

# (optional) pretty-print helper
def print_summary():
    print("Available plans:", list_plans())
    for pid, p in PLANS.items():
        print(f"{pid}: {p['meta']['name']} - days with exercises:", len(p['week']))

# If run directly, print a short summary
if __name__ == "__main__":
    print_summary()
