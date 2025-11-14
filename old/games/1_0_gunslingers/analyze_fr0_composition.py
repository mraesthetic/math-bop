#!/usr/bin/env python3
"""
Analyze FR0.csv composition to understand why RTP is low.

Compares FR0.csv (regular bonus) with FR1.csv (superbonus) to identify
symbol density differences and low symbol clusters.
"""

import os
from pathlib import Path
from collections import defaultdict, Counter
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_config import GameConfig


def analyze_reelset(reelset, filename):
    """Analyze a reelset and return statistics.
    
    reelset is a list of reels (columns), where each reel is a list of symbols.
    """
    symbol_counts = Counter()
    premium_counts = Counter()  # H1-H4
    low_counts = Counter()      # L1-L5
    wild_count = 0
    vs_count = 0
    scatter_count = 0
    total_symbols = 0
    
    # Track low symbol clusters per reel
    reel_clusters = defaultdict(list)  # {reel_index: [cluster_lengths]}
    
    # Process each reel (column)
    num_reels = len(reelset) if reelset else 0
    for reel_idx, reel in enumerate(reelset):
        consecutive_lows = 0
        for symbol in reel:
            total_symbols += 1
            symbol_counts[symbol] += 1
            
            if symbol.startswith('H'):
                premium_counts[symbol] += 1
            elif symbol.startswith('L'):
                low_counts[symbol] += 1
                consecutive_lows += 1
            else:
                # Non-low symbol encountered - check if we had a cluster
                if consecutive_lows >= 3:
                    reel_clusters[reel_idx].append(consecutive_lows)
                consecutive_lows = 0
            
            if symbol == 'W':
                wild_count += 1
            elif symbol == 'VS':
                vs_count += 1
            elif symbol == 'S':
                scatter_count += 1
        
        # Check if reel ends with a cluster
        if consecutive_lows >= 3:
            reel_clusters[reel_idx].append(consecutive_lows)
    
    # Calculate totals
    total_premiums = sum(premium_counts.values())
    total_lows = sum(low_counts.values())
    
    # Calculate percentages
    premium_pct = (total_premiums / total_symbols * 100) if total_symbols > 0 else 0
    low_pct = (total_lows / total_symbols * 100) if total_symbols > 0 else 0
    wild_pct = (wild_count / total_symbols * 100) if total_symbols > 0 else 0
    vs_pct = (vs_count / total_symbols * 100) if total_symbols > 0 else 0
    scatter_pct = (scatter_count / total_symbols * 100) if total_symbols > 0 else 0
    
    return {
        'filename': filename,
        'total_symbols': total_symbols,
        'num_rows': len(reelset[0]) if reelset and len(reelset) > 0 else 0,
        'symbol_counts': symbol_counts,
        'premium_counts': premium_counts,
        'low_counts': low_counts,
        'wild_count': wild_count,
        'vs_count': vs_count,
        'scatter_count': scatter_count,
        'total_premiums': total_premiums,
        'total_lows': total_lows,
        'premium_pct': premium_pct,
        'low_pct': low_pct,
        'wild_pct': wild_pct,
        'vs_pct': vs_pct,
        'scatter_pct': scatter_pct,
        'reel_clusters': reel_clusters,
        'premium_to_low_ratio': total_premiums / total_lows if total_lows > 0 else 0,
    }


