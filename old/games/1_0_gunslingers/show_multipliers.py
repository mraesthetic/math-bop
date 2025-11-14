#!/usr/bin/env python3
"""Display multiplier distributions with weights and probabilities."""

print("="*80)
print("MULTIPLIER DISTRIBUTIONS FOR GUNSLINGERS: DRAW!")
print("="*80)
print()

# Wild (W) multipliers - used in freegame mode
w_mult = {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}
w_total = sum(w_mult.values())
w_avg = sum(mult * weight for mult, weight in w_mult.items()) / w_total

print("WILD (W) MULTIPLIER DISTRIBUTION")
print("-" * 80)
print(f"Used in: Freegame mode only (not base game)")
print(f"Total weight: {w_total}")
print(f"Average multiplier: {w_avg:.4f}×")
print()
print("Multiplier | Weight | Probability | Percentage")
print("-" * 80)
for mult in sorted(w_mult.keys()):
    weight = w_mult[mult]
    prob = weight / w_total
    print(f"   {mult:2d}×    | {weight:5d} | {prob:11.6f} | {prob*100:8.4f}%")
print()

# VS (DRAW) multipliers - regular bonus (FR0.csv)
# Updated: Added 25× and 50× for increased volatility while maintaining ~2.35× average
vs_bonus_mult = {2: 818, 3: 170, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
vs_bonus_total = sum(vs_bonus_mult.values())
vs_bonus_avg = sum(mult * weight for mult, weight in vs_bonus_mult.items()) / vs_bonus_total

print("VS (DRAW) MULTIPLIER DISTRIBUTION - REGULAR BONUS")
print("-" * 80)
print(f"Used in: Bonus mode (DRAW! YOUR WEAPON) - uses FR0.csv")
print(f"Also used in: Base game (very rare VS appearances)")
print(f"Total weight: {vs_bonus_total}")
print(f"Average multiplier: {vs_bonus_avg:.4f}× (target: 2.35×)")
print(f"25× probability: {vs_bonus_mult[25]/vs_bonus_total*100:.4f}%")
print(f"50× probability: {vs_bonus_mult[50]/vs_bonus_total*100:.4f}%")
print()
print("Multiplier | Weight | Probability | Percentage")
print("-" * 80)
for mult in sorted(vs_bonus_mult.keys()):
    weight = vs_bonus_mult[mult]
    prob = weight / vs_bonus_total
    print(f"   {mult:2d}×    | {weight:5d} | {prob:11.6f} | {prob*100:8.4f}%")
print()

# VS (DRAW) multipliers - superbonus (FR1.csv)
# Updated: Added 25× and 50× for increased volatility (slightly higher chance than regular bonus)
vs_super_mult = {2: 743, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
vs_super_total = sum(vs_super_mult.values())
vs_super_avg = sum(mult * weight for mult, weight in vs_super_mult.items()) / vs_super_total

print("VS (DRAW) MULTIPLIER DISTRIBUTION - SUPERBONUS")
print("-" * 80)
print(f"Used in: Superbonus mode (SUPER DRAW!) - uses FR1.csv")
print(f"Total weight: {vs_super_total}")
print(f"Average multiplier: {vs_super_avg:.4f}× (target: 2.35×)")
print(f"25× probability: {vs_super_mult[25]/vs_super_total*100:.4f}%")
print(f"50× probability: {vs_super_mult[50]/vs_super_total*100:.4f}%")
print()
print("Multiplier | Weight | Probability | Percentage")
print("-" * 80)
for mult in sorted(vs_super_mult.keys()):
    weight = vs_super_mult[mult]
    prob = weight / vs_super_total
    print(f"   {mult:2d}×    | {weight:5d} | {prob:11.6f} | {prob*100:8.4f}%")
print()

print("="*80)
print("SUMMARY")
print("="*80)
print(f"Wild (W) - Average: {w_avg:.4f}×")
print(f"VS Bonus - Average: {vs_bonus_avg:.4f}×")
print(f"VS Super  - Average: {vs_super_avg:.4f}×")
print()
print("APPLICATION METHOD:")
print("  • VS multipliers: Applied per REEL (multiplicative when multiple reels)")
print("    Example: Reel 2 has 3×, Reel 4 has 5× → Combined = 3 × 5 = 15×")
print("    Cap: Combined multipliers capped at 500× (increased from 250×)")
print()
print("  • Wild multipliers: Applied per SYMBOL (additive method)")
print("    Example: Line has W symbols with [2×, 3×, 5×] → Combined = 2 + 3 + 5 = 10×")
print("    No cap on wild multipliers")

