# BASE Bet Mode RTP Verification Report

**Analysis Date**: 2025-11-08  
**Configuration**: Updated BR0.csv + game_config.py changes applied

---

## RTP Decomposition

| Component | RTP Contribution | % of Total RTP | Count | Avg Win | Target Status |
|-----------|------------------|----------------|-------|---------|---------------|
| **Basegame-Only** | 49.72% | 42.44% | 99,250 | 0.50× | ⚠️ High (target: 40-45%) |
| **Regular Bonus** | 41.75% | 35.64% | 550 | 75.75× | ✅ On target |
| **Superbonus** | 25.68% | 21.92% | 100 | 256.26× | ✅ On target |
| **Wincap** | 1001.00% | (excluded) | 100 | 10,000.00× | (test spins) |
| **Total** | **117.14%** | **100.00%** | 99,800 | 1.17× | ⚠️ Above target (96.2%) |

---

## Natural Trigger Rates from Base

| Trigger Type | Rate | Frequency | Target | Status |
|--------------|------|-----------|--------|--------|
| **3-scatter (Regular Bonus)** | 0.55% | 1 in 182 spins | 0.5-0.7% | ✅ **PERFECT** |
| **4-scatter (Superbonus)** | 0.1002% | 1 in 998 spins | 0.05-0.15% | ✅ **PERFECT** |
| **Total freegame** | 0.65% | 1 in 154 spins | ~0.65% | ✅ **PERFECT** |

**Trigger Ratio**: 5.5:1 (regular:superbonus) ✅ Matches target ratio

---

## Status Summary

### ✅ **ON TARGET** - Trigger Rates
- Regular bonus trigger: **0.55%** (target: 0.5-0.7%) ✅
- Superbonus trigger: **0.10%** (target: 0.05-0.15%) ✅
- Total freegame: **0.65%** ✅

### ⚠️ **ABOVE TARGET** - Total RTP
- Current: **117.14%**
- Target: **96.2%**
- Difference: **+20.94% RTP**

### ⚠️ **SLIGHTLY HIGH** - Basegame-Only RTP
- Current: **49.72%**
- Target: **40-45%**
- Difference: **+4.72% to +9.72%**

---

## Analysis

### What's Working ✅

1. **Trigger rates are perfect**: The freegame quota (0.0065) and scatter_triggers weights ({3: 85, 4: 15}) are correctly calibrated to achieve the target trigger rates.

2. **Bonus RTP contributions are reasonable**:
   - Regular bonus: 41.75% RTP from 0.55% trigger rate
   - Superbonus: 25.68% RTP from 0.10% trigger rate
   - Total bonus: 67.42% RTP

### What Needs Adjustment ⚠️

1. **Total RTP is 20.94% too high**: 117.14% vs 96.2% target
   - Basegame-only: 49.72% (should be ~40-45%)
   - Bonus total: 67.42% (should be ~51-56%)

2. **Basegame-only RTP is too high**: 49.72% vs target 40-45%
   - This is the main contributor to excess RTP
   - Need to reduce basegame RTP by ~5-10%

3. **Note on bonus averages**: 
   - Regular bonus average: 75.75× (lower than expected 92.1× from buy mode)
   - Superbonus average: 256.26× (lower than expected 377-384× from buy mode)
   - This may be due to different conditions when triggered naturally vs. bought

---

## Recommendations

### Primary Fix: Reduce Basegame-Only RTP

The main issue is that basegame-only RTP (49.72%) is higher than target (40-45%). To reduce total RTP from 117.14% to 96.2%, we need to reduce basegame RTP by approximately **20.94%**.

**Option 1: Reduce basegame quota (increase zero-win quota)**
- Current: basegame 59.25%, zero 40%
- Proposed: basegame 54.25%, zero 45%
- This reduces basegame spins from 59.25% to 54.25% of total
- Expected basegame RTP reduction: ~8.4% (49.72% × 0.5425/0.5925 = 45.52%)
- Expected total RTP: ~112.86% (still 16.66% above target)

