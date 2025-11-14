#!/usr/bin/env python3
"""
Verify FR1.csv balance after re-balancing correction.

This script:
1. Runs fresh 100k superbonus simulation with re-balanced FR1.csv
2. Analyzes results (excluding wincap)
3. Compares to previous results (1006× and 255× cases)
4. Generates verification report
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
from src.write_data.write_configs import generate_configs


# Previous results for comparison
PREVIOUS_255X = {
    'avg_feature_win': 255.14,
    'effective_rtp': 0.6379,
    'num_features': 99900,
    'bucket_percentages': {
        '< 25×': 4.51,
        '25–50×': 8.21,
        '50–100×': 18.68,
        '100–250×': 36.67,
        '250–500×': 20.48,
        '500–1000×': 8.57,
        '1000×+': 2.88,
    },
    'below_cost_pct': 83.35,
    'above_cost_pct': 16.65,
    'above_800_pct': 4.69,
    'above_1000_pct': 2.88,
    'hit_cap_pct': 0.0030,
    'hit_cap_count': 3,
}

PREVIOUS_1006X = {
    'avg_feature_win': 1006.33,
    'effective_rtp': 2.5158,
    'num_features': 99900,
    'bucket_percentages': {
        '< 25×': 0.36,
        '25–50×': 0.70,
        '50–100×': 2.23,
        '100–250×': 10.73,
        '250–500×': 21.80,
        '500–1000×': 30.70,
        '1000×+': 33.49,
    },
    'below_cost_pct': 27.36,
    'above_cost_pct': 72.64,
    'above_800_pct': 43.42,
    'above_1000_pct': 33.49,
    'hit_cap_pct': 0.1592,
    'hit_cap_count': 159,
}


def run_superbonus_simulation(config, gamestate, num_features=100000):
    """Run simulation for superbonus mode only."""
    print(f"\n{'='*80}")
    print(f"Running SUPERBONUS simulation: {num_features:,} features")
    print(f"Using re-balanced FR1.csv (H3: 170, W: 13, Lows restored)")
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
                    print(f"Warning: Failed to parse line {line_num}: {e}")
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


def calculate_statistics(feature_wins, buy_cost=400.0):
    """Calculate comprehensive statistics for superbonus features."""
    if not feature_wins:
        raise ValueError("No feature wins to analyze!")
    
    num_features = len(feature_wins)
    
    # Core numbers
    avg_feature_win = sum(feature_wins) / num_features
    effective_rtp = avg_feature_win / buy_cost
    median_win = statistics.median(feature_wins)
    min_win = min(feature_wins)
    max_win = max(feature_wins)
    
    # Win thresholds
    win_cap = 10000.0
    below_cost = sum(1 for w in feature_wins if w < buy_cost)
    above_cost = sum(1 for w in feature_wins if w >= buy_cost)
    above_800 = sum(1 for w in feature_wins if w >= 800.0)
    above_1000 = sum(1 for w in feature_wins if w >= 1000.0)
    hit_cap = sum(1 for w in feature_wins if w >= win_cap)
    
    # Bucket distribution
    buckets = {
        '< 25×': (0, 25),
        '25–50×': (25, 50),
        '50–100×': (50, 100),
        '100–250×': (100, 250),
        '250–500×': (250, 500),
        '500–1000×': (500, 1000),
        '1000×+': (1000, float('inf')),
    }
    
    bucket_counts = {}
    bucket_percentages = {}
    
    for bucket_name, (min_val, max_val) in buckets.items():
        if max_val == float('inf'):
            count = sum(1 for w in feature_wins if w >= min_val)
        else:
            count = sum(1 for w in feature_wins if min_val <= w < max_val)
        
        bucket_counts[bucket_name] = count
        bucket_percentages[bucket_name] = (count / num_features) * 100.0
    
    return {
        'num_features': num_features,
        'avg_feature_win': avg_feature_win,
        'effective_rtp': effective_rtp,
        'buy_cost': buy_cost,
        'win_cap': win_cap,
        'median_win': median_win,
        'min_win': min_win,
        'max_win': max_win,
        'below_cost_count': below_cost,
        'below_cost_pct': (below_cost / num_features) * 100.0,
        'above_cost_count': above_cost,
        'above_cost_pct': (above_cost / num_features) * 100.0,
        'above_800_count': above_800,
        'above_800_pct': (above_800 / num_features) * 100.0,
        'above_1000_count': above_1000,
        'above_1000_pct': (above_1000 / num_features) * 100.0,
        'hit_cap_count': hit_cap,
        'hit_cap_pct': (hit_cap / num_features) * 100.0,
        'bucket_counts': bucket_counts,
        'bucket_percentages': bucket_percentages,
    }


def generate_verification_report(stats_255x, stats_1006x, new_stats, output_file=None):
    """Generate verification report comparing all three states."""
    
    report = f"""# SUPERBONUS Balance Verification Report

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

