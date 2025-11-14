#!/usr/bin/env python3
"""Analyze FR1.csv symbol distribution per reel and overall."""

import csv
import os
from collections import defaultdict

base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, 'reels', 'FR1.csv')

# Initialize counters
reel_symbols = [defaultdict(int) for _ in range(5)]  # Per reel
overall_symbols = defaultdict(int)  # Overall
total_per_reel = [0] * 5
total_overall = 0
rows = 0

# Read and analyze
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 5:
            continue
        rows += 1
        for reel_idx, sym in enumerate(row):
            if sym:
                reel_symbols[reel_idx][sym] += 1
                overall_symbols[sym] += 1
                total_per_reel[reel_idx] += 1
                total_overall += 1

# Print analysis
print("="*80)
print("FR1.CSV SYMBOL ANALYSIS")
print("="*80)
print(f"\nTotal Rows: {rows}")
print(f"Total Symbols: {total_overall}")
print(f"Symbols per Reel: {total_per_reel}")
print()

# Per-reel breakdown
symbol_categories = {
    'Premium': ['H1', 'H2', 'H3', 'H4'],
    'Low': ['L1', 'L2', 'L3', 'L4', 'L5'],
    'Special': ['W', 'VS', 'S']
}

print("PER-REEL SYMBOL COUNTS")
print("="*80)
for reel_idx in range(5):
    print(f"\nReel {reel_idx + 1}:")
    print("-" * 80)
    print(f"{'Symbol':<8} {'Count':<8} {'Percentage':<12}")
    print("-" * 80)
    
    # Premiums
    print("  Premiums:")
    for sym in ['H1', 'H2', 'H3', 'H4']:
        count = reel_symbols[reel_idx][sym]
        pct = (count / total_per_reel[reel_idx] * 100) if total_per_reel[reel_idx] > 0 else 0
        print(f"    {sym:<8} {count:<8} {pct:>10.2f}%")
    
    # Lows
    print("  Lows:")
    for sym in ['L1', 'L2', 'L3', 'L4', 'L5']:
        count = reel_symbols[reel_idx][sym]
        pct = (count / total_per_reel[reel_idx] * 100) if total_per_reel[reel_idx] > 0 else 0
        print(f"    {sym:<8} {count:<8} {pct:>10.2f}%")
    
    # Specials
    print("  Specials:")
    for sym in ['W', 'VS', 'S']:
        count = reel_symbols[reel_idx][sym]
        pct = (count / total_per_reel[reel_idx] * 100) if total_per_reel[reel_idx] > 0 else 0
        print(f"    {sym:<8} {count:<8} {pct:>10.2f}%")
    
    # Summary
    premium_total = sum(reel_symbols[reel_idx][s] for s in ['H1', 'H2', 'H3', 'H4'])
    low_total = sum(reel_symbols[reel_idx][s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
    special_total = sum(reel_symbols[reel_idx][s] for s in ['W', 'VS', 'S'])
    print(f"\n  Totals: Premium={premium_total} ({premium_total/total_per_reel[reel_idx]*100:.1f}%), "
          f"Low={low_total} ({low_total/total_per_reel[reel_idx]*100:.1f}%), "
          f"Special={special_total} ({special_total/total_per_reel[reel_idx]*100:.1f}%)")

# Overall summary
print("\n" + "="*80)
print("OVERALL SYMBOL COUNTS")
print("="*80)
print(f"\n{'Symbol':<8} {'Count':<8} {'Percentage':<12}")
print("-" * 80)

# Premiums
print("Premiums:")
for sym in ['H1', 'H2', 'H3', 'H4']:
    count = overall_symbols[sym]
    pct = (count / total_overall * 100) if total_overall > 0 else 0
    print(f"  {sym:<8} {count:<8} {pct:>10.2f}%")

# Lows
print("\nLows:")
for sym in ['L1', 'L2', 'L3', 'L4', 'L5']:
    count = overall_symbols[sym]
    pct = (count / total_overall * 100) if total_overall > 0 else 0
    print(f"  {sym:<8} {count:<8} {pct:>10.2f}%")

# Specials
print("\nSpecials:")
for sym in ['W', 'VS', 'S']:
    count = overall_symbols[sym]
    pct = (count / total_overall * 100) if total_overall > 0 else 0
    print(f"  {sym:<8} {count:<8} {pct:>10.2f}%")

# Category totals
premium_total = sum(overall_symbols[s] for s in ['H1', 'H2', 'H3', 'H4'])
low_total = sum(overall_symbols[s] for s in ['L1', 'L2', 'L3', 'L4', 'L5'])
special_total = sum(overall_symbols[s] for s in ['W', 'VS', 'S'])

print("\n" + "-" * 80)
print(f"Premium Total: {premium_total} ({premium_total/total_overall*100:.1f}%)")
print(f"Low Total: {low_total} ({low_total/total_overall*100:.1f}%)")
print(f"Special Total: {special_total} ({special_total/total_overall*100:.1f}%)")
print(f"Grand Total: {total_overall}")

# Identify problematic patterns
print("\n" + "="*80)
print("PATTERN ANALYSIS")
print("="*80)
print("\nLow symbol clusters (rows with 3+ lows):")
low_cluster_count = 0
with open(file_path, 'r') as f:
    reader = csv.reader(f)
    for row_num, row in enumerate(reader, 1):
        if len(row) != 5:
            continue
        low_count = sum(1 for sym in row if sym and sym.startswith('L'))
        if low_count >= 3:
            low_cluster_count += 1
            if low_cluster_count <= 10:  # Show first 10
                print(f"  Row {row_num}: {','.join(row)} ({low_count} lows)")

print(f"\nTotal rows with 3+ lows: {low_cluster_count} ({low_cluster_count/rows*100:.1f}%)")

