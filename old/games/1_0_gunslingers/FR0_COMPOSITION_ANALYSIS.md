# FR0.csv Composition Analysis

**Purpose**: Analyze FR0.csv (regular bonus) to understand why RTP is only 46.39% (target: 96.2%)

---

## Symbol Counts - FR0.csv (Regular Bonus)

### Premium Symbols (H1-H4)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **H1** | 104 | 10.25% |
| **H2** | 85 | 8.37% |
| **H3** | 91 | 8.97% |
| **H4** | 84 | 8.28% |
| **Total Premiums** | 364 | 35.86% |

### Low Symbols (L1-L5)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **L1** | 133 | 13.10% |
| **L2** | 103 | 10.15% |
| **L3** | 121 | 11.92% |
| **L4** | 123 | 12.12% |
| **L5** | 116 | 11.43% |
| **Total Lows** | 596 | 58.72% |

### Special Symbols

| Symbol | Count | Percentage |
|--------|-------|------------|
| **W (Wild)** | 39 | 3.84% |
| **VS (DRAW)** | 5 | 0.49% |
| **S (Scatter)** | 11 | 1.08% |

---

## Symbol Counts - FR1.csv (Superbonus)

### Premium Symbols (H1-H4)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **H1** | 35 | 3.45% |
| **H2** | 34 | 3.35% |
| **H3** | 270 | 26.60% |
| **H4** | 29 | 2.86% |
| **Total Premiums** | 368 | 36.26% |

### Low Symbols (L1-L5)

| Symbol | Count | Percentage |
|--------|-------|------------|
| **L1** | 150 | 14.78% |
| **L2** | 75 | 7.39% |
| **L3** | 70 | 6.90% |
| **L4** | 165 | 16.26% |
| **L5** | 155 | 15.27% |
| **Total Lows** | 615 | 60.59% |

### Special Symbols

| Symbol | Count | Percentage |
|--------|-------|------------|
| **W (Wild)** | 19 | 1.87% |
| **VS (DRAW)** | 2 | 0.20% |
| **S (Scatter)** | 11 | 1.08% |

---

## Comparison: FR0 vs FR1

### Key Ratios

| Metric | FR0 (Regular Bonus) | FR1 (Superbonus) | Difference |
|--------|---------------------|------------------|------------|
| **Premium/Low Ratio** | 0.611 | 0.598 | -0.012 |
| **Premium %** | 35.86% | 36.26% | +0.39% |
| **Low %** | 58.72% | 60.59% | +1.87% |
| **Wild %** | 3.84% | 1.87% | -1.97% |
| **VS %** | 0.49% | 0.20% | -0.30% |
| **Scatter %** | 1.08% | 1.08% | +0.00% |

### Symbol Count Differences

| Symbol | FR0 Count | FR1 Count | Difference | % Change |
|--------|-----------|-----------|------------|----------|
| **H1** | 104 | 35 | -69 | -66.3% |
| **H2** | 85 | 34 | -51 | -60.0% |
| **H3** | 91 | 270 | +179 | +196.7% |
| **H4** | 84 | 29 | -55 | -65.5% |
| **W** | 39 | 19 | -20 | -51.3% |
| **VS** | 5 | 2 | -3 | -60.0% |

---

## Low Symbol Clusters (3+ consecutive lows)

### FR0.csv Clusters


| Reel | Cluster Lengths |
|------|-----------------|
| **Reel 1** | 10, 9, 6, 5, 40, 9, 22, 12, 12, 3 |
| **Reel 2** | 25, 5, 3, 9, 32, 5, 17, 17, 3 |
| **Reel 3** | 4, 30, 22, 11, 3, 18, 21, 18, 5 |
| **Reel 4** | 8, 13, 4, 6, 11, 14, 16, 3, 4, 22, 10, 3 |
| **Reel 5** | 30, 6, 6, 3, 12, 35, 12 |

**Total clusters in FR0**: 47

### FR1.csv Clusters

