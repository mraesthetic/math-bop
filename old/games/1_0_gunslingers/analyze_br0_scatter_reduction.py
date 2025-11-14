#!/usr/bin/env python3
"""
Analyze BR0.csv scatter distribution and calculate reduction needed to achieve target trigger rates.

Current: 3-scatter 9.79%, 4-scatter 0.22% (total 10.01%)
Target: 3-scatter 0.55%, 4-scatter 0.10% (total 0.65%)

Reduction factor needed: ~18x for 3-scatter, ~2x for 4-scatter
But since they're weighted 98:2, we need to reduce overall scatter density significantly.
"""

import csv
from collections import Counter
import math

def analyze_scatter_distribution(reelset_file):
    """Analyze current scatter distribution in BR0.csv"""
    scatter_counts = [0, 0, 0, 0, 0]
    total_rows = 0
    scatter_positions = []  # List of (row, reel) tuples where scatters appear
    
    with open(reelset_file, 'r') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if len(row) == 5:
                total_rows += 1
                for reel_idx in range(5):
                    if row[reel_idx].strip() == 'S':
                        scatter_counts[reel_idx] += 1
                        scatter_positions.append((row_idx, reel_idx))
    
    total_scatters = sum(scatter_counts)
    scatter_density = total_scatters / (total_rows * 5) * 100
    
    return {
        'total_rows': total_rows,
        'total_scatters': total_scatters,
        'scatter_counts': scatter_counts,
        'scatter_density': scatter_density,
        'scatter_positions': scatter_positions,
    }

def calculate_trigger_probability(scatter_counts, total_rows, scatter_triggers_weights):
    """
    Estimate trigger probability based on scatter distribution.
    
    For a simplified calculation:
    - Probability of scatter on reel i = scatter_counts[i] / total_rows
    - We need to calculate probability of getting 3+ scatters across 5 reels
    """
    # Calculate scatter probability per reel
    scatter_probs = [count / total_rows for count in scatter_counts]
    
    # For a rough estimate, we can use:
    # P(3 scatters) ≈ product of 3 reel probs × product of 2 non-scatter probs × combinations
    # This is simplified but gives us a ballpark
    
    # More accurate: calculate expected trigger rate
    # Using simulation approach would be more accurate, but for estimation:
    
    # Average scatter probability
    avg_scatter_prob = sum(scatter_probs) / 5
    
    # Rough estimate: probability of getting exactly 3 scatters
    # Using binomial approximation (not perfect for different probs per reel, but close enough)
    p_3_scatters = math.comb(5, 3) * (avg_scatter_prob ** 3) * ((1 - avg_scatter_prob) ** 2)
    p_4_scatters = math.comb(5, 4) * (avg_scatter_prob ** 4) * ((1 - avg_scatter_prob) ** 1)
    p_5_scatters = avg_scatter_prob ** 5
    
    # Total probability of triggering (3+ scatters)
    p_trigger = p_3_scatters + p_4_scatters + p_5_scatters
    
    # Weighted by scatter_triggers configuration
    if scatter_triggers_weights:
        total_weight = sum(scatter_triggers_weights.values())
        p_3_weighted = p_trigger * (scatter_triggers_weights.get(3, 0) / total_weight)
        p_4_weighted = p_trigger * (scatter_triggers_weights.get(4, 0) / total_weight)
    else:
        p_3_weighted = p_trigger * 0.98  # Default 98% for 3-scatter
        p_4_weighted = p_trigger * 0.02  # Default 2% for 4-scatter
    
    return {
        'avg_scatter_prob': avg_scatter_prob,
        'p_3_scatters': p_3_scatters,
        'p_4_scatters': p_4_scatters,
        'p_trigger': p_trigger,
        'p_3_weighted': p_3_weighted * 100,  # Convert to percentage
        'p_4_weighted': p_4_weighted * 100,
    }

