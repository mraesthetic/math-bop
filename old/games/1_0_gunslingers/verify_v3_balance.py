#!/usr/bin/env python3
"""
Verify v3 balance for FR1.csv (superbonus reelset).

This script:
1. Runs 100k superbonus feature simulations with v3 distribution
2. Analyzes feature-level wins (excluding wincap)
3. Generates a detailed markdown report with bucket distribution
4. Provides summary assessment against target (384× ± 5×)
"""

import json
import os
import sys
import zstandard as zst
from io import TextIOWrapper
from collections import defaultdict
from pathlib import Path
import statistics
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_config import GameConfig
from gamestate import GameState
from src.state.run_sims import create_books


def run_superbonus_simulation(config, gamestate, num_features=100000):
    """Run simulation for superbonus mode only."""
    print(f"\n{'='*80}")
    print(f"Running SUPERBONUS simulation (v3): {num_features:,} features")
    print(f"{'='*80}\n")
    
    num_threads = 10
    batching_size = 5000
    compression = True
    profiling = False
    
    # Run simulation for superbonus only
    num_sim_args = {
        "superbonus": num_features,
    }
    
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )
    
    # Generate configs after simulation
    from src.write_data.write_configs import generate_configs
    generate_configs(gamestate)
    
    print(f"\n✓ Simulation complete: {num_features:,} superbonus features\n")


def analyze_superbonus_books(book_file_path: str, exclude_wincap: bool = True):
    """Analyze superbonus books to extract feature win distribution."""
    feature_wins = []
    wincap_count = 0
    total_features = 0
    
    if not os.path.exists(book_file_path):
        raise FileNotFoundError(f"Book file not found: {book_file_path}")
    
    print(f"Reading books from: {book_file_path}")
    
    with open(book_file_path, "rb") as f:
        decompressor = zst.ZstdDecompressor()
        with decompressor.stream_reader(f) as reader:
            txt_stream = TextIOWrapper(reader, encoding="UTF-8")
            for line_num, line in enumerate(txt_stream, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    blob = json.loads(line)
                except json.JSONDecodeError as e:
                    continue
                
                payout_mult = blob.get("payoutMultiplier", 0) / 100.0
                criteria = blob.get("criteria", "")
                
                total_features += 1
                
                if exclude_wincap and criteria == "wincap":
                    wincap_count += 1
                    continue
                
                feature_wins.append(payout_mult)
                
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num:,} features...", end='\r')
    
    print(f"\n✓ Analyzed {total_features:,} features (excluded {wincap_count:,} wincap)\n")
    
    return {
        'feature_wins': feature_wins,
        'total_features': total_features,
        'wincap_count': wincap_count,
        'analyzed_features': len(feature_wins),
    }


def calculate_statistics(feature_wins, buy_cost=400.0, wincap=10000.0):
    """Calculate comprehensive statistics for superbonus features."""
    if not feature_wins:
        return None
    
    avg_win = statistics.mean(feature_wins)
    median_win = statistics.median(feature_wins)
    min_win = min(feature_wins)
    max_win = max(feature_wins)
    rtp = (avg_win / buy_cost) * 100
    
    # Bucket distribution
    buckets = {
        '< 25×': 0,
        '25–50×': 0,
        '50–100×': 0,
        '100–250×': 0,
        '250–500×': 0,
        '500–1000×': 0,
        '1000×+': 0,
    }
    
    for win in feature_wins:
        if win < 25:
            buckets['< 25×'] += 1
        elif win < 50:
            buckets['25–50×'] += 1
        elif win < 100:
            buckets['50–100×'] += 1
        elif win < 250:
            buckets['100–250×'] += 1
        elif win < 500:
            buckets['250–500×'] += 1
        elif win < 1000:
            buckets['500–1000×'] += 1
        else:
            buckets['1000×+'] += 1
    
    total = len(feature_wins)
    bucket_pct = {k: (v / total * 100) for k, v in buckets.items()}
    
    # Performance vs buy cost
    below_cost = sum(1 for w in feature_wins if w < buy_cost)
    above_cost = sum(1 for w in feature_wins if w >= buy_cost)
    above_2x = sum(1 for w in feature_wins if w >= buy_cost * 2)
    above_2_5x = sum(1 for w in feature_wins if w >= buy_cost * 2.5)
    
    pct_below = (below_cost / total) * 100
    pct_above = (above_cost / total) * 100
    pct_2x = (above_2x / total) * 100
    pct_2_5x = (above_2_5x / total) * 100
    
    # Count dead spins (< 25×)
    dead_spins = buckets['< 25×']
    dead_spins_pct = bucket_pct['< 25×']
    
    # Count big wins (1000×+)
    big_wins = buckets['1000×+']
    big_wins_pct = bucket_pct['1000×+']
    
    return {
        'avg_win': avg_win,
        'median_win': median_win,
        'min_win': min_win,
        'max_win': max_win,
        'rtp': rtp,
        'buckets': buckets,
        'bucket_pct': bucket_pct,
        'total_features': total,
        'below_cost': below_cost,
        'pct_below_cost': pct_below,
        'above_cost': above_cost,
        'pct_above_cost': pct_above,
        'above_2x_cost': above_2x,
        'pct_2x_cost': pct_2x,
        'above_2_5x_cost': above_2_5x,
        'pct_2_5x_cost': pct_2_5x,
        'dead_spins': dead_spins,
        'dead_spins_pct': dead_spins_pct,
        'big_wins': big_wins,
        'big_wins_pct': big_wins_pct,
    }


