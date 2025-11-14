#!/usr/bin/env python3
"""
Analyze REGULAR BONUS feature volatility and win distribution.

This script:
1. Runs 100k regular bonus feature simulations (if needed)
2. Analyzes feature-level wins (excluding wincap)
3. Generates a detailed markdown report with bucket distribution
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


def run_bonus_simulation(config, gamestate, num_features=100000):
    """Run simulation for regular bonus mode only."""
    print(f"\n{'='*80}")
    print(f"Running REGULAR BONUS simulation: {num_features:,} features")
    print(f"{'='*80}\n")
    
    num_threads = 10
    batching_size = 5000
    compression = True
    profiling = False
    
    # Run simulation for bonus only
    num_sim_args = {
        "bonus": num_features,
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
    
    print(f"\n✓ Simulation complete: {num_features:,} regular bonus features\n")


def analyze_bonus_books(book_file_path: str, exclude_wincap: bool = True):
    """
    Analyze regular bonus books to extract feature win distribution.
    
    Returns:
        dict with feature wins and statistics
    """
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
                
                # Get feature win from payoutMultiplier (stored in cents, convert to bet multiplier)
                payout_mult = blob.get("payoutMultiplier", 0) / 100.0
                criteria = blob.get("criteria", "")
                
                total_features += 1
                
                # Filter out wincap if requested
                if exclude_wincap and criteria == "wincap":
                    wincap_count += 1
                    continue
                
                feature_wins.append(payout_mult)
                
                # Progress indicator
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num:,} features...", end='\r')
    
    print(f"\n✓ Analyzed {total_features:,} features (excluded {wincap_count:,} wincap)\n")
    
    return {
        'feature_wins': feature_wins,
        'total_features': total_features,
        'wincap_count': wincap_count,
        'analyzed_features': len(feature_wins),
    }


def calculate_statistics(feature_wins, buy_cost=100.0):
    """Calculate comprehensive statistics for regular bonus features."""
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
    win_cap = 10000.0  # From config
    below_cost = sum(1 for w in feature_wins if w < buy_cost)
    above_cost = sum(1 for w in feature_wins if w >= buy_cost)
    above_200 = sum(1 for w in feature_wins if w >= 200.0)
    above_500 = sum(1 for w in feature_wins if w >= 500.0)
    hit_cap = sum(1 for w in feature_wins if w >= win_cap)
    
    # Bucket distribution (as requested: < 10×, 10–25×, 25–50×, 50–100×, 100–250×, 250–500×, 500×+)
    buckets = {
        '< 10×': (0, 10),
        '10–25×': (10, 25),
        '25–50×': (25, 50),
        '50–100×': (50, 100),
        '100–250×': (100, 250),
        '250–500×': (250, 500),
        '500×+': (500, float('inf')),
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
        'median_win': median_win,
        'min_win': min_win,
        'max_win': max_win,
        'buy_cost': buy_cost,
        'win_cap': win_cap,
        'below_cost_count': below_cost,
        'below_cost_pct': (below_cost / num_features) * 100.0,
        'above_cost_count': above_cost,
        'above_cost_pct': (above_cost / num_features) * 100.0,
        'above_200_count': above_200,
        'above_200_pct': (above_200 / num_features) * 100.0,
        'above_500_count': above_500,
        'above_500_pct': (above_500 / num_features) * 100.0,
        'hit_cap_count': hit_cap,
        'hit_cap_pct': (hit_cap / num_features) * 100.0,
        'bucket_counts': bucket_counts,
        'bucket_percentages': bucket_percentages,
    }


def generate_markdown_report(stats, analysis_data, output_file=None):
    """Generate a markdown report with all statistics."""
    
    # Check if max win is hitting the cap
    max_win_note = ""
    if stats['max_win'] >= stats['win_cap']:
        max_win_note = f" (hitting {stats['win_cap']:.0f}× cap)"
    
    report = f"""# REGULAR BONUS Feature Volatility & RTP Analysis

**Game**: Gunslingers: DRAW!  
**Bet Mode**: bonus (DRAW! YOUR WEAPON)  
**Buy Cost**: {stats['buy_cost']:.0f}× bet  
**Features Analyzed**: {stats['num_features']:,} (wincap excluded)  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Core Statistics

| Metric | Value |
|--------|-------|
| **Average Feature Win** | {stats['avg_feature_win']:.2f}× bet |
| **Effective RTP** | {stats['effective_rtp']*100:.2f}% ({stats['effective_rtp']:.4f}) |
| **Target RTP** | 96.2% (96.2× / 100×) |
| **Median Feature Win** | {stats['median_win']:.2f}× bet |
| **Min Feature Win** | {stats['min_win']:.2f}× bet |
| **Max Feature Win** | {stats['max_win']:.2f}× bet{max_win_note} |

---

## Win Distribution by Bucket

| Bucket | Features | Percentage |
|--------|----------|------------|
| **< 10×** | {stats['bucket_counts']['< 10×']:,} | {stats['bucket_percentages']['< 10×']:.2f}% |
| **10–25×** | {stats['bucket_counts']['10–25×']:,} | {stats['bucket_percentages']['10–25×']:.2f}% |
| **25–50×** | {stats['bucket_counts']['25–50×']:,} | {stats['bucket_percentages']['25–50×']:.2f}% |
| **50–100×** | {stats['bucket_counts']['50–100×']:,} | {stats['bucket_percentages']['50–100×']:.2f}% |
| **100–250×** | {stats['bucket_counts']['100–250×']:,} | {stats['bucket_percentages']['100–250×']:.2f}% |
| **250–500×** | {stats['bucket_counts']['250–500×']:,} | {stats['bucket_percentages']['250–500×']:.2f}% |
| **500×+** | {stats['bucket_counts']['500×+']:,} | {stats['bucket_percentages']['500×+']:.2f}% |

