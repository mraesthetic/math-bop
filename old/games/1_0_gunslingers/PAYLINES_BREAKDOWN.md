# Gunslingers: DRAW! — Paylines Breakdown (Math-SDK)

**Source**: `games/1_0_gunslingers/game_config.py` (lines 78-100)  
**Date**: Generated from math-sdk codebase analysis

---

## Summary

- **Total Paylines**: **10 fixed paylines**
- **Grid Size**: 5 reels × 3 rows
- **Indexing**: 0-based (0 = top row, 1 = middle row, 2 = bottom row)
- **Evaluation Direction**: Left-to-right only
- **Configurability**: Fixed (hardcoded in `game_config.py`)
- **Alignment**: Fully aligned with `Lines.get_lines()` logic

---

## Detailed Payline Definitions

### Line 1: Straight Top Row

| Property | Value |
|----------|-------|
| **Line ID** | 1 |
| **Row Positions** | `[0, 0, 0, 0, 0]` |
| **Visual Description** | Straight top row (all reels, top position) |
| **Shape Name** | Straight top |
| **Visual Pattern** | `─ ─ ─ ─ ─` (all top) |

**Code Reference**: `game_config.py`, line 81

---

### Line 2: Straight Middle Row

| Property | Value |
|----------|-------|
| **Line ID** | 2 |
| **Row Positions** | `[1, 1, 1, 1, 1]` |
| **Visual Description** | Straight middle row (all reels, middle position) |
| **Shape Name** | Straight middle |
| **Visual Pattern** | `─ ─ ─ ─ ─` (all middle) |

**Code Reference**: `game_config.py`, line 83

---

### Line 3: Straight Bottom Row

| Property | Value |
|----------|-------|
| **Line ID** | 3 |
| **Row Positions** | `[2, 2, 2, 2, 2]` |
| **Visual Description** | Straight bottom row (all reels, bottom position) |
| **Shape Name** | Straight bottom |
| **Visual Pattern** | `─ ─ ─ ─ ─` (all bottom) |

**Code Reference**: `game_config.py`, line 85

---

### Line 4: V-Shape Down

