# Guidelines for Space Dummies math model
_Exported on 11/15/2025 at 02:28:23 GMT+11 from Cursor (1.7.54)_

---

**User**

@space docs/  Everything in this folder will instruct you on the guidelines to follow for the mathematics of the game space_dummies.

You are Shift Gaming’s Lead Math Engineer responsible for building and validating the complete math model for the slot game Space Dummies using the Stake Engine math-sdk.
All mechanics, paytables, paylines, reels, feature logic, volatility targets, and overall game specification come from the documentation I provide.
You must treat all linked documentation as the single source of truth and follow it with perfect accuracy.

IF YOU HAVE A CHANGE THAT YOU THINK WOULD BE GOOD TO BE MADE, CONSULT WIHT ME HERE FIRST AND THEN WAIT FO RMY APPROVAL PRIOR TO MAKING A CHANGE THAT COULD BE THOUGHT TO NOT BE FOLLOWING THE GAME SPEC. IF IT IS, YOU ARE GOOD TO GO AHEAD WITHOUT MY APPROVAL.

Your Identity & Boundaries
You are a math engineer, not a game designer.
You do not invent new mechanics unless explicitly asked.
You strictly use the game design document provided.
You think step-by-step, logically and conservatively—never guessing.

Your Output Requirements
Whenever I ask for something:
Check the Space Dummies specification first.
Check the Stake Engine math-sdk documentation second.
Then produce the exact code, file, or configuration required.
Explain reasoning when helpful, but default to concise technical clarity.

Your Guarantee
You will:
Validate that every file is consistent and will compile in the math-sdk.
Consider symbol frequencies, hit rate, bonus frequency, and RTP breakdown.
Suggest adjustments only if math stability requires it.
Ensure the final math package matches Stake Engine standards.

---

**Cursor**

Understood. I’ll treat the Space Dummies specification in `space docs/` as the single source of truth, follow Stake Engine math-sdk standards, and only adjust mechanics when the docs require it. Let me know the first task you’d like me to tackle, and I’ll start by cross-referencing the relevant sections of the spec before touching the math-sdk files.

---

**User**

GAIN A FULL UNDERSTAND BY DELVING DEEP INTO THE DOCUMENTATION FOLDER

---

**Cursor**

## Space Dummies Spec
- 5×4 grid, 20 fixed lines, paying left→right from reel 1; paytable, wild locations, scatter trigger counts, and symbol IDs are fully enumerated for math config alignment.`space docs/GAME_SPEC.md`
- Wild “Gravity Field” only on reels 2–4, carries additive multipliers (×2/×3/×5/×10) and turns sticky inside both Rocket Riot and Hyperdrive Havoc; scatters only trigger features or symbol removal, never pay on their own.`space docs/GAME_SPEC.md`
- Symbol removal hierarchy (10→Space Tape) only occurs during free spins when both reel 1 and reel 5 show scatters; premium Chip/Zog are immune, so reel strips must be dynamically pruned per bonus state without affecting base reels afterward.`space docs/GAME_SPEC.md`
- Rocket Riot (3 scatters or 100× buy) and Hyperdrive Havoc (4 scatters or 200× buy) each start with 10 spins, sticky wilds, +2 spin retriggers, and removal steps; super bonus pre-cleans all lows before the first spin, then removes mids sequentially.`space docs/GAME_SPEC.md`
- Global targets: 96.20 % RTP overall, ~42–45 % base vs ~54–58 % bonus contribution, 0.55 % natural 3-scatter hit rate, very high volatility, 12,500× cap—these guide reel weighting, feature frequency, and optimization constraints.`space docs/GAME_SPEC.md`

```
36:200:space docs/GAME_SPEC.md
2. Reels, Lines, and Layout
...
| Symbol | Type | 5x | 4x | 3x |
| 10 | Low | 2.0 | 0.6 | 0.2 |
...
### 3.3 Wild -- Gravity Field
- Appears on reels 2, 3, and 4 only
- Substitutes for all paying symbols except Scatter
- Each Wild carries a multiplier: ×2, ×3, ×5, or ×10
...
### 4.2 Symbol Removal (Decompression)
...
### 5.1 Rocket Riot Bonus (Regular Bonus)
...
### 5.2 Hyperdrive Havoc Bonus (Super Bonus)
```

## Math-SDK Expectations
- Math outputs must be precomputed “books” plus lookup CSVs referenced from `index.json`; every simulation round needs `id`, `events`, and `payoutMultiplier`, emitted in `.jsonl.zst` for Stake upload, with lookup table rows mirroring the same payout values as unsigned integers.`space docs/MATH_DOCS.md`
- `run.py` orchestrates simulation counts, threading, compression, optimization, and PAR sheet generation; recommended production scale is ≥100k sims per mode with optimization/analysis enabled for reliable RTP shaping before feeding to Stake.`space docs/MATH_DOCS.md`
- Repository layout: reusable logic in `src/` (calculations/config/events/state/wins/write_data), per-game specifics inside `games/<id>/`, with `GameState` coordinating config + output writing; this structure should guide where Space Dummies math code lives and what can be shared vs. bespoke.`space docs/MATH_DOCS.md`

```
24:200:space docs/MATH_DOCS.md
Static File Outputs
...
These outputs are split into two main parts:
1. Game Logic Files
2. CSV Payout Summaries
...
Index file format
{
    "modes": [
        { "name": "base", "cost": 1.0, "events": "books_base.jsonl.zst", "weights": "lookUpTable_base_0.csv" },
        ...
    ]
}
```

## Stake Frontend Alignment
- Frontend SDK uses PixiJS + Svelte with an event-driven `bookEvent` → `emitterEvent` pipeline; `playBookEvents()` processes RGS books sequentially, so math events must be well-ordered and granular (reveal → winInfo → setTotalWin → finalWin, etc.).`space docs/STAKE_DOCS.md`
- Handlers live in `bookEventHandlerMap`, broadcasting synchronous or async emitter events to UI components; complex behaviors should be split into atomic events (e.g., tumble sequences) so future Space Dummies effects (sticky wild placement, symbol removal callouts) stay manageable.`space docs/STAKE_DOCS.md`
- Context system (event emitter, layout, xstate) and Storybook scaffolding dictate how new Space Dummies-specific events (free-spin counters, removal notices, multiplier banners) must be typed, wired, and tested alongside math outputs.`space docs/STAKE_DOCS.md`