def propose_scatter_reduction(current_analysis, target_rates):
    """
    Propose scatter reduction to achieve target trigger rates.
    
    target_rates: {'3_scatter': 0.55, '4_scatter': 0.10}
    """
    # Current rates from analysis
    current_3_scatter_rate = 9.79  # From BASE_RTP_ANALYSIS.md
    current_4_scatter_rate = 0.22
    
    # Calculate reduction factors
    reduction_factor_3 = current_3_scatter_rate / target_rates['3_scatter']
    reduction_factor_4 = current_4_scatter_rate / target_rates['4_scatter']
    
    # Use the more aggressive reduction (3-scatter needs more reduction)
    # But we need to be careful - the scatter_triggers weights affect the ratio
    # If we reduce scatters by 18x, both rates drop, but the ratio stays roughly 98:2
    
    # Target: 0.55% for 3-scatter, 0.10% for 4-scatter
    # Current: 9.79% for 3-scatter, 0.22% for 4-scatter
    # Ratio: 9.79/0.22 = 44.5:1, Target: 0.55/0.10 = 5.5:1
    
    # The scatter_triggers weights are {3: 98, 4: 2} = 49:1 ratio
    # So if we have 3+ scatters, 98% become 3-scatter triggers, 2% become 4-scatter
    
    # If current 3-scatter rate is 9.79%, and it's 98% of triggers:
    # Total trigger rate = 9.79 / 0.98 = 9.99%
    # 4-scatter rate = 9.99 * 0.02 = 0.20% (close to observed 0.22%)
    
    # Target: 3-scatter 0.55% (98% of triggers), so total trigger rate = 0.55 / 0.98 = 0.56%
    # Target 4-scatter = 0.56 * 0.02 = 0.011% (but we want 0.10%, so we need different weights!)
    
    # Actually, wait - the target says 0.10% for 4-scatter, not 0.011%
    # This means we need to adjust the scatter_triggers weights, OR
    # We need a different reduction strategy
    
    # Let's recalculate: If total trigger rate should be ~0.65% (0.55% + 0.10%)
    # And we want 0.55% for 3-scatter and 0.10% for 4-scatter
    # Then the ratio should be 5.5:1, not 49:1
    
    # So we need to change scatter_triggers weights from {3: 98, 4: 2} to approximately {3: 85, 4: 15}
    # But the user said to keep bonus averages as-is, so maybe they want to adjust the weights?
    
    # Actually, let me re-read the requirements...
    # "Regular bonus (3 scatter): ~0.55% trigger rate"
    # "Superbonus (4 scatter): ~0.10% trigger rate"
    
    # If we keep scatter_triggers at {3: 98, 4: 2}, then:
    # - 98% of triggers become 3-scatter = 0.55% → total triggers = 0.55/0.98 = 0.56%
    # - 2% become 4-scatter = 0.56 * 0.02 = 0.011% (not 0.10%!)
    
    # So we need to change the weights to achieve 0.55% and 0.10%
    # If total trigger rate is T, and weights are {3: w3, 4: w4}:
    # - 3-scatter rate = T * w3 / (w3 + w4) = 0.55%
    # - 4-scatter rate = T * w4 / (w3 + w4) = 0.10%
    # - T = 0.55 + 0.10 = 0.65%
    # - w3 / (w3 + w4) = 0.55 / 0.65 = 0.846
    # - w4 / (w3 + w4) = 0.10 / 0.65 = 0.154
    # - So weights should be approximately {3: 85, 4: 15} (ratio 5.67:1)
    
    # But first, let's reduce scatter density to achieve ~0.65% total trigger rate
    # Current total trigger rate = 9.99%
    # Target = 0.65%
    # Reduction factor = 9.99 / 0.65 = 15.4x
    
    # Current scatter density = 1.46%
    # Target scatter density ≈ 1.46% / 15.4 = 0.095%
    
    # Current total scatters = 16
    # Target total scatters ≈ 16 / 15.4 = 1.04 ≈ 1 scatter
    
    # But we need at least 3 scatters to trigger, so we need at least 3 scatters total
    # Actually, we need scatters on different reels to allow 3+ scatters to appear
    
    # Let's think differently: we need to reduce scatter probability per reel
    # Current: [5, 1, 5, 1, 4] = 16 total
    # If we reduce by 15.4x: [0.32, 0.06, 0.32, 0.06, 0.26] ≈ [0, 0, 0, 0, 0]
    # That's too aggressive - we'd have no scatters!
    
    # Let's use a more conservative approach:
    # Reduce to approximately 1/15th, but keep at least 1 scatter per reel that needs it
    # For 3-scatter triggers, we need scatters on at least 3 reels
    
    # Better approach: Reduce to 1 scatter per reel = 5 total scatters
    # That's 16 / 5 = 3.2x reduction, which gives us 9.99% / 3.2 = 3.12% trigger rate
    # Still too high!
    
    # Let's calculate more precisely:
    # We want 0.65% total trigger rate
    # Current: 9.99% with 16 scatters
    # If scatter probability scales linearly (rough approximation):
    # New scatter count = 16 * (0.65 / 9.99) = 16 * 0.065 = 1.04
    
    # But scatter probability doesn't scale linearly - it scales with the cube (for 3-scatter)
    # P(3 scatters) ≈ p^3 where p is scatter probability
    # So if we want to reduce P(3) by factor R, we need to reduce p by factor R^(1/3)
    
    # Reduction factor for 3-scatter rate: 9.79 / 0.55 = 17.8
    # So we need to reduce scatter probability by: 17.8^(1/3) = 2.61x
    
    # Current avg scatter prob = 16 / (219 * 5) = 0.0146
    # Target avg scatter prob = 0.0146 / 2.61 = 0.0056
    # Target total scatters = 0.0056 * 219 * 5 = 6.13 ≈ 6 scatters
    
    # But we also need to consider 4-scatter triggers
    # For 4-scatter: reduction factor = 0.22 / 0.10 = 2.2x
    # Scatter prob reduction = 2.2^(1/4) = 1.22x
    
    # The 3-scatter requirement is more restrictive, so we'll use that
    
    reduction_factor = reduction_factor_3
    scatter_prob_reduction = reduction_factor ** (1/3)  # Cube root for 3-scatter probability
    
    current_total_scatters = current_analysis['total_scatters']
    current_scatter_counts = current_analysis['scatter_counts']
    
    # Calculate target scatter counts
    target_total_scatters = int(current_total_scatters / scatter_prob_reduction)
    # Ensure we have at least 3 scatters (minimum for 3-scatter trigger)
    target_total_scatters = max(target_total_scatters, 3)
    
    # Distribute scatters proportionally across reels
    # But keep at least 1 scatter on reels that currently have scatters (for 3+ scatter possibility)
    target_scatter_counts = []
    for count in current_scatter_counts:
        if count > 0:
            # Reduce proportionally, but keep at least 1 if originally had scatters
            new_count = max(1, int(count / scatter_prob_reduction))
            target_scatter_counts.append(new_count)
        else:
            target_scatter_counts.append(0)
    
    # Adjust to match target_total_scatters
    current_sum = sum(target_scatter_counts)
    if current_sum != target_total_scatters:
        # Adjust by adding/removing scatters from reels with most scatters
        diff = target_total_scatters - current_sum
        if diff > 0:
            # Add scatters to reels with most scatters
            for _ in range(diff):
                max_idx = target_scatter_counts.index(max(target_scatter_counts))
                target_scatter_counts[max_idx] += 1
        else:
            # Remove scatters from reels with most scatters (but keep at least 1)
            for _ in range(abs(diff)):
                # Find reels with more than 1 scatter
                candidates = [i for i, c in enumerate(target_scatter_counts) if c > 1]
                if candidates:
                    max_idx = max(candidates, key=lambda i: target_scatter_counts[i])
                    target_scatter_counts[max_idx] -= 1
    
    return {
        'reduction_factor': reduction_factor,
        'scatter_prob_reduction': scatter_prob_reduction,
        'target_total_scatters': target_total_scatters,
        'target_scatter_counts': target_scatter_counts,
        'current_scatter_counts': current_scatter_counts,
    }