| Property | Value |
|----------|-------|
| **Line ID** | 4 |
| **Row Positions** | `[0, 1, 2, 1, 0]` |
| **Visual Description** | V-shape pointing down (top → middle → bottom → middle → top) |
| **Shape Name** | V-shape down |
| **Visual Pattern** | `\ / \` (downward V) |

**Code Reference**: `game_config.py`, line 87  
**Comment**: "V shape down (1-2-3-2-1)"

---

### Line 5: V-Shape Up

| Property | Value |
|----------|-------|
| **Line ID** | 5 |
| **Row Positions** | `[2, 1, 0, 1, 2]` |
| **Visual Description** | V-shape pointing up (bottom → middle → top → middle → bottom) |
| **Shape Name** | V-shape up |
| **Visual Pattern** | `/ \ /` (upward V) |

**Code Reference**: `game_config.py`, line 89  
**Comment**: "V shape up (3-2-1-2-3)"

---

### Line 6: Zigzag Down

| Property | Value |
|----------|-------|
| **Line ID** | 6 |
| **Row Positions** | `[0, 0, 1, 1, 2]` |
| **Visual Description** | Zigzag pattern moving down (top-top → middle-middle → bottom) |
| **Shape Name** | Zigzag down |
| **Visual Pattern** | `─ ─ \ \` (stepping down) |

**Code Reference**: `game_config.py`, line 91  
**Comment**: "zigzag down (1-1-2-2-3)"

---

### Line 7: Zigzag Up

| Property | Value |
|----------|-------|
| **Line ID** | 7 |
| **Row Positions** | `[2, 2, 1, 1, 0]` |
| **Visual Description** | Zigzag pattern moving up (bottom-bottom → middle-middle → top) |
| **Shape Name** | Zigzag up |
| **Visual Pattern** | `/ / ─ ─` (stepping up) |

**Code Reference**: `game_config.py`, line 93  
**Comment**: "zigzag up (3-3-2-2-1)"

---

### Line 8: Step Down

| Property | Value |
|----------|-------|
| **Line ID** | 8 |
| **Row Positions** | `[0, 1, 1, 1, 2]` |
| **Visual Description** | Step pattern moving down (top → middle-middle-middle → bottom) |
| **Shape Name** | Step down |
| **Visual Pattern** | `\ ─ ─ ─ \` (step down) |

**Code Reference**: `game_config.py`, line 95  
**Comment**: "step down (1-2-2-2-3)"

---

### Line 9: Step Up

| Property | Value |
|----------|-------|
| **Line ID** | 9 |
| **Row Positions** | `[2, 1, 1, 1, 0]` |
| **Visual Description** | Step pattern moving up (bottom → middle-middle-middle → top) |
| **Shape Name** | Step up |
| **Visual Pattern** | `/ ─ ─ ─ /` (step up) |

**Code Reference**: `game_config.py`, line 97  
**Comment**: "step up (3-2-2-2-1)"

---

### Line 10: Wave

| Property | Value |
|----------|-------|
| **Line ID** | 10 |
| **Row Positions** | `[0, 1, 0, 1, 0]` |
| **Visual Description** | Wave pattern (top → middle → top → middle → top) |
| **Shape Name** | Wave |
| **Visual Pattern** | `\ / \ /` (wave) |

**Code Reference**: `game_config.py`, line 99  
**Comment**: "wave (1-2-1-2-1)"

---

## Complete Paylines Table

| Line ID | Row Positions (Reel 0-4) | Shape Name | Visual Pattern |
|---------|---------------------------|------------|----------------|
| 1 | `[0, 0, 0, 0, 0]` | Straight top | `─ ─ ─ ─ ─` |
| 2 | `[1, 1, 1, 1, 1]` | Straight middle | `─ ─ ─ ─ ─` |
| 3 | `[2, 2, 2, 2, 2]` | Straight bottom | `─ ─ ─ ─ ─` |
| 4 | `[0, 1, 2, 1, 0]` | V-shape down | `\ / \` |
| 5 | `[2, 1, 0, 1, 2]` | V-shape up | `/ \ /` |
| 6 | `[0, 0, 1, 1, 2]` | Zigzag down | `─ ─ \ \` |
| 7 | `[2, 2, 1, 1, 0]` | Zigzag up | `/ / ─ ─` |
| 8 | `[0, 1, 1, 1, 2]` | Step down | `\ ─ ─ ─ \` |
| 9 | `[2, 1, 1, 1, 0]` | Step up | `/ ─ ─ ─ /` |
| 10 | `[0, 1, 0, 1, 0]` | Wave | `\ / \ /` |

---

## Evaluation Details

### Left-to-Right Only

**Confirmed**: ✅ Yes, all paylines are evaluated **left-to-right only**

**Implementation**: `src/calculations/lines.py` → `Lines.get_lines()` (lines 28-118)

**Process**:
1. Iterates through `config.paylines.keys()` (line 42)
2. For each payline, evaluates from reel 0 (left) to reel 4 (right)
3. Line evaluation loop: `for reel in range(1, len(line))` (line 53)
4. Stops evaluation when a non-matching symbol is found (line 59, 68)

**Code Flow**:
```python
for line_index in config.paylines.keys():  # Iterate all paylines
    line = config.paylines[line_index]      # Get row positions
    first_sym = board[0][line[0]]           # Start at reel 0 (left)
    for reel in range(1, len(line)):        # Move right (reel 1-4)
        sym = board[reel][line[reel]]       # Check each reel left-to-right
        # ... evaluation logic ...