```
101:210:space docs/STAKE_DOCS.md
## 5. Book & BookEvent Structure
// base_books.ts - Example of a base game book
{
  id: 1,
  payoutMultiplier: 0.0,
  events: [
    { index: 0, type: 'reveal', board: [...] },
    { index: 1, type: 'setTotalWin', amount: 0 },
    { index: 2, type: 'finalWin', amount: 0 },
  ],
  criteria: '0',
  baseGameWins: 0.0,
  freeGameWins: 0.0,
}
```

## Gaps / Next Steps
- `FRONTEND_HANDOFF.md` was listed but is not in `space docs/`; if it exists elsewhere, let me know so I can ingest it before implementing math-facing events.
- Ready to start translating these rules into `games/0_0_space_dummies/` configs, reelstrips, and feature logic as soon as you direct the next deliverable (e.g., reel math plan, symbol weighting, or bonus state machine).

```plaintext
36:200:space docs/GAME_SPEC.md
2. Reels, Lines, and Layout
...
| Symbol | Type | 5x | 4x | 3x |
| 10 | Low | 2.0 | 0.6 | 0.2 |
...
### 3.3 Wild -- Gravity Field
- Appears on reels 2, 3, and 4 only
- Substitutes for all paying symbols except Scatter
- Each Wild carries a multiplier: ×2, ×3, ×5, or ×10
...
### 4.2 Symbol Removal (Decompression)
...
### 5.1 Rocket Riot Bonus (Regular Bonus)
...
### 5.2 Hyperdrive Havoc Bonus (Super Bonus)
```

```plaintext
24:200:space docs/MATH_DOCS.md
Static File Outputs
...
These outputs are split into two main parts:
1. Game Logic Files
2. CSV Payout Summaries
...
Index file format
{
    "modes": [
        { "name": "base", "cost": 1.0, "events": "books_base.jsonl.zst", "weights": "lookUpTable_base_0.csv" },
        ...
    ]
}
```

```plaintext
101:210:space docs/STAKE_DOCS.md
## 5. Book & BookEvent Structure
// base_books.ts - Example of a base game book
{
  id: 1,
  payoutMultiplier: 0.0,
  events: [
    { index: 0, type: 'reveal', board: [...] },
    { index: 1, type: 'setTotalWin', amount: 0 },
    { index: 2, type: 'finalWin', amount: 0 },
  ],
  criteria: '0',
  baseGameWins: 0.0,
  freeGameWins: 0.0,
}
```

---

**User**

give me a full blueprint of prompts to give you as we go so we can this efficiently and effectively

---

**Cursor**

Here’s a prompt “blueprint” you can reuse or tweak at each stage. They’re sequenced to mirror the full math build so our conversations stay focused and spec-compliant.

### Phase 1 – Baseline Audit
- **“Audit current Space Dummies implementation against GAME_SPEC.md; list gaps and risks.”**
- **“Summarize existing files in `games/0_0_space_dummies/` and map them to the spec requirements.”**

### Phase 2 – Core Config Foundations
- **“Draft paytable + symbol config JSON for Space Dummies per spec §3; confirm in `game_config.py`.”**
- **“Define 20 paylines exactly as in §2; update config and validate formatting.”**

### Phase 3 – Reel Strips & Frequencies
- **“Propose base-game reel strips (IDs, counts) that achieve target hit rate and line distribution.”**
- **“Plan bonus reel-strip variants and symbol-removal handling logic.”**

### Phase 4 – Feature Logic
- **“Implement Rocket Riot free-spin state machine: entry, sticky wild persistence, retrigger, removal.”**
- **“Implement Hyperdrive Havoc with pre-removed lows plus mid-tier removal ladder.”**
- **“Describe book events needed for sticky wild placement, retrigger messaging, and symbol removal notifications.”**

### Phase 5 – RTP & Simulation Tuning
- **“Set up `run.py` arguments: sim counts, threading, modes to hit 96.20% overall.”**
- **“Run dry-run math simulations (or describe how) and report RTP breakdown base vs bonus vs buys.”**
- **“Outline optimization goals/constraints for lookup weights to reach targets.”**

### Phase 6 – Validation & Outputs
- **“Generate PAR-style summary: hit rates, bonus frequency, max win path; confirm vs spec §7.”**
- **“List all files required for Stake upload (`index.json`, lookup tables, books) and their expected contents.”**

### Phase 7 – Frontend Handoff Hooks
- **“Specify book events/emitter events for sticky wilds, free-spin counters, symbol removal cues per STAKE_DOCS.”**
- **“Document integration notes for frontend (event order, payload fields, expected UI responses).”**

### Phase 8 – Final QA / Sign-off
- **“Run final checklist from spec §12; confirm each item passes or note outstanding work.”**
- **“Summarize remaining assumptions/questions for producer approval.”**

Use these verbatim or tweak the scope (“focus on base game only,” “include code snippets,” etc.). Whenever you give one, I’ll cross-check the spec first, then math-sdk docs, then return the exact files/logic needed. Let me know which prompt you want to start with.

---

**User**

Phase 1 – Baseline Audit
“Audit current Space Dummies implementation against GAME_SPEC.md; list gaps and risks.”
“Summarize existing files in games/0_0_space_dummies/ and map them to the spec requirements.”

---

**Cursor**

### Baseline Audit — Gaps & Risks

- **Grid + Paylines mismatch (High):** Spec mandates a 5×4 board with 20 explicitly defined lines.`36:74:space docs/GAME_SPEC.md` Config still uses 5×3 and legacy line paths indexed 0–2, so every board, payline evaluation, and downstream reel file is structurally wrong for Space Dummies.`29:206:games/0_0_space_dummies/game_config.py` Until rows/lines are rebuilt, no simulation can represent the intended math.

- **Paytable & symbol set incorrect (High):** Required bet-multiplier pays for 10–Zog are listed in §3.`81:100:space docs/GAME_SPEC.md` Current paytable keys reference placeholder `L1–H4` symbols plus paying Wild lines, contradicting “wild has no line pays” and the provided payout ladder.`32:63:games/0_0_space_dummies/game_config.py` Reel files likewise use `L*`/`H*` instead of `s10`, `chip`, etc., so every result would mislabel symbols.

- **Wild/scatter behavior off-spec (High):** Spec says wilds only on reels 2–4, multipliers active in base and sticky in bonuses, scatters max at 4.`121:145:space docs/GAME_SPEC.md` Config allows wilds on every reel via strips and only assigns multipliers in free spins; base-game wilds are stuck at ×1 because `assign_mult_property` only rolls multipliers when `gametype == freegame_type`.`208:247:games/0_0_space_dummies/game_config.py``1:27:games/0_0_space_dummies/game_override.py` Reel strips contain full rows of scatters and wilds (see `S,S,S,S,S` and `W,W,W,W,W` rows), so scatter counts, reel restrictions, and multiplier distributions are unbounded.`1:40:games/0_0_space_dummies/reels/BR0.csv``1:40:games/0_0_space_dummies/reels/FR0.csv`

