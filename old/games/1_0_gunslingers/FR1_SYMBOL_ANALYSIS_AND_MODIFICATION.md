# FR1.csv Symbol Analysis and Volatility Modification

## Current Symbol Distribution (Approximate)

Based on analysis of FR1.csv (204 rows, 1020 total symbol positions):

### Overall Symbol Counts (BEFORE)
| Symbol | Count | Percentage | Per Reel Avg |
|--------|-------|------------|--------------|
| H1 | ~45 | 4.4% | ~9 |
| H2 | ~65 | 6.4% | ~13 |
| H3 | ~34 | 3.3% | ~7 |
| H4 | ~55 | 5.4% | ~11 |
| L1 | ~186 | 18.2% | ~37 |
| L2 | ~84 | 8.2% | ~17 |
| L3 | ~75 | 7.4% | ~15 |
| L4 | ~95 | 9.3% | ~19 |
| L5 | ~85 | 8.3% | ~17 |
| W | ~18 | 1.8% | ~4 |
| VS | 2 | 0.2% | ~0.4 |
| S | ~8 | 0.8% | ~2 |

### Category Totals (BEFORE)
- **Premiums (H1-H4)**: ~199 (19.5%)
- **Lows (L1-L5)**: ~525 (51.5%)
- **Specials (W,VS,S)**: ~28 (2.7%)

---

## Modification Strategy

### Replacement Targets

| Symbol | Current | Target Reduction | Replacements |
|--------|---------|------------------|--------------|
| L1 | ~186 | -50% (93 symbols) | → H3 (75), H2 (18) |
| L2 | ~84 | -40% (34 symbols) | → H3 (20), H2 (14) |
| L3 | ~75 | -35% (26 symbols) | → H2 (18), H1 (8) |
| L4 | ~95 | -15% (14 symbols) | → H3 (11), H2 (3) |
| W | ~18 | -12% (2 symbols) | → H2 (1), H3 (1) |

### Expected After Modifications

| Symbol | Before | After | Change |
|--------|--------|-------|--------|
| H1 | ~45 | ~53 | +8 |
| H2 | ~65 | ~116 | +51 |
| H3 | ~34 | ~140 | +106 |
| H4 | ~55 | ~55 | 0 |
| L1 | ~186 | ~93 | -93 |
| L2 | ~84 | ~50 | -34 |
| L3 | ~75 | ~49 | -26 |
| L4 | ~95 | ~81 | -14 |
| L5 | ~85 | ~85 | 0 |
| W | ~18 | ~16 | -2 |
| VS | 2 | 2 | 0 |
| S | ~8 | ~8 | 0 |

### Category Totals (AFTER)
- **Premiums (H1-H4)**: ~364 (35.7%) - **+83% increase**
- **Lows (L1-L5)**: ~358 (35.1%) - **-32% decrease**
- **Specials (W,VS,S)**: ~26 (2.5%) - **Slight decrease**

---

## Implementation Plan

### Phase 1: Break Up Low Clusters
Target rows with 3+ L1/L2/L3 symbols (worst clusters):
- Row 4: `H3,L1,H1,L1,L1` → `H3,H2,H1,H3,H3`
- Row 9: `L1,H1,L5,L1,L1` → `H3,H1,L5,H3,H3`
- Row 10: `L3,L1,L1,L2,H4` → `H2,H3,H3,H3,H4`
- Row 12: `L5,L1,L1,L5,L1` → `L5,H3,H3,L5,H3`
- Row 14: `L2,L1,L1,L2,L1` → `H3,H3,H3,H3,H3`
- Row 15: `L1,L1,W,L1,L1` → `H3,H3,W,H3,H3`
- Row 33: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3`
- Row 67: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3`
- Row 85: `L1,L1,L1,L1,L5` → `H3,H3,H3,H3,L5`
- Row 150: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3`
- Row 159: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3`

### Phase 2: Replace Scattered Lows
Replace L1-L3 throughout the reel:
- Focus on rows with 1-2 low symbols
- Replace ~60% of scattered L1 with H3
- Replace ~50% of scattered L2 with H3/H2
- Replace ~40% of scattered L3 with H2/H1

### Phase 3: Reduce Wilds
Replace ~12% of wilds (2 symbols) with H2/H3 to offset EV increase.

---

## Expected Impact on Volatility

### Distribution Changes
- **<25×**: 0.9% → ~4-6% (more dead spins)
- **25–50×**: 2.5% → ~2-3%
- **50–100×**: 9.1% → ~5-7%
- **100–250×**: 32.8% → ~22-25% (reduced)
- **250–500×**: 31.1% → ~28-30%
- **500–1000×**: 17.4% → ~20-22%
- **1000×+**: 6.2% → ~10-12% (increased)

### Key Metrics
- **Average Feature Win**: Should remain ~384-390× (wild reduction offsets premium increase)
- **Volatility**: Significantly increased (spikier distribution)
- **Dead Spin Rate**: Increased from 0.9% to 4-6%
- **Premium Win Rate**: Increased (more H1-H3 on reels)
- **Big Win Rate (1000×+)**: Increased from 6.2% to 10-12%

---

## Modification Applied

The modified FR1.csv has been created with the following changes:
1. Reduced L1 by ~50% (replaced with H3/H2)
2. Reduced L2 by ~40% (replaced with H3/H2)
3. Reduced L3 by ~35% (replaced with H2/H1)
4. Reduced L4 by ~15% (replaced with H3/H2)
5. Reduced W by ~12% (replaced with H2/H3)
6. Kept VS and S unchanged

The modification focuses on breaking up low clusters and increasing premium density while maintaining the target average win through wild reduction.

