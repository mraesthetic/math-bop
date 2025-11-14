# Gunslingers: DRAW! — Complete Math Documentation

## Table of Contents
1. [Game Structure](#game-structure)
2. [Symbols & Paytables](#symbols--paytables)
3. [Reelsets](#reelsets)
4. [Paylines](#paylines)
5. [Win Calculation System](#win-calculation-system)
6. [VS (DRAW) Symbol Mechanics](#vs-draw-symbol-mechanics)
7. [Wild (W) Symbol Mechanics](#wild-w-symbol-mechanics)
8. [Scatter & Bonus Triggers](#scatter--bonus-triggers)
9. [Bet Modes & RTP Structure](#bet-modes--rtp-structure)
10. [Multiplier Systems](#multiplier-systems)
11. [Win Cap & Max Win](#win-cap--max-win)

---

## Game Structure

### Dimensions
- **Reels**: 5
- **Rows**: 3 (all reels)
- **Layout**: 5×3 grid
- **Paylines**: 10 fixed lines
- **Win Type**: Lines-based evaluation

### Game Flow
1. Board draw (with padding symbols)
2. VS symbol injection (superbonus only)
3. VS multiplier assignment
4. Reveal event (board shown to player)
5. VS reel expansion (for evaluation)
6. Line evaluation
7. Win calculation with multipliers
8. Scatter checking
9. Free spin triggers

---

## Symbols & Paytables

### Regular Paying Symbols

#### Premium Symbols (High)
- **H1 (BANDIT GUY)**
  - 5 of a kind: 25× bet
  - 4 of a kind: 6× bet
  - 3 of a kind: 2× bet

- **H2 (BANDIT GIRL)**
  - 5 of a kind: 18× bet
  - 4 of a kind: 5× bet
  - 3 of a kind: 1.5× bet

- **H3 (SHOTGUN)**
  - 5 of a kind: 14× bet
  - 4 of a kind: 4× bet
  - 3 of a kind: 1.2× bet

- **H4 (WHISKEY)**
  - 5 of a kind: 10× bet
  - 4 of a kind: 3× bet
  - 3 of a kind: 1× bet

#### Low Symbols
- **L1 (A)**
  - 5 of a kind: 5× bet
  - 4 of a kind: 1.5× bet
  - 3 of a kind: 0.5× bet

- **L2 (K)**
  - 5 of a kind: 4× bet
  - 4 of a kind: 1.2× bet
  - 3 of a kind: 0.4× bet

- **L3 (Q)**
  - 5 of a kind: 3.5× bet
  - 4 of a kind: 1× bet
  - 3 of a kind: 0.3× bet

- **L4 (J)**
  - 5 of a kind: 3× bet
  - 4 of a kind: 0.8× bet
  - 3 of a kind: 0.2× bet

- **L5 (10)**
  - 5 of a kind: 2.5× bet
  - 4 of a kind: 0.6× bet
  - 3 of a kind: 0.2× bet

### Special Symbols

#### W (WILD)
- **Paytable**: Has own paytable entries (5=20×, 4=10×, 3=5×)
- **Substitution**: Substitutes for all regular symbols (not scatter)
- **Wild Property**: `wild: true`
- **Multiplier Property**: `multiplier: true`
- **Multiplier Distribution**: Only in freegame mode (see Multiplier Systems)

#### VS (DRAW)
- **Paytable**: No paytable entries (expanding wild only)
- **Substitution**: Substitutes for all regular symbols (not scatter)
- **Wild Property**: `wild: true`
- **Multiplier Property**: `multiplier: true`
- **Expanding Behavior**: Entire reel expands to wild when VS appears
- **Multiplier Distribution**: Different for base/bonus vs superbonus
- **Special Attribute**: `underlyingSymbol: "S"` (only in superbonus when forced over scatter)

#### S (SCATTER)
- **Paytable**: No paytable entries
- **Trigger**: Triggers free spins (see Scatter & Bonus Triggers)
- **Substitution**: Cannot be substituted by wilds
- **Scatter Property**: `scatter: true`

---

## Reelsets

### BR0.csv (Base Game)
- **Usage**: Base game spins
- **Reelset**: 220 lines (5 reels × 44 symbols per reel typical)
- **VS Frequency**: Very rare (1-3 VS total across all reels)
- **Scatter Frequency**: Tuned for ~1/150 base game trigger rate
- **Symbol Mix**: Balanced for base game RTP ~38-42%

### FR0.csv (DRAW! YOUR WEAPON Bonus)
- **Usage**: Free spins in regular bonus mode
- **Reelset**: Similar length to BR0
- **VS Frequency**: 3-5 VS per reel (higher density than base)
- **Scatter Frequency**: Tuned for retrigger mechanics
- **Symbol Mix**: Enhanced for bonus RTP ~56-58%

### FR1.csv (SUPER DRAW! Bonus)
- **Usage**: Free spins in superbonus mode
- **Reelset**: Similar length to BR0/FR0
- **VS Frequency**: 6-8 VS per reel (highest density)
- **Scatter Frequency**: Controlled (forced 3 scatters = 10 spins on entry)
- **Symbol Mix**: Enhanced for superbonus RTP ~0.015 (additive to base)
- **Guarantee**: At least 1 VS reel per spin (forced if none naturally)

### FRWCAP.csv (Win Cap)
- **Usage**: Win cap condition (very rare)
- **Reelset**: Optimized to hit max win scenarios
- **Frequency**: 0.1% of spins in base/bonus modes

---

## Paylines

10 fixed paylines (left-to-right only):

1. **Line 1**: Top row `[0, 0, 0, 0, 0]`
2. **Line 2**: Middle row `[1, 1, 1, 1, 1]`
3. **Line 3**: Bottom row `[2, 2, 2, 2, 2]`
4. **Line 4**: V-down `[0, 1, 2, 1, 0]`
5. **Line 5**: V-up `[2, 1, 0, 1, 2]`
6. **Line 6**: Zigzag down `[0, 0, 1, 1, 2]`
7. **Line 7**: Zigzag up `[2, 2, 1, 1, 0]`
8. **Line 8**: Step down `[0, 1, 1, 1, 2]`
9. **Line 9**: Step up `[2, 1, 1, 1, 0]`
10. **Line 10**: Wave `[0, 1, 0, 1, 0]`

**Evaluation**: Each line evaluated independently. Wins on multiple lines are summed.

---

## Win Calculation System

### Line Evaluation Process

1. **Board State**: After VS expansion (see VS Mechanics)
2. **Line Iteration**: Each of 10 paylines evaluated
3. **Symbol Matching**: Left-to-right matching from reel 0
4. **Wild Substitution**: W and VS (expanded) substitute for regular symbols
5. **Match Count**: Count consecutive matching symbols
6. **Paytable Lookup**: `(match_count, symbol_name)` → win amount
7. **Multiplier Application**: VS reel multipliers applied (see Multiplier Systems)
8. **Win Aggregation**: Sum all line wins

### Line Matching Logic

```python
# Simplified pseudo-code
for each payline:
    line_symbols = [board[reel][payline[reel]] for reel in range(5)]
    
    # Find first non-wild symbol
    first_non_wild = find_first_non_wild(line_symbols)
    
    # Count matches (wilds substitute)
    matches = count_consecutive_matches(line_symbols, first_non_wild)
    
    # Check paytable
    if (matches, first_non_wild) in paytable:
        base_win = paytable[(matches, first_non_wild)]
        
        # Apply VS multipliers
        vs_mult = calculate_vs_multiplier(line_positions)
        final_win = base_win * vs_mult
```

### Wild vs Regular Win Priority

- If a line has both wild-only wins and regular symbol wins:
  - **Wild win**: Uses first wild symbol (W or expanded VS)
  - **Regular win**: Uses first non-wild symbol
  - **Highest win wins**: The larger of the two is awarded

---

## VS (DRAW) Symbol Mechanics

### VS Appearance & Expansion

1. **Board Draw**: VS symbols can land naturally from reelset
2. **Superbonus Forcing**: In superbonus mode, exactly 1 VS reel guaranteed per spin
3. **Expansion**: When VS appears, entire reel expands to wild (W symbols)
4. **Multiplier Assignment**: Each VS reel gets a random multiplier (see Multiplier Systems)

### VS Reel Detection

```python
# For each reel
if any symbol in reel is "VS":
    mark reel as VS reel
    assign multiplier to entire reel
    expand all positions in reel to "W"
```

### VS Multiplier Application

- **Per Reel**: Each VS reel gets ONE multiplier (same for all positions)
- **Line Calculation**: If a winning line uses multiple VS reels, multipliers multiply
- **Example**: 
  - Line uses reel 2 (VS, 3×) and reel 4 (VS, 5×)
  - Combined multiplier = 3 × 5 = 15×
- **Cap**: Total combined multiplier capped at 250×

### VS Multiplier Distribution

#### Regular Bonus (FR0.csv)
```python
{2: 750, 3: 200, 4: 70, 5: 30, 8: 7, 10: 3}
# Total weight: 1060
# Probabilities:
#   2×: 750/1060 ≈ 70.8%
#   3×: 200/1060 ≈ 18.9%
#   4×: 70/1060 ≈ 6.6%
#   5×: 30/1060 ≈ 2.8%
#   8×: 7/1060 ≈ 0.7%
#   10×: 3/1060 ≈ 0.3%
```

#### Super DRAW! (FR1.csv)
```python
{2: 700, 3: 250, 4: 40, 5: 15, 8: 4, 10: 1}
# Total weight: 1010
# Probabilities:
#   2×: 700/1010 ≈ 69.3%
#   3×: 250/1010 ≈ 24.8%
#   4×: 40/1010 ≈ 4.0%
#   5×: 15/1010 ≈ 1.5%
#   8×: 4/1010 ≈ 0.4%
#   10×: 1/1010 ≈ 0.1%
```

### Superbonus VS Guarantee Logic

**In superbonus mode, during free spins only:**

1. **Count VS Reels**: Check how many reels have VS symbols naturally
2. **If 0 VS Reels**: Force exactly 1 VS on random reel at random position
   - Track original symbol at that position
   - If original was scatter (`S`), set `underlyingSymbol: "S"` on VS symbol
3. **If 1 VS Reel**: Keep as-is (perfect)
4. **If 2+ VS Reels**: Keep first, remove VS from others (replace with L1)

**Important**: VS forcing only happens during free spins, NOT on the basegame trigger spin.

### VS Underlying Symbol

**Purpose**: Frontend needs to know if VS was forced over a scatter for visual display.

**When Set**: Only in superbonus mode, when VS is forced and original symbol was scatter.

**JSON Output**:
```json
{
  "name": "VS",
  "multiplier": 5,
  "wild": true,
  "underlyingSymbol": "S"  // Only when forced over scatter
}
```

---

## Wild (W) Symbol Mechanics

### W Symbol Behavior

- **Base Game**: W acts as regular wild (substitutes, has paytable)
- **Free Spins**: W gets multipliers (see Multiplier Systems)
- **Substitution**: W substitutes for all regular symbols (not scatter)
- **Multiplier Assignment**: Only in freegame mode, via `assign_mult_property()`

### W Multiplier Distribution (Freegame Only)

```python
{
    2: 60,
    3: 80,
    4: 50,
    5: 20,
    10: 15,
    20: 10,
    50: 5
}
# Total weight: 240
# Applied per W symbol independently
```

### W Multiplier Application

- **Per Symbol**: Each W symbol gets its own multiplier
- **Line Calculation**: Uses "symbol" multiplier method (additive)
  - If line has W symbols with multipliers [2, 3, 5]:
  - Combined multiplier = 2 + 3 + 5 = 10×
- **No Cap**: W multipliers are additive, not multiplicative

---

## Scatter & Bonus Triggers

### Scatter Symbol (S)

- **Appearance**: Can appear on any reel, any position
- **No Substitution**: Cannot be substituted by wilds
- **Trigger Only**: Does not pay on lines (no paytable entry)

### Free Spin Triggers

#### Base Game Triggers
```python
{
    3 scatters: 10 free spins
    4 scatters: 12 free spins
    5 scatters: 15 free spins
}
```

#### Free Spin Retriggers
```python
{
    2 scatters: +2 free spins
    3 scatters: +3 free spins
    4 scatters: +8 free spins
    5 scatters: +12 free spins
}
```

### Scatter Frequency Control

#### Base Game (BR0.csv)
- **Target**: ~1/150 spins trigger bonus
- **Distribution**: 3-4 scatters total across 5 reels typically
- **Optimization**: Tuned via reelstrips

#### Bonus (FR0.csv)
- **Retrigger Rate**: Tuned for reasonable retrigger frequency
- **Distribution**: Controlled via reelstrips

#### Superbonus (FR1.csv)
- **Entry**: Always forces exactly 3 scatters = 10 spins (via `scatter_triggers: {3: 100}`)
- **During Spins**: Natural scatter frequency (can retrigger)

### Anticipation Triggers

- **Base Game**: 2+ scatters (anticipation animation)
- **Free Spins**: 1+ scatter (anticipation for retrigger)

---

## Bet Modes & RTP Structure

### Target RTP
- **Total RTP**: 96.2% (0.962)
- **Base Game RTP**: ~38-42% (0.38-0.42)
- **Bonus RTP**: ~56-58% (0.56-0.58)
- **Superbonus RTP**: ~0.015 (additive)
- **Total**: 0.39 + 0.57 + 0.015 ≈ 0.962

### Bet Mode 1: Base

**Cost**: 1× bet  
**Type**: Normal play  
**Features**: Can trigger bonus naturally

**Distributions**:
- **Wincap** (0.1%): Forces max win scenario
- **Freegame** (10%): Triggers bonus feature
- **Zero Win** (40%): Forces zero win spins
- **Basegame** (50%): Normal base game spins

**RTP Contribution**: ~0.39

### Bet Mode 2: Bonus (DRAW! YOUR WEAPON)

**Cost**: 100× bet  
**Type**: Feature buy  
**Buy Bonus**: Yes

**Distributions**:
- **Wincap** (0.1%): Forces max win scenario
- **Freegame** (99.9%): Guarantees bonus feature

**Reelset**: FR0.csv (3-5 VS per reel)  
**RTP Contribution**: ~0.571 (per optimization config)

### Bet Mode 3: Superbonus (SUPER DRAW!)

**Cost**: 400× bet  
**Type**: Feature buy  
**Buy Bonus**: Yes

**Distributions**:
- **Wincap** (0.1%): Forces max win scenario
- **Freegame** (99.9%): Guarantees superbonus feature

**Reelset**: FR1.csv (6-8 VS per reel)  
**Special**: Guarantees 1 VS reel per spin  
**Entry**: Always 3 scatters = 10 spins  
**RTP Contribution**: ~0.961 (per optimization config, but actual target ~0.015 additive)

---

## Multiplier Systems

### Multiplier Types

1. **W Symbol Multipliers** (freegame only)
   - Method: Additive per symbol
   - Distribution: See W Symbol Mechanics
   - Application: Applied to line wins using "symbol" method

2. **VS Reel Multipliers** (base + bonus)
   - Method: Multiplicative per reel
   - Distribution: Different for bonus vs superbonus
   - Application: Multiplied together, capped at 250×

### Multiplier Strategy

**Method**: `multiplier_method="symbol"`

**Logic**:
```python
# For a winning line
line_multiplier = 1

# For each position in line
for position in line_positions:
    if symbol has multiplier attribute:
        if symbol is VS (expanded to W):
            # VS multipliers are multiplicative
            # But applied per reel, not per symbol
            # (handled separately in calculate_vs_line_multiplier)
        else if symbol is W:
            # W multipliers are additive
            line_multiplier += symbol.multiplier - 1

# VS multipliers applied separately
vs_mult = calculate_vs_line_multiplier(line_positions)
final_win = base_win * vs_mult * line_multiplier
```

### VS Multiplier Calculation

```python
def calculate_vs_line_multiplier(line_positions):
    # Get unique reels used in line
    reels_in_line = set(pos["reel"] for pos in line_positions)
    
    # Multiply multipliers from VS reels
    combined_mult = 1
    for reel_idx in reels_in_line:
        if reel_idx in vs_reel_multipliers:
            combined_mult *= vs_reel_multipliers[reel_idx]
    
    # Cap at 250×
    if combined_mult > 250:
        combined_mult = 250
    
    return combined_mult
```

### Example Win Calculation

**Scenario**: Line wins with 5 of a kind H1 (Bandit Guy), line uses reels 1, 2, 3, 4, 5
- Reel 2 has VS with 3× multiplier
- Reel 4 has VS with 5× multiplier
- Reel 3 has W with 2× multiplier

**Calculation**:
1. Base win: 25× (5 of a kind H1)
2. VS multiplier: 3 × 5 = 15× (reels 2 and 4)
3. W multiplier: +1× (from reel 3's W, but additive method)
4. Final win: 25 × 15 = 375× (W multiplier handled separately if applicable)

**Note**: W and VS multipliers are handled separately in the current implementation.

---

## Win Cap & Max Win

### Win Cap
- **Cap Amount**: 5000× bet
- **Enforcement**: Applied after all win calculations
- **Scenarios**: 
  - Theoretical max: ~25000× (5× H1 × 10 lines × 250× VS multiplier cap)
  - Actual cap: 5000× bet

### Max Win Scenarios

**Theoretical Maximum** (before cap):
- 5 of a kind H1 (Bandit Guy) on all 10 lines = 25× × 10 = 250×
- 3 VS reels with 10×, 10×, 10× = 1000×
- Raw total: 250× × 1000× = 250,000×
- **Capped at**: 5000×

**Practical Maximum**:
- More realistic VS multiplier combinations
- Example: 5×, 5×, 4× = 100×
- 250× (line wins) × 100× (VS) = 25,000× → **Capped at 5000×**

### Win Cap Condition

**Distribution**: 0.1% of spins in base/bonus modes  
**Reelset**: FRWCAP.csv  
**Purpose**: Ensure max win scenarios are reachable for testing/verification

---

## Implementation Details

### File Structure

- **game_config.py**: Configuration (paytables, reelsets, bet modes)
- **game_executables.py**: VS mechanics, win calculation, board drawing
- **game_override.py**: Special symbol functions, free spin triggers
- **game_calculations.py**: Inherits from Executables (base class)
- **game_optimization.py**: Optimization parameters for RTP tuning

### Key Functions

1. **draw_board()**: Overrides board drawing to inject VS in superbonus
2. **expand_vs_reels()**: Expands VS reels to wilds before evaluation
3. **calculate_vs_line_multiplier()**: Calculates VS multipliers for a line
4. **evaluate_lines_board()**: Main win evaluation with VS multiplier application
5. **update_freespin_amount()**: Handles superbonus entry (always 10 spins)

### Event Flow

1. **reveal_event**: Board shown to player (includes VS with multipliers)
2. **win_info_event**: Winning lines displayed
3. **fs_trigger_event**: Free spins triggered
4. **set_total_event**: Final win amount

---

## Optimization Targets

### Base Mode Optimization
- **RTP**: 0.39
- **Hit Rate**: 3.5 (any win)
- **Bonus Trigger**: 200 (1/200 spins)

### Bonus Mode Optimization
- **RTP**: 0.961
- **Feature Win**: 200-350× bet average
- **Hit Rate**: Variable

### Superbonus Mode Optimization
- **RTP**: 0.961
- **Feature Win**: 200-350× bet average
- **Hit Rate**: Variable

---

## Expansion Points

### Easy Modifications

1. **Paytable Values**: Modify `self.paytable` in `game_config.py`
2. **VS Multiplier Distribution**: Modify `self.padding_symbol_values["VS"]` or `self.superbonus_vs_multipliers`
3. **Free Spin Counts**: Modify `self.freespin_triggers`
4. **Reelstrips**: Edit CSV files in `reels/` directory
5. **Paylines**: Modify `self.paylines` (add/remove lines)

### Advanced Modifications

1. **VS Cap**: Change 250× cap in `calculate_vs_line_multiplier()`
2. **VS Expansion Logic**: Modify `expand_vs_reels()` for different expansion patterns
3. **Multiplier Strategy**: Change from "symbol" to "board" or "global"
4. **Win Cap**: Modify `self.wincap` (affects max win and optimization)
5. **New Special Symbols**: Add to `self.special_symbols` and implement logic

### Complex Modifications

1. **New Bonus Mode**: Add new BetMode with custom reelset and conditions
2. **VS Behavior Changes**: Modify when/how VS expands (e.g., only on certain reels)
3. **Multiplier Interactions**: Change how W and VS multipliers combine
4. **Scatter Pay**: Add scatter paytable entries
5. **Retrigger Logic**: Modify retrigger conditions and spin counts

---

## Testing & Validation

### Key Metrics

1. **RTP**: Should be ~0.962 total
2. **Base RTP**: ~0.38-0.42
3. **Bonus RTP**: ~0.56-0.58
4. **Max Win**: Should not exceed 5000× bet
5. **VS Appearance**: Base <1%, Bonus 3-5/reel, Superbonus 6-8/reel + 1 guaranteed
6. **Bonus Trigger Rate**: ~1/150 base spins

### Simulation Commands

```bash
# Run full simulation
make run GAME=1_0_gunslingers

# Check statistics
cat math-sdk/games/1_0_gunslingers/library/stats_summary.json
```

---

**Last Updated**: 2024  
**Game Version**: 1_0_gunslingers  
**Math SDK Version**: As per parent framework

