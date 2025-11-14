# SUPERBONUS v2 Distribution Analysis Report

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

**Date**: 2025-11-08 00:40:04

---

## Executive Summary

| Metric | Target | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** | Status |
|--------|--------|------------------|----------------------|----------------------|--------------|--------|
| **Average Feature Win** | 384× ± 5× | 255.14× | 1006.33× | 169.64× | **278.33×** | ⚠️ |
| **Effective RTP** | 96.2% | 63.79% | 251.58% | 42.41% | **69.58%** | |

---

## Core Statistics

| Metric | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **Average Feature Win** | 255.14× | 1006.33× | 169.64× | **278.33×** |
| **Effective RTP** | 63.79% | 251.58% | 42.41% | **69.58%** |
| **Median Feature Win** | - | - | 101.60× | **161.00×** |
| **Min Feature Win** | - | - | 0.20× | **0.20×** |
| **Max Feature Win** | - | - | 10000.00× | **10000.00×** |

---

## Win Distribution by Bucket

| Bucket | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **< 25×** | 4.51% | 0.36% | 9.26% | **5.85%** |
| **25–50×** | 8.21% | 0.70% | 14.57% | **8.98%** |
| **50–100×** | 18.68% | 2.23% | 25.44% | **18.09%** |
| **100–250×** | 36.67% | 10.73% | 32.94% | **33.49%** |
| **250–500×** | 20.48% | 21.80% | 12.45% | **20.13%** |
| **500–1000×** | 8.57% | 30.70% | 4.10% | **9.63%** |
| **1000×+** | 2.88% | 33.49% | 1.25% | **3.82%** |

---

## Performance vs Buy Cost

| Threshold | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|-----------|------------------|----------------------|----------------------|--------------|
| **< 400×** (below cost) | 83.35% | 27.36% | 91.89% | **81.22%** |
| **≥ 400×** (at/above cost) | 16.65% | 72.64% | 8.11% | **18.78%** |
| **≥ 800×** | 4.69% | 43.42% | 1.97% | **5.86%** |
| **≥ 1000×** | 2.88% | 33.49% | 1.25% | **3.82%** |

---

## Max Win Cap

| Metric | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **Win Cap** | 10,000× bet | 10,000× bet | 10,000× bet | 10,000× bet |
| **Features Hitting Cap** | 3 | 159 | 5 | **22** |
| **Cap Hit Rate** | 0.0030% | 0.1592% | 0.0050% | **0.0220%** |

---

## v2 Symbol Distribution

| Symbol | Count | Target | Status |
|--------|-------|--------|--------|
| **H3** | 240 | 240 | ✅ |
| **W** | 16 | 16 | ✅ |
| **L1** | 147 | 147 | ✅ |
| **L2** | 75 | 75 | ✅ |
| **L3** | 70 | 70 | ✅ |
| **L4** | 184 | 184 | ✅ |
| **L5** | 172 | 172 | ✅ |
| **Total** | 904 | 904 | ✅ |

---

## RTP Balance Assessment

### Average Feature Win Analysis

⚠️ **TOO TIGHT**: Average feature win (278.33×) is below target range (384× - 5× = 379×)
- Current RTP: 69.58% (target: 96.2%)
- Delta from target: 105.67× below target
- **Recommendation**: Increase H3 or W slightly

### Volatility Comparison

**Dead Spins (< 25×)**:
- 255× config: 4.51%
- 1006× config: 0.36%
- 169× config: 9.26%
- **v2**: 5.85%
- v2 has more dead spins than 1006× (+5.49%), which is good for volatility

**Big Wins (1000×+)**:
- 255× config: 2.88%
- 1006× config: 33.49%
- 169× config: 1.25%
- **v2**: 3.82%
- v2 is between 169× (1.25%) and 1006× (33.49%) - balanced

**Medium Wins (100–500×)**:
- 255× config: 57.15%
- 1006× config: 32.53%
- 169× config: 45.39%
- **v2**: 53.62%
- v2 has fewer medium wins than 255× (-3.53%) - better volatility

### Overall Assessment

**v2 Status**: ⚠️ **STILL TOO TIGHT** - Average below target
- Current: 278.33× vs Target: 384× ± 5×
- v2 improved from 169× (+64.3% increase) but needs more premium symbols
- Gap to target: 105.67× below target (27.5% short)

**Progress Analysis**:
- 169× → 278×: +109× improvement (good progress)
- 278× → 384×: Need additional +106× (38% more)
- Trend: Moving in right direction, but needs further adjustment

**Comparison to Target**:
- v2 is at 72.5% of target (278/384)
- Need ~38% more premium win frequency to reach target

**Recommendations**:
1. **Increase H3**: 240 → 260-280 (add 20-40 H3)
   - This should add significant premium win potential
2. **Increase W**: 16 → 18-20 (add 2-4 wilds)
   - Wilds help form wins and boost connectivity
3. **Consider**: May need to reduce L4/L5 further to make room
   - Current L4+L5 = 356, could reduce to ~320-330

### Summary

- **Features Analyzed**: 99,900 (wincap excluded)
- **Average Feature Win**: 278.33× bet
- **Effective RTP**: 69.58%
- **Median Feature Win**: 161.00× bet
- **Min Feature Win**: 0.20× bet
- **Max Feature Win**: 10000.00× bet
- **Below Cost**: 81.22% of features
- **Above Cost**: 18.78% of features
- **1000×+ Hits**: 3.82% of features
- **Cap Hits**: 0.0220% of features (22 features)

**Analysis Date**: 2025-11-08 00:40:04
