# BR0.csv Scatter Reduction Proposal

## Current State Analysis

### BR0.csv Scatter Distribution

| Metric | Value |
|--------|-------|
| **Total rows** | 219 |
| **Total scatter symbols** | 16 |
| **Scatter counts per reel** | [5, 1, 5, 1, 4] |
| **Scatter density** | 1.46% |
| **Rows with scatters** | 5 rows |
| - Rows with 3 scatters | 4 |
| - Rows with 4 scatters | 1 |
| - Rows with 5 scatters | 0 |

### Current Trigger Rates (from BASE_RTP_ANALYSIS.md)

| Trigger Type | Rate | Frequency |
|--------------|------|-----------|
| **3-scatter (Regular Bonus)** | 9.79% | 1 in 10 spins |
| **4-scatter (Superbonus)** | 0.22% | 1 in 450 spins |
| **Total freegame** | 10.01% | 1 in 10 spins |

### Current Configuration (game_config.py)

- **Freegame distribution quota**: 0.1 (10% of spins forced to trigger)
- **Scatter_triggers weights**: `{3: 98, 4: 2}`
  - 98% of triggers become 3-scatter (regular bonus)
  - 2% of triggers become 4-scatter (superbonus)
- **Ratio**: 49:1 (regular:superbonus)

### Current RTP Breakdown

| Component | RTP Contribution | % of Total |
|-----------|------------------|------------|
| Basegame-Only | 42.00% | 3.77% |
| Regular Bonus | 1007.97% | 90.43% |
| Superbonus | 64.69% | 5.80% |
| **Total** | **1114.66%** | **100.00%** |

**Status**: ⚠️ **1114.66% RTP** (1018.46% above 96.2% target)

---

## Target Configuration

### Target Trigger Rates

| Trigger Type | Target Rate | Frequency | RTP Contribution |
|--------------|-------------|-----------|------------------|
| **3-scatter (Regular Bonus)** | 0.55% | 1 in 180 spins | ~0.57× (0.55% × 102.94×) |
| **4-scatter (Superbonus)** | 0.10% | 1 in 1000 spins | ~0.29× (0.10% × 290.81×) |
| **Total freegame** | 0.65% | 1 in 154 spins | ~0.86× |

### Target RTP Breakdown

| Component | Target RTP | % of Total |
|-----------|------------|------------|
| Basegame-Only | ~40-45% | ~42-47% |
| Regular Bonus | ~0.57% | ~0.6% |
| Superbonus | ~0.29% | ~0.3% |
| **Total** | **~96.2%** | **100%** |

### Required Changes

1. **Reduce freegame quota**: 10% → 0.65% (15.4× reduction)
2. **Adjust scatter_triggers weights**: `{3: 98, 4: 2}` → `{3: 85, 4: 15}`
   - Achieves 5.5:1 ratio (0.55% : 0.10%)
3. **Redistribute BR0.csv scatters**: More balanced distribution

---

## Proposed BR0.csv Changes

### Scatter Distribution

| Reel | Current | Target | Change |
|------|---------|--------|--------|
| **Reel 1** | 5 | 4 | -1 |
| **Reel 2** | 1 | 2 | +1 |
| **Reel 3** | 5 | 4 | -1 |
| **Reel 4** | 1 | 2 | +1 |
| **Reel 5** | 4 | 4 | 0 |
| **Total** | **16** | **16** | **0** |

### Scatter Placement Strategy

**New placement** (5 rows with scatters):
- **Row 37**: 3 scatters on reels 1, 3, 5
- **Row 74**: 4 scatters on reels 1, 2, 3, 5
- **Row 110**: 3 scatters on reels 1, 3, 5
- **Row 147**: 4 scatters on reels 1, 3, 4, 5
- **Row 183**: 2 scatters on reels 2, 4

**Rationale**:
- More balanced distribution across reels (reels 2 and 4 increased from 1 to 2)
- Ensures multiple rows have 3+ scatters (enables trigger combinations)
- Maintains total scatter count (16 scatters)
- Well-spread across reelstrip (not clustered)

---

## Required game_config.py Changes

### Change 1: Reduce Freegame Quota

**Location**: `bet_modes[0].distributions[1]` (base mode, freegame distribution)

**Current**:
```python
Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
```

**Proposed**:
```python
Distribution(criteria="freegame", quota=0.0065, conditions=freegame_condition),
```

**Impact**: Reduces forced freegame triggers from 10% to 0.65% of spins

### Change 2: Adjust Scatter Triggers Weights

**Location**: `freegame_condition["scatter_triggers"]`

