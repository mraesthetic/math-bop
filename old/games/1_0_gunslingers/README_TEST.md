# Quick Test Script - 30,000 Spins (No Optimization)

This directory contains a quick test script to run 30,000 spins per mode without optimization.

## Usage

### Option 1: Using Makefile (Recommended)
```bash
cd /Users/anthony/Downloads/game1/math-sdk
make test-spins GAME=1_0_gunslingers
```

### Option 2: Direct Python execution
```bash
cd /Users/anthony/Downloads/game1/math-sdk
python3 games/1_0_gunslingers/test_5000_spins.py
```

### Option 3: From game directory
```bash
cd /Users/anthony/Downloads/game1/math-sdk/games/1_0_gunslingers
python3 test_5000_spins.py
```

## What It Does

- Runs **30,000 spins** for each mode (base, bonus, superbonus)
- **No optimization** - just raw simulation
- Generates books, lookup tables, and configs
- Prints RTP and statistics summary at the end

## Output

Results are saved to:
- Books: `games/1_0_gunslingers/library/books/`
- Lookup tables: `games/1_0_gunslingers/library/lookup_tables/`
- Configs: `games/1_0_gunslingers/library/configs/`

The script will also print a summary of RTP and statistics for each mode.

## Differences from Full Run

The main `run.py` script:
- Runs 50,000 spins per mode
- Runs optimization
- Runs analysis
- Runs format checks

This test script:
- Runs 30,000 spins per mode
- **Skips optimization**
- Still generates configs and stats summary
- Faster execution for quick testing (compared to full 50,000 + optimization)

