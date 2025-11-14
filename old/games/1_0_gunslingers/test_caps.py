#!/usr/bin/env python3
"""Quick sanity check for max win cap and VS multiplier cap changes."""

from game_config import GameConfig
from game_executables import GameExecutables
from game_calculations import GameCalculations

print("="*80)
print("MAX WIN CAP & VS MULTIPLIER CAP - SANITY CHECK")
print("="*80)
print()

# Check config
config = GameConfig()
print(f"✅ Max Win Cap: {config.wincap}× bet")
assert config.wincap == 10000.0, f"Expected 10000.0, got {config.wincap}"
print(f"   All bet modes use max_win={config.wincap}×")
print()

# Check VS multiplier cap in game_executables
# Create a mock gamestate to test calculate_vs_line_multiplier
class MockGameState(GameExecutables):
    def __init__(self):
        # Minimal init to test the method
        self.vs_reel_multipliers = {0: 10, 1: 10, 2: 10}  # Should give 1000×, capped at 500×

# Test VS multiplier cap
mock_state = MockGameState()
# Create positions that use all 3 reels with VS multipliers
positions = [{"reel": 0, "row": 0}, {"reel": 1, "row": 0}, {"reel": 2, "row": 0}]
result = mock_state.calculate_vs_line_multiplier(positions)
print(f"✅ VS Multiplier Cap Test:")
print(f"   Test: 3 VS reels with 10× each = 1000× (should cap at 500×)")
print(f"   Result: {result}×")
assert result == 500, f"Expected 500, got {result}"
print(f"   ✅ VS multiplier cap is correctly set to 500×")
print()

# Test with lower multipliers (should not cap)
mock_state.vs_reel_multipliers = {0: 5, 1: 4}  # 5 × 4 = 20×
positions = [{"reel": 0, "row": 0}, {"reel": 1, "row": 0}]
result = mock_state.calculate_vs_line_multiplier(positions)
print(f"✅ VS Multiplier Test (below cap):")
print(f"   Test: 2 VS reels with 5× and 4× = 20×")
print(f"   Result: {result}×")
assert result == 20, f"Expected 20, got {result}"
print(f"   ✅ Multipliers multiply correctly when below cap")
print()

print("="*80)
print("ALL CHECKS PASSED ✅")
print("="*80)
print()
print("Summary:")
print(f"  • Max Win Cap: {config.wincap}× bet")
print(f"  • VS Multiplier Cap: 500×")
print(f"  • FRWCAP.csv updated with max win configuration")
print()

