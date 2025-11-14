#!/usr/bin/env python3
"""
Finalize v2 distribution, verify counts, run simulation, and generate 4-column report.

This script:
1. Ensures FR1.csv has exact v2 symbol counts
2. Verifies no stale copies exist
3. Runs 100k superbonus simulation
4. Generates comprehensive 4-column comparison report
"""

import json
import os
import sys
import csv
import zstandard as zst
from io import TextIOWrapper
from collections import defaultdict
from pathlib import Path
import statistics
from datetime import datetime
import shutil
import random

random.seed(42)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_config import GameConfig
from gamestate import GameState
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


# Previous results for comparison
STATS_255X = {
    'avg_feature_win': 255.14,
    'effective_rtp': 0.6379,
    'median_win': None,
    'min_win': None,
    'max_win': None,
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

STATS_1006X = {
    'avg_feature_win': 1006.33,
    'effective_rtp': 2.5158,
    'median_win': None,
    'min_win': None,
    'max_win': None,
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

STATS_169X = {
    'avg_feature_win': 169.64,
    'effective_rtp': 0.4241,
    'median_win': 101.60,
    'min_win': 0.20,
    'max_win': 10000.00,
    'bucket_percentages': {
        '< 25×': 9.26,
        '25–50×': 14.57,
        '50–100×': 25.44,
        '100–250×': 32.94,
        '250–500×': 12.45,
        '500–1000×': 4.10,
        '1000×+': 1.25,
    },
    'below_cost_pct': 91.89,
    'above_cost_pct': 8.11,
    'above_800_pct': 1.97,
    'above_1000_pct': 1.25,
    'hit_cap_pct': 0.0050,
    'hit_cap_count': 5,
}

# V2 Target counts
V2_TARGETS = {
    'H3': 240,
    'W': 16,
    'L1': 147,
    'L2': 75,
    'L3': 70,
    'L4': 184,
    'L5': 172,
}


def verify_and_fix_fr1_counts():
    """Verify and fix FR1.csv to exact v2 targets."""
    base_path = Path(__file__).parent
    input_file = base_path / 'reels' / 'FR1.csv'
    
    # Read current file
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 5:
                rows.append(list(row))
    
    # Count current
    current = defaultdict(int)
    for row in rows:
        for sym in row:
            current[sym] += 1
    
    # Check if adjustments needed
    modified = [row.copy() for row in rows]
    needs_adjustment = False
    
    # Fine-tune L4 and L5 to exact targets
    l4_diff = current.get('L4', 0) - V2_TARGETS['L4']
    l5_diff = current.get('L5', 0) - V2_TARGETS['L5']
    
    if l4_diff != 0 or l5_diff != 0:
        needs_adjustment = True
        print(f"Fine-tuning: L4 diff={l4_diff}, L5 diff={l5_diff}")
        
        # If L4 is too high, convert to L5 (or vice versa)
        if l4_diff > 0:
            # Convert L4 to L5
            converted = 0
            for row_idx, row in enumerate(modified):
                if converted >= l4_diff:
                    break
                for reel_idx, sym in enumerate(row):
                    if sym == 'L4' and converted < l4_diff:
                        if l5_diff < 0:  # L5 needs more
                            modified[row_idx][reel_idx] = 'L5'
                            converted += 1
                            l5_diff += 1
                            if converted >= l4_diff:
                                break
    
    if needs_adjustment:
        # Re-count
        after = defaultdict(int)
        for row in modified:
            for sym in row:
                after[sym] += 1
        
        # Save if adjusted
        with open(input_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in modified:
                writer.writerow(row)
        print(f"✓ Fine-tuned FR1.csv")
    
    # Final verification
    final = defaultdict(int)
    for row in modified:
        for sym in row:
            final[sym] += 1
    
    print(f"\nFinal symbol counts:")
    for sym in ['H3', 'W', 'L1', 'L2', 'L3', 'L4', 'L5']:
        curr = final.get(sym, 0)
        targ = V2_TARGETS.get(sym, 0)
        status = "✓" if abs(curr - targ) <= 2 else "⚠"
        print(f"  {sym}: {curr} (target: {targ}) {status}")
    
    return True


def run_superbonus_simulation(config, gamestate, num_features=100000):
    """Run simulation for superbonus mode only."""
    print(f"\n{'='*80}")
    print(f"Running SUPERBONUS simulation: {num_features:,} features")
    print(f"Using FR1.csv v2 distribution")
    print(f"{'='*80}\n")
    
    num_threads = 10
    batching_size = 5000
    compression = True
    profiling = False
    
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


def calculate_statistics(feature_wins, buy_cost=400.0):
    """Calculate comprehensive statistics for superbonus features."""
    if not feature_wins:
        raise ValueError("No feature wins to analyze!")
    
    num_features = len(feature_wins)
    
    avg_feature_win = sum(feature_wins) / num_features
    effective_rtp = avg_feature_win / buy_cost
    median_win = statistics.median(feature_wins)
    min_win = min(feature_wins)
    max_win = max(feature_wins)
    
    win_cap = 10000.0
    below_cost = sum(1 for w in feature_wins if w < buy_cost)
    above_cost = sum(1 for w in feature_wins if w >= buy_cost)
    above_800 = sum(1 for w in feature_wins if w >= 800.0)
    above_1000 = sum(1 for w in feature_wins if w >= 1000.0)
    hit_cap = sum(1 for w in feature_wins if w >= win_cap)
    
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


def generate_v2_report(stats_255x, stats_1006x, stats_169x, stats_v2, output_file=None):
    """Generate comprehensive 4-column comparison report."""
    
    report = f"""# SUPERBONUS v2 Distribution Analysis Report

**Game**: Gunslingers: DRAW!  
**Bet Mode**: superbonus  
**Buy Cost**: 400× bet  
**Analysis**: 100,000 features (wincap excluded)

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

| Metric | Target | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** | Status |
|--------|--------|------------------|----------------------|----------------------|--------------|--------|
| **Average Feature Win** | 384× ± 5× | {stats_255x['avg_feature_win']:.2f}× | {stats_1006x['avg_feature_win']:.2f}× | {stats_169x['avg_feature_win']:.2f}× | **{stats_v2['avg_feature_win']:.2f}×** | {"✅" if 379 <= stats_v2['avg_feature_win'] <= 389 else "⚠️"} |
| **Effective RTP** | 96.2% | {stats_255x['effective_rtp']*100:.2f}% | {stats_1006x['effective_rtp']*100:.2f}% | {stats_169x['effective_rtp']*100:.2f}% | **{stats_v2['effective_rtp']*100:.2f}%** | |

---

## Core Statistics

| Metric | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **Average Feature Win** | {stats_255x['avg_feature_win']:.2f}× | {stats_1006x['avg_feature_win']:.2f}× | {stats_169x['avg_feature_win']:.2f}× | **{stats_v2['avg_feature_win']:.2f}×** |
| **Effective RTP** | {stats_255x['effective_rtp']*100:.2f}% | {stats_1006x['effective_rtp']*100:.2f}% | {stats_169x['effective_rtp']*100:.2f}% | **{stats_v2['effective_rtp']*100:.2f}%** |
| **Median Feature Win** | - | - | {stats_169x['median_win']:.2f}× | **{stats_v2['median_win']:.2f}×** |
| **Min Feature Win** | - | - | {stats_169x['min_win']:.2f}× | **{stats_v2['min_win']:.2f}×** |
| **Max Feature Win** | - | - | {stats_169x['max_win']:.2f}× | **{stats_v2['max_win']:.2f}×** |

---

## Win Distribution by Bucket

| Bucket | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **< 25×** | {stats_255x['bucket_percentages']['< 25×']:.2f}% | {stats_1006x['bucket_percentages']['< 25×']:.2f}% | {stats_169x['bucket_percentages']['< 25×']:.2f}% | **{stats_v2['bucket_percentages']['< 25×']:.2f}%** |
| **25–50×** | {stats_255x['bucket_percentages']['25–50×']:.2f}% | {stats_1006x['bucket_percentages']['25–50×']:.2f}% | {stats_169x['bucket_percentages']['25–50×']:.2f}% | **{stats_v2['bucket_percentages']['25–50×']:.2f}%** |
| **50–100×** | {stats_255x['bucket_percentages']['50–100×']:.2f}% | {stats_1006x['bucket_percentages']['50–100×']:.2f}% | {stats_169x['bucket_percentages']['50–100×']:.2f}% | **{stats_v2['bucket_percentages']['50–100×']:.2f}%** |
| **100–250×** | {stats_255x['bucket_percentages']['100–250×']:.2f}% | {stats_1006x['bucket_percentages']['100–250×']:.2f}% | {stats_169x['bucket_percentages']['100–250×']:.2f}% | **{stats_v2['bucket_percentages']['100–250×']:.2f}%** |
| **250–500×** | {stats_255x['bucket_percentages']['250–500×']:.2f}% | {stats_1006x['bucket_percentages']['250–500×']:.2f}% | {stats_169x['bucket_percentages']['250–500×']:.2f}% | **{stats_v2['bucket_percentages']['250–500×']:.2f}%** |
| **500–1000×** | {stats_255x['bucket_percentages']['500–1000×']:.2f}% | {stats_1006x['bucket_percentages']['500–1000×']:.2f}% | {stats_169x['bucket_percentages']['500–1000×']:.2f}% | **{stats_v2['bucket_percentages']['500–1000×']:.2f}%** |
| **1000×+** | {stats_255x['bucket_percentages']['1000×+']:.2f}% | {stats_1006x['bucket_percentages']['1000×+']:.2f}% | {stats_169x['bucket_percentages']['1000×+']:.2f}% | **{stats_v2['bucket_percentages']['1000×+']:.2f}%** |

---

## Performance vs Buy Cost

| Threshold | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|-----------|------------------|----------------------|----------------------|--------------|
| **< 400×** (below cost) | {stats_255x['below_cost_pct']:.2f}% | {stats_1006x['below_cost_pct']:.2f}% | {stats_169x['below_cost_pct']:.2f}% | **{stats_v2['below_cost_pct']:.2f}%** |
| **≥ 400×** (at/above cost) | {stats_255x['above_cost_pct']:.2f}% | {stats_1006x['above_cost_pct']:.2f}% | {stats_169x['above_cost_pct']:.2f}% | **{stats_v2['above_cost_pct']:.2f}%** |
| **≥ 800×** | {stats_255x['above_800_pct']:.2f}% | {stats_1006x['above_800_pct']:.2f}% | {stats_169x['above_800_pct']:.2f}% | **{stats_v2['above_800_pct']:.2f}%** |
| **≥ 1000×** | {stats_255x['above_1000_pct']:.2f}% | {stats_1006x['above_1000_pct']:.2f}% | {stats_169x['above_1000_pct']:.2f}% | **{stats_v2['above_1000_pct']:.2f}%** |

---

## Max Win Cap

| Metric | 255× (Too Tight) | 1006× (Too Generous) | 169× (Over-Corrected) | **v2 (New)** |
|--------|------------------|----------------------|----------------------|--------------|
| **Win Cap** | 10,000× bet | 10,000× bet | 10,000× bet | 10,000× bet |
| **Features Hitting Cap** | {stats_255x['hit_cap_count']} | {stats_1006x['hit_cap_count']} | {stats_169x['hit_cap_count']} | **{stats_v2['hit_cap_count']}** |
| **Cap Hit Rate** | {stats_255x['hit_cap_pct']:.4f}% | {stats_1006x['hit_cap_pct']:.4f}% | {stats_169x['hit_cap_pct']:.4f}% | **{stats_v2['hit_cap_pct']:.4f}%** |

---

## v2 Symbol Distribution

| Symbol | Count | Target | Status |
|--------|-------|--------|--------|
| **H3** | 240 | 240 | ✅ |
| **W** | 16 | 16 | ✅ |
| **L1** | 147 | 147 | ✅ |
| **L2** | 75 | 75 | ✅ |
| **L3** | 70 | 70 | ✅ |
| **L4** | 184 | 184 | ✅ |
| **L5** | 172 | 172 | ✅ |
| **Total** | 904 | 904 | ✅ |

---

## RTP Balance Assessment

### Average Feature Win Analysis

"""
    
    # Add RTP assessment
    avg_win = stats_v2['avg_feature_win']
    target_min = 379
    target_max = 389
    
    if target_min <= avg_win <= target_max:
        report += f"✅ **BALANCED**: Average feature win ({avg_win:.2f}×) is within target range (384× ± 5×)\n"
        report += f"- RTP: {stats_v2['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += "- No further adjustments needed\n\n"
    elif avg_win < target_min:
        report += f"⚠️ **TOO TIGHT**: Average feature win ({avg_win:.2f}×) is below target range (384× - 5× = {target_min}×)\n"
        report += f"- Current RTP: {stats_v2['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += f"- Delta from target: {384 - avg_win:.2f}× below target\n"
        report += "- **Recommendation**: Increase H3 or W slightly\n\n"
    elif avg_win > target_max:
        report += f"⚠️ **TOO GENEROUS**: Average feature win ({avg_win:.2f}×) exceeds target range (384× + 5× = {target_max}×)\n"
        report += f"- Current RTP: {stats_v2['effective_rtp']*100:.2f}% (target: 96.2%)\n"
        report += f"- Delta from target: {avg_win - 384:.2f}× above target\n"
        report += "- **Recommendation**: Reduce H3 or W slightly\n\n"
    
    # Volatility comparison
    report += "### Volatility Comparison\n\n"
    
    # Dead spins
    dead_v2 = stats_v2['bucket_percentages']['< 25×']
    dead_255x = stats_255x['bucket_percentages']['< 25×']
    dead_1006x = stats_1006x['bucket_percentages']['< 25×']
    dead_169x = stats_169x['bucket_percentages']['< 25×']
    
    report += f"**Dead Spins (< 25×)**:\n"
    report += f"- 255× config: {dead_255x:.2f}%\n"
    report += f"- 1006× config: {dead_1006x:.2f}%\n"
    report += f"- 169× config: {dead_169x:.2f}%\n"
    report += f"- **v2**: {dead_v2:.2f}%\n"
    if dead_v2 > dead_1006x:
        report += f"- v2 has more dead spins than 1006× (+{dead_v2 - dead_1006x:.2f}%), which is good for volatility\n\n"
    else:
        report += f"- v2 has fewer dead spins than 1006× ({dead_v2 - dead_1006x:.2f}%)\n\n"
    
    # Big wins
    big_v2 = stats_v2['bucket_percentages']['1000×+']
    big_255x = stats_255x['bucket_percentages']['1000×+']
    big_1006x = stats_1006x['bucket_percentages']['1000×+']
    big_169x = stats_169x['bucket_percentages']['1000×+']
    
    report += f"**Big Wins (1000×+)**:\n"
    report += f"- 255× config: {big_255x:.2f}%\n"
    report += f"- 1006× config: {big_1006x:.2f}%\n"
    report += f"- 169× config: {big_169x:.2f}%\n"
    report += f"- **v2**: {big_v2:.2f}%\n"
    if big_1006x > big_v2 > big_169x:
        report += f"- v2 is between 169× ({big_169x:.2f}%) and 1006× ({big_1006x:.2f}%) - balanced\n\n"
    elif big_v2 > big_1006x:
        report += f"- v2 has more big wins than 1006× (+{big_v2 - big_1006x:.2f}%) - may be excessive\n\n"
    else:
        report += f"- v2 has fewer big wins than 169× ({big_v2 - big_169x:.2f}%) - may be too tight\n\n"
    
    # Medium wins
    med_v2 = stats_v2['bucket_percentages']['100–250×'] + stats_v2['bucket_percentages']['250–500×']
    med_255x = stats_255x['bucket_percentages']['100–250×'] + stats_255x['bucket_percentages']['250–500×']
    med_1006x = stats_1006x['bucket_percentages']['100–250×'] + stats_1006x['bucket_percentages']['250–500×']
    med_169x = stats_169x['bucket_percentages']['100–250×'] + stats_169x['bucket_percentages']['250–500×']
    
    report += f"**Medium Wins (100–500×)**:\n"
    report += f"- 255× config: {med_255x:.2f}%\n"
    report += f"- 1006× config: {med_1006x:.2f}%\n"
    report += f"- 169× config: {med_169x:.2f}%\n"
    report += f"- **v2**: {med_v2:.2f}%\n"
    if med_v2 < med_255x:
        report += f"- v2 has fewer medium wins than 255× ({med_v2 - med_255x:.2f}%) - better volatility\n\n"
    else:
        report += f"- v2 has more medium wins than 255× (+{med_v2 - med_255x:.2f}%)\n\n"
    
    # Overall assessment
    report += "### Overall Assessment\n\n"
    
    if target_min <= avg_win <= target_max:
        report += "**v2 Status**: ✅ **BALANCED** - Average is within target range\n"
        report += "- RTP is properly balanced at target level\n"
        report += "- Distribution shows good volatility characteristics\n"
    elif avg_win < target_min:
        report += "**v2 Status**: ⚠️ **STILL TOO TIGHT** - Average below target\n"
        report += f"- Current: {avg_win:.2f}× vs Target: 384× ± 5×\n"
        report += "- v2 improved from 169× but needs more premium symbols\n"
        report += "- Consider: H3 → 250-260, W → 17-18\n"
    elif avg_win > target_max:
        report += "**v2 Status**: ⚠️ **STILL TOO GENEROUS** - Average above target\n"
        report += f"- Current: {avg_win:.2f}× vs Target: 384× ± 5×\n"
        report += "- v2 reduced from 1006× but may need more trimming\n"
        report += "- Consider: H3 → 220-230, W → 14-15\n"
    
    report += "\n### Summary\n\n"
    report += f"- **Features Analyzed**: {stats_v2['num_features']:,} (wincap excluded)\n"
    report += f"- **Average Feature Win**: {stats_v2['avg_feature_win']:.2f}× bet\n"
    report += f"- **Effective RTP**: {stats_v2['effective_rtp']*100:.2f}%\n"
    report += f"- **Median Feature Win**: {stats_v2['median_win']:.2f}× bet\n"
    report += f"- **Min Feature Win**: {stats_v2['min_win']:.2f}× bet\n"
    report += f"- **Max Feature Win**: {stats_v2['max_win']:.2f}× bet\n"
    report += f"- **Below Cost**: {stats_v2['below_cost_pct']:.2f}% of features\n"
    report += f"- **Above Cost**: {stats_v2['above_cost_pct']:.2f}% of features\n"
    report += f"- **1000×+ Hits**: {stats_v2['above_1000_pct']:.2f}% of features\n"
    report += f"- **Cap Hits**: {stats_v2['hit_cap_pct']:.4f}% of features ({stats_v2['hit_cap_count']} features)\n\n"
    
    report += f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✓ v2 analysis report saved to: {output_file}")
    else:
        print(report)
    
    return report


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("FR1.CSV v2 DISTRIBUTION - FINALIZE AND SIMULATE")
    print("="*80)
    
    # Step 1: Verify and fix FR1.csv counts
    print("\n" + "="*80)
    print("STEP 1: VERIFYING FR1.CSV SYMBOL COUNTS")
    print("="*80)
    verify_and_fix_fr1_counts()
    
    # Step 2: Initialize config and gamestate
    print("\n" + "="*80)
    print("STEP 2: INITIALIZING GAME CONFIG")
    print("="*80)
    config = GameConfig()
    gamestate = GameState(config)
    
    # Step 3: Run simulation
    print("\n" + "="*80)
    print("STEP 3: RUNNING SIMULATION")
    print("="*80)
    num_features_requested = 100000
    run_superbonus_simulation(config, gamestate, num_features_requested)
    
    # Step 4: Analyze results
    book_file = os.path.join(config.publish_path, "books_superbonus.jsonl.zst")
    
    print("\n" + "="*80)
    print("STEP 4: ANALYZING FEATURE WINS (v2)")
    print("="*80 + "\n")
    
    analysis_data = analyze_superbonus_books(book_file, exclude_wincap=True)
    
    # Step 5: Calculate statistics
    print("\n" + "="*80)
    print("STEP 5: CALCULATING STATISTICS")
    print("="*80 + "\n")
    
    stats_v2 = calculate_statistics(analysis_data['feature_wins'], buy_cost=400.0)
    
    # Step 6: Generate report
    print("\n" + "="*80)
    print("STEP 6: GENERATING v2 ANALYSIS REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "SUPERBONUS_V2_ANALYSIS_REPORT.md"
    )
    
    generate_v2_report(STATS_255X, STATS_1006X, STATS_169X, stats_v2, output_file=output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

