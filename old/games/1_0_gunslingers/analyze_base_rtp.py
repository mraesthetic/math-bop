#!/usr/bin/env python3
"""
Analyze BASE bet mode RTP decomposition.

This script:
1. Runs a fresh base mode simulation
2. Decomposes RTP into basegame-only, regular bonus, superbonus, and wincap contributions
3. Analyzes freegame trigger rates and average values
4. Generates comprehensive report
"""

import json
import os
import sys
import zstandard as zst
from io import TextIOWrapper
from collections import defaultdict, Counter
from pathlib import Path
import statistics
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from game_config import GameConfig
from gamestate import GameState
from src.state.run_sims import create_books


def run_base_simulation(config, gamestate, num_spins=100000):
    """Run simulation for base mode only."""
    print(f"\n{'='*80}")
    print(f"Running BASE simulation: {num_spins:,} spins")
    print(f"{'='*80}\n")
    
    num_threads = 10
    batching_size = 5000
    compression = True
    profiling = False
    
    # Run simulation for base only
    num_sim_args = {
        "base": num_spins,
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
    
    print(f"\n✓ Simulation complete: {num_spins:,} base spins\n")


def analyze_base_books(book_file_path: str):
    """
    Analyze base books to extract RTP decomposition.
    
    Returns:
        dict with detailed statistics
    """
    basegame_only_wins = []
    regular_bonus_wins = []
    superbonus_wins = []
    wincap_wins = []
    
    total_spins = 0
    basegame_only_count = 0
    regular_bonus_count = 0
    superbonus_count = 0
    wincap_count = 0
    zerowin_count = 0
    
    # Track scatter triggers
    scatter_3_triggers = 0
    scatter_4_triggers = 0
    total_freegame_triggers = 0
    
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
                events = blob.get("events", [])
                
                # Categorize by criteria
                # Note: wincap spins are test spins that hit max win - exclude from analysis
                if criteria == "wincap":
                    wincap_wins.append(payout_mult)
                    wincap_count += 1
                    # Don't increment total_spins for wincap (excluded from RTP calculation)
                    continue  # Skip processing wincap entries
                
                # All other criteria count as spins (basegame, freegame, zero)
                total_spins += 1
                
                if criteria == "freegame":
                    # Check events to determine if 3-scatter (regular bonus) or 4-scatter (superbonus)
                    # Look for freeSpinTrigger event which has positions array
                    is_superbonus = False
                    scatter_count = 0
                    
                    # Check events for freeSpinTrigger
                    for event in events:
                        event_type = event.get("type", "")
                        if event_type == "freeSpinTrigger":
                            # Count scatter positions
                            positions = event.get("positions", [])
                            scatter_count = len(positions)
                            if scatter_count == 4:
                                is_superbonus = True
                                break
                        # Also check for scatter event with scatterCount
                        elif event_type == "scatter":
                            scatter_count = event.get("scatterCount", event.get("kind", 0))
                            if scatter_count == 4:
                                is_superbonus = True
                                break
                        # Check for FR1 reelset usage (superbonus indicator)
                        if "reelset" in event:
                            reelset = str(event.get("reelset", ""))
                            if "FR1" in reelset or reelset == "FR1":
                                is_superbonus = True
                                break
                        # Check for superbonus flag
                        if event.get("isSuperbonus", False) or event.get("is_superbonus", False):
                            is_superbonus = True
                            break
                    
                    # If we found scatter_count from positions, use it
                    if scatter_count == 0:
                        # Try to count scatters from first reveal event
                        for event in events:
                            if event.get("type") == "reveal":
                                board = event.get("board", [])
                                scatter_count = 0
                                for row in board:
                                    for cell in row:
                                        if isinstance(cell, dict) and cell.get("scatter"):
                                            scatter_count += 1
                                if scatter_count == 4:
                                    is_superbonus = True
                                break
                    
                    # Default: if scatter_count is 4, it's superbonus; otherwise regular bonus
                    if scatter_count == 4:
                        is_superbonus = True
                    elif scatter_count == 0:
                        # If we can't determine, assume regular bonus (3 scatters)
                        scatter_count = 3
                    
                    if is_superbonus:
                        superbonus_wins.append(payout_mult)
                        superbonus_count += 1
                        scatter_4_triggers += 1
                    else:
                        regular_bonus_wins.append(payout_mult)
                        regular_bonus_count += 1
                        scatter_3_triggers += 1
                    
                    total_freegame_triggers += 1
                elif criteria == "basegame":
                    basegame_only_wins.append(payout_mult)
                    basegame_only_count += 1
                elif criteria == "0":
                    # Zero win basegame spin
                    basegame_only_wins.append(0.0)
                    basegame_only_count += 1
                    zerowin_count += 1
                else:
                    # Unknown criteria, treat as basegame
                    basegame_only_wins.append(payout_mult)
                    basegame_only_count += 1
                
                # Progress indicator
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num:,} spins...", end='\r')
    
    # Adjust total_spins to exclude wincap for RTP calculation
    effective_spins = total_spins - wincap_count
    
    print(f"\n✓ Analyzed {total_spins:,} spins ({effective_spins:,} excluding wincap)\n")
    
    return {
        'total_spins': total_spins,
        'effective_spins': effective_spins,
        'basegame_only_wins': basegame_only_wins,
        'regular_bonus_wins': regular_bonus_wins,
        'superbonus_wins': superbonus_wins,
        'wincap_wins': wincap_wins,
        'basegame_only_count': basegame_only_count,
        'regular_bonus_count': regular_bonus_count,
        'superbonus_count': superbonus_count,
        'wincap_count': wincap_count,
        'zerowin_count': zerowin_count,
        'scatter_3_triggers': scatter_3_triggers,
        'scatter_4_triggers': scatter_4_triggers,
        'total_freegame_triggers': total_freegame_triggers,
    }


