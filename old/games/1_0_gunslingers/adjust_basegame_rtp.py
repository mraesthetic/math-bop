#!/usr/bin/env python3
"""
Adjust basegame RTP by reducing paytable values in BR0.csv.

Strategy:
- Reduce premium symbol frequencies slightly
- OR reduce premium symbol payouts slightly
- Goal: Reduce basegame-only RTP from ~44% to ~40-42%
"""

import csv
from collections import Counter

def analyze_br0_symbols(reelset_file):
    """Analyze symbol distribution in BR0.csv"""
    symbol_counts = Counter()
    total_symbols = 0
    rows = []
    
    with open(reelset_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 5:
                rows.append([cell.strip() for cell in row])
                for symbol in row:
                    symbol_counts[symbol.strip()] += 1
                    total_symbols += 1
    
    return rows, symbol_counts, total_symbols

def reduce_premium_frequencies(rows, reduction_factor=0.95):
    """
    Reduce premium symbol frequencies by replacing some with low symbols.
    
    Premium symbols: H1, H2, H3, H4
    Low symbols: L1, L2, L3, L4, L5
    """
    new_rows = [row.copy() for row in rows]
    
    # Count current premiums
    premium_count = sum(1 for row in new_rows for sym in row if sym in ['H1', 'H2', 'H3', 'H4'])
    target_reduction = int(premium_count * (1 - reduction_factor))
    
    # Replace some premiums with lows (prefer L1, L2)
    replacements = 0
    for row_idx, row in enumerate(new_rows):
        for reel_idx in range(5):
            if replacements >= target_reduction:
                break
            if row[reel_idx] in ['H1', 'H2', 'H3', 'H4']:
                # Replace with L1 or L2 (most common lows)
                new_rows[row_idx][reel_idx] = 'L1' if replacements % 2 == 0 else 'L2'
                replacements += 1
        if replacements >= target_reduction:
            break
    
    return new_rows, replacements

def main():
    reelset_file = 'reels/BR0.csv'
    output_file = 'reels/BR0_ADJUSTED.csv'
    backup_file = 'reels/BR0.csv.backup_before_rtp_reduction'
    
    print("=" * 80)
    print("BR0.csv Basegame RTP Reduction")
    print("=" * 80)
    print()
    
    # Backup current BR0
    import shutil
    shutil.copy(reelset_file, backup_file)
    print(f"✓ Backed up {reelset_file} to {backup_file}")
    print()
    
    # Analyze current distribution
    rows, symbol_counts, total_symbols = analyze_br0_symbols(reelset_file)
    print(f"Total symbols: {total_symbols}")
    print(f"Total rows: {len(rows)}")
    print()
    
    print("Current Symbol Distribution (top 15):")
    for symbol, count in symbol_counts.most_common(15):
        pct = count / total_symbols * 100
        print(f"  {symbol:3s}: {count:4d} ({pct:5.2f}%)")
    print()
    
    # Calculate premium symbol percentage
    premium_symbols = ['H1', 'H2', 'H3', 'H4']
    premium_count = sum(symbol_counts.get(sym, 0) for sym in premium_symbols)
    premium_pct = premium_count / total_symbols * 100
    
    print(f"Premium symbols (H1-H4): {premium_count} ({premium_pct:.2f}%)")
    print()
    
    # Reduce premium frequencies by 5%
    reduction_factor = 0.95
    new_rows, replacements = reduce_premium_frequencies(rows, reduction_factor)
    
    print(f"Replaced {replacements} premium symbols with low symbols")
    print(f"Reduction factor: {(1-reduction_factor)*100:.1f}%")
    print()
    
    # Analyze new distribution
    new_symbol_counts = Counter()
    for row in new_rows:
        for symbol in row:
            new_symbol_counts[symbol] += 1
    
    new_premium_count = sum(new_symbol_counts.get(sym, 0) for sym in premium_symbols)
    new_premium_pct = new_premium_count / total_symbols * 100
    
    print(f"New premium symbols (H1-H4): {new_premium_count} ({new_premium_pct:.2f}%)")
    print(f"Reduction: {premium_count - new_premium_count} symbols ({premium_pct - new_premium_pct:.2f}%)")
    print()
    
    # Write new file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)
    
    print(f"✓ Wrote adjusted reelset to {output_file}")
    print()
    print("Next steps:")
    print("  1. Review the changes")
    print("  2. If acceptable, replace BR0.csv with BR0_ADJUSTED.csv")
    print("  3. Run verification simulation")

if __name__ == '__main__':
    main()

