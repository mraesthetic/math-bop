# Gunslingers: DRAW! — Complete Math Specification

**Game ID**: `1_0_gunslingers`  
**Working Name**: Gunslingers: DRAW!  
**Target RTP**: 96.2%  
**Max Win**: 5000× bet

---

## Table of Contents

1. [Core Layout](#1-core-layout)
2. [Symbols & Paytable](#2-symbols--paytable)
3. [Reel Strips](#3-reel-strips)
4. [Paylines](#4-paylines)
5. [Special Mechanics](#5-special-mechanics)
   - [Wild (W) Behavior](#51-wild-w-behavior)
   - [VS (DRAW) Behavior](#52-vs-draw-behavior)
6. [Bonus Logic](#6-bonus-logic)
   - [Regular Bonus: DRAW! YOUR WEAPON](#61-regular-bonus-draw-your-weapon)
   - [Super Bonus: SUPER DRAW!](#62-super-bonus-super-draw)
7. [Bonus Buy Details](#7-bonus-buy-details)
8. [Caps & Limits](#8-caps--limits)
9. [Multiplier Systems](#9-multiplier-systems)
10. [Existing Simulation Outputs](#10-existing-simulation-outputs)

---

## 1. Core Layout

### Game Dimensions
- **Reels**: 5
- **Rows**: 3 (all reels)
- **Layout**: 5×3 grid
- **Paylines**: 10 fixed lines
- **Win Type**: Lines-based evaluation (left-to-right only)
- **Evaluation Method**: Each line evaluated independently, wins summed

---

## 2. Symbols & Paytable

### Symbol Types

| Symbol ID | Name | Type | Substitutes For | Special Properties |
|-----------|------|------|-----------------|-------------------|
| **W** | WILD | Wild | All except scatter | Has multipliers in freegame |
| **VS** | DRAW | Expanding Wild | All except scatter | Expands reel, has multipliers |
| **S** | SCATTER | Scatter | None | Triggers free spins |
| **H1** | BANDIT GUY | Premium | None | Regular paying symbol |
| **H2** | BANDIT GIRL | Premium | None | Regular paying symbol |
| **H3** | SHOTGUN | Premium | None | Regular paying symbol |
| **H4** | WHISKEY | Premium | None | Regular paying symbol |
| **L1** | A | Low | None | Regular paying symbol |
| **L2** | K | Low | None | Regular paying symbol |
| **L3** | Q | Low | None | Regular paying symbol |
| **L4** | J | Low | None | Regular paying symbol |
| **L5** | 10 | Low | None | Regular paying symbol |

### Paytable (in × bet per line)

All payouts are **per line** (not total bet). Wins are multiplied by the number of active lines (10 fixed lines).

| Symbol | 5 of a kind | 4 of a kind | 3 of a kind |
|--------|-------------|-------------|-------------|
| **W (WILD)** | 20× | 10× | 5× |
| **H1 (BANDIT GUY)** | 25× | 6× | 2× |
| **H2 (BANDIT GIRL)** | 18× | 5× | 1.5× |
| **H3 (SHOTGUN)** | 14× | 4× | 1.2× |
| **H4 (WHISKEY)** | 10× | 3× | 1× |
| **L1 (A)** | 5× | 1.5× | 0.5× |
| **L2 (K)** | 4× | 1.2× | 0.4× |
| **L3 (Q)** | 3.5× | 1× | 0.3× |
| **L4 (J)** | 5× | 0.8× | 0.2× |
| **L5 (10)** | 2.5× | 0.6× | 0.2× |
| **VS (DRAW)** | No paytable (expanding wild only) | | |
| **S (SCATTER)** | No paytable (trigger only) | | |

**Note**: VS and S symbols do not have paytable entries. VS acts as an expanding wild with multipliers, and S triggers the bonus feature.

---

## 3. Reel Strips

### Base Game Reelset: `BR0.csv`

- **Used in**: Base game spins
- **Length**: ~220 rows (5 columns per row)
- **VS Frequency**: Very rare (1-3 VS total across all reels)
- **Scatter Frequency**: ~1 per 150 spins (approximately 3-4 scatters total)
- **Wild Frequency**: Moderate (appears in base game, no multipliers)
- **Symbol Distribution**: 
  - Premiums (H1-H4): Moderate density
  - Lows (L1-L5): High density
  - Wilds (W): Moderate density
  - VS: Very rare (1-3 total)
  - Scatter (S): Rare (for bonus trigger)

**Reel Strip Format**: Each row contains 5 symbols (one per reel), comma-separated.

### Bonus Reelset: `FR0.csv` (DRAW! YOUR WEAPON)

- **Used in**: Regular bonus mode (free spins after 3+ scatters)
- **Length**: ~203 rows
- **VS Frequency**: 4-6 VS symbols per reel (spread out)
- **Wild Frequency**: ~55-60 W symbols (reduced from base)
- **Scatter Frequency**: Controlled for retriggers
- **Symbol Distribution**:
  - Premiums: Similar to base
  - Lows: Increased (replacing some wilds)
  - Wilds (W): ~55-60 total (with multipliers in freegame)
  - VS: 4-6 per reel
  - Scatter (S): Controlled for retrigger logic

### Superbonus Reelset: `FR1.csv` (SUPER DRAW!)

- **Used in**: Superbonus mode only
- **Length**: ~203 rows
- **VS Frequency**: 6-8 VS symbols per reel (spread out)
- **Wild Frequency**: Lower than FR0
- **Scatter Frequency**: Controlled (always 3 scatters = 10 spins on entry)
- **Symbol Distribution**:
  - Premiums: Similar to base/bonus
  - Lows: High density (many L1 symbols)
  - Wilds (W): Reduced compared to FR0
  - VS: 6-8 per reel
  - Scatter (S): Controlled

### Win Cap Reelset: `FRWCAP.csv`

- **Used in**: Win cap condition (very rare, 0.1% of spins)
- **Purpose**: Forces max win scenarios
- **Frequency**: Only used in special conditions for max win testing

---

## 4. Paylines

**Total Paylines**: 10 fixed lines

All paylines are **left-to-right only**. Each line is defined by row positions per reel (0-based indexing: 0=top, 1=middle, 2=bottom).

| Line | Row Positions (Reel 0-4) | Description |
|------|---------------------------|-------------|
| 1 | `[0, 0, 0, 0, 0]` | Top row (straight) |
| 2 | `[1, 1, 1, 1, 1]` | Middle row (straight) |
| 3 | `[2, 2, 2, 2, 2]` | Bottom row (straight) |
| 4 | `[0, 1, 2, 1, 0]` | V-shape down |
| 5 | `[2, 1, 0, 1, 2]` | V-shape up |
| 6 | `[0, 0, 1, 1, 2]` | Zigzag down |
| 7 | `[2, 2, 1, 1, 0]` | Zigzag up |
| 8 | `[0, 1, 1, 1, 2]` | Step down |
| 9 | `[2, 1, 1, 1, 0]` | Step up |
| 10 | `[0, 1, 0, 1, 0]` | Wave |

**Evaluation**: Each line is evaluated independently. If a symbol appears on multiple lines, each line pays separately. Total win = sum of all line wins (after multipliers).

---

## 5. Special Mechanics

### 5.1 Wild (W) Behavior

#### Base Game
- **Substitution**: W substitutes for all regular symbols (not scatter)
- **No Multipliers**: In base game, W has no multiplier values
- **Paytable**: W can form its own wins (5-of-a-kind W = 20×, 4-of-a-kind = 10×, 3-of-a-kind = 5×)

#### Freegame (Bonus/Superbonus)
- **Multipliers Active**: Each W symbol gets a random multiplier from the W multiplier distribution
- **Multiplier Method**: **Additive** (per symbol)
  - Each W symbol on a winning line contributes its multiplier value
  - Example: Line with 3 W symbols having multipliers [2×, 3×, 5×] → Combined multiplier = 2 + 3 + 5 = 10×
- **Multiplier Distribution**: See [Multiplier Systems](#9-multiplier-systems)

#### Win Priority
- If a line has both wild-only wins and regular symbol wins:
  - **Wild win**: Uses first wild symbol (W)
  - **Regular win**: Uses first non-wild symbol
  - **Highest win wins**: The larger of the two is awarded

### 5.2 VS (DRAW) Behavior

#### Appearance

**Base Game**:
- VS appears very rarely (1-3 total VS symbols across all reels in BR0.csv)
- No forced VS in base game

**Bonus Mode (FR0.csv)**:
- VS frequency: 4-6 VS symbols per reel (spread out)
- Natural landing only (no forced VS)

**Superbonus Mode (FR1.csv)**:
- VS frequency: 6-8 VS symbols per reel (spread out)
- **Guaranteed VS**: Exactly ONE VS reel per spin (forced if none land naturally)
- If multiple VS reels land, only the first one is kept; others are removed
- If no VS reel lands, one is forced on a random reel at a random position

#### Expansion
- When VS appears on a reel, the **entire reel expands to wild** (all positions become W symbols)
- Expansion happens **before line evaluation**
- VS symbols are replaced with W symbols after expansion (for win calculation)

#### Multiplier Assignment

**Per-Reel Multiplier**:
- Each VS reel gets **ONE multiplier** (same multiplier for all positions on that reel)
- Multipliers are assigned **before reveal event** (for frontend display)
- Multiplier distribution differs by mode:
  - **Regular Bonus**: Uses `self.padding_symbol_values["VS"]["multiplier"]`
  - **Superbonus**: Uses `self.superbonus_vs_multipliers`

**Multiplier Application**:
- **Multiplicative across reels**: If a winning line uses multiple VS reels, multipliers multiply
- Example: Line uses reel 2 (VS, 3×) and reel 4 (VS, 5×) → Combined multiplier = 3 × 5 = 15×
- **Cap**: Total combined multiplier capped at **250×**

**Scatter Handling**:
- If VS is forced over a scatter symbol in superbonus, the scatter is preserved via `underlyingSymbol` attribute
- VS does not substitute for scatter symbols

---

## 6. Bonus Logic

### 6.1 Regular Bonus: DRAW! YOUR WEAPON

#### Trigger Conditions
- **From Base Game**: 3+ scatters (S symbols) anywhere on the board
- **Scatter Counts**:
  - 3 scatters = 10 free spins
  - 4 scatters = 12 free spins
  - 5 scatters = 15 free spins

#### Retrigger (During Free Spins)
- **During free spins**: 2+ scatters can retrigger
- **Retrigger Awards**:
  - 2 scatters = +2 free spins
  - 3 scatters = +3 free spins
  - 4 scatters = +8 free spins
  - 5 scatters = +12 free spins

#### Reelset
- Uses `FR0.csv` for all free spins
- VS frequency: 4-6 per reel
- Wilds have multipliers (see [Multiplier Systems](#9-multiplier-systems))

#### Starting State
- Initial free spins awarded based on trigger count
- No guaranteed VS on first spin
- Normal VS probability applies

### 6.2 Super Bonus: SUPER DRAW!

#### Access
- **Feature Buy Only**: Cannot be naturally triggered from base game
- **Cost**: 400× bet

#### Trigger (Feature Buy Entry)
- When feature buy is purchased, player is dropped into free spins mode
- **Always awards**: Exactly 3 scatters = 10 free spins (forced)
- Emits `freeSpinTrigger` event (not retrigger) for intro screen

#### Reelset
- Uses `FR1.csv` for all free spins
- VS frequency: 6-8 per reel
- **Guaranteed VS**: Exactly ONE VS reel per spin (forced if none land naturally)

#### Retrigger (During Free Spins)
- Same as regular bonus:
  - 2 scatters = +2 free spins
  - 3 scatters = +3 free spins
  - 4 scatters = +8 free spins
  - 5 scatters = +12 free spins

#### Multiplier Distribution
- Uses superbonus-specific VS multiplier distribution (see [Multiplier Systems](#9-multiplier-systems))

---

## 7. Bonus Buy Details

### Base Mode
- **Mode ID**: `base`
- **Cost**: 1× bet
- **Access**: Normal base game spins
- **Features**: 
  - Can trigger bonus naturally (3+ scatters)
  - No feature buy option

### Regular Bonus Buy
- **Mode ID**: `bonus`
- **Cost**: 100× bet
- **Access**: Feature buy only (`is_buybonus=True`)
- **State on Entry**:
  - Drops player into free spins mode
  - Uses `FR0.csv` reelset
  - Starts with free spins (number determined by simulation conditions)
  - Wilds have multipliers
  - No guaranteed VS on first spin

### Superbonus Buy
- **Mode ID**: `superbonus`
- **Cost**: 400× bet
- **Access**: Feature buy only (`is_buybonus=True`)
- **State on Entry**:
  - Drops player into free spins mode
  - Uses `FR1.csv` reelset
  - **Always awards exactly 10 free spins** (3 scatters forced)
  - Emits `freeSpinTrigger` event for intro screen
  - **Guaranteed VS**: Exactly ONE VS reel per spin (including first spin)
  - Uses superbonus-specific VS multiplier distribution

---

## 8. Caps & Limits

### Max Win Cap
- **Overall Max Win**: 5000× bet
- Applies to total win across all lines and multipliers

### VS Multiplier Cap
- **Combined VS Multiplier Cap**: 250×
- If multiple VS reels contribute to a winning line, their multipliers multiply together
- If the product exceeds 250×, it is capped at 250×

### Wild Multiplier
- **No Cap**: Wild multipliers are additive (per symbol), so no explicit cap
- However, max win cap (5000×) still applies to total win

### Free Spin Limits
- **No Hard Limit**: No maximum number of free spins (can retrigger indefinitely)
- **Practical Limit**: Controlled by retrigger probabilities and simulation conditions

---

## 9. Multiplier Systems

### Wild (W) Multiplier Distribution

**Used in**: Freegame mode only (bonus and superbonus)

| Multiplier | Weight | Probability | Percentage |
|------------|--------|-------------|------------|
| 2× | 100 | 0.294118 | 29.41% |
| 3× | 50 | 0.147059 | 14.71% |
| 4× | 50 | 0.147059 | 14.71% |
| 5× | 50 | 0.147059 | 14.71% |
| 10× | 30 | 0.088235 | 8.82% |
| 20× | 20 | 0.058824 | 5.88% |
| 50× | 5 | 0.014706 | 1.47% |

**Total Weight**: 305  
**Average Multiplier**: ~6.77×

**Application Method**: Additive (per symbol)
- Each W symbol on a winning line contributes its multiplier value
- Example: Line with W symbols [2×, 3×, 5×] → Combined = 2 + 3 + 5 = 10×

### VS (DRAW) Multiplier Distribution - Regular Bonus

**Used in**: 
- Bonus mode (DRAW! YOUR WEAPON) - uses FR0.csv
- Base game (very rare VS appearances)

| Multiplier | Weight | Probability | Percentage |
|------------|--------|-------------|------------|
| 2× | 830 | 0.764641 | 76.46% |
| 3× | 170 | 0.156549 | 15.65% |
| 4× | 60 | 0.055250 | 5.53% |
| 5× | 22 | 0.020258 | 2.03% |
| 8× | 3 | 0.002763 | 0.28% |
| 10× | 1 | 0.000921 | 0.09% |

**Total Weight**: 1086  
**Average Multiplier**: ~2.352×

**Application Method**: Multiplicative (per reel)
- Each VS reel gets one multiplier
- If a line uses multiple VS reels, multipliers multiply
- Example: Reel 2 = 3×, Reel 4 = 5× → Combined = 3 × 5 = 15×
- **Cap**: Combined multiplier capped at 250×

### VS (DRAW) Multiplier Distribution - Superbonus

**Used in**: Superbonus mode (SUPER DRAW!) - uses FR1.csv

| Multiplier | Weight | Probability | Percentage |
|------------|--------|-------------|------------|
| 2× | 750 | 0.726744 | 72.67% |
| 3× | 230 | 0.222868 | 22.29% |
| 4× | 38 | 0.036822 | 3.68% |
| 5× | 10 | 0.009690 | 0.97% |
| 8× | 3 | 0.002907 | 0.29% |
| 10× | 1 | 0.000969 | 0.10% |

**Total Weight**: 1032  
**Average Multiplier**: ~2.350×

**Application Method**: Multiplicative (per reel)
- Same as regular bonus (multiplicative across reels)
- **Cap**: Combined multiplier capped at 250×

---

## 10. Existing Simulation Outputs

### Target RTP Structure
- **Total RTP**: 96.2%
- **Base Game RTP**: ~38-42%
- **Bonus RTP**: ~58-62%
- **Superbonus RTP**: ~0.015% (additive to base)
- **Volatility**: High

### Statistics Summary (from `library/statistics_summary.json`)

#### Base Mode
- **Cost**: 1× bet
- **Freegame Hit Rate**: ~200 (scatter trigger rate)
- **Freegame RTP**: 0.571 (57.1%)
- **Freegame Avg Win**: 114.2× bet
- **Basegame Hit Rate**: 3.5%
- **Basegame RTP**: 0.39 (39%)
- **Basegame Avg Win**: 1.36× bet

#### Bonus Mode
- **Cost**: 100× bet
- **Scatter Hit Rate**: 100% (always triggers on buy)
- **Scatter Avg Win**: 9620× bet (96.2× per feature)

#### Superbonus Mode
- **Cost**: 400× bet
- **Scatter Hit Rate**: 100% (always triggers on buy)
- **Scatter Avg Win**: 38480× bet (384.8× per feature)

### Win Distribution Notes
- Max win scenarios are tested via `FRWCAP.csv` reelset
- Win cap condition occurs in ~0.1% of spins
- Average feature wins target:
  - Bonus: ~96.2× bet (at 100× cost = 96.2% RTP)
  - Superbonus: ~384.8× bet (at 400× cost = 96.2% RTP)

---

## Implementation Notes

### Key Code Files
- **`game_config.py`**: Main configuration (symbols, paytable, reels, multipliers, bet modes)
- **`game_executables.py`**: VS expansion logic, multiplier assignment, line evaluation
- **`game_override.py`**: Wild multiplier assignment in freegame, superbonus spin count override
- **`game_stats_summary.py`**: RTP and statistics calculation
- **`reels/BR0.csv`**: Base game reelset
- **`reels/FR0.csv`**: Bonus reelset
- **`reels/FR1.csv`**: Superbonus reelset

### Multiplier Application Order
1. Board is drawn (with padding symbols)
2. VS symbols are injected (superbonus only, if needed)
3. VS multipliers are assigned (before reveal event)
4. Reveal event is emitted (board shown to player)
5. VS reels are expanded to wilds (for evaluation)
6. Line evaluation occurs (using expanded board)
7. VS multipliers are applied to line wins (multiplicative)
8. Wild multipliers are applied (additive, per symbol)
9. Total win is calculated (sum of all line wins)

### Special Considerations
- VS expansion happens **before** line evaluation (reel becomes all wilds)
- VS multipliers are applied **after** base win calculation (multiply the line win)
- Wild multipliers use "symbol" method (additive per symbol)
- VS multipliers use custom logic (multiplicative per reel, capped at 250×)
- Superbonus forces exactly ONE VS reel per spin (not on trigger spin, only during free spins)

---

**End of Math Specification**

For questions or modifications, refer to the code files listed above or consult the game design documentation.

