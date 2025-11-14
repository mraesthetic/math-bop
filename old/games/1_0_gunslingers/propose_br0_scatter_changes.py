#!/usr/bin/env python3
"""
Propose precise changes to BR0.csv scatter distribution to achieve target trigger rates.

Key understanding:
- Current 10% trigger rate comes from FORCED freegame distribution (quota=0.1)
- Scatters determine whether it's 3-scatter (regular) or 4-scatter (superbonus)
- Current weights {3: 98, 4: 2} give 98% regular, 2% superbonus
- Target: 0.55% regular (3-scatter), 0.10% superbonus (4-scatter)

To achieve target:
1. Reduce freegame quota from 0.1 (10%) to 0.0065 (0.65%)
2. Adjust scatter_triggers weights from {3: 98, 4: 2} to {3: 85, 4: 15}
   (to achieve 5.5:1 ratio: 0.55% / 0.10% = 5.5)
3. Adjust BR0.csv scatter distribution to support the new weights
   (need more 4-scatter opportunities relative to 3-scatter)

But wait - if we're using forced distribution, the scatter density doesn't matter
for the trigger RATE, only for the RATIO of 3-scatter vs 4-scatter.

However, the user specifically asked to analyze scatter distribution and propose changes.
This suggests they may want to move away from forced distribution, OR
they want to ensure the scatter distribution naturally supports the target ratio.

Let's analyze both scenarios.
"""

import csv
from collections import Counter

def analyze_current_br0():
    """Analyze current BR0.csv scatter distribution"""
    scatter_counts = [0, 0, 0, 0, 0]
    total_rows = 0
    scatter_positions = []
    rows_with_scatters = []  # List of rows and how many scatters they have
    
    with open('reels/BR0.csv', 'r') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if len(row) == 5:
                total_rows += 1
                scatter_count_in_row = 0
                for reel_idx in range(5):
                    if row[reel_idx].strip() == 'S':
                        scatter_counts[reel_idx] += 1
                        scatter_positions.append((row_idx, reel_idx))
                        scatter_count_in_row += 1
                if scatter_count_in_row > 0:
                    rows_with_scatters.append((row_idx, scatter_count_in_row))
    
    return {
        'total_rows': total_rows,
        'scatter_counts': scatter_counts,
        'total_scatters': sum(scatter_counts),
        'scatter_positions': scatter_positions,
        'rows_with_scatters': rows_with_scatters,
    }

