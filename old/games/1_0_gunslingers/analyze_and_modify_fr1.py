#!/usr/bin/env python3
"""Analyze and modify FR1.csv for increased volatility."""

import csv
import os
from collections import defaultdict

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Read reel
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
print("BEFORE MODIFICATION - FR1.CSV SYMBOL COUNTS")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")
print(f"\n{'Symbol':<8} {'Count':<8} {'Percentage':<12}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    count = overall_symbols[sym]
    pct = (count / total * 100) if total > 0 else 0
    print(f"{sym:<8} {count:<8} {pct:>10.2f}%")

print(f"\nPer-Reel Symbol Counts:")
print("-" * 80)
for reel_idx in range(5):
    print(f"\nReel {reel_idx + 1} (Total: {len(rows)} symbols):")
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

# MODIFY REEL
print("\n" + "="*80)
print("MODIFYING REEL FOR INCREASED VOLATILITY")
print("="*80)

# Create modified copy
modified_rows = [row.copy() for row in rows]

# Strategy:
# 1. Replace L1-L3 with premiums (especially in low clusters)
# 2. Replace some L4 with premiums
# 3. Replace some W with premiums to offset EV
# 4. Keep VS and S unchanged

import random
random.seed(42)  # Reproducible

# Find rows with many lows (clusters to break up)
low_cluster_rows = []
for i, row in enumerate(rows):
    low_count = sum(1 for sym in row if sym in ['L1', 'L2', 'L3'])
    if low_count >= 3:
        low_cluster_rows.append((i, low_count))

low_cluster_rows.sort(key=lambda x: x[1], reverse=True)

# Replacement strategy
# L1 -> H3 (most common replacement, keeps volatility)
# L2 -> H3 or H2
# L3 -> H2 or H1 (higher premium)
# L4 -> occasional H3
# W -> H2 or H3 (reduce wilds slightly)

replacements = 0
replacement_log = []

# Replace in clusters first (highest impact)
for row_idx, low_count in low_cluster_rows[:30]:  # Process top 30 clusters
    row = modified_rows[row_idx]
    for reel_idx, sym in enumerate(row):
        if sym == 'L1':
            modified_rows[row_idx][reel_idx] = 'H3'
            replacements += 1
            replacement_log.append(f"Row {row_idx+1}, Reel {reel_idx+1}: L1 -> H3")
        elif sym == 'L2' and random.random() < 0.7:  # 70% of L2
            modified_rows[row_idx][reel_idx] = random.choice(['H3', 'H2'])
            replacements += 1
            replacement_log.append(f"Row {row_idx+1}, Reel {reel_idx+1}: L2 -> {modified_rows[row_idx][reel_idx]}")
        elif sym == 'L3' and random.random() < 0.6:  # 60% of L3
            modified_rows[row_idx][reel_idx] = random.choice(['H2', 'H1'])
            replacements += 1
            replacement_log.append(f"Row {row_idx+1}, Reel {reel_idx+1}: L3 -> {modified_rows[row_idx][reel_idx]}")

# Replace scattered L1 throughout (aggressive reduction)
l1_target_reduction = int(overall_symbols['L1'] * 0.5)  # Reduce L1 by 50%
l1_replaced = sum(1 for log in replacement_log if 'L1 ->' in log)

for row_idx, row in enumerate(modified_rows):
    if l1_replaced >= l1_target_reduction:
        break
    if row_idx in [x[0] for x in low_cluster_rows[:30]]:
        continue  # Skip already processed
    
    for reel_idx, sym in enumerate(row):
        if sym == 'L1' and l1_replaced < l1_target_reduction:
            modified_rows[row_idx][reel_idx] = 'H3'
            l1_replaced += 1
            replacements += 1

# Replace scattered L2 and L3
l2_target_reduction = int(overall_symbols['L2'] * 0.4)
l3_target_reduction = int(overall_symbols['L3'] * 0.4)

l2_replaced = sum(1 for log in replacement_log if 'L2 ->' in log)
l3_replaced = sum(1 for log in replacement_log if 'L3 ->' in log)

for row_idx, row in enumerate(modified_rows):
    if l2_replaced >= l2_target_reduction and l3_replaced >= l3_target_reduction:
        break
    if row_idx in [x[0] for x in low_cluster_rows[:30]]:
        continue
    
    for reel_idx, sym in enumerate(row):
        if sym == 'L2' and l2_replaced < l2_target_reduction and random.random() < 0.5:
            modified_rows[row_idx][reel_idx] = random.choice(['H3', 'H2'])
            l2_replaced += 1
            replacements += 1
        elif sym == 'L3' and l3_replaced < l3_target_reduction and random.random() < 0.5:
            modified_rows[row_idx][reel_idx] = random.choice(['H2', 'H1'])
            l3_replaced += 1
            replacements += 1

# Replace some wilds to offset EV increase (10% of wilds)
wild_target_reduction = int(overall_symbols['W'] * 0.10)
wild_replaced = 0

for row_idx, row in enumerate(modified_rows):
    if wild_replaced >= wild_target_reduction:
        break
    for reel_idx, sym in enumerate(row):
        if sym == 'W' and wild_replaced < wild_target_reduction and random.random() < 0.3:
            modified_rows[row_idx][reel_idx] = random.choice(['H2', 'H3'])
            wild_replaced += 1
            replacements += 1

print(f"\nMade {replacements} symbol replacements")
print(f"  L1 replaced: {l1_replaced}")
print(f"  L2 replaced: {l2_replaced}")
print(f"  L3 replaced: {l3_replaced}")
print(f"  W replaced: {wild_replaced}")

# Analyze AFTER
after_reel_symbols = [defaultdict(int) for _ in range(5)]
after_overall_symbols = defaultdict(int)

for row in modified_rows:
    for reel_idx, sym in enumerate(row):
        after_reel_symbols[reel_idx][sym] += 1
        after_overall_symbols[sym] += 1

after_total = sum(after_overall_symbols.values())

print("\n" + "="*80)
print("AFTER MODIFICATION - FR1.CSV SYMBOL COUNTS")
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
print("WRITING MODIFIED FR1.CSV")
print("="*80)

# Create backup
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup')
if not os.path.exists(backup_file):
    import shutil
    shutil.copy(input_file, backup_file)
    print(f"Created backup: {backup_file}")

output_file = os.path.join(base_path, 'reels', 'FR1.csv')
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified_rows:
        writer.writerow(row)

print(f"✓ Modified FR1.csv written")
print(f"✓ Total replacements: {replacements}")

