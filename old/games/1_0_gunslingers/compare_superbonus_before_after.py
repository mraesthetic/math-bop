#!/usr/bin/env python3
"""
Compare SUPERBONUS volatility before and after FR1.csv modifications.

This script:
1. Runs fresh 100k superbonus simulation with modified FR1.csv
2. Analyzes results (excluding wincap)
3. Compares to previous baseline results
4. Generates BEFORE vs AFTER comparison report
"""

import json
import os
import sys
import zstandard as zst
from io import TextIOWrapper
from collections import defaultdict
from pathlib import Path
import statistics

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_config import GameConfig
from gamestate import GameState
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


# Previous baseline results (from SUPERBONUS_VOLATILITY_REPORT.md)
BASELINE_RESULTS = {
    'avg_feature_win': 394.05,
    'effective_rtp': 0.9851,
    'num_features': 99900,  # 100k - 100 wincap
    'bucket_percentages': {
        '< 25×': 0.90,
        '25–50×': 2.51,
        '50–100×': 9.14,
        '100–250×': 32.76,
        '250–500×': 31.07,
        '500–1000×': 17.43,
        '1000×+': 6.19,
    },
    'below_cost_pct': 67.49,
    'above_cost_pct': 32.51,
    'above_800_pct': 10.05,
    'above_1000_pct': 6.19,
    'hit_cap_pct': 0.0150,
    'hit_cap_count': 15,
}


def run_superbonus_simulation(config, gamestate, num_features=100000):
    """Run simulation for superbonus mode only."""
    print(f"\n{'='*80}")
    print(f"Running SUPERBONUS simulation: {num_features:,} features")
    print(f"Using modified FR1.csv")
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
    """
    Analyze superbonus books to extract feature win distribution.
    
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


def calculate_statistics(feature_wins, buy_cost=400.0):
    """Calculate comprehensive statistics for superbonus features."""
    if not feature_wins:
        raise ValueError("No feature wins to analyze!")
    
    num_features = len(feature_wins)
    
    # Core numbers
    avg_feature_win = sum(feature_wins) / num_features
    effective_rtp = avg_feature_win / buy_cost
    
    # Win thresholds
    win_cap = 10000.0  # From config
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
        'median_win': statistics.median(feature_wins),
        'min_win': min(feature_wins),
        'max_win': max(feature_wins),
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


def generate_comparison_report(baseline_stats, new_stats, output_file=None):
    """Generate a markdown report comparing before and after."""
    
    report = f"""# SUPERBONUS Volatility Comparison: BEFORE vs AFTER FR1 Modification

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

---

## Core Statistics Comparison

| Metric | BEFORE | AFTER | Change | Status |
|--------|--------|-------|--------|--------|
| **Average Feature Win** | {baseline_stats['avg_feature_win']:.2f}× | {new_stats['avg_feature_win']:.2f}× | {new_stats['avg_feature_win'] - baseline_stats['avg_feature_win']:+.2f}× | {"✅" if 379 <= new_stats['avg_feature_win'] <= 389 else "⚠️"} |
| **Effective RTP** | {baseline_stats['effective_rtp']*100:.2f}% | {new_stats['effective_rtp']*100:.2f}% | {(new_stats['effective_rtp'] - baseline_stats['effective_rtp'])*100:+.2f}% | |
| **Target RTP** | 96.2% | 96.2% | - | |
| **Median Feature Win** | - | {new_stats['median_win']:.2f}× | - | |
| **Min Feature Win** | - | {new_stats['min_win']:.2f}× | - | |
| **Max Feature Win** | - | {new_stats['max_win']:.2f}× | - | |

---

## Win Distribution by Bucket