| Reel | Cluster Lengths |
|------|-----------------|
| **Reel 1** | 17, 55, 10, 18, 6, 32 |
| **Reel 2** | 3, 25, 34, 5, 18, 22 |
| **Reel 3** | 13, 5, 18, 15, 10, 4, 16, 50, 5 |
| **Reel 4** | 16, 12, 30, 5, 6, 25, 17 |
| **Reel 5** | 42, 13, 51, 13 |

**Total clusters in FR1**: 32


---

## Analysis & Observations

### 1. Premium-to-Low Ratio

- **FR0 (Regular Bonus)**: 0.611 (1 premium per 1.64 lows)
- **FR1 (Superbonus)**: 0.598 (1 premium per 1.67 lows)
- **Difference**: FR0 has **2.1%** higher premium-to-low ratio, but this is misleading

**Impact**: While FR0 has a slightly better premium-to-low ratio, the **distribution** of premiums is the critical issue. FR0 has balanced H1-H4 (104/85/91/84) but FR1 is heavily weighted toward H3 (270 symbols). H3 is a key high-paying symbol, and FR0's low H3 density (8.97% vs 26.60%) is a major factor in the low RTP.

### 2. VS (DRAW) Symbol Frequency

- **FR0**: 5 VS symbols (0.49%)
- **FR1**: 2 VS symbols (0.20%)
- **Difference**: FR0 has **3 more** VS symbols than FR1, but both are critically low

**Impact**: VS symbols are critical for big wins (expanding wilds with multipliers). While FR0 has more VS than FR1, 5 VS symbols (0.49%) is still far too low for a bonus feature that needs to achieve 96.2% RTP. VS frequency needs to be increased significantly (target: 20-30 symbols, ~2-3%).

### 3. Wild Symbol Frequency

- **FR0**: 39 W symbols (3.84%)
- **FR1**: 19 W symbols (1.87%)
- **Difference**: FR0 has **20 more** W symbols than FR1

**Impact**: FR0's wild frequency (3.84%) is reasonable and higher than FR1. Wilds contribute to wins and can have multipliers. This is not a critical issue, but distribution could be optimized.

### 4. Low Symbol Density

- **FR0**: 596 low symbols (58.72%)
- **FR1**: 615 low symbols (60.59%)
- **Difference**: FR0 has **19 fewer** low symbols than FR1

**Impact**: While FR0 has slightly fewer low symbols than FR1, 58.72% is still too high for a bonus feature targeting 96.2% RTP. The bigger issue is the **clustering** of low symbols - FR0 has 47 clusters of 3+ consecutive low symbols, creating dead zones that reduce win potential.

### 5. H3 Symbol (Shotgun) Frequency

