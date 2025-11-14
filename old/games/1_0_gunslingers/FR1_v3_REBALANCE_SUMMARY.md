# FR1.csv v3 Rebalance Summary

**Date**: 2025-11-08 00:54:33

## Objective

Final mild rebalance to increase RTP from 69.58% (278.33×) toward 96.2% (384×) target while maintaining volatility.

## v2 → v3 Symbol Adjustments

| Symbol | v2 (Current) | v3 Target | v3 Actual | Change | Status |
|--------|--------------|-----------|-----------|--------|--------|
| **H3** | 240 | 270 ± 10 | 270 | +30 | ✅ |
| **W** | 16 | 19 ± 1 | 19 | +3 | ✅ |
| **L1** | 147 | 147 (unchanged) | 147 | +0 | ✅ |
| **L2** | 75 | 75 (unchanged) | 75 | +0 | ✅ |
| **L3** | 70 | 70 (unchanged) | 70 | +0 | ✅ |
| **L4** | 184 | 165 ± 5 | 168 | -16 | ✅ |
| **L5** | 172 | 155 ± 5 | 155 | -17 | ✅ |

**Other symbols (unchanged)**:
- H1: 35
- H2: 34
- H4: 29
- VS: 2
- S: 11

## Category Changes

| Category | v2 Before | v3 After | Change |
|----------|-----------|----------|--------|
| **Premiums (H1-H4)** | 338 | 368 | +30 |
| **Lows (L1-L5)** | 648 | 615 | -33 |
| **Specials (W,VS,S)** | 29 | 32 | +3 |

## Expected Impact

**v2 Performance**:
- Average Feature Win: 278.33×
- Effective RTP: 69.58%
- Median: 161.00×

**Estimated v3 Performance**:
- Average Feature Win: ~337.4× (estimate)
- Effective RTP: ~84.36% (estimate)
- Estimated increase: +59.1× from v2

**Target**:
- Average Feature Win: 384× ± 5× (379× - 389×)
- Effective RTP: 96.2%

**Status**: ⚠️ May need fine-tuning after simulation

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

- Converted 30 L4/L5 → H3
- Converted 3 L4/L5 → W
- Total symbols converted: 33
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