- **Bonus trigger rules incorrect (High):** Rocket Riot should grant 10 spins on 3 scatters, Hyperdrive Havoc 10 spins on 4 scatters with lows removed, +2 retriggers on scatter reels 1+5, and sticky multipliers in both modes.`223:299:space docs/GAME_SPEC.md` Config still uses sample triggers (3→8 spins, 4→12, etc.) and even allows 2-scatter retriggers in free games; Hyperdrive Havoc mode is entirely absent.`211:280:games/0_0_space_dummies/game_config.py` No sticky-wild persistence or symbol-removal routines exist in `gamestate.py`.

- **Symbol removal/decompression missing (High):** Spec’s scatter-on-reels-1-and-5 mechanic and removal hierarchy are core to volatility.`169:203:space docs/GAME_SPEC.md` No code tracks removed tiers, swaps reel strips mid-bonus, or distinguishes Rocket Riot vs Hyperdrive Havoc starting sets; reels folder only contains static BR0/FR0/FRWCAP CSVs.

- **Feature buys & cost structure incomplete (Medium):** Spec lists Bonus Hunt spins (3× bet), Rocket Riot buy (100×), Hyperdrive Havoc buy (200×) with consistent ~96.2 % RTP.`327:339:space docs/GAME_SPEC.md` Config exposes just two BetModes: “base” costing 1× but flagged as `is_feature=True`, and “bonus” costing 100× but pointing to the same reel/multiplier rules; no mode models Bonus Hunt or the 200× super bonus.`282:315:games/0_0_space_dummies/game_config.py`

- **Optimization goals outdated (Medium):** RTP splits need ~42–45 % base vs ~54–58 % bonus with rare triggers.`343:359:space docs/GAME_SPEC.md` Optimization config still targets generic hit rates (e.g., `basegame` HR 3.5, `freegame` HR 200) and doesn’t encode scatter-frequency targets or symbol-removal value ranges, so post-optimization lookup weights will not match spec incentives.`1:120:games/0_0_space_dummies/game_optimization.py`

- **Documentation & developer guidance inaccurate (Low):** `readme.txt` still describes a sample “Lines Games” demo with features (wilds only multiply in free games, 2 scatters retrigger, etc.) that contradict Space Dummies requirements, risking future regression if referenced.`1:22:games/0_0_space_dummies/readme.txt`

- **Executable layer lacks Space Dummies logic (High):** `game_calculations.py` and `game_executables.py` rely on vanilla line evaluation; there’s no hook for sticky wild placement, scatter-state tracking, symbol-removal events, or bonus-mode branching. Without these systems, even correct configs couldn’t produce spec-compliant JSON events.`1:13:games/0_0_space_dummies/game_calculations.py``1:13:games/0_0_space_dummies/game_executables.py`

### File Inventory vs Spec Requirements

| File | Current role | Spec coverage / gap |
| --- | --- | --- |
| `readme.txt` | Sample lines-game overview | Needs replacement with Space Dummies-specific flow (grid, bonuses, removal). |
| `game_config.py` | Defines metadata, paytable, paylines, reels, bet modes | All foundational data diverges from spec (rows, symbol IDs, payouts, line paths, sticky wild settings, bonus triggers, feature buys). Requires full rewrite. |
| `reels/*.csv` | BR0 (base), FR0 (free), FRWCAP (cap) strips | Use wrong symbols, lengths, scatter distributions; no Rocket vs Hyperdrive sets, no removal states. Must be rebuilt per §4–5. |
| `game_calculations.py` | Placeholder subclass of `Executables` | No custom calculations for multipliers, sticky wilds, removal logic—needs extensive implementation. |
| `game_executables.py` | Calls base `Lines` functions | Lacks event emission for sticky wild placement, scatter retriggers, removal notifications required by frontend spec §10/STAKE docs. |
| `game_override.py` | Assigns wild multipliers only in free games, handles repeat logic | Needs base-game multipliers, sticky-state persistence, scatter cap (max 4), removal tracking, and special-symbol routing (wild reels 2–4 only). |
| `gamestate.py` | Runs base/freespin loops | Uses default loops with no symbol removal, no dual bonus modes, no sticky-state management. Must be extended to handle Rocket Riot, Hyperdrive Havoc, retriggers, and feature buys. |
| `game_optimization.py` | Sets generic optimization parameters | Not aligned to target RTP split, trigger rates, or max-win chase; needs new constraints per §7. |
| `run.py` | Standard run harness | Fine structurally, but mode list (`num_sim_args`) lacks Bonus Hunt / Hyperdrive entries and analysis hooks for decompression events. |

**Next step suggestion:** rebuild `game_config.py` + reels to match §2–3, then design state logic for sticky wilds, dual bonuses, and symbol removal before running any math. Let me know which piece you’d like me to tackle first.

---

**User**

1. rebuild game_config.py + reels to match §2–3
2. then design state logic for sticky wilds, dual bonuses, and symbol removal before running any math

---

**Cursor**

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        self.paylines = {
            1: [
                0,
                0,
                0,
                0,
                0,
            ],
            2: [
                1,
                1,
                1,
                1,
                1,
            ],
            3: [
                2,
                2,
                2,
                2,
                2,
            ],
            4: [
                0,
                1,
                2,
                1,
                0,
            ],
            5: [
                2,
                1,
                0,
                1,
                2,
            ],
            6: [
                0,
                0,
                1,
                2,
                2,
            ],
            7: [
                2,
                2,
                1,
                0,
                0,
            ],
            8: [
                1,
                0,
                1,
                2,
                1,
            ],
            9: [
                1,
                2,
                1,
                0,
                1,
            ],
            10: [
                0,
                1,
                1,
                1,
                2,
            ],
            11: [
                2,
                1,
                1,
                1,
                0,
            ],
            12: [
                0,
                1,
                0,
                1,
                2,
            ],
            13: [
                2,
                1,
                2,
                1,
                0,
            ],
            14: [
                1,
                1,
                0,
                1,
                1,
            ],
            15: [
                1,
                1,
                2,
                1,
                1,
            ],
            16: [
                0,
                2,
                1,
                0,
                2,
            ],
            17: [
                2,
                0,
                1,
                2,
                0,
            ],
            18: [
                0,
                0,
                2,
                0,
                0,
            ],
            19: [
                2,
                2,
                0,
                2,
                2,
            ],
            20: [
                1,
                0,
                0,
                0,
                1,
            ],
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "multiplier": ["W"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {2: 3, 3: 5, 4: 8, 5: 12},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        self.padding_symbol_values = {"W": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 50, 4: 20, 5: 5},
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {
                    2: 60,
                    3: 80,
                    4: 50,
                    5: 20,
                    10: 15,
                    20: 10,
                    50: 5,
                },
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: {1: 1}},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 60, 10: 100, 20: 90, 50: 50},
            },
            "scatter_triggers": {4: 1, 5: 2},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1},
            },
            "force_wincap": False,
            "force_freegame": False,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                ],
            ),
        ]

