#!/usr/bin/env python3
import json
import zstandard as zst
from io import TextIOWrapper
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

book_file = "games/1_0_gunslingers/library/publish_files/books_base.jsonl.zst"
lut_file = "games/1_0_gunslingers/library/publish_files/lookUpTable_base_0.csv"

if not os.path.exists(book_file):
    print(f"Book file not found: {book_file}")
    sys.exit(1)

if not os.path.exists(lut_file):
    print(f"Lookup table file not found: {lut_file}")
    sys.exit(1)

# Read book payouts
book_payouts = {}
with open(book_file, "rb") as f:
    decompressor = zst.ZstdDecompressor()
    with decompressor.stream_reader(f) as reader:
        txt_stream = TextIOWrapper(reader, encoding="UTF-8")
        for line in txt_stream:
            line = line.strip()
            if not line:
                continue
            try:
                blob = json.loads(line)
                book_payouts[blob["id"]] = blob["payoutMultiplier"]
            except Exception as e:
                print(f"Error parsing book line: {e}")
                continue

# Read lookup table payouts
lut_payouts = {}
with open(lut_file, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3:
            try:
                sim_id = int(row[0])
                payout = int(row[2])
                lut_payouts[sim_id] = payout
            except Exception as e:
                print(f"Error parsing LUT row: {e}")
                continue

# Find mismatches
mismatches = []
missing_in_books = []
missing_in_lut = []

all_ids = set(book_payouts.keys()) | set(lut_payouts.keys())

for sim_id in sorted(all_ids):
    book_payout = book_payouts.get(sim_id)
    lut_payout = lut_payouts.get(sim_id)
    
    if book_payout is None:
        missing_in_books.append(sim_id)
    elif lut_payout is None:
        missing_in_lut.append(sim_id)
    elif book_payout != lut_payout:
        mismatches.append((sim_id, book_payout, lut_payout, book_payout - lut_payout))

print(f"Total books: {len(book_payouts)}")
print(f"Total LUT entries: {len(lut_payouts)}")
print(f"Mismatches: {len(mismatches)}")
print(f"Missing in books: {len(missing_in_books)}")
print(f"Missing in LUT: {len(missing_in_lut)}")

if mismatches:
    print(f"\nFirst 20 mismatches:")
    for sim_id, book, lut, diff in mismatches[:20]:
        print(f"  Sim {sim_id}: Book={book}, LUT={lut}, Diff={diff}")
        
    # Check if all diffs are the same
    diffs = [d for _, _, _, d in mismatches]
    if len(set(diffs)) == 1:
        print(f"\nAll mismatches have the same difference: {diffs[0]}")
    else:
        print(f"\nDifferent differences found: {set(diffs)}")
else:
    print("\nNo mismatches found!")
