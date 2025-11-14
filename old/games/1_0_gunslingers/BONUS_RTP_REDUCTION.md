# Regular Bonus RTP Reduction Summary

## Changes Made

### Updated VS Multiplier Distribution for Bonus Mode

**File**: `game_config.py`  
**Location**: `self.padding_symbol_values["VS"]["multiplier"]`

#### Old Distribution:
```python
{2: 750, 3: 200, 4: 70, 5: 30, 8: 7, 10: 3}
```
- Total weight: 1060
- Average multiplier: ~2.468×
- Probabilities:
  - 2×: 70.75%
  - 3×: 18.87%
  - 4×: 6.60%
  - 5×: 2.83%
  - 8×: 0.66%
  - 10×: 0.28%

#### New Distribution:
```python
{2: 840, 3: 170, 4: 50, 5: 15, 8: 3, 10: 1}
```
- Total weight: 1079
- Average multiplier: ~2.317×
- Probabilities:
  - 2×: 77.85% (+7.10%)
  - 3×: 15.76% (-3.11%)
  - 4×: 4.63% (-1.97%)
  - 5×: 1.39% (-1.44%)
  - 8×: 0.28% (-0.38%)
  - 10×: 0.09% (-0.19%)

### Impact Calculation

**Multiplier Reduction**: 
- Old average: 2.468×
- New average: 2.317×
- Reduction: 6.1%

**Expected Feature Win Impact**:
- Current avg feature win: 102.33× bet
- Estimated new avg: 102.33 × 0.939 = **96.09× bet**
- Target: 96.2× bet
- Difference: -0.11× bet (within tolerance)

**Expected RTP**:
- Current RTP: 102.33% (102.33 / 100)
- Estimated new RTP: **96.09%** (96.09 / 100)
- Target RTP: 96.2%
- Difference: -0.11% (within tolerance)

## What Changed

1. **Increased 2× multiplier weight**: 750 → 840 (+90, +12%)
   - Most common multiplier, lowest value
   - Increases probability from 70.75% to 77.85%

2. **Reduced 3× multiplier weight**: 200 → 170 (-30, -15%)
   - Second most common multiplier
   - Decreases probability from 18.87% to 15.76%

3. **Reduced 4× multiplier weight**: 70 → 50 (-20, -28.6%)
   - Medium-high multiplier
   - Decreases probability from 6.60% to 4.63%

4. **Reduced 5× multiplier weight**: 30 → 15 (-15, -50%)
   - High multiplier, significant reduction
   - Decreases probability from 2.83% to 1.39%

5. **Reduced 8× multiplier weight**: 7 → 3 (-4, -57.1%)
   - Very high multiplier, major reduction
   - Decreases probability from 0.66% to 0.28%

6. **Reduced 10× multiplier weight**: 3 → 1 (-2, -66.7%)
   - Highest multiplier, largest percentage reduction
   - Decreases probability from 0.28% to 0.09%

## What Did NOT Change

✅ **Paytable values**: All symbol payouts remain unchanged  
✅ **Line payouts**: All line win values remain unchanged  
✅ **Base game**: No changes to base game mechanics  
✅ **Superbonus**: Uses separate `superbonus_vs_multipliers` (unchanged)  
✅ **VS appearance frequency**: Reel strips (FR0.csv) unchanged  
✅ **VS expansion logic**: Still expands entire reel to wild  
✅ **VS multiplier cap**: Still capped at 250× combined  

## Files Modified

1. **game_config.py**
   - Updated `self.padding_symbol_values["VS"]["multiplier"]`
   - Updated comments to reflect new target RTP

## Next Steps

1. **Run simulation** to verify actual results:
   ```bash
   make run GAME=1_0_gunslingers
   ```

2. **Check statistics**:
   ```bash
   cat math-sdk/games/1_0_gunslingers/library/stats_summary.json
   ```

3. **Verify**:
   - Average bonus feature win ≈ 96.2× bet (± tolerance)
   - Bonus RTP ≈ 96.2% (± tolerance)

4. **If adjustment needed**:
   - Slightly increase 2× weight if RTP too high
   - Slightly decrease 2× weight if RTP too low
   - Fine-tune 3×, 4× weights as needed

## Notes

- The reduction is achieved by shifting probability from higher multipliers to the lowest (2×)
- This maintains the exciting potential (10× still possible, just rarer)
- The change only affects bonus mode; base and superbonus are unchanged
- All changes are in math config only; no code logic changes needed

