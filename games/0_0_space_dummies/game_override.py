import os
import random
from copy import deepcopy
from typing import Optional

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import (
    fs_trigger_event,
    reveal_event,
    symbol_removal_event,
    symbol_removal_notice_event,
)


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
        self.active_reel_weights = None
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0
        self.scatter_disabled = False

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

        base_reel_weights = self.get_current_distribution_conditions()["reel_weights"][self.config.freegame_type]
        self.active_reel_weights = self._select_bonus_reel_weights(base_reel_weights)
        self.bonus_reel_maps = {
            reel_id: deepcopy(self.config.reels[reel_id]) for reel_id in self.active_reel_weights.keys()
        }

        if self.active_bonus_mode == "hyper":
            for symbol_name in self.config.symbol_ids["low"]:
                self._remove_symbol_from_bonus_reels(symbol_name)
                self.removed_symbols.add(symbol_name)
            self.next_symbol_removal_index = len(self.config.symbol_ids["low"])
            self.seed_initial_sticky_wilds(min_new=2, max_new=3)
            self._emit_symbol_removal_events(initial=True)
        elif self.active_bonus_mode == "rocket":
            self.seed_initial_sticky_wilds(min_new=0, max_new=2)

    def _select_bonus_reel_weights(self, base_weights):
        """Return the reel selection map to use for the pending bonus mode."""
        if self.active_bonus_mode == "hyper" and "WCAP" in self.config.reels:
            return {"WCAP": sum(base_weights.values()) or 1}
        if self.active_bonus_mode == "rocket" and "FR0" in self.config.reels:
            return {"FR0": sum(base_weights.values()) or 1}
        return base_weights

    def clear_bonus_session(self):
        self.active_bonus_mode = None
        self.bonus_reel_maps = {}
        self.sticky_wild_positions = {}
        self.removed_symbols = set()
        self.next_symbol_removal_index = 0
        self.active_reel_weights = None
        self.scatter_disabled = False

    def _replicate_symbols(self, strip: list[str], count: int) -> list[str]:
        """Return `count` replacement symbols sampled from the current strip."""
        if not strip:
            return []
        return [random.choice(strip) for _ in range(count)]

    def _remove_symbol_from_bonus_reels(self, symbol_name: str) -> bool:
        """Remove a symbol from all bonus reel copies; returns True if anything changed."""
        removed_any = False
        for reel_id in self.bonus_reel_maps:
            for reel_index, reel_strip in enumerate(self.bonus_reel_maps[reel_id]):
                if symbol_name not in reel_strip:
                    continue

                filtered_strip = [sym for sym in reel_strip if sym != symbol_name]
                removed_count = len(reel_strip) - len(filtered_strip)
                if removed_count == 0:
                    continue

                if len(filtered_strip) == 0:
                    raise RuntimeError(f"Symbol removal '{symbol_name}' exhausted reel {reel_index} in {reel_id}.")

                replacements = self._replicate_symbols(filtered_strip, removed_count)
                if len(replacements) < removed_count:
                    raise RuntimeError(f"Unable to backfill removed symbols for reel {reel_index} in {reel_id}.")

                new_strip = filtered_strip + replacements
                random.shuffle(new_strip)
                self.bonus_reel_maps[reel_id][reel_index] = new_strip
                removed_any = True

        if removed_any:
            self.removed_symbols.add(symbol_name)
        return removed_any

    def _purge_symbol_from_bonus_reels(self, symbol_name: str) -> None:
        """Completely remove a symbol (e.g., scatter) from all bonus reel strips."""
        for reel_id in self.bonus_reel_maps:
            for reel_index, reel_strip in enumerate(self.bonus_reel_maps[reel_id]):
                if symbol_name not in reel_strip:
                    continue
                filtered_strip = [sym for sym in reel_strip if sym != symbol_name]
                if not filtered_strip:
                    # Removing this symbol would empty the strip; instead, replace scatters with lows.
                    fallback_symbols = self.config.symbol_ids["low"] or [sym for sym in reel_strip if sym != symbol_name]
                    replacements = [random.choice(fallback_symbols) for _ in reel_strip]
                    self.bonus_reel_maps[reel_id][reel_index] = replacements
                    continue
                replacements = self._replicate_symbols(filtered_strip, len(reel_strip) - len(filtered_strip))
                new_strip = filtered_strip + replacements
                random.shuffle(new_strip)
                self.bonus_reel_maps[reel_id][reel_index] = new_strip

    def _disable_future_scatter_triggers(self) -> None:
        """Prevent additional scatter retriggers once all removals are complete."""
        if self.scatter_disabled:
            return
        self._purge_symbol_from_bonus_reels("scatter")
        self.scatter_disabled = True

    def remove_next_symbol_in_queue(self) -> Optional[str]:
        """Remove the next symbol in the configured hierarchy."""
        while self.next_symbol_removal_index < len(self.config.symbol_removal_order):
            target_symbol = self.config.symbol_removal_order[self.next_symbol_removal_index]
            self.next_symbol_removal_index += 1
            if target_symbol in self.removed_symbols:
                continue
            removed = self._remove_symbol_from_bonus_reels(target_symbol)
            if removed:
                if len(self.removed_symbols) >= len(self.config.symbol_removal_order):
                    self._disable_future_scatter_triggers()
                return target_symbol
        return None

    def draw_bonus_board(self, emit_event: bool = True):
        """Create a board using the mutable bonus reelstrips."""
        if not self.bonus_reel_maps:
            raise RuntimeError("Bonus reel strips not initialized.")

        if self.gametype == self.config.freegame_type and self.active_reel_weights:
            freegame_reel_weights = self.active_reel_weights
        else:
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

    def seed_initial_sticky_wilds(self, min_new: int, max_new: int) -> None:
        """Seed sticky wilds before the first bonus spin begins."""
        if max_new <= 0:
            return
        count = random.randint(max(min_new, 0), max_new)
        if count <= 0:
            return

        allowed_reels = range(1, self.config.num_reels - 1)
        positions = [
            (reel, row)
            for reel in allowed_reels
            for row in range(self.config.num_rows[reel])
        ]
        random.shuffle(positions)
        for reel, row in positions[:count]:
            self.sticky_wild_positions[(reel, row)] = self._get_seed_multiplier()

    def _get_seed_multiplier(self) -> int:
        dist = self.get_current_distribution_conditions().get("mult_values", {})
        weights = dist.get(self.config.freegame_type) or {2: 40, 3: 35, 5: 20, 10: 5}
        total = sum(weights.values()) or 1
        target = random.random() * total
        upto = 0
        for mult, weight in weights.items():
            upto += weight
            if upto >= target:
                return mult
        return 2

    def process_edge_scatter_removal(self) -> Optional[str]:
        """Check for Scatter on reels 1 and 5, award spins and remove symbols if needed."""
        if self.scatter_disabled:
            return None

        scatter_positions = self.special_syms_on_board.get("scatter", [])
        has_left = any(pos["reel"] == 0 for pos in scatter_positions)
        has_right = any(pos["reel"] == self.config.num_reels - 1 for pos in scatter_positions)
        if not (has_left and has_right):
            return None

        removed_symbol = self.remove_next_symbol_in_queue()
        if removed_symbol is None:
            if len(self.removed_symbols) >= len(self.config.symbol_removal_order):
                self._disable_future_scatter_triggers()
            return None

        # +2 free spins per spec (only while removals remain)
        self.tot_fs += 2
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)
        self._emit_symbol_removal_events(removed_symbol=removed_symbol)

        if len(self.removed_symbols) >= len(self.config.symbol_removal_order):
            self._disable_future_scatter_triggers()
        return removed_symbol

    def _emit_symbol_removal_events(self, removed_symbol: Optional[str] = None, initial: bool = False):
        """Send backend + frontend notifications about current removal state."""
        ordered_removed = [sym for sym in self.config.symbol_removal_order if sym in self.removed_symbols]
        if not ordered_removed and not initial:
            return
        symbol_removal_event(self, ordered_removed, initial=initial)
        if removed_symbol:
            remaining = [sym for sym in self.config.symbol_removal_order if sym not in self.removed_symbols]
            symbol_removal_notice_event(
                self,
                removed_symbol=removed_symbol,
                remaining_symbols=remaining,
                total_removed=len(self.removed_symbols),
                bonus_mode=self.active_bonus_mode,
            )

    def check_repeat(self):
        super().check_repeat()
        if self.repeat:
            return

        win_criteria = self.get_current_betmode_distributions().get_win_criteria()
        if win_criteria is not None and self.final_win != win_criteria:
            self.repeat = True
            if os.getenv("SIM_DEBUG_PROGRESS", "0") != "0":
                print(
                    "[sim-debug] repeat_override mode={mode} criteria={criteria} "
                    "target={target} final={final}".format(
                        mode=self.betmode,
                        criteria=self.criteria,
                        target=win_criteria,
                        final=self.final_win,
                    ),
                    flush=True,
                )
