#!/usr/bin/env python3
"""
Fix FR1.csv to restore RTP by reducing excess low symbols and restoring wilds.

Based on simulation results showing 255× average, we need to:
1. Reduce L1 from current (~306) to target (~125) - need to REMOVE ~180 L1
2. Reduce L2 from current (~94) to target (~61) - need to REMOVE ~33 L2  
3. Reduce L3 from current (~109) to target (~59) - need to REMOVE ~50 L3
4. Reduce W slightly from current (~20) to target (~17) - need to REMOVE ~3 W
5. Replace removed lows with premiums (H1-H3) to maintain volatility
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_fix')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Original baseline
ORIGINAL = {
    'H1': 45,
    'H2': 65,
    'H3': 34,
    'H4': 55,
    'L1': 186,
    'L2': 84,
    'L3': 75,
    'L4': 95,
    'L5': 85,
    'W': 18,
    'VS': 2,
    'S': 8,
}

# Read file
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Count current
current = defaultdict(int)
for row in rows:
    for sym in row:
        current[sym] += 1

total = sum(current.values())
print("="*80)
print("FR1.CSV RTP FIX - REDUCING EXCESS LOWS")
print("="*80)
print(f"\nRows: {len(rows)}, Total symbols: {total}")

print(f"\n{'='*80}")
print("CURRENT STATE")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Original':<10} {'Diff':<10}")
print("-" * 60)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    curr = current.get(sym, 0)
    orig = ORIGINAL.get(sym, 0)
    diff = curr - orig
    print(f"{sym:<8} {curr:<10} {orig:<10} {diff:+10}")

# Target counts (restored to reasonable levels)
targets = {
    'L1': int(ORIGINAL['L1'] * 0.67),  # 33% reduction → 125
    'L2': int(ORIGINAL['L2'] * 0.73),  # 27% reduction → 61
    'L3': int(ORIGINAL['L3'] * 0.78),  # 22% reduction → 59
    'W': int(ORIGINAL['W'] * 0.94),    # 6% reduction → 17
}

# Keep other symbols at current levels
targets['H1'] = current.get('H1', 0)
targets['H2'] = current.get('H2', 0)
targets['H3'] = current.get('H3', 0)
targets['H4'] = current.get('H4', 0)
targets['L4'] = current.get('L4', 0)
targets['L5'] = current.get('L5', 0)
targets['VS'] = current.get('VS', 0)
targets['S'] = current.get('S', 0)

print(f"\n{'='*80}")
print("TARGET COUNTS")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Target':<10} {'Need to Change':<15}")
print("-" * 60)

changes = {}
for sym in ['L1', 'L2', 'L3', 'W']:
    curr = current.get(sym, 0)
    targ = targets[sym]
    needed = targ - curr
    changes[sym] = needed
    action = "REMOVE" if needed < 0 else "ADD"
    print(f"{sym:<8} {curr:<10} {targ:<10} {action} {abs(needed):<10}")

# Calculate how many premiums to add
lows_to_remove = abs(changes['L1']) + abs(changes['L2']) + abs(changes['L3'])
wilds_to_remove = abs(changes['W']) if changes['W'] < 0 else 0
total_to_remove = lows_to_remove + wilds_to_remove

# Distribute premiums: mostly H3 (volatility), some H2, some H1
premiums_to_add = {
    'H3': int(total_to_remove * 0.60),  # 60% H3
    'H2': int(total_to_remove * 0.30),  # 30% H2
    'H1': int(total_to_remove * 0.10),  # 10% H1
}

print(f"\nWill add premiums:")
print(f"  H3: +{premiums_to_add['H3']}")
print(f"  H2: +{premiums_to_add['H2']}")
print(f"  H1: +{premiums_to_add['H1']}")

# Create modified copy
modified = [row.copy() for row in rows]

# Phase 1: Remove excess L1
if changes['L1'] < 0:
    removed = 0
    to_remove = abs(changes['L1'])
    # Target L1 in rows with many lows (clusters)
    for row_idx, row in enumerate(modified):
        if removed >= to_remove:
            break
        row_l1_count = sum(1 for s in row if s == 'L1')
        if row_l1_count >= 2:  # Target rows with L1 clusters
            for reel_idx, sym in enumerate(row):
                if sym == 'L1' and removed < to_remove:
                    if random.random() < 0.6:  # 60% chance
                        # Replace with premium (prefer H3)
                        if removed < premiums_to_add['H3']:
                            modified[row_idx][reel_idx] = 'H3'
                        elif removed < premiums_to_add['H3'] + premiums_to_add['H2']:
                            modified[row_idx][reel_idx] = 'H2'
                        else:
                            modified[row_idx][reel_idx] = 'H1'
                        removed += 1
                        if removed >= to_remove:
                            break
    print(f"\nRemoved {removed} L1 symbols")

# Phase 2: Remove excess L2
if changes['L2'] < 0:
    removed = 0
    to_remove = abs(changes['L2'])
    for row_idx, row in enumerate(modified):
        if removed >= to_remove:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'L2' and removed < to_remove:
                if random.random() < 0.5:
                    removed_l1_so_far = sum(1 for r in modified if 'L1' in r and modified.index(r) < row_idx)
                    if removed_l1_so_far < premiums_to_add['H3']:
                        modified[row_idx][reel_idx] = 'H3'
                    elif removed_l1_so_far < premiums_to_add['H3'] + premiums_to_add['H2']:
                        modified[row_idx][reel_idx] = 'H2'
                    else:
                        modified[row_idx][reel_idx] = 'H1'
                    removed += 1
                    if removed >= to_remove:
                        break
    print(f"Removed {removed} L2 symbols")

# Phase 3: Remove excess L3
if changes['L3'] < 0:
    removed = 0
    to_remove = abs(changes['L3'])
    for row_idx, row in enumerate(modified):
        if removed >= to_remove:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'L3' and removed < to_remove:
                if random.random() < 0.5:
                    removed_so_far = sum(1 for r in modified for s in r if r == modified[row_idx] and s in ['L1', 'L2'])
                    if removed_so_far < premiums_to_add['H3']:
                        modified[row_idx][reel_idx] = 'H3'
                    elif removed_so_far < premiums_to_add['H3'] + premiums_to_add['H2']:
                        modified[row_idx][reel_idx] = 'H2'
                    else:
                        modified[row_idx][reel_idx] = 'H1'
                    removed += 1
                    if removed >= to_remove:
                        break
    print(f"Removed {removed} L3 symbols")

# Phase 4: Remove excess W
if changes['W'] < 0:
    removed = 0
    to_remove = abs(changes['W'])
    for row_idx, row in enumerate(modified):
        if removed >= to_remove:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'W' and removed < to_remove:
                if random.random() < 0.3:
                    modified[row_idx][reel_idx] = 'H3'  # Replace with premium
                    removed += 1
                    if removed >= to_remove:
                        break
    print(f"Removed {removed} wilds")

# Count after
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("AFTER CORRECTION")
print("="*80)
print(f"\n{'Symbol':<8} {'Original':<10} {'Before':<10} {'After':<10} {'Change':<10}")
print("-" * 70)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    orig = ORIGINAL.get(sym, 0)
    bef = current.get(sym, 0)
    aft = after.get(sym, 0)
    chg = aft - bef
    print(f"{sym:<8} {orig:<10} {bef:<10} {aft:<10} {chg:+10}")

# Category totals
def cat_total(syms, counts):
    return sum(counts.get(s, 0) for s in syms)

orig_premium = cat_total(['H1','H2','H3','H4'], ORIGINAL)
bef_premium = cat_total(['H1','H2','H3','H4'], current)
aft_premium = cat_total(['H1','H2','H3','H4'], after)

orig_low = cat_total(['L1','L2','L3','L4','L5'], ORIGINAL)
bef_low = cat_total(['L1','L2','L3','L4','L5'], current)
aft_low = cat_total(['L1','L2','L3','L4','L5'], after)

orig_special = cat_total(['W','VS','S'], ORIGINAL)
bef_special = cat_total(['W','VS','S'], current)
aft_special = cat_total(['W','VS','S'], after)

print(f"\nCategory Totals:")
print(f"{'Category':<15} {'Original':<10} {'Before':<10} {'After':<10} {'Change':<10}")
print("-" * 70)
print(f"{'Premiums (H1-H4)':<15} {orig_premium:<10} {bef_premium:<10} {aft_premium:<10} {aft_premium-bef_premium:+10}")
print(f"{'Lows (L1-L5)':<15} {orig_low:<10} {bef_low:<10} {aft_low:<10} {aft_low-bef_low:+10}")
print(f"{'Specials (W,VS,S)':<15} {orig_special:<10} {bef_special:<10} {aft_special:<10} {aft_special-bef_special:+10}")

# Estimate impact
low_change = aft_low - bef_low
premium_change = aft_premium - bef_premium

# More lows removed = more volatility but lower base wins
# Actually wait - we're REMOVING lows, which should DECREASE RTP further
# This is backwards! We need to ADD lows back, not remove them!

print(f"\n{'='*80}")
print("ERROR: Strategy backwards!")
print("="*80)
print("\nThe file has TOO MANY lows, but we need MORE lows to increase RTP.")
print("This suggests the file state doesn't match the simulation results.")
print("\nAborting - please check file state manually.")
print("="*80)

# Don't write the file - something is wrong
print("\nFile NOT modified - please verify current state")

