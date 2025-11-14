#!/usr/bin/env python3
"""
Final mild rebalance of FR1.csv to v3 distribution.

Target v3 adjustments (from v2):
- H3: 240 → 270 (add 30)
- W: 16 → 19 (add 3)
- L4: 184 → 165 (remove 19)
- L5: 172 → 155 (remove 17)
- L1, L2, L3: Unchanged (147, 75, 70)

Strategy:
- Convert L4/L5 to H3 and W
- Maintain total symbol count
- Preserve reel structure and balance
"""

import csv
import os
import shutil
import random
from collections import defaultdict
from datetime import datetime

random.seed(42)

base_path = os.path.dirname(__file__)
input_file = os.path.join(base_path, 'reels', 'FR1.csv')
backup_file = os.path.join(base_path, 'reels', 'FR1.csv.backup_before_v3')
output_file = os.path.join(base_path, 'reels', 'FR1.csv')
report_file = os.path.join(base_path, 'FR1_v3_REBALANCE_SUMMARY.md')

# Current v2 counts
V2_CURRENT = {
    'H3': 240,
    'W': 16,
    'L1': 147,
    'L2': 75,
    'L3': 70,
    'L4': 184,
    'L5': 172,
}

# Target v3 counts
V3_TARGETS = {
    'H3': 270,  # Mid-point of 260-280 range
    'W': 19,    # Mid-point of 18-20 range
    'L1': 147,  # Unchanged
    'L2': 75,   # Unchanged
    'L3': 70,   # Unchanged
    'L4': 165,  # Mid-point of 160-170 range
    'L5': 155,  # Mid-point of 150-160 range
}

# Read current file
rows = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 5:
            rows.append(list(row))

# Count current symbols
current = defaultdict(int)
for row in rows:
    for sym in row:
        current[sym] += 1

total = sum(current.values())

print("="*80)
print("FR1.CSV v3 REBALANCE - FINAL MILD ADJUSTMENT")
print("="*80)
print(f"\nTotal Rows: {len(rows)}")
print(f"Total Symbols: {total}")

print(f"\n{'='*80}")
print("CURRENT STATE (v2)")
print("="*80)
print(f"\n{'Symbol':<8} {'v2 Current':<12} {'v3 Target':<12} {'Change Needed':<15}")
print("-" * 70)

changes_needed = {}
for sym in ['H3', 'W', 'L1', 'L2', 'L3', 'L4', 'L5']:
    curr = current.get(sym, 0)
    targ = V3_TARGETS[sym]
    need = targ - curr
    changes_needed[sym] = need
    action = "ADD" if need > 0 else "REMOVE" if need < 0 else "KEEP"
    print(f"{sym:<8} {curr:<12} {targ:<12} {action} {abs(need) if need != 0 else 0:<10}")

# Verify other symbols unchanged
print(f"\n{'='*80}")
print("OTHER SYMBOLS (Should remain unchanged)")
print("="*80)
print(f"\n{'Symbol':<8} {'Count':<10}")
print("-" * 30)

other_symbols = ['H1', 'H2', 'H4', 'VS', 'S']
for sym in other_symbols:
    count = current.get(sym, 0)
    print(f"{sym:<8} {count:<10}")

# Create working copy
modified = [row.copy() for row in rows]

# Strategy: Convert L4/L5 to H3 and W
# Phase 1: Convert L4/L5 to H3 (need +30 H3)
print(f"\n{'='*80}")
print("PHASE 1: Converting L4/L5 → H3")
print("="*80)

h3_to_add = changes_needed['H3']  # +30
h3_added = 0

for row_idx, row in enumerate(modified):
    if h3_added >= h3_to_add:
        break
    for reel_idx, sym in enumerate(row):
        if sym in ['L4', 'L5'] and h3_added < h3_to_add:
            # Avoid creating H3 clusters (max 5-6 H3 per row)
            row_h3_count = sum(1 for s in modified[row_idx] if s == 'H3')
            if row_h3_count < 6:
                if random.random() < 0.55:  # 55% chance
                    modified[row_idx][reel_idx] = 'H3'
                    h3_added += 1
                    if h3_added >= h3_to_add:
                        break