---

## Performance vs Buy Cost

| Threshold | Count | Percentage |
|-----------|-------|------------|
| **< {stats['buy_cost']:.0f}×** (below cost) | {stats['below_cost_count']:,} | {stats['below_cost_pct']:.2f}% |
| **≥ {stats['buy_cost']:.0f}×** (at/above cost) | {stats['above_cost_count']:,} | {stats['above_cost_pct']:.2f}% |
| **≥ 200×** | {stats['above_200_count']:,} | {stats['above_200_pct']:.2f}% |
| **≥ 500×** | {stats['above_500_count']:,} | {stats['above_500_pct']:.2f}% |

---

## Max Win Cap Statistics

| Metric | Value |
|--------|-------|
| **Win Cap** | {stats['win_cap']:.0f}× bet |
| **Features Hitting Cap** | {stats['hit_cap_count']:,} |
| **Cap Hit Rate** | {stats['hit_cap_pct']:.4f}% |
| **Total Features** (including cap) | {analysis_data['total_features']:,} |
| **Wincap Features Excluded** | {analysis_data['wincap_count']:,} |

---

## Summary

- **Average Feature Win**: {stats['avg_feature_win']:.2f}× bet
- **Effective RTP**: {stats['effective_rtp']*100:.2f}%
- **Below Cost (< {stats['buy_cost']:.0f}×)**: {stats['below_cost_pct']:.2f}% of features
- **Above Cost (≥ {stats['buy_cost']:.0f}×)**: {stats['above_cost_pct']:.2f}% of features
- **500×+ Hits**: {stats['above_500_pct']:.2f}% of features ({stats['above_500_count']:,} features)
- **Max Win Cap Hits**: {stats['hit_cap_pct']:.4f}% of features ({stats['hit_cap_count']:,} features)

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
    print("REGULAR BONUS VOLATILITY & RTP ANALYSIS")
    print("="*80)
    
    # Initialize config and gamestate
    config = GameConfig()
    gamestate = GameState(config)
    
    # Path to books file
    book_file = os.path.join(config.publish_path, "books_bonus.jsonl.zst")
    
    # Check if we need to run simulation
    num_features_requested = 100000
    run_simulation = False
    
    if not os.path.exists(book_file):
        print(f"⚠️  Book file not found. Will run new simulation.")
        run_simulation = True
    else:
        # Check how many features we have
        print("Checking existing simulation data...")
        try:
            with open(book_file, "rb") as f:
                decompressor = zst.ZstdDecompressor()
                with decompressor.stream_reader(f) as reader:
                    txt_stream = TextIOWrapper(reader, encoding="UTF-8")
                    existing_count = sum(1 for line in txt_stream if line.strip())
            
            print(f"Found {existing_count:,} existing features in books file")
            
            if existing_count < num_features_requested:
                print(f"⚠️  Not enough features ({existing_count:,} < {num_features_requested:,}). Will run new simulation.")
                run_simulation = True
            else:
                print(f"✓ Sufficient features found. Using existing data.")
        except Exception as e:
            print(f"⚠️  Error reading existing file: {e}. Will run new simulation.")
            run_simulation = True
    
    # Run simulation if needed
    if run_simulation:
        run_bonus_simulation(config, gamestate, num_features_requested)
        # Update book file path (may have changed)
        book_file = os.path.join(config.publish_path, "books_bonus.jsonl.zst")
    
    # Analyze books
    print("\n" + "="*80)
    print("ANALYZING FEATURE WINS")
    print("="*80 + "\n")
    
    analysis_data = analyze_bonus_books(book_file, exclude_wincap=True)
    
    # Calculate statistics
    print("\n" + "="*80)
    print("CALCULATING STATISTICS")
    print("="*80 + "\n")
    
    stats = calculate_statistics(analysis_data['feature_wins'], buy_cost=100.0)
    
    # Print quick summary
    print("\n" + "="*80)
    print("QUICK SUMMARY")
    print("="*80)
    print(f"Average Feature Win: {stats['avg_feature_win']:.2f}× bet")
    print(f"Effective RTP: {stats['effective_rtp']*100:.2f}%")
    print(f"Median: {stats['median_win']:.2f}× bet")
    print(f"Min: {stats['min_win']:.2f}× bet")
    print(f"Max: {stats['max_win']:.2f}× bet")
    print(f"Below Cost (< {stats['buy_cost']:.0f}×): {stats['below_cost_pct']:.2f}%")
    print(f"Above Cost (≥ {stats['buy_cost']:.0f}×): {stats['above_cost_pct']:.2f}%")
    print(f"500×+: {stats['above_500_pct']:.2f}%")
    print(f"Cap Hit Rate: {stats['hit_cap_pct']:.4f}%")
    
    # Generate report
    print("\n" + "="*80)
    print("GENERATING REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "REGULAR_BONUS_VOLATILITY_RTP_REPORT.md"
    )
    
    generate_markdown_report(stats, analysis_data, output_file=output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

