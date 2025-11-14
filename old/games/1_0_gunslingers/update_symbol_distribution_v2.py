#!/usr/bin/env python3
"""
Update FR1.csv symbol distribution to v2 target counts.

Target v2 distribution:
- H3: 240 (was 170, +70)
- W: 16 (was 13, +3)
- L1: 147 (unchanged)
- L2: 75 (unchanged)
- L3: 70 (unchanged)
- L4: 184 (was 222, -38)
- L5: 172 (was 207, -35)

Strategy:
- Convert 70 L4/L5 → H3
- Convert 3 L4/L5 → W
- Keep other symbols unchanged
"""

import csv
import os
import shutil
import random
from collections import defaultdict
from datetime import datetime

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_v2')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Current counts (from user)
CURRENT = {
    'H3': 170,
    'W': 13,
    'L1': 147,
    'L2': 75,
    'L3': 70,
    'L4': 222,
    'L5': 207,
}

# Target v2 counts
TARGETS = {
    'H3': 240,
    'W': 16,
    'L1': 147,
    'L2': 75,
    'L3': 70,
    'L4': 184,
    'L5': 172,
}

# Read current file
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Count current symbols
current_actual = defaultdict(int)
for row in rows:
    for sym in row:
        current_actual[sym] += 1

total = sum(current_actual.values())

print("="*80)
print("FR1.CSV SYMBOL DISTRIBUTION UPDATE TO V2")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")

print(f"\n{'='*80}")
print("CURRENT STATE")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Target':<10} {'Change Needed':<15}")
print("-" * 70)

changes_needed = {}
for sym in ['H3', 'W', 'L1', 'L2', 'L3', 'L4', 'L5']:
    curr = current_actual.get(sym, 0)
    targ = TARGETS[sym]
    need = targ - curr
    changes_needed[sym] = need
    action = "ADD" if need > 0 else "REMOVE"
    print(f"{sym:<8} {curr:<10} {targ:<10} {action} {abs(need):<10}")

# Verify other symbols are unchanged
print(f"\n{'='*80}")
print("OTHER SYMBOLS (Should remain unchanged)")
print("="*80)
print(f"\n{'Symbol':<8} {'Count':<10}")
print("-" * 30)

other_symbols = ['H1', 'H2', 'H4', 'VS', 'S']
for sym in other_symbols:
    count = current_actual.get(sym, 0)
    print(f"{sym:<8} {count:<10}")

# Create working copy
modified = [row.copy() for row in rows]

# Strategy: Convert L4/L5 to H3 and W
# Phase 1: Convert L4/L5 to H3 (need +70 H3)
print(f"\n{'='*80}")
print("PHASE 1: Converting L4/L5 → H3")
print("="*80)

h3_to_add = changes_needed['H3']  # +70
h3_added = 0

# Prefer converting L4/L5 that are in rows with many lows
for row_idx, row in enumerate(modified):
    if h3_added >= h3_to_add:
        break
    for reel_idx, sym in enumerate(row):
        if sym in ['L4', 'L5'] and h3_added < h3_to_add:
            # Avoid creating H3 clusters (max 4-5 H3 per row)
            row_h3_count = sum(1 for s in modified[row_idx] if s == 'H3')
            if row_h3_count < 5:
                if random.random() < 0.6:  # 60% chance
                    modified[row_idx][reel_idx] = 'H3'
                    h3_added += 1
                    if h3_added >= h3_to_add:
                        break

print(f"✓ Added {h3_added} H3 symbols (converted from L4/L5)")

# Phase 2: Convert L4/L5 to W (need +3 W)
print(f"\n{'='*80}")
print("PHASE 2: Converting L4/L5 → W")
print("="*80)

w_to_add = changes_needed['W']  # +3
w_added = 0

for row_idx, row in enumerate(modified):
    if w_added >= w_to_add:
        break
    for reel_idx, sym in enumerate(row):
        if sym in ['L4', 'L5'] and w_added < w_to_add:
            # Don't create W clusters (max 1 W per row)
            row_w_count = sum(1 for s in modified[row_idx] if s == 'W')
            if row_w_count == 0:
                if random.random() < 0.4:  # 40% chance
                    modified[row_idx][reel_idx] = 'W'
                    w_added += 1
                    if w_added >= w_to_add:
                        break