| Bucket | BEFORE | AFTER | Change | % Change |
|--------|--------|-------|--------|----------|
| **< 25×** | {baseline_stats['bucket_percentages']['< 25×']:.2f}% | {new_stats['bucket_percentages']['< 25×']:.2f}% | {new_stats['bucket_percentages']['< 25×'] - baseline_stats['bucket_percentages']['< 25×']:+.2f}% | {((new_stats['bucket_percentages']['< 25×'] - baseline_stats['bucket_percentages']['< 25×']) / baseline_stats['bucket_percentages']['< 25×'] * 100) if baseline_stats['bucket_percentages']['< 25×'] > 0 else 0:+.1f}% |
| **25–50×** | {baseline_stats['bucket_percentages']['25–50×']:.2f}% | {new_stats['bucket_percentages']['25–50×']:.2f}% | {new_stats['bucket_percentages']['25–50×'] - baseline_stats['bucket_percentages']['25–50×']:+.2f}% | {((new_stats['bucket_percentages']['25–50×'] - baseline_stats['bucket_percentages']['25–50×']) / baseline_stats['bucket_percentages']['25–50×'] * 100) if baseline_stats['bucket_percentages']['25–50×'] > 0 else 0:+.1f}% |
| **50–100×** | {baseline_stats['bucket_percentages']['50–100×']:.2f}% | {new_stats['bucket_percentages']['50–100×']:.2f}% | {new_stats['bucket_percentages']['50–100×'] - baseline_stats['bucket_percentages']['50–100×']:+.2f}% | {((new_stats['bucket_percentages']['50–100×'] - baseline_stats['bucket_percentages']['50–100×']) / baseline_stats['bucket_percentages']['50–100×'] * 100) if baseline_stats['bucket_percentages']['50–100×'] > 0 else 0:+.1f}% |
| **100–250×** | {baseline_stats['bucket_percentages']['100–250×']:.2f}% | {new_stats['bucket_percentages']['100–250×']:.2f}% | {new_stats['bucket_percentages']['100–250×'] - baseline_stats['bucket_percentages']['100–250×']:+.2f}% | {((new_stats['bucket_percentages']['100–250×'] - baseline_stats['bucket_percentages']['100–250×']) / baseline_stats['bucket_percentages']['100–250×'] * 100) if baseline_stats['bucket_percentages']['100–250×'] > 0 else 0:+.1f}% |
| **250–500×** | {baseline_stats['bucket_percentages']['250–500×']:.2f}% | {new_stats['bucket_percentages']['250–500×']:.2f}% | {new_stats['bucket_percentages']['250–500×'] - baseline_stats['bucket_percentages']['250–500×']:+.2f}% | {((new_stats['bucket_percentages']['250–500×'] - baseline_stats['bucket_percentages']['250–500×']) / baseline_stats['bucket_percentages']['250–500×'] * 100) if baseline_stats['bucket_percentages']['250–500×'] > 0 else 0:+.1f}% |
| **500–1000×** | {baseline_stats['bucket_percentages']['500–1000×']:.2f}% | {new_stats['bucket_percentages']['500–1000×']:.2f}% | {new_stats['bucket_percentages']['500–1000×'] - baseline_stats['bucket_percentages']['500–1000×']:+.2f}% | {((new_stats['bucket_percentages']['500–1000×'] - baseline_stats['bucket_percentages']['500–1000×']) / baseline_stats['bucket_percentages']['500–1000×'] * 100) if baseline_stats['bucket_percentages']['500–1000×'] > 0 else 0:+.1f}% |
| **1000×+** | {baseline_stats['bucket_percentages']['1000×+']:.2f}% | {new_stats['bucket_percentages']['1000×+']:.2f}% | {new_stats['bucket_percentages']['1000×+'] - baseline_stats['bucket_percentages']['1000×+']:+.2f}% | {((new_stats['bucket_percentages']['1000×+'] - baseline_stats['bucket_percentages']['1000×+']) / baseline_stats['bucket_percentages']['1000×+'] * 100) if baseline_stats['bucket_percentages']['1000×+'] > 0 else 0:+.1f}% |

---

## Performance vs Buy Cost

| Threshold | BEFORE | AFTER | Change |
|-----------|--------|-------|--------|
| **< 400×** (below cost) | {baseline_stats['below_cost_pct']:.2f}% | {new_stats['below_cost_pct']:.2f}% | {new_stats['below_cost_pct'] - baseline_stats['below_cost_pct']:+.2f}% |
| **≥ 400×** (at/above cost) | {baseline_stats['above_cost_pct']:.2f}% | {new_stats['above_cost_pct']:.2f}% | {new_stats['above_cost_pct'] - baseline_stats['above_cost_pct']:+.2f}% |
| **≥ 800×** | {baseline_stats['above_800_pct']:.2f}% | {new_stats['above_800_pct']:.2f}% | {new_stats['above_800_pct'] - baseline_stats['above_800_pct']:+.2f}% |
| **≥ 1000×** | {baseline_stats['above_1000_pct']:.2f}% | {new_stats['above_1000_pct']:.2f}% | {new_stats['above_1000_pct'] - baseline_stats['above_1000_pct']:+.2f}% |

---

## Max Win Cap

| Metric | BEFORE | AFTER | Change |
|--------|--------|-------|--------|
| **Win Cap** | 10,000× bet | 10,000× bet | - |
| **Features Hitting Cap** | {baseline_stats['hit_cap_count']} | {new_stats['hit_cap_count']} | {new_stats['hit_cap_count'] - baseline_stats['hit_cap_count']:+d} |
| **Cap Hit Rate** | {baseline_stats['hit_cap_pct']:.4f}% | {new_stats['hit_cap_pct']:.4f}% | {new_stats['hit_cap_pct'] - baseline_stats['hit_cap_pct']:+.4f}% |

---

## Interpretation

### RTP Balance Assessment

