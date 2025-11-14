# Space Dummies — Frontend Mode & UI Handoff

This note packages everything the frontend team needs to expose the newly wired bet modes (Bonus Hunt, Rocket Riot buy, Hyperdrive buy) and keep the UI synced with current math outputs.

## 1. Mode Mapping (RGS ↔ UI)

| UI Label (suggested) | Math Mode (`index.json`) | Cost (× bet) | Entry State | Notes |
| --- | --- | --- | --- | --- |
| Standard Spin | `base` | 1× | Base reels, natural triggers | Default play button. |
| Bonus Hunt Spin | `bonus_hunt` | 3× | Base reels, boosted scatter quota | Treat as a toggle on the main spin button; when enabled, client should call `bonus_hunt` mode instead of `base`. |
| Rocket Riot Buy | `rocket_buy` | 100× | Forces 3-scatter Rocket Riot | Directly enters 10-spin Rocket Riot with sticky wilds. |
| Hyperdrive Buy | `hyper_buy` | 200× | Forces 4-scatter Hyperdrive | Starts 10 spins with all low symbols removed and sticky wilds. |

- These names appear verbatim in math output (books, lookup tables, future `index.json`). Hook UI selectors/buy buttons to the matching mode name when requesting the math SDK/RGS.
- Costs are already normalized as multipliers of the base bet; display the actual currency by multiplying the player’s chosen stake.

## 2. UI Surface Plan

1. **Bonus Hunt Toggle**
   - Live in the stake/bet strip.
   - OFF → call `base`; ON → call `bonus_hunt`.
   - Show cost text: “3× bet / spin” or similar.

2. **Buy Buttons**
   - “Rocket Riot (100×)” → request `rocket_buy`.
   - “Hyperdrive (200×)” → request `hyper_buy`.
   - Disable while a spin is resolving; respect wallet min/max the same way as standard buys in the Stake SDK.

3. **State Feedback**
   - When entering a buy, immediately swap UI to bonus intro: free-spin counter starts at 10, sticky wild slots highlight reels 2–4.
   - Display a “Bonus Hunt active” indicator so players know the 3× cost is live.

## 3. Frontend Config Touchpoints

_Exact file names vary per project; reference the Stake frontend-sdk docs (§5–8)._

| Area | Action |
| --- | --- |
| Mode registry (e.g. `apps/space_dummies/src/config/modes.ts`) | Add entries for `bonus_hunt`, `rocket_buy`, `hyper_buy` with their costs, localized labels, and availability flags. |
| Game selector / bet bar | Wire the toggle + buttons to call `playRound({ mode: "<modeName>" })`. |
| Storybook stories | Add `MODE_bonus_hunt`, `MODE_rocket_buy`, `MODE_hyper_buy` stories so QA can preview each mode’s books. |
| HUD cost display | Multiply the selected bet size by mode cost to surface the correct total price before the spin/buy is confirmed. |

No backend contract changes are needed: the math SDK already exports these modes once simulations are rerun.

## 4. Event / Animation Hooks

Existing book events (already produced):
- `reveal` → board, padding positions, anticipation.
- `winInfo`, `setWin`, `setTotalWin`, `finalWin` → line wins and payout totals.
- `fsTrigger` → differentiates base trigger vs retrigger.
- `updateFreeSpin` / `freespinEnd` → drive the free-spin counter UI.

Upcoming math work will add dedicated events so the UI can:
- Show new sticky wild placements (reels 2–4, multipliers stacked).
- Announce symbol removal moments (which tier was removed, remaining list).

Plan ahead by reserving emitter handlers for:
- `stickyWildUpdate` (payload: array of `{ reel, row, multiplier, isNew }`).
- `symbolRemovalNotice` (payload: `{ removedSymbol, remainingSymbols, totalRemoved }`).

Once those events are emitted by the math SDK, wire them into the Pixi/Svelte components per the Stake SDK guidance (`bookEventHandlerMap` → `emitterEvent`s).

## 5. QA / UX Checklist

- Ensure toggle/button states stay mutually exclusive and reset after re-entry from a bonus summary.
- Validate wallet math: `stake × cost` lines up with the wager debited from the backend ticket.
- Storybook coverage for each mode so designers can sign off on copy and animations without math reruns.

That’s everything the frontend team needs to expose Bonus Hunt + buys and stay aligned with the current math deliverable. Ping me once the UI is wired so I can keep book events in sync with whatever extra visuals you add.

