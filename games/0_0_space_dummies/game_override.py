import random
from copy import deepcopy
from typing import Optional

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import fs_trigger_event, reveal_event


class GameStateOverride(GameExecutables):
    """
    Extend the base gamestate with Space Dummies-specific overrides:
    - Wild multipliers in all modes
    - Sticky wild tracking during bonuses
    - Dual bonus modes with symbol removal handling
    """

    def reset_book(self):
        super().reset_book()
        self.pending_bonus_mode = None
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "wild": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in all modes."""
        multiplier_value = 1
        mult_config = self.get_current_distribution_conditions().get("mult_values", {})
        if self.gametype in mult_config:
            multiplier_value = get_random_outcome(mult_config[self.gametype])
        symbol.assign_attribute({"multiplier": multiplier_value})

    # --- Bonus session helpers -------------------------------------------------

    def initialize_bonus_session(self):
        """Create local reel copies, removal state, and sticky storage."""
        if self.pending_bonus_mode is None:
            raise RuntimeError("Bonus mode not set before initializing free spins.")
        self.active_bonus_mode = self.pending_bonus_mode
        self.pending_bonus_mode = None
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.config.freegame_type]
        self.bonus_reel_maps = {
            reel_id: deepcopy(self.config.reels[reel_id]) for reel_id in freegame_reel_weights.keys()
        }

        if self.active_bonus_mode == "hyper":
            for symbol_name in self.config.symbol_ids["low"]:
                self._remove_symbol_from_bonus_reels(symbol_name)
            self.next_symbol_removal_index = len(self.config.symbol_ids["low"])

    def clear_bonus_session(self):
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0

    def _remove_symbol_from_bonus_reels(self, symbol_name: str) -> bool:
        """Remove a symbol from all bonus reel copies; returns True if anything changed."""
        removed_any = False
        for reel_id in self.bonus_reel_maps:
            for reel_index, reel_strip in enumerate(self.bonus_reel_maps[reel_id]):
                filtered_strip = [sym for sym in reel_strip if sym != symbol_name]
                if len(filtered_strip) != len(reel_strip):
                    removed_any = True
                    self.bonus_reel_maps[reel_id][reel_index] = filtered_strip
                if len(self.bonus_reel_maps[reel_id][reel_index]) == 0:
                    raise RuntimeError(f"Symbol removal '{symbol_name}' exhausted reel {reel_index} in {reel_id}.")
        if removed_any:
            self.removed_symbols.add(symbol_name)
        return removed_any

    def remove_next_symbol_in_queue(self) -> Optional[str]:
        """Remove the next symbol in the configured hierarchy."""
        if self.next_symbol_removal_index >= len(self.config.symbol_removal_order):
            return None
        target_symbol = self.config.symbol_removal_order[self.next_symbol_removal_index]
        self.next_symbol_removal_index += 1
        if target_symbol in self.removed_symbols:
            return target_symbol
        removed = self._remove_symbol_from_bonus_reels(target_symbol)
        if removed:
            return target_symbol
        return target_symbol

    def draw_bonus_board(self, emit_event: bool = True):
        """Create a board using the mutable bonus reelstrips."""
        if not self.bonus_reel_maps:
            raise RuntimeError("Bonus reel strips not initialized.")

        freegame_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.gametype]
        reelstrip_id = get_random_outcome(freegame_reel_weights)
        reelstrip = self.bonus_reel_maps[reelstrip_id]

        self.refresh_special_syms()
        anticipation = [0] * self.config.num_reels
        board = [[]] * self.config.num_reels
        if self.config.include_padding:
            top_symbols = []
            bottom_symbols = []
        reel_positions = [0] * self.config.num_reels
        padding_positions = [0] * self.config.num_reels
        first_scatter_reel = -1

        for reel in range(self.config.num_reels):
            if len(reelstrip[reel]) == 0:
                raise RuntimeError(f"Reel {reel} for strip {reelstrip_id} is empty after symbol removal.")
            board[reel] = [None] * self.config.num_rows[reel]
            reel_pos = random.randrange(0, len(reelstrip[reel]))
            reel_positions[reel] = reel_pos
            if self.config.include_padding:
                top_symbols.append(self.create_symbol(reelstrip[reel][(reel_pos - 1) % len(reelstrip[reel])]))
                bottom_symbols.append(
                    self.create_symbol(reelstrip[reel][(reel_pos + len(board[reel])) % len(reelstrip[reel])])
                )
            for row in range(self.config.num_rows[reel]):
                sym_id = reelstrip[reel][(reel_pos + row) % len(reelstrip[reel])]
                symbol = self.create_symbol(sym_id)
                board[reel][row] = symbol
                if symbol.special:
                    for special_symbol in self.special_syms_on_board:
                        for s in self.config.special_symbols[special_symbol]:
                            if symbol.name == s:
                                self.special_syms_on_board[special_symbol].append({"reel": reel, "row": row})
                                if (
                                    symbol.check_attribute("scatter")
                                    and len(self.special_syms_on_board[special_symbol])
                                    >= self.config.anticipation_triggers[self.gametype]
                                    and first_scatter_reel == -1
                                ):
                                    first_scatter_reel = reel + 1
            padding_positions[reel] = (reel_positions[reel] + len(board[reel]) + 1) % len(reelstrip[reel])

        if first_scatter_reel > -1 and first_scatter_reel != self.config.num_reels:
            count = 1
            for reel in range(first_scatter_reel, self.config.num_reels):
                anticipation[reel] = count
                count += 1

        self.board = board
        self.reel_positions = reel_positions
        self.padding_position = padding_positions
        self.anticipation = anticipation
        self.reelstrip_id = reelstrip_id
        self.reelstrip = reelstrip
        if self.config.include_padding:
            self.top_symbols = top_symbols
            self.bottom_symbols = bottom_symbols

        if emit_event:
            reveal_event(self)

    def apply_existing_sticky_wilds(self):
        """Overlay previously stored sticky wilds onto the active board."""
        if not self.sticky_wild_positions:
            self.get_special_symbols_on_board()
            return

        for (reel, row), multiplier in self.sticky_wild_positions.items():
            sticky_symbol = self.create_symbol("wild")
            sticky_symbol.assign_attribute({"multiplier": multiplier})
            self.board[reel][row] = sticky_symbol
        self.get_special_symbols_on_board()

    def capture_new_sticky_wilds(self) -> list:
        """Record any new wilds that landed this spin so they persist."""
        new_wilds = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                symbol = self.board[reel][row]
                if symbol.name != "wild":
                    continue
                key = (reel, row)
                if key in self.sticky_wild_positions:
                    continue
                multiplier = symbol.get_attribute("multiplier") if symbol.check_attribute("multiplier") else 1
                self.sticky_wild_positions[key] = multiplier
                new_wilds.append({"reel": reel, "row": row, "multiplier": multiplier})
        return new_wilds

    def process_edge_scatter_removal(self) -> Optional[str]:
        """Check for Scatter on reels 1 and 5, award spins and remove symbols if needed."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        has_left = any(pos["reel"] == 0 for pos in scatter_positions)
        has_right = any(pos["reel"] == self.config.num_reels - 1 for pos in scatter_positions)
        if not (has_left and has_right):
            return None

        # +2 free spins per spec
        self.tot_fs += 2
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
        return self.remove_next_symbol_in_queue()

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
