# Per-Thread RTP Display Issue Analysis

## The Problem

The per-thread RTP values shown during book creation appear incorrect:

```
Thread 2 finished with 7.568 RTP. [baseGame: 0.451, freeGame: 7.117]
Thread 0 finished with 7.958 RTP. [baseGame: 0.451, freeGame: 7.506]
...
Thread 1 finished with 16.407 RTP. [baseGame: 0.385, freeGame: 16.023]
```

These show **700-1600% RTP**, which is clearly wrong!

## Root Cause

The per-thread RTP calculation in `src/state/state.py` (line 271) is:

```python
round(self.win_manager.total_cumulative_wins / (num_sims * mode_cost), 3)
```

**The Issue**: This calculation doesn't account for the **forced condition distributions** used during book creation.

### Base Mode Distributions:
- **Wincap** (0.1%): Forces max win scenarios
- **Freegame** (10%): **FORCES** free spin triggers (`force_freegame: True`)
- **Zero Win** (40%): Forces zero win spins
- **Basegame** (50%): Normal base game spins

### Why It's Wrong:

1. **10% of spins are FORCED to trigger free spins** (via `freegame` distribution)
2. Each forced freegame spin triggers 10-15 free spins
3. Those free spins can win significantly (especially with VS multipliers)
4. But the denominator only counts: `5000 spins × 1× bet = 5000× bet cost`
5. The free spin wins are being divided by the base spin cost, not accounting for the fact that 10% of spins are artificially forced to trigger bonuses

**Example**:
- 500 spins (10%) are forced to trigger free games
- Each triggers ~10 free spins = 5,000 free spins total
- Free spins average ~50× bet each = 250,000× bet in wins
- Denominator: 5,000× bet (only base spins)
- **RTP = 250,000 / 5,000 = 50× = 5000%** (way too high!)

## Why Final Stats Are Correct

The **final aggregated statistics** (in `stats_summary.json`) are correct because:

1. They use **lookup tables** (LUTs) which properly weight all outcomes
2. The optimization process adjusts weights to account for forced conditions
3. The final RTP calculation uses weighted distributions, not raw unweighted sums

## The Per-Thread Display Is Misleading

The per-thread RTP values are **intermediate, unweighted calculations** during book creation. They show:
- Raw win totals divided by raw spin counts
- **Not** the final weighted RTP that accounts for:
  - Forced condition distributions
  - Proper weighting of different outcomes
  - Optimization adjustments

## Conclusion

**The per-thread RTP display is misleading but harmless**:
- ✅ **Final stats are correct**: 96.2% RTP for all modes
- ⚠️ **Per-thread display is wrong**: Shows unweighted, unoptimized values
- ✅ **This is expected behavior**: The optimization process fixes the weighting

## Recommendation

The per-thread RTP display could be improved to show:
1. A note that these are "unweighted intermediate values"
2. Or suppress the display entirely (since it's misleading)
3. Or show the weighted RTP after optimization instead

But the **final results are correct**, so this is a display/UX issue, not a math issue.

---

**Status**: ✅ Final RTP is correct (96.2% for all modes)  
**Issue**: ⚠️ Per-thread display is misleading (shows unweighted values)  
**Impact**: None on final results, but confusing during development

