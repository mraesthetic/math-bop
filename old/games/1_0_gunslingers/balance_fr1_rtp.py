#!/usr/bin/env python3
"""
Balance FR1.csv RTP by restoring some low symbols and wilds.

Strategy:
- Restore L1 reduction from 50% to 30-35%
- Restore L2 reduction from 40% to 25-30%
- Restore L3 reduction from 35% to 20-25%
- Restore W to near-original (from -12% to -5% or baseline)
- Keep current premium density (H1-H3)
- Preserve VS and S
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)  # Reproducible

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_current')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Original baseline counts (from documentation)
ORIGINAL_BASELINE = {
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

# Read current (modified) reel
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Analyze CURRENT (after aggressive modification)
current_symbols = defaultdict(int)
for row in rows:
    for sym in row:
        current_symbols[sym] += 1

total = sum(current_symbols.values())

print("="*80)
print("FR1.CSV RTP BALANCE CORRECTION")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")

print(f"\n{'='*80}")
print("CURRENT STATE (After Aggressive Modification)")
print("="*80)
print(f"\n{'Symbol':<8} {'Current':<10} {'Original':<10} {'Difference':<12}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    current = current_symbols[sym]
    original = ORIGINAL_BASELINE.get(sym, 0)
    diff = current - original
    print(f"{sym:<8} {current:<10} {original:<10} {diff:+12}")

# Calculate target counts for correction
print(f"\n{'='*80}")
print("TARGET COUNTS (After Balance Correction)")
print("="*80)

# Targets based on reduction percentages:
# L1: Original 186, target reduction 30-35% → 121-130 (current ~100, need +20-30)
# L2: Original 84, target reduction 25-30% → 59-63 (current ~50, need +9-13)
# L3: Original 75, target reduction 20-25% → 56-60 (current ~60, need -4 to +4, keep similar)
# W: Original 18, target -5% → 17 (current ~16, need +1)

target_counts = {
    'L1': int(ORIGINAL_BASELINE['L1'] * 0.67),  # 33% reduction → 125
    'L2': int(ORIGINAL_BASELINE['L2'] * 0.73),  # 27% reduction → 61
    'L3': int(ORIGINAL_BASELINE['L3'] * 0.77),  # 23% reduction → 58
    'W': int(ORIGINAL_BASELINE['W'] * 0.95),    # 5% reduction → 17
}

# Keep current premium counts (they're good)
target_counts['H1'] = current_symbols['H1']
target_counts['H2'] = current_symbols['H2']
target_counts['H3'] = current_symbols['H3']
target_counts['H4'] = current_symbols['H4']
target_counts['L4'] = current_symbols['L4']  # Keep as is
target_counts['L5'] = current_symbols['L5']  # Keep as is
target_counts['VS'] = current_symbols['VS']  # Preserve
target_counts['S'] = current_symbols['S']    # Preserve

# Calculate needed changes
needed_changes = {
    'L1': target_counts['L1'] - current_symbols['L1'],
    'L2': target_counts['L2'] - current_symbols['L2'],
    'L3': target_counts['L3'] - current_symbols['L3'],
    'W': target_counts['W'] - current_symbols['W'],
}

# To restore lows, we need to convert some premiums back to lows
# Priority: Convert H3 back to L1 (since H3 was added the most)
# Convert some H2/H3 back to L2
# Convert some H2 back to L3

print(f"\nNeeded Changes:")
for sym, needed in needed_changes.items():
    print(f"  {sym}: {current_symbols[sym]} → {target_counts[sym]} (need {needed:+d})")

# Create modified copy
modified_rows = [row.copy() for row in rows]

# Phase 1: Restore wilds first (convert some H2/H3 back to W)
w_needed = needed_changes['W']
w_restored = 0

if w_needed > 0:
    print(f"\nPhase 1: Restoring {w_needed} wilds...")
    for row_idx, row in enumerate(modified_rows):
        if w_restored >= w_needed:
            break
        for reel_idx, sym in enumerate(row):
            # Convert H2 or H3 back to W (prefer H3 since it was added most)
            if sym in ['H3', 'H2'] and w_restored < w_needed:
                if random.random() < 0.3:  # 30% chance per premium
                    modified_rows[row_idx][reel_idx] = 'W'
                    w_restored += 1
                    if w_restored >= w_needed:
                        break

print(f"  Restored {w_restored} wilds")

# Phase 2: Restore L1 (convert H3 back to L1)
l1_needed = needed_changes['L1']
l1_restored = 0

if l1_needed > 0:
    print(f"\nPhase 2: Restoring {l1_needed} L1 symbols...")
    # Prefer converting H3 (which was added the most) back to L1
    for row_idx, row in enumerate(modified_rows):
        if l1_restored >= l1_needed:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'H3' and l1_restored < l1_needed:
                # Don't convert if it would create a low cluster
                # Check surrounding symbols
                row_lows = sum(1 for s in row if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:  # Avoid creating clusters
                    if random.random() < 0.4:  # 40% chance
                        modified_rows[row_idx][reel_idx] = 'L1'
                        l1_restored += 1
                        if l1_restored >= l1_needed:
                            break

print(f"  Restored {l1_restored} L1 symbols")

# Phase 3: Restore L2 (convert H3/H2 back to L2)
l2_needed = needed_changes['L2']
l2_restored = 0

if l2_needed > 0:
    print(f"\nPhase 3: Restoring {l2_needed} L2 symbols...")
    for row_idx, row in enumerate(modified_rows):
        if l2_restored >= l2_needed:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H3', 'H2'] and l2_restored < l2_needed:
                row_lows = sum(1 for s in row if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:
                    if random.random() < 0.3:  # 30% chance
                        modified_rows[row_idx][reel_idx] = 'L2'
                        l2_restored += 1
                        if l2_restored >= l2_needed:
                            break

print(f"  Restored {l2_restored} L2 symbols")

# Phase 4: Restore L3 (convert H2/H1 back to L3, but only if needed)
l3_needed = needed_changes['L3']
l3_restored = 0

if l3_needed > 0:
    print(f"\nPhase 4: Restoring {l3_needed} L3 symbols...")
    for row_idx, row in enumerate(modified_rows):
        if l3_restored >= l3_needed:
            break
        for reel_idx, sym in enumerate(row):
            if sym in ['H2', 'H1'] and l3_restored < l3_needed:
                row_lows = sum(1 for s in row if s in ['L1', 'L2', 'L3'])
                if row_lows < 4:
                    if random.random() < 0.25:  # 25% chance
                        modified_rows[row_idx][reel_idx] = 'L3'
                        l3_restored += 1
                        if l3_restored >= l3_needed:
                            break

print(f"  Restored {l3_restored} L3 symbols")

# Analyze AFTER correction
after_symbols = defaultdict(int)
for row in modified_rows:
    for sym in row:
        after_symbols[sym] += 1

print(f"\n{'='*80}")
print("AFTER BALANCE CORRECTION")
print("="*80)
print(f"\n{'Symbol':<8} {'Original':<10} {'Current':<10} {'After':<10} {'Change':<12}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    original = ORIGINAL_BASELINE.get(sym, 0)
    current = current_symbols[sym]
    after = after_symbols[sym]
    change = after - current
    print(f"{sym:<8} {original:<10} {current:<10} {after:<10} {change:+12}")

# Category totals
original_premium = sum(ORIGINAL_BASELINE[s] for s in ['H1', 'H2', 'H3', 'H4'])
current_premium = sum(current_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])
after_premium = sum(after_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])

original_low = sum(ORIGINAL_BASELINE[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
current_low = sum(current_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
after_low = sum(after_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])

original_special = sum(ORIGINAL_BASELINE[s] for s in ['W', 'VS', 'S'])
current_special = sum(current_symbols[s] for s in ['W', 'VS', 'S'])
after_special = sum(after_symbols[s] for s in ['W', 'VS', 'S'])

print(f"\nCategory Totals:")
print(f"{'Category':<15} {'Original':<12} {'Current':<12} {'After':<12} {'Change':<12}")
print("-" * 80)
print(f"{'Premiums':<15} {original_premium:<12} {current_premium:<12} {after_premium:<12} {after_premium-current_premium:+12}")
print(f"{'Lows':<15} {original_low:<12} {current_low:<12} {after_low:<12} {after_low-current_low:+12}")
print(f"{'Specials':<15} {original_special:<12} {current_special:<12} {after_special:<12} {after_special-current_special:+12}")

# Estimate expected average
# Rough estimate: More lows + more wilds should increase base win frequency
# Current avg: 255×, need to get to ~384×
# That's a 50.6% increase needed
# Restoring ~40-50 low symbols + ~1-2 wilds should help significantly

# Very rough estimate based on symbol count changes
low_restoration = after_low - current_low
wild_restoration = after_symbols['W'] - current_symbols['W']

print(f"\n{'='*80}")
print("EXPECTED IMPACT ESTIMATE")
print("="*80)

# Rough calculation: Each low symbol restored adds base win potential
# Each wild restored adds win connectivity
# Estimate: restoring ~40-50 symbols should add ~50-70× to average

estimated_avg_increase = (low_restoration * 1.2) + (wild_restoration * 3.0)  # Rough multipliers
estimated_new_avg = 255.14 + estimated_avg_increase

print(f"\nSymbol Restoration:")
print(f"  Low symbols restored: {low_restoration:+d}")
print(f"  Wilds restored: {wild_restoration:+d}")
print(f"\nEstimated Impact:")
print(f"  Current average: 255.14×")
print(f"  Estimated new average: ~{estimated_new_avg:.1f}×")
print(f"  Estimated increase: +{estimated_avg_increase:.1f}×")
print(f"\nTarget Range: 379× - 389× (384× ± 5×)")
if 379 <= estimated_new_avg <= 389:
    print(f"  Status: ✅ Within target range (estimate)")
elif estimated_new_avg < 379:
    print(f"  Status: ⚠️  Still below target (may need more restoration)")
else:
    print(f"  Status: ⚠️  May exceed target (monitor carefully)")

# Write modified file
print(f"\n{'='*80}")
print("APPLYING CORRECTIONS")
print("="*80)

# Create backup of current state
if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)
    print(f"✓ Created backup: {backup_file}")

# Write corrected file
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified_rows:
        writer.writerow(row)

print(f"✓ Corrected FR1.csv written")
print(f"\nSummary of corrections:")
print(f"  L1 restored: {l1_restored} symbols")
print(f"  L2 restored: {l2_restored} symbols")
print(f"  L3 restored: {l3_restored} symbols")
print(f"  W restored: {w_restored} symbols")
print(f"  Total symbols restored: {l1_restored + l2_restored + l3_restored + w_restored}")

print(f"\n{'='*80}")
print("CORRECTION COMPLETE")
print("="*80)
print("\nNext step: Run simulation to verify average is closer to 384× target")