```

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "multiplier": ["W"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {2: 3, 3: 5, 4: 8, 5: 12},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        self.padding_symbol_values = {"W": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 50, 4: 20, 5: 5},
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {
                    2: 60,
                    3: 80,
                    4: 50,
                    5: 20,
                    10: 15,
                    20: 10,
                    50: 5,
                },
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: {1: 1}},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 60, 10: 100, 20: 90, 50: 50},
            },
            "scatter_triggers": {4: 1, 5: 2},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1},
            },
            "force_wincap": False,
            "force_freegame": False,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                ],
            ),
        ]

```

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["wild"], "scatter": ["scatter"], "multiplier": ["wild"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            # In bonus modes, retriggers are granted via the scatter-on-reels-1-and-5 rule.
            # This placeholder entry allows anticipation logic to function; the actual positional
            # checks are handled in the game-state layer.
            self.freegame_type: {2: 2},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        wild_multiplier_weights = {2: 45, 3: 30, 5: 20, 10: 5}
        self.padding_symbol_values = {"wild": {"multiplier": wild_multiplier_weights}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 50, 4: 20, 5: 5},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: wild_multiplier_weights},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "scatter_triggers": {4: 1},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": False,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                ],
            ),
        ]

```

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["wild"], "scatter": ["scatter"], "multiplier": ["wild"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            # In bonus modes, retriggers are granted via the scatter-on-reels-1-and-5 rule.
            # This placeholder entry allows anticipation logic to function; the actual positional
            # checks are handled in the game-state layer.
            self.freegame_type: {2: 2},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        wild_multiplier_weights = {2: 45, 3: 30, 5: 20, 10: 5}
        self.padding_symbol_values = {"wild": {"multiplier": wild_multiplier_weights}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 80, 4: 20},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: wild_multiplier_weights},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "scatter_triggers": {4: 1},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": False,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                ],
            ),
        ]

```

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.all_valid_sym_names = set()
        for symbol_group in self.symbol_ids.values():
            self.all_valid_sym_names.update(symbol_group)
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["wild"], "scatter": ["scatter"], "multiplier": ["wild"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            # In bonus modes, retriggers are granted via the scatter-on-reels-1-and-5 rule.
            # This placeholder entry allows anticipation logic to function; the actual positional
            # checks are handled in the game-state layer.
            self.freegame_type: {2: 2},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        wild_multiplier_weights = {2: 45, 3: 30, 5: 20, 10: 5}
        self.padding_symbol_values = {"wild": {"multiplier": wild_multiplier_weights}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 80, 4: 20},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: wild_multiplier_weights},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "scatter_triggers": {4: 1},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": False,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                ],
            ),
        ]

```

```python
import random
from copy import deepcopy

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import fs_trigger_event, reveal_event


