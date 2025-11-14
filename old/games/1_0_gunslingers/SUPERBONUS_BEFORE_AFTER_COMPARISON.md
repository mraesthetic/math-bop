# SUPERBONUS Volatility Comparison: BEFORE vs AFTER FR1 Modification

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

---

## Executive Summary

| Metric | Target | BEFORE | AFTER | Status |
|--------|--------|--------|-------|--------|
| **Average Feature Win** | 384× ± 5× | 394.05× | 255.14× | ❌ **Too Low** |
| **Effective RTP** | 96.2% | 98.51% | 63.79% | ❌ **Too Low** |
| **Dead Spins (<25×)** | Increase | 0.90% | 4.51% | ✅ Increased |
| **Big Wins (1000×+)** | Increase | 6.19% | 2.88% | ❌ Decreased |
| **Medium Wins (100-500×)** | Decrease | 63.83% | 57.15% | ✅ Decreased |

**Verdict**: ❌ **Modification too aggressive** - Average dropped 35.3% below target. Need to dial back changes and restore some low symbols to maintain base win frequency.

---

## Core Statistics Comparison

| Metric | BEFORE | AFTER | Change | Status |
|--------|--------|-------|--------|--------|
| **Average Feature Win** | 394.05× | 255.14× | -138.91× | ⚠️ |
| **Effective RTP** | 98.51% | 63.79% | -34.72% | |
| **Target RTP** | 96.2% | 96.2% | - | |
| **Median Feature Win** | - | 161.00× | - | |
| **Min Feature Win** | - | 0.20× | - | |
| **Max Feature Win** | - | 10000.00× | - | |

---

## Win Distribution by Bucket

| Bucket | BEFORE | AFTER | Change | % Change |
|--------|--------|-------|--------|----------|
| **< 25×** | 0.90% | 4.51% | +3.61% | +401.3% |
| **25–50×** | 2.51% | 8.21% | +5.70% | +227.1% |
| **50–100×** | 9.14% | 18.68% | +9.54% | +104.3% |
| **100–250×** | 32.76% | 36.67% | +3.91% | +11.9% |
| **250–500×** | 31.07% | 20.48% | -10.59% | -34.1% |
| **500–1000×** | 17.43% | 8.57% | -8.86% | -50.8% |
| **1000×+** | 6.19% | 2.88% | -3.31% | -53.5% |

---

## Performance vs Buy Cost

| Threshold | BEFORE | AFTER | Change |
|-----------|--------|-------|--------|
| **< 400×** (below cost) | 67.49% | 83.35% | +15.86% |
| **≥ 400×** (at/above cost) | 32.51% | 16.65% | -15.86% |
| **≥ 800×** | 10.05% | 4.69% | -5.36% |
| **≥ 1000×** | 6.19% | 2.88% | -3.31% |

---

## Max Win Cap

| Metric | BEFORE | AFTER | Change |
|--------|--------|-------|--------|
| **Win Cap** | 10,000× bet | 10,000× bet | - |
| **Features Hitting Cap** | 15 | 3 | -12 |
| **Cap Hit Rate** | 0.0150% | 0.0030% | -0.0120% |

---

## Interpretation

### RTP Balance Assessment

⚠️ **TOO TIGHT**: Average feature win (255.14×) is **significantly below** target (384× - 5× = 379×)
- Current RTP: 63.79% (target: 96.2%)
- **Delta from target**: -128.86× (33.6% below target)
- **Issue**: Modification was too aggressive - removed too many low symbols without sufficient compensation
- **Recommendation**: Dial back the modifications:
  - Add back some L1/L2 symbols (reduce reduction from 50% to ~30-35%)
  - Keep more L4/L5 symbols (reduce their reduction)
  - Increase wild (W) density slightly to boost base win frequency
  - Ensure premium increases are balanced with base win maintenance

### Volatility Assessment

✅ **Dead spins increased**: <25× bucket increased by 3.61% (0.90% → 4.51%)
- More complete whiffs (as intended)

❌ **Big wins DECREASED**: 1000×+ bucket decreased by -3.31% (6.19% → 2.88%)
- This is the **opposite** of the intended effect
- Issue: Too many low symbols removed reduced base win frequency
- Premium symbols alone don't guarantee big wins if base combinations are harder to form

✅ **Medium wins reduced**: 100–500× range decreased by 6.68% (63.83% → 57.15%)
- Fewer flat medium wins (as intended)
- However, this reduction came at the cost of overall RTP

### Detailed Analysis

#### What Worked ✅
1. **Dead spins increased**: <25× bucket increased from 0.90% to 4.51% (+401%)
   - More complete whiffs (as intended for volatility)
2. **Medium wins reduced**: 100–500× range decreased from 63.83% to 57.15%
   - Fewer flat medium wins (as intended)

#### What Didn't Work ❌
1. **Average win dropped too much**: 394.05× → 255.14× (-35.3%)
   - Way below target of 384× ± 5×
   - RTP dropped from 98.51% to 63.79% (-34.7 percentage points)
2. **Big wins decreased**: 1000×+ bucket decreased from 6.19% to 2.88% (-53.5%)
   - Opposite of intended effect
   - Premium symbols don't help if base wins are too rare
3. **Above-cost hits decreased**: 32.51% → 16.65% (-48.8%)
   - Too many features now pay less than the buy cost

#### Root Cause Analysis
The modification was **too aggressive**:
- Removed too many low symbols (L1-L3) reduced base win frequency
- Premium symbols (H1-H3) alone don't guarantee wins - they need to form combinations
- With fewer low symbols, it's harder to form winning combinations overall
- The guaranteed VS per spin helps, but not enough to compensate for the loss of base wins

#### Recommendations for Next Iteration
1. **Reduce modification intensity**: 
   - L1 reduction: 50% → 30-35%
   - L2 reduction: 40% → 25-30%
   - L3 reduction: 35% → 20-25%
   - Keep L4/L5 mostly unchanged
2. **Increase wild density**: Add more W symbols (they help form wins)
3. **Maintain better balance**: Don't remove lows without ensuring base win frequency is maintained
4. **Test incrementally**: Make smaller changes and test, rather than large sweeping changes

### Summary

- **Features Analyzed**: 99,900 (wincap excluded)
- **Average Feature Win**: 255.14× bet ⚠️ (Target: 384×)
- **Effective RTP**: 63.79% ⚠️ (Target: 96.2%)
- **Below Cost**: 83.35% of features (increased from 67.49%)
- **Above Cost**: 16.65% of features (decreased from 32.51%)
- **1000×+ Hits**: 2.88% of features (decreased from 6.19%)
- **Cap Hits**: 0.0030% of features (3 features, decreased from 15)

**Verdict**: ❌ **Modification too aggressive - needs dialing back**

**Analysis Date**: 2025-11-07 23:17:41
