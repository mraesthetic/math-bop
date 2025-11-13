Space Dummies -- Game Design Document
====================================

**Developer:** Shift Gaming\
**Engine:** Stake Engine\
**Grid:** 5×4\
**Paylines:** 20 (fixed)\
**Volatility:** High\
**RTP Target (overall):** 96.20%\
**Max Win:** 12,500× bet

* * * * *

0\. Project Meta
----------------

-   **Game ID:** space_dummies

-   **Internal Name:** ShiftGaming.SpaceDummies

* * * * *

1\. Theme & Overview
--------------------

Space Dummies is a high-volatility, cartoon sci-fi slot featuring two incompetent space explorers:

-   **Chip** -- human engineer astronaut

-   **Zog** -- alien sidekick

Players spin through an asteroid belt, collecting wins from premium character symbols, sticky Wild "gravity fields," and a symbol removal mechanic that progressively upgrades the reel set during bonus rounds.

* * * * *

2\. Reels, Lines, and Layout
----------------------------

-   **Reel grid:** 5 reels × 4 rows

-   **Paylines:** 20 fixed, standard left-to-right evaluation

-   **Bet options:** Defined by Stake Engine config via RGS

-   **Win direction:** Left to right, starting from reel 1

-   **Win calculation:** Sum of all line wins per spin

**Paylines:**

{
  "paylines": [
    [2,2,2,2,2],
    [1,1,1,1,1],
    [3,3,3,3,3],
    [4,4,4,4,4],
    [1,2,3,2,1],
    [4,3,2,3,4],
    [1,2,1,2,1],
    [4,3,4,3,4],
    [2,1,2,3,2],
    [3,4,3,2,3],
    [1,1,2,3,4],
    [4,4,3,2,1],
    [2,3,4,3,2],
    [3,2,1,2,3],
    [1,2,3,4,4],
    [4,3,2,1,1],
    [2,3,2,1,2],
    [3,2,3,4,3],
    [1,1,2,2,3],
    [4,4,3,3,2]
  ]
}

* * * * *

3\. Symbols
-----------

### 3.1 Symbol List and Payouts

All payouts are **multiples of the total bet**.

| Symbol | Type | 5x | 4x | 3x |
| --- | --- | --- | --- | --- |
| 10 | Low | 2.0 | 0.6 | 0.2 |
| J | Low | 2.4 | 0.8 | 0.2 |
| Q | Low | 3.0 | 1.0 | 0.2 |
| K | Low | 4.0 | 1.4 | 0.4 |
| A | Low | 5.0 | 2.0 | 0.4 |
| Cosmic Fizz | Mid | 6.0 | 3.0 | 1.0 |
| Zero-G Donut | Mid | 8.0 | 4.0 | 1.2 |
| Space Tape | Mid | 10.0 | 5.0 | 1.4 |
| Chip | Premium | 40.0 | 15.0 | 3.0 |
| Zog | Premium | 100.0 | 20.0 | 4.0 |
| Wild | Feature | --- | --- | --- |
| Scatter | Feature | --- | --- | --- |

> Note: Wild and Scatter do not have their own line pays; Wild substitutes and Scatter triggers features only.

### 3.2 Symbol IDs (for reelstrips.json)

| Symbol | ID |
| --- | --- |
| 10 | s10 |
| J | sj |
| Q | sq |
| K | sk |
| A | sa |
| Cosmic Fizz | sc1 |
| Zero-G Donut | sc2 |
| Space Tape | sc3 |
| Chip | chip |
| Zog | zog |
| Wild | wild |
| Scatter | scatter |

### 3.3 Wild -- Gravity Field

-   Appears on reels **2, 3, and 4 only** (base game and bonuses).

-   Substitutes for **all paying symbols** (Low, Mid, Premium) except **Scatter**.

-   Each Wild carries a multiplier: **×2, ×3, ×5, or ×10**.

-   If multiple Wilds are part of a winning line, their multipliers **add together** and are then applied to the line's base payout:

    -   Example: line win = 4.0×, wilds = ×2 and ×3 → total multiplier = ×5 → final win = 20.0×.