class GameStateOverride(GameExecutables):
    """
    Extend the base gamestate with Space Dummies-specific overrides:
    - Wild multipliers in all modes
    - Sticky wild tracking during bonuses
    - Dual bonus modes with symbol removal handling
    """

    def reset_book(self):
        super().reset_book()
        self.pending_bonus_mode = None
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "wild": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in all modes."""
        multiplier_value = 1
        mult_config = self.get_current_distribution_conditions().get("mult_values", {})
        if self.gametype in mult_config:
            multiplier_value = get_random_outcome(mult_config[self.gametype])
        symbol.assign_attribute({"multiplier": multiplier_value})

    # --- Bonus session helpers -------------------------------------------------

    def initialize_bonus_session(self):
        """Create local reel copies, removal state, and sticky storage."""
        if self.pending_bonus_mode is None:
            raise RuntimeError("Bonus mode not set before initializing free spins.")
        self.active_bonus_mode = self.pending_bonus_mode
        self.pending_bonus_mode = None
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.config.freegame_type]
        self.bonus_reel_maps = {
            reel_id: [list(column) for column in self.config.reels[reel_id]] for reel_id in freegame_reel_weights.keys()
        }

        if self.active_bonus_mode == "hyper":
            for symbol_name in self.config.symbol_ids["low"]:
                self._remove_symbol_from_bonus_reels(symbol_name)
            self.next_symbol_removal_index = len(self.config.symbol_ids["low"])

    def clear_bonus_session(self):
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def _remove_symbol_from_bonus_reels(self, symbol_name: str) -> bool:
        """Remove a symbol from all bonus reel copies; returns True if anything changed."""
        removed_any = False
        for reel_id in self.bonus_reel_maps:
            for reel_index, reel_strip in enumerate(self.bonus_reel_maps[reel_id]):
                filtered_strip = [sym for sym in reel_strip if sym != symbol_name]
                if len(filtered_strip) != len(reel_strip):
                    removed_any = True
                    self.bonus_reel_maps[reel_id][reel_index] = filtered_strip
                if len(self.bonus_reel_maps[reel_id][reel_index]) == 0:
                    raise RuntimeError(f"Symbol removal '{symbol_name}' exhausted reel {reel_index} in {reel_id}.")
        if removed_any:
            self.removed_symbols.add(symbol_name)
        return removed_any

    def remove_next_symbol_in_queue(self) -> str | None:
        """Remove the next symbol in the configured hierarchy."""
        if self.next_symbol_removal_index >= len(self.config.symbol_removal_order):
            return None
        target_symbol = self.config.symbol_removal_order[self.next_symbol_removal_index]
        self.next_symbol_removal_index += 1
        if target_symbol in self.removed_symbols:
            return target_symbol
        removed = self._remove_symbol_from_bonus_reels(target_symbol)
        if removed:
            return target_symbol
        return target_symbol

    def draw_bonus_board(self, emit_event: bool = True):
        """Create a board using the mutable bonus reelstrips."""
        if not self.bonus_reel_maps:
            raise RuntimeError("Bonus reel strips not initialized.")

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.gametype]
        reelstrip_id = get_random_outcome(freegame_reel_weights)
        reelstrip = self.bonus_reel_maps[reelstrip_id]

        self.refresh_special_syms()
        anticipation = [0] * self.config.num_reels
        board = [[]] * self.config.num_reels
        if self.config.include_padding:
            top_symbols = []
            bottom_symbols = []
        reel_positions = [0] * self.config.num_reels
        padding_positions = [0] * self.config.num_reels
        first_scatter_reel = -1

        for reel in range(self.config.num_reels):
            if len(reelstrip[reel]) == 0:
                raise RuntimeError(f"Reel {reel} for strip {reelstrip_id} is empty after symbol removal.")
            board[reel] = [None] * self.config.num_rows[reel]
            reel_pos = random.randrange(0, len(reelstrip[reel]))
            reel_positions[reel] = reel_pos
            if self.config.include_padding:
                top_symbols.append(self.create_symbol(reelstrip[reel][(reel_pos - 1) % len(reelstrip[reel])]))
                bottom_symbols.append(
                    self.create_symbol(reelstrip[reel][(reel_pos + len(board[reel])) % len(reelstrip[reel])])
                )
            for row in range(self.config.num_rows[reel]):
                sym_id = reelstrip[reel][(reel_pos + row) % len(reelstrip[reel])]
                symbol = self.create_symbol(sym_id)
                board[reel][row] = symbol
                if symbol.special:
                    for special_symbol in self.special_syms_on_board:
                        for s in self.config.special_symbols[special_symbol]:
                            if symbol.name == s:
                                self.special_syms_on_board[special_symbol].append({"reel": reel, "row": row})
                                if (
                                    symbol.check_attribute("scatter")
                                    and len(self.special_syms_on_board[special_symbol])
                                    >= self.config.anticipation_triggers[self.gametype]
                                    and first_scatter_reel == -1
                                ):
                                    first_scatter_reel = reel + 1
            padding_positions[reel] = (reel_positions[reel] + len(board[reel]) + 1) % len(reelstrip[reel])

        if first_scatter_reel > -1 and first_scatter_reel != self.config.num_reels:
            count = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1

        self.board = board
        self.reel_positions = reel_positions
        self.padding_position = padding_positions
        self.anticipation = anticipation
        self.reelstrip_id = reelstrip_id
        self.reelstrip = reelstrip
        if self.config.include_padding:
            self.top_symbols = top_symbols
            self.bottom_symbols = bottom_symbols

        if emit_event:
            reveal_event(self)

    def apply_existing_sticky_wilds(self):
        """Overlay previously stored sticky wilds onto the active board."""
        if not self.sticky_wild_positions:
            self.get_special_symbols_on_board()
            return

        for (reel, row), multiplier in self.sticky_wild_positions.items():
            sticky_symbol = self.create_symbol("wild")
            sticky_symbol.assign_attribute({"multiplier": multiplier})
            self.board[reel][row] = sticky_symbol
        self.get_special_symbols_on_board()

    def capture_new_sticky_wilds(self) -> list:
        """Record any new wilds that landed this spin so they persist."""
        new_wilds = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                symbol = self.board[reel][row]
                if symbol.name != "wild":
                    continue
                key = (reel, row)
                if key in self.sticky_wild_positions:
                    continue
                multiplier = symbol.get_attribute("multiplier") if symbol.check_attribute("multiplier") else 1
                self.sticky_wild_positions[key] = multiplier
                new_wilds.append({"reel": reel, "row": row, "multiplier": multiplier})
        return new_wilds

    def process_edge_scatter_removal(self) -> str | None:
        """Check for Scatter on reels 1 and 5, award spins and remove symbols if needed."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        has_left = any(pos["reel"] == 0 for pos in scatter_positions)
        has_right = any(pos["reel"] == self.config.num_reels - 1 for pos in scatter_positions)
        if not (has_left and has_right):
            return None

        # +2 free spins per spec
        self.tot_fs += 2
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
        return self.remove_next_symbol_in_queue()

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

```

```python
import random
from copy import deepcopy
from typing import Optional

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import fs_trigger_event, reveal_event