print(f"✓ Added {w_added} wilds (converted from L4/L5)")

# Count after modifications
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("AFTER V2 UPDATE")
print("="*80)
print(f"\n{'Symbol':<8} {'Before':<10} {'After':<10} {'Target':<10} {'Change':<10} {'Status':<10}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    bef = current_actual.get(sym, 0)
    aft = after.get(sym, 0)
    targ = TARGETS.get(sym, '-')
    chg = aft - bef
    if sym in TARGETS:
        status = "✓" if abs(aft - targ) <= 3 else "⚠"
    else:
        status = "-"
    print(f"{sym:<8} {bef:<10} {aft:<10} {str(targ):<10} {chg:+10} {status:<10}")

# Verify totals
target_total = sum(TARGETS.values())
actual_total = sum(after.get(s, 0) for s in TARGETS.keys())
print(f"\nTarget total for adjusted symbols: {target_total}")
print(f"Actual total for adjusted symbols: {actual_total}")
print(f"Difference: {actual_total - target_total:+d}")

# Category totals
def cat_total(syms, counts):
    return sum(counts.get(s, 0) for s in syms)

bef_premium = cat_total(['H1','H2','H3','H4'], current_actual)
aft_premium = cat_total(['H1','H2','H3','H4'], after)
bef_low = cat_total(['L1','L2','L3','L4','L5'], current_actual)
aft_low = cat_total(['L1','L2','L3','L4','L5'], after)
bef_special = cat_total(['W','VS','S'], current_actual)
aft_special = cat_total(['W','VS','S'], after)

print(f"\nCategory Totals:")
print(f"{'Category':<15} {'Before':<10} {'After':<10} {'Change':<10}")
print("-" * 60)
print(f"{'Premiums (H1-H4)':<15} {bef_premium:<10} {aft_premium:<10} {aft_premium-bef_premium:+10}")
print(f"{'Lows (L1-L5)':<15} {bef_low:<10} {aft_low:<10} {aft_low-bef_low:+10}")
print(f"{'Specials (W,VS,S)':<15} {bef_special:<10} {aft_special:<10} {aft_special-bef_special:+10}")

# Save file
print(f"\n{'='*80}")
print("SAVING UPDATED FILE")
print("="*80)

if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)
    print(f"✓ Created backup: {backup_file}")

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified:
        writer.writerow(row)

print(f"✓ Updated FR1.csv saved with v2 distribution")

print(f"\n{'='*80}")
print("V2 DISTRIBUTION UPDATE COMPLETE")
print("="*80)
print(f"\nSummary:")
print(f"  H3: {current_actual.get('H3', 0)} → {after.get('H3', 0)} ({after.get('H3', 0) - current_actual.get('H3', 0):+d}) [Target: {TARGETS['H3']}]")
print(f"  W: {current_actual.get('W', 0)} → {after.get('W', 0)} ({after.get('W', 0) - current_actual.get('W', 0):+d}) [Target: {TARGETS['W']}]")
print(f"  L1: {current_actual.get('L1', 0)} → {after.get('L1', 0)} (unchanged) [Target: {TARGETS['L1']}]")
print(f"  L2: {current_actual.get('L2', 0)} → {after.get('L2', 0)} (unchanged) [Target: {TARGETS['L2']}]")
print(f"  L3: {current_actual.get('L3', 0)} → {after.get('L3', 0)} (unchanged) [Target: {TARGETS['L3']}]")
print(f"  L4: {current_actual.get('L4', 0)} → {after.get('L4', 0)} ({after.get('L4', 0) - current_actual.get('L4', 0):+d}) [Target: {TARGETS['L4']}]")
print(f"  L5: {current_actual.get('L5', 0)} → {after.get('L5', 0)} ({after.get('L5', 0) - current_actual.get('L5', 0):+d}) [Target: {TARGETS['L5']}]")
print(f"\nReady for simulation!")

