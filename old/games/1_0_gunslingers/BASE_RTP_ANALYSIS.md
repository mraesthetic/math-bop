# BASE Bet Mode RTP Analysis

**Game**: Gunslingers: DRAW!  
**Bet Mode**: base  
**Cost**: 1.0× bet  
**Spins Analyzed**: 99,800 (wincap excluded)  
**Total Spins (including wincap)**: 99,900  
**Analysis Date**: 2025-11-08 04:27:26

---

## Overall RTP Summary

| Metric | Value |
|--------|-------|
| **Total Effective RTP** | 98.12% (0.9812) |
| **Target RTP** | 96.2% (0.9620) |
| **Difference** | +1.92% (+0.0192) |
| **Status** | ⚠️  ABOVE TARGET |

---

## RTP Decomposition

| Component | RTP Contribution | % of Total RTP | Count | Avg Win per Spin |
|-----------|-----------------|----------------|-------|------------------|
| **Basegame-Only** | 41.85% | 42.65% | 99,380 | 0.42× |
| **Regular Bonus** | 35.31% | 35.98% | 443 | 79.54× |
| **Superbonus** | 20.97% | 21.37% | 77 | 271.79× |
| **Wincap** | 1001.00% | 1020.14% | 100 | 10000.00× |
| **Total** | 98.12% | 100.00% | 99,800 | 0.98× |
| **Wincap (excluded)** | 1001.00% | (test spins) | 100 | 10,000.00× |

---

## Freegame Trigger Statistics

### Overall Freegame Hit Rate

| Metric | Value |
|--------|-------|
| **Total Freegame Triggers** | 520 |
| **Freegame Hit Rate** | 0.52% |
| **Expected** | ~10% (from config) |

### Scatter Trigger Split

| Trigger Type | Count | % of Freegames | % of Total Spins |
|--------------|-------|----------------|------------------|
| **3 Scatters (Regular Bonus)** | 443 | 85.19% | 0.44% |
| **4 Scatters (Superbonus)** | 77 | 14.81% | 0.08% |

### Superbonus Frequency

| Metric | Value |
|--------|-------|
| **Superbonus Triggers** | 77 |
| **Superbonus Rate** | 0.0772% |
| **Spins per Superbonus** | 1 in 1296 |
| **Expected Range** | 1 in 400-1000 spins (0.1-0.25%) |

---

## Average Freegame Values (from Base)

### Regular Bonus (3 Scatters)

| Metric | Value |
|--------|-------|
| **Average Feature Win** | 79.54× bet |
| **Buy Cost** | 100× bet |
| **Effective RTP** | 79.54% |
| **Count** | 443 |

### Superbonus (4 Scatters)

| Metric | Value |
|--------|-------|
| **Average Feature Win** | 271.79× bet |
| **Buy Cost** | 400× bet |
| **Effective RTP** | 67.95% |
| **Count** | 77 |

---

## Basegame-Only Statistics

| Metric | Value |
|--------|-------|
| **Basegame-Only Spins** | 99,380 |
| **Zero Win Spins** | 47,380 |
| **Average Basegame Win** | 0.42× bet |
| **Basegame RTP Contribution** | 41.85% |
| **Hit Rate** | 52.32% |

---

## Interpretation

### Overall Base Bet Mode RTP

**Status**: ⚠️  ABOVE TARGET

The total effective RTP is **98.12%**, which is **1.92%** above the 96.2% target.

**Assessment**: ⚠️  **ABOVE TARGET** - RTP is 1.92% above target

### Basegame-Only vs Bonus Portions

**Basegame-Only RTP**: 41.85% (42.65% of total)  
**Regular Bonus RTP**: 35.31% (35.98% of total)  
**Superbonus RTP**: 20.97% (21.37% of total)  
**Total Bonus RTP**: 56.28% (57.35% of total)

**Assessment**: ✅ **BALANCED** - Basegame and bonus portions are appropriately balanced

### Natural Superbonus Hit Rate

**Superbonus Rate**: 0.0772% (1 in 1296 spins)  
**Expected Range**: 0.1-0.25% (1 in 400-1000 spins)

**Assessment**: ⚠️  **{'TOO RARE' if stats['superbonus_rate'] < 0.1 else 'TOO COMMON'}** - Superbonus hit rate is {'below' if stats['superbonus_rate'] < 0.1 else 'above'} expected range

---

## Recommendations


**RTP Above Target**:
- Current: 98.12%
- Target: 96.2%
- Excess: 1.92% RTP

**Suggested Actions**:
1. Reduce basegame paytable values slightly
2. Reduce regular bonus contribution
3. Adjust freegame trigger rate if needed

**Superbonus Too Rare**:
- Current: 0.0772% (1 in 1296)
- Target: 0.1-0.25% (1 in 400-1000)
- **Suggestion**: Increase 4-scatter trigger rate in freegame_condition scatter_triggers


---

**Report Generated**: 2025-11-08 04:27:26