class GameStateOverride(GameExecutables):
    """
    Extend the base gamestate with Space Dummies-specific overrides:
    - Wild multipliers in all modes
    - Sticky wild tracking during bonuses
    - Dual bonus modes with symbol removal handling
    """

    def reset_book(self):
        super().reset_book()
        self.pending_bonus_mode = None
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "wild": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in all modes."""
        multiplier_value = 1
        mult_config = self.get_current_distribution_conditions().get("mult_values", {})
        if self.gametype in mult_config:
            multiplier_value = get_random_outcome(mult_config[self.gametype])
        symbol.assign_attribute({"multiplier": multiplier_value})

    # --- Bonus session helpers -------------------------------------------------

    def initialize_bonus_session(self):
        """Create local reel copies, removal state, and sticky storage."""
        if self.pending_bonus_mode is None:
            raise RuntimeError("Bonus mode not set before initializing free spins.")
        self.active_bonus_mode = self.pending_bonus_mode
        self.pending_bonus_mode = None
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.config.freegame_type]
        self.bonus_reel_maps = {
            reel_id: deepcopy(self.config.reels[reel_id]) for reel_id in freegame_reel_weights.keys()
        }

        if self.active_bonus_mode == "hyper":
            for symbol_name in self.config.symbol_ids["low"]:
                self._remove_symbol_from_bonus_reels(symbol_name)
            self.next_symbol_removal_index = len(self.config.symbol_ids["low"])

    def clear_bonus_session(self):
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def _remove_symbol_from_bonus_reels(self, symbol_name: str) -> bool:
        """Remove a symbol from all bonus reel copies; returns True if anything changed."""
        removed_any = False
        for reel_id in self.bonus_reel_maps:
            for reel_index, reel_strip in enumerate(self.bonus_reel_maps[reel_id]):
                filtered_strip = [sym for sym in reel_strip if sym != symbol_name]
                if len(filtered_strip) != len(reel_strip):
                    removed_any = True
                    self.bonus_reel_maps[reel_id][reel_index] = filtered_strip
                if len(self.bonus_reel_maps[reel_id][reel_index]) == 0:
                    raise RuntimeError(f"Symbol removal '{symbol_name}' exhausted reel {reel_index} in {reel_id}.")
        if removed_any:
            self.removed_symbols.add(symbol_name)
        return removed_any

    def remove_next_symbol_in_queue(self) -> Optional[str]:
        """Remove the next symbol in the configured hierarchy."""
        if self.next_symbol_removal_index >= len(self.config.symbol_removal_order):
            return None
        target_symbol = self.config.symbol_removal_order[self.next_symbol_removal_index]
        self.next_symbol_removal_index += 1
        if target_symbol in self.removed_symbols:
            return target_symbol
        removed = self._remove_symbol_from_bonus_reels(target_symbol)
        if removed:
            return target_symbol
        return target_symbol

    def draw_bonus_board(self, emit_event: bool = True):
        """Create a board using the mutable bonus reelstrips."""
        if not self.bonus_reel_maps:
            raise RuntimeError("Bonus reel strips not initialized.")

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.gametype]
        reelstrip_id = get_random_outcome(freegame_reel_weights)
        reelstrip = self.bonus_reel_maps[reelstrip_id]

        self.refresh_special_syms()
        anticipation = [0] * self.config.num_reels
        board = [[]] * self.config.num_reels
        if self.config.include_padding:
            top_symbols = []
            bottom_symbols = []
        reel_positions = [0] * self.config.num_reels
        padding_positions = [0] * self.config.num_reels
        first_scatter_reel = -1

        for reel in range(self.config.num_reels):
            if len(reelstrip[reel]) == 0:
                raise RuntimeError(f"Reel {reel} for strip {reelstrip_id} is empty after symbol removal.")
            board[reel] = [None] * self.config.num_rows[reel]
            reel_pos = random.randrange(0, len(reelstrip[reel]))
            reel_positions[reel] = reel_pos
            if self.config.include_padding:
                top_symbols.append(self.create_symbol(reelstrip[reel][(reel_pos - 1) % len(reelstrip[reel])]))
                bottom_symbols.append(
                    self.create_symbol(reelstrip[reel][(reel_pos + len(board[reel])) % len(reelstrip[reel])])
                )
            for row in range(self.config.num_rows[reel]):
                sym_id = reelstrip[reel][(reel_pos + row) % len(reelstrip[reel])]
                symbol = self.create_symbol(sym_id)
                board[reel][row] = symbol
                if symbol.special:
                    for special_symbol in self.special_syms_on_board:
                        for s in self.config.special_symbols[special_symbol]:
                            if symbol.name == s:
                                self.special_syms_on_board[special_symbol].append({"reel": reel, "row": row})
                                if (
                                    symbol.check_attribute("scatter")
                                    and len(self.special_syms_on_board[special_symbol])
                                    >= self.config.anticipation_triggers[self.gametype]
                                    and first_scatter_reel == -1
                                ):
                                    first_scatter_reel = reel + 1
            padding_positions[reel] = (reel_positions[reel] + len(board[reel]) + 1) % len(reelstrip[reel])

        if first_scatter_reel > -1 and first_scatter_reel != self.config.num_reels:
            count = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1

        self.board = board
        self.reel_positions = reel_positions
        self.padding_position = padding_positions
        self.anticipation = anticipation
        self.reelstrip_id = reelstrip_id
        self.reelstrip = reelstrip
        if self.config.include_padding:
            self.top_symbols = top_symbols
            self.bottom_symbols = bottom_symbols

        if emit_event:
            reveal_event(self)

    def apply_existing_sticky_wilds(self):
        """Overlay previously stored sticky wilds onto the active board."""
        if not self.sticky_wild_positions:
            self.get_special_symbols_on_board()
            return

        for (reel, row), multiplier in self.sticky_wild_positions.items():
            sticky_symbol = self.create_symbol("wild")
            sticky_symbol.assign_attribute({"multiplier": multiplier})
            self.board[reel][row] = sticky_symbol
        self.get_special_symbols_on_board()

    def capture_new_sticky_wilds(self) -> list:
        """Record any new wilds that landed this spin so they persist."""
        new_wilds = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                symbol = self.board[reel][row]
                if symbol.name != "wild":
                    continue
                key = (reel, row)
                if key in self.sticky_wild_positions:
                    continue
                multiplier = symbol.get_attribute("multiplier") if symbol.check_attribute("multiplier") else 1
                self.sticky_wild_positions[key] = multiplier
                new_wilds.append({"reel": reel, "row": row, "multiplier": multiplier})
        return new_wilds

    def process_edge_scatter_removal(self) -> Optional[str]:
        """Check for Scatter on reels 1 and 5, award spins and remove symbols if needed."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        has_left = any(pos["reel"] == 0 for pos in scatter_positions)
        has_right = any(pos["reel"] == self.config.num_reels - 1 for pos in scatter_positions)
        if not (has_left and has_right):
            return None

        # +2 free spins per spec
        self.tot_fs += 2
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
        return self.remove_next_symbol_in_queue()

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

```

```python
from game_override import GameStateOverride
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                scatter_total = self.count_special_symbols("scatter")
                self.pending_bonus_mode = "hyper" if scatter_total >= 4 else "rocket"
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        self.initialize_bonus_session()
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_bonus_board(emit_event=False)
            self.apply_existing_sticky_wilds()
            self.capture_new_sticky_wilds()
            reveal_event(self)

            self.evaluate_lines_board()
            self.process_edge_scatter_removal()

            self.win_manager.update_gametype_wins(self.gametype)

        self.clear_bonus_session()
        self.end_freespin()

```

```python
from game_override import GameStateOverride
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                scatter_total = self.count_special_symbols("scatter")
                self.pending_bonus_mode = "hyper" if scatter_total >= 4 else "rocket"
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        self.initialize_bonus_session()
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_bonus_board(emit_event=False)
            self.apply_existing_sticky_wilds()
            self.capture_new_sticky_wilds()
            reveal_event(self)

            self.evaluate_lines_board()
            removed_symbol = self.process_edge_scatter_removal()
            if removed_symbol is not None:
                self.record({"event": "symbolRemoval", "symbol": removed_symbol, "mode": self.active_bonus_mode})

            self.win_manager.update_gametype_wins(self.gametype)

        self.clear_bonus_session()
        self.end_freespin()

