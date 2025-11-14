#!/usr/bin/env python3
"""
Analyze FR1.csv and modify it to increase volatility.

Strategy:
1. Reduce low symbols (especially L1-L3) - replace with premiums or blanks
2. Increase premium symbols (H1-H3)
3. Slightly reduce wilds to offset EV increase
4. Break up repetitive low-line patterns
5. Keep VS and S counts reasonable
"""

import csv
import os
from collections import defaultdict
from copy import deepcopy

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Read current reel
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(row)

print(f"Read {len(rows)} rows from FR1.csv\n")

# Analyze current distribution
reel_symbols = [defaultdict(int) for _ in range(5)]
overall_symbols = defaultdict(int)

for row in rows:
    for reel_idx, sym in enumerate(row):
        reel_symbols[reel_idx][sym] += 1
        overall_symbols[sym] += 1

total_per_reel = [sum(reel_symbols[i].values()) for i in range(5)]
total_overall = sum(overall_symbols.values())

# Print BEFORE analysis
print("="*80)
print("BEFORE MODIFICATION")
print("="*80)
print(f"\nOverall Symbol Counts:")
print(f"{'Symbol':<8} {'Count':<8} {'Percentage':<12}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    count = overall_symbols[sym]
    pct = (count / total_overall * 100) if total_overall > 0 else 0
    print(f"{sym:<8} {count:<8} {pct:>10.2f}%")

premium_total = sum(overall_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])
low_total = sum(overall_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
special_total = sum(overall_symbols[s] for s in ['W', 'VS', 'S'])

print(f"\nCategory Totals:")
print(f"  Premiums (H1-H4): {premium_total} ({premium_total/total_overall*100:.1f}%)")
print(f"  Lows (L1-L5): {low_total} ({low_total/total_overall*100:.1f}%)")
print(f"  Specials (W,VS,S): {special_total} ({special_total/total_overall*100:.1f}%)")

print(f"\nPer-Reel Symbol Counts:")
print("-" * 80)
for reel_idx in range(5):
    print(f"\nReel {reel_idx + 1}:")
    for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
        count = reel_symbols[reel_idx][sym]
        pct = (count / total_per_reel[reel_idx] * 100) if total_per_reel[reel_idx] > 0 else 0
        if count > 0:
            print(f"  {sym}: {count} ({pct:.1f}%)")

# MODIFICATION STRATEGY
print("\n" + "="*80)
print("MODIFICATION STRATEGY")
print("="*80)

# Create modified rows
modified_rows = deepcopy(rows)

# Track changes
changes_made = 0
replacement_map = defaultdict(int)

# Strategy:
# 1. Replace L1-L3 (lowest paying lows) with premiums or blanks
# 2. Replace some L4-L5 with premiums
# 3. Replace some W with premiums (to offset EV)
# 4. Break up low clusters

# Priority replacements (in order):
# - L1 -> H3 or H2 (most frequent low -> mid-high premium)
# - L2 -> H3 or H2
# - L3 -> H2 or H1
# - L4 -> H3 or H2
# - W -> H2 or H3 (reduce wilds slightly)

# Target: Reduce L1-L3 by ~40-50%, increase H1-H3 by ~30-40%
# Keep VS and S counts the same

low_symbols_to_replace = ['L1', 'L2', 'L3']
premium_symbols_to_add = ['H1', 'H2', 'H3']

# Calculate replacement targets
current_l1_l3_total = sum(overall_symbols[s] for s in ['L1', 'L2', 'L3'])
target_reduction = int(current_l1_l3_total * 0.45)  # Reduce by 45%

current_h1_h3_total = sum(overall_symbols[s] for s in ['H1', 'H2', 'H3'])
target_increase = int(current_h1_h3_total * 0.35)  # Increase by 35%

print(f"\nReplacement Targets:")
print(f"  Reduce L1-L3 by ~45%: {current_l1_l3_total} -> {current_l1_l3_total - target_reduction}")
print(f"  Increase H1-H3 by ~35%: {current_h1_h3_total} -> {current_h1_h3_total + target_increase}")

# Make replacements row by row
# Strategy: Replace lows in rows with many lows first (break up clusters)
# Then replace scattered lows

rows_with_many_lows = []
for i, row in enumerate(modified_rows):
    low_count = sum(1 for sym in row if sym in ['L1', 'L2', 'L3'])
    if low_count >= 3:
        rows_with_many_lows.append((i, low_count, row))

# Sort by low count (highest first)
rows_with_many_lows.sort(key=lambda x: x[1], reverse=True)

print(f"\nFound {len(rows_with_many_lows)} rows with 3+ lows")

# Replacement mapping (weighted by frequency and value)
replacement_preferences = {
    'L1': ['H3', 'H2', 'H3', 'H2', 'H1'],  # Mostly H3/H2, some H1
    'L2': ['H3', 'H2', 'H3', 'H1', 'H2'],  # Mostly H3/H2, some H1
    'L3': ['H2', 'H1', 'H2', 'H3', 'H1'],  # Mostly H2/H1, some H3
    'L4': ['H3', 'H2'],  # Occasional L4 -> premium
    'W': ['H2', 'H3'],  # Reduce some wilds
}

import random
random.seed(42)  # For reproducibility

# Replace in high-low clusters first
replacements_made = {'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0, 'W': 0}

for row_idx, low_count, row in rows_with_many_lows[:len(rows_with_many_lows)//2]:  # Process half of clusters
    for reel_idx, sym in enumerate(row):
        if sym in ['L1', 'L2', 'L3'] and replacements_made[sym] < target_reduction // 3:
            # Replace with premium
            replacements = replacement_preferences.get(sym, ['H3'])
            new_sym = random.choice(replacements)
            modified_rows[row_idx][reel_idx] = new_sym
            replacements_made[sym] += 1
            changes_made += 1
            replacement_map[f"{sym}->{new_sym}"] += 1

# Replace scattered lows throughout the reel
for row_idx, row in enumerate(modified_rows):
    if row_idx in [x[0] for x in rows_with_many_lows]:
        continue  # Skip already processed rows
    
    for reel_idx, sym in enumerate(row):
        if sym == 'L1' and replacements_made['L1'] < target_reduction:
            new_sym = random.choice(replacement_preferences['L1'])
            modified_rows[row_idx][reel_idx] = new_sym
            replacements_made['L1'] += 1
            changes_made += 1
            replacement_map[f"L1->{new_sym}"] += 1
        elif sym == 'L2' and replacements_made['L2'] < target_reduction:
            new_sym = random.choice(replacement_preferences['L2'])
            modified_rows[row_idx][reel_idx] = new_sym
            replacements_made['L2'] += 1
            changes_made += 1
            replacement_map[f"L2->{new_sym}"] += 1
        elif sym == 'L3' and replacements_made['L3'] < target_reduction:
            new_sym = random.choice(replacement_preferences['L3'])
            modified_rows[row_idx][reel_idx] = new_sym
            replacements_made['L3'] += 1
            changes_made += 1
            replacement_map[f"L3->{new_sym}"] += 1

# Replace some wilds (to offset EV increase from premiums)
wild_replacements = int(overall_symbols['W'] * 0.10)  # Replace 10% of wilds
wild_replaced = 0

for row_idx, row in enumerate(modified_rows):
    for reel_idx, sym in enumerate(row):
        if sym == 'W' and wild_replaced < wild_replacements:
            # Replace with H2 or H3 (mid premiums)
            new_sym = random.choice(['H2', 'H3'])
            modified_rows[row_idx][reel_idx] = new_sym
            wild_replaced += 1
            changes_made += 1
            replacement_map[f"W->{new_sym}"] += 1

print(f"\nMade {changes_made} symbol replacements")
print(f"\nReplacement breakdown:")
for replacement, count in sorted(replacement_map.items()):
    print(f"  {replacement}: {count}")

# Analyze AFTER distribution
after_reel_symbols = [defaultdict(int) for _ in range(5)]
after_overall_symbols = defaultdict(int)

for row in modified_rows:
    for reel_idx, sym in enumerate(row):
        after_reel_symbols[reel_idx][sym] += 1
        after_overall_symbols[sym] += 1

after_total_per_reel = [sum(after_reel_symbols[i].values()) for i in range(5)]
after_total_overall = sum(after_overall_symbols.values())

# Print AFTER analysis
print("\n" + "="*80)
print("AFTER MODIFICATION")
print("="*80)
print(f"\nOverall Symbol Counts:")
print(f"{'Symbol':<8} {'Before':<10} {'After':<10} {'Change':<10} {'% Change':<12}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    before_count = overall_symbols[sym]
    after_count = after_overall_symbols[sym]
    change = after_count - before_count
    pct_change = (change / before_count * 100) if before_count > 0 else 0
    print(f"{sym:<8} {before_count:<10} {after_count:<10} {change:+10} {pct_change:>+11.1f}%")

after_premium_total = sum(after_overall_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])
after_low_total = sum(after_overall_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
after_special_total = sum(after_overall_symbols[s] for s in ['W', 'VS', 'S'])

print(f"\nCategory Totals:")
print(f"{'Category':<15} {'Before':<15} {'After':<15} {'Change':<15} {'% Change':<12}")
print("-" * 80)
print(f"{'Premiums':<15} {premium_total:<15} {after_premium_total:<15} {after_premium_total-premium_total:+15} {(after_premium_total-premium_total)/premium_total*100:>+11.1f}%")
print(f"{'Lows':<15} {low_total:<15} {after_low_total:<15} {after_low_total-low_total:+15} {(after_low_total-low_total)/low_total*100:>+11.1f}%")
print(f"{'Specials':<15} {special_total:<15} {after_special_total:<15} {after_special_total-special_total:+15} {(after_special_total-special_total)/special_total*100:>+11.1f}%")

print(f"\nPer-Reel Symbol Counts (AFTER):")
print("-" * 80)
for reel_idx in range(5):
    print(f"\nReel {reel_idx + 1}:")
    print(f"{'Symbol':<8} {'Before':<10} {'After':<10} {'Change':<10}")
    print("-" * 40)
    for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
        before_count = reel_symbols[reel_idx][sym]
        after_count = after_reel_symbols[reel_idx][sym]
        if before_count > 0 or after_count > 0:
            change = after_count - before_count
            print(f"  {sym:<8} {before_count:<10} {after_count:<10} {change:+10}")

# Write modified reel
print(f"\n" + "="*80)
print("WRITING MODIFIED FR1.CSV")
print("="*80)

backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup')
if not os.path.exists(backup_file):
    # Create backup
    import shutil
    shutil.copy(input_file, backup_file)
    print(f"Created backup: {backup_file}")

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified_rows:
        writer.writerow(row)

print(f"✓ Modified FR1.csv written to {output_file}")
print(f"\nTotal changes: {changes_made} symbol replacements")

