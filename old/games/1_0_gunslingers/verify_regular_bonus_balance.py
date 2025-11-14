#!/usr/bin/env python3
"""
Verify REGULAR BONUS balance after FR0.csv rebalancing.

This script:
1. Runs a fresh simulation with the rebalanced FR0.csv
2. Analyzes feature-level wins (excluding wincap)
3. Generates a comprehensive verification report
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


def generate_verification_report(stats, analysis_data, output_file=None):
    """Generate a comprehensive verification report."""
    
    # Check if max win is hitting the cap
    max_win_note = ""
    if stats['max_win'] >= stats['win_cap']:
        max_win_note = f" (hitting {stats['win_cap']:.0f}× cap)"
    
    # Target assessment
    target_avg = 96.2
    avg_diff = stats['avg_feature_win'] - target_avg
    avg_diff_pct = (avg_diff / target_avg) * 100
    
    # Determine status
    if abs(avg_diff) <= 5:
        avg_status = "✅ ON TARGET"
        avg_assessment = f"Average feature win ({stats['avg_feature_win']:.2f}×) is within ±5× of target (96.2×)"
    elif avg_diff < -5:
        avg_status = "⚠️  BELOW TARGET"
        avg_assessment = f"Average feature win ({stats['avg_feature_win']:.2f}×) is {abs(avg_diff):.2f}× below target (96.2×)"
    else:
        avg_status = "⚠️  ABOVE TARGET"
        avg_assessment = f"Average feature win ({stats['avg_feature_win']:.2f}×) is {avg_diff:.2f}× above target (96.2×)"
    
    report = f"""# REGULAR BONUS Balance Verification Report

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

### Target Assessment

**Status**: {avg_status}

{avg_assessment}

- **Difference**: {avg_diff:+.2f}× ({avg_diff_pct:+.2f}%)
- **Target Range**: 91.2× - 101.2× (±5× from 96.2×)

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

## Summary & Assessment

### RTP Performance

- **Average Feature Win**: {stats['avg_feature_win']:.2f}× bet
- **Effective RTP**: {stats['effective_rtp']*100:.2f}%
- **Target**: 96.2× (96.2% RTP)
- **Status**: {avg_status}

### Volatility Profile

- **Below Cost (< {stats['buy_cost']:.0f}×)**: {stats['below_cost_pct']:.2f}% of features
- **Above Cost (≥ {stats['buy_cost']:.0f}×)**: {stats['above_cost_pct']:.2f}% of features
- **500×+ Hits**: {stats['above_500_pct']:.2f}% of features ({stats['above_500_count']:,} features)
- **Max Win Cap Hits**: {stats['hit_cap_pct']:.4f}% of features ({stats['hit_cap_count']:,} features)

### Comparison to Superbonus

The regular bonus should have **lower volatility** than the superbonus (400× buy):
- Regular bonus 500×+ rate: {stats['above_500_pct']:.2f}%
- Expected superbonus 500×+ rate: ~5-8%
- **Assessment**: {"✅ Lower volatility (as expected)" if stats['above_500_pct'] < 5.0 else "⚠️  Similar or higher volatility than expected"}

---

## Recommendations

"""
    
    # Add recommendations based on results
    if abs(avg_diff) <= 5:
        report += f"""
**RTP Status**: ✅ **ON TARGET**

The average feature win ({stats['avg_feature_win']:.2f}×) is within the acceptable range (91.2× - 101.2×).
The rebalancing was successful in bringing RTP from 46.39% to {stats['effective_rtp']*100:.2f}%.

**No further tuning required** for RTP target.
"""
    elif avg_diff < -5:
        deficit = abs(avg_diff)
        rtp_deficit = (deficit / stats['buy_cost']) * 100
        report += f"""
**RTP Status**: ⚠️  **BELOW TARGET**

The average feature win ({stats['avg_feature_win']:.2f}×) is {deficit:.2f}× below target (96.2×).
This represents a {rtp_deficit:.2f}% RTP deficit.

**Recommended Actions**:
1. **Increase H3 density** by ~{int(deficit * 0.6)}-{int(deficit * 0.8)} symbols (from 225 to ~{225 + int(deficit * 0.6)}-{225 + int(deficit * 0.8)})
2. **Increase VS frequency** by ~{int(deficit * 0.15)}-{int(deficit * 0.2)} symbols (from 25 to ~{25 + int(deficit * 0.15)}-{25 + int(deficit * 0.2)})
3. **Slightly increase H2/H4** to balance premium distribution

