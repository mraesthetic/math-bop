#!/usr/bin/env python3
"""Calculate VS multiplier weights to add 25× and 50× while maintaining ~2.35× average."""

def calculate_avg(mult_dist):
    """Calculate average multiplier from distribution."""
    total_weight = sum(mult_dist.values())
    weighted_sum = sum(mult * weight for mult, weight in mult_dist.items())
    return weighted_sum / total_weight if total_weight > 0 else 0

def print_distribution(name, mult_dist):
    """Print distribution with statistics."""
    total_weight = sum(mult_dist.values())
    avg = calculate_avg(mult_dist)
    print(f"\n{name}")
    print("="*80)
    print("Multiplier | Weight | Probability | Percentage")
    print("-"*80)
    for mult in sorted(mult_dist.keys()):
        weight = mult_dist[mult]
        prob = weight / total_weight
        print(f"   {mult:2d}×    | {weight:5d} | {prob:11.6f} | {prob*100:8.4f}%")
    print("-"*80)
    print(f"Total Weight: {total_weight}")
    print(f"Average Multiplier: {avg:.6f}×")
    print(f"Target: ~2.35× (within ±0.02)")

# Original distributions
regular_bonus_original = {2: 830, 3: 170, 4: 60, 5: 22, 8: 3, 10: 1}
superbonus_original = {2: 750, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1}

print("ORIGINAL DISTRIBUTIONS")
print("="*80)
print_distribution("Regular Bonus VS (Original)", regular_bonus_original)
print_distribution("Superbonus VS (Original)", superbonus_original)

# Target: Add 25× and 50×, keep average ~2.35×
# Strategy: Add small weights for 25× and 50×, then adjust other weights

print("\n\nCALCULATING NEW DISTRIBUTIONS")
print("="*80)

# Regular Bonus: Add 25× and 50× with very small weights
# Let's try: 25×: 1, 50×: 1 (very rare, <0.2% each)
# Then adjust other weights to maintain average

# New regular bonus distribution
regular_bonus_new = {2: 825, 3: 168, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}

# Calculate current average
avg_reg = calculate_avg(regular_bonus_new)
print(f"\nRegular Bonus (first attempt): avg = {avg_reg:.6f}×")

# Adjust weights iteratively to get closer to 2.35
# If average is too high, reduce weights on high multipliers or increase on 2×
# If average is too low, reduce weight on 2× or increase on mid multipliers

# Let's adjust more carefully
# Target: 2.35× average
# With 25× and 50× added, we need to reduce average contribution from other multipliers
# Reducing 2× weight slightly and adjusting 3×/4× to compensate

regular_bonus_final = {2: 820, 3: 168, 4: 61, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
avg_reg_final = calculate_avg(regular_bonus_final)

# Superbonus: Slightly higher chance of 25×/50× than regular bonus
# Let's use: 25×: 2, 50×: 1 (slightly more than regular bonus)
superbonus_final = {2: 745, 3: 228, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
avg_sup_final = calculate_avg(superbonus_final)

# Fine-tune to get exactly 2.35×
# Regular bonus: Need avg = 2.35
# Current: let's calculate more precisely
def optimize_weights(target_avg, base_dist, high_mults):
    """Optimize weights to hit target average."""
    # Start with base distribution
    mult_dist = base_dist.copy()
    mult_dist.update(high_mults)
    
    # Calculate current average
    current_avg = calculate_avg(mult_dist)
    
    # Adjust 2× weight (most common) to fine-tune
    total_other = sum(w for m, w in mult_dist.items() if m != 2)
    weighted_sum_other = sum(m * w for m, w in mult_dist.items() if m != 2)
    
    # Solve: (2 * w2 + weighted_sum_other) / (w2 + total_other) = target_avg
    # w2 = (target_avg * total_other - weighted_sum_other) / (2 - target_avg)
    w2 = (target_avg * total_other - weighted_sum_other) / (2 - target_avg)
    w2 = round(w2)
    
    mult_dist[2] = int(w2)
    return mult_dist

# Calculate optimal weights
print("\n\nOPTIMIZING TO TARGET 2.35×")
print("="*80)

# Regular bonus with 25×:1, 50×:1
reg_base = {3: 168, 4: 61, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
reg_high = {25: 1, 50: 1}
reg_optimized = optimize_weights(2.35, reg_base, reg_high)
print(f"Regular Bonus Optimized: avg = {calculate_avg(reg_optimized):.6f}×")

# Superbonus with 25×:2, 50×:1
sup_base = {3: 228, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
sup_high = {25: 2, 50: 1}
sup_optimized = optimize_weights(2.35, sup_base, sup_high)
print(f"Superbonus Optimized: avg = {calculate_avg(sup_optimized):.6f}×")

# Let's manually fine-tune to get exactly 2.35
print("\n\nFINAL DISTRIBUTIONS")
print("="*80)

# Regular bonus - manual fine-tuning
reg_final = {2: 818, 3: 168, 4: 61, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
reg_avg = calculate_avg(reg_final)
print_distribution("Regular Bonus VS (Final)", reg_final)
print(f"Deviation from target: {abs(reg_avg - 2.35):.6f}×")

# Superbonus - manual fine-tuning  
sup_final = {2: 743, 3: 228, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
sup_avg = calculate_avg(sup_final)
print_distribution("Superbonus VS (Final)", sup_final)
print(f"Deviation from target: {abs(sup_avg - 2.35):.6f}×")

# Verify constraints
print("\n\nVERIFICATION")
print("="*80)
reg_total = sum(reg_final.values())
sup_total = sum(sup_final.values())

reg_25_50_prob = (reg_final[25] + reg_final[50]) / reg_total
sup_25_50_prob = (sup_final[25] + sup_final[50]) / sup_total

print(f"Regular Bonus:")
print(f"  2× probability: {reg_final[2]/reg_total*100:.4f}% (should be highest)")
print(f"  25× probability: {reg_final[25]/reg_total*100:.4f}%")
print(f"  50× probability: {reg_final[50]/reg_total*100:.4f}%")
print(f"  25× + 50× combined: {reg_25_50_prob*100:.4f}% (should be <1%)")
print(f"  Average: {reg_avg:.6f}× (target: 2.35×, diff: {abs(reg_avg - 2.35):.6f}×)")

print(f"\nSuperbonus:")
print(f"  2× probability: {sup_final[2]/sup_total*100:.4f}% (should be highest)")
print(f"  25× probability: {sup_final[25]/sup_total*100:.4f}%")
print(f"  50× probability: {sup_final[50]/sup_total*100:.4f}%")
print(f"  25× + 50× combined: {sup_25_50_prob*100:.4f}% (should be <1%, slightly > regular)")
print(f"  Average: {sup_avg:.6f}× (target: 2.35×, diff: {abs(sup_avg - 2.35):.6f}×)")

print("\n✅ Final weights for code:")
print(f"Regular Bonus: {reg_final}")
print(f"Superbonus: {sup_final}")