**Current**:
```python
"scatter_triggers": {3: 98, 4: 2},  # 49:1 ratio
```

**Proposed**:
```python
"scatter_triggers": {3: 85, 4: 15},  # 5.67:1 ratio (target: 5.5:1)
```

**Impact**: 
- Increases 4-scatter (superbonus) probability from 2% to 15% of triggers
- Achieves target ratio of ~5.5:1 (0.55% : 0.10%)

### Change 3: Update Distribution Quotas

After reducing freegame quota, we need to adjust other distributions to maintain total = 1.0:

**Current**:
- Wincap: 0.001 (0.1%)
- Freegame: 0.1 (10%)
- Zero: 0.4 (40%)
- Basegame: 0.5 (50%)
- **Total**: 1.001

**Proposed**:
- Wincap: 0.001 (0.1%)
- Freegame: 0.0065 (0.65%)
- Zero: 0.4 (40%)
- Basegame: 0.5925 (59.25%)
- **Total**: 1.0

**Note**: Basegame quota increases to compensate for reduced freegame quota, maintaining basegame-only RTP.

---

## Expected Outcomes

### Trigger Rates

| Metric | Current | Target | Change |
|--------|---------|--------|--------|
| **3-scatter (Regular Bonus)** | 9.79% | 0.55% | -94.4% |
| **4-scatter (Superbonus)** | 0.22% | 0.10% | -54.5% |
| **Total freegame** | 10.01% | 0.65% | -93.5% |

### RTP Contribution

| Component | Current RTP | Target RTP | Change |
|-----------|-------------|------------|--------|
| **Basegame-Only** | 42.00% | ~42.00% | ~0% (maintained) |
| **Regular Bonus** | 1007.97% | ~0.57% | -1007.40% |
| **Superbonus** | 64.69% | ~0.29% | -64.40% |
| **Total** | **1114.66%** | **~96.2%** | **-1018.46%** |

### RTP Breakdown (Target)

| Component | RTP | % of Total |
|-----------|-----|------------|
| Basegame-Only | 42.00% | 43.6% |
| Regular Bonus | 0.57% | 0.6% |
| Superbonus | 0.29% | 0.3% |
| Wincap | ~0.01% | 0.01% |
| **Total** | **~96.2%** | **100%** |

---

## Implementation Steps

1. **Backup current BR0.csv**
   ```bash
   cp reels/BR0.csv reels/BR0.csv.backup_before_scatter_reduction
   ```

2. **Apply new BR0.csv**
   ```bash
   cp reels/BR0_NEW.csv reels/BR0.csv
   ```

3. **Update game_config.py**
   - Change `freegame` quota from `0.1` to `0.0065`
   - Change `scatter_triggers` from `{3: 98, 4: 2}` to `{3: 85, 4: 15}`
   - Adjust `basegame` quota from `0.5` to `0.5925`

4. **Run verification simulation**
   - Simulate 100,000+ base spins
   - Verify trigger rates: 3-scatter ~0.55%, 4-scatter ~0.10%
   - Verify total RTP: ~96.2%
   - Verify basegame-only RTP: ~40-45%

---

## Summary

### Key Changes

1. **BR0.csv**: Redistribute scatters from `[5, 1, 5, 1, 4]` to `[4, 2, 4, 2, 4]` (more balanced)
2. **game_config.py**: 
   - Reduce freegame quota: 10% → 0.65%
   - Adjust scatter_triggers weights: `{3: 98, 4: 2}` → `{3: 85, 4: 15}`
   - Adjust basegame quota: 50% → 59.25%

### Expected Impact

- **Total RTP**: 1114.66% → ~96.2% (✅ on target)
- **Regular bonus trigger**: 9.79% → 0.55% (✅ ~1 in 180 spins)
- **Superbonus trigger**: 0.22% → 0.10% (✅ ~1 in 1000 spins)
- **Basegame-only RTP**: 42.00% (✅ maintained ~40-45%)

### How This Fixes the Imbalance

1. **Reduces bonus RTP contribution**: From 1072.66% to ~0.86% (99.9% reduction)
2. **Maintains basegame RTP**: Basegame-only remains ~42% (appropriate for 96.2% target)
3. **Achieves target trigger rates**: Regular bonus 0.55%, Superbonus 0.10%
4. **Preserves volatility**: High volatility maintained (many dead spins, rare triggers)

---

## Files Generated

- `reels/BR0_NEW.csv`: New BR0.csv with redistributed scatters
- `BR0_SCATTER_REDUCTION_PROPOSAL.md`: This document

---

**Date**: 2025-11-08  
**Status**: Ready for implementation and verification

