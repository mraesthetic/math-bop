#!/usr/bin/env python3
"""
Add 3 L1 symbols to FR1.csv (superbonus reelset).

Strategy: Convert 3 L4 or L5 symbols to L1 to maintain total symbol count.
"""

import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_l1_add')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

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

print("="*80)
print("ADDING 3 L1 SYMBOLS TO FR1.CSV")
print("="*80)
print(f"\nCurrent L1 count: {current.get('L1', 0)}")
print(f"Target L1 count: {current.get('L1', 0) + 3}")
print(f"\nCurrent symbol counts:")
for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    count = current.get(sym, 0)
    print(f"  {sym}: {count}")

# Create working copy
modified = [row.copy() for row in rows]

# Strategy: Convert 3 L4 or L5 to L1
# Prefer L4 over L5 for conversion
l1_to_add = 3
l1_added = 0

print(f"\n{'='*80}")
print("CONVERTING L4/L5 → L1")
print("="*80)

# First, try to convert L4
for row_idx, row in enumerate(modified):
    if l1_added >= l1_to_add:
        break
    for reel_idx, sym in enumerate(row):
        if sym == 'L4' and l1_added < l1_to_add:
            # Check if row already has reasonable L1 density (max 3-4 L1 per row)
            row_l1_count = sum(1 for s in modified[row_idx] if s == 'L1')
            if row_l1_count < 4:
                modified[row_idx][reel_idx] = 'L1'
                l1_added += 1
                if l1_added >= l1_to_add:
                    break

# If still need more, convert L5
if l1_added < l1_to_add:
    for row_idx, row in enumerate(modified):
        if l1_added >= l1_to_add:
            break
        for reel_idx, sym in enumerate(row):
            if sym == 'L5' and l1_added < l1_to_add:
                row_l1_count = sum(1 for s in modified[row_idx] if s == 'L1')
                if row_l1_count < 4:
                    modified[row_idx][reel_idx] = 'L1'
                    l1_added += 1
                    if l1_added >= l1_to_add:
                        break

print(f"✓ Added {l1_added} L1 symbols (converted from L4/L5)")

# Count after modifications
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("AFTER ADDING 3 L1 SYMBOLS")
print("="*80)
print(f"\n{'Symbol':<8} {'Before':<10} {'After':<10} {'Change':<10}")
print("-" * 50)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    bef = current.get(sym, 0)
    aft = after.get(sym, 0)
    chg = aft - bef
    if chg != 0:
        print(f"{sym:<8} {bef:<10} {aft:<10} {chg:+10}")

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

print(f"✓ Updated FR1.csv saved")
print(f"\nSummary:")
print(f"  L1: {current.get('L1', 0)} → {after.get('L1', 0)} (+{after.get('L1', 0) - current.get('L1', 0)})")
print(f"  L4/L5: Converted {l1_added} symbols to L1")
print(f"\n✓ Done! 3 L1 symbols added to FR1.csv")