**Base game:** Wilds are non-sticky.\
**Bonuses:** Wilds become sticky (see section 5).

### 3.4 Scatter -- Bonus Pod

-   Appears on all reels.

-   **3 Scatters** trigger the regular bonus (Rocket Riot).

-   **4 Scatters** trigger the super bonus (Hyperdrive Havoc).

-   Scatter symbols do **not** have standalone pays (trigger only).

-   The maximum amount of scatters that can land on the board is 4. 5 Scatters CANNOT land.

* * * * *

4\. Core Mechanics
------------------

### 4.1 Base Game

-   5×4, 20-line fixed slot.

-   Wild multipliers can land on reels **2--4**, non-sticky.

-   Evaluation per spin:

    1.  All 20 lines are checked left→right from reel 1.

    2.  For each line, determine the best win (highest paying symbol combination).

    3.  If one or more Wilds are on the winning line, sum their multipliers to get the **line multiplier**.

    4.  Line win = base payout × summed Wild multiplier (or ×1 if no Wilds).

    5.  **Total spin win** = sum of all line wins.

### 4.2 Symbol Removal (Decompression)

Symbol removal is used to "decompress" the reel set during bonus rounds, making the game more volatile by eliminating lower-paying symbols.

-   Symbol removal occurs **only in free spin modes** (Rocket Riot / Hyperdrive Havoc).

-   Trigger condition: **Simultaneous Scatter on reel 1 and reel 5 in a free spin** (see sections 5.1 and 5.2).

-   When triggered, the **lowest-ranked remaining symbol** from the following hierarchy is removed from the reel strips for the **remainder of the current bonus**:

    1.  10

    2.  J

    3.  Q

    4.  K

    5.  A

    6.  Cosmic Fizz

    7.  Zero-G Donut

    8.  Space Tape

-   Once a symbol tier is removed:

    -   It is no longer present on any reel for that entire bonus instance.

    -   Removal applies to **both** regular and super bonus (with different starting states, see below).

-   **Premium symbols (Chip, Zog) are never removed.**\
    This ensures chase symbols remain available throughout the feature.

* * * * *

5\. Bonus Features
------------------

In all bonus modes:

-   Wilds only land on reels **2, 3, and 4**.

-   Wilds are **sticky**: once landed, they remain locked in their positions and retain their multiplier value for the rest of the bonus.

### 5.1 Rocket Riot Bonus (Regular Bonus)

**Trigger:** Land **3 Scatter** symbols in the base game.

**Setup:**

-   Award **10 Free Spins**.

-   All Wilds that land during the bonus:

    -   Are sticky.

    -   Retain their original multiplier (×2, ×3, ×5, or ×10).

-   Initial reel set includes all symbols (no removal at start).

**Scatter Retrigger + Symbol Removal:**

-   During free spins, if a spin lands:

    -   **Scatter on reel 1** and **Scatter on reel 5** simultaneously:

        -   Award **+2 additional free spins**.

        -   **Remove the next lowest-ranked symbol** from the symbol hierarchy defined in §4.2.

-   If the lowest symbol still present is "Q", for example, that is the one removed next.

**End Condition:**

-   The bonus ends when all free spins (including retriggers) are used.

-   Total win from all bonus spins is displayed before returning to the base game.

* * * * *

### 5.2 Hyperdrive Havoc Bonus (Super Bonus)

**Trigger:** Land **4 or 5 Scatter** symbols in the base game.

**Setup:**

-   Award **10 Free Spins**.

-   Remove **all low-paying card symbols (10, J, Q, K, A)** from the reel set **before** the first bonus spin.

-   Sticky Wild behavior is identical to Rocket Riot:

    -   Wilds land only on reels 2--4.

    -   Wilds are sticky and keep their multipliers.

**Symbol Removal Progression:**

-   During free spins, a spin that lands **Scatter on reel 1** and **Scatter on reel 5**:

    -   Awards **+2 additional free spins**.

    -   Removes the next available symbol in the remaining hierarchy (only Mid symbols remain removable):

        1.  Cosmic Fizz

        2.  Zero-G Donut

        3.  Space Tape

