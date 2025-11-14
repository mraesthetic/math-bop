# Gunslingers: DRAW! — Backend Implementation Analysis

**Game ID**: `1_0_gunslingers`  
**Working Name**: Gunslingers: DRAW!  
**Target RTP**: 96.2%  
**Max Win**: 10,000× bet  
**Documentation Date**: Generated from codebase analysis

---

## Table of Contents

1. [Modes & Bet Variants](#31-modes--bet-variants)
2. [Symbols, Paylines, and Evaluation](#32-symbols-paylines-and-evaluation)
3. [Reels and Reelsets](#33-reels-and-reelsets)
4. [VS and Wild Behavior (Backend Truth)](#34-vs-and-wild-behavior-backend-truth)
5. [Scatters, Bonus Triggers, and Retriggers](#35-scatters-bonus-triggers-and-retriggers)
6. [Win Caps and Wincap Behavior](#36-win-caps-and-wincap-behavior)
7. [RTP / Simulation Tools (Backend View)](#37-rtp--simulation-tools-backend-view)
8. [Backend vs Frontend Comparison](#4-compare-backend-behavior-vs-frontend-expectations)

---

## 3.1 Modes & Bet Variants

Gunslingers has **3 bet modes** defined in `game_config.py`:

### Base Game

| Property | Value |
|----------|-------|
| **Mode Identifier** | `"base"` |
| **Config Key** | `bet_modes[0]` (name="base") |
| **Game Type** | `basegame_type` ("basegame") |
| **Cost** | 1.0× bet |
| **RTP** | 96.2% |
| **Max Win** | 10,000× bet |
| **How Entered** | Normal base game spins (default mode) |
| **Feature Buy** | No (`is_buybonus=False`) |
| **Default Reelset** | `BR0.csv` |
| **Distributions** | 4 conditions: wincap (0.1%), freegame (10%), zerowin (40%), basegame (50%) |

**Entry Method**: Default mode when starting a new game session. No special trigger required.

**Test/Debug Modes**: None explicitly defined, but distributions include:
- **Wincap condition** (0.1% quota): Forces max win scenarios using `FRWCAP.csv` reelset
- **Zero win condition** (40% quota): Forces zero-win spins for RTP balancing

---

### Regular Bonus (DRAW! YOUR WEAPON)

| Property | Value |
|----------|-------|
| **Mode Identifier** | `"bonus"` |
| **Config Key** | `bet_modes[1]` (name="bonus") |
| **Game Type** | `freegame_type` ("freegame") after trigger |
| **Cost** | 100.0× bet |
| **RTP** | 96.2% |
| **Max Win** | 10,000× bet |
| **How Entered** | Feature buy only (`is_buybonus=True`) |
| **Feature Buy** | Yes |
| **Default Reelset** | `FR0.csv` (forced via `regular_bonus_buy_condition`) |
| **Distributions** | 2 conditions: wincap (0.1%), freegame (99.9%) |

**Entry Method**: 
- **Feature Buy**: Player purchases bonus for 100× bet
- **Natural Trigger**: Can also be triggered from base game with 3 scatters (see scatter logic)
- **Scatter Protection**: Regular bonus buy **always forces exactly 3 scatters** (prevents 4-scatter superbonus trigger)

**Special Behavior**: 
- Uses `regular_bonus_buy_condition` which sets `scatter_triggers: {3: 100}` to ensure only 3 scatters appear
- This prevents accidental superbonus trigger when buying regular bonus

---

### Super Bonus (SUPER DRAW!)

| Property | Value |
|----------|-------|
| **Mode Identifier** | `"superbonus"` |
| **Config Key** | `bet_modes[2]` (name="superbonus") |
| **Game Type** | `freegame_type` ("freegame") after trigger |
| **Cost** | 400.0× bet |
| **RTP** | 96.2% |
| **Max Win** | 10,000× bet |
| **How Entered** | Feature buy only (`is_buybonus=True`) OR natural 4-scatter trigger from base |
| **Feature Buy** | Yes |
| **Default Reelset** | `FR1.csv` (forced via `superbonus_condition`) |
| **Distributions** | 2 conditions: wincap (0.1%), freegame (99.9%) |

**Entry Method**:
- **Feature Buy**: Player purchases superbonus for 400× bet
- **Natural Trigger**: Can be triggered from base game with **4 scatters** (see scatter logic)
- **Scatter Protection**: Superbonus buy **always forces exactly 4 scatters** (`scatter_triggers: {4: 100}`)

**Special Behavior**:
- Uses `FR1.csv` reelset (different from regular bonus)
- **Guaranteed VS**: Exactly ONE VS reel per free spin (enforced in `draw_board()`)
- Uses `superbonus_vs_multipliers` distribution (different from regular bonus)

---

### Test/Wincap Mode

| Property | Value |
|----------|-------|
| **Mode Identifier** | Not a separate mode, but a distribution condition |
| **Config Key** | `wincap_condition` (used in all bet modes) |
| **Game Type** | `freegame_type` ("freegame") |
| **Cost** | Same as parent bet mode |
| **RTP** | N/A (test condition) |
| **Max Win** | 10,000× bet (forced) |
| **How Entered** | Via distribution quota (0.1% of spins in all modes) |
| **Reelset** | `FRWCAP.csv` (weight: 5) + `FR0.csv` (weight: 1) |
| **Purpose** | Forces max win scenarios for testing |

**Entry Method**: Automatically included in all bet modes with 0.1% quota. Uses `force_wincap: True` to ensure max win outcomes.

---

## 3.2 Symbols, Paylines, and Evaluation

### Grid Size

- **Reels**: 5
- **Rows**: 3 (all reels)
- **Layout**: 5×3 grid
- **Padding**: Enabled (`include_padding = True`) — adds top/bottom symbols for visual effect

### Paylines

**Backend Implementation**: **10 fixed paylines** (defined in `game_config.py`, lines 79-100)

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

**Indexing**: 0-based (0=top, 1=middle, 2=bottom)

**Evaluation**: Left-to-right only. Each line evaluated independently. Wins are summed across all lines.

---

### Symbols

#### Regular Paying Symbols

| Symbol ID | Name | Type | Paytable (3/4/5 of a kind) |
|-----------|------|------|----------------------------|
| **H1** | BANDIT GUY | Premium | 2× / 6× / 25× |
| **H2** | BANDIT GIRL | Premium | 1.5× / 5× / 18× |
| **H3** | SHOTGUN | Premium | 1.2× / 4× / 14× |
| **H4** | WHISKEY | Premium | 1× / 3× / 10× |
| **L1** | A | Low | 0.5× / 1.5× / 5× |
| **L2** | K | Low | 0.4× / 1.2× / 4× |
| **L3** | Q | Low | 0.3× / 1× / 3.5× |
| **L4** | J | Low | 0.2× / 0.8× / 3× |
| **L5** | 10 | Low | 0.2× / 0.6× / 2.5× |

**Paytable Format**: Values are **× line bet** (not × total bet). Since there are 10 fixed paylines, a 5-of-a-kind H1 win pays 25× per line = 25× total bet (assuming 1× bet per line).

**Backend Storage**: Paytable stored as `(count, symbol_name)` tuples in `self.paytable`:
```python
(5, "H1"): 25,  # 5 of a kind H1 = 25× line bet
(4, "H1"): 6,   # 4 of a kind H1 = 6× line bet
(3, "H1"): 2,   # 3 of a kind H1 = 2× line bet
```

#### Special Symbols

| Symbol ID | Name | Type | Special Properties |
|-----------|------|------|-------------------|
| **W** | WILD | Wild | Substitutes for all except scatter. Has multipliers in freegame. |
| **VS** | DRAW | Expanding Wild | Expands entire reel to wilds. Has multipliers. Substitutes for all except scatter. |
| **S** | SCATTER | Scatter | Triggers free spins. No paytable entry. |

**Special Symbol Configuration**:
```python
self.special_symbols = {
    "wild": ["W", "VS"],
    "scatter": ["S"],
    "multiplier": ["W", "VS"],
    "underlyingSymbol": []  # Custom attribute for VS covering scatters
}
```

#### Backend-Only / Padding Symbols

- **Top/Bottom Padding**: When `include_padding = True`, each reel has a top and bottom symbol that are visible but not part of the evaluation grid
- **No separate padding symbol types**: Padding uses the same symbol types as the main board (drawn from the same reelset)

---

### Paytable (Backend Storage)

**Location**: `game_config.py`, lines 34-76

**Format**: Dictionary with `(count, symbol_name)` keys:
- `count`: Number of symbols in a line (3, 4, or 5)
- `symbol_name`: Symbol identifier (e.g., "H1", "W", "L5")

**Values**: Multipliers in **× line bet** (not × total bet)

**Example**:
```python
(5, "H1"): 25,  # 5 H1 symbols = 25× line bet
(4, "W"): 10,   # 4 W symbols = 10× line bet
(3, "L5"): 0.2, # 3 L5 symbols = 0.2× line bet
```

**Missing Entries**: 
- No 2-of-a-kind payouts (minimum is 3)
- No paytable entries for `S` (scatter) or `VS` (DRAW) — these are special symbols only

---

### Line Evaluation Logic

**Implementation**: `src/calculations/lines.py` → `Lines.get_lines()`

**Process**:

1. **Left-to-Right Only**: Each payline is evaluated from reel 0 (left) to reel 4 (right)

2. **Wild Substitution**:
   - `W` and `VS` (after expansion) substitute for all regular symbols except scatter
   - Wilds can form their own wins (e.g., 5 W symbols = 20× line bet)

3. **Win Priority**:
   - If a line has both wild-only wins and regular symbol wins, the **higher win is awarded**
   - Example: Line with `[W, W, W, H1, H1]`:
     - Wild win: 3 W = 5× line bet
     - Regular win: 5 symbols (3 W + 2 H1) = 25× line bet
     - **Award**: 25× line bet (higher value)

4. **VS Expansion** (before evaluation):
   - VS reels are expanded to wilds **before** line evaluation (see VS behavior section)
   - Expansion happens in `game_executables.py` → `expand_vs_reels()`
   - After expansion, VS symbols are replaced with `W` symbols for evaluation

5. **Multiplier Application**:
   - **Wild multipliers** (W symbols): Applied using "symbol" method (additive per symbol)
   - **VS multipliers**: Applied after base win calculation (multiplicative per reel, capped at 500×)
   - See VS behavior section for details

6. **Evaluation Order**:
   ```
   draw_board() → expand_vs_reels() → Lines.get_lines() → apply VS multipliers → emit events
   ```

**Code Reference**: `game_executables.py`, lines 183-213

---

## 3.3 Reels and Reelsets

### Reelset Files

All reelsets are CSV files located in `games/1_0_gunslingers/reels/`:

| Reelset | File | Used For | Length (approx) |
|---------|------|----------|-----------------|
| **BR0** | `BR0.csv` | Base game | ~220 rows |
| **FR0** | `FR0.csv` | Regular bonus (DRAW! YOUR WEAPON) | ~203 rows |
| **FR1** | `FR1.csv` | Superbonus (SUPER DRAW!) | ~203 rows |
| **WCAP** | `FRWCAP.csv` | Win cap test scenarios | Variable |

**Format**: Each row contains 5 symbols (one per reel), comma-separated:
```
L1,H3,L5,L4,L3
H1,H3,H4,L2,L5
H3,H1,L4,L1,H4
```

---

### Base Game Reelset: BR0.csv

| Property | Value |
|----------|-------|
| **File** | `reels/BR0.csv` |
| **Used In** | Base game spins only |
| **Length** | ~220 rows (5 columns per row) |
| **VS Frequency** | Very rare (1-3 VS total across all reels) |
| **Scatter Frequency** | ~1 per 150 spins (approximately 3-4 scatters total) |
| **Wild Frequency** | Moderate (appears in base game, no multipliers) |
| **Max Scatters** | 4 per board (enforced in reel strip) |

**Symbol Distribution**:
- Premiums (H1-H4): Moderate density
- Lows (L1-L5): High density
- Wilds (W): Moderate density
- VS: Very rare (1-3 total)
- Scatter (S): Rare (for bonus trigger)

**Configuration**: `self.padding_reels[self.basegame_type] = self.reels["BR0"]`

---

### Regular Bonus Reelset: FR0.csv

| Property | Value |
|----------|-------|
| **File** | `reels/FR0.csv` |
| **Used In** | Regular bonus (DRAW! YOUR WEAPON) |
| **Length** | ~203 rows |
| **VS Frequency** | 4-6 VS symbols per reel (spread out) |
| **Wild Frequency** | ~55-60 W symbols (reduced from base) |
| **Scatter Frequency** | Controlled for retriggers |
| **VS Multipliers** | Uses `self.padding_symbol_values["VS"]["multiplier"]` |

**Symbol Distribution**:
- Premiums: Similar to base
- Lows: Increased (replacing some wilds)
- Wilds (W): ~55-60 total (with multipliers in freegame)
- VS: 4-6 per reel
- Scatter (S): Controlled for retrigger logic

**Configuration**: `self.padding_reels[self.freegame_type] = self.reels["FR0"]` (default, can be switched to FR1 for superbonus)

---

### Superbonus Reelset: FR1.csv

| Property | Value |
|----------|-------|
| **File** | `reels/FR1.csv` |
| **Used In** | Superbonus (SUPER DRAW!) only |
| **Length** | ~203 rows |
| **VS Frequency** | 6-8 VS symbols per reel (spread out) |
| **Wild Frequency** | Lower than FR0 |
| **Scatter Frequency** | Controlled (always 3 scatters = 10 spins on entry) |
| **VS Multipliers** | Uses `self.superbonus_vs_multipliers` |
| **Guaranteed VS** | Exactly ONE VS reel per spin (enforced in code) |

**Symbol Distribution**:
- Premiums: Similar to base/bonus
- Lows: High density (many L1 symbols)
- Wilds (W): Reduced compared to FR0
- VS: 6-8 per reel
- Scatter (S): Controlled

**Configuration**: Set dynamically when superbonus is triggered:
```python
self.config.padding_reels[self.config.freegame_type] = self.config.reels["FR1"]
```

---

### Win Cap Reelset: FRWCAP.csv

| Property | Value |
|----------|-------|
| **File** | `reels/FRWCAP.csv` |
| **Used In** | Win cap condition (0.1% of spins in all modes) |
| **Purpose** | Forces max win scenarios |
| **Frequency** | Only used in `wincap_condition` distribution |
| **Weight** | 5 (vs FR0 weight: 1) when used in freegame |

**Configuration**: Used in `wincap_condition`:
```python
"reel_weights": {
    self.basegame_type: {"BR0": 1},
    self.freegame_type: {"FR0": 1, "WCAP": 5},  # WCAP has 5× weight
}
```

---

### Reelset Selection by Mode

| Mode | Base Game Reelset | Free Game Reelset |
|------|-------------------|-------------------|
| **Base** | `BR0.csv` | `FR0.csv` (when bonus triggered) |
| **Bonus Buy** | `BR0.csv` | `FR0.csv` (forced) |
| **Superbonus Buy** | `BR0.csv` | `FR1.csv` (forced) |
| **Natural 3 Scatter** | `BR0.csv` | `FR0.csv` (switched in `run_freespin_from_base()`) |
| **Natural 4 Scatter** | `BR0.csv` | `FR1.csv` (switched in `run_freespin_from_base()`) |
| **Wincap Test** | `BR0.csv` | `FRWCAP.csv` (weight: 5) + `FR0.csv` (weight: 1) |

**Code Reference**: `game_override.py`, lines 45-101 (reelset switching logic)

---

## 3.4 VS and Wild Behavior (Backend Truth)

### VS Symbol Generation / Injection

**Location**: `game_executables.py` → `draw_board()` (lines 9-105)

**Process**:

1. **Natural Landing**: VS symbols can land naturally from the reelset (FR0 or FR1)

2. **Superbonus Guarantee** (lines 14-57):
   - **When**: Only in superbonus mode (`betmode == "superbonus"` OR `is_superbonus_from_scatter == True`) AND during free spins (`gametype == freegame_type`)
   - **NOT on trigger spin**: Guarantee only applies during free spins, not on the basegame trigger spin
   - **Logic**:
     - Count how many reels have VS symbols
     - If **0 VS reels**: Force exactly one VS on a random reel at a random position
     - If **>1 VS reels**: Keep only the first one, remove VS from all other reels (replace with L1)
     - If **exactly 1 VS reel**: Do nothing (already correct)

3. **Scatter Preservation** (lines 36-45):
   - If VS is forced over a scatter symbol, the scatter is preserved via `underlyingSymbol` attribute
   - Code: `vs_symbol.assign_attribute({"underlyingSymbol": "S"})`
   - This allows frontend to show scatter indicator even when VS covers it

---

### VS Expansion Timing

**Location**: `game_executables.py` → `expand_vs_reels()` (lines 132-156)

**When**: **BEFORE line evaluation** (but AFTER reveal event)

**Process**:

1. **Multiplier Assignment** (in `draw_board()`, lines 59-99):
   - Multipliers are assigned to VS symbols **before** reveal event
   - Each VS reel gets **ONE multiplier** (same for all positions on that reel)
   - Multiplier is stored in `self.vs_reel_multipliers[reel_idx]`
   - Multiplier attribute is attached to VS symbols for frontend display

2. **Reveal Event** (line 105):
   - Reveal event is emitted with VS symbols still visible (with multiplier attributes)

3. **Expansion** (in `evaluate_lines_board()`, line 187):
   - `expand_vs_reels()` is called
   - All VS symbols on a reel are replaced with `W` symbols
   - Original VS symbols are discarded (but multipliers are stored in `self.vs_reel_multipliers`)

4. **Line Evaluation** (lines 190-195):
   - Lines are evaluated using the expanded board (VS reels are now all wilds)

**Code Flow**:
```
draw_board() → assign VS multipliers → reveal_event() → expand_vs_reels() → evaluate_lines_board()
```

---

### VS Multiplier Distribution

#### Regular Bonus (FR0.csv)

**Location**: `game_config.py`, line 148

**Distribution**:
```python
{2: 810, 3: 168, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
```

**Statistics**:
- **Total Weight**: 1,065
- **Average Multiplier**: ~2.425×
- **Probabilities**:
  - 2×: 76.06%
  - 3×: 15.77%
  - 4×: 5.63%
  - 5×: 2.07%
  - 8×: 0.28%
  - 10×: 0.09%
  - 25×: 0.09%
  - 50×: 0.09%

**Used In**: Regular bonus (DRAW! YOUR WEAPON) and base game (very rare VS appearances)

**Code Reference**: `game_executables.py`, line 84

---

#### Superbonus (FR1.csv)

**Location**: `game_config.py`, line 161

**Distribution**:
```python
{2: 740, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
```

**Statistics**:
- **Total Weight**: 1,025
- **Average Multiplier**: ~2.425×
- **Probabilities**:
  - 2×: 72.20%
  - 3×: 22.44%
  - 4×: 3.71%
  - 5×: 0.98%
  - 8×: 0.29%
  - 10×: 0.10%
  - 25×: 0.20%
  - 50×: 0.10%

**Used In**: Superbonus (SUPER DRAW!) only

**Code Reference**: `game_executables.py`, line 82

---

### VS Multiplier Application

**Location**: `game_executables.py` → `calculate_vs_line_multiplier()` (lines 158-181)

**Method**: **Multiplicative across reels**

**Process**:

1. **Per-Reel Multiplier**: Each VS reel gets ONE multiplier (stored in `self.vs_reel_multipliers[reel_idx]`)

2. **Line Multiplier Calculation**:
   - For each winning line, find all unique reels that have VS multipliers
   - Multiply all VS reel multipliers together
   - Example: Line uses reel 2 (VS, 3×) and reel 4 (VS, 5×) → Combined = 3 × 5 = 15×

3. **Cap Application** (line 178):
   - Combined multiplier is **capped at 500×**
   - Code: `if combined_mult > 500: combined_mult = 500`

4. **Win Application** (lines 198-206):
   - VS multiplier is applied to the base line win (after wild multipliers)
   - Formula: `final_win = base_win * vs_multiplier`
   - Stored in win meta: `win["meta"]["vsMultiplier"] = vs_mult`

**Code Reference**: `game_executables.py`, lines 197-206

---

### Wild (W) Behavior

#### Multiplier Assignment

**Location**: `game_override.py` → `assign_mult_property()` (lines 36-43)

**When**: Only in **freegame mode** (`gametype == freegame_type`)

**Distribution** (from `game_config.py`, line 147):
```python
{2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}
```

**Statistics**:
- **Total Weight**: 305
- **Average Multiplier**: ~6.77×
- **Probabilities**:
  - 2×: 32.79%
  - 3×: 16.39%
  - 4×: 16.39%
  - 5×: 16.39%
  - 10×: 9.84%
  - 20×: 6.56%
  - 50×: 1.64%

**Assignment**: Each `W` symbol gets a random multiplier from the distribution when created (via `assign_special_sym_function()`)

---

#### Multiplier Application

**Location**: `src/wins/multiplier_strategy.py` → `apply_mult()` (called from `Lines.get_lines()`)

**Method**: **Additive (per symbol)**

**Process**:

1. **Per-Symbol Addition**: Each `W` symbol on a winning line contributes its multiplier value
2. **Combined Multiplier**: Sum of all wild multipliers on the line
3. **Example**: Line with `[W(2×), W(3×), W(5×), H1, H1]` → Combined multiplier = 2 + 3 + 5 = 10×

**Formula**: `line_win = base_win * (sum of all wild multipliers on line)`

**Code Reference**: `src/calculations/lines.py`, lines 80-82, 98-100 (calls `apply_mult()` with `multiplier_method="symbol"`)

---

#### Wild-Only Wins

**Location**: `src/calculations/lines.py`, lines 71-95

**Process**:

1. **Wild-Only Line**: If a line starts with wilds and has no regular symbols, it can form a wild-only win
2. **Paytable**: Wild-only wins use the paytable entry `(wild_count, "W")`
3. **Example**: `[W, W, W, W, W]` = 5 W = 20× line bet

**Win Priority**: If a line has both wild-only wins and regular symbol wins, the **higher win is awarded** (see line evaluation logic)

---

## 3.5 Scatters, Bonus Triggers, and Retriggers

### Scatter Logic (Backend Truth)

**Location**: `game_config.py`, lines 110-122

**Max Scatters**: **4 scatters maximum** per board (enforced in BR0.csv reel strip)

**Configuration**:
```python
self.freespin_triggers = {
    self.basegame_type: {3: 10, 4: 10},  # 3 scatters = regular bonus, 4 scatters = superbonus
    self.freegame_type: {2: 2, 3: 3, 4: 8},  # Retriggers (5 scatters removed, max 4)
}
```

**Anticipation Triggers**:
```python
self.anticipation_triggers = {
    self.basegame_type: 2,  # 2+ scatters = anticipation (min trigger is 3, so 3-1=2)
    self.freegame_type: 1,  # 1+ scatters = anticipation (min trigger is 2, so 2-1=1)
}
```

---

### Base → Regular Bonus

**Trigger**: **3 scatters** from base game

**Awards**: **10 free spins**

**Reelset**: `FR0.csv` (regular bonus reelset)

**Code Reference**: `game_override.py`, lines 73-77

**Process**:
1. `check_fs_condition()` detects 3 scatters
2. `run_freespin_from_base()` is called
3. `is_superbonus_from_scatter = False` (ensures regular bonus mode)
4. Reelset switched to `FR0.csv`
5. `update_freespin_amount()` sets `tot_fs = 10`
6. `fs_trigger_event()` emits `freeSpinTrigger` event

---

### Base → Superbonus

**Trigger**: **4 scatters** from base game

**Awards**: **10 free spins** (same as regular bonus)

**Reelset**: `FR1.csv` (superbonus reelset)

**Code Reference**: `game_override.py`, lines 65-72

**Process**:
1. `check_fs_condition()` detects 4 scatters
2. `run_freespin_from_base()` is called
3. `is_superbonus_from_scatter = True` (enables superbonus behavior)
4. Reelset switched to `FR1.csv`
5. `update_freespin_amount()` sets `tot_fs = 10` (overridden for superbonus)
6. `fs_trigger_event()` emits `freeSpinTrigger` event

**Special Protection**: Regular bonus buy (`betmode == "bonus"`) **never triggers superbonus**, even if 4 scatters land (lines 61-67)

---

### Retriggers (During Free Spins)

**Location**: `game_config.py`, line 117

**Triggers**:
- **2 scatters** = +2 free spins
- **3 scatters** = +3 free spins
- **4 scatters** = +8 free spins
- **5 scatters** = **NOT POSSIBLE** (max 4 scatters enforced)

**Code Reference**: `gamestate.py`, lines 33-34

**Process**:
1. During free spins, `check_fs_condition()` detects 2+ scatters
2. `update_fs_retrigger_amt()` is called
3. Additional spins added to `tot_fs`
4. `fs_trigger_event()` emits `freeSpinRetrigger` event (not `freeSpinTrigger`)

---

### Event Emission

**Location**: `src/events/events.py` → `fs_trigger_event()` (lines 45-77)

**Events Emitted**:

1. **freeSpinTrigger** (from base game):
   - **When**: 3 or 4 scatters from base game
   - **Fields**: `totalFs`, `positions` (scatter positions)
   - **Code**: `fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)`

2. **freeSpinRetrigger** (during free spins):
   - **When**: 2, 3, or 4 scatters during free spins
   - **Fields**: `totalFs` (updated total), `positions` (scatter positions)
   - **Code**: `fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)`

**Position Format**: Scatter positions include padding offset (+1 row) if `include_padding_index=True`

**Code Reference**: `game_override.py`, lines 103-119 (superbonus override), `src/executables/executables.py`, lines 72-84 (default behavior)

---

## 3.6 Win Caps and Wincap Behavior

### Global Max Win Cap

**Location**: `game_config.py`, line 24

**Value**: **10,000× bet**

**Configuration**:
```python
self.wincap = 10000.0
```

**Applied To**: All bet modes (base, bonus, superbonus)

**Enforcement**: Applied in multiple places:
- `src/events/events.py` → `win_info_event()` (line 152): Caps individual win amounts
- `src/events/events.py` → `set_win_event()` (line 89): Caps spin win amounts
- `src/events/events.py` → `set_total_event()` (line 104): Caps running bet win amounts
- `src/events/events.py` → `final_win_event()` (line 213): Caps final win amounts

**Code Pattern**:
```python
min(win_amount, gamestate.config.wincap) * 100  # Convert to cents
```

---

### VS Combined Multiplier Cap

**Location**: `game_executables.py`, line 178

**Value**: **500×** (increased from 250× to allow max win of 10,000× bet)

**Configuration**:
```python
# Cap at 500× (increased from 250× to allow max win of 10,000× bet)
if combined_mult > 500:
    combined_mult = 500
```

**Applied To**: Combined VS multipliers across multiple reels in a single winning line

**Example**: If a line uses 3 VS reels with multipliers [10×, 10×, 10×], the combined multiplier would be 1,000×, but it's capped at 500×.

**Code Reference**: `game_executables.py` → `calculate_vs_line_multiplier()` (lines 158-181)

---

### Wincap Criteria and Measurement

**Location**: `game_config.py`, lines 215-229

**Wincap Condition**:
```python
wincap_condition = {
    "reel_weights": {
        self.basegame_type: {"BR0": 1},
        self.freegame_type: {"FR0": 1, "WCAP": 5},  # FRWCAP.csv has 5× weight
    },
    "mult_values": {
        self.basegame_type: {1: 1},
        self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 60, 10: 100, 20: 90, 50: 50},
    },
    "scatter_triggers": {4: 1},  # Removed 5-scatter case (max 4 scatters)
    "force_wincap": True,
    "force_freegame": True,
}
```

**Usage**: Included in all bet modes with **0.1% quota**:
```python
Distribution(
    criteria="wincap", 
    quota=0.001,  # 0.1%
    win_criteria=self.wincap,  # 10,000×
    conditions=wincap_condition
)
```

**Purpose**: Forces max win scenarios for testing and RTP validation

**Measurement**: 
- Wincap is measured as total win across all lines and multipliers
- Warning "High repeat count: Criteria: wincap" indicates the simulation is trying to force a 10,000× win but failing (likely due to reel/multiplier constraints)

---

### FRWCAP Reelset Usage

**Location**: `game_config.py`, line 220

**Frequency**: Only used in `wincap_condition` distribution (0.1% of spins)

**Weight**: 5× (vs FR0 weight: 1) when used in freegame

**Purpose**: Forces max win scenarios by:
- Using high-value multipliers in `mult_values`
- Using optimized reel strip (FRWCAP.csv) with favorable symbol distribution
- Forcing freegame trigger (`force_freegame: True`)

**Normal Sims**: FRWCAP.csv is **NOT used** in normal simulations (only in wincap condition)

---

## 3.7 RTP / Simulation Tools (Backend View)

### Simulation Execution

**Entry Point**: `games/1_0_gunslingers/run.py`

**Process**:
1. Loads `GameConfig` (singleton)
2. Iterates through `bet_modes` (base, bonus, superbonus)
3. For each bet mode, runs simulations based on distributions
4. Generates book files (`.jsonl.zst`) and lookup tables (`.csv`)

**Command**: `make run GAME=1_0_gunslingers`

---

### RTP Calculation

**Location**: `utils/analysis/distribution_functions.py` → `calculate_rtp()`

**Method**: Uses lookup tables (LUTs) to calculate weighted RTP

**Process**:
1. **Lookup Table Format**: CSV file with columns: `win_amount, weight`
2. **RTP Formula**: `RTP = (sum of win_amount × weight) / (sum of weights × cost)`
3. **Weighted Average**: Accounts for distribution quotas and forced conditions

**Code Reference**: `game_stats_summary.py`, lines 124-125

---

### Statistics Calculation

**Location**: `games/1_0_gunslingers/game_stats_summary.py`

**Functions**:

1. **`calculate_mode_statistics()`** (lines 100-185):
   - Calculates RTP, hit rate, average win from lookup tables
   - Analyzes VS statistics from book files
   - Returns comprehensive statistics dict

2. **`analyze_books_for_vs_stats()`** (lines 14-97):
   - Parses book files (`.jsonl.zst`) to extract VS usage
   - Tracks: spins with VS, VS reels per spin, VS multipliers
   - Returns VS statistics dict

3. **`print_rtp_summary()`** (lines 188-234):
   - Prints formatted RTP summary for all modes
   - Includes RTP, hit rate, VS statistics, feature statistics

**Output**: Console output + `library/statistics_summary.json` (if generated)

---

### Target RTP Per Mode

**Location**: `game_config.py`, line 26

**Target**: **96.2%** for all modes

**Enforcement**:
- **Base Game**: Achieved via reel tuning and distribution quotas
- **Bonus Buy**: Achieved via VS multiplier distribution tuning (target: 96.2× avg feature win at 100× cost)
- **Superbonus Buy**: Achieved via superbonus VS multiplier distribution tuning (target: 384.8× avg feature win at 400× cost)

**Current Status** (from `RTP_ANALYSIS.md`):
- Base Game: **96.2%** ✅
- Bonus: **96.2%** ✅
- Superbonus: **96.2%** ✅

---

### Game-Specific Assumptions

1. **VS Multiplier Tuning**: VS multiplier distributions are tuned to achieve target RTP:
   - Regular bonus: Average ~2.425× multiplier
   - Superbonus: Average ~2.425× multiplier (slightly higher high-tier weights)

2. **Distribution Quotas**: Base game uses forced distributions to balance RTP:
   - 10% freegame quota (forces bonus triggers)
   - 40% zerowin quota (forces zero-win spins)
   - 50% basegame quota (normal spins)

3. **Reel Tuning**: Reel strips are tuned to achieve:
   - Base game: ~38-42% RTP contribution
   - Bonus: ~58-62% RTP contribution
   - Combined: 96.2% total RTP

---

## 4. Compare Backend Behavior vs Frontend Expectations

### Frontend Integration Guide Summary

Based on the frontend integration guide in `apps/gunslingers/docs/math-sdk-frontend-integration.md`:

| Expectation | Frontend Value |
|-------------|----------------|
| **Grid** | 5×3 layout |
| **Paylines** | 20 fixed lines |
| **Max Win** | 10,000× bet |
| **Bonus Cost** | 100× bet |
| **Super Bonus Cost** | 250× bet (per user guide) / 400× bet (per frontend code) |
| **Scatter Triggers** | 3 scatters = bonus, 4 scatters = superbonus (no 5 scatters) |
| **Free Spins** | 10 for both bonuses |
| **VS Multiplier Cap** | 250× (per user guide) / 500× (per backend code) |
| **Win Levels** | Keys: 1-10 (aliases: big=6, super=7, mega=8, max=10) |

---

### Mismatches and Potential Desyncs

#### 1. Paylines Count Mismatch

**Issue**: Backend uses **10 paylines**, frontend expects **20 paylines**

**Backend**: `game_config.py`, lines 79-100 defines 10 paylines (lines 1-10)

**Frontend**: `apps/gunslingers/src/game/config.ts`, lines 31-52 defines 20 paylines (lines 1-20)

**Impact**: 
- Frontend will evaluate 20 lines, but backend only provides wins for 10 lines
- Frontend lines 11-20 will never have wins
- This is a **critical desync**

**Recommendation**: **Change backend** to add 10 more paylines (lines 11-20) matching frontend definitions

---

#### 2. Super Bonus Cost Mismatch

**Issue**: Backend uses **400× bet**, frontend guide says **250× bet**, but frontend code shows **400× bet**

**Backend**: `game_config.py`, line 301: `cost=400.0`

**Frontend Guide**: User guide says 250× bet

**Frontend Code**: `apps/gunslingers/src/game/betModeMeta.ts`, line 62: `costMultiplier: 400`

**Impact**: 
- Frontend code matches backend (400×)
- User guide is outdated
- **No desync** (frontend code is correct)

**Recommendation**: **Update user guide** to reflect 400× bet cost

---

#### 3. VS Multiplier Cap Mismatch

**Issue**: Backend caps at **500×**, frontend guide says **250×**, but frontend code may expect different

**Backend**: `game_executables.py`, line 178: `if combined_mult > 500: combined_mult = 500`

**Frontend Guide**: Says 250× cap

**Frontend Code**: Need to verify frontend expectations

**Impact**: 
- If frontend expects 250× cap, wins above 250× will be incorrect
- Backend comment says "increased from 250× to allow max win of 10,000× bet"
- **Potential desync** if frontend doesn't handle 500× cap

**Recommendation**: **Verify frontend code** to confirm expected cap, then align backend/frontend

---

#### 4. Scatter Count Alignment

**Status**: **✅ ALIGNED**

**Backend**: Max 4 scatters (enforced in BR0.csv and code)

**Frontend**: Clamps at 4 scatters (`scatterLandIndex()`)

**Impact**: No desync

---

#### 5. Free Spin Counts

**Status**: **✅ ALIGNED**

**Backend**: 
- 3 scatters = 10 FS
- 4 scatters = 10 FS (superbonus)
- Retriggers: 2=+2, 3=+3, 4=+8

**Frontend**: Expects `totalFs = 10` for both bonuses

**Impact**: No desync

---

#### 6. Win Level Keys

**Status**: **✅ ALIGNED**

**Backend**: Uses numeric keys 1-10 (from `config.get_win_level()`)

**Frontend**: `winLevelMap.ts` defines keys 1-10 with aliases (big=6, super=7, mega=8, max=10)

**Impact**: No desync (frontend maps numeric keys to aliases)

---

#### 7. Symbol Metadata Fields

**Status**: **✅ MOSTLY ALIGNED**

**Backend Provides**:
- `name`: Symbol identifier (e.g., "H1", "VS", "W")
- `multiplier`: Multiplier value (for W and VS)
- `wild`: Boolean (for W and VS)
- `underlyingSymbol`: String (for VS covering scatters)

**Frontend Expects**:
- `name`: ✅
- `multiplier`: ✅
- `wild`: ✅
- `underlyingSymbol`: ✅
- `revealed`, `specialType`: Optional (backend may not provide)

**Impact**: No desync (frontend handles optional fields)

---

#### 8. Event Structure

**Status**: **✅ ALIGNED**

**Backend Emits**:
- `reveal`: Board array with symbol metadata ✅
- `winInfo`: Wins, positions, amount, winLevel ✅
- `freeSpinTrigger`: Positions, totalFs ✅
- `updateFreeSpin`: amount (0-based index), total ✅
- `freeSpinEnd`: Total win, winLevel ✅

**Frontend Expects**: Same events with same fields

**Impact**: No desync

---

#### 9. VS Multiplier Persistence After Expansion

**Status**: **⚠️ POTENTIAL ISSUE**

**Backend Behavior**:
- VS multipliers are assigned **before** reveal event
- VS symbols are expanded to wilds **after** reveal event
- Expanded wilds are `W` symbols (not VS)
- Multipliers are stored in `self.vs_reel_multipliers` (not on symbols)

**Frontend Expectation**: 
- Frontend guide says "Math must carry multipliers on the final wilds"
- Frontend `detectAndTriggerVsReels()` converts VS to wilds using math-provided multipliers

**Impact**: 
- If frontend expects multipliers on expanded wilds, they may be missing
- Backend stores multipliers separately and applies them to wins
- **Potential desync** if frontend needs multipliers on wild symbols themselves

**Recommendation**: **Verify frontend code** to confirm if multipliers need to be on wild symbols or if separate storage is acceptable

---

#### 10. Game Type Emission

**Status**: **✅ ALIGNED**

**Backend**: Emits `gameType: "basegame"` or `"freegame"` in reveal events

**Frontend**: Expects `gameType` field

**Impact**: No desync

---

### Summary of Required Changes

| Priority | Issue | Action | File(s) to Change |
|----------|-------|--------|------------------|
| **CRITICAL** | Paylines count (10 vs 20) | Add 10 more paylines to backend | `game_config.py` |
| **HIGH** | VS multiplier cap (250× vs 500×) | Verify frontend expectations, align | `game_executables.py` or frontend |
| **MEDIUM** | VS multiplier persistence | Verify frontend needs multipliers on wilds | `game_executables.py` or frontend |
| **LOW** | Super bonus cost (250× vs 400×) | Update user guide | Documentation |

---

## 5. Output Format

This document is structured as a single, well-organized markdown file with:

- **Clear headings** and subheadings
- **Tables** for structured data
- **Code references** with file paths and line numbers
- **Comparison section** highlighting mismatches
- **Actionable recommendations** for each issue

The document can be used as:
- **Backend implementation reference** for developers
- **Frontend-backend sync checklist** for QA
- **Blueprint for math tuning** and optimization
- **Documentation for future modifications**

---

**End of Documentation**

