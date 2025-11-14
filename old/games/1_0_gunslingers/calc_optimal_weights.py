#!/usr/bin/env python3
"""Calculate optimal VS multiplier weights."""

def calc_avg(d):
    total = sum(d.values())
    weighted = sum(m * w for m, w in d.items())
    return weighted / total, total

# Original distributions
orig_reg = {2: 830, 3: 170, 4: 60, 5: 22, 8: 3, 10: 1}
orig_sup = {2: 750, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1}

orig_reg_avg, orig_reg_total = calc_avg(orig_reg)
orig_sup_avg, orig_sup_total = calc_avg(orig_sup)

print("ORIGINAL:")
print(f"Regular: avg={orig_reg_avg:.6f}×")
print(f"Superbonus: avg={orig_sup_avg:.6f}×")

# Find best weights for regular bonus
print("\nREGULAR BONUS - Finding optimal weights:")
best_reg = None
best_diff = 1

for w2 in range(805, 825, 1):
    for w3 in [168, 169, 170, 171]:
        test = {2: w2, 3: w3, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
        avg, total = calc_avg(test)
        diff = abs(avg - 2.35)
        if diff < best_diff:
            best_diff = diff
            best_reg = (w2, w3, avg, diff, test.copy())
            if diff < 0.005:
                break
    if best_diff < 0.005:
        break

if best_reg:
    w2, w3, avg, diff, dist = best_reg
    total = sum(dist.values())
    reg_25_50_pct = (dist[25] + dist[50]) / total * 100
    reg_2_pct = dist[2] / total * 100
    print(f"Best Regular: 2×={w2}, 3×={w3}")
    print(f"  Average: {avg:.6f}× (diff: {diff:.6f}×)")
    print(f"  Distribution: {dist}")
    print(f"  25×+50× prob: {reg_25_50_pct:.4f}%")
    print(f"  2× prob: {reg_2_pct:.4f}%")

# Find best weights for superbonus
print("\nSUPERBONUS - Finding optimal weights:")
best_sup = None
best_diff = 1

for w2 in range(740, 750, 1):
    test = {2: w2, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
    avg, total = calc_avg(test)
    diff = abs(avg - 2.35)
    if diff < best_diff:
        best_diff = diff
        best_sup = (w2, avg, diff, test.copy())
        if diff < 0.005:
            break

if best_sup:
    w2, avg, diff, dist = best_sup
    total = sum(dist.values())
    sup_25_50_pct = (dist[25] + dist[50]) / total * 100
    sup_2_pct = dist[2] / total * 100
    print(f"Best Superbonus: 2×={w2}")
    print(f"  Average: {avg:.6f}× (diff: {diff:.6f}×)")
    print(f"  Distribution: {dist}")
    print(f"  25×+50× prob: {sup_25_50_pct:.4f}%")
    print(f"  2× prob: {sup_2_pct:.4f}%")

print("\n" + "="*80)
print("FINAL DISTRIBUTIONS:")
if best_reg:
    w2, w3, avg, diff, dist = best_reg
    print(f"Regular Bonus: {dist}")
if best_sup:
    w2, avg, diff, dist = best_sup
    print(f"Superbonus: {dist}")