| Metric | Target | 255× (Too Tight) | 1006× (Too Generous) | **NEW (Re-Balanced)** | Status |
|--------|--------|------------------|----------------------|----------------------|--------|
| **Average Feature Win** | 384× ± 5× | {stats_255x['avg_feature_win']:.2f}× | {stats_1006x['avg_feature_win']:.2f}× | **{new_stats['avg_feature_win']:.2f}×** | {"✅" if 379 <= new_stats['avg_feature_win'] <= 389 else "⚠️"} |
| **Effective RTP** | 96.2% | {stats_255x['effective_rtp']*100:.2f}% | {stats_1006x['effective_rtp']*100:.2f}% | **{new_stats['effective_rtp']*100:.2f}%** | |
| **Median Feature Win** | - | - | - | **{new_stats['median_win']:.2f}×** | |

---

## Core Statistics

| Metric | 255× (Too Tight) | 1006× (Too Generous) | **NEW (Re-Balanced)** | Change vs 1006× |
|--------|------------------|----------------------|----------------------|-----------------|
| **Average Feature Win** | {stats_255x['avg_feature_win']:.2f}× | {stats_1006x['avg_feature_win']:.2f}× | **{new_stats['avg_feature_win']:.2f}×** | {new_stats['avg_feature_win'] - stats_1006x['avg_feature_win']:+.2f}× |
| **Effective RTP** | {stats_255x['effective_rtp']*100:.2f}% | {stats_1006x['effective_rtp']*100:.2f}% | **{new_stats['effective_rtp']*100:.2f}%** | {(new_stats['effective_rtp'] - stats_1006x['effective_rtp'])*100:+.2f}% |
| **Median Feature Win** | - | - | **{new_stats['median_win']:.2f}×** | - |
| **Min Feature Win** | - | - | **{new_stats['min_win']:.2f}×** | - |
| **Max Feature Win** | - | - | **{new_stats['max_win']:.2f}×** | - |

---

## Win Distribution by Bucket

| Bucket | 255× (Too Tight) | 1006× (Too Generous) | **NEW (Re-Balanced)** | Change vs 1006× |
|--------|------------------|----------------------|----------------------|-----------------|
| **< 25×** | {stats_255x['bucket_percentages']['< 25×']:.2f}% | {stats_1006x['bucket_percentages']['< 25×']:.2f}% | **{new_stats['bucket_percentages']['< 25×']:.2f}%** | {new_stats['bucket_percentages']['< 25×'] - stats_1006x['bucket_percentages']['< 25×']:+.2f}% |
| **25–50×** | {stats_255x['bucket_percentages']['25–50×']:.2f}% | {stats_1006x['bucket_percentages']['25–50×']:.2f}% | **{new_stats['bucket_percentages']['25–50×']:.2f}%** | {new_stats['bucket_percentages']['25–50×'] - stats_1006x['bucket_percentages']['25–50×']:+.2f}% |
| **50–100×** | {stats_255x['bucket_percentages']['50–100×']:.2f}% | {stats_1006x['bucket_percentages']['50–100×']:.2f}% | **{new_stats['bucket_percentages']['50–100×']:.2f}%** | {new_stats['bucket_percentages']['50–100×'] - stats_1006x['bucket_percentages']['50–100×']:+.2f}% |
| **100–250×** | {stats_255x['bucket_percentages']['100–250×']:.2f}% | {stats_1006x['bucket_percentages']['100–250×']:.2f}% | **{new_stats['bucket_percentages']['100–250×']:.2f}%** | {new_stats['bucket_percentages']['100–250×'] - stats_1006x['bucket_percentages']['100–250×']:+.2f}% |
| **250–500×** | {stats_255x['bucket_percentages']['250–500×']:.2f}% | {stats_1006x['bucket_percentages']['250–500×']:.2f}% | **{new_stats['bucket_percentages']['250–500×']:.2f}%** | {new_stats['bucket_percentages']['250–500×'] - stats_1006x['bucket_percentages']['250–500×']:+.2f}% |
| **500–1000×** | {stats_255x['bucket_percentages']['500–1000×']:.2f}% | {stats_1006x['bucket_percentages']['500–1000×']:.2f}% | **{new_stats['bucket_percentages']['500–1000×']:.2f}%** | {new_stats['bucket_percentages']['500–1000×'] - stats_1006x['bucket_percentages']['500–1000×']:+.2f}% |
| **1000×+** | {stats_255x['bucket_percentages']['1000×+']:.2f}% | {stats_1006x['bucket_percentages']['1000×+']:.2f}% | **{new_stats['bucket_percentages']['1000×+']:.2f}%** | {new_stats['bucket_percentages']['1000×+'] - stats_1006x['bucket_percentages']['1000×+']:+.2f}% |