def calculate_rtp_decomposition(analysis_data, cost=1.0):
    """Calculate RTP decomposition."""
    total_spins = analysis_data['total_spins']
    effective_spins = analysis_data.get('effective_spins', total_spins - analysis_data['wincap_count'])
    
    # Calculate total win (sum of all wins EXCLUDING wincap for RTP calculation)
    basegame_total = sum(analysis_data['basegame_only_wins'])
    regular_bonus_total = sum(analysis_data['regular_bonus_wins'])
    superbonus_total = sum(analysis_data['superbonus_wins'])
    wincap_total = sum(analysis_data['wincap_wins'])
    
    # Total win for RTP (excluding wincap test spins)
    total_win_for_rtp = basegame_total + regular_bonus_total + superbonus_total
    total_win_with_wincap = total_win_for_rtp + wincap_total
    
    # Calculate total RTP (total win / effective spins / cost) - excluding wincap
    total_rtp = (total_win_for_rtp / effective_spins) / cost
    
    # Calculate basegame-only RTP contribution (excluding wincap from denominator)
    basegame_rtp = (basegame_total / effective_spins) / cost
    
    # Calculate regular bonus RTP contribution (excluding wincap from denominator)
    regular_bonus_rtp = (regular_bonus_total / effective_spins) / cost
    
    # Calculate superbonus RTP contribution (excluding wincap from denominator)
    superbonus_rtp = (superbonus_total / effective_spins) / cost
    
    # Calculate wincap RTP contribution (for reference only, excluded from total RTP)
    wincap_rtp = (wincap_total / total_spins) / cost  # Use total_spins for wincap percentage
    
    # Calculate averages
    avg_basegame_win = basegame_total / analysis_data['basegame_only_count'] if analysis_data['basegame_only_count'] > 0 else 0
    avg_regular_bonus_win = statistics.mean(analysis_data['regular_bonus_wins']) if analysis_data['regular_bonus_wins'] else 0
    avg_superbonus_win = statistics.mean(analysis_data['superbonus_wins']) if analysis_data['superbonus_wins'] else 0
    
    # Calculate trigger rates (using effective_spins, excluding wincap)
    freegame_hit_rate = (analysis_data['total_freegame_triggers'] / effective_spins) * 100
    regular_bonus_rate = (analysis_data['regular_bonus_count'] / effective_spins) * 100
    superbonus_rate = (analysis_data['superbonus_count'] / effective_spins) * 100
    
    # Calculate scatter split
    scatter_3_pct = (analysis_data['scatter_3_triggers'] / analysis_data['total_freegame_triggers'] * 100) if analysis_data['total_freegame_triggers'] > 0 else 0
    scatter_4_pct = (analysis_data['scatter_4_triggers'] / analysis_data['total_freegame_triggers'] * 100) if analysis_data['total_freegame_triggers'] > 0 else 0
    
    # Calculate spins per superbonus (using effective_spins)
    spins_per_superbonus = effective_spins / analysis_data['superbonus_count'] if analysis_data['superbonus_count'] > 0 else float('inf')
    
    return {
        'total_rtp': total_rtp,
        'basegame_rtp': basegame_rtp,
        'regular_bonus_rtp': regular_bonus_rtp,
        'superbonus_rtp': superbonus_rtp,
        'wincap_rtp': wincap_rtp,
        'avg_basegame_win': avg_basegame_win,
        'avg_regular_bonus_win': avg_regular_bonus_win,
        'avg_superbonus_win': avg_superbonus_win,
        'freegame_hit_rate': freegame_hit_rate,
        'regular_bonus_rate': regular_bonus_rate,
        'superbonus_rate': superbonus_rate,
        'scatter_3_pct': scatter_3_pct,
        'scatter_4_pct': scatter_4_pct,
        'spins_per_superbonus': spins_per_superbonus,
        'basegame_only_count': analysis_data['basegame_only_count'],
        'regular_bonus_count': analysis_data['regular_bonus_count'],
        'superbonus_count': analysis_data['superbonus_count'],
        'wincap_count': analysis_data['wincap_count'],
        'zerowin_count': analysis_data['zerowin_count'],
        'effective_spins': effective_spins,
    }