print(f"✓ Added {h3_added} H3 symbols (converted from L4/L5)")

# Phase 2: Convert L4/L5 to W (need +3 W)
print(f"\n{'='*80}")
print("PHASE 2: Converting L4/L5 → W")
print("="*80)

w_to_add = changes_needed['W']  # +3
w_added = 0

for row_idx, row in enumerate(modified):
    if w_added >= w_to_add:
        break
    for reel_idx, sym in enumerate(row):
        if sym in ['L4', 'L5'] and w_added < w_to_add:
            # Don't create W clusters (max 1 W per row)
            row_w_count = sum(1 for s in modified[row_idx] if s == 'W')
            if row_w_count == 0:
                if random.random() < 0.4:  # 40% chance
                    modified[row_idx][reel_idx] = 'W'
                    w_added += 1
                    if w_added >= w_to_add:
                        break

print(f"✓ Added {w_added} wilds (converted from L4/L5)")

# Count after modifications
after = defaultdict(int)
for row in modified:
    for sym in row:
        after[sym] += 1

print(f"\n{'='*80}")
print("AFTER v3 REBALANCE")
print("="*80)
print(f"\n{'Symbol':<8} {'v2 Before':<12} {'v3 After':<12} {'v3 Target':<12} {'Change':<10} {'Status':<10}")
print("-" * 80)

for sym in ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'L5', 'W', 'VS', 'S']:
    bef = current.get(sym, 0)
    aft = after.get(sym, 0)
    targ = V3_TARGETS.get(sym, '-')
    chg = aft - bef
    if sym in V3_TARGETS:
        status = "✓" if abs(aft - targ) <= 3 else "⚠"
    else:
        status = "-"
    print(f"{sym:<8} {bef:<12} {aft:<12} {str(targ):<12} {chg:+10} {status:<10}")

# Category totals
def cat_total(syms, counts):
    return sum(counts.get(s, 0) for s in syms)

bef_premium = cat_total(['H1','H2','H3','H4'], current)
aft_premium = cat_total(['H1','H2','H3','H4'], after)
bef_low = cat_total(['L1','L2','L3','L4','L5'], current)
aft_low = cat_total(['L1','L2','L3','L4','L5'], after)
bef_special = cat_total(['W','VS','S'], current)
aft_special = cat_total(['W','VS','S'], after)

print(f"\nCategory Totals:")
print(f"{'Category':<15} {'v2 Before':<12} {'v3 After':<12} {'Change':<10}")
print("-" * 60)
print(f"{'Premiums (H1-H4)':<15} {bef_premium:<12} {aft_premium:<12} {aft_premium-bef_premium:+10}")
print(f"{'Lows (L1-L5)':<15} {bef_low:<12} {aft_low:<12} {aft_low-bef_low:+10}")
print(f"{'Specials (W,VS,S)':<15} {bef_special:<12} {aft_special:<12} {aft_special-bef_special:+10}")

# Estimate impact on average feature win
h3_change = after['H3'] - current['H3']
w_change = after['W'] - current['W']
l4_change = after['L4'] - current['L4']
l5_change = after['L5'] - current['L5']

# Rough estimate: 
# v2 avg was 278.33×
# Adding 30 H3 should add significant premium win potential (~2-3× per H3 = 60-90×)
# Adding 3 W should add connectivity (~3-4× per W = 9-12×)
# Removing L4/L5 (36 symbols) reduces low-value wins (~1× per symbol = -36×)
# Net estimate: +33 to +66×

estimated_increase = (h3_change * 2.5) + (w_change * 3.5) - ((abs(l4_change) + abs(l5_change)) * 0.8)
estimated_new_avg = 278.33 + estimated_increase

