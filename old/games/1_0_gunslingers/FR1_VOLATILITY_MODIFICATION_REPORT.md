# FR1.csv Volatility Modification Report

## Current Problem
The superbonus feature is too flat:
- Too many medium wins (100–500× range: 63.9% of features)
- Very few dead features (<25×: only 0.9%)
- Average win: 394.05× (slightly above target 384.8×)

**Goal**: Increase volatility by reducing small/medium wins and creating more spiky, premium-heavy outcomes.

---

## Modification Strategy

### 1. Symbol Replacement Plan

| Symbol | Current Count (approx) | Reduction Target | Replacement Strategy |
|--------|------------------------|------------------|----------------------|
| **L1** | ~120-140 | -50% | → H3 (80%), H2 (20%) |
| **L2** | ~50-70 | -40% | → H3 (60%), H2 (40%) |
| **L3** | ~60-80 | -35% | → H2 (70%), H1 (30%) |
| **L4** | ~80-100 | -15% | → H3 (80%), H2 (20%) |
| **W** | ~15-20 | -12% | → H2 (50%), H3 (50%) |
| **VS** | 2 | 0% | Keep unchanged |
| **S** | ~8-10 | 0% | Keep unchanged |

### 2. Priority Order
1. **Break up low clusters**: Replace L1-L3 in rows with 3+ low symbols (highest impact)
2. **Replace scattered lows**: Replace L1-L3 throughout the reel
3. **Reduce wilds**: Replace some W to offset EV increase from premiums

### 3. Expected Impact
- **More dead spins**: Fewer low symbols = more complete whiffs
- **More premium wins**: Higher H1-H3 density = bigger wins when they hit
- **Increased volatility**: Spikier distribution (more <25× and more 1000×+)
- **Average maintained**: Wild reduction offsets premium increase

---

## Before/After Comparison

### Overall Symbol Counts

| Symbol | Before | After | Change | % Change |
|--------|--------|-------|--------|----------|
| H1 | ~40-50 | ~55-65 | +15 | +30% |
| H2 | ~60-70 | ~90-100 | +30 | +45% |
| H3 | ~70-80 | ~140-150 | +70 | +90% |
| H4 | ~50-60 | ~50-60 | 0 | 0% |
| L1 | ~120-140 | ~60-70 | -60 | -50% |
| L2 | ~50-70 | ~30-40 | -20 | -40% |
| L3 | ~60-80 | ~40-50 | -20 | -35% |
| L4 | ~80-100 | ~70-85 | -10 | -15% |
| L5 | ~80-100 | ~80-100 | 0 | 0% |
| W | ~15-20 | ~13-18 | -2 | -12% |
| VS | 2 | 2 | 0 | 0% |
| S | ~8-10 | ~8-10 | 0 | 0% |

### Category Totals

| Category | Before | After | Change |
|----------|--------|-------|--------|
| Premiums (H1-H4) | ~220-260 | ~335-375 | +115 |
| Lows (L1-L5) | ~390-450 | ~280-345 | -110 |
| Specials (W,VS,S) | ~25-32 | ~23-30 | -2 |

---

## Implementation Notes

1. **Low Cluster Priority**: Rows with 3+ L1/L2/L3 symbols are targeted first
2. **Replacement Distribution**: 
   - L1 → Mostly H3 (increases mid-premium density)
   - L2 → Mix of H3/H2
   - L3 → Mix of H2/H1 (higher premiums for better volatility)
3. **Wild Reduction**: Small reduction to offset EV increase
4. **VS/S Preservation**: Critical symbols kept unchanged

---

## Expected Results After Modification

### Distribution Changes
- **<25×**: 0.9% → ~3-5% (more dead spins)
- **25–50×**: 2.5% → ~2-3%
- **50–100×**: 9.1% → ~6-8%
- **100–250×**: 32.8% → ~25-28% (reduced)
- **250–500×**: 31.1% → ~28-30%
- **500–1000×**: 17.4% → ~18-20%
- **1000×+**: 6.2% → ~8-10% (increased)

### Key Metrics
- Average Feature Win: ~384-390× (maintained near target)
- Volatility: Significantly increased (spikier distribution)
- Premium Hit Rate: Increased (more H1-H3 on reels)
- Dead Spin Rate: Increased (fewer low symbols)

---

## Next Steps

1. Run simulation with modified FR1.csv
2. Verify average stays near 384×
3. Confirm volatility increase (more <25× and more 1000×+)
4. Adjust if needed (fine-tune symbol counts)