---

## Performance vs Buy Cost

| Threshold | 255× (Too Tight) | 1006× (Too Generous) | **NEW (Re-Balanced)** | Change vs 1006× |
|-----------|------------------|----------------------|----------------------|-----------------|
| **< 400×** (below cost) | {stats_255x['below_cost_pct']:.2f}% | {stats_1006x['below_cost_pct']:.2f}% | **{new_stats['below_cost_pct']:.2f}%** | {new_stats['below_cost_pct'] - stats_1006x['below_cost_pct']:+.2f}% |
| **≥ 400×** (at/above cost) | {stats_255x['above_cost_pct']:.2f}% | {stats_1006x['above_cost_pct']:.2f}% | **{new_stats['above_cost_pct']:.2f}%** | {new_stats['above_cost_pct'] - stats_1006x['above_cost_pct']:+.2f}% |
| **≥ 800×** | {stats_255x['above_800_pct']:.2f}% | {stats_1006x['above_800_pct']:.2f}% | **{new_stats['above_800_pct']:.2f}%** | {new_stats['above_800_pct'] - stats_1006x['above_800_pct']:+.2f}% |
| **≥ 1000×** | {stats_255x['above_1000_pct']:.2f}% | {stats_1006x['above_1000_pct']:.2f}% | **{new_stats['above_1000_pct']:.2f}%** | {new_stats['above_1000_pct'] - stats_1006x['above_1000_pct']:+.2f}% |

---

## Max Win Cap

| Metric | 255× (Too Tight) | 1006× (Too Generous) | **NEW (Re-Balanced)** | Change vs 1006× |
|--------|------------------|----------------------|----------------------|-----------------|
| **Win Cap** | 10,000× bet | 10,000× bet | 10,000× bet | - |
| **Features Hitting Cap** | {stats_255x['hit_cap_count']} | {stats_1006x['hit_cap_count']} | **{new_stats['hit_cap_count']}** | {new_stats['hit_cap_count'] - stats_1006x['hit_cap_count']:+d} |
| **Cap Hit Rate** | {stats_255x['hit_cap_pct']:.4f}% | {stats_1006x['hit_cap_pct']:.4f}% | **{new_stats['hit_cap_pct']:.4f}%** | {new_stats['hit_cap_pct'] - stats_1006x['hit_cap_pct']:+.4f}% |

---

## Detailed Comparison Analysis

### Dead Spins (< 25×)

- **255× case**: {stats_255x['bucket_percentages']['< 25×']:.2f}% (too many dead spins)
- **1006× case**: {stats_1006x['bucket_percentages']['< 25×']:.2f}% (too few dead spins)
- **NEW**: {new_stats['bucket_percentages']['< 25×']:.2f}% 
- **Change vs 1006×**: {new_stats['bucket_percentages']['< 25×'] - stats_1006x['bucket_percentages']['< 25×']:+.2f}%
- **Assessment**: {"✅ Increased dead spins (better volatility)" if new_stats['bucket_percentages']['< 25×'] > stats_1006x['bucket_percentages']['< 25×'] else "⚠️ Dead spins still low"}

### Medium Wins (100–500×)

- **255× case**: {stats_255x['bucket_percentages']['100–250×'] + stats_255x['bucket_percentages']['250–500×']:.2f}%
- **1006× case**: {stats_1006x['bucket_percentages']['100–250×'] + stats_1006x['bucket_percentages']['250–500×']:.2f}%
- **NEW**: {new_stats['bucket_percentages']['100–250×'] + new_stats['bucket_percentages']['250–500×']:.2f}%
- **Change vs 1006×**: {(new_stats['bucket_percentages']['100–250×'] + new_stats['bucket_percentages']['250–500×']) - (stats_1006x['bucket_percentages']['100–250×'] + stats_1006x['bucket_percentages']['250–500×']):+.2f}%
- **Assessment**: {"✅ Reduced medium wins (better volatility)" if (new_stats['bucket_percentages']['100–250×'] + new_stats['bucket_percentages']['250–500×']) < (stats_1006x['bucket_percentages']['100–250×'] + stats_1006x['bucket_percentages']['250–500×']) else "⚠️ Medium wins still high"}

### Big Wins (1000×+)