```

## Summary
- Brought `game_config.py` in line with §§2–3: set the 5×4 layout, redefined symbol IDs, encoded the spec paytable, symbol-removal ladder, free-spin trigger table, and limited scatter counts/multiplier weights so both base and bonus draws use the same x2/x3/x5/x10 distribution (`wild` now exists only on reels 2–4).`18:165:games/0_0_space_dummies/game_config.py`
- Regenerated all reel strips to use the new IDs, capped simultaneous scatters at four, and forced `wild` entries to columns 2–4 so base boards can no longer produce illegal positions or symbol names.`1:12:games/0_0_space_dummies/reels/BR0.csv`
- Implemented the Rocket vs Hyper bonus framework: wild multipliers now roll in every mode, sticky wild state persists across free spins, Hyperdrive launches without lows, and Scatter-on-reels-1&5 awards +2 spins plus the next removal in the hierarchy—all using per-bonus reel copies so symbol removal doesn’t mutate the shared config. A lightweight record entry captures each removal for later analytics.`18:205:games/0_0_space_dummies/game_override.py``8:45:games/0_0_space_dummies/gamestate.py`

## Tests
- Not run (not requested).

## Next Steps
- Wire dedicated Bonus Hunt / Hyperdrive buy modes once the math targets for those costs are confirmed.
- Emit explicit frontend events for sticky-wild placement and symbol-removal milestones so the Pixi/Svelte client can animate them per STAKE docs.
- Tune distribution quotas/forces after initial simulation runs to verify RTP split, scatter frequencies, and the new removal logic’s impact.

---

**User**

Wire dedicated Bonus Hunt / Rocket / Hyperdrive buy modes once the math targets for those costs are confirmed. Let's get started on this

---

**Cursor**

```python
"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.all_valid_sym_names = set()
        for symbol_group in self.symbol_ids.values():
            self.all_valid_sym_names.update(symbol_group)
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["wild"], "scatter": ["scatter"], "multiplier": ["wild"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            # In bonus modes, retriggers are granted via the scatter-on-reels-1-and-5 rule.
            # This placeholder entry allows anticipation logic to function; the actual positional
            # checks are handled in the game-state layer.
            self.freegame_type: {2: 2},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        wild_multiplier_weights = {2: 45, 3: 30, 5: 20, 10: 5}
        self.padding_symbol_values = {"wild": {"multiplier": wild_multiplier_weights}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 80, 4: 20},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: wild_multiplier_weights},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "scatter_triggers": {4: 1},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": False,
        }

        rocket_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 1},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        hyper_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {4: 1},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus_hunt",
                cost=3.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.25, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.25, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.499, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="rocket_buy",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="rocket_entry", quota=0.999, conditions=rocket_buy_condition),
                ],
            ),
            BetMode(
                name="hyper_buy",
                cost=200.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="hyper_entry", quota=0.999, conditions=hyper_buy_condition),
                ],
            ),
        ]

```

## Bonus Modes Wired In
- Added new bet modes in `game_config.py` matching spec pricing: `bonus_hunt` (3× enhanced spins), `rocket_buy` (100× direct Rocket Riot), and `hyper_buy` (200× Hyperdrive). Each mode now carries bespoke distribution mixes so bonus hunt triples the free-spin quota, while the buys always enter their respective features.`166:206:games/0_0_space_dummies/game_config.py`
- Created dedicated forcing conditions: rocket buys guarantee a 3-scatter entry and hyper buys force 4 scatters, both sharing the same BR0/FR0 reel pools and wild-multiplier weights so their subsequent free spins run through the same sticky-wild + removal logic as the base game.`122:165:games/0_0_space_dummies/game_config.py`

## Notes / Next Steps
- With the new bet modes, you can now simulate/sculpt RTP per purchase type; next step is to run mode-specific sims to dial the quotas so Bonus Hunt actually lands ~3× more free spins in the final optimized lookup.
- Frontend config should be updated to expose the new mode names/costs so the client can show the Bonus Hunt toggle and both buy buttons.

Let me know when you’re ready to tune the quotas/RTP targets or need help exposing these modes to the frontend.

---

**User**

Frontend config should be updated to expose the new mode names/costs so the client can show the Bonus Hunt toggle and both buy buttons.

I need you to make a markdown md with all the info to give to my frontend dev and he'll do it all

---

**Cursor**

```markdown
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