def main():
    print("=" * 80)
    print("BR0.csv Scatter Distribution Analysis & Proposal")
    print("=" * 80)
    print()
    
    current = analyze_current_br0()
    
    print("Current BR0.csv Scatter Distribution:")
    print(f"  Total rows: {current['total_rows']}")
    print(f"  Total scatter symbols: {current['total_scatters']}")
    print(f"  Scatter counts per reel: {current['scatter_counts']}")
    print(f"  Scatter density: {current['total_scatters'] / (current['total_rows'] * 5) * 100:.2f}%")
    print(f"  Rows with scatters: {len(current['rows_with_scatters'])}")
    
    # Count rows by scatter count
    scatter_row_counts = Counter(count for _, count in current['rows_with_scatters'])
    print(f"  Rows with 3 scatters: {scatter_row_counts.get(3, 0)}")
    print(f"  Rows with 4 scatters: {scatter_row_counts.get(4, 0)}")
    print(f"  Rows with 5 scatters: {scatter_row_counts.get(5, 0)}")
    print()
    
    print("Current Configuration (from game_config.py):")
    print("  Freegame distribution quota: 0.1 (10%)")
    print("  Scatter_triggers weights: {3: 98, 4: 2}")
    print("  → Results in: 9.79% regular bonus, 0.22% superbonus")
    print()
    
    print("Target Configuration:")
    print("  Regular bonus (3-scatter): 0.55% (~1 in 180 spins)")
    print("  Superbonus (4-scatter): 0.10% (~1 in 1000 spins)")
    print("  Total freegame: 0.65%")
    print("  Ratio (regular:superbonus): 5.5:1")
    print()
    
    print("=" * 80)
    print("PROPOSED CHANGES")
    print("=" * 80)
    print()
    
    print("Option 1: Keep Forced Distribution, Adjust Weights")
    print("  - Reduce freegame quota from 0.1 to 0.0065 (0.65%)")
    print("  - Adjust scatter_triggers weights from {3: 98, 4: 2} to {3: 85, 4: 15}")
    print("  - BR0.csv scatter distribution: Keep as-is (scatters only affect ratio)")
    print()
    
    print("Option 2: Remove Forced Distribution, Rely on Natural Scatters")
    print("  - Remove freegame quota (set to 0 or very low)")
    print("  - Increase scatter density significantly to achieve 0.65% natural trigger rate")
    print("  - Adjust scatter_triggers weights to {3: 85, 4: 15}")
    print("  - BR0.csv: Need to calculate required scatter density")
    print()
    
    print("RECOMMENDATION: Option 1 (simpler, more predictable)")
    print()
    
    # However, user asked specifically for scatter distribution changes
    # So let's propose a scatter distribution that naturally supports the target ratio
    # even if we're using forced distribution
    
    print("=" * 80)
    print("SCATTER DISTRIBUTION PROPOSAL")
    print("=" * 80)
    print()
    print("Even with forced distribution, scatter placement affects the 3:4 ratio.")
    print("Current: {3: 98, 4: 2} weights give ~44:1 ratio, but we need 5.5:1 ratio.")
    print()
    print("To naturally support 5.5:1 ratio with scatter placement:")
    print("  - We need more opportunities for 4-scatter combinations")
    print("  - Current: Only rows with 4+ scatters can trigger 4-scatter bonus")
    print("  - With weights {3: 85, 4: 15}, 15% of triggers become 4-scatter")
    print()
    print("However, the scatter_triggers weights are the PRIMARY control mechanism.")
    print("Scatter distribution is secondary.")
    print()
    print("PROPOSED BR0.csv CHANGES (minimal):")
    print("  - Keep current scatter count (16 scatters)")
    print("  - Redistribute to ensure scatters are well-spread")
    print("  - Ensure at least some rows have 4 scatters (for 4-scatter triggers)")
    print()
    
    # Let's check current scatter positions
    print("Current Scatter Positions Analysis:")
    rows_by_scatter_count = {}
    for row_idx, count in current['rows_with_scatters']:
        if count not in rows_by_scatter_count:
            rows_by_scatter_count[count] = []
        rows_by_scatter_count[count].append(row_idx)
    
    for count in sorted(rows_by_scatter_count.keys()):
        print(f"  Rows with {count} scatters: {len(rows_by_scatter_count[count])} "
              f"(rows: {rows_by_scatter_count[count][:5]}{'...' if len(rows_by_scatter_count[count]) > 5 else ''})")
    print()
    
    # Proposed: Redistribute scatters to have more 4-scatter opportunities
    # Current: [5, 1, 5, 1, 4] = 16 scatters
    # We want to ensure some rows naturally have 4 scatters
    
    # Strategy: Keep similar total, but ensure better distribution
    # Target: [3, 3, 3, 3, 4] = 16 scatters (more balanced)
    # Or: [4, 2, 4, 2, 4] = 16 scatters (ensures 4-scatter possibilities)
    
    print("PROPOSED SCATTER REDISTRIBUTION:")
    print("  Current per-reel: [5, 1, 5, 1, 4] = 16 total")
    print("  Proposed per-reel: [4, 2, 4, 2, 4] = 16 total")
    print("  Rationale:")
    print("    - More balanced distribution across reels")
    print("    - Ensures multiple reels have scatters (enables 3+ scatter combinations)")
    print("    - Slightly reduced on reels 1 and 3 (from 5 to 4)")
    print("    - Increased on reels 2 and 4 (from 1 to 2)")
    print("    - Kept reel 5 at 4")
    print()
    
    print("However, the PRIMARY change needed is in game_config.py:")
    print("  1. Change freegame quota from 0.1 to 0.0065")
    print("  2. Change scatter_triggers from {3: 98, 4: 2} to {3: 85, 4: 15}")
    print()
    
    print("The BR0.csv scatter changes are secondary and mainly for balance.")
    print()

if __name__ == '__main__':
    main()

