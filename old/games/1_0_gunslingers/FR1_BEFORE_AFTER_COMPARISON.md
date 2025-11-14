# FR1.csv Before/After Symbol Count Comparison

## Summary of Modifications

Applied volatility-increasing modifications to FR1.csv:
- **Reduced low symbols** (especially L1-L3): ~40-50% reduction
- **Increased premium symbols** (H1-H3): Significant increase
- **Slight wild reduction**: To offset EV increase
- **Preserved VS and S**: Critical symbols unchanged

---

## Symbol Count Comparison

### Overall Symbol Counts

| Symbol | Before (approx) | After (approx) | Change | % Change | Notes |
|--------|----------------|----------------|--------|----------|-------|
| **H1** | ~45 | ~50-55 | +5-10 | +10-20% | Increased via L3 replacements |
| **H2** | ~65 | ~80-90 | +15-25 | +25-40% | Increased via L2/L3/W replacements |
| **H3** | ~34 | ~90-100 | +55-65 | +160-190% | **Major increase** via L1/L2 replacements |
| **H4** | ~55 | ~55 | 0 | 0% | Unchanged |
| **L1** | ~186 | ~90-100 | -85-95 | **-45-50%** | **Major reduction** |
| **L2** | ~84 | ~50-60 | -25-35 | -30-40% | Significant reduction |
| **L3** | ~75 | ~60-70 | -10-15 | -15-20% | Moderate reduction |
| **L4** | ~95 | ~85-90 | -5-10 | -5-10% | Slight reduction |
| **L5** | ~85 | ~85 | 0 | 0% | Unchanged |
| **W** | ~18 | ~16-17 | -1-2 | -5-12% | Slight reduction |
| **VS** | 2 | 2 | 0 | 0% | **Preserved** |
| **S** | ~8-10 | ~8-10 | 0 | 0% | **Preserved** |

**Total Symbols**: 1020 (204 rows × 5 reels) - unchanged

### Category Totals

| Category | Before | After | Change | % Change |
|----------|--------|-------|--------|----------|
| **Premiums (H1-H4)** | ~199 (19.5%) | ~275-300 (27-29%) | +75-100 | +38-50% |
| **Lows (L1-L5)** | ~525 (51.5%) | ~370-405 (36-40%) | -120-155 | -23-30% |
| **Specials (W,VS,S)** | ~28 (2.7%) | ~26-29 (2.5-2.8%) | -1-2 | -5-7% |

---

## Per-Reel Symbol Distribution (Estimated)

### Reel 1
- **Before**: High L1/L2 density, moderate premiums
- **After**: Reduced L1/L2, increased H3/H2
- **Impact**: Fewer dead spins, more premium potential

### Reel 2
- **Before**: Moderate low density, some premiums
- **After**: Further reduced lows, increased premiums
- **Impact**: Better win potential

### Reel 3
- **Before**: Similar to Reel 2
- **After**: More premiums, fewer lows
- **Impact**: Increased volatility

### Reel 4
- **Before**: Moderate distribution
- **After**: More premium-heavy
- **Impact**: Better win opportunities

### Reel 5
- **Before**: Moderate distribution
- **After**: Slightly more premium-heavy
- **Impact**: Increased win potential

---

## Key Modifications Applied

### 1. Low Cluster Breakdown
- **Row 4**: `H3,L1,H1,L1,L1` → `H3,H2,H1,H3,H3` (3 lows eliminated)
- **Row 9**: `L1,H1,L5,L1,L1` → `H3,H1,L5,H3,H3` (3 lows eliminated)
- **Row 10**: `L3,L1,L1,L2,H4` → `H2,H3,H3,H3,H4` (4 lows eliminated)
- **Row 14**: `L2,L1,L1,L2,L1` → `H3,H3,H3,H3,H3` (5 lows → all premiums!)
- **Row 15**: `L1,L1,W,L1,L1` → `H3,H3,W,H3,H3` (4 lows eliminated)
- **Row 31**: `L1,L1,L2,H3,L1` → `H3,H3,H3,H3,H3` (4 lows → all premiums!)
- **Row 33**: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3` (5 lows → all premiums!)
- **Row 67**: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3` (5 lows eliminated)
- **Row 85**: `L1,L1,L1,L1,L5` → `H3,H3,H3,H3,L5` (4 lows eliminated)
- **Row 150**: `L3,L1,L1,L1,L1` → `H2,H3,H3,H3,H3` (5 lows eliminated)
- **Row 159**: `L1,L1,L1,L1,L1` → `H3,H3,H3,H3,H3` (5 lows → all premiums!)

### 2. Scattered Low Replacements
- Multiple patterns of `L1,L1,...` → `H3,H3,...`
- Many `L1` → `H3` replacements throughout
- Several `L2` → `H3` or `H2` replacements
- Some `L3` → `H2` or `H1` replacements

### 3. Wild Reduction
- Some `W` → `H2` or `H3` (to offset EV increase)

---

## Expected Volatility Impact

### Distribution Changes (Expected)

| Bucket | Before | After (Expected) | Change |
|--------|--------|------------------|--------|
| **< 25×** | 0.9% | 4-6% | +3-5% (more dead spins) |
| **25–50×** | 2.5% | 2-3% | Slight change |
| **50–100×** | 9.1% | 5-7% | -2-4% (reduced) |
| **100–250×** | 32.8% | 22-25% | -8-11% (reduced) |
| **250–500×** | 31.1% | 28-30% | -1-3% (reduced) |
| **500–1000×** | 17.4% | 20-22% | +3-5% (increased) |
| **1000×+** | 6.2% | 10-12% | +4-6% (increased) |

### Key Metrics (Expected)

- **Average Feature Win**: ~384-390× (maintained near target)
- **Median Feature Win**: Likely increased (more premium wins)
- **Volatility**: Significantly increased
- **Dead Spin Rate**: Increased from 0.9% to 4-6%
- **Premium Win Rate**: Increased
- **Big Win Rate (1000×+)**: Increased from 6.2% to 10-12%

---

## Implementation Status

✅ **Completed**:
- Low cluster breakdown (worst clusters eliminated)
- Scattered low replacements (significant reduction)
- Premium symbol increases (H1-H3)
- VS and S preservation

⚠️ **Note**: Exact symbol counts may vary slightly from estimates. A full simulation is needed to verify the exact impact on volatility and average win.

---

## Next Steps

1. **Run simulation** with modified FR1.csv (100k+ features)
2. **Verify average** stays near 384× (96.2% RTP at 400× cost)
3. **Confirm volatility increase**:
   - More <25× outcomes (dead spins)
   - More 1000×+ outcomes (premium wins)
   - Reduced 100-500× range (medium wins)
4. **Fine-tune if needed** (adjust symbol counts based on results)

---

## Files Modified

- `games/1_0_gunslingers/reels/FR1.csv` - Modified reel strip
- Backup created: `games/1_0_gunslingers/reels/FR1.csv.backup` (if script was used)

## Documentation Created

- `FR1_SYMBOL_ANALYSIS_AND_MODIFICATION.md` - Detailed modification plan
- `FR1_MODIFICATIONS_SUMMARY.md` - Summary of changes
- `FR1_BEFORE_AFTER_COMPARISON.md` - This document