- **255× case**: {stats_255x['bucket_percentages']['1000×+']:.2f}% (too few big wins)
- **1006× case**: {stats_1006x['bucket_percentages']['1000×+']:.2f}% (too many big wins)
- **NEW**: {new_stats['bucket_percentages']['1000×+']:.2f}%
- **Change vs 1006×**: {new_stats['bucket_percentages']['1000×+'] - stats_1006x['bucket_percentages']['1000×+']:+.2f}%
- **Assessment**: {"✅ Reduced excessive big wins" if new_stats['bucket_percentages']['1000×+'] < stats_1006x['bucket_percentages']['1000×+'] else "⚠️ Big wins still excessive"}

---

## RTP Balance Assessment

"""
    
    # Add RTP assessment
    avg_win = new_stats['avg_feature_win']
    target_min = 379
    target_max = 389
    
    if target_min <= avg_win <= target_max:
        report += f"✅ **BALANCED**: Average feature win ({avg_win:.2f}×) is within target range (384× ± 5×)\n"
        report += f"- RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += "- No further adjustments needed to FR1.csv\n"
        report += "- Re-balancing successful!\n\n"
    elif avg_win < target_min:
        report += f"⚠️ **STILL TOO TIGHT**: Average feature win ({avg_win:.2f}×) is below target range (384× - 5× = {target_min}×)\n"
        report += f"- Current RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += f"- Delta from target: {384 - avg_win:.2f}× below target\n"
        report += "- **Recommendation**: Need to reduce H3 less, or add more wilds/premiums\n"
        report += "- Consider: H3 target 180-200, W target 14-15\n\n"
    elif avg_win > target_max:
        report += f"⚠️ **STILL TOO GENEROUS**: Average feature win ({avg_win:.2f}×) exceeds target range (384× + 5× = {target_max}×)\n"
        report += f"- Current RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += f"- Delta from target: {avg_win - 384:.2f}× above target\n"
        report += "- **Recommendation**: Need to reduce H3 further, or reduce wilds more\n"
        report += "- Consider: H3 target 150-160, W target 11-12, or reduce L4/L5 density\n\n"
    else:
        report += f"⚠️ **NEAR TARGET**: Average feature win ({avg_win:.2f}×) is close but outside ±5× range\n"
        report += f"- Current RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += "- Consider minor fine-tuning if precision is required\n\n"
    
    report += "### Summary\n\n"
    report += f"- **Features Analyzed**: {new_stats['num_features']:,} (wincap excluded)\n"
    report += f"- **Average Feature Win**: {new_stats['avg_feature_win']:.2f}× bet\n"
    report += f"- **Effective RTP**: {new_stats['effective_rtp']*100:.2f}%\n"
    report += f"- **Median Feature Win**: {new_stats['median_win']:.2f}× bet\n"
    report += f"- **Min Feature Win**: {new_stats['min_win']:.2f}× bet\n"
    report += f"- **Max Feature Win**: {new_stats['max_win']:.2f}× bet\n"
    report += f"- **Below Cost**: {new_stats['below_cost_pct']:.2f}% of features\n"
    report += f"- **Above Cost**: {new_stats['above_cost_pct']:.2f}% of features\n"
    report += f"- **1000×+ Hits**: {new_stats['above_1000_pct']:.2f}% of features\n"
    report += f"- **Cap Hits**: {new_stats['hit_cap_pct']:.4f}% of features ({new_stats['hit_cap_count']} features)\n\n"
    
    report += f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✓ Verification report saved to: {output_file}")
    else:
        print(report)
    
    return report


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("SUPERBONUS BALANCE VERIFICATION")
    print("="*80)
    
    # Initialize config and gamestate
    config = GameConfig()
    gamestate = GameState(config)
    
    # Path to books file
    book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    # Always run fresh simulation with re-balanced FR1.csv
    num_features_requested = 100000
    print(f"\n⚠️  Running fresh simulation with re-balanced FR1.csv...")
    run_superbonus_simulation(config, gamestate, num_features_requested)
    
    # Update book file path
    book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    # Analyze books
    print("\n" + "="*80)
    print("ANALYZING FEATURE WINS (AFTER RE-BALANCING)")
    print("="*80 + "\n")
    
    analysis_data = analyze_superbonus_books(book_file, exclude_wincap=True)
    
    # Calculate statistics
    print("\n" + "="*80)
    print("CALCULATING STATISTICS")
    print("="*80 + "\n")
    
    new_stats = calculate_statistics(analysis_data['feature_wins'], buy_cost=400.0)
    
    # Generate verification report
    print("\n" + "="*80)
    print("GENERATING VERIFICATION REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "SUPERBONUS_BALANCE_VERIFICATION.md"
    )
    
    generate_verification_report(PREVIOUS_255X, PREVIOUS_1006X, new_stats, output_file=output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

