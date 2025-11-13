# Space Dummies – Frontend Integration Brief

This document highlights every math-side event and state signal the frontend must consume in order to present Space Dummies correctly.

## 1. Event Timeline Overview

Each spin or free spin resolves through the usual Carrot event pipeline:

1. `reveal` – base or bonus board symbols, padding rows, scatter anticipation values.
2. `stickyWildUpdate` / `stickyWildReset` – only during Rocket Riot / Hyperdrive. Keeps the UI in sync with persistent wilds and their multipliers.
3. `symbolRemoval` – emitted whenever a symbol tier is removed from the bonus ladder.
4. `winInfo`, `setWin`, `setTotalWin` – line wins with additive wild multipliers reflected in `meta.multiplier`.
5. `updateFreeSpin` – counted every free-spin reveal.
6. Optional: `freeSpinRetrigger` if scatters land on both reel 1 and reel 5.
7. `freeSpinEnd` / `exitBonus` – final summary and reset when the feature finishes.
8. `finalWin` – overall multiplier for the completed simulation.

## 2. New Event Types

| Event Type            | When Emitted                              | Payload                                                         |
|-----------------------|-------------------------------------------|-----------------------------------------------------------------|
| `stickyWildUpdate`    | After capturing sticky wild positions     | `wilds: [{ reel, row, multiplier }]`                            |
| `stickyWildReset`     | When entering a new bonus or finishing it | No payload (clears sticky state)                                |
| `symbolRemoval`       | After each removal in Rocket/Hyperdrive   | `removedSymbols: [ids], initial: bool`                          |
| `enterBonus`          | On Rocket Riot or Hyperdrive start        | `bonusMode: "rocket" | "hyperdrive"`                           |
| `exitBonus`           | At the end of any bonus                   | No payload                                                      |

The standard `freeSpinTrigger`, `freeSpinRetrigger`, `updateFreeSpin`, `freeSpinEnd`, `winInfo`, `setWin`, `setTotalWin`, `finalWin` events remain unchanged.

### Sticky Wilds
- Wilds only appear on reels 2, 3, 4.
- Multipliers are additive. The payload lists each sticky position plus its multiplier so the frontend can render the correct badge.
- When a new sticky wild lands, the math captures it and emits `stickyWildUpdate` on the same reveal.
- `stickyWildReset` fires before the first sticky placement and after the feature ends—clear any pins in the UI.

### Symbol Removal
- `symbolRemoval` runs whenever a ladder step is removed.
- `initial: true` indicates the pre-bonus removal for Hyperdrive (low symbols purged before spin 1).
- `removedSymbols` is cumulative—rendering logic can hide symbols already removed without tracking separate state.

## 3. Bonus Modes

| Trigger                  | Free Spins | Reel Set | Notes                                                      |
|--------------------------|------------|----------|------------------------------------------------------------|
| 3 scatters (Rocket Riot) | 10         | `RR0`    | Full symbol ladder, stickies start landing aggressively.   |
| 4 scatters (Hyperdrive)  | 10         | `HD0`    | Lows removed up front, only mids + premiums remain.        |

Retriggers (scatter on reels 1 and 5) award `+2` spins and emit `freeSpinRetrigger`. Each retrigger also removes the next available symbol and emits `symbolRemoval`.

## 4. Line Wins

- `winInfo` includes additive wild multipliers in `meta.multiplier`.
- `meta.lineMultiplier` already divides out the global multiplier (always 1 for this math flow).
- When multiple wilds contribute, the multiplier equals the sum. Example: base win `100`, wilds ×5 and ×10 → `win = 1500`, `multiplier = 15`, `lineMultiplier = 15`.

## 5. Bonus Entry & Exit

- `enterBonus` arrives before the sticky wild reset so the UI can play its intro, display the bonus name, and switch reel art.
- `exitBonus` arrives after `freeSpinEnd`—ideal spot to fade out sticky wild indicators and restore base UI.
- `stickyWildReset` is always paired with bonus transitions (before first bonus spin and after the final spin).

## 6. Sample Event Sequence

```
reveal
stickyWildReset
enterBonus (bonusMode: "rocket")
freeSpinTrigger
updateFreeSpin
stickyWildUpdate (wild lands on reel 3, row 2, multiplier 5)
winInfo / setWin / setTotalWin
...
symbolRemoval (removedSymbols: ["s10", "sj"])
freeSpinRetrigger
updateFreeSpin
stickyWildUpdate (same positions + any new)
...
freeSpinEnd
exitBonus
finalWin
```

## 7. Integration Checklist

- [ ] Map new event types onto frontend handlers (Pixi/Svelte components) to show sticky wild overlays and removal states.
- [ ] Update Storybook stories with new event payloads for `stickyWildUpdate`, `symbolRemoval`, and `enterBonus`.
- [ ] Ensure wild badges display additive numbers (e.g., `+5` or `×15`) based on the multiplier value.
- [ ] When a symbol is removed, hide it from the reel art / paytable overlay until the bonus completes.
- [ ] Reset sticky visuals on `stickyWildReset` and after `exitBonus`.

For any questions about the payloads or sequencing, refer back to `src/events/events.py` (math) and the updated reel documentation in `games/0_0_space_dummies/readme.txt`. 

