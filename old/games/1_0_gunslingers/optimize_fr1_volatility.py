#!/usr/bin/env python3
"""
Analyze FR1.csv symbol distribution and apply volatility-increasing modifications.

Goal: Reduce small/medium wins, increase spiky premium outcomes while maintaining ~384× avg.
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)  # Reproducible results

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Read current reel
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Analyze BEFORE
reel_symbols = [defaultdict(int) for _ in range(5)]
overall_symbols = defaultdict(int)

for row in rows:
    for reel_idx, sym in enumerate(row):
        reel_symbols[reel_idx][sym] += 1
        overall_symbols[sym] += 1

total = sum(overall_symbols.values())

print("="*80)
print("FR1.CSV SYMBOL ANALYSIS - BEFORE MODIFICATION")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total} (across all reels)")
print(f"\n{'Symbol':<8} {'Count':<8} {'Percentage':<12} {'Per Reel Avg':<15}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    count = overall_symbols[sym]
    pct = (count / total * 100) if total > 0 else 0
    per_reel_avg = count / 5
    print(f"{sym:<8} {count:<8} {pct:>10.2f}% {per_reel_avg:>14.1f}")

print(f"\nPer-Reel Symbol Counts:")
print("-" * 80)
for reel_idx in range(5):
    print(f"\nReel {reel_idx + 1} ({len(rows)} positions):")
    for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
        count = reel_symbols[reel_idx][sym]
        if count > 0:
            pct = (count / len(rows) * 100)
            print(f"  {sym}: {count:3d} ({pct:5.2f}%)")

premium_total = sum(overall_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])
low_total = sum(overall_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
special_total = sum(overall_symbols[s] for s in ['W', 'VS', 'S'])

print(f"\nCategory Totals:")
print(f"  Premiums (H1-H4): {premium_total} ({premium_total/total*100:.1f}%)")
print(f"  Lows (L1-L5): {low_total} ({low_total/total*100:.1f}%)")
print(f"  Specials (W,VS,S): {special_total} ({special_total/total*100:.1f}%)")

# Identify low clusters (rows with 3+ low symbols)
low_cluster_rows = []
for i, row in enumerate(rows):
    low_count = sum(1 for sym in row if sym in ['L1', 'L2', 'L3'])
    if low_count >= 3:
        low_cluster_rows.append((i, low_count, row))

low_cluster_rows.sort(key=lambda x: x[1], reverse=True)
print(f"\nLow Clusters: {len(low_cluster_rows)} rows with 3+ L1/L2/L3 symbols")
print(f"  Worst clusters: {[f'Row {r[0]+1} ({r[1]} lows)' for r in low_cluster_rows[:10]]}")

# MODIFICATION PLAN
print("\n" + "="*80)
print("MODIFICATION PLAN")
print("="*80)

# Strategy:
# 1. Aggressively reduce L1 (lowest paying): Replace ~50% with H3
# 2. Reduce L2: Replace ~40% with H3/H2
# 3. Reduce L3: Replace ~35% with H2/H1
# 4. Slightly reduce L4: Replace ~15% with H3
# 5. Reduce W by ~12%: Replace with H2/H3 to offset EV
# 6. Keep VS and S unchanged
# 7. Focus on breaking up low clusters

targets = {
    'L1': {'reduction_pct': 0.50, 'replacements': ['H3'] * 8 + ['H2'] * 2},  # 80% H3, 20% H2
    'L2': {'reduction_pct': 0.40, 'replacements': ['H3'] * 6 + ['H2'] * 4},  # 60% H3, 40% H2
    'L3': {'reduction_pct': 0.35, 'replacements': ['H2'] * 7 + ['H1'] * 3},  # 70% H2, 30% H1
    'L4': {'reduction_pct': 0.15, 'replacements': ['H3'] * 8 + ['H2'] * 2},  # 80% H3, 20% H2
    'W':  {'reduction_pct': 0.12, 'replacements': ['H2'] * 5 + ['H3'] * 5},  # 50% H2, 50% H3
}

print("\nReplacement Targets:")
for sym, config in targets.items():
    current = overall_symbols[sym]
    target_reduction = int(current * config['reduction_pct'])
    print(f"  {sym}: {current} -> {current - target_reduction} (reduce by {target_reduction}, {config['reduction_pct']*100:.0f}%)")

# Create modified copy
modified_rows = [row.copy() for row in rows]
replacement_counts = defaultdict(int)

# Phase 1: Break up low clusters (highest priority)
print("\nPhase 1: Breaking up low clusters...")
for row_idx, low_count, row in low_cluster_rows[:25]:  # Process top 25 worst clusters
    for reel_idx, sym in enumerate(row):
        if sym in ['L1', 'L2', 'L3']:
            config = targets.get(sym)
            if config and replacement_counts[sym] < int(overall_symbols[sym] * config['reduction_pct']):
                new_sym = random.choice(config['replacements'])
                modified_rows[row_idx][reel_idx] = new_sym
                replacement_counts[sym] += 1

# Phase 2: Replace scattered low symbols
print("Phase 2: Replacing scattered low symbols...")
processed_cluster_rows = set(r[0] for r in low_cluster_rows[:25])

for row_idx, row in enumerate(modified_rows):
    if row_idx in processed_cluster_rows:
        continue
    
    for reel_idx, sym in enumerate(row):
        if sym in ['L1', 'L2', 'L3', 'L4']:
            config = targets.get(sym)
            if config and replacement_counts[sym] < int(overall_symbols[sym] * config['reduction_pct']):
                # Random chance to replace (to avoid over-replacement)
                if random.random() < 0.6:  # 60% chance
                    new_sym = random.choice(config['replacements'])
                    modified_rows[row_idx][reel_idx] = new_sym
                    replacement_counts[sym] += 1

# Phase 3: Reduce wilds slightly
print("Phase 3: Reducing wilds...")
for row_idx, row in enumerate(modified_rows):
    for reel_idx, sym in enumerate(row):
        if sym == 'W':
            config = targets['W']
            if replacement_counts['W'] < int(overall_symbols['W'] * config['reduction_pct']):
                if random.random() < 0.4:  # 40% chance per wild
                    new_sym = random.choice(config['replacements'])
                    modified_rows[row_idx][reel_idx] = new_sym
                    replacement_counts['W'] += 1

print(f"\nReplacements made:")
for sym in ['L1', 'L2', 'L3', 'L4', 'W']:
    print(f"  {sym}: {replacement_counts[sym]}")

# Analyze AFTER
after_reel_symbols = [defaultdict(int) for _ in range(5)]
after_overall_symbols = defaultdict(int)

for row in modified_rows:
    for reel_idx, sym in enumerate(row):
        after_reel_symbols[reel_idx][sym] += 1
        after_overall_symbols[sym] += 1

after_total = sum(after_overall_symbols.values())

print("\n" + "="*80)
print("AFTER MODIFICATION - SYMBOL COUNTS")
print("="*80)
print(f"\n{'Symbol':<8} {'Before':<10} {'After':<10} {'Change':<10} {'% Change':<12}")
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

# Write modified file
print("\n" + "="*80)
print("APPLYING CHANGES")
print("="*80)

# Create backup if it doesn't exist
if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)
    print(f"✓ Created backup: {backup_file}")

# Write modified file
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified_rows:
        writer.writerow(row)

print(f"✓ Modified FR1.csv written")
print(f"✓ Total symbol replacements: {sum(replacement_counts.values())}")

print("\n" + "="*80)
print("MODIFICATION COMPLETE")
print("="*80)
print("\nSummary of changes:")
print(f"  - Reduced L1-L3 by ~{sum(replacement_counts[s] for s in ['L1','L2','L3'])} symbols")
print(f"  - Increased H1-H3 by ~{sum(replacement_counts[s] for s in ['L1','L2','L3','L4','W'])} symbols")
print(f"  - Reduced wilds by {replacement_counts['W']} symbols")
print(f"  - VS and S counts unchanged")
print("\nExpected impact:")
print("  - More dead spins (fewer low symbols)")
print("  - More premium wins (higher H1-H3 density)")
print("  - Increased volatility (spikier distribution)")
print("  - Average should remain ~384× (wild reduction offsets premium increase)")