def main():
    reelset_file = 'reels/BR0.csv'
    
    print("=" * 80)
    print("BR0.csv Scatter Distribution Analysis")
    print("=" * 80)
    print()
    
    # Analyze current distribution
    current = analyze_scatter_distribution(reelset_file)
    
    print("Current Scatter Distribution:")
    print(f"  Total rows: {current['total_rows']}")
    print(f"  Total scatter symbols: {current['total_scatters']}")
    print(f"  Scatter counts per reel: {current['scatter_counts']}")
    print(f"  Scatter density: {current['scatter_density']:.2f}%")
    print()
    
    # Calculate current trigger probabilities (rough estimate)
    scatter_triggers_weights = {3: 98, 4: 2}
    current_probs = calculate_trigger_probability(
        current['scatter_counts'],
        current['total_rows'],
        scatter_triggers_weights
    )
    
    print("Current Estimated Trigger Probabilities:")
    print(f"  Average scatter probability per reel: {current_probs['avg_scatter_prob']:.4f}")
    print(f"  Estimated 3-scatter trigger rate: {current_probs['p_3_weighted']:.2f}%")
    print(f"  Estimated 4-scatter trigger rate: {current_probs['p_4_weighted']:.2f}%")
    print(f"  (Note: Actual rates from simulation: 9.79% and 0.22%)")
    print()
    
    # Target rates
    target_rates = {
        '3_scatter': 0.55,  # ~1 in 180 spins
        '4_scatter': 0.10,  # ~1 in 1000 spins
    }
    
    print("Target Trigger Rates:")
    print(f"  3-scatter (Regular Bonus): {target_rates['3_scatter']:.2f}% (~1 in {100/target_rates['3_scatter']:.0f} spins)")
    print(f"  4-scatter (Superbonus): {target_rates['4_scatter']:.2f}% (~1 in {100/target_rates['4_scatter']:.0f} spins)")
    print(f"  Total freegame: {target_rates['3_scatter'] + target_rates['4_scatter']:.2f}%")
    print()
    
    # Propose reduction
    proposal = propose_scatter_reduction(current, target_rates)
    
    print("Proposed Scatter Reduction:")
    print(f"  Reduction factor needed (3-scatter): {proposal['reduction_factor']:.2f}x")
    print(f"  Scatter probability reduction: {proposal['scatter_prob_reduction']:.2f}x")
    print(f"  Current total scatters: {current['total_scatters']}")
    print(f"  Target total scatters: {proposal['target_total_scatters']}")
    print()
    print("Scatter counts per reel (before → after):")
    for reel_idx in range(5):
        current_count = proposal['current_scatter_counts'][reel_idx]
        target_count = proposal['target_scatter_counts'][reel_idx]
        change = target_count - current_count
        print(f"  Reel {reel_idx + 1}: {current_count} → {target_count} ({change:+.0f})")
    print()
    
    # Estimate new trigger rates
    new_probs = calculate_trigger_probability(
        proposal['target_scatter_counts'],
        current['total_rows'],
        scatter_triggers_weights
    )
    
    print("Estimated New Trigger Rates (with current weights {3: 98, 4: 2}):")
    print(f"  Estimated 3-scatter trigger rate: {new_probs['p_3_weighted']:.2f}%")
    print(f"  Estimated 4-scatter trigger rate: {new_probs['p_4_weighted']:.2f}%")
    print()
    
    # Note about weights
    print("NOTE: To achieve target rates of 0.55% (3-scatter) and 0.10% (4-scatter),")
    print("      we may need to adjust scatter_triggers weights from {3: 98, 4: 2}")
    print("      to approximately {3: 85, 4: 15} to achieve the 5.5:1 ratio.")
    print()

if __name__ == '__main__':
    main()

