#!/usr/bin/env python3
"""
Final balance correction for FR1.csv.

Target counts:
- L1: 125 (33% reduction from 186)
- L2: 61 (27% reduction from 84)  
- L3: 58 (23% reduction from 75)
- W: 17 (6% reduction from 18)

Strategy: Convert excess H3 (added in aggressive mod) back to lows to reach targets.
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_final')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

ORIGINAL = {'H1': 45, 'H2': 65, 'H3': 34, 'H4': 55, 'L1': 186, 'L2': 84, 'L3': 75, 'L4': 95, 'L5': 85, 'W': 18, 'VS': 2, 'S': 8}
TARGETS = {'L1': 125, 'L2': 61, 'L3': 58, 'W': 17}

# Read file
rows = []
with open(input_file, 'r') as f:
    rows = [list(row) for row in csv.reader(f) if len(row) == 5]

# Count current
current = defaultdict(int)
for row in rows:
    for sym in row:
        current[sym] += 1

print("="*80)
print("FR1.CSV FINAL BALANCE")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Target':<10} {'Need':<10}")
print("-" * 60)

needs = {}
for sym in ['L1', 'L2', 'L3', 'W']:
    curr = current.get(sym, 0)
    targ = TARGETS[sym]
    need = targ - curr
    needs[sym] = need
    action = "ADD" if need > 0 else "REMOVE"
    print(f"{sym:<8} {curr:<10} {targ:<10} {action} {abs(need):<10}")

modified = [row.copy() for row in rows]

# Convert H3 to lows where needed (H3 was over-added)
# L1 restoration
if needs['L1'] != 0:
    change = 0
    target = abs(needs['L1'])
    action = 'add' if needs['L1'] > 0 else 'remove'
    
    for row_idx, row in enumerate(modified):
        if change >= target:
            break
        for reel_idx, sym in enumerate(row):
            if action == 'add' and sym == 'H3' and change < target:
                row_l1 = sum(1 for s in modified[row_idx] if s == 'L1')
                if row_l1 < 3:
                    if random.random() < 0.35:
                        modified[row_idx][reel_idx] = 'L1'
                        change += 1
            elif action == 'remove' and sym == 'L1' and change < target:
                if random.random() < 0.5:
                    modified[row_idx][reel_idx] = 'H3'
                    change += 1
    print(f"\nL1: {action}ed {change} symbols")

# L2 restoration
if needs['L2'] != 0:
    change = 0
    target = abs(needs['L2'])
    action = 'add' if needs['L2'] > 0 else 'remove'
    
    for row_idx, row in enumerate(modified):
        if change >= target:
            break
        for reel_idx, sym in enumerate(row):
            if action == 'add' and sym in ['H3', 'H2'] and change < target:
                row_l2 = sum(1 for s in modified[row_idx] if s == 'L2')
                if row_l2 < 3:
                    if random.random() < 0.3:
                        modified[row_idx][reel_idx] = 'L2'
                        change += 1
            elif action == 'remove' and sym == 'L2' and change < target:
                if random.random() < 0.5:
                    modified[row_idx][reel_idx] = 'H3'
                    change += 1
    print(f"L2: {action}ed {change} symbols")

# L3 restoration  
if needs['L3'] != 0:
    change = 0
    target = abs(needs['L3'])
    action = 'add' if needs['L3'] > 0 else 'remove'
    
    for row_idx, row in enumerate(modified):
        if change >= target:
            break
        for reel_idx, sym in enumerate(row):
            if action == 'add' and sym in ['H2', 'H1'] and change < target:
                row_l3 = sum(1 for s in modified[row_idx] if s == 'L3')
                if row_l3 < 3:
                    if random.random() < 0.25:
                        modified[row_idx][reel_idx] = 'L3'
                        change += 1
            elif action == 'remove' and sym == 'L3' and change < target:
                if random.random() < 0.5:
                    modified[row_idx][reel_idx] = 'H2'
                    change += 1
    print(f"L3: {action}ed {change} symbols")

# W adjustment
if needs['W'] != 0:
    change = 0
    target = abs(needs['W'])
    action = 'add' if needs['W'] > 0 else 'remove'
    
    for row_idx, row in enumerate(modified):
        if change >= target:
            break
        for reel_idx, sym in enumerate(row):
            if action == 'add' and sym in ['H3', 'H2'] and change < target:
                row_w = sum(1 for s in modified[row_idx] if s == 'W')
                if row_w == 0:
                    if random.random() < 0.2:
                        modified[row_idx][reel_idx] = 'W'
                        change += 1
            elif action == 'remove' and sym == 'W' and change < target:
                if random.random() < 0.4:
                    modified[row_idx][reel_idx] = 'H3'
                    change += 1
    print(f"W: {action}ed {change} symbols")

# Count after
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("FINAL COUNTS")
print("="*80)
print(f"\n{'Symbol':<8} {'Original':<10} {'Before':<10} {'After':<10} {'Target':<10} {'Status':<10}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    orig = ORIGINAL.get(sym, 0)
    bef = current.get(sym, 0)
    aft = after.get(sym, 0)
    targ = TARGETS.get(sym, '-')
    if sym in TARGETS:
        status = "✓" if abs(aft - targ) <= 5 else "⚠"
    else:
        status = "-"
    print(f"{sym:<8} {orig:<10} {bef:<10} {aft:<10} {str(targ):<10} {status:<10}")

# Category totals
prem_bef = sum(current.get(s, 0) for s in ['H1','H2','H3','H4'])
prem_aft = sum(after.get(s, 0) for s in ['H1','H2','H3','H4'])
low_bef = sum(current.get(s, 0) for s in ['L1','L2','L3','L4','L5'])
low_aft = sum(after.get(s, 0) for s in ['L1','L2','L3','L4','L5'])

print(f"\nCategory Changes:")
print(f"  Premiums: {prem_bef} → {prem_aft} ({prem_aft-prem_bef:+d})")
print(f"  Lows: {low_bef} → {low_aft} ({low_aft-low_bef:+d})")

# Estimate
low_change = low_aft - low_bef
prem_change = prem_aft - prem_bef
w_change = after['W'] - current['W']

# If we removed lows, RTP goes down; if we added lows, RTP goes up
estimated_increase = (low_change * 2.0) + (w_change * 3.5) - (prem_change * 0.5)
estimated_avg = 255.14 + estimated_increase

print(f"\n{'='*80}")
print("EXPECTED IMPACT")
print("="*80)
print(f"\nCurrent average: 255.14×")
print(f"Estimated average: ~{estimated_avg:.1f}×")
print(f"Change: {estimated_increase:+.1f}×")
print(f"Target: 384× ± 5×")
if 379 <= estimated_avg <= 389:
    print(f"Status: ✅ Within target (estimate)")
else:
    print(f"Status: ⚠️  Outside target range")

# Save
if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)

with open(output_file, 'w', newline='') as f:
    csv.writer(f).writerows(modified)

print(f"\n{'='*80}")
print("FILE SAVED - Ready for simulation!")
print("="*80)
print(f"\nBefore → After:")
print(f"  L1: {current.get('L1', 0)} → {after.get('L1', 0)} (target: {TARGETS['L1']})")
print(f"  L2: {current.get('L2', 0)} → {after.get('L2', 0)} (target: {TARGETS['L2']})")
print(f"  L3: {current.get('L3', 0)} → {after.get('L3', 0)} (target: {TARGETS['L3']})")
print(f"  W: {current.get('W', 0)} → {after.get('W', 0)} (target: {TARGETS['W']})")

