#!/usr/bin/env python3
"""Verify new VS multiplier weights are correct."""

def calc_avg(mult_dist):
    total = sum(mult_dist.values())
    weighted = sum(m * weight for m, weight in mult_dist.items())
    avg = weighted / total if total > 0 else 0
    return avg, total, weighted

# New distributions from code
regular_bonus = {2: 810, 3: 168, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
superbonus = {2: 740, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}

reg_avg, reg_total, reg_weighted = calc_avg(regular_bonus)
sup_avg, sup_total, sup_weighted = calc_avg(superbonus)

print("VERIFICATION OF NEW VS MULTIPLIER DISTRIBUTIONS")
print("="*80)
print(f"\nRegular Bonus VS:")
print(f"  Distribution: {regular_bonus}")
print(f"  Total weight: {reg_total}")
print(f"  Weighted sum: {reg_weighted}")
print(f"  Average: {reg_avg:.6f}×")
print(f"  Target: 2.35× | Deviation: {abs(reg_avg - 2.35):.6f}×")
print(f"  Within ±0.02? {abs(reg_avg - 2.35) <= 0.02}")

reg_25_50_pct = (regular_bonus[25] + regular_bonus[50]) / reg_total * 100
reg_2_pct = regular_bonus[2] / reg_total * 100
print(f"  25× probability: {regular_bonus[25]/reg_total*100:.4f}%")
print(f"  50× probability: {regular_bonus[50]/reg_total*100:.4f}%")
print(f"  25× + 50× combined: {reg_25_50_pct:.4f}% (< 1%)")
print(f"  2× probability: {reg_2_pct:.4f}% (highest: {reg_2_pct == max(v/reg_total*100 for v in regular_bonus.values())})")

print(f"\nSuperbonus VS:")
print(f"  Distribution: {superbonus}")
print(f"  Total weight: {sup_total}")
print(f"  Weighted sum: {sup_weighted}")
print(f"  Average: {sup_avg:.6f}×")
print(f"  Target: 2.35× | Deviation: {abs(sup_avg - 2.35):.6f}×")
print(f"  Within ±0.02? {abs(sup_avg - 2.35) <= 0.02}")

sup_25_50_pct = (superbonus[25] + superbonus[50]) / sup_total * 100
sup_2_pct = superbonus[2] / sup_total * 100
print(f"  25× probability: {superbonus[25]/sup_total*100:.4f}%")
print(f"  50× probability: {superbonus[50]/sup_total*100:.4f}%")
print(f"  25× + 50× combined: {sup_25_50_pct:.4f}% (< 1%)")
print(f"  2× probability: {sup_2_pct:.4f}% (highest: {sup_2_pct == max(v/sup_total*100 for v in superbonus.values())})")

print(f"\nComparison:")
print(f"  Superbonus 25×+50× ({sup_25_50_pct:.4f}%) > Regular ({reg_25_50_pct:.4f}%): {sup_25_50_pct > reg_25_50_pct}")

if abs(reg_avg - 2.35) > 0.02 or abs(sup_avg - 2.35) > 0.02:
    print(f"\n⚠️  WARNING: Averages are outside ±0.02 tolerance!")
    print(f"   Need to adjust weights to get closer to 2.35×")
else:
    print(f"\n✅ All constraints met!")

