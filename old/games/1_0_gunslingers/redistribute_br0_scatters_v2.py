#!/usr/bin/env python3
"""
Redistribute scatters in BR0.csv to achieve target distribution.

Current: [5, 1, 5, 1, 4] = 16 scatters
Target: [4, 2, 4, 2, 4] = 16 scatters

Strategy:
- Place scatters on specific rows to enable 3+ scatter combinations
- Maintain target counts per reel
- Ensure scatters are spread across the reelstrip (not all clustered)
"""

import csv
import random

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
    scatter_counts = [0, 0, 0, 0, 0]
    scatter_positions = []
    
    for row_idx, row in enumerate(rows):
        for reel_idx in range(5):
            if row[reel_idx] == 'S':
                scatter_positions.append((row_idx, reel_idx))
                scatter_counts[reel_idx] += 1
    
    return scatter_positions, scatter_counts

def create_scatter_placement_plan(target_counts, total_rows):
    """
    Create a plan for placing scatters to achieve target counts.
    
    Strategy:
    - Create some rows with 3 scatters (for 3-scatter triggers)
    - Create some rows with 4 scatters (for 4-scatter triggers)
    - Spread rows across the reelstrip
    """
    # Target: [4, 2, 4, 2, 4] = 16 scatters total
    
    # Plan:
    # - 2 rows with 3 scatters each = 6 scatters
    # - 2 rows with 4 scatters each = 8 scatters
    # - 1 row with 2 scatters = 2 scatters
    # Total: 16 scatters
    
    # For 3-scatter rows, use reels 1, 3, 5 (most common)
    # For 4-scatter rows, use reels 1, 2, 3, 5 or 1, 3, 4, 5
    # For 2-scatter rows, use reels 2, 4 (least common)
    
    placements = []  # List of (row_idx, reel_idx)
    
    # Calculate row positions (spread evenly)
    row_positions = []
    num_scatter_rows = 5  # 2 rows of 3, 2 rows of 4, 1 row of 2
    step = total_rows / (num_scatter_rows + 1)
    for i in range(num_scatter_rows):
        row_positions.append(int(step * (i + 1)))
    
    # Row 1: 3 scatters on reels 1, 3, 5
    row_idx = row_positions[0]
    placements.extend([(row_idx, 0), (row_idx, 2), (row_idx, 4)])
    
    # Row 2: 4 scatters on reels 1, 2, 3, 5
    row_idx = row_positions[1]
    placements.extend([(row_idx, 0), (row_idx, 1), (row_idx, 2), (row_idx, 4)])
    
    # Row 3: 3 scatters on reels 1, 3, 5
    row_idx = row_positions[2]
    placements.extend([(row_idx, 0), (row_idx, 2), (row_idx, 4)])
    
    # Row 4: 4 scatters on reels 1, 3, 4, 5
    row_idx = row_positions[3]
    placements.extend([(row_idx, 0), (row_idx, 2), (row_idx, 3), (row_idx, 4)])
    
    # Row 5: 2 scatters on reels 2, 4
    row_idx = row_positions[4]
    placements.extend([(row_idx, 1), (row_idx, 3)])
    
    # Count placements per reel
    counts = [0, 0, 0, 0, 0]
    for _, reel_idx in placements:
        counts[reel_idx] += 1
    
    # Verify: Should be [4, 2, 4, 2, 4]
    if counts != target_counts:
        # Adjust if needed
        # Current: [4, 2, 4, 2, 4] from the plan above
        # Let's verify:
        # Reel 0: 2 (row1) + 1 (row2) + 1 (row3) + 1 (row4) = 4 ✓
        # Reel 1: 1 (row2) + 1 (row5) = 2 ✓
        # Reel 2: 1 (row1) + 1 (row2) + 1 (row3) + 1 (row4) = 4 ✓
        # Reel 3: 1 (row4) + 1 (row5) = 2 ✓
        # Reel 4: 1 (row1) + 1 (row2) + 1 (row3) + 1 (row4) = 4 ✓
        pass  # Should be correct
    
    return placements, counts

def apply_scatter_redistribution(rows, placements):
    """Apply scatter placements to rows"""
    new_rows = [row.copy() for row in rows]
    
    # Remove all current scatters
    for row in new_rows:
        for reel_idx in range(5):
            if row[reel_idx] == 'S':
                # Replace with L1 (common low symbol)
                row[reel_idx] = 'L1'
    
    # Place new scatters
    for row_idx, reel_idx in placements:
        if 0 <= row_idx < len(new_rows) and 0 <= reel_idx < 5:
            new_rows[row_idx][reel_idx] = 'S'
    
    return new_rows

def main():
    reelset_file = 'reels/BR0.csv'
    output_file = 'reels/BR0_NEW.csv'
    
    print("=" * 80)
    print("BR0.csv Scatter Redistribution (v2)")
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
    target_counts = [4, 2, 4, 2, 4]
    print(f"Target scatter counts per reel: {target_counts}")
    print(f"Target total scatters: {sum(target_counts)}")
    print()
    
    # Create placement plan
    placements, plan_counts = create_scatter_placement_plan(target_counts, len(rows))
    print("Scatter placement plan:")
    print(f"  Total placements: {len(placements)}")
    print(f"  Counts per reel: {plan_counts}")
    
    # Group by row to show which rows have scatters
    rows_with_scatters = {}
    for row_idx, reel_idx in placements:
        if row_idx not in rows_with_scatters:
            rows_with_scatters[row_idx] = []
        rows_with_scatters[row_idx].append(reel_idx)
    
    print(f"  Rows with scatters: {len(rows_with_scatters)}")
    for row_idx in sorted(rows_with_scatters.keys()):
        reel_indices = sorted(rows_with_scatters[row_idx])
        reel_labels = [f"R{i+1}" for i in reel_indices]
        print(f"    Row {row_idx + 1}: {len(reel_indices)} scatters on {', '.join(reel_labels)}")
    print()
    
    # Apply redistribution
    new_rows = apply_scatter_redistribution(rows, placements)
    
    # Verify new distribution
    new_scatters, new_counts = analyze_scatters(new_rows)
    print(f"New scatter counts per reel: {new_counts}")
    print(f"New total scatters: {sum(new_counts)}")
    
    if new_counts == target_counts:
        print("✓ Target distribution achieved!")
    else:
        print("⚠ Warning: Target distribution not exactly matched")
    print()
    
    # Write new file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)
    
    print(f"✓ Wrote new reelset to {output_file}")
    print()
    
    print("Note: This redistribution maintains scatter count but changes placement.")
    print("The PRIMARY changes needed are in game_config.py:")
    print("  1. Reduce freegame quota from 0.1 to 0.0065")
    print("  2. Change scatter_triggers from {3: 98, 4: 2} to {3: 85, 4: 15}")

if __name__ == '__main__':
    main()