def generate_analysis_report(fr0_stats, fr1_stats, output_file=None):
    """Generate a comprehensive analysis report."""
    
    report = f"""# FR0.csv Composition Analysis

**Purpose**: Analyze FR0.csv (regular bonus) to understand why RTP is only 46.39% (target: 96.2%)

---

## Symbol Counts - FR0.csv (Regular Bonus)

### Premium Symbols (H1-H4)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **H1** | {fr0_stats['premium_counts'].get('H1', 0):,} | {fr0_stats['premium_counts'].get('H1', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **H2** | {fr0_stats['premium_counts'].get('H2', 0):,} | {fr0_stats['premium_counts'].get('H2', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **H3** | {fr0_stats['premium_counts'].get('H3', 0):,} | {fr0_stats['premium_counts'].get('H3', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **H4** | {fr0_stats['premium_counts'].get('H4', 0):,} | {fr0_stats['premium_counts'].get('H4', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **Total Premiums** | {fr0_stats['total_premiums']:,} | {fr0_stats['premium_pct']:.2f}% |

### Low Symbols (L1-L5)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **L1** | {fr0_stats['low_counts'].get('L1', 0):,} | {fr0_stats['low_counts'].get('L1', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **L2** | {fr0_stats['low_counts'].get('L2', 0):,} | {fr0_stats['low_counts'].get('L2', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **L3** | {fr0_stats['low_counts'].get('L3', 0):,} | {fr0_stats['low_counts'].get('L3', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **L4** | {fr0_stats['low_counts'].get('L4', 0):,} | {fr0_stats['low_counts'].get('L4', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **L5** | {fr0_stats['low_counts'].get('L5', 0):,} | {fr0_stats['low_counts'].get('L5', 0) / fr0_stats['total_symbols'] * 100:.2f}% |
| **Total Lows** | {fr0_stats['total_lows']:,} | {fr0_stats['low_pct']:.2f}% |

### Special Symbols

| Symbol | Count | Percentage |
|--------|-------|------------|
| **W (Wild)** | {fr0_stats['wild_count']:,} | {fr0_stats['wild_pct']:.2f}% |
| **VS (DRAW)** | {fr0_stats['vs_count']:,} | {fr0_stats['vs_pct']:.2f}% |
| **S (Scatter)** | {fr0_stats['scatter_count']:,} | {fr0_stats['scatter_pct']:.2f}% |

---

## Symbol Counts - FR1.csv (Superbonus)

### Premium Symbols (H1-H4)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **H1** | {fr1_stats['premium_counts'].get('H1', 0):,} | {fr1_stats['premium_counts'].get('H1', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **H2** | {fr1_stats['premium_counts'].get('H2', 0):,} | {fr1_stats['premium_counts'].get('H2', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **H3** | {fr1_stats['premium_counts'].get('H3', 0):,} | {fr1_stats['premium_counts'].get('H3', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **H4** | {fr1_stats['premium_counts'].get('H4', 0):,} | {fr1_stats['premium_counts'].get('H4', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **Total Premiums** | {fr1_stats['total_premiums']:,} | {fr1_stats['premium_pct']:.2f}% |

### Low Symbols (L1-L5)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **L1** | {fr1_stats['low_counts'].get('L1', 0):,} | {fr1_stats['low_counts'].get('L1', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **L2** | {fr1_stats['low_counts'].get('L2', 0):,} | {fr1_stats['low_counts'].get('L2', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **L3** | {fr1_stats['low_counts'].get('L3', 0):,} | {fr1_stats['low_counts'].get('L3', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **L4** | {fr1_stats['low_counts'].get('L4', 0):,} | {fr1_stats['low_counts'].get('L4', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **L5** | {fr1_stats['low_counts'].get('L5', 0):,} | {fr1_stats['low_counts'].get('L5', 0) / fr1_stats['total_symbols'] * 100:.2f}% |
| **Total Lows** | {fr1_stats['total_lows']:,} | {fr1_stats['low_pct']:.2f}% |

### Special Symbols

| Symbol | Count | Percentage |
|--------|-------|------------|
| **W (Wild)** | {fr1_stats['wild_count']:,} | {fr1_stats['wild_pct']:.2f}% |
| **VS (DRAW)** | {fr1_stats['vs_count']:,} | {fr1_stats['vs_pct']:.2f}% |
| **S (Scatter)** | {fr1_stats['scatter_count']:,} | {fr1_stats['scatter_pct']:.2f}% |

---

## Comparison: FR0 vs FR1

### Key Ratios

| Metric | FR0 (Regular Bonus) | FR1 (Superbonus) | Difference |
|--------|---------------------|------------------|------------|
| **Premium/Low Ratio** | {fr0_stats['premium_to_low_ratio']:.3f} | {fr1_stats['premium_to_low_ratio']:.3f} | {fr1_stats['premium_to_low_ratio'] - fr0_stats['premium_to_low_ratio']:+.3f} |
| **Premium %** | {fr0_stats['premium_pct']:.2f}% | {fr1_stats['premium_pct']:.2f}% | {fr1_stats['premium_pct'] - fr0_stats['premium_pct']:+.2f}% |
| **Low %** | {fr0_stats['low_pct']:.2f}% | {fr1_stats['low_pct']:.2f}% | {fr1_stats['low_pct'] - fr0_stats['low_pct']:+.2f}% |
| **Wild %** | {fr0_stats['wild_pct']:.2f}% | {fr1_stats['wild_pct']:.2f}% | {fr1_stats['wild_pct'] - fr0_stats['wild_pct']:+.2f}% |
| **VS %** | {fr0_stats['vs_pct']:.2f}% | {fr1_stats['vs_pct']:.2f}% | {fr1_stats['vs_pct'] - fr0_stats['vs_pct']:+.2f}% |
| **Scatter %** | {fr0_stats['scatter_pct']:.2f}% | {fr1_stats['scatter_pct']:.2f}% | {fr1_stats['scatter_pct'] - fr0_stats['scatter_pct']:+.2f}% |

### Symbol Count Differences

| Symbol | FR0 Count | FR1 Count | Difference | % Change |
|--------|-----------|-----------|------------|----------|
| **H1** | {fr0_stats['premium_counts'].get('H1', 0)} | {fr1_stats['premium_counts'].get('H1', 0)} | {fr1_stats['premium_counts'].get('H1', 0) - fr0_stats['premium_counts'].get('H1', 0):+d} | {((fr1_stats['premium_counts'].get('H1', 0) - fr0_stats['premium_counts'].get('H1', 0)) / max(fr0_stats['premium_counts'].get('H1', 1), 1) * 100):+.1f}% |
| **H2** | {fr0_stats['premium_counts'].get('H2', 0)} | {fr1_stats['premium_counts'].get('H2', 0)} | {fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0):+d} | {((fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0)) / max(fr0_stats['premium_counts'].get('H2', 1), 1) * 100):+.1f}% |
| **H3** | {fr0_stats['premium_counts'].get('H3', 0)} | {fr1_stats['premium_counts'].get('H3', 0)} | {fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0):+d} | {((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) / max(fr0_stats['premium_counts'].get('H3', 1), 1) * 100):+.1f}% |
| **H4** | {fr0_stats['premium_counts'].get('H4', 0)} | {fr1_stats['premium_counts'].get('H4', 0)} | {fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0):+d} | {((fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0)) / max(fr0_stats['premium_counts'].get('H4', 1), 1) * 100):+.1f}% |
| **W** | {fr0_stats['wild_count']} | {fr1_stats['wild_count']} | {fr1_stats['wild_count'] - fr0_stats['wild_count']:+d} | {((fr1_stats['wild_count'] - fr0_stats['wild_count']) / max(fr0_stats['wild_count'], 1) * 100):+.1f}% |
| **VS** | {fr0_stats['vs_count']} | {fr1_stats['vs_count']} | {fr1_stats['vs_count'] - fr0_stats['vs_count']:+d} | {((fr1_stats['vs_count'] - fr0_stats['vs_count']) / max(fr0_stats['vs_count'], 1) * 100):+.1f}% |

---

## Low Symbol Clusters (3+ consecutive lows)

### FR0.csv Clusters

"""
    
    # Add cluster information for FR0
    if fr0_stats['reel_clusters']:
        report += "\n| Reel | Cluster Lengths |\n"
        report += "|------|-----------------|\n"
        for reel_idx in sorted(fr0_stats['reel_clusters'].keys()):
            clusters = fr0_stats['reel_clusters'][reel_idx]
            if clusters:
                cluster_str = ", ".join([f"{c}" for c in clusters])
                report += f"| **Reel {reel_idx + 1}** | {cluster_str} |\n"
        total_clusters_fr0 = sum(len(clusters) for clusters in fr0_stats['reel_clusters'].values())
        report += f"\n**Total clusters in FR0**: {total_clusters_fr0}\n"
    else:
        report += "\n**No clusters of 3+ consecutive low symbols found in FR0.csv**\n"
    
    report += "\n### FR1.csv Clusters\n\n"
    
    # Add cluster information for FR1
    if fr1_stats['reel_clusters']:
        report += "| Reel | Cluster Lengths |\n"
        report += "|------|-----------------|\n"
        for reel_idx in sorted(fr1_stats['reel_clusters'].keys()):
            clusters = fr1_stats['reel_clusters'][reel_idx]
            if clusters:
                cluster_str = ", ".join([f"{c}" for c in clusters])
                report += f"| **Reel {reel_idx + 1}** | {cluster_str} |\n"
        total_clusters_fr1 = sum(len(clusters) for clusters in fr1_stats['reel_clusters'].values())
        report += f"\n**Total clusters in FR1**: {total_clusters_fr1}\n"
    else:
        report += "\n**No clusters of 3+ consecutive low symbols found in FR1.csv**\n"
    
    # Analysis section
    report += f"""

---

## Analysis & Observations

### 1. Premium-to-Low Ratio

- **FR0 (Regular Bonus)**: {fr0_stats['premium_to_low_ratio']:.3f} (1 premium per {1/fr0_stats['premium_to_low_ratio']:.2f} lows)
- **FR1 (Superbonus)**: {fr1_stats['premium_to_low_ratio']:.3f} (1 premium per {1/fr1_stats['premium_to_low_ratio']:.2f} lows)
- **Difference**: FR0 has **{((fr0_stats['premium_to_low_ratio'] / fr1_stats['premium_to_low_ratio'] - 1) * 100):.1f}%** {'lower' if fr0_stats['premium_to_low_ratio'] < fr1_stats['premium_to_low_ratio'] else 'higher'} premium density

**Impact**: Lower premium density in FR0 means fewer high-paying wins, contributing to lower RTP.

### 2. VS (DRAW) Symbol Frequency

- **FR0**: {fr0_stats['vs_count']} VS symbols ({fr0_stats['vs_pct']:.2f}%)
- **FR1**: {fr1_stats['vs_count']} VS symbols ({fr1_stats['vs_pct']:.2f}%)
- **Difference**: FR0 has **{fr1_stats['vs_count'] - fr0_stats['vs_count']:+d}** {'fewer' if fr0_stats['vs_count'] < fr1_stats['vs_count'] else 'more'} VS symbols

**Impact**: VS symbols are critical for big wins (expanding wilds with multipliers). Lower VS frequency in FR0 significantly reduces win potential.

### 3. Wild Symbol Frequency

- **FR0**: {fr0_stats['wild_count']} W symbols ({fr0_stats['wild_pct']:.2f}%)
- **FR1**: {fr1_stats['wild_count']} W symbols ({fr1_stats['wild_pct']:.2f}%)
- **Difference**: FR0 has **{fr1_stats['wild_count'] - fr0_stats['wild_count']:+d}** {'fewer' if fr0_stats['wild_count'] < fr1_stats['wild_count'] else 'more'} W symbols

**Impact**: Wilds contribute to wins and can have multipliers. Lower wild frequency reduces win potential.

### 4. Low Symbol Density

- **FR0**: {fr0_stats['total_lows']} low symbols ({fr0_stats['low_pct']:.2f}%)
- **FR1**: {fr1_stats['total_lows']} low symbols ({fr1_stats['low_pct']:.2f}%)
- **Difference**: FR0 has **{fr0_stats['total_lows'] - fr1_stats['total_lows']:+d}** {'more' if fr0_stats['total_lows'] > fr1_stats['total_lows'] else 'fewer'} low symbols

**Impact**: Higher low symbol density means more frequent low-paying wins, diluting the overall RTP.

### 5. H3 Symbol (Shotgun) Frequency

- **FR0**: {fr0_stats['premium_counts'].get('H3', 0)} H3 symbols ({fr0_stats['premium_counts'].get('H3', 0) / fr0_stats['total_symbols'] * 100:.2f}%)
- **FR1**: {fr1_stats['premium_counts'].get('H3', 0)} H3 symbols ({fr1_stats['premium_counts'].get('H3', 0) / fr1_stats['total_symbols'] * 100:.2f}%)
- **Difference**: FR0 has **{fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0):+d}** {'fewer' if fr0_stats['premium_counts'].get('H3', 0) < fr1_stats['premium_counts'].get('H3', 0) else 'more'} H3 symbols

**Impact**: H3 is a key premium symbol. Lower H3 density reduces premium win frequency.

---

## Recommendations for Improvement

Based on the analysis, the following changes are recommended to increase FR0 RTP from 46.39% to ~96.2%:

### Primary Issues Identified:

1. **VS Frequency Too Low**: FR0 has only {fr0_stats['vs_count']} VS symbols vs {fr1_stats['vs_count']} in FR1. VS symbols are critical for big wins.
2. **Premium Density Too Low**: FR0 has {fr0_stats['premium_pct']:.1f}% premiums vs {fr1_stats['premium_pct']:.1f}% in FR1.
3. **Low Symbol Density Too High**: FR0 has {fr0_stats['low_pct']:.1f}% lows vs {fr1_stats['low_pct']:.1f}% in FR1.
4. **H3 Density Too Low**: H3 is significantly under-represented in FR0.

### Suggested Initial Direction:

#### 1. Increase VS Symbol Density
- **Current**: {fr0_stats['vs_count']} VS symbols ({fr0_stats['vs_pct']:.2f}%)
- **Target**: Increase by **{(fr1_stats['vs_count'] - fr0_stats['vs_count']) / max(fr0_stats['vs_count'], 1) * 100:.0f}%** to match or approach FR1 density
- **Action**: Add approximately **{fr1_stats['vs_count'] - fr0_stats['vs_count']}** VS symbols to FR0
- **Impact**: VS symbols provide expanding wilds with multipliers, critical for big wins

#### 2. Increase Premium Symbol Density (especially H3)
- **Current H3**: {fr0_stats['premium_counts'].get('H3', 0)} symbols
- **Target**: Increase H3 by **{int((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 1.5)}-{int((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 2)}** symbols (~{(fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 1.5 / fr0_stats['premium_counts'].get('H3', 1) * 100:.0f}-{((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 2 / max(fr0_stats['premium_counts'].get('H3', 1), 1) * 100):.0f}% increase)
- **Action**: Replace low symbols (L1-L3) with H3 symbols
- **Impact**: Increases premium win frequency and average win size

#### 3. Increase H2 and H4 Density
- **Current H2**: {fr0_stats['premium_counts'].get('H2', 0)} symbols
- **Target**: Increase H2 by **{int((fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0)) * 0.8)}-{int((fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0)) * 1.2)}** symbols
- **Current H4**: {fr0_stats['premium_counts'].get('H4', 0)} symbols  
- **Target**: Increase H4 by **{int((fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0)) * 0.8)}-{int((fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0)) * 1.2)}** symbols
- **Impact**: Balanced premium distribution for better win potential

#### 4. Reduce Low Symbol Density (especially L1-L3)
- **Current**: {fr0_stats['total_lows']} low symbols ({fr0_stats['low_pct']:.2f}%)
- **Target**: Reduce by **{int((fr0_stats['total_lows'] - fr1_stats['total_lows']) * 0.7)}-{int((fr0_stats['total_lows'] - fr1_stats['total_lows']) * 0.9)}** symbols (focus on L1-L3)
- **Action**: Replace low symbols with premiums (H2, H3, H4) and VS symbols
- **Impact**: Reduces low-paying win frequency, increases average win size

#### 5. Maintain or Slightly Increase Wild Density
- **Current**: {fr0_stats['wild_count']} W symbols
- **Target**: Maintain current level or increase slightly
- **Impact**: Wilds contribute to wins and can have multipliers

### Summary of Recommended Changes:

1. **Add {fr1_stats['vs_count'] - fr0_stats['vs_count']} VS symbols** (replace low symbols)
2. **Increase H3 by ~{int((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 1.5)}-{int((fr1_stats['premium_counts'].get('H3', 0) - fr0_stats['premium_counts'].get('H3', 0)) * 2)} symbols**
3. **Increase H2 by ~{int((fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0)) * 0.8)}-{int((fr1_stats['premium_counts'].get('H2', 0) - fr0_stats['premium_counts'].get('H2', 0)) * 1.2)} symbols**
4. **Increase H4 by ~{int((fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0)) * 0.8)}-{int((fr1_stats['premium_counts'].get('H4', 0) - fr0_stats['premium_counts'].get('H4', 0)) * 1.2)} symbols**
5. **Reduce L1-L3 by ~{int((fr0_stats['low_counts'].get('L1', 0) + fr0_stats['low_counts'].get('L2', 0) + fr0_stats['low_counts'].get('L3', 0)) - (fr1_stats['low_counts'].get('L1', 0) + fr1_stats['low_counts'].get('L2', 0) + fr1_stats['low_counts'].get('L3', 0)))} symbols total**

**Expected Impact**: These changes should significantly increase the premium-to-low ratio and VS frequency, moving RTP from 46.39% toward the 96.2% target.

---

**Analysis Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
    print("FR0.CSV COMPOSITION ANALYSIS")
    print("="*80)
    
    # Initialize config
    config = GameConfig()
    
    # Read reelsets
    fr0_reelset = config.reels["FR0"]
    fr1_reelset = config.reels["FR1"]
    
    print(f"\nAnalyzing FR0.csv ({len(fr0_reelset[0]) if fr0_reelset and len(fr0_reelset) > 0 else 0} rows)...")
    fr0_stats = analyze_reelset(fr0_reelset, "FR0.csv")
    
    print(f"Analyzing FR1.csv ({len(fr1_reelset[0]) if fr1_reelset and len(fr1_reelset) > 0 else 0} rows)...")
    fr1_stats = analyze_reelset(fr1_reelset, "FR1.csv")
    
    # Generate report
    output_file = os.path.join(
        Path(__file__).parent,
        "FR0_COMPOSITION_ANALYSIS.md"
    )
    
    generate_analysis_report(fr0_stats, fr1_stats, output_file=output_file)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"FR0 Premium/Low Ratio: {fr0_stats['premium_to_low_ratio']:.3f}")
    print(f"FR1 Premium/Low Ratio: {fr1_stats['premium_to_low_ratio']:.3f}")
    print(f"FR0 VS Count: {fr0_stats['vs_count']} ({fr0_stats['vs_pct']:.2f}%)")
    print(f"FR1 VS Count: {fr1_stats['vs_count']} ({fr1_stats['vs_pct']:.2f}%)")
    print(f"FR0 Wild Count: {fr0_stats['wild_count']} ({fr0_stats['wild_pct']:.2f}%)")
    print(f"FR1 Wild Count: {fr1_stats['wild_count']} ({fr1_stats['wild_pct']:.2f}%)")
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

