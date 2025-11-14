#!/usr/bin/env python3
"""
Calculate precise scatter reduction needed for BR0.csv to achieve target trigger rates.

Based on actual simulation results:
- Current: 3-scatter 9.79%, 4-scatter 0.22% with 16 scatters and weights {3: 98, 4: 2}
- Target: 3-scatter 0.55%, 4-scatter 0.10%

Key insights:
1. Trigger probability scales roughly with scatter density^3 (for 3-scatter)
2. We need ~18x reduction in 3-scatter rate
3. We also need to adjust scatter_triggers weights to achieve 5.5:1 ratio (not 49:1)
"""

import csv
import math

def analyze_current_br0():
    """Get current scatter distribution"""
    scatter_counts = [0, 0, 0, 0, 0]
    total_rows = 0
    scatter_positions = []
    
    with open('reels/BR0.csv', 'r') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if len(row) == 5:
                total_rows += 1
                for reel_idx in range(5):
                    if row[reel_idx].strip() == 'S':
                        scatter_counts[reel_idx] += 1
                        scatter_positions.append((row_idx, reel_idx))
    
    return {
        'total_rows': total_rows,
        'scatter_counts': scatter_counts,
        'total_scatters': sum(scatter_counts),
        'scatter_positions': scatter_positions,
    }

def calculate_expected_trigger_rate(scatter_counts, total_rows, scatter_weights):
    """
    More accurate calculation using combinatorial probability.
    
    For each reel, probability of scatter = scatter_count / total_rows
    We need to calculate probability of getting 3+ scatters across 5 reels.
    """
    reel_probs = [count / total_rows for count in scatter_counts]
    
    # Calculate probability of exactly k scatters
    # Using inclusion-exclusion or direct calculation
    
    # For 5 reels with different probabilities, we can use:
    # P(exactly 3) = sum of all combinations of 3 reels having scatter * 2 reels not having scatter
    from itertools import combinations
    
    p_exact_3 = 0
    p_exact_4 = 0
    p_exact_5 = 0
    
    # Exactly 3 scatters
    for combo in combinations(range(5), 3):
        prob = 1.0
        for i in range(5):
            if i in combo:
                prob *= reel_probs[i]
            else:
                prob *= (1 - reel_probs[i])
        p_exact_3 += prob
    
    # Exactly 4 scatters
    for combo in combinations(range(5), 4):
        prob = 1.0
        for i in range(5):
            if i in combo:
                prob *= reel_probs[i]
            else:
                prob *= (1 - reel_probs[i])
        p_exact_4 += prob
    
    # Exactly 5 scatters
    p_exact_5 = 1.0
    for p in reel_probs:
        p_exact_5 *= p
    
    # Total trigger probability (3+ scatters)
    p_trigger = p_exact_3 + p_exact_4 + p_exact_5
    
    # Weighted by scatter_triggers configuration
    total_weight = sum(scatter_weights.values())
    p_3_weighted = p_trigger * (scatter_weights.get(3, 0) / total_weight)
    p_4_weighted = p_trigger * (scatter_weights.get(4, 0) / total_weight)
    
    return {
        'p_exact_3': p_exact_3,
        'p_exact_4': p_exact_4,
        'p_exact_5': p_exact_5,
        'p_trigger': p_trigger,
        'p_3_weighted': p_3_weighted * 100,
        'p_4_weighted': p_4_weighted * 100,
    }