**Option 2: Reduce basegame paytable values**
- Slightly reduce premium symbol payouts or symbol frequencies in BR0.csv
- This directly reduces basegame RTP contribution
- More precise control but requires reelset rebalancing

**Option 3: Combination approach**
- Reduce basegame quota slightly (basegame 57%, zero 43%)
- AND reduce basegame paytable values slightly
- This provides fine-grained control

### Secondary Adjustments (if needed)

If basegame reduction isn't enough:

1. **Slightly reduce freegame quota**: From 0.0065 to 0.0055 (0.55% trigger rate)
   - This reduces bonus RTP contribution by ~10%
   - Regular bonus: 41.75% → ~37.58%
   - Superbonus: 25.68% → ~23.11%
   - Total bonus: 67.42% → ~60.69%

2. **Adjust scatter_triggers weights**: From {3: 85, 4: 15} to {3: 88, 4: 12}
   - This slightly increases regular bonus rate and decreases superbonus rate
   - Minor impact on total RTP

---

## Recommended Action Plan

### Step 1: Reduce Basegame-Only RTP (Primary Fix)

**Proposed change to game_config.py:**
```python
# Current
Distribution(criteria="basegame", quota=0.5925, conditions=basegame_condition),
Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),

# Proposed
Distribution(criteria="basegame", quota=0.54, conditions=basegame_condition),
Distribution(criteria="0", quota=0.4535, win_criteria=0.0, conditions=zerowin_condition),
```

**Expected impact:**
- Basegame-only RTP: 49.72% → ~45.33% (reduction of ~4.39%)
- Total RTP: 117.14% → ~112.75% (still ~16.55% above target)

### Step 2: Fine-tune with Paytable Adjustment (If Needed)

If Step 1 isn't sufficient, reduce basegame paytable values in BR0.csv:
- Reduce premium symbol frequencies slightly
- OR reduce premium symbol payouts slightly

### Step 3: Verify

Run simulation again and verify:
- Total RTP: ~96.2%
- Basegame-only RTP: ~40-45%
- Trigger rates: Maintain 0.55% regular, 0.10% superbonus

---

## Summary Table

| Metric | Current | Target | Status | Action Needed |
|--------|---------|--------|--------|---------------|
| **Total RTP** | 117.14% | 96.2% | ⚠️ +20.94% | Reduce basegame RTP |
| **Basegame-Only RTP** | 49.72% | 40-45% | ⚠️ +4.72% to +9.72% | Reduce basegame quota/paytable |
| **Regular Bonus Trigger** | 0.55% | 0.5-0.7% | ✅ Perfect | None |
| **Superbonus Trigger** | 0.10% | 0.05-0.15% | ✅ Perfect | None |
| **Regular Bonus RTP** | 41.75% | ~50%* | ⚠️ Lower | (Expected 50.66% with 92.1× avg) |
| **Superbonus RTP** | 25.68% | ~38%* | ⚠️ Lower | (Expected 38% with 380× avg) |

*Note: Bonus RTP contributions are lower than expected because average wins (75.75× and 256.26×) are lower than buy mode averages (92.1× and 377-384×). This is actually helpful for reducing total RTP, but may indicate that features perform differently when triggered naturally vs. bought.

---

## Conclusion

**Trigger rates are perfect** ✅ - No changes needed to freegame quota or scatter_triggers weights.

**Total RTP needs reduction** ⚠️ - Primary issue is basegame-only RTP being too high (49.72% vs target 40-45%).

**Recommended fix**: Reduce basegame quota from 59.25% to 54% (increase zero-win from 40% to 45.35%) to reduce basegame RTP by ~4.4%. If this isn't sufficient, additional paytable adjustments may be needed.

---

**Status**: ⚠️ **ABOVE TARGET** - Needs basegame RTP reduction