-   Once all Mid symbols are removed, no further removal is possible; retriggers still award +2 spins if Scatter 1+5 occurs.

**End Condition:**

-   Same as Rocket Riot:

    -   Ends when all free spins (including retriggers) are used.

    -   Total bonus win is displayed and returned to base.

* * * * *

### 5.3 Symbol Behavior Inside Bonuses

-   **Wilds:**

    -   Sticky, multipliers preserved, can stack in multiple positions.

    -   Multiple Wilds on the same winning line add their multipliers.

-   **Scatters:**

    -   Only used for:

        -   Initial triggering of the bonus (3 or 4 scatters).

        -   Retrigger + symbol removal within the bonus (Scatter 1 & 5).

-   **Symbol Removal:**

    -   Only affects **Low + Mid symbols** (10--A, Cosmic Fizz, Zero-G Donut, Space Tape).

    -   Does not affect Wild or Scatter presence or behavior.

    -   Premium symbols **Chip and Zog** are always present in the reel strips.

* * * * *

6\. Feature Buys
----------------

Feature buys are optional modes that allow the player to pay an upfront price to access increased bonus potential.

| Feature Buy Name | Description | RTP Target (approx.) |
| --- | --- | --- |
| Bonus Hunt Spins | Spins with ~3× chance of landing any bonus | 96.20% (tunable) |
| Rocket Riot Bonus | Direct buy of the 3-Scatter regular bonus | 96.20% (tunable) |
| Hyperdrive Havoc | Direct buy of the 4+/5-Scatter super bonus | 96.20% (tunable) |

> Exact prices and RTPs will be finalized during math balancing but should align to an overall 96.20% target.

* * * * *

7\. RTP and Volatility Targets
------------------------------

-   **Overall RTP (target):** 96.20%

-   **Base Game RTP (non-feature buy):** ~42--45%

-   **Bonus Game RTP (all bonuses combined):** ~54--58%

-   **3-Scatter Trigger Rate (natural):** ~0.55% per base spin (target)

-   **4+/5-Scatter Trigger Rate (natural):** ~0.10% per base spin (target)

-   **Max Win:** 12,500× bet

-   **Volatility:** Very High (rare but large bonus outcomes with high wild multiplier stacking and symbol removal)

* * * * *

8\. Animations
--------------

### 8.1 Chip

-   **Idle:** Floating in microgravity, subtle visor bob and slow body drift.

-   **Win:** Raises wrench in a clumsy celebration, brief spark FX.

-   **Big Win:** Spins helmet / visor, small explosion FX behind him (non-damaging, cartoon).

### 8.2 Zog

-   **Idle:** Belly bob breathing, lazy grin, small antenna wiggle.

-   **Win:** Laughs or claps with goofy motion.

-   **Big Win:** Inflates slightly then deflates like a balloon with comic timing.

### 8.3 Wild -- Gravity Field

-   Pulsing energy field with orbiting particles.

-   On winning lines: glow intensifies, minor shockwave effect.

### 8.4 Scatter -- Bonus Pod

-   Idle: slow spin with subtle light flicker.

-   Trigger: rapid spin, bright flash and particle burst.

### 8.5 Animation File Requirements

-   All character and feature animations exported as **Spine 2D**:

    -   Files: `.json` + `.atlas` + `.png`.

-   Naming convention:

    -   `chip_idle.spine.json`

    -   `chip_win.spine.json`

    -   `chip_bigWin.spine.json`

    -   `zog_idle.spine.json`, etc.

-   Required states per premium symbol:

    -   `idle`, `win`, `bigWin`.

-   Sprite atlases must be **≤ 2048×2048**.

-   Pivot/origin points must be consistent across states for each symbol to prevent visual popping.

* * * * *

9\. Visual & Audio Direction
----------------------------

### 9.1 Visual

-   **Background:** Cartoon nebula, drifting asteroids, subtle parallax; cockpit framing in foreground.

