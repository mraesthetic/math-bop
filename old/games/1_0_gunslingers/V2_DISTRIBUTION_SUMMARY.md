# FR1.csv v2 Distribution - Implementation Summary

**Date**: 2025-11-08

## Overview

Successfully updated FR1.csv to v2 symbol distribution and ran simulation to verify results.

## v2 Symbol Distribution Applied

| Symbol | Previous (169×) | v2 Target | v2 Actual | Status |
|--------|----------------|-----------|-----------|--------|
| **H3** | 170 | 240 | 240 | ✅ |
| **W** | 13 | 16 | 16 | ✅ |
| **L1** | 147 | 147 | 147 | ✅ |
| **L2** | 75 | 75 | 75 | ✅ |
| **L3** | 70 | 70 | 70 | ✅ |
| **L4** | 222 | 184 | 184 | ✅ |
| **L5** | 207 | 172 | 172 | ✅ |
| **Total** | 904 | 904 | 904 | ✅ |

**Other symbols (unchanged)**:
- H1: 35
- H2: 34
- H4: 29
- VS: 2
- S: 11

## Changes Made

1. **Increased H3**: 170 → 240 (+70, converted from L4/L5)
2. **Increased W**: 13 → 16 (+3, converted from L4/L5)
3. **Reduced L4**: 222 → 184 (-38)
4. **Reduced L5**: 207 → 172 (-35)
5. **L1, L2, L3**: Unchanged (147, 75, 70)

## Simulation Results

**Mode**: superbonus (400× buy)  
**Features**: 100,000 (wincap excluded)  
**Date**: 2025-11-08

### v2 Results

- **Average Feature Win**: 278.33× (target: 384× ± 5×)
- **Effective RTP**: 69.58% (target: 96.2%)
- **Median**: 161.00×
- **Min**: 0.20×
- **Max**: 10,000×

### Comparison to Previous Configs

| Config | Avg Win | RTP | Status |
|--------|---------|-----|--------|
| 255× (Too Tight) | 255.14× | 63.79% | Too low |
| 1006× (Too Generous) | 1006.33× | 251.58% | Too high |
| 169× (Over-Corrected) | 169.64× | 42.41% | Too low |
| **v2 (New)** | **278.33×** | **69.58%** | **Still too tight** |

### Progress

- v2 improved from 169× to 278× (+64.3% increase)
- Still 105.67× below target (27.5% short)
- Need ~38% more premium win frequency

## Files Updated

1. ✅ **FR1.csv**: Updated to v2 distribution (H3: 240, W: 16, etc.)
2. ✅ **Backup created**: `FR1.csv.backup_before_v2`
3. ✅ **Report generated**: `SUPERBONUS_BALANCE_VERIFICATION.md`

## Files Verified (No Changes Needed)

- ✅ `game_config.py`: Reads FR1.csv directly (no hardcoded counts)
- ✅ `game_override.py`: Uses FR1.csv from config (no hardcoded references)
- ✅ All other reel strip files (BR0.csv, FR0.csv, FRWCAP.csv): Unchanged

## Automation

The following script can be used to easily update symbol counts and re-run simulations:

**Script**: `games/1_0_gunslingers/finalize_v2_and_simulate.py`

**Usage**:
1. Update `V2_TARGETS` dictionary in script with new target counts
2. Run: `python3 games/1_0_gunslingers/finalize_v2_and_simulate.py`
3. Script will:
   - Update FR1.csv to match targets
   - Run 100k simulation
   - Generate comparison report

## Next Steps

Based on v2 results (278.33×, still 105.67× below target):

**Recommended v3 adjustments**:
- H3: 240 → 270-280 (add 30-40)
- W: 16 → 18-19 (add 2-3)
- L4: 184 → 170-175 (reduce 9-14)
- L5: 172 → 160-165 (reduce 7-12)

**Expected v3 outcome**:
- Average should approach 384× target
- RTP should approach 96.2% target
- Maintain healthy volatility (dead spins, big wins)

---

**Status**: ✅ v2 distribution implemented and verified. Ready for v3 adjustments if needed.