print(f"\n{'='*80}")
print("EXPECTED IMPACT ESTIMATE")
print("="*80)
print(f"\nSymbol Changes:")
print(f"  H3 increased: +{h3_change} (from {current['H3']} to {after['H3']})")
print(f"  W increased: +{w_change} (from {current['W']} to {after['W']})")
print(f"  L4 reduced: {l4_change} (from {current['L4']} to {after['L4']})")
print(f"  L5 reduced: {l5_change} (from {current['L5']} to {after['L5']})")
print(f"\nEstimated Average Feature Win:")
print(f"  v2 Current: 278.33×")
print(f"  Estimated v3: ~{estimated_new_avg:.1f}×")
print(f"  Estimated increase: +{estimated_increase:.1f}×")
print(f"  Target: 384× ± 5× (379× - 389×)")

if 379 <= estimated_new_avg <= 389:
    print(f"  Status: ✅ Within target range (estimate)")
elif estimated_new_avg < 379:
    print(f"  Status: ⚠️  Below target - may need more H3/W")
    print(f"  Recommendation: Increase H3 to 280 or W to 20")
else:
    print(f"  Status: ⚠️  Above target - may need less H3/W")
    print(f"  Recommendation: Reduce H3 to 260 or W to 18")

# Save file
print(f"\n{'='*80}")
print("SAVING v3 REBALANCED FILE")
print("="*80)

if not os.path.exists(backup_file):
    shutil.copy(input_file, backup_file)
    print(f"✓ Created backup: {backup_file}")

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in modified:
        writer.writerow(row)

print(f"✓ v3 rebalanced FR1.csv saved")

