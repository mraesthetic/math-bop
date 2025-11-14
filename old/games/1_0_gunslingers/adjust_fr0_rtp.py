#!/usr/bin/env python3
"""
Adjust FR0.csv - remove 1 VS and add 1 low symbol to fix RTP.

This should reduce regular bonus RTP slightly.
"""

import csv
import os
import shutil
from collections import Counter
from pathlib import Path
import random


def read_reelset_csv(file_path):
    """Read reelset CSV and return as list of rows (each row has 5 symbols)."""
    rows = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 5:
                rows.append([s.strip() for s in row])
    return rows


def rows_to_reels(rows):
    """Convert rows to reels (columns)."""
    if not rows:
        return []
    num_reels = len(rows[0])
    reels = [[] for _ in range(num_reels)]
    for row in rows:
        for reel_idx, symbol in enumerate(row):
            reels[reel_idx].append(symbol)
    return reels


def reels_to_rows(reels):
    """Convert reels (columns) back to rows."""
    if not reels:
        return []
    num_rows = len(reels[0])
    rows = []
    for row_idx in range(num_rows):
        row = [reels[reel_idx][row_idx] for reel_idx in range(len(reels))]
        rows.append(row)
    return rows


def count_symbols(rows):
    """Count all symbols in the reelset."""
    counts = Counter()
    for row in rows:
        for symbol in row:
            counts[symbol] += 1
    return counts


def adjust_fr0(rows):
    """Remove 1 VS and add 1 low symbol."""
    # Convert to reels
    reels = rows_to_reels(rows)
    
    # Find VS positions
    vs_positions = []
    for reel_idx, reel in enumerate(reels):
        for pos, symbol in enumerate(reel):
            if symbol == 'VS':
                vs_positions.append((reel_idx, pos))
    
    if not vs_positions:
        print("ERROR: No VS symbols found!")
        return rows
    
    # Randomly select one VS to remove
    random.seed(42)
    random.shuffle(vs_positions)
    vs_to_remove = vs_positions[0]
    reel_idx, pos = vs_to_remove
    
    # Replace VS with a low symbol (use L2 as a balanced choice)
    reels[reel_idx][pos] = 'L2'
    
    # Convert back to rows
    new_rows = reels_to_rows(reels)
    
    return new_rows


def validate_reelset(rows):
    """Validate that all reels have the same length."""
    if not rows:
        return False, "Empty reelset"
    
    num_reels = len(rows[0])
    for i, row in enumerate(rows):
        if len(row) != num_reels:
            return False, f"Row {i} has {len(row)} symbols, expected {num_reels}"
    
    return True, "Valid"


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("FR0.CSV RTP ADJUSTMENT")
    print("="*80)
    
    base_path = Path(__file__).parent
    input_file = base_path / "reels" / "FR0.csv"
    backup_file = base_path / "reels" / "FR0.csv.backup_before_rtp_adjustment"
    output_file = base_path / "reels" / "FR0.csv"
    
    # Read current reelset
    print(f"\nReading {input_file}...")
    rows = read_reelset_csv(input_file)
    print(f"Loaded {len(rows)} rows")
    
    # Count before
    before_counts = count_symbols(rows)
    print("\nBefore counts:")
    print(f"  VS: {before_counts.get('VS', 0)}")
    print(f"  L2: {before_counts.get('L2', 0)}")
    
    # Validate before
    is_valid, msg = validate_reelset(rows)
    print(f"\nValidation: {msg}")
    if not is_valid:
        print("ERROR: Invalid reelset before modification!")
        return
    
    # Create backup
    print(f"\nCreating backup: {backup_file}")
    shutil.copy(input_file, backup_file)
    
    # Adjust reelset
    print("\nAdjusting reelset (remove 1 VS, add 1 L2)...")
    new_rows = adjust_fr0(rows)
    
    # Count after
    after_counts = count_symbols(new_rows)
    print("\nAfter counts:")
    print(f"  VS: {after_counts.get('VS', 0)} ({after_counts.get('VS', 0) - before_counts.get('VS', 0):+d})")
    print(f"  L2: {after_counts.get('L2', 0)} ({after_counts.get('L2', 0) - before_counts.get('L2', 0):+d})")
    
    # Validate after
    is_valid, msg = validate_reelset(new_rows)
    print(f"\nValidation: {msg}")
    if not is_valid:
        print("ERROR: Invalid reelset after modification!")
        return
    
    # Save new reelset
    print(f"\nSaving adjusted reelset: {output_file}")
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)
    
    # Print summary
    print("\n" + "="*80)
    print("ADJUSTMENT COMPLETE")
    print("="*80)
    print("\nChanges:")
    print(f"  VS: {before_counts.get('VS', 0)} → {after_counts.get('VS', 0)} (-1)")
    print(f"  L2: {before_counts.get('L2', 0)} → {after_counts.get('L2', 0)} (+1)")
    print("\nExpected Impact:")
    print("  Average Feature Win: Should decrease by ~2-3×")
    print("  RTP: Should decrease by ~2-3% (from ~92% to ~89-90%)")
    print("  Volatility: Should remain similar")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

