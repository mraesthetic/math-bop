from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import fs_trigger_event


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        """Reset game state, including VS reel multipliers."""
        super().reset_book()
        if hasattr(self, 'vs_reel_multipliers'):
            self.vs_reel_multipliers = {}
        # Reset superbonus flag at start of new base spin
        if hasattr(self, 'is_superbonus_from_scatter'):
            self.is_superbonus_from_scatter = False

    def reset_fs_spin(self):
        """Reset free spin state, including VS reel multipliers."""
        super().reset_fs_spin()
        if hasattr(self, 'vs_reel_multipliers'):
            self.vs_reel_multipliers = {}
        # Note: is_superbonus_from_scatter flag is set in run_freespin_from_base
        # and should persist through the entire free spins feature

    def assign_special_sym_function(self):
        """Map special symbols to their assignment functions."""
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            # VS multipliers are assigned in expand_vs_reels(), not here
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in freegame."""
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def run_freespin_from_base(self, scatter_key: str = "scatter") -> None:
        """Override to handle 4-scatter superbonus trigger from base game.
        
        Scatter trigger logic:
        - 3 scatters from base → regular bonus (FR0 reelset, normal VS behavior)
        - 4 scatters from base → SUPER DRAW! (FR1 reelset, guaranteed VS, superbonus multipliers)
        - Max 4 scatters can appear (5 scatters cannot occur)
        
        Feature buy protection:
        - Regular bonus buy (betmode="bonus"): Always stays in regular bonus mode, even if 4 scatters land
        - Superbonus buy (betmode="superbonus"): Always uses superbonus mode
        - Natural trigger from base (betmode="base"): Can trigger either regular bonus (3 scatters) or superbonus (4 scatters)
        """
        scatter_count = self.count_special_symbols(scatter_key)
        
        # Check if this is a regular bonus buy - if so, never switch to superbonus
        is_regular_bonus_buy = (hasattr(self, 'betmode') and self.betmode == "bonus")
        
        # Check if 4 scatters triggered (should enter superbonus mode)
        # BUT: Only if NOT a regular bonus buy (regular bonus buy must stay in regular bonus mode)
        if (scatter_count == 4 and 
            self.gametype == self.config.basegame_type and 
            not is_regular_bonus_buy):
            # 4 scatters from base (not from regular bonus buy) = SUPER DRAW! (superbonus)
            # Switch to FR1 reelset and enable superbonus behavior
            self.is_superbonus_from_scatter = True
            # Switch freegame reelset to FR1 for superbonus
            self.config.padding_reels[self.config.freegame_type] = self.config.reels["FR1"]
        elif scatter_count == 3 and self.gametype == self.config.basegame_type:
            # 3 scatters = regular bonus (always, even if it was a bonus buy)
            self.is_superbonus_from_scatter = False
            # Ensure regular bonus uses FR0 reelset
            self.config.padding_reels[self.config.freegame_type] = self.config.reels["FR0"]
        elif is_regular_bonus_buy:
            # Regular bonus buy with any scatter count (including 4) → always regular bonus
            # This ensures buying regular bonus can never accidentally trigger superbonus
            self.is_superbonus_from_scatter = False
            self.config.padding_reels[self.config.freegame_type] = self.config.reels["FR0"]
        else:
            # Other cases (shouldn't happen from base, but handle gracefully)
            self.is_superbonus_from_scatter = False
            self.config.padding_reels[self.config.freegame_type] = self.config.reels["FR0"]
        
        # Record the trigger
        self.record(
            {
                "kind": scatter_count,
                "symbol": scatter_key,
                "gametype": self.gametype,
            }
        )
        
        # Update free spin amount (will use the correct trigger logic)
        self.update_freespin_amount(scatter_key)
        
        # Start free spins
        self.run_freespin()
    
    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Override to ensure superbonus always gives exactly 10 spins."""
        # Check if in superbonus mode (either from feature buy or 4-scatter trigger)
        is_superbonus = (
            (hasattr(self, 'betmode') and self.betmode == "superbonus") or
            (hasattr(self, 'is_superbonus_from_scatter') and self.is_superbonus_from_scatter)
        )
        
        if is_superbonus:
            # SUPER DRAW! always awards exactly 10 free spins
            # Since superbonus starts from basegame, use basegame_trigger=True
            # to emit freeSpinTrigger event (not freeSpinRetrigger)
            self.tot_fs = 10
            fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
        else:
            # Use default behavior for other modes
            super().update_freespin_amount(scatter_key)

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return
