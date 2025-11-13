from copy import deepcopy
from typing import Dict, List, Optional

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import (
    enter_bonus_event,
    exit_bonus_event,
    fs_trigger_event,
    sticky_wild_reset_event,
    sticky_wild_update_event,
    symbol_removal_event,
)


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        self.config.reels = deepcopy(self.config.base_reels)
        self.current_bonus_mode: Optional[str] = None
        self.bonus_reel_id: Optional[str] = None
        self.removal_queue: List[str] = []
        self.removed_symbols: List[str] = []
        self.sticky_wilds: Dict[tuple, int] = {}
        self.retrigger_count = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "wild": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol based on current gametype."""
        multiplier_value = 1
        try:
            mult_lookup = self.get_current_distribution_conditions().get("mult_values", {})
            if self.gametype in mult_lookup and mult_lookup[self.gametype]:
                multiplier_value = get_random_outcome(mult_lookup[self.gametype])
        except Exception:
            multiplier_value = 1
        symbol.assign_attribute({"multiplier": multiplier_value})

    def determine_bonus_mode(self, scatter_count: int) -> str:
        forced_mode = self.get_current_distribution_conditions().get("bonus_mode")
        if forced_mode:
            return forced_mode
        return "hyperdrive" if scatter_count >= 4 else "rocket"

    def resolve_bonus_reel_id(self) -> Optional[str]:
        reel_weights = self.get_current_distribution_conditions().get("reel_weights", {})
        freegame_weights = reel_weights.get(self.config.freegame_type, {})
        if freegame_weights:
            return next(iter(freegame_weights.keys()))
        return None

    def prepare_bonus_mode(self, mode: str) -> None:
        self.current_bonus_mode = mode
        self.bonus_reel_id = self.resolve_bonus_reel_id()
        self.removed_symbols = []
        self.removal_queue = (
            list(self.config.symbol_removal_order_super)
            if mode == "hyperdrive"
            else list(self.config.symbol_removal_order_regular)
        )
        self.sticky_wilds = {}
        self.retrigger_count = 0
        if mode == "hyperdrive":
            self._initialize_hyperdrive_removal()

    def _initialize_hyperdrive_removal(self) -> None:
        initial_symbols = ["s10", "sj", "sq", "sk", "sa"]
        for sym in initial_symbols:
            self.remove_symbol_from_bonus_reels(sym)
            self.removed_symbols.append(sym)
            if sym in self.removal_queue:
                self.removal_queue.remove(sym)
        if initial_symbols:
            self.broadcast_symbol_removal(initial=True)

    def reset_bonus_state(self) -> None:
        if self.current_bonus_mode is not None:
            exit_bonus_event(self)
        self.current_bonus_mode = None
        self.bonus_reel_id = None
        self.removal_queue = []
        self.removed_symbols = []
        self.sticky_wilds = {}
        self.retrigger_count = 0
        sticky_wild_reset_event(self)

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        if self.gametype == self.config.basegame_type:
            trigger_map = self.config.freespin_triggers[self.gametype]
            if not trigger_map:
                return False
            return (
                self.count_special_symbols(scatter_key) >= min(trigger_map.keys())
                and not self.repeat
            )
        if self.gametype == self.config.freegame_type and self.current_bonus_mode:
            return self._has_edge_scatters(scatter_key)
        return False

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        scatter_count = self.count_special_symbols(scatter_key)
        mode = self.determine_bonus_mode(scatter_count)
        self.prepare_bonus_mode(mode)
        self.tot_fs = 10
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        sticky_wild_reset_event(self)
        enter_bonus_event(self, mode)
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        self.tot_fs += 2
        self.retrigger_count += 1
        self.handle_symbol_removal_progress()
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def handle_symbol_removal_progress(self) -> None:
        if not self.current_bonus_mode or not self.removal_queue:
            return
        next_symbol = self.removal_queue.pop(0)
        self.remove_symbol_from_bonus_reels(next_symbol)
        self.removed_symbols.append(next_symbol)
        self.broadcast_symbol_removal()

    def remove_symbol_from_bonus_reels(self, symbol_name: str) -> None:
        if not self.bonus_reel_id:
            return
        reel_ids = {self.bonus_reel_id}
        if "WCAP" in self.config.reels:
            reel_ids.add("WCAP")
        for reel_id in reel_ids:
            if reel_id not in self.config.reels:
                continue
            updated_reels: List[List[str]] = []
            for reel in self.config.reels[reel_id]:
                filtered = [sym for sym in reel if sym != symbol_name]
                updated_reels.append(filtered if filtered else reel[:])
            self.config.reels[reel_id] = updated_reels

    def restore_sticky_wilds_on_board(self) -> None:
        if (
            self.gametype != self.config.freegame_type
            or not self.current_bonus_mode
            or not self.sticky_wilds
        ):
            return
        for (reel, row), multiplier in self.sticky_wilds.items():
            if reel >= self.config.num_reels or row >= self.config.num_rows[reel]:
                continue
            wild_symbol = self.symbol_storage.create_symbol_state("wild")
            wild_symbol.assign_attribute({"multiplier": multiplier, "sticky": True})
            self.board[reel][row] = wild_symbol
        self.get_special_symbols_on_board()

    def capture_sticky_wilds_from_board(self) -> None:
        if self.gametype != self.config.freegame_type or not self.current_bonus_mode:
            return
        wild_positions = self.special_syms_on_board.get("wild", [])
        if not wild_positions:
            return
        for pos in wild_positions:
            reel = pos["reel"]
            row = pos["row"]
            if reel not in (1, 2, 3):  # 0-indexed reels 2-4
                continue
            multiplier = 1
            symbol = self.board[reel][row]
            if symbol.check_attribute("multiplier"):
                multiplier = symbol.get_attribute("multiplier")
            self.sticky_wilds[(reel, row)] = multiplier
        self.broadcast_sticky_wilds()

    def broadcast_sticky_wilds(self) -> None:
        if self.sticky_wilds:
            sticky_wild_update_event(self, self.sticky_wilds)

    def broadcast_symbol_removal(self, initial: bool = False) -> None:
        if self.removed_symbols:
            symbol_removal_event(self, list(self.removed_symbols), initial=initial)

    def _has_edge_scatters(self, scatter_key: str) -> bool:
        if scatter_key not in self.special_syms_on_board:
            return False
        first_reel = 0
        last_reel = self.config.num_reels - 1
        reels_with_scatter = {pos["reel"] for pos in self.special_syms_on_board[scatter_key]}
        return first_reel in reels_with_scatter and last_reel in reels_with_scatter

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
