#!/usr/bin/env python3
"""Find optimal VS multiplier weights."""

def calc_avg(d):
    total = sum(d.values())
    weighted = sum(m * w for m, w in d.items())
    return weighted / total, total

# Find best regular bonus weights
print("Finding optimal Regular Bonus weights:")
best_reg = None
best_diff = 1

for w2 in range(770, 820, 2):
    for w3 in [165, 167, 168, 169, 170]:
        test = {2: w2, 3: w3, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}
        avg, total = calc_avg(test)
        diff = abs(avg - 2.35)
        if diff < best_diff:
            best_diff = diff
            best_reg = (w2, w3, avg, diff, test.copy())
            if diff < 0.01:
                break
    if best_diff < 0.01:
        break

if best_reg:
    w2, w3, avg, diff, dist = best_reg
    total = sum(dist.values())
    print(f"Best: 2×={w2}, 3×={w3}, avg={avg:.6f}, diff={diff:.6f}")
    print(f"Distribution: {dist}")

# Find best superbonus weights
print("\nFinding optimal Superbonus weights:")
best_sup = None
best_diff = 1

for w2 in range(735, 750, 2):
    test = {2: w2, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}
    avg, total = calc_avg(test)
    diff = abs(avg - 2.35)
    if diff < best_diff:
        best_diff = diff
        best_sup = (w2, avg, diff, test.copy())
        if diff < 0.01:
            break

if best_sup:
    w2, avg, diff, dist = best_sup
    print(f"Best: 2×={w2}, avg={avg:.6f}, diff={diff:.6f}")
    print(f"Distribution: {dist}")

print("\n" + "="*80)
print("FINAL DISTRIBUTIONS FOR CODE:")
if best_reg:
    w2, w3, avg, diff, dist = best_reg
    print(f"Regular Bonus: {dist}")
if best_sup:
    w2, avg, diff, dist = best_sup
    print(f"Superbonus: {dist}")