```

**No Right-to-Left Evaluation**: The code does not support right-to-left or bidirectional evaluation.

---

### Fixed or Configurable

**Status**: **Fixed** (hardcoded in configuration)

**Location**: `games/1_0_gunslingers/game_config.py`, lines 78-100

**Configuration Method**:
```python
self.paylines = {
    1: [0, 0, 0, 0, 0],
    2: [1, 1, 1, 1, 1],
    # ... etc ...
    10: [0, 1, 0, 1, 0],
}
```

**Modifiability**:
- ✅ **Can be modified** by editing `game_config.py` directly
- ❌ **Not configurable** via external config files or runtime parameters
- ❌ **Not dynamically adjustable** during simulation

**To Add/Remove Paylines**:
1. Edit `self.paylines` dictionary in `game_config.py`
2. Add new entries with unique line IDs (integer keys)
3. Each entry must be a list of 5 integers (one per reel, values 0-2)
4. Re-run simulation to regenerate lookup tables

**Note**: Changing payline count will affect RTP and require re-optimization.

---

### Alignment with Lines.get_lines() Logic

**Status**: ✅ **Fully Aligned**

**Verification**:

1. **Payline Structure**:
   - ✅ Backend paylines are stored as `dict[int, list[int]]` (line IDs → row positions)
   - ✅ `Lines.get_lines()` expects `config.paylines` to be iterable with `.keys()` method (line 42)
   - ✅ Each payline is a list of 5 integers (one per reel)

2. **Indexing Compatibility**:
   - ✅ Backend uses 0-based indexing (0=top, 1=middle, 2=bottom)
   - ✅ `Lines.get_lines()` accesses board as `board[reel][line[reel]]` (line 44, 54)
   - ✅ Board structure: `board[reel_index][row_index]` matches payline format

3. **Evaluation Order**:
   - ✅ Backend paylines define positions from reel 0 to reel 4
   - ✅ `Lines.get_lines()` evaluates from reel 0 (left) to reel 4 (right)
   - ✅ Loop order: `for reel in range(1, len(line))` processes reels 1-4 sequentially

4. **Data Flow**:
   ```
   game_config.py → self.paylines → Lines.get_lines() → config.paylines.keys()
   ```

**Code Reference**: `src/calculations/lines.py`, lines 42-43:
```python
for line_index in config.paylines.keys():
    line = config.paylines[line_index]
```

**Conclusion**: The payline definitions in `game_config.py` are **perfectly compatible** with the `Lines.get_lines()` evaluation logic. No modifications needed.

---

## Payline Count Summary

### Total Count

**Backend (Math-SDK)**: **10 paylines** (lines 1-10)

**Source**: `games/1_0_gunslingers/game_config.py`, line 78:
```python
# 10 fixed paylines for 5x3 grid
```

### Verification

**All 10 paylines are defined**:
- Line IDs: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- All have valid row positions (5 integers each, values 0-2)
- All are unique (no duplicate patterns)

**No additional paylines** found in:
- `game_config.py` (only 10 defined)
- `game_executables.py` (no payline overrides)
- `game_override.py` (no payline modifications)
- `game_calculations.py` (no payline logic)

---

## Code References

### Primary Definition
- **File**: `games/1_0_gunslingers/game_config.py`
- **Lines**: 78-100
- **Class**: `GameConfig.__init__()`

### Evaluation Logic
- **File**: `src/calculations/lines.py`
- **Function**: `Lines.get_lines()`
- **Lines**: 28-118
- **Usage**: Called from `game_executables.py` → `evaluate_lines_board()` (line 190)

### Documentation References
- `COMPLETE_MATH_SPEC.md`: Section 4 (Paylines)
- `MATH_DOCUMENTATION.md`: Section on Paylines
- `BACKEND_IMPLEMENTATION_ANALYSIS.md`: Section 3.2 (Symbols, Paylines, and Evaluation)

---

## Visual Representation

### Grid Layout (5×3)

```
Reel:  0    1    2    3    4
Row 0: [ ]  [ ]  [ ]  [ ]  [ ]  ← Top (0)
Row 1: [ ]  [ ]  [ ]  [ ]  [ ]  ← Middle (1)
Row 2: [ ]  [ ]  [ ]  [ ]  [ ]  ← Bottom (2)
```

### Example: Line 4 (V-shape down)

```
Reel:  0    1    2    3    4
Row 0: [X]  [ ]  [ ]  [ ]  [X]  ← Top
Row 1: [ ]  [X]  [ ]  [X]  [ ]  ← Middle
Row 2: [ ]  [ ]  [X]  [ ]  [ ]  ← Bottom
       └─────┴─────┴─────┴─────┘
         V-shape down pattern
```

---

## Notes

1. **Indexing Convention**: All row positions use 0-based indexing (0=top, 1=middle, 2=bottom)

2. **Uniqueness**: All 10 paylines have unique patterns (no duplicates)

3. **Completeness**: All paylines cover all 5 reels (no partial lines)

4. **Symmetry**: Some paylines are symmetric pairs:
   - Line 4 (V down) ↔ Line 5 (V up)
   - Line 6 (zigzag down) ↔ Line 7 (zigzag up)
   - Line 8 (step down) ↔ Line 9 (step up)

5. **Modification Impact**: Changing payline count or patterns will:
   - Require re-running simulations
   - Regenerate lookup tables
   - Potentially affect RTP (may need re-optimization)

---

**End of Paylines Breakdown**

