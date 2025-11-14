"""Game-specific configuration file, inherits from src/config/config.py"""

import os
from copy import deepcopy
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
        self.game_id = "space_dummies"
        self.provider_number = 0
        self.working_name = "ShiftGaming.SpaceDummies"
        self.wincap = 12500.0
        self.win_type = "lines"
        self.rtp = 0.9620
        self.construct_paths()

        # Custom win levels for Space Dummies
        self.win_levels = {
            "standard": {
                1: (0, 0.1),
                2: (0.1, 1.0),
                3: (1.0, 5.0),
                4: (5.0, 25.0),
                5: (25.0, 50.0),      # Substantial win (>25x)
                6: (50.0, 100.0),     # Big win (>50x)
                7: (100.0, 250.0),    # Super win (>100x)
                8: (250.0, 500.0),    # Mega win (>250x)
                9: (500.0, self.wincap),  # Epic win (>500x)
                10: (self.wincap, float("inf")),  # Max win (12500x)
            },
            "endFeature": {
                1: (0.0, 1.0),
                2: (1.0, 5.0),
                3: (5.0, 10.0),
                4: (10.0, 25.0),
                5: (25.0, 50.0),      # Substantial win (>25x)
                6: (50.0, 100.0),     # Big win (>50x)
                7: (100.0, 250.0),    # Super win (>100x)
                8: (250.0, 500.0),    # Mega win (>250x)
                9: (500.0, self.wincap),  # Epic win (>500x)
                10: (self.wincap, float("inf")),  # Max win (12500x)
            },
        }

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [4] * self.num_reels
        # Board and Symbol Properties
        self.paytable = {
            (5, "zog"): 100.0,
            (4, "zog"): 20.0,
            (3, "zog"): 4.0,
            (5, "chip"): 40.0,
            (4, "chip"): 15.0,
            (3, "chip"): 3.0,
            (5, "sc3"): 10.0,
            (4, "sc3"): 5.0,
            (3, "sc3"): 1.4,
            (5, "sc2"): 8.0,
            (4, "sc2"): 4.0,
            (3, "sc2"): 1.2,
            (5, "sc1"): 6.0,
            (4, "sc1"): 3.0,
            (3, "sc1"): 1.0,
            (5, "sa"): 5.0,
            (4, "sa"): 2.0,
            (3, "sa"): 0.4,
            (5, "sk"): 4.0,
            (4, "sk"): 1.4,
            (3, "sk"): 0.4,
            (5, "sq"): 3.0,
            (4, "sq"): 1.0,
            (3, "sq"): 0.2,
            (5, "sj"): 2.4,
            (4, "sj"): 0.8,
            (3, "sj"): 0.2,
            (5, "s10"): 2.0,
            (4, "s10"): 0.6,
            (3, "s10"): 0.2,
        }

        self.paylines = {
            1: [1, 1, 1, 1, 1],
            2: [0, 0, 0, 0, 0],
            3: [2, 2, 2, 2, 2],
            4: [3, 3, 3, 3, 3],
            5: [0, 1, 2, 1, 0],
            6: [3, 2, 1, 2, 3],
            7: [0, 1, 0, 1, 0],
            8: [3, 2, 3, 2, 3],
            9: [1, 0, 1, 2, 1],
            10: [2, 3, 2, 1, 2],
            11: [0, 0, 1, 2, 3],
            12: [3, 3, 2, 1, 0],
            13: [1, 2, 3, 2, 1],
            14: [2, 1, 0, 1, 2],
            15: [0, 1, 2, 3, 3],
            16: [3, 2, 1, 0, 0],
            17: [1, 2, 1, 0, 1],
            18: [2, 1, 2, 3, 2],
            19: [0, 0, 1, 1, 2],
            20: [3, 3, 2, 2, 1],
        }

        self.include_padding = True
        self.special_symbols = {
            "wild": ["wild"],
            "scatter": ["scatter"],
            "multiplier": ["wild"],
            "sticky": ["wild"],
        }

        self.symbol_removal_order_regular = [
            "s10",
            "sj",
            "sq",
            "sk",
            "sa",
            "sc1",
            "sc2",
            "sc3",
        ]
        self.symbol_removal_order_super = ["sc1", "sc2", "sc3"]

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},
            self.freegame_type: {},
        }
        self.anticipation_triggers = {}
        for gametype, trigger_map in self.freespin_triggers.items():
            self.anticipation_triggers[gametype] = (
                min(trigger_map.keys()) - 1 if trigger_map else 0
            )

        # Reels
        reels = {"BR0": "BR0.csv", "RR0": "RR0.csv", "HD0": "HD0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        self.base_reels = deepcopy(self.reels)

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["RR0"]
        self.padding_symbol_values = {
            "wild": {"multiplier": {2: 60, 3: 25, 5: 10, 10: 5}},
        }

        base_multiplier_weights = {
            self.basegame_type: {2: 60, 3: 25, 5: 10, 10: 5},
            self.freegame_type: {2: 40, 3: 30, 5: 20, 10: 10},
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": False,
        }

        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"WCAP": 1},
            },
            "mult_values": base_multiplier_weights,
            "force_wincap": True,
            "force_freegame": True,
            "bonus_mode": "hyperdrive",
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": False,
        }

        rocket_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"RR0": 1},
            },
            "scatter_triggers": {3: 1},
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": True,
            "bonus_mode": "rocket",
        }

        hyper_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"HD0": 1},
            },
            "scatter_triggers": {4: 1},
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": True,
            "bonus_mode": "hyperdrive",
        }

        rocket_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"RR0": 1},
            },
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": True,
            "bonus_mode": "rocket",
        }

        hyper_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"HD0": 1},
            },
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": True,
            "bonus_mode": "hyperdrive",
        }
        extra_feature_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"RR0": 1},
            },
            "scatter_triggers": {2: 250, 3: 25, 4: 2},
            "mult_values": base_multiplier_weights,
            "force_wincap": False,
            "force_freegame": False,
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
                        criteria="wincap", quota=0.0005, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="hyperdrive", quota=0.02, conditions=hyper_condition),
                    Distribution(criteria="rocket", quota=0.08, conditions=rocket_condition),
                    Distribution(criteria="0", quota=0.45, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.4445, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="rocket_riot_buy",
                cost=75.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.0005, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="rocket", quota=0.9995, conditions=rocket_buy_condition),
                ],
            ),
            BetMode(
                name="hyperdrive_buy",
                cost=150.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.0005, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="hyperdrive", quota=0.9995, conditions=hyper_buy_condition),
                ],
            ),
            BetMode(
                name="extra_feature_spin",
                cost=3.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.0005, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="tease", quota=0.15, conditions=extra_feature_condition),
                    Distribution(criteria="0", quota=0.45, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.3995, conditions=basegame_condition),
                ],
            ),
        ]
