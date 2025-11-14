# SUPERBONUS Final Balance Report

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

**Date**: 2025-11-07 23:47:03

---

## Executive Summary

| Metric | Target | BEFORE (255×) | AFTER | Change | Status |
|--------|--------|---------------|-------|--------|--------|
| **Average Feature Win** | 384× ± 5× | 255.14× | 1006.33× | +751.19× | ⚠️ |
| **Effective RTP** | 96.2% | 63.79% | 251.58% | +187.79% | |
| **Target RTP** | 96.2% | 96.2% | 96.2% | - | |

---

## Core Statistics Comparison

| Metric | BEFORE (255×) | AFTER | Change |
|--------|---------------|-------|--------|
| **Average Feature Win** | 255.14× | 1006.33× | +751.19× |
| **Effective RTP** | 63.79% | 251.58% | +187.79% |
| **Median Feature Win** | - | 691.80× | - |
| **Min Feature Win** | - | 0.20× | - |
| **Max Feature Win** | - | 10000.00× | - |

---

## Win Distribution by Bucket

| Bucket | BEFORE (255×) | AFTER | Change | % Change |
|--------|---------------|-------|--------|----------|
| **< 25×** | 4.51% | 0.36% | -4.15% | -92.0% |
| **25–50×** | 8.21% | 0.70% | -7.51% | -91.5% |
| **50–100×** | 18.68% | 2.23% | -16.45% | -88.1% |
| **100–250×** | 36.67% | 10.73% | -25.94% | -70.7% |
| **250–500×** | 20.48% | 21.80% | +1.32% | +6.4% |
| **500–1000×** | 8.57% | 30.70% | +22.13% | +258.2% |
| **1000×+** | 2.88% | 33.49% | +30.61% | +1062.7% |

---

## Performance vs Buy Cost

| Threshold | BEFORE (255×) | AFTER | Change |
|-----------|---------------|-------|--------|
| **< 400×** (below cost) | 83.35% | 27.36% | -55.99% |
| **≥ 400×** (at/above cost) | 16.65% | 72.64% | +55.99% |
| **≥ 800×** | 4.69% | 43.42% | +38.73% |
| **≥ 1000×** | 2.88% | 33.49% | +30.61% |

---

## Max Win Cap

| Metric | BEFORE (255×) | AFTER | Change |
|--------|---------------|-------|--------|
| **Win Cap** | 10,000× bet | 10,000× bet | - |
| **Features Hitting Cap** | 3 | 159 | +156 |
| **Cap Hit Rate** | 0.0030% | 0.1592% | +0.1562% |

---

## Interpretation

### RTP Balance Assessment

⚠️ **TOO GENEROUS**: Average feature win (1006.33×) **significantly exceeds** target range (384× + 5× = 389×)
- Current RTP: 251.58% (target: 96.2%)
- Delta from target: **+622.33× above target** (162% over target)
- **Root Cause**: Premium symbols (especially H3) are too abundant - H3 count increased to ~409 vs original 34
- **Issue**: Correction script removed too many low symbols and converted them to premiums, making reels too premium-heavy
- **Recommendation**: 
  - **Reduce H3 significantly**: Convert ~200-250 H3 back to lows (L1/L2/L3)
  - **Reduce wilds**: Lower W count by 3-5 symbols
  - **Increase L1/L2/L3**: Bring lows back to maintain base win frequency without excessive premium spikes
  - Target H3 count: ~150-200 (still high for volatility, but not excessive)
  - Re-balance: More lows for base wins, fewer premiums to reduce massive wins

### Volatility Assessment

⚠️ **Dead spins**: <25× bucket at 0.36% (changed by -4.15%)

✅ **Big wins increased**: 1000×+ bucket at 33.49% (increased by +30.61%)
- More premium spikes (as intended)

⚠️ **Medium wins**: 100–500× range at 32.53% (actually increased by +24.62%)
- This shows too many features in medium-high range
- Combined with 33.49% in 1000×+ range, indicates excessive win frequency
- Need to reduce both premium density and overall win frequency

### Summary

- **Features Analyzed**: 99,900 (wincap excluded)
- **Average Feature Win**: 1006.33× bet ⚠️ (Target: 384×)
- **Effective RTP**: 251.58% ⚠️ (Target: 96.2%)
- **Median Feature Win**: 691.80× bet
- **Below Cost**: 27.36% of features (decreased from 83.35%)
- **Above Cost**: 72.64% of features (increased from 16.65%)
- **1000×+ Hits**: 33.49% of features (increased from 2.88%)
- **Cap Hits**: 0.1592% of features (159 features, increased from 3)

### Key Findings

**Problem**: Correction went too far - removed too many lows and added too many premiums (H3)

**Impact**:
- Average win increased from 255× → 1006× (+295% increase)
- 33.49% of features now pay 1000×+ (vs 2.88% before)
- 72.64% of features pay ≥400× (vs 16.65% before)
- RTP at 251.58% is 2.6× the target

**Required Adjustments**:
1. **Reduce H3 by ~200-250 symbols** (from ~409 to ~150-200)
2. **Convert removed H3 back to L1/L2/L3** to restore base win frequency
3. **Reduce wilds by 3-5 symbols** (from 17 to 12-14)
4. **Target final distribution**:
   - L1: ~140-150 (increase from 125)
   - L2: ~70-75 (increase from 61)
   - L3: ~65-70 (increase from 58)
   - H3: ~150-200 (decrease from 409)
   - W: ~12-14 (decrease from 17)

**Expected Outcome After Correction**:
- Average should drop from 1006× toward 384× target
- Reduce excessive 1000×+ hits from 33.49% to ~5-8%
- Maintain higher volatility than original (more dead spins, fewer medium wins)

**Analysis Date**: 2025-11-07 23:47:03
