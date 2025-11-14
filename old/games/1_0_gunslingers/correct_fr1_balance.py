#!/usr/bin/env python3
"""
Balance FR1.csv by restoring some low symbols and wilds to increase RTP.

Target:
- L1: Reduce from current to ~125-130 (30-35% reduction from original 186)
- L2: Reduce to ~60-63 (25-30% reduction from original 84)  
- L3: Reduce to ~58-60 (20-25% reduction from original 75)
- W: Restore to ~17 (5% reduction from original 18, not 12% cut)
- Keep premiums (H1-H3) as they are
- Keep VS and S unchanged
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_balance')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Original baseline (before any modifications)
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

# Read current file
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Count current symbols
current = defaultdict(int)
for row in rows:
    for sym in row:
        current[sym] += 1

total = sum(current.values())
print("="*80)
print("FR1.CSV RTP BALANCE CORRECTION")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")

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

# Calculate targets (restore some lows but keep them reduced)
targets = {
    'L1': int(ORIGINAL['L1'] * 0.67),  # 33% reduction → 125
    'L2': int(ORIGINAL['L2'] * 0.73),  # 27% reduction → 61  
    'L3': int(ORIGINAL['L3'] * 0.78),  # 22% reduction → 59
    'W': int(ORIGINAL['W'] * 0.94),    # 6% reduction → 17
}

# Keep current premiums (they're good for volatility)
targets['H1'] = current['H1']
targets['H2'] = current['H2']
targets['H3'] = current['H3']
targets['H4'] = current['H4']
targets['L4'] = current['L4']
targets['L5'] = current['L5']
targets['VS'] = current['VS']
targets['S'] = current['S']

print(f"\n{'='*80}")
print("TARGET COUNTS")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Target':<10} {'Change':<10}")
print("-" * 60)

changes_needed = {}
for sym in ['L1', 'L2', 'L3', 'W']:
    curr = current.get(sym, 0)
    targ = targets[sym]
    needed = targ - curr
    changes_needed[sym] = needed
    print(f"{sym:<8} {curr:<10} {targ:<10} {needed:+10}")

# Create working copy
modified = [row.copy() for row in rows]

# Strategy: Convert some H3 back to lows (since H3 was added most aggressively)
# Also convert some H2 back to lows where appropriate
# And restore some wilds

# Phase 1: Restore wilds (convert some H3/H2 to W)
if changes_needed['W'] > 0:
    restored = 0
    for row_idx, row in enumerate(modified):
        if restored >= changes_needed['W']:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and restored < changes_needed['W']:
                # Convert with some probability to avoid creating patterns
                if random.random() < 0.4:
                    modified[row_idx][reel_idx] = 'W'
                    restored += 1
                    if restored >= changes_needed['W']:
                        break
    print(f"\nRestored {restored} wilds")

# Phase 2: Restore L1 (convert H3 back to L1)
if changes_needed['L1'] > 0:
    restored = 0
    for row_idx, row in enumerate(modified):
        if restored >= changes_needed['L1']:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'H3' and restored < changes_needed['L1']:
                # Avoid creating L1 clusters
                row_lows = sum(1 for s in modified[row_idx] if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:  # Don't create clusters
                    if random.random() < 0.35:
                        modified[row_idx][reel_idx] = 'L1'
                        restored += 1
                        if restored >= changes_needed['L1']:
                            break
    print(f"Restored {restored} L1 symbols")

# Phase 3: Restore L2 (convert H3/H2 back to L2)
if changes_needed['L2'] > 0:
    restored = 0
    for row_idx, row in enumerate(modified):
        if restored >= changes_needed['L2']:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and restored < changes_needed['L2']:
                row_lows = sum(1 for s in modified[row_idx] if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:
                    if random.random() < 0.3:
                        modified[row_idx][reel_idx] = 'L2'
                        restored += 1
                        if restored >= changes_needed['L2']:
                            break
    print(f"Restored {restored} L2 symbols")

# Phase 4: Restore L3 (convert H2/H1 back to L3)
if changes_needed['L3'] > 0:
    restored = 0
    for row_idx, row in enumerate(modified):
        if restored >= changes_needed['L3']:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H2', 'H1'] and restored < changes_needed['L3']:
                row_lows = sum(1 for s in modified[row_idx] if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:
                    if random.random() < 0.25:
                        modified[row_idx][reel_idx] = 'L3'
                        restored += 1
                        if restored >= changes_needed['L3']:
                            break
    print(f"Restored {restored} L3 symbols")

# Count after modifications
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
low_restored = aft_low - bef_low
wild_restored = after['W'] - current['W']

# Rough estimate: Each low restored adds base win potential
# Current avg was 255×, need ~384× (50% increase)
estimated_increase = (low_restored * 1.5) + (wild_restored * 4.0)
estimated_avg = 255.14 + estimated_increase

print(f"\n{'='*80}")
print("EXPECTED IMPACT")
print("="*80)
print(f"\nSymbols restored:")
print(f"  Low symbols: {low_restored:+d}")
print(f"  Wilds: {wild_restored:+d}")
print(f"\nEstimated average feature win:")
print(f"  Current: 255.14×")
print(f"  Estimated: ~{estimated_avg:.1f}×")
print(f"  Increase: +{estimated_increase:.1f}×")
print(f"\nTarget: 384× ± 5× (379× - 389×)")
if 379 <= estimated_avg <= 389:
    print(f"  Status: ✅ Within target range (estimate)")
elif estimated_avg < 379:
    print(f"  Status: ⚠️  Below target - may need more restoration")
else:
    print(f"  Status: ⚠️  Above target - monitor carefully")

# Write file
print(f"\n{'='*80}")
print("SAVING CORRECTED FILE")
print("="*80)

if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)
    print(f"✓ Created backup: {backup_file}")

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified:
        writer.writerow(row)

print(f"✓ Corrected FR1.csv saved")
print(f"\nSummary:")
print(f"  L1: {current['L1']} → {after['L1']} ({after['L1']-current['L1']:+d})")
print(f"  L2: {current['L2']} → {after['L2']} ({after['L2']-current['L2']:+d})")
print(f"  L3: {current['L3']} → {after['L3']} ({after['L3']-current['L3']:+d})")
print(f"  W: {current['W']} → {after['W']} ({after['W']-current['W']:+d})")
print(f"\nReady for simulation!")