- **FR0**: 91 H3 symbols (8.97%)
- **FR1**: 270 H3 symbols (26.60%)
- **Difference**: FR0 has **179 fewer** H3 symbols (only 33.7% of FR1's H3 count)

**Impact**: **This is the CRITICAL issue.** H3 is a key premium symbol with high payouts. FR0's H3 density (8.97%) is critically low compared to FR1 (26.60%). This massive difference in H3 frequency is likely the primary reason for FR0's low RTP (46.39% vs target 96.2%). H3 density needs to be increased dramatically (target: 200-240 symbols, ~20-24%).

---

## Recommendations for Improvement

Based on the analysis, the following changes are recommended to increase FR0 RTP from 46.39% to ~96.2%:

### Primary Issues Identified:

1. **H3 Density Critically Low**: FR0 has only 91 H3 symbols (8.97%) vs 270 in FR1 (26.60%). H3 is a key premium symbol.
2. **Premium Distribution Unbalanced**: FR0 has balanced H1-H4 distribution (104/85/91/84), but H3 density is too low for a bonus feature.
3. **VS Frequency Very Low**: FR0 has only 5 VS symbols (0.49%). While FR1 has even fewer (2), both are low. VS symbols are critical for big wins.
4. **Low Symbol Clusters**: FR0 has 47 clusters of 3+ consecutive low symbols, creating dead zones that reduce win potential.
5. **Wild Density**: FR0 has 39 W symbols (3.84%) which is reasonable, but could potentially be optimized.

### Suggested Initial Direction:

#### 1. Dramatically Increase H3 Symbol Density (CRITICAL)
- **Current**: 91 H3 symbols (8.97%)
- **Target**: Increase H3 by **120-150 symbols** (from 91 to ~211-241, approximately 130-165% increase)
- **Rationale**: H3 is the highest-paying premium symbol in FR1 (26.60%). While we don't need to match FR1 exactly, FR0 needs significantly more H3 for proper RTP.
- **Action**: Replace low symbols (primarily L1, L2, L3) with H3 symbols
- **Impact**: This is the single most important change. H3 increases premium win frequency and average win size dramatically.

#### 2. Increase VS Symbol Density
- **Current**: 5 VS symbols (0.49%)
- **Target**: Increase by **15-25 symbols** (from 5 to ~20-30, approximately 300-400% increase)
- **Rationale**: VS symbols provide expanding wilds with multipliers. Even a small increase in VS frequency significantly boosts big win potential.
- **Action**: Replace low symbols with VS symbols, distribute evenly across reels
- **Impact**: VS symbols are critical for big wins (500×+). Increasing frequency from 0.49% to ~2-3% should significantly improve RTP.

#### 3. Increase H2 and H4 Density Moderately
- **Current H2**: 85 symbols (8.37%)
- **Target**: Increase H2 by **30-50 symbols** (from 85 to ~115-135, approximately 35-60% increase)
- **Current H4**: 84 symbols (8.28%)
- **Target**: Increase H4 by **20-40 symbols** (from 84 to ~104-124, approximately 24-48% increase)
- **Action**: Replace low symbols (L1-L3) with H2 and H4
- **Impact**: Balanced premium distribution improves overall win potential

#### 4. Reduce Low Symbol Density (especially L1-L3)
- **Current**: 596 low symbols (58.72%)
  - L1: 133, L2: 103, L3: 121, L4: 123, L5: 116
- **Target**: Reduce by **170-240 symbols total** (from 596 to ~356-426, focus on L1-L3)
  - Reduce L1 by 50-70 symbols
  - Reduce L2 by 40-60 symbols
  - Reduce L3 by 50-70 symbols
  - Keep L4 and L5 relatively stable
- **Action**: Replace with H3, H2, H4, and VS symbols
- **Impact**: Reduces low-paying win frequency, increases average win size

#### 5. Break Up Low Symbol Clusters
- **Current**: 47 clusters of 3+ consecutive low symbols
- **Target**: Reduce clusters significantly by inserting premium/VS symbols into cluster zones
- **Action**: Identify clusters (especially long ones like 30+ consecutive lows) and replace some symbols with premiums/VS
- **Impact**: Eliminates dead zones that create strings of low-paying spins

#### 6. Maintain or Slightly Optimize Wild Density
- **Current**: 39 W symbols (3.84%)
- **Target**: Maintain at 35-45 symbols (3.5-4.5%)
- **Action**: Optimize distribution if needed, but maintain current level
- **Impact**: Wilds contribute to wins and can have multipliers

### Summary of Recommended Changes:

1. **Increase H3 by 120-150 symbols** (CRITICAL - from 91 to ~211-241, ~130-165% increase)
2. **Increase VS by 15-25 symbols** (from 5 to ~20-30, ~300-400% increase)
3. **Increase H2 by 30-50 symbols** (from 85 to ~115-135, ~35-60% increase)
4. **Increase H4 by 20-40 symbols** (from 84 to ~104-124, ~24-48% increase)
5. **Reduce L1-L3 by ~140-200 symbols total** (primarily to make room for H3, H2, H4, VS)
6. **Break up low symbol clusters** (target the 47 existing clusters)

**Expected Net Change**: 
- Remove ~170-240 low symbols (L1-L3)
- Add ~120-150 H3 symbols
- Add ~30-50 H2 symbols
- Add ~20-40 H4 symbols
- Add ~15-25 VS symbols
- Net: ~+15-25 symbols total (may need to adjust to maintain reel length)

**Expected Impact**: 
- Premium density increases from 35.86% to ~45-50%
- H3 density increases from 8.97% to ~20-24%
- VS density increases from 0.49% to ~2-3%
- Low density decreases from 58.72% to ~42-50%
- These changes should move RTP from 46.39% toward the 96.2% target

---

**Analysis Date**: 2025-11-08 01:38:10