**Expected Impact**: These changes should increase average feature win by ~{deficit:.2f}×, bringing RTP closer to 96.2%.
"""
    else:
        excess = avg_diff
        rtp_excess = (excess / stats['buy_cost']) * 100
        report += f"""
**RTP Status**: ⚠️  **ABOVE TARGET**

The average feature win ({stats['avg_feature_win']:.2f}×) is {excess:.2f}× above target (96.2×).
This represents a {rtp_excess:.2f}% RTP excess.

**Recommended Actions**:
1. **Reduce H3 density** by ~{int(excess * 0.5)}-{int(excess * 0.7)} symbols (from 225 to ~{225 - int(excess * 0.7)}-{225 - int(excess * 0.5)})
2. **Slightly reduce VS frequency** if needed
3. **Slightly increase low symbols** (L1-L3) to balance distribution

**Expected Impact**: These changes should decrease average feature win by ~{excess:.2f}×, bringing RTP closer to 96.2%.
"""
    
    # Volatility assessment
    if stats['above_500_pct'] < 3.0:
        report += f"""
**Volatility Status**: ⚠️  **LOW VOLATILITY**

The 500×+ hit rate ({stats['above_500_pct']:.2f}%) is lower than expected for a bonus feature.
Consider slightly increasing VS frequency or high-tier multipliers to boost big win potential.
"""
    elif stats['above_500_pct'] > 5.0:
        report += f"""
**Volatility Status**: ⚠️  **HIGH VOLATILITY**

The 500×+ hit rate ({stats['above_500_pct']:.2f}%) is higher than expected for regular bonus.
This may be acceptable, but consider if it's too close to superbonus volatility.
"""
    else:
        report += f"""
**Volatility Status**: ✅ **APPROPRIATE**

The 500×+ hit rate ({stats['above_500_pct']:.2f}%) is within expected range for regular bonus.
Volatility is appropriately lower than superbonus (400× buy).
"""
    
    report += f"""

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
    print("REGULAR BONUS BALANCE VERIFICATION")
    print("="*80)
    
    # Initialize config and gamestate
    config = GameConfig()
    gamestate = GameState(config)
    
    # Path to books file
    book_file = os.path.join(config.publish_path, "books_bonus.jsonl.zst")
    
    # Always run fresh simulation with rebalanced FR0.csv
    num_features_requested = 100000
    print(f"\n⚠️  Running fresh simulation with rebalanced FR0.csv...")
    print(f"    This will overwrite existing books_bonus.jsonl.zst")
    
    # Run simulation
    run_bonus_simulation(config, gamestate, num_features_requested)
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
    print(f"Target: 96.2× (96.2% RTP)")
    print(f"Difference: {stats['avg_feature_win'] - 96.2:+.2f}×")
    print(f"Median: {stats['median_win']:.2f}× bet")
    print(f"Min: {stats['min_win']:.2f}× bet")
    print(f"Max: {stats['max_win']:.2f}× bet")
    print(f"Below Cost (< {stats['buy_cost']:.0f}×): {stats['below_cost_pct']:.2f}%")
    print(f"Above Cost (≥ {stats['buy_cost']:.0f}×): {stats['above_cost_pct']:.2f}%")
    print(f"500×+: {stats['above_500_pct']:.2f}%")
    print(f"Cap Hit Rate: {stats['hit_cap_pct']:.4f}%")
    
    # Generate report
    print("\n" + "="*80)
    print("GENERATING VERIFICATION REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "REGULAR_BONUS_BALANCE_VERIFICATION.md"
    )
    
    generate_verification_report(stats, analysis_data, output_file=output_file)
    
    # Final assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    target_avg = 96.2
    avg_diff = stats['avg_feature_win'] - target_avg
    
    print(f"\n✅ Average Feature Win: {stats['avg_feature_win']:.2f}×")
    if abs(avg_diff) <= 5:
        print(f"   Status: ✅ ON TARGET (within ±5× of {target_avg}×)")
    else:
        direction = "below" if avg_diff < 0 else "above"
        print(f"   Status: ⚠️  {abs(avg_diff):.2f}× {direction} target ({target_avg}×)")
    
    print(f"\n✅ Volatility Profile:")
    print(f"   500×+ Hits: {stats['above_500_pct']:.2f}%")
    if stats['above_500_pct'] < 3.0:
        print(f"   Status: ⚠️  Low volatility (consider increasing VS)")
    elif stats['above_500_pct'] > 5.0:
        print(f"   Status: ⚠️  High volatility (may be too close to superbonus)")
    else:
        print(f"   Status: ✅ Appropriate for regular bonus")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