"""
    
    # Add RTP assessment
    avg_win = new_stats['avg_feature_win']
    if 379 <= avg_win <= 389:
        report += f"✅ **BALANCED**: Average feature win ({avg_win:.2f}×) is within target range (384× ± 5×)\n"
        report += "- RTP is properly balanced\n"
        report += "- No adjustments needed to FR1.csv\n\n"
    elif avg_win > 390:
        report += f"⚠️ **TOO GENEROUS**: Average feature win ({avg_win:.2f}×) exceeds target (384× + 5×)\n"
        report += f"- Current RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += "- **Recommendation**: Add some low symbols back to reduce average\n"
        report += "- Consider increasing L1/L2 density slightly\n\n"
    elif avg_win < 380:
        report += f"⚠️ **TOO TIGHT**: Average feature win ({avg_win:.2f}×) below target (384× - 5×)\n"
        report += f"- Current RTP: {new_stats['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += "- **Recommendation**: Add more premium symbols or wilds\n"
        report += "- Consider increasing H1/H2/H3 or W density slightly\n\n"
    
    # Volatility assessment
    dead_spin_change = new_stats['bucket_percentages']['< 25×'] - baseline_stats['bucket_percentages']['< 25×']
    big_win_change = new_stats['bucket_percentages']['1000×+'] - baseline_stats['bucket_percentages']['1000×+']
    medium_win_change = (new_stats['bucket_percentages']['100–250×'] + new_stats['bucket_percentages']['250–500×']) - (baseline_stats['bucket_percentages']['100–250×'] + baseline_stats['bucket_percentages']['250–500×'])
    
    report += "### Volatility Assessment\n\n"
    
    if dead_spin_change > 2:
        report += f"✅ **Dead spins increased**: <25× bucket increased by {dead_spin_change:.2f}% ({baseline_stats['bucket_percentages']['< 25×']:.2f}% → {new_stats['bucket_percentages']['< 25×']:.2f}%)\n"
        report += "- More complete whiffs (as intended)\n\n"
    else:
        report += f"⚠️ **Dead spins not significantly increased**: <25× bucket changed by {dead_spin_change:+.2f}%\n\n"
    
    if big_win_change > 2:
        report += f"✅ **Big wins increased**: 1000×+ bucket increased by {big_win_change:.2f}% ({baseline_stats['bucket_percentages']['1000×+']:.2f}% → {new_stats['bucket_percentages']['1000×+']:.2f}%)\n"
        report += "- More premium spikes (as intended)\n\n"
    else:
        report += f"⚠️ **Big wins not significantly increased**: 1000×+ bucket changed by {big_win_change:+.2f}%\n\n"
    
    if medium_win_change < -5:
        report += f"✅ **Medium wins reduced**: 100–500× range decreased by {abs(medium_win_change):.2f}%\n"
        report += "- Fewer flat medium wins (as intended)\n\n"
    else:
        report += f"⚠️ **Medium wins not significantly reduced**: 100–500× range changed by {medium_win_change:+.2f}%\n\n"
    
    report += "### Summary\n\n"
    report += f"- **Features Analyzed**: {new_stats['num_features']:,} (wincap excluded)\n"
    report += f"- **Average Feature Win**: {new_stats['avg_feature_win']:.2f}× bet\n"
    report += f"- **Effective RTP**: {new_stats['effective_rtp']*100:.2f}%\n"
    report += f"- **Below Cost**: {new_stats['below_cost_pct']:.2f}% of features\n"
    report += f"- **Above Cost**: {new_stats['above_cost_pct']:.2f}% of features\n"
    report += f"- **1000×+ Hits**: {new_stats['above_1000_pct']:.2f}% of features\n"
    report += f"- **Cap Hits**: {new_stats['hit_cap_pct']:.4f}% of features ({new_stats['hit_cap_count']} features)\n\n"
    
    report += f"**Analysis Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✓ Comparison report saved to: {output_file}")
    else:
        print(report)
    
    return report


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("SUPERBONUS BEFORE/AFTER COMPARISON")
    print("="*80)
    
    # Initialize config and gamestate
    config = GameConfig()
    gamestate = GameState(config)
    
    # Path to books file
    book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    # Check if we need to run simulation
    num_features_requested = 100000
    run_simulation = False
    
    if not os.path.exists(book_file):
        print(f"⚠️  Book file not found. Running new simulation.")
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
            
            # Always run new simulation to get fresh results with modified FR1.csv
            print(f"⚠️  Running fresh simulation with modified FR1.csv...")
            run_simulation = True
        except Exception as e:
            print(f"⚠️  Error reading existing file: {e}. Running new simulation.")
            run_simulation = True
    
    # Run simulation if needed
    if run_simulation:
        run_superbonus_simulation(config, gamestate, num_features_requested)
        # Update book file path (may have changed)
        book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    # Analyze books
    print("\n" + "="*80)
    print("ANALYZING FEATURE WINS (AFTER MODIFICATION)")
    print("="*80 + "\n")
    
    analysis_data = analyze_superbonus_books(book_file, exclude_wincap=True)
    
    # Calculate statistics
    print("\n" + "="*80)
    print("CALCULATING STATISTICS")
    print("="*80 + "\n")
    
    new_stats = calculate_statistics(analysis_data['feature_wins'], buy_cost=400.0)
    
    # Generate comparison report
    print("\n" + "="*80)
    print("GENERATING COMPARISON REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "SUPERBONUS_BEFORE_AFTER_COMPARISON.md"
    )
    
    generate_comparison_report(BASELINE_RESULTS, new_stats, output_file=output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