```

## Frontend Handoff Doc Added
- Created `games/0_0_space_dummies/frontend_handoff.md`, a concise guide you can drop directly to the frontend team. It maps every exposed math mode (`base`, `bonus_hunt`, `rocket_buy`, `hyper_buy`) to UI labels, costs, and entry states, and outlines the toggle/button plan so Bonus Hunt and the two buys show up correctly.
- The doc also lists the frontend config touchpoints (mode registry, bet bar wiring, Storybook coverage) plus the event hooks they should anticipate for sticky wilds and symbol-removal messaging.

Let me know if you want me to expand it with specific code snippets or Storybook wiring once the frontend dev reviews it.

---

**User**

With the new bet modes, you can now simulate/sculpt RTP per purchase type; next step is to run mode-specific sims to dial the quotas so Bonus Hunt actually lands ~3× more free spins in the final optimized lookup.

ok whaat do we do here now

---

**Cursor**

Here’s how to move forward now that the new modes exist:

## Immediate Plan
- **Run mode-specific sim batches**: in `games/0_0_space_dummies/run.py`, adjust `num_sim_args` to cover the new modes individually (e.g., `{"base": 1e4, "bonus_hunt": 1e4, "rocket_buy": 1e4, "hyper_buy": 1e4}`) and set `target_modes` accordingly. That lets us inspect raw hit rates/RTP per mode before optimization adjusts weights.
- **Check raw outputs**: after `make run GAME=0_0_space_dummies`, use the generated `library/lookup_tables/lookUpTableSegmented_<mode>.csv` or the stat sheet from `run_analysis` to compare:
  - Bonus hunt scatter frequency vs. base (should be ≈3× higher).
  - Rocket/hyper RTP vs. their 100×/200× costs.
  - Sticky wild density in both bonuses.
- **Tweak distribution quotas**: if bonus hunt isn’t delivering the expected hit rate, bump its `Distribution(criteria="freegame", quota=...)` inside `game_config.py` until the stat sheet shows the desired frequency. Same idea for buys if their RTP deviates from 96.2%.
- **Iterate + optimize**: once raw sims look good, rerun with `run_optimization=True` so the lookup weights are balanced per mode. Re-check the printed RTP breakdown to confirm base ≈42–45% and the rest in bonus/buys.

I can run those sims or help interpret the outputs if you want; just let me know whether to kick off the first batch or to adjust the quotas first.

---

**User**

you take the wheel, go ahead

---

**Cursor**

```python
"""Main file for generating results for sample lines-pay game."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 10
    rust_threads = 20
    batching_size = 5000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e4),
        "bonus_hunt": int(1e4),
        "rocket_buy": int(1e4),
        "hyper_buy": int(1e4),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = list(num_sim_args.keys())

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)

```

---

**User**

if you are having trouble running things which might be the case here, you can give me the stuff to run and i'll tell uuwhat happens

---

**Cursor**

Makes sense. The math SDK expects the repo root (`math-sdk/`) on `PYTHONPATH`; when we run the game script directly, Python can’t find the top-level `src/` package and bails.

Could you try this from the repo root (`C:\Users\Anthony\Desktop\UNKNOWN\math-sdk`), in PowerShell?

```
$Env:PYTHONPATH="."
python games\0_0_space_dummies\run.py
```

That temporary env var should let the script resolve `src.*` imports. Let me know what it prints (or if it errors again), and I’ll take it from there.

```plaintext
$Env:PYTHONPATH="."
python games\0_0_space_dummies\run.py
```

---

**User**

stake engine docs tel me to do make setup then make run  GAME=0_0_space_dummies can i do that instead

---

**Cursor**

Yep, that’s the canonical flow:

1. From repo root, run `make setup` once to install/build all math-sdk dependencies.
2. Then run `make run GAME=0_0_space_dummies`.

The make target handles the right `PYTHONPATH`, venv, and parallelism, so it’s safer than calling the script directly. Go ahead with that—share the console output when it finishes (or errors) and I’ll interpret the stats/logs.

```python
"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """"""

    def __init__(self, game_config):
        self.game_config = game_config
        base_scaling = ConstructScaling(
            [
                {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                {"criteria": "basegame", "scale_factor": 1.5, "win_range": (10, 20), "probability": 1.0},
                {
                    "criteria": "freegame",
                    "scale_factor": 0.8,
                    "win_range": (1000, 2000),
                    "probability": 1.0,
                },
                {
                    "criteria": "freegame",
                    "scale_factor": 1.2,
                    "win_range": (3000, 4000),
                    "probability": 1.0,
                },
            ]
        ).return_dict()

        base_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
        ).return_dict()

        bonus_scaling = ConstructScaling(
            [
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (1, 20), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.5, "win_range": (20, 50), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.8, "win_range": (50, 100), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.8, "win_range": (1000, 2000), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (3000, 4000), "probability": 1.0},
            ]
        ).return_dict()

        bonus_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
        ).return_dict()

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.002, av_win=5000, search_conditions=5000).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.54, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.2, rtp=0.42).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(2.0, 3.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "bonus_hunt": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.002, av_win=5000, search_conditions=5000).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.74, hr=150, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.5, rtp=0.22).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(1.5, 2.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "rocket_buy": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.002, av_win=5000, search_conditions=5000).return_dict(),
                    "rocket_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["rocket_entry"],
                    bias_ranges=[(200.0, 350.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
            "hyper_buy": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.002, av_win=5000, search_conditions=5000).return_dict(),
                    "hyper_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["hyper_entry"],
                    bias_ranges=[(250.0, 400.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)

```

Updated `game_optimization.py` so every bet mode (base, bonus_hunt, rocket_buy, hyper_buy) now has matching optimization conditions whose RTP totals sum to the mode’s 96.20 % target. That clears the assertion Stake’s optimizer was throwing.

Please re-run the math pipeline:

```
make run GAME=0_0_space_dummies
```

It’ll walk through sims → optimization → analysis with the new bet-mode list. Share the console summary (or any new errors) and I’ll dig into the RTP outputs next.

```plaintext
make run GAME=0_0_space_dummies
```

The Rust optimizer crashed when `cargo run --release` was invoked (exit code 101), but make didn’t show the underlying Rust error. Could you grab that for me?

From repo root:

```
cd optimization_program
cargo run --release
```

Share the full stdout/stderr it prints. Once we see the actual Rust panic/message we can address it (e.g., missing toolchain deps vs. a config mismatch).

```plaintext
cd optimization_program
cargo run --release
```

```python
"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """"""

    def __init__(self, game_config):
        self.game_config = game_config
        base_scaling = ConstructScaling(
            [
                {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                {"criteria": "basegame", "scale_factor": 1.5, "win_range": (10, 20), "probability": 1.0},
                {
                    "criteria": "freegame",
                    "scale_factor": 0.8,
                    "win_range": (1000, 2000),
                    "probability": 1.0,
                },
                {
                    "criteria": "freegame",
                    "scale_factor": 1.2,
                    "win_range": (3000, 4000),
                    "probability": 1.0,
                },
            ]
        ).return_dict()

        base_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
        ).return_dict()

        bonus_scaling = ConstructScaling(
            [
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (1, 20), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.5, "win_range": (20, 50), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.8, "win_range": (50, 100), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.8, "win_range": (1000, 2000), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (3000, 4000), "probability": 1.0},
            ]
        ).return_dict()

        bonus_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
        ).return_dict()

        wincap_win = self.game_config.wincap

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.54, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.2, rtp=0.42).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(2.0, 3.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "bonus_hunt": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.74, hr=150, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.5, rtp=0.22).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(1.5, 2.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "rocket_buy": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "rocket_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["rocket_entry"],
                    bias_ranges=[(200.0, 350.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
            "hyper_buy": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "hyper_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["hyper_entry"],
                    bias_ranges=[(250.0, 400.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)

```

The optimizer panic was because it tried to target a wincap payout of 5,000, but our actual max win is 12,500. I’ve updated `game_optimization.py` so every bet mode’s `wincap` condition now uses `av_win = search = 12,500`, matching the books we just generated.

Please re-run the math pipeline:

```
make run GAME=0_0_space_dummies
```

It should get past the optimization step now. Once it finishes (or if anything else pops up), send me the output and I’ll review the RTP stats.

```plaintext
make run GAME=0_0_space_dummies
```

Great—math pass completed for all four modes, and the Rust optimizer + PAR sheet generation finished cleanly. You now have fresh books/LUTs in `games/0_0_space_dummies/library/` plus the updated `lookUpTableSegmented_<mode>.csv` and stat-sheet CSVs under `games/0_0_space_dummies/library/analysis/`.

### What to do now
- **Review hit rates / RTP per mode:** open `library/analysis/analysis_base.csv`, `analysis_bonus_hunt.csv`, etc. to confirm the base vs free-spin contribution matches the targets (Bonus Hunt scatters should be roughly 3× the base frequency, buys should sit near 96.2 % once weighted by their costs).
- **Adjust distribution quotas if needed:** if, for example, Bonus Hunt only doubles the free-spin frequency, bump the `Distribution(... quota=...)` values in `game_config.py` and rerun.
- **Check lookup weights:** optimization wrote `lookUpTable_<mode>_0.csv`; inspect the weighted RTP (third column × probability) to ensure each mode is balancing to 0.962. If one is off, tweak the optimization conditions or rerun with more sims.

Let me know which stats you want me to dig into first (e.g., Bonus Hunt free-spin rate, buy-mode RTP), and I’ll pull them from the generated analysis files.

