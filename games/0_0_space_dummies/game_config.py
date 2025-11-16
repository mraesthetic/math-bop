"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_space_dummies"
        self.provider_number = 0
        self.working_name = "Space Dummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels

        # Symbol groupings (used for validation + removal logic)
        self.symbol_ids = {
            "low": ["s10", "sj", "sq", "sk", "sa"],
            "mid": ["sc1", "sc2", "sc3"],
            "premium": ["chip", "zog"],
            "feature": ["wild", "scatter"],
        }
        self.all_valid_sym_names = set()
        for symbol_group in self.symbol_ids.values():
            self.all_valid_sym_names.update(symbol_group)
        self.symbol_removal_order = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]

        # Board and Symbol Properties — pays are total-bet multipliers
        payouts = {
            "s10": {5: 2.0, 4: 0.6, 3: 0.2},
            "sj": {5: 2.4, 4: 0.8, 3: 0.2},
            "sq": {5: 3.0, 4: 1.0, 3: 0.2},
            "sk": {5: 4.0, 4: 1.4, 3: 0.4},
            "sa": {5: 5.0, 4: 2.0, 3: 0.4},
            "sc1": {5: 6.0, 4: 3.0, 3: 1.0},
            "sc2": {5: 8.0, 4: 4.0, 3: 1.2},
            "sc3": {5: 10.0, 4: 5.0, 3: 1.4},
            "chip": {5: 40.0, 4: 15.0, 3: 3.0},
            "zog": {5: 100.0, 4: 20.0, 3: 4.0},
        }
        self.paytable = {}
        for symbol, symbol_payouts in payouts.items():
            for count, amount in symbol_payouts.items():
                self.paytable[(count, symbol)] = amount

        payline_definitions = [
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4],
            [1, 2, 3, 2, 1],
            [4, 3, 2, 3, 4],
            [1, 2, 1, 2, 1],
            [4, 3, 4, 3, 4],
            [2, 1, 2, 3, 2],
            [3, 4, 3, 2, 3],
            [1, 1, 2, 3, 4],
            [4, 4, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [3, 2, 1, 2, 3],
            [1, 2, 3, 4, 4],
            [4, 3, 2, 1, 1],
            [2, 3, 2, 1, 2],
            [3, 2, 3, 4, 3],
            [1, 1, 2, 2, 3],
            [4, 4, 3, 3, 2],
        ]
        self.paylines = {
            idx + 1: [position - 1 for position in pattern] for idx, pattern in enumerate(payline_definitions)
        }

        self.include_padding = True
        self.special_symbols = {"wild": ["wild"], "scatter": ["scatter"], "multiplier": ["wild"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            # In bonus modes, retriggers are granted via the scatter-on-reels-1-and-5 rule.
            # This placeholder entry allows anticipation logic to function; the actual positional
            # checks are handled in the game-state layer.
            self.freegame_type: {2: 2},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        wild_multiplier_weights = {2: 45, 3: 30, 5: 20, 10: 5}
        self.padding_symbol_values = {"wild": {"multiplier": wild_multiplier_weights}}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 80, 4: 20},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: wild_multiplier_weights},
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "scatter_triggers": {4: 1},
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": False,
        }

        rocket_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 1},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        hyper_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"WCAP": 1},
            },
            "scatter_triggers": {4: 1},
            "mult_values": {
                self.basegame_type: wild_multiplier_weights,
                self.freegame_type: wild_multiplier_weights,
            },
            "force_wincap": False,
            "force_freegame": True,
        }
        # Contains all game-logic simulation conditions
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.1, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.5, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus_hunt",
                cost=3.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.25, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.25, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.499, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="rocket_buy",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="rocket_entry", quota=0.999, conditions=rocket_buy_condition),
                ],
            ),
            BetMode(
                name="hyper_buy",
                cost=200.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="hyper_entry", quota=0.999, conditions=hyper_buy_condition),
                ],
            ),
        ]
