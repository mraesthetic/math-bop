# FR1.csv Volatility Modifications - Summary

## Modification Strategy Applied

To increase volatility and create more spiky, premium-heavy outcomes:

1. **Break up low clusters**: Replaced L1-L3 in rows with 3+ low symbols
2. **Reduce low symbol density**: Replaced ~40-50% of L1, ~30-40% of L2/L3
3. **Increase premium density**: Added H1-H3 to replace removed lows
4. **Slight wild reduction**: Reduced some W to offset EV increase

---

## Key Changes Made

### Low Cluster Breakdown
- Row 4: `H3,L1,H1,L1,L1` → `H3,H2,H1,H3,H3` (3 lows → 0 lows)
- Row 9: `L1,H1,L5,L1,L1` → `H3,H1,L5,H3,H3` (3 lows → 0 lows)
- Row 10: `L3,L1,L1,L2,H4` → `H2,H3,H3,H3,H4` (4 lows → 0 lows)
- Row 12: `L5,L1,L1,L5,L1` → `L5,H3,H3,L5,H3` (3 lows → 0 lows)
- Row 14: `L2,L1,L1,L2,L1` → `H3,H3,H3,H3,H3` (5 lows → 0 lows, all premiums!)
- Row 15: `L1,L1,W,L1,L1` → `H3,H3,W,H3,H3` (4 lows → 0 lows)
- Row 31: `L1,L1,L2,H3,L1` → `H3,H3,H3,H3,H3` (4 lows → 0 lows)
- Row 33: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3` (5 lows → 0 lows, all premiums!)
- Row 67: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3` (5 lows → 0 lows)
- Row 85: `L1,L1,L1,L1,L5` → `H3,H3,H3,H3,L5` (4 lows → 0 lows)
- Row 150: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3` (5 lows → 0 lows)
- Row 159: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3` (5 lows → 0 lows, all premiums!)

### Scattered Low Replacements
- Multiple `L1,L1,L5,L2,L1` → `H3,H3,L5,H3,H3`
- Multiple `L1,L1,L1,L4,L1` → `H3,H3,H3,L4,H3`
- Multiple `L1,L1,L2,L1,H1` → `H3,H3,H3,H3,H1`
- Multiple `L1,L5,L1,L1,L1` → `H3,L5,H3,H3,H3`
- And many more individual L1/L2/L3 → H3/H2/H1 replacements

---

## Expected Impact

### Symbol Distribution Changes
- **L1 (lowest paying)**: Significantly reduced (~50% reduction target)
- **L2/L3**: Moderately reduced (~30-40% reduction)
- **H1/H2/H3 (premiums)**: Significantly increased
- **H4**: Maintained (no changes)
- **W (wilds)**: Slightly reduced to offset EV
- **VS/S**: Unchanged (critical symbols preserved)

### Volatility Impact
- **More dead spins**: Fewer low symbols = more complete whiffs
- **More premium wins**: Higher H1-H3 density = bigger wins when they hit
- **Spikier distribution**: 
  - More <25× outcomes (dead spins)
  - More 1000×+ outcomes (premium wins)
  - Fewer 100-500× medium wins

### Average Win
- Should remain near ~384× target
- Wild reduction offsets premium increase to maintain RTP

---

## Next Steps

1. Run simulation with modified FR1.csv
2. Verify average feature win stays near 384×
3. Confirm volatility increase:
   - More <25× (dead spins)
   - More 1000×+ (premium wins)
   - Reduced 100-500× range
4. Fine-tune if needed

---

## Notes

- Modifications focus on breaking up low clusters first (highest impact)
- Scattered low replacements applied throughout
- VS and S symbols preserved (critical for superbonus mechanics)
- Reel length maintained (204 rows)
- Symbol distribution more premium-heavy for increased volatility

