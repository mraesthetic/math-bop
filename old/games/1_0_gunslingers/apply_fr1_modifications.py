import csv
import os
import shutil
import random
from collections import defaultdict

random.seed(42)

# File paths
base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')

# Read reel
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Analyze BEFORE
overall_symbols = defaultdict(int)
for row in rows:
    for sym in row:
        overall_symbols[sym] += 1

total = sum(overall_symbols.values())
print("BEFORE:")
for sym in ['H1','H2','H3','H4','L1','L2','L3','L4','L5','W','VS','S']:
    count = overall_symbols[sym]
    print(f"  {sym}: {count} ({count/total*100:.1f}%)")

# Modification
modified_rows = [row.copy() for row in rows]

# Find low clusters
low_clusters = []
for i, row in enumerate(rows):
    low_count = sum(1 for s in row if s in ['L1','L2','L3'])
    if low_count >= 3:
        low_clusters.append((i, low_count))
low_clusters.sort(key=lambda x: x[1], reverse=True)

# Replacements
targets = {
    'L1': {'pct': 0.50, 'repl': ['H3']*8 + ['H2']*2},
    'L2': {'pct': 0.40, 'repl': ['H3']*6 + ['H2']*4},
    'L3': {'pct': 0.35, 'repl': ['H2']*7 + ['H1']*3},
    'L4': {'pct': 0.15, 'repl': ['H3']*8 + ['H2']*2},
    'W':  {'pct': 0.12, 'repl': ['H2']*5 + ['H3']*5},
}

counts = defaultdict(int)

# Phase 1: Clusters
for idx, _ in low_clusters[:25]:
    for reel_idx, sym in enumerate(modified_rows[idx]):
        if sym in targets and counts[sym] < int(overall_symbols[sym] * targets[sym]['pct']):
            modified_rows[idx][reel_idx] = random.choice(targets[sym]['repl'])
            counts[sym] += 1

# Phase 2: Scattered
processed = set(r[0] for r in low_clusters[:25])
for idx, row in enumerate(modified_rows):
    if idx in processed:
        continue
    for reel_idx, sym in enumerate(row):
        if sym in ['L1','L2','L3','L4'] and counts[sym] < int(overall_symbols[sym] * targets[sym]['pct']):
            if random.random() < 0.6:
                modified_rows[idx][reel_idx] = random.choice(targets[sym]['repl'])
                counts[sym] += 1

# Phase 3: Wilds
for idx, row in enumerate(modified_rows):
    for reel_idx, sym in enumerate(row):
        if sym == 'W' and counts['W'] < int(overall_symbols['W'] * targets['W']['pct']):
            if random.random() < 0.4:
                modified_rows[idx][reel_idx] = random.choice(targets['W']['repl'])
                counts['W'] += 1

# Analyze AFTER
after_symbols = defaultdict(int)
for row in modified_rows:
    for sym in row:
        after_symbols[sym] += 1

print("\nAFTER:")
for sym in ['H1','H2','H3','H4','L1','L2','L3','L4','L5','W','VS','S']:
    before = overall_symbols[sym]
    after = after_symbols[sym]
    print(f"  {sym}: {before} -> {after} ({after-before:+d})")

# Backup and write
if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(modified_rows)

print(f"\n✓ Modified {len(modified_rows)} rows")
print(f"✓ Backup: {backup_file}")
print(f"✓ Output: {output_file}")