# Generate summary report
report = f"""# FR1.csv v3 Rebalance Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Objective

Final mild rebalance to increase RTP from 69.58% (278.33×) toward 96.2% (384×) target while maintaining volatility.

## v2 → v3 Symbol Adjustments

| Symbol | v2 (Current) | v3 Target | v3 Actual | Change | Status |
|--------|--------------|-----------|-----------|--------|--------|
| **H3** | 240 | 270 ± 10 | {after.get('H3', 0)} | {after.get('H3', 0) - current.get('H3', 0):+d} | {"✅" if abs(after.get('H3', 0) - V3_TARGETS['H3']) <= 10 else "⚠️"} |
| **W** | 16 | 19 ± 1 | {after.get('W', 0)} | {after.get('W', 0) - current.get('W', 0):+d} | {"✅" if abs(after.get('W', 0) - V3_TARGETS['W']) <= 2 else "⚠️"} |
| **L1** | 147 | 147 (unchanged) | {after.get('L1', 0)} | {after.get('L1', 0) - current.get('L1', 0):+d} | ✅ |
| **L2** | 75 | 75 (unchanged) | {after.get('L2', 0)} | {after.get('L2', 0) - current.get('L2', 0):+d} | ✅ |
| **L3** | 70 | 70 (unchanged) | {after.get('L3', 0)} | {after.get('L3', 0) - current.get('L3', 0):+d} | ✅ |
| **L4** | 184 | 165 ± 5 | {after.get('L4', 0)} | {after.get('L4', 0) - current.get('L4', 0):+d} | {"✅" if abs(after.get('L4', 0) - V3_TARGETS['L4']) <= 5 else "⚠️"} |
| **L5** | 172 | 155 ± 5 | {after.get('L5', 0)} | {after.get('L5', 0) - current.get('L5', 0):+d} | {"✅" if abs(after.get('L5', 0) - V3_TARGETS['L5']) <= 5 else "⚠️"} |

**Other symbols (unchanged)**:
- H1: {after.get('H1', 0)}
- H2: {after.get('H2', 0)}
- H4: {after.get('H4', 0)}
- VS: {after.get('VS', 0)}
- S: {after.get('S', 0)}

## Category Changes

| Category | v2 Before | v3 After | Change |
|----------|-----------|----------|--------|
| **Premiums (H1-H4)** | {bef_premium} | {aft_premium} | {aft_premium - bef_premium:+d} |
| **Lows (L1-L5)** | {bef_low} | {aft_low} | {aft_low - bef_low:+d} |
| **Specials (W,VS,S)** | {bef_special} | {aft_special} | {aft_special - bef_special:+d} |

## Expected Impact

**v2 Performance**:
- Average Feature Win: 278.33×
- Effective RTP: 69.58%
- Median: 161.00×

**Estimated v3 Performance**:
- Average Feature Win: ~{estimated_new_avg:.1f}× (estimate)
- Effective RTP: ~{estimated_new_avg/400*100:.2f}% (estimate)
- Estimated increase: +{estimated_increase:.1f}× from v2

**Target**:
- Average Feature Win: 384× ± 5× (379× - 389×)
- Effective RTP: 96.2%

**Status**: {"✅ Estimated to be within target range" if 379 <= estimated_new_avg <= 389 else "⚠️ May need fine-tuning after simulation"}

## Symbol Distribution Rationale

1. **H3 increased (240 → 270)**: 
   - Adds premium win potential
   - Should increase big win frequency
   - Estimated contribution: +60-75× to average

2. **W increased (16 → 19)**:
   - Improves win connectivity
   - Helps form winning combinations
   - Estimated contribution: +9-12× to average

3. **L4/L5 reduced (356 → 320)**:
   - Removes low-value symbol density
   - Creates more room for premium symbols
   - Should reduce flat medium wins

4. **L1-L3 unchanged**:
   - Maintains base win frequency
   - Preserves volatility characteristics
   - Keeps dead spin rate stable

## Implementation

- Converted {h3_added} L4/L5 → H3
- Converted {w_added} L4/L5 → W
- Total symbols converted: {h3_added + w_added}
- Reel structure preserved
- Total symbol count maintained

## Next Steps

1. ✅ v3 distribution applied to FR1.csv
2. ⏳ **Run simulation** to verify actual average
3. ⏳ Compare results to target (384× ± 5×)
4. ⏳ Fine-tune if needed

## Files

- **Modified file**: `games/1_0_gunslingers/reels/FR1.csv`
- **Backup**: `games/1_0_gunslingers/reels/FR1.csv.backup_before_v3`
- **This report**: `games/1_0_gunslingers/FR1_v3_REBALANCE_SUMMARY.md`

---

**Status**: ✅ v3 rebalance applied. Ready for simulation verification.
"""

with open(report_file, 'w') as f:
    f.write(report)

print(f"✓ v3 rebalance summary saved: {report_file}")

print(f"\n{'='*80}")
print("v3 REBALANCE COMPLETE")
print("="*80)
print(f"\nSummary:")
print(f"  H3: {current.get('H3', 0)} → {after.get('H3', 0)} ({after.get('H3', 0) - current.get('H3', 0):+d}) [Target: {V3_TARGETS['H3']}]")
print(f"  W: {current.get('W', 0)} → {after.get('W', 0)} ({after.get('W', 0) - current.get('W', 0):+d}) [Target: {V3_TARGETS['W']}]")
print(f"  L4: {current.get('L4', 0)} → {after.get('L4', 0)} ({after.get('L4', 0) - current.get('L4', 0):+d}) [Target: {V3_TARGETS['L4']}]")
print(f"  L5: {current.get('L5', 0)} → {after.get('L5', 0)} ({after.get('L5', 0) - current.get('L5', 0):+d}) [Target: {V3_TARGETS['L5']}]")
print(f"  L1, L2, L3: Unchanged")
print(f"\nEstimated average: ~{estimated_new_avg:.1f}× (target: 384× ± 5×)")
print(f"\nReady for simulation!")

