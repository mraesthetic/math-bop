#!/usr/bin/env python3
"""Count symbols in reel strip files."""
import csv
import os

reels = ['BR0', 'FR0', 'FR1']
base_path = os.path.dirname(__file__)

for reel_name in reels:
    print(f'\n{"="*60}')
    print(f'{reel_name}.csv SYMBOL COUNTS')
    print("="*60)
    
    file_path = os.path.join(base_path, 'reels', f'{reel_name}.csv')
    symbols = {'H1': 0, 'H2': 0, 'H3': 0, 'H4': 0, 
               'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0, 'L5': 0, 
               'W': 0, 'VS': 0, 'S': 0}
    total = 0
    rows = 0
    
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows += 1
            for sym in row:
                if sym in symbols:
                    symbols[sym] += 1
                    total += 1
    
    print(f'Total Rows: {rows}')
    print(f'Total Symbols: {total}')
    print()
    print('Symbol | Count | Percentage')
    print('-' * 60)
    for sym in sorted(symbols.keys()):
        count = symbols[sym]
        pct = (count / total * 100) if total > 0 else 0
        print(f'{sym:6s} | {count:5d} | {pct:6.2f}%')