-   **Reel Frame:** Metallic sci-fi edges, worn paint, rivets/bolts, LED trim lines.

-   **UI:** Clean HUD with neon purple/cyan accents, matching brand identity of Shift Gaming.

### 9.2 Audio

-   **Base Game:** Low-tempo synth groove with ambient space noise.

-   **Bonus Game:** Higher-tempo heroic sci-fi score, more percussion.

-   **Retrigger / Symbol Removal:** Rising alarm / "gravity lock engaged" SFX.

-   **Big Win / Mega Win:** Triumphant yet comedic fanfare.

-   **UI Interactions:** Subtle beeps, button clicks, slider whooshes.

* * * * *

10\. Technical Integration Notes (Stake Engine Web-SDK / Pixi)
--------------------------------------------------------------

### 10.1 Game Loop

1.  **Spin Start**

    -   Deduct bet.

    -   Disable spin / bet controls.

    -   Trigger reel spin animations.

2.  **Result Resolution**

    -   Receive result JSON from math-sdk:

        -   Final symbols per reel.

        -   Line wins.

        -   Wild positions and multipliers.

        -   Scatter positions and any state changes (bonus start, retrigger, removal events).

    -   Update internal game state (base or bonus mode, sticky wilds, removed symbols, remaining spins).

3.  **Win Evaluation**

    -   For each winning line, apply:

        -   Base payout from paytable.

        -   Sum of wild multipliers on that line.

    -   Update total spin win and overall session win.

4.  **Win / FX Animations**

    -   Highlight winning symbols.

    -   Play relevant symbol animations (`idle`→`win` or `bigWin`).

    -   Trigger any Wild / Scatter VFX.

5.  **Feature Transitions**

    -   If 3 or 4 Scatters on the triggering spin:

        -   Animate Scatter trigger.

        -   Transition from base to appropriate bonus mode.

    -   In bonus mode, manage:

        -   Sticky wild placement.

        -   Free spin counters.

        -   Retriggers and symbol removal.

6.  **Bonus Loop**

    -   Repeat free spins until spin counter reaches zero.

    -   Track cumulative bonus win.

7.  **Summary Screen**

    -   Show total bonus win.

    -   Transition back to base game state, restoring base reel strips (no persistent symbol removal across features).

* * * * *

11\. Performance Targets
------------------------

-   **Desktop:** 60 FPS target.

-   **Mobile:** 45+ FPS target.

-   **Max texture atlas size:** 2048×2048.

-   **Spine skeleton complexity:** ≤ 25 bones per symbol where possible.

-   Optimize draw calls and texture usage to minimize GPU load on low-end mobile devices.

* * * * *

12\. QA Checklist
-----------------

-   Paylines:

    -   All 20 lines resolve correctly left→right from reel 1.

-   Wilds:

    -   Wild multipliers **add**, not multiply.

    -   Wilds substitute correctly for all non-Scatter symbols.

    -   In base game: Wilds are non-sticky.

    -   In bonuses: Wilds are sticky and persist with correct multipliers.

-   Bonuses:

    -   3 Scatters → Rocket Riot (regular bonus).

    -   4 Scatters → Hyperdrive Havoc (super bonus).

    -   Free spins awarded correctly (10 + retriggers).

-   Symbol Removal:

    -   Triggered only when Scatter appears on reel 1 and reel 5 in free spins.

    -   Removes the correct next-lowest symbol from the hierarchy.

    -   Applies for the remainder of the current bonus only.

    -   Premium symbols (Chip, Zog) are never removed.

-   Retriggers:

    -   Each Scatter 1+5 event awards exactly **+2 free spins**.

-   State Handling:

    -   Sticky wilds persist correctly across free spins.

    -   Reel strips reset correctly when returning to base game.

-   Animations:

    -   All Spine animations play and loop correctly.

    -   No visual popping due to inconsistent pivots.

-   Feature Buys:

    -   Prices are correct and match math configuration.

    -   Entry into the correct bonus type, no desync with math results.

-   Performance:

    -   FPS targets met on supported devices.

    -   No major memory leaks or texture load issues.