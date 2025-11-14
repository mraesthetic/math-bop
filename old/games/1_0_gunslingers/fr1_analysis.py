import csv
from collections import defaultdict

file_path = 'reels/FR1.csv'
reel_symbols = [defaultdict(int) for _ in range(5)]
overall_symbols = defaultdict(int)
rows = []

with open(file_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))
            for reel_idx, sym in enumerate(row):
                reel_symbols[reel_idx][sym] += 1
                overall_symbols[sym] += 1

total = sum(overall_symbols.values())
print('BEFORE MODIFICATION:')
print(f'Total Rows: {len(rows)}, Total Symbols: {total}')
print('\nOverall Symbol Counts:')
for sym in ['H1','H2','H3','H4','L1','L2','L3','L4','L5','W','VS','S']:
    count = overall_symbols[sym]
    pct = count/total*100
    print(f'  {sym}: {count:4d} ({pct:5.2f}%)')

print('\nPer-Reel Symbol Counts:')
for reel_idx in range(5):
    print(f'\n  Reel {reel_idx+1}:')
    for sym in ['H1','H2','H3','H4','L1','L2','L3','L4','L5','W','VS','S']:
        count = reel_symbols[reel_idx][sym]
        if count > 0:
            pct = count/len(rows)*100
            print(f'    {sym}: {count:3d} ({pct:5.2f}%)')

