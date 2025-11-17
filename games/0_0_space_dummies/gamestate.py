import os

from game_override import GameStateOverride
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim, simulation_seed=None):
        debug_spin = os.getenv("SIM_DEBUG_PROGRESS", "0") != "0"
        attempt_interval = max(int(os.getenv("SIM_DEBUG_SPIN_INTERVAL", "100")), 1)
        attempt = 0
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            attempt += 1
            if debug_spin and (attempt == 1 or attempt % attempt_interval == 0):
                print(
                    "[sim-debug] spin_attempt mode={mode} criteria={criteria} attempt={attempt} "
                    "betmode={betmode} seed={seed}".format(
                        mode=self.betmode,
                        criteria=self.criteria,
                        attempt=attempt,
                        betmode=self.betmode,
                        seed=simulation_seed,
                    ),
                    flush=True,
                )
            self.reset_book()
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                scatter_total = self.count_special_symbols("scatter")
                self.pending_bonus_mode = "hyper" if scatter_total >= 4 else "rocket"
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()
            if debug_spin and not self.repeat:
                print(
                    "[sim-debug] spin_resolved mode={mode} criteria={criteria} attempts={attempt} "
                    "final_win={win:.4f} triggered_fg={fg}".format(
                        mode=self.betmode,
                        criteria=self.criteria,
                        attempts=attempt,
                        win=self.final_win,
                        fg=self.triggered_freegame,
                    ),
                    flush=True,
                )
        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        self.initialize_bonus_session()
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_bonus_board(emit_event=False)
            self.apply_existing_sticky_wilds()
            self.capture_new_sticky_wilds()
            reveal_event(self)

            self.evaluate_lines_board()
            removed_symbol = self.process_edge_scatter_removal()
            if removed_symbol is not None:
                self.record({"event": "symbolRemoval", "symbol": removed_symbol, "mode": self.active_bonus_mode})

            self.win_manager.update_gametype_wins(self.gametype)

        self.clear_bonus_session()
        self.end_freespin()