def generate_v3_report(stats, analysis_data, output_file=None):
    """Generate comprehensive v3 verification report."""
    if not stats:
        return "No statistics available"
    
    wincap = 10000.0
    buy_cost = 400.0
    
    # Pre-compute status strings to avoid nested f-string issues
    dead_status = "✅ Appropriate" if 3.0 <= stats['dead_spins_pct'] <= 4.0 else f"⚠️ Too {'high' if stats['dead_spins_pct'] > 4.0 else 'low'}"
    big_status = "✅ Appropriate" if 5.0 <= stats['big_wins_pct'] <= 8.0 else f"⚠️ Too {'high' if stats['big_wins_pct'] > 8.0 else 'low'}"
    dist_status = "✅ Balanced" if stats['bucket_pct']['100–250×'] + stats['bucket_pct']['250–500×'] > 40 and stats['dead_spins_pct'] < 5 and stats['big_wins_pct'] > 4 else "⚠️ Needs review"
    
    report = f"""# SUPERBONUS v3 Balance Verification Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

**v3 Distribution**:
- H3: 270 (increased from 240)
- W: 19 (increased from 16)
- L4: 168 (reduced from 184)
- L5: 155 (reduced from 175)
- L1, L2, L3: Unchanged

**Target**:
- Average Feature Win: 384× ± 5× (379× - 389×)
- Effective RTP: 96.2%
- Expected Volatility: 3-4% dead spins, 5-8% big wins (1000×+)

---

## Core Statistics

| Metric | Value |
|--------|-------|
| **Average Feature Win** | {stats['avg_win']:.2f}× bet |
| **Effective RTP** | {stats['rtp']:.2f}% |
| **Median Feature Win** | {stats['median_win']:.2f}× bet |
| **Min Feature Win** | {stats['min_win']:.2f}× bet |
| **Max Feature Win** | {stats['max_win']:.2f}× bet |

**Analysis**:
- ✅/⚠️ Average is {"**WITHIN**" if 379 <= stats['avg_win'] <= 389 else "**OUTSIDE**"} target range (379× - 389×)
- Target: 384× ± 5×
- Difference from target: {stats['avg_win'] - 384:+.2f}× ({abs(stats['avg_win'] - 384) / 384 * 100:.2f}%)
- RTP difference from 96.2%: {stats['rtp'] - 96.2:+.2f}%

---

## Win Distribution by Bucket

| Bucket | Count | Percentage |
|--------|-------|------------|
| **< 25×** | {stats['buckets']['< 25×']:,} | {stats['bucket_pct']['< 25×']:.2f}% |
| **25–50×** | {stats['buckets']['25–50×']:,} | {stats['bucket_pct']['25–50×']:.2f}% |
| **50–100×** | {stats['buckets']['50–100×']:,} | {stats['bucket_pct']['50–100×']:.2f}% |
| **100–250×** | {stats['buckets']['100–250×']:,} | {stats['bucket_pct']['100–250×']:.2f}% |
| **250–500×** | {stats['buckets']['250–500×']:,} | {stats['bucket_pct']['250–500×']:.2f}% |
| **500–1000×** | {stats['buckets']['500–1000×']:,} | {stats['bucket_pct']['500–1000×']:.2f}% |
| **1000×+** | {stats['buckets']['1000×+']:,} | {stats['bucket_pct']['1000×+']:.2f}% |

---

## Performance vs Buy Cost (400×)

| Metric | Count | Percentage |
|--------|-------|------------|
| **< 400×** | {stats['below_cost']:,} | {stats['pct_below_cost']:.2f}% |
| **≥ 400×** | {stats['above_cost']:,} | {stats['pct_above_cost']:.2f}% |
| **≥ 800×** | {stats['above_2x_cost']:,} | {stats['pct_2x_cost']:.2f}% |
| **≥ 1000×** | {stats['above_2_5x_cost']:,} | {stats['pct_2_5x_cost']:.2f}% |

---

## Win Cap Statistics

| Metric | Value |
|--------|-------|
| **Cap Value** | {wincap:.0f}× bet |
| **Features Hit Cap** | {analysis_data['wincap_count']:,} |
| **Cap Hit Rate** | {analysis_data['wincap_count'] / analysis_data['total_features'] * 100:.4f}% |
| **Total Features (including cap)** | {analysis_data['total_features']:,} |
| **Features Analyzed (cap excluded)** | {stats['total_features']:,} |

---

## Volatility Assessment

### Dead Spins (< 25×)
- **Count**: {stats['dead_spins']:,} features
- **Percentage**: {stats['dead_spins_pct']:.2f}%
- **Target Range**: 3-4%
- **Status**: {"✅" if 3.0 <= stats['dead_spins_pct'] <= 4.0 else "⚠️"} {"WITHIN" if 3.0 <= stats['dead_spins_pct'] <= 4.0 else "OUTSIDE"} expected range

### Big Wins (1000×+)
- **Count**: {stats['big_wins']:,} features
- **Percentage**: {stats['big_wins_pct']:.2f}%
- **Target Range**: 5-8%
- **Status**: {"✅" if 5.0 <= stats['big_wins_pct'] <= 8.0 else "⚠️"} {"WITHIN" if 5.0 <= stats['big_wins_pct'] <= 8.0 else "OUTSIDE"} expected range

### Overall Volatility Profile
- **Dead spin rate**: {dead_status}
- **Big win frequency**: {big_status}
- **Win distribution**: {dist_status}

---

## Target Alignment Summary

### RTP Alignment

| Target | Actual | Status |
|--------|--------|--------|
| **Average Feature Win** | 384× ± 5× | {stats['avg_win']:.2f}× | {"✅" if 379 <= stats['avg_win'] <= 389 else "⚠️"} |
| **Effective RTP** | 96.2% | {stats['rtp']:.2f}% | {"✅" if 94.75 <= stats['rtp'] <= 97.25 else "⚠️"} |

**Assessment**:
- {"✅ **ON TARGET**: Average feature win is within target range (379× - 389×)" if 379 <= stats['avg_win'] <= 389 else f"⚠️ **OFF TARGET**: Average feature win is {abs(stats['avg_win'] - 384):.2f}× {'below' if stats['avg_win'] < 379 else 'above'} target range"}
- {"✅ **ON TARGET**: Effective RTP is within target range (94.75% - 97.25%)" if 94.75 <= stats['rtp'] <= 97.25 else f"⚠️ **OFF TARGET**: Effective RTP is {abs(stats['rtp'] - 96.2):.2f}% {'below' if stats['rtp'] < 94.75 else 'above'} target range"}

### Volatility Alignment

| Metric | Target Range | Actual | Status |
|--------|--------------|--------|--------|
| **Dead Spins (< 25×)** | 3-4% | {stats['dead_spins_pct']:.2f}% | {"✅" if 3.0 <= stats['dead_spins_pct'] <= 4.0 else "⚠️"} |
| **Big Wins (1000×+)** | 5-8% | {stats['big_wins_pct']:.2f}% | {"✅" if 5.0 <= stats['big_wins_pct'] <= 8.0 else "⚠️"} |

---

## Recommendations

"""
    
    # Add recommendations based on results
    if stats['avg_win'] < 379:
        deficit = 379 - stats['avg_win']
        rtp_deficit = (deficit / 400) * 100
        report += f"""
**RTP Below Target**:
- Current: {stats['avg_win']:.2f}× ({stats['rtp']:.2f}%)
- Target: 384× (96.2%)
- Deficit: {deficit:.2f}× ({rtp_deficit:.2f}% RTP)
- **Recommendation**: Increase H3 by ~{int(deficit / 2.5)}-{int(deficit / 2)} (from 270 to ~{270 + int(deficit / 2.5)}-{270 + int(deficit / 2)}) or increase W by ~{int(deficit / 3.5)} (from 19 to ~{19 + int(deficit / 3.5)})

"""
    elif stats['avg_win'] > 389:
        excess = stats['avg_win'] - 389
        rtp_excess = (excess / 400) * 100
        report += f"""
**RTP Above Target**:
- Current: {stats['avg_win']:.2f}× ({stats['rtp']:.2f}%)
- Target: 384× (96.2%)
- Excess: {excess:.2f}× ({rtp_excess:.2f}% RTP)
- **Recommendation**: Reduce H3 by ~{int(excess / 2.5)}-{int(excess / 2)} (from 270 to ~{270 - int(excess / 2)}-{270 - int(excess / 2.5)}) or reduce W by ~{int(excess / 3.5)} (from 19 to ~{19 - int(excess / 3.5)})

"""
    else:
        report += f"""
**RTP On Target**:
- ✅ Average feature win ({stats['avg_win']:.2f}×) is within target range (379× - 389×)
- ✅ Effective RTP ({stats['rtp']:.2f}%) is within target range (94.75% - 97.25%)
- v3 distribution is well-balanced for target RTP

"""
    
    if stats['dead_spins_pct'] < 3.0:
        report += f"""
**Dead Spin Rate Too Low**:
- Current: {stats['dead_spins_pct']:.2f}%
- Target: 3-4%
- **Recommendation**: Consider reducing L1-L3 slightly to create more dead spins

"""
    elif stats['dead_spins_pct'] > 4.0:
        report += f"""
**Dead Spin Rate Too High**:
- Current: {stats['dead_spins_pct']:.2f}%
- Target: 3-4%
- **Recommendation**: Consider increasing L1-L3 slightly to reduce dead spins

"""
    
    if stats['big_wins_pct'] < 5.0:
        report += f"""
**Big Win Rate Too Low**:
- Current: {stats['big_wins_pct']:.2f}%
- Target: 5-8%
- **Recommendation**: Consider increasing H3 or W to boost big win potential

"""
    elif stats['big_wins_pct'] > 8.0:
        report += f"""
**Big Win Rate Too High**:
- Current: {stats['big_wins_pct']:.2f}%
- Target: 5-8%
- **Recommendation**: Consider reducing H3 slightly to moderate big win frequency

"""
    
    report += f"""
---

## Simulation Details

- **Simulation Mode**: superbonus (400× buy)
- **Features Simulated**: {analysis_data['total_features']:,}
- **Features Analyzed** (wincap excluded): {stats['total_features']:,}
- **Wincap Features Excluded**: {analysis_data['wincap_count']:,}
- **Buy Cost**: {buy_cost:.0f}× bet
- **Max Win Cap**: {wincap:.0f}× bet

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to: {output_file}")
    else:
        print(report)
    
    return report


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("SUPERBONUS v3 BALANCE VERIFICATION")
    print("="*80)
    
    # Initialize config and gamestate
    print("\n" + "="*80)
    print("STEP 1: INITIALIZING GAME CONFIG")
    print("="*80)
    config = GameConfig()
    gamestate = GameState(config)
    
    # Step 2: Run simulation
    print("\n" + "="*80)
    print("STEP 2: RUNNING SUPERBONUS SIMULATION (v3)")
    print("="*80)
    num_features_requested = 100000
    run_superbonus_simulation(config, gamestate, num_features_requested)
    
    # Step 3: Analyze results
    book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    print("\n" + "="*80)
    print("STEP 3: ANALYZING FEATURE WINS (v3)")
    print("="*80 + "\n")
    
    analysis_data = analyze_superbonus_books(book_file, exclude_wincap=True)
    
    # Step 4: Calculate statistics
    print("\n" + "="*80)
    print("STEP 4: CALCULATING STATISTICS")
    print("="*80 + "\n")
    
    stats = calculate_statistics(analysis_data['feature_wins'], buy_cost=400.0)
    
    if not stats:
        print("ERROR: No statistics calculated. Exiting.")
        return
    
    # Print summary
    print("\n" + "="*80)
    print("QUICK SUMMARY")
    print("="*80)
    print(f"Average Feature Win: {stats['avg_win']:.2f}×")
    print(f"Effective RTP: {stats['rtp']:.2f}%")
    print(f"Median: {stats['median_win']:.2f}×")
    print(f"Dead Spins (< 25×): {stats['dead_spins_pct']:.2f}%")
    print(f"Big Wins (1000×+): {stats['big_wins_pct']:.2f}%")
    print(f"Cap Hit Rate: {analysis_data['wincap_count'] / analysis_data['total_features'] * 100:.4f}%")
    
    # Step 5: Generate report
    print("\n" + "="*80)
    print("STEP 5: GENERATING v3 VERIFICATION REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "SUPERBONUS_v3_BALANCE_VERIFICATION.md"
    )
    
    generate_v3_report(stats, analysis_data, output_file=output_file)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    print(f"\n✅ Average Feature Win: {stats['avg_win']:.2f}×")
    if 379 <= stats['avg_win'] <= 389:
        print(f"   Status: ✅ WITHIN target range (379× - 389×)")
    else:
        diff = abs(stats['avg_win'] - 384)
        direction = "below" if stats['avg_win'] < 379 else "above"
        print(f"   Status: ⚠️  {diff:.2f}× {direction} target range")
    
    print(f"\n✅ Volatility Profile:")
    print(f"   Dead Spins (< 25×): {stats['dead_spins_pct']:.2f}% {'✅' if 3.0 <= stats['dead_spins_pct'] <= 4.0 else '⚠️'} (target: 3-4%)")
    print(f"   Big Wins (1000×+): {stats['big_wins_pct']:.2f}% {'✅' if 5.0 <= stats['big_wins_pct'] <= 8.0 else '⚠️'} (target: 5-8%)")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