def generate_base_rtp_report(stats, analysis_data, output_file=None):
    """Generate comprehensive base RTP report."""
    
    target_rtp = 0.962  # 96.2%
    rtp_diff = stats['total_rtp'] - target_rtp
    rtp_diff_pct = (rtp_diff / target_rtp) * 100
    
    # Determine status
    if abs(rtp_diff) <= 0.01:  # Within 1%
        rtp_status = "✅ ON TARGET"
    elif rtp_diff < 0:
        rtp_status = "⚠️  BELOW TARGET"
    else:
        rtp_status = "⚠️  ABOVE TARGET"
    
    report = f"""# BASE Bet Mode RTP Analysis

**Game**: Gunslingers: DRAW!  
**Bet Mode**: base  
**Cost**: 1.0× bet  
**Spins Analyzed**: {stats.get('effective_spins', analysis_data['total_spins']):,} (wincap excluded)  
**Total Spins (including wincap)**: {analysis_data['total_spins']:,}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overall RTP Summary

| Metric | Value |
|--------|-------|
| **Total Effective RTP** | {stats['total_rtp']*100:.2f}% ({stats['total_rtp']:.4f}) |
| **Target RTP** | 96.2% (0.9620) |
| **Difference** | {rtp_diff*100:+.2f}% ({rtp_diff:+.4f}) |
| **Status** | {rtp_status} |

---

## RTP Decomposition

| Component | RTP Contribution | % of Total RTP | Count | Avg Win per Spin |
|-----------|-----------------|----------------|-------|------------------|
| **Basegame-Only** | {stats['basegame_rtp']*100:.2f}% | {stats['basegame_rtp']/stats['total_rtp']*100:.2f}% | {stats['basegame_only_count']:,} | {stats['avg_basegame_win']:.2f}× |
| **Regular Bonus** | {stats['regular_bonus_rtp']*100:.2f}% | {stats['regular_bonus_rtp']/stats['total_rtp']*100:.2f}% | {stats['regular_bonus_count']:,} | {stats['avg_regular_bonus_win']:.2f}× |
| **Superbonus** | {stats['superbonus_rtp']*100:.2f}% | {stats['superbonus_rtp']/stats['total_rtp']*100:.2f}% | {stats['superbonus_count']:,} | {stats['avg_superbonus_win']:.2f}× |
| **Wincap** | {stats['wincap_rtp']*100:.2f}% | {stats['wincap_rtp']/stats['total_rtp']*100:.2f}% | {stats['wincap_count']:,} | {stats['wincap_rtp']*analysis_data['total_spins']/max(stats['wincap_count'], 1):.2f}× |
| **Total** | {stats['total_rtp']*100:.2f}% | 100.00% | {stats.get('effective_spins', analysis_data['total_spins']):,} | {stats['total_rtp']:.2f}× |
| **Wincap (excluded)** | {stats['wincap_rtp']*100:.2f}% | (test spins) | {stats['wincap_count']:,} | 10,000.00× |

---

## Freegame Trigger Statistics

### Overall Freegame Hit Rate

| Metric | Value |
|--------|-------|
| **Total Freegame Triggers** | {analysis_data['total_freegame_triggers']:,} |
| **Freegame Hit Rate** | {stats['freegame_hit_rate']:.2f}% |
| **Expected** | ~10% (from config) |

### Scatter Trigger Split

| Trigger Type | Count | % of Freegames | % of Total Spins |
|--------------|-------|----------------|------------------|
| **3 Scatters (Regular Bonus)** | {analysis_data['scatter_3_triggers']:,} | {stats['scatter_3_pct']:.2f}% | {stats['regular_bonus_rate']:.2f}% |
| **4 Scatters (Superbonus)** | {analysis_data['scatter_4_triggers']:,} | {stats['scatter_4_pct']:.2f}% | {stats['superbonus_rate']:.2f}% |

### Superbonus Frequency

| Metric | Value |
|--------|-------|
| **Superbonus Triggers** | {stats['superbonus_count']:,} |
| **Superbonus Rate** | {stats['superbonus_rate']:.4f}% |
| **Spins per Superbonus** | 1 in {stats['spins_per_superbonus']:.0f} |
| **Expected Range** | 1 in 400-1000 spins (0.1-0.25%) |

---

## Average Freegame Values (from Base)

### Regular Bonus (3 Scatters)

| Metric | Value |
|--------|-------|
| **Average Feature Win** | {stats['avg_regular_bonus_win']:.2f}× bet |
| **Buy Cost** | 100× bet |
| **Effective RTP** | {stats['avg_regular_bonus_win']/100*100:.2f}% |
| **Count** | {stats['regular_bonus_count']:,} |

### Superbonus (4 Scatters)

| Metric | Value |
|--------|-------|
| **Average Feature Win** | {stats['avg_superbonus_win']:.2f}× bet |
| **Buy Cost** | 400× bet |
| **Effective RTP** | {stats['avg_superbonus_win']/400*100:.2f}% |
| **Count** | {stats['superbonus_count']:,} |

---

## Basegame-Only Statistics

| Metric | Value |
|--------|-------|
| **Basegame-Only Spins** | {stats['basegame_only_count']:,} |
| **Zero Win Spins** | {stats['zerowin_count']:,} |
| **Average Basegame Win** | {stats['avg_basegame_win']:.2f}× bet |
| **Basegame RTP Contribution** | {stats['basegame_rtp']*100:.2f}% |
| **Hit Rate** | {(stats['basegame_only_count'] - stats['zerowin_count']) / stats['basegame_only_count'] * 100:.2f}% |

---

## Interpretation

### Overall Base Bet Mode RTP

**Status**: {rtp_status}

The total effective RTP is **{stats['total_rtp']*100:.2f}%**, which is **{abs(rtp_diff)*100:.2f}%** {'below' if rtp_diff < 0 else 'above'} the 96.2% target.

**Assessment**: {"✅ **ON TARGET** - RTP is within acceptable range of 96.2%" if abs(rtp_diff) <= 0.01 else f"⚠️  **{'BELOW' if rtp_diff < 0 else 'ABOVE'} TARGET** - RTP is {abs(rtp_diff)*100:.2f}% {'below' if rtp_diff < 0 else 'above'} target"}

### Basegame-Only vs Bonus Portions

**Basegame-Only RTP**: {stats['basegame_rtp']*100:.2f}% ({stats['basegame_rtp']/stats['total_rtp']*100:.2f}% of total)  
**Regular Bonus RTP**: {stats['regular_bonus_rtp']*100:.2f}% ({stats['regular_bonus_rtp']/stats['total_rtp']*100:.2f}% of total)  
**Superbonus RTP**: {stats['superbonus_rtp']*100:.2f}% ({stats['superbonus_rtp']/stats['total_rtp']*100:.2f}% of total)  
**Total Bonus RTP**: {(stats['regular_bonus_rtp'] + stats['superbonus_rtp'])*100:.2f}% ({(stats['regular_bonus_rtp'] + stats['superbonus_rtp'])/stats['total_rtp']*100:.2f}% of total)

**Assessment**: {("⚠️  **IMBALANCED** - Basegame portion is **too low** relative to bonus portions. Basegame contributes only {:.1f}% of total RTP, while bonuses contribute {:.1f}%. For a balanced game targeting 96.2% RTP, basegame should contribute ~40-45% (38-43% RTP) and bonuses ~55-60% (53-58% RTP).".format(stats['basegame_rtp']/stats['total_rtp']*100, (stats['regular_bonus_rtp'] + stats['superbonus_rtp'])/stats['total_rtp']*100) if stats['basegame_rtp']/stats['total_rtp'] < 0.4 else "✅ **BALANCED** - Basegame and bonus portions are appropriately balanced" if 0.4 <= stats['basegame_rtp']/stats['total_rtp'] <= 0.6 else "⚠️  **IMBALANCED** - Basegame portion is **too high** relative to bonus portions.")}

### Natural Superbonus Hit Rate

**Superbonus Rate**: {stats['superbonus_rate']:.4f}% (1 in {stats['spins_per_superbonus']:.0f} spins)  
**Expected Range**: 0.1-0.25% (1 in 400-1000 spins)

**Assessment**: {"✅ **REASONABLE** - Superbonus hit rate is within expected range" if 0.1 <= stats['superbonus_rate'] <= 0.25 else "⚠️  **{'TOO RARE' if stats['superbonus_rate'] < 0.1 else 'TOO COMMON'}** - Superbonus hit rate is {'below' if stats['superbonus_rate'] < 0.1 else 'above'} expected range"}

---

## Recommendations

"""
    
    # Add recommendations based on analysis
    if abs(rtp_diff) > 0.01:
        if rtp_diff < 0:
            deficit = abs(rtp_diff) * 100
            report += f"""
**RTP Below Target**:
- Current: {stats['total_rtp']*100:.2f}%
- Target: 96.2%
- Deficit: {deficit:.2f}% RTP

**Suggested Actions**:
1. Increase basegame paytable values slightly
2. Increase regular bonus contribution
3. Adjust freegame trigger rate if needed
"""
        else:
            excess = rtp_diff * 100
            report += f"""
**RTP Above Target**:
- Current: {stats['total_rtp']*100:.2f}%
- Target: 96.2%
- Excess: {excess:.2f}% RTP

**Suggested Actions**:
1. Reduce basegame paytable values slightly
2. Reduce regular bonus contribution
3. Adjust freegame trigger rate if needed
"""
    else:
        report += """
**RTP On Target**:
- ✅ Current RTP is within acceptable range of 96.2%
- No major adjustments needed
"""
    
    if stats['superbonus_rate'] < 0.1:
        report += f"""
**Superbonus Too Rare**:
- Current: {stats['superbonus_rate']:.4f}% (1 in {stats['spins_per_superbonus']:.0f})
- Target: 0.1-0.25% (1 in 400-1000)
- **Suggestion**: Increase 4-scatter trigger rate in freegame_condition scatter_triggers
"""
    elif stats['superbonus_rate'] > 0.25:
        report += f"""
**Superbonus Too Common**:
- Current: {stats['superbonus_rate']:.4f}% (1 in {stats['spins_per_superbonus']:.0f})
- Target: 0.1-0.25% (1 in 400-1000)
- **Suggestion**: Decrease 4-scatter trigger rate in freegame_condition scatter_triggers
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
    print("BASE BET MODE RTP ANALYSIS")
    print("="*80)
    
    # Initialize config and gamestate
    config = GameConfig()
    gamestate = GameState(config)
    
    # Path to books file
    book_file = os.path.join(config.publish_path, "books_base.jsonl.zst")
    
    # Always run fresh simulation
    num_spins_requested = 100000
    print(f"\n⚠️  Running fresh simulation with current FR0.csv and FR1.csv...")
    print(f"    This will overwrite existing books_base.jsonl.zst")
    
    # Run simulation
    run_base_simulation(config, gamestate, num_spins_requested)
    book_file = os.path.join(config.publish_path, "books_base.jsonl.zst")
    
    # Analyze books
    print("\n" + "="*80)
    print("ANALYZING BASE SPINS")
    print("="*80 + "\n")
    
    analysis_data = analyze_base_books(book_file)
    
    # Calculate statistics
    print("\n" + "="*80)
    print("CALCULATING RTP DECOMPOSITION")
    print("="*80 + "\n")
    
    stats = calculate_rtp_decomposition(analysis_data, cost=1.0)
    
    # Print quick summary
    print("\n" + "="*80)
    print("QUICK SUMMARY")
    print("="*80)
    print(f"Total RTP: {stats['total_rtp']*100:.2f}% (target: 96.2%)")
    print(f"Basegame-Only RTP: {stats['basegame_rtp']*100:.2f}%")
    print(f"Regular Bonus RTP: {stats['regular_bonus_rtp']*100:.2f}%")
    print(f"Superbonus RTP: {stats['superbonus_rtp']*100:.2f}%")
    print(f"Wincap RTP: {stats['wincap_rtp']*100:.2f}%")
    print(f"\nFreegame Hit Rate: {stats['freegame_hit_rate']:.2f}%")
    print(f"Regular Bonus Rate: {stats['regular_bonus_rate']:.2f}%")
    print(f"Superbonus Rate: {stats['superbonus_rate']:.4f}% (1 in {stats['spins_per_superbonus']:.0f})")
    print(f"\nAvg Regular Bonus Win: {stats['avg_regular_bonus_win']:.2f}×")
    print(f"Avg Superbonus Win: {stats['avg_superbonus_win']:.2f}×")
    
    # Generate report
    print("\n" + "="*80)
    print("GENERATING REPORT")
    print("="*80 + "\n")
    
    output_file = os.path.join(
        Path(__file__).parent,
        "BASE_RTP_ANALYSIS.md"
    )
    
    generate_base_rtp_report(stats, analysis_data, output_file=output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

