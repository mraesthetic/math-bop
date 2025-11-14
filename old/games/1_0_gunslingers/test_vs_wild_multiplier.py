#!/usr/bin/env python3
"""Test script to verify VS vs Wild multiplier logic.

Tests the scenario where VS expands a reel that already has wilds with multipliers.
Verifies that VS multiplier only replaces wild multipliers if VS multiplier is higher.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from game_config import GameConfig
from game_executables import GameExecutables
from src.calculations.symbol import Symbol


class MockGameState(GameExecutables):
    """Mock game state for testing VS vs Wild multiplier logic."""
    
    def __init__(self):
        self.config = GameConfig()
        self.board = []
        self.vs_reel_multipliers = {}
        self.vs_reel_multipliers_applied = {}
        
    def create_symbol(self, name: str):
        """Create a symbol object."""
        return Symbol(self.config, name)


def test_vs_higher_than_wild():
    """Test: VS multiplier is higher than existing wild multiplier -> should use VS multiplier."""
    print("="*80)
    print("TEST 1: VS Multiplier (10×) > Wild Multiplier (5×)")
    print("="*80)
    
    gamestate = MockGameState()
    
    # Create a board with:
    # Reel 0: W (5×), W (5×), VS
    # This simulates a reel with existing wilds that gets VS
    gamestate.board = [
        [
            Symbol(gamestate.config, "W"),  # Row 0: Wild with 5× multiplier
            Symbol(gamestate.config, "W"),  # Row 1: Wild with 5× multiplier
            Symbol(gamestate.config, "VS")  # Row 2: VS symbol
        ]
    ]
    
    # Set multipliers on existing wilds
    gamestate.board[0][0].assign_attribute({"multiplier": 5})  # Wild with 5×
    gamestate.board[0][1].assign_attribute({"multiplier": 5})  # Wild with 5×
    
    # Set VS multiplier (higher than wild)
    gamestate.vs_reel_multipliers = {0: 10}  # VS has 10× multiplier
    
    print("\nBefore expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (VS)")
    print(f"  VS multiplier: {gamestate.vs_reel_multipliers[0]}×")
    
    # Expand VS reels
    gamestate.expand_vs_reels()
    
    print("\nAfter expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (mult: {gamestate.board[0][2].get_attribute('multiplier') if gamestate.board[0][2].check_attribute('multiplier') else 'none'})")
    print(f"  VS multiplier applied: {gamestate.vs_reel_multipliers_applied.get(0, False)}")
    
    # Verify results
    all_use_vs_mult = True
    for row_idx in range(3):
        if not gamestate.board[0][row_idx].check_attribute("multiplier"):
            all_use_vs_mult = False
            break
        if gamestate.board[0][row_idx].get_attribute("multiplier") != 10:
            all_use_vs_mult = False
            break
    
    vs_applied = gamestate.vs_reel_multipliers_applied.get(0, False)
    
    if all_use_vs_mult and vs_applied:
        print("\n✅ PASS: All positions use VS multiplier (10×), VS multiplier is applied multiplicatively")
        return True
    else:
        print("\n❌ FAIL: Expected all positions to use VS multiplier (10×)")
        if not all_use_vs_mult:
            print("   Issue: Not all positions have VS multiplier")
        if not vs_applied:
            print("   Issue: VS multiplier not marked as applied")
        return False


def test_vs_lower_than_wild():
    """Test: VS multiplier is lower than existing wild multiplier -> should keep wild multiplier."""
    print("\n" + "="*80)
    print("TEST 2: VS Multiplier (3×) < Wild Multiplier (10×)")
    print("="*80)
    
    gamestate = MockGameState()
    
    # Create a board with:
    # Reel 0: W (10×), W (10×), VS
    # This simulates a reel with existing wilds that gets VS with lower multiplier
    gamestate.board = [
        [
            Symbol(gamestate.config, "W"),  # Row 0: Wild with 10× multiplier
            Symbol(gamestate.config, "W"),  # Row 1: Wild with 10× multiplier
            Symbol(gamestate.config, "VS")  # Row 2: VS symbol
        ]
    ]
    
    # Set multipliers on existing wilds (higher than VS)
    gamestate.board[0][0].assign_attribute({"multiplier": 10})  # Wild with 10×
    gamestate.board[0][1].assign_attribute({"multiplier": 10})  # Wild with 10×
    
    # Set VS multiplier (lower than wild)
    gamestate.vs_reel_multipliers = {0: 3}  # VS has 3× multiplier
    
    print("\nBefore expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (VS)")
    print(f"  VS multiplier: {gamestate.vs_reel_multipliers[0]}×")
    
    # Expand VS reels
    gamestate.expand_vs_reels()
    
    print("\nAfter expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (mult: {gamestate.board[0][2].get_attribute('multiplier') if gamestate.board[0][2].check_attribute('multiplier') else 'none'})")
    print(f"  VS multiplier applied: {gamestate.vs_reel_multipliers_applied.get(0, False)}")
    
    # Verify results
    # Existing wilds should keep their 10× multiplier
    # VS position should get 3× (since it wasn't a wild before)
    row0_keeps_wild = (gamestate.board[0][0].name == "W" and 
                      gamestate.board[0][0].check_attribute("multiplier") and
                      gamestate.board[0][0].get_attribute("multiplier") == 10)
    row1_keeps_wild = (gamestate.board[0][1].name == "W" and 
                      gamestate.board[0][1].check_attribute("multiplier") and
                      gamestate.board[0][1].get_attribute("multiplier") == 10)
    # VS position becomes wild with VS multiplier (since it wasn't a wild before)
    row2_gets_vs = (gamestate.board[0][2].name == "W" and 
                   gamestate.board[0][2].check_attribute("multiplier") and
                   gamestate.board[0][2].get_attribute("multiplier") == 3)
    
    vs_not_applied = not gamestate.vs_reel_multipliers_applied.get(0, True)
    
    if row0_keeps_wild and row1_keeps_wild and row2_gets_vs and vs_not_applied:
        print("\n✅ PASS: Existing wilds keep their multipliers (10×), VS multiplier NOT applied multiplicatively")
        print("   Note: VS position gets VS multiplier (3×) since it wasn't a wild before expansion")
        return True
    else:
        print("\n❌ FAIL: Expected existing wilds to keep their multipliers")
        if not row0_keeps_wild:
            print(f"   Issue: Row 0 should be W with 10×, got {gamestate.board[0][0].name} with {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'}")
        if not row1_keeps_wild:
            print(f"   Issue: Row 1 should be W with 10×, got {gamestate.board[0][1].name} with {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'}")
        if not row2_gets_vs:
            print(f"   Issue: Row 2 should be W with 3×, got {gamestate.board[0][2].name} with {gamestate.board[0][2].get_attribute('multiplier') if gamestate.board[0][2].check_attribute('multiplier') else 'none'}")
        if not vs_not_applied:
            print("   Issue: VS multiplier should NOT be applied multiplicatively")
        return False


def test_vs_equal_to_wild():
    """Test: VS multiplier equals existing wild multiplier -> should keep wild multiplier."""
    print("\n" + "="*80)
    print("TEST 3: VS Multiplier (5×) == Wild Multiplier (5×)")
    print("="*80)
    
    gamestate = MockGameState()
    
    # Create a board with:
    # Reel 0: W (5×), W (5×), VS
    gamestate.board = [
        [
            Symbol(gamestate.config, "W"),  # Row 0: Wild with 5× multiplier
            Symbol(gamestate.config, "W"),  # Row 1: Wild with 5× multiplier
            Symbol(gamestate.config, "VS")  # Row 2: VS symbol
        ]
    ]
    
    # Set multipliers on existing wilds
    gamestate.board[0][0].assign_attribute({"multiplier": 5})  # Wild with 5×
    gamestate.board[0][1].assign_attribute({"multiplier": 5})  # Wild with 5×
    
    # Set VS multiplier (equal to wild)
    gamestate.vs_reel_multipliers = {0: 5}  # VS has 5× multiplier (equal)
    
    print("\nBefore expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (VS)")
    print(f"  VS multiplier: {gamestate.vs_reel_multipliers[0]}×")
    
    # Expand VS reels
    gamestate.expand_vs_reels()
    
    print("\nAfter expansion:")
    print(f"  Reel 0, Row 0: {gamestate.board[0][0].name} (mult: {gamestate.board[0][0].get_attribute('multiplier') if gamestate.board[0][0].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 1: {gamestate.board[0][1].name} (mult: {gamestate.board[0][1].get_attribute('multiplier') if gamestate.board[0][1].check_attribute('multiplier') else 'none'})")
    print(f"  Reel 0, Row 2: {gamestate.board[0][2].name} (mult: {gamestate.board[0][2].get_attribute('multiplier') if gamestate.board[0][2].check_attribute('multiplier') else 'none'})")
    print(f"  VS multiplier applied: {gamestate.vs_reel_multipliers_applied.get(0, False)}")
    
    # Verify results
    # Existing wilds should keep their 5× multiplier (VS is not higher)
    row0_keeps_wild = (gamestate.board[0][0].name == "W" and 
                      gamestate.board[0][0].check_attribute("multiplier") and
                      gamestate.board[0][0].get_attribute("multiplier") == 5)
    row1_keeps_wild = (gamestate.board[0][1].name == "W" and 
                      gamestate.board[0][1].check_attribute("multiplier") and
                      gamestate.board[0][1].get_attribute("multiplier") == 5)
    # VS position gets 5× (since it wasn't a wild before)
    row2_gets_vs = (gamestate.board[0][2].name == "W" and 
                   gamestate.board[0][2].check_attribute("multiplier") and
                   gamestate.board[0][2].get_attribute("multiplier") == 5)
    
    vs_not_applied = not gamestate.vs_reel_multipliers_applied.get(0, True)
    
    if row0_keeps_wild and row1_keeps_wild and row2_gets_vs and vs_not_applied:
        print("\n✅ PASS: Existing wilds keep their multipliers (5×), VS multiplier NOT applied multiplicatively")
        print("   (VS multiplier equals wild multiplier, so wild multiplier is preserved)")
        return True
    else:
        print("\n❌ FAIL: Expected existing wilds to keep their multipliers")
        return False


def test_calculate_vs_line_multiplier():
    """Test that calculate_vs_line_multiplier respects vs_reel_multipliers_applied."""
    print("\n" + "="*80)
    print("TEST 4: calculate_vs_line_multiplier respects vs_reel_multipliers_applied")
    print("="*80)
    
    gamestate = MockGameState()
    
    # Test case 1: VS multiplier was applied (higher than wild)
    gamestate.vs_reel_multipliers = {0: 10, 1: 5}
    gamestate.vs_reel_multipliers_applied = {0: True, 1: True}  # Both applied
    
    positions = [
        {"reel": 0, "row": 0},
        {"reel": 1, "row": 0},
        {"reel": 2, "row": 0}
    ]
    
    mult = gamestate.calculate_vs_line_multiplier(positions)
    expected = 10 * 5  # Both VS multipliers applied
    print(f"\nTest 4a: Both VS multipliers applied")
    print(f"  VS multipliers: Reel 0 = {gamestate.vs_reel_multipliers[0]}×, Reel 1 = {gamestate.vs_reel_multipliers[1]}×")
    print(f"  Applied: Reel 0 = {gamestate.vs_reel_multipliers_applied[0]}, Reel 1 = {gamestate.vs_reel_multipliers_applied[1]}")
    print(f"  Result: {mult}× (expected: {expected}×)")
    
    if mult == expected:
        print("  ✅ PASS")
        test4a = True
    else:
        print("  ❌ FAIL")
        test4a = False
    
    # Test case 2: VS multiplier was NOT applied (lower than wild)
    gamestate.vs_reel_multipliers = {0: 3, 1: 5}
    gamestate.vs_reel_multipliers_applied = {0: False, 1: True}  # Only reel 1 applied
    
    positions = [
        {"reel": 0, "row": 0},
        {"reel": 1, "row": 0},
        {"reel": 2, "row": 0}
    ]
    
    mult = gamestate.calculate_vs_line_multiplier(positions)
    expected = 5  # Only reel 1's VS multiplier applied (reel 0 was not applied)
    print(f"\nTest 4b: Only one VS multiplier applied (reel 0 not applied)")
    print(f"  VS multipliers: Reel 0 = {gamestate.vs_reel_multipliers[0]}×, Reel 1 = {gamestate.vs_reel_multipliers[1]}×")
    print(f"  Applied: Reel 0 = {gamestate.vs_reel_multipliers_applied[0]}, Reel 1 = {gamestate.vs_reel_multipliers_applied[1]}")
    print(f"  Result: {mult}× (expected: {expected}×)")
    
    if mult == expected:
        print("  ✅ PASS")
        test4b = True
    else:
        print("  ❌ FAIL")
        test4b = False
    
    return test4a and test4b


if __name__ == "__main__":
    print("="*80)
    print("VS vs WILD MULTIPLIER LOGIC TEST")
    print("="*80)
    print("\nTesting: VS multiplier only replaces wild multiplier if VS multiplier is HIGHER")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(test_vs_higher_than_wild())
    results.append(test_vs_lower_than_wild())
    results.append(test_vs_equal_to_wild())
    results.append(test_calculate_vs_line_multiplier())
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)








