#!/usr/bin/env python3
"""
Redistribute scatters in BR0.csv according to proposed changes.

Current: [5, 1, 5, 1, 4] = 16 scatters
Proposed: [4, 2, 4, 2, 4] = 16 scatters

Strategy:
1. Read current BR0.csv
2. Identify current scatter positions
3. Redistribute to achieve target counts per reel
4. Ensure scatters are well-spread (not clustered)
5. Write new BR0.csv
"""

import csv
import random
from collections import defaultdict

def read_br0(reelset_file):
    """Read BR0.csv and return rows"""
    rows = []
    with open(reelset_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 5:
                rows.append([cell.strip() for cell in row])
    return rows

def analyze_scatters(rows):
    """Analyze current scatter distribution"""
    scatter_positions = []  # (row_idx, reel_idx)
    scatter_counts = [0, 0, 0, 0, 0]
    
    for row_idx, row in enumerate(rows):
        for reel_idx in range(5):
            if row[reel_idx] == 'S':
                scatter_positions.append((row_idx, reel_idx))
                scatter_counts[reel_idx] += 1
    
    return scatter_positions, scatter_counts

def redistribute_scatters(rows, target_counts):
    """
    Redistribute scatters to achieve target counts per reel.
    
    Strategy:
    1. Remove all current scatters
    2. Place scatters according to target counts, spread evenly
    """
    # Create a copy
    new_rows = [row.copy() for row in rows]
    
    # Remove all current scatters
    for row in new_rows:
        for reel_idx in range(5):
            if row[reel_idx] == 'S':
                # Replace with a low symbol (L1) - need to pick something appropriate
                # Actually, we should preserve the original symbol if possible
                # Let's mark positions to change
                pass
    
    # Get current scatter positions to know where NOT to place (to avoid conflicts)
    current_scatters, _ = analyze_scatters(rows)
    current_scatter_set = set(current_scatters)
    
    # Create list of available positions for each reel (excluding current scatter positions initially)
    # Actually, we'll replace scatters, so we can use any position
    
    # Strategy: Spread scatters evenly across the reelstrip
    # For each reel, calculate positions to place scatters
    total_rows = len(rows)
    
    scatter_placements = []  # List of (row_idx, reel_idx) to place scatters
    
    for reel_idx, target_count in enumerate(target_counts):
        if target_count == 0:
            continue
        
        # Calculate evenly-spaced positions
        if target_count == 1:
            positions = [total_rows // 2]
        else:
            # Spread evenly
            step = total_rows / (target_count + 1)
            positions = [int(step * (i + 1)) for i in range(target_count)]
        
        # Ensure positions are within bounds
        positions = [min(p, total_rows - 1) for p in positions]
        
        for pos in positions:
            scatter_placements.append((pos, reel_idx))
    
    # Remove all current scatters first
    for row_idx, row in enumerate(new_rows):
        for reel_idx in range(5):
            if row[reel_idx] == 'S':
                # Replace with L1 (low symbol)
                row[reel_idx] = 'L1'
    
    # Place new scatters
    for row_idx, reel_idx in scatter_placements:
        new_rows[row_idx][reel_idx] = 'S'
    
    return new_rows

def main():
    reelset_file = 'reels/BR0.csv'
    output_file = 'reels/BR0_NEW.csv'
    
    print("=" * 80)
    print("BR0.csv Scatter Redistribution")
    print("=" * 80)
    print()
    
    # Read current BR0
    rows = read_br0(reelset_file)
    print(f"Read {len(rows)} rows from {reelset_file}")
    
    # Analyze current distribution
    current_scatters, current_counts = analyze_scatters(rows)
    print(f"Current scatter counts per reel: {current_counts}")
    print(f"Current total scatters: {sum(current_counts)}")
    print()
    
    # Target distribution
    target_counts = [4, 2, 4, 2, 4]  # Total: 16
    print(f"Target scatter counts per reel: {target_counts}")
    print(f"Target total scatters: {sum(target_counts)}")
    print()
    
    # Redistribute
    new_rows = redistribute_scatters(rows, target_counts)
    
    # Verify new distribution
    new_scatters, new_counts = analyze_scatters(new_rows)
    print(f"New scatter counts per reel: {new_counts}")
    print(f"New total scatters: {sum(new_counts)}")
    print()
    
    # Check if target achieved
    if new_counts == target_counts:
        print("✓ Target distribution achieved!")
    else:
        print("⚠ Warning: Target distribution not exactly matched")
        print(f"  Expected: {target_counts}")
        print(f"  Got: {new_counts}")
    print()
    
    # Write new file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)
    
    print(f"✓ Wrote new reelset to {output_file}")
    print()
    
    # Show sample of changes
    print("Sample of scatter positions (first 10 rows with scatters):")
    count = 0
    for row_idx, row in enumerate(new_rows):
        if 'S' in row:
            scatter_positions = [f"R{i+1}" for i, sym in enumerate(row) if sym == 'S']
            print(f"  Row {row_idx + 1}: {', '.join(scatter_positions)}")
            count += 1
            if count >= 10:
                break

if __name__ == '__main__':
    main()

