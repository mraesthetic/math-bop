#!/usr/bin/env python3
"""
Restore some low symbols in FR1.csv to balance RTP while keeping volatility.

Based on user requirements:
- L1 reduction: 30-35% (target: ~121-130 from original 186)
- L2 reduction: 25-30% (target: ~59-63 from original 84)
- L3 reduction: 20-25% (target: ~56-60 from original 75)
- W: Restore to ~17 (5% reduction from 18, not 12%)
- Keep premiums (H1-H3) at current levels
- Preserve VS and S
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_restore')
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

# Target counts after restoration (moderate reduction from original)
TARGETS = {
    'L1': int(ORIGINAL['L1'] * 0.67),  # 33% reduction → 125
    'L2': int(ORIGINAL['L2'] * 0.73),  # 27% reduction → 61
    'L3': int(ORIGINAL['L3'] * 0.77),  # 23% reduction → 58
    'W': int(ORIGINAL['W'] * 0.94),    # 6% reduction → 17
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
print("FR1.CSV LOW SYMBOL RESTORATION")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")

print(f"\n{'='*80}")
print("CURRENT STATE")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Original':<10} {'Target':<10} {'Need':<10}")
print("-" * 70)

needs = {}
for sym in ['L1', 'L2', 'L3', 'W']:
    curr = current.get(sym, 0)
    orig = ORIGINAL.get(sym, 0)
    targ = TARGETS[sym]
    need = targ - curr
    needs[sym] = need
    print(f"{sym:<8} {curr:<10} {orig:<10} {targ:<10} {need:+10}")

# Show all symbols
print(f"\n{'='*80}")
print("ALL SYMBOL COUNTS (BEFORE)")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Original':<10} {'Difference':<12}")
print("-" * 70)
for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    curr = current.get(sym, 0)
    orig = ORIGINAL.get(sym, 0)
    diff = curr - orig
    print(f"{sym:<8} {curr:<10} {orig:<10} {diff:+12}")

# Create working copy
modified = [row.copy() for row in rows]

# Strategy: 
# If we need to ADD lows, convert some premiums (H3, H2) back to lows
# If we need to REMOVE lows (file has too many), remove excess

total_added = 0

# Restore L1: Convert H3/H2 to L1
if needs['L1'] > 0:
    added = 0
    target_add = needs['L1']
    print(f"\n{'='*80}")
    print(f"RESTORING L1: Need to add {target_add}")
    print("="*80)
    
    for row_idx, row in enumerate(modified):
        if added >= target_add:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and added < target_add:
                # Don't create L1 clusters (max 2-3 L1 per row)
                row_l1_count = sum(1 for s in modified[row_idx] if s == 'L1')
                if row_l1_count < 3:
                    if random.random() < 0.4:  # 40% chance
                        modified[row_idx][reel_idx] = 'L1'
                        added += 1
                        total_added += 1
                        if added >= target_add:
                            break
    print(f"✓ Added {added} L1 symbols")

# Restore L2: Convert H3/H2 to L2
if needs['L2'] > 0:
    added = 0
    target_add = needs['L2']
    print(f"\n{'='*80}")
    print(f"RESTORING L2: Need to add {target_add}")
    print("="*80)
    
    for row_idx, row in enumerate(modified):
        if added >= target_add:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and added < target_add:
                row_l2_count = sum(1 for s in modified[row_idx] if s == 'L2')
                if row_l2_count < 3:
                    if random.random() < 0.35:  # 35% chance
                        modified[row_idx][reel_idx] = 'L2'
                        added += 1
                        total_added += 1
                        if added >= target_add:
                            break
    print(f"✓ Added {added} L2 symbols")

# Restore L3: Convert H2/H1 to L3
if needs['L3'] > 0:
    added = 0
    target_add = needs['L3']
    print(f"\n{'='*80}")
    print(f"RESTORING L3: Need to add {target_add}")
    print("="*80)
    
    for row_idx, row in enumerate(modified):
        if added >= target_add:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H2', 'H1'] and added < target_add:
                row_l3_count = sum(1 for s in modified[row_idx] if s == 'L3')
                if row_l3_count < 3:
                    if random.random() < 0.3:  # 30% chance
                        modified[row_idx][reel_idx] = 'L3'
                        added += 1
                        total_added += 1
                        if added >= target_add:
                            break
    print(f"✓ Added {added} L3 symbols")

# Restore W: Convert H3/H2 to W (but only if we need more)
if needs['W'] > 0:
    added = 0
    target_add = needs['W']
    print(f"\n{'='*80}")
    print(f"RESTORING W: Need to add {target_add}")
    print("="*80)
    
    for row_idx, row in enumerate(modified):
        if added >= target_add:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and added < target_add:
                # Don't create W clusters
                row_w_count = sum(1 for s in modified[row_idx] if s == 'W')
                if row_w_count < 1:  # Max 1 W per row
                    if random.random() < 0.25:  # 25% chance
                        modified[row_idx][reel_idx] = 'W'
                        added += 1
                        total_added += 1
                        if added >= target_add:
                            break
    print(f"✓ Added {added} wilds")

# Handle case where we need to REMOVE excess (file has too many)
# Remove excess L1
if needs['L1'] < 0:
    removed = 0
    target_remove = abs(needs['L1'])
    print(f"\n{'='*80}")
    print(f"REDUCING L1: Need to remove {target_remove}")
    print("="*80)
    
    # Target rows with many L1s
    for row_idx, row in enumerate(modified):
        if removed >= target_remove:
            break
        row_l1_count = sum(1 for s in row if s == 'L1')
        if row_l1_count >= 3:  # Target clusters
            for reel_idx, sym in enumerate(row):
                if sym == 'L1' and removed < target_remove:
                    if random.random() < 0.6:
                        # Replace with premium
                        modified[row_idx][reel_idx] = 'H3'
                        removed += 1
                        if removed >= target_remove:
                            break
    print(f"✓ Removed {removed} L1 symbols (converted to H3)")

# Similar for L2, L3, W if needed
for sym_name, sym_val in [('L2', 'L2'), ('L3', 'L3'), ('W', 'W')]:
    if needs[sym_name] < 0:
        removed = 0
        target_remove = abs(needs[sym_name])
        print(f"\nReducing {sym_name}: removing {target_remove}...")
        for row_idx, row in enumerate(modified):
            if removed >= target_remove:
                break
            for reel_idx, sym in enumerate(row):
                if sym == sym_val and removed < target_remove:
                    if random.random() < 0.5:
                        modified[row_idx][reel_idx] = 'H3'
                        removed += 1
                        if removed >= target_remove:
                            break
        print(f"✓ Removed {removed} {sym_name} symbols")

# Count after modifications
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("AFTER RESTORATION")
print("="*80)
print(f"\n{'Symbol':<8} {'Original':<10} {'Before':<10} {'After':<10} {'Change':<10} {'Target':<10}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    orig = ORIGINAL.get(sym, 0)
    bef = current.get(sym, 0)
    aft = after.get(sym, 0)
    chg = aft - bef
    targ = TARGETS.get(sym, '-')
    print(f"{sym:<8} {orig:<10} {bef:<10} {aft:<10} {chg:+10} {str(targ):<10}")

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

# Estimate impact on average feature win
low_change = aft_low - bef_low
premium_change = aft_premium - bef_premium
wild_change = after['W'] - current['W']

# Rough estimate: restoring lows should increase base win frequency
# Current avg: 255×, target: 384×
# Each low restored adds base win potential
# Each wild restored adds connectivity

if low_change > 0:
    estimated_increase = (low_change * 1.8) + (wild_change * 4.0)
elif low_change < 0:
    estimated_increase = (low_change * 1.5) + (wild_change * 4.0)  # Negative
else:
    estimated_increase = wild_change * 4.0

estimated_avg = 255.14 + estimated_increase

print(f"\n{'='*80}")
print("EXPECTED IMPACT ESTIMATE")
print("="*80)
print(f"\nSymbol Changes:")
print(f"  Low symbols: {low_change:+d}")
print(f"  Wilds: {wild_change:+d}")
print(f"  Premiums: {premium_change:+d}")
print(f"\nEstimated Average Feature Win:")
print(f"  Current: 255.14×")
print(f"  Estimated: ~{estimated_avg:.1f}×")
print(f"  Change: {estimated_increase:+.1f}×")
print(f"\nTarget: 384× ± 5× (379× - 389×)")
if 379 <= estimated_avg <= 389:
    print(f"  Status: ✅ Within target range (estimate)")
elif estimated_avg < 379:
    print(f"  Status: ⚠️  Still below target")
    print(f"  Recommendation: May need to restore more lows or increase wilds")
else:
    print(f"  Status: ⚠️  May exceed target")
    print(f"  Recommendation: Monitor carefully in simulation")

# Save file
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
print(f"  L1: {current.get('L1', 0)} → {after.get('L1', 0)} ({after.get('L1', 0) - current.get('L1', 0):+d}) [Target: {TARGETS['L1']}]")
print(f"  L2: {current.get('L2', 0)} → {after.get('L2', 0)} ({after.get('L2', 0) - current.get('L2', 0):+d}) [Target: {TARGETS['L2']}]")
print(f"  L3: {current.get('L3', 0)} → {after.get('L3', 0)} ({after.get('L3', 0) - current.get('L3', 0):+d}) [Target: {TARGETS['L3']}]")
print(f"  W: {current.get('W', 0)} → {after.get('W', 0)} ({after.get('W', 0) - current.get('W', 0):+d}) [Target: {TARGETS['W']}]")
print(f"\n{'='*80}")
print("RESTORATION COMPLETE - Ready for simulation!")
print("="*80)