def main():
    print("=" * 80)
    print("BR0.csv Scatter Reduction Calculation")
    print("=" * 80)
    print()
    
    # Current state
    current = analyze_current_br0()
    current_weights = {3: 98, 4: 2}
    
    print("Current State:")
    print(f"  Total rows: {current['total_rows']}")
    print(f"  Scatter counts per reel: {current['scatter_counts']}")
    print(f"  Total scatters: {current['total_scatters']}")
    print(f"  Scatter density: {current['total_scatters'] / (current['total_rows'] * 5) * 100:.2f}%")
    print(f"  Scatter_triggers weights: {current_weights}")
    print()
    
    # Calculate current expected rates
    current_probs = calculate_expected_trigger_rate(
        current['scatter_counts'],
        current['total_rows'],
        current_weights
    )
    
    print("Current Calculated Trigger Rates:")
    print(f"  P(exactly 3 scatters): {current_probs['p_exact_3'] * 100:.4f}%")
    print(f"  P(exactly 4 scatters): {current_probs['p_exact_4'] * 100:.4f}%")
    print(f"  P(exactly 5 scatters): {current_probs['p_exact_5'] * 100:.4f}%")
    print(f"  P(3+ scatters total): {current_probs['p_trigger'] * 100:.4f}%")
    print(f"  3-scatter trigger rate (weighted): {current_probs['p_3_weighted']:.4f}%")
    print(f"  4-scatter trigger rate (weighted): {current_probs['p_4_weighted']:.4f}%")
    print(f"  (Actual from simulation: 9.79% and 0.22%)")
    print()
    
    # Target rates
    target_3_scatter = 0.55
    target_4_scatter = 0.10
    target_total = target_3_scatter + target_4_scatter
    
    print("Target Trigger Rates:")
    print(f"  3-scatter: {target_3_scatter:.2f}% (~1 in {100/target_3_scatter:.0f} spins)")
    print(f"  4-scatter: {target_4_scatter:.2f}% (~1 in {100/target_4_scatter:.0f} spins)")
    print(f"  Total: {target_total:.2f}%")
    print(f"  Ratio (3:4): {target_3_scatter/target_4_scatter:.1f}:1")
    print()
    
    # Calculate reduction needed
    # Current: 9.79% (3-scatter), Target: 0.55%
    reduction_factor_3 = 9.79 / target_3_scatter  # 17.8x
    
    # Current total trigger rate (estimated): 9.79 / 0.98 = 9.99%
    # Target total trigger rate: 0.65%
    reduction_factor_total = 9.99 / target_total  # 15.4x
    
    print("Reduction Analysis:")
    print(f"  3-scatter reduction needed: {reduction_factor_3:.2f}x")
    print(f"  Total trigger reduction needed: {reduction_factor_total:.2f}x")
    print()
    
    # Since trigger probability scales roughly with scatter density^3 (for 3-scatter):
    # P_new = P_old * (density_new / density_old)^3
    # So: density_new / density_old = (P_new / P_old)^(1/3)
    density_reduction = (target_total / 9.99) ** (1/3)
    
    print(f"  Scatter density reduction factor: {density_reduction:.2f}x")
    print(f"  (Using cube root since 3-scatter probability scales with density^3)")
    print()
    
    # Calculate target scatter counts
    current_density = current['total_scatters'] / (current['total_rows'] * 5)
    target_density = current_density / density_reduction
    target_total_scatters = int(target_density * current['total_rows'] * 5)
    
    # Ensure minimum of 3 scatters (needed for 3-scatter trigger)
    target_total_scatters = max(target_total_scatters, 3)
    
    print(f"  Current scatter density: {current_density:.6f}")
    print(f"  Target scatter density: {target_density:.6f}")
    print(f"  Current total scatters: {current['total_scatters']}")
    print(f"  Target total scatters: {target_total_scatters}")
    print()
    
    # Distribute scatters proportionally
    # Strategy: Reduce each reel proportionally, but keep at least 1 scatter on reels that need it
    # For 3-scatter triggers, we need scatters on at least 3 different reels
    
    target_counts = []
    for count in current['scatter_counts']:
        if count > 0:
            # Reduce proportionally
            new_count = max(1, int(count / density_reduction))
            target_counts.append(new_count)
        else:
            target_counts.append(0)
    
    # Adjust to match target_total_scatters
    current_sum = sum(target_counts)
    if current_sum != target_total_scatters:
        diff = target_total_scatters - current_sum
        # Adjust by modifying counts on reels with most scatters
        while current_sum != target_total_scatters:
            if diff > 0:
                # Add to reel with most scatters
                max_idx = target_counts.index(max(target_counts))
                target_counts[max_idx] += 1
                current_sum += 1
            else:
                # Remove from reel with most scatters (but keep at least 1)
                candidates = [i for i, c in enumerate(target_counts) if c > 1]
                if candidates:
                    max_idx = max(candidates, key=lambda i: target_counts[i])
                    target_counts[max_idx] -= 1
                    current_sum -= 1
                else:
                    break
    
    print("Proposed Scatter Distribution:")
    print("  Reel | Current | Target | Change")
    print("  -----|---------|--------|-------")
    for i in range(5):
        curr = current['scatter_counts'][i]
        targ = target_counts[i]
        change = targ - curr
        print(f"  {i+1}    | {curr:3d}     | {targ:3d}    | {change:+3d}")
    print(f"  Total| {sum(current['scatter_counts']):3d}     | {sum(target_counts):3d}    | {sum(target_counts)-sum(current['scatter_counts']):+3d}")
    print()
    
    # Calculate expected new rates with current weights
    new_probs_current_weights = calculate_expected_trigger_rate(
        target_counts,
        current['total_rows'],
        current_weights
    )
    
    print("Expected New Rates (with current weights {3: 98, 4: 2}):")
    print(f"  3-scatter trigger rate: {new_probs_current_weights['p_3_weighted']:.4f}%")
    print(f"  4-scatter trigger rate: {new_probs_current_weights['p_4_weighted']:.4f}%")
    print(f"  Total trigger rate: {new_probs_current_weights['p_trigger'] * 100:.4f}%")
    print()
    
    # Calculate required weights to achieve target ratio
    # We want 0.55% : 0.10% = 5.5:1 ratio
    # If total trigger rate is T, then:
    #   0.55 = T * w3 / (w3 + w4)
    #   0.10 = T * w4 / (w3 + w4)
    #   So: w3 / w4 = 0.55 / 0.10 = 5.5
    #   If w3 + w4 = 100, then: w3 = 84.6, w4 = 15.4
    
    target_weights = {3: 85, 4: 15}  # Approximate 5.67:1 ratio
    
    new_probs_target_weights = calculate_expected_trigger_rate(
        target_counts,
        current['total_rows'],
        target_weights
    )
    
    print("Expected New Rates (with adjusted weights {3: 85, 4: 15}):")
    print(f"  3-scatter trigger rate: {new_probs_target_weights['p_3_weighted']:.4f}%")
    print(f"  4-scatter trigger rate: {new_probs_target_weights['p_4_weighted']:.4f}%")
    print(f"  Total trigger rate: {new_probs_target_weights['p_trigger'] * 100:.4f}%")
    print()
    
    # Fine-tune: We may need to adjust scatter counts slightly to hit exact targets
    # But first, let's see what the calculation gives us
    
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print("Actions needed:")
    print(f"  1. Reduce scatters from {current['total_scatters']} to {target_total_scatters} total")
    print(f"  2. Adjust scatter_triggers weights from {current_weights} to {target_weights}")
    print(f"  3. Verify with simulation after changes")
    print()

if __name__ == '__main__':
    main()

