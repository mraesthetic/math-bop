# Space Dummies – Math Overview

Space Dummies is a 5×4, 20-line high-volatility slot focused on building sticky wild multipliers and aggressive symbol removal during bonus features. This math package powers the Shift Gaming implementation of the game inside the Carrot Math SDK.

## Core Loop
* Base reels lean heavily on low+mid symbols with carefully spaced scatters and rare premium hits to keep volatility high.
* Wild Gravity Fields can land only on reels 2–4. In the base game they are transient, while in bonuses they stick and carry their multiplier value.
* Wild multipliers are additive. Two wilds showing ×5 and ×10 on the same win line turn a 100× Zog line into a 1,500× payout.

## Bonus Modes
### Rocket Riot (3 scatters)
* Uses `RR0.csv` reel set.
* Includes the full symbol ladder but boosts wild density to jump-start sticky setups.
* Symbol removal ladder: `[s10, sj, sq, sk, sa, sc1, sc2, sc3]`.
* Retriggers (scatter on reels 1 & 5) award +2 spins and remove the next symbol in the ladder.

### Hyperdrive Havoc (4 scatters)
* Uses `HD0.csv` after a one-time purge of all low symbols.
* Reels contain only mid/premium symbols plus sticky wilds and scatters.
* Removal ladder continues through `[sc1, sc2, sc3]`.
* Wild density is higher than Rocket Riot, making max-win climbs more attainable.

### Wincap reel set
* `WCAP.csv` guarantees boards packed with premium Zogs and wilds on reels 2–4.
* Used only for forced max-win simulations; sticky logic plus repeated 10× draws will keep replaying until the 12,500× cap is met.

## Reel Strip Construction
All reel strips are 60 entries (10 for wincap) and share the following design principles:
* **Reel 1 & 5:** No wild symbols, premium rates tuned for volatility.
* **Reels 2–4:** Wild frequency increases from base → Rocket → Hyperdrive.
* **Scatter spacing:** Avoids double-stacking but keeps retrigger possibilities alive.
* **Premium density:** Zog and Chip are rare in the base set, becoming progressively common in Rocket and hyperdrive reels.

### Files
* `BR0.csv` – Base game reels (5×60)
* `RR0.csv` – Rocket Riot bonus reels (5×60)
* `HD0.csv` – Hyperdrive Havoc reels, low symbols removed (5×60)
* `WCAP.csv` – Max-win reel set (5×10)

Each CSV aligns row-wise; row 1 maps to the first stop on all five reels, row 2 to the next stop, etc.

## Implementation Notes
* Sticky wild data and symbol removal state are tracked in `game_override.py`.
* Wild multipliers attach via `assign_mult_property` and are stored for rehydration every free-spin.
* Retriggers call symbol removal, emit events (`stickyWildUpdate`, `symbolRemoval`), and schedule the next spin with the filtered reel strips.

## Next Steps
* Run targeted simulations to balance RTP splits and validate hit rates.
* Tune `game_optimization.py` so the optimization program converges on 96.20% target with the new strips.
* Add pytest coverage for:
  * Wild multiplier addition
  * Sticky wild persistence across free spins
  * Hyperdrive symbol removal progression
# Lines Games

This is an example of a simple lines-game-win

Wilds have multipliers in the freeGame and have the effect of multiplying a given line win by the addition multiplier of values attached to Wild symbols, 
only when the multiplier value is > 1.

Basegame:
Scatter Symbols appear on all reels, a minimum of 3 Scatters are needed to trigger the Freegame

FreeGame:
A separate reelstrip is used for the freegame 
Wilds have larger multipliers (minimum of 2x) and appear on all reels
2 Scatters are needed to trigger extra spins, appearing only on reels 2,3,4


Notes:
Wilds only pay on 5-Kind. If the paytable is chosen such that 3/4 Kind Wilds pay, the line
calculation will assign the highest base-win symbols as winning. For example if there is a 3-Kind
Wild is on the same line as a 5-Kind L4, the 3-Kind wild will be chosen, regardless of the multiplier
on the final Wild since the base payout 3W > 5L4