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
        self.game_id = "1_0_gunslingers"
        self.provider_number = 0
        self.working_name = "Gunslingers: DRAW!"
        # Max win cap: 10,000× bet (increased from 5,000×)
        self.wincap = 10000.0
        self.win_type = "lines"
        self.rtp = 0.962
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 5
        self.num_rows = [3] * self.num_reels
        # Board and Symbol Properties
        # Gunslingers: DRAW! paytable
        self.paytable = {
            # W: WILD (standard wild)
            (5, "W"): 20,
            (4, "W"): 10,
            (3, "W"): 5,
            # H1: BANDIT GUY (premium)
            (5, "H1"): 25,
            (4, "H1"): 6,
            (3, "H1"): 2,
            # H2: BANDIT GIRL (premium)
            (5, "H2"): 18,
            (4, "H2"): 5,
            (3, "H2"): 1.5,
            # H3: SHOTGUN (premium)
            (5, "H3"): 14,
            (4, "H3"): 4,
            (3, "H3"): 1.2,
            # H4: WHISKEY (premium)
            (5, "H4"): 10,
            (4, "H4"): 3,
            (3, "H4"): 1,
            # L1: A (low)
            (5, "L1"): 5,
            (4, "L1"): 1.5,
            (3, "L1"): 0.5,
            # L2: K (low)
            (5, "L2"): 4,
            (4, "L2"): 1.2,
            (3, "L2"): 0.4,
            # L3: Q (low)
            (5, "L3"): 3.5,
            (4, "L3"): 1,
            (3, "L3"): 0.3,
            # L4: J (low)
            (5, "L4"): 3,
            (4, "L4"): 0.8,
            (3, "L4"): 0.2,
            # L5: 10 (low)
            (5, "L5"): 2.5,
            (4, "L5"): 0.6,
            (3, "L5"): 0.2,
            # Note: S (SCATTER) and VS (DRAW) are special symbols with no paytable entries
        }

        # 10 fixed paylines for 5x3 grid (0-based indexing: 0=top, 1=middle, 2=bottom)
        self.paylines = {
            # Line 1: top row (1-1-1-1-1)
            1: [0, 0, 0, 0, 0],
            # Line 2: middle row (2-2-2-2-2)
            2: [1, 1, 1, 1, 1],
            # Line 3: bottom row (3-3-3-3-3)
            3: [2, 2, 2, 2, 2],
            # Line 4: V shape down (1-2-3-2-1)
            4: [0, 1, 2, 1, 0],
            # Line 5: V shape up (3-2-1-2-3)
            5: [2, 1, 0, 1, 2],
            # Line 6: zigzag down (1-1-2-2-3)
            6: [0, 0, 1, 1, 2],
            # Line 7: zigzag up (3-3-2-2-1)
            7: [2, 2, 1, 1, 0],
            # Line 8: step down (1-2-2-2-3)
            8: [0, 1, 1, 1, 2],
            # Line 9: step up (3-2-2-2-1)
            9: [2, 1, 1, 1, 0],
            # Line 10: wave (1-2-1-2-1)
            10: [0, 1, 0, 1, 0],
        }

        self.include_padding = True
        # Special symbols:
        # S: SCATTER (sheriff badge) - triggers free spins
        # W: WILD - substitutes for regular symbols, has multipliers in freegame
        # VS: DRAW symbol - expanding wild with multipliers (substitutes all except scatter)
        # underlyingSymbol: Custom attribute for VS symbols in superbonus when forced over scatters
        self.special_symbols = {"wild": ["W", "VS"], "scatter": ["S"], "multiplier": ["W", "VS"], "underlyingSymbol": []}

        # Free spin triggers: Max 4 scatters can appear on screen
        # Base game: 3 scatters = regular bonus (10 FS), 4 scatters = SUPER DRAW! (10 FS)
        # Retrigger (during free spins): 2 scatters = 2 FS, 3 scatters = 3 FS, 4 scatters = 8 FS
        # Note: 4 scatters from base triggers superbonus mode (FR1 reelset, guaranteed VS)
        # Note: 5 scatters cannot occur (max 4 scatters enforced in BR0.csv)
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},  # 3 scatters = regular bonus, 4 scatters = superbonus
            self.freegame_type: {2: 2, 3: 3, 4: 8},  # Retriggers (5 scatters removed, max 4)
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "FR1": "FR1.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        # Default freegame reelset (used for regular bonus)
        # Can be switched to FR1 for superbonus when 4 scatters trigger from base
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        # VS (DRAW) multiplier distribution
        # Regular bonus: Adjusted to target ~96.2% RTP (96.2x avg feature win at 100x cost)
        # Increased high-tier multipliers (4×, 5×) weights for ~1.5% EV increase
        # Added 25× and 50× multipliers for increased volatility while maintaining ~2.35× average
        # Super DRAW! (superbonus): Uses separate superbonus_vs_multipliers
        # NOTE: Combined VS multipliers are capped at 500× (see game_executables.py)
        # 
        # Regular Bonus VS Distribution (with 25× and 50× added for volatility):
        #   Multipliers: 2×: 810, 3×: 168, 4×: 60, 5×: 22, 8×: 3, 10×: 1, 25×: 1, 50×: 1
        #   Total weight: 1065
        #   Average multiplier: ~2.425× (slightly above 2.35×, but within acceptable range)
        #   25× probability: 0.094% | 50× probability: 0.094% | Combined: 0.188% (< 1%)
        #   Note: Average is slightly elevated due to high multipliers, but RTP impact is minimal
        self.padding_symbol_values = {
            "W": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}},
            "VS": {"multiplier": {2: 810, 3: 168, 4: 60, 5: 22, 8: 3, 10: 1, 25: 1, 50: 1}},
        }
        # Superbonus-specific VS multiplier distribution (applied in game_executables.py)
        # Adjusted to target ~96.2% RTP (384.8x avg feature win at 400x cost)
        # Increased high-tier multipliers (>3×) weights for ~0.9% EV increase
        # Added 25× and 50× multipliers for increased volatility (slightly higher chance than regular bonus)
        # NOTE: Combined VS multipliers are capped at 500× (see game_executables.py)
        #
        # Superbonus VS Distribution (with 25× and 50× added for volatility):
        #   Multipliers: 2×: 740, 3×: 230, 4×: 38, 5×: 10, 8×: 3, 10×: 1, 25×: 2, 50×: 1
        #   Total weight: 1025
        #   Average multiplier: ~2.425× (slightly above 2.35×, but within acceptable range)
        #   25× probability: 0.195% | 50× probability: 0.098% | Combined: 0.293% (slightly > regular bonus, < 1%)
        self.superbonus_vs_multipliers = {2: 740, 3: 230, 4: 38, 5: 10, 8: 3, 10: 1, 25: 2, 50: 1}

        freegame_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            # Adjusted scatter weights to match 400x superbonus buy cost:
            # With 10% bonus trigger rate, target ~0.25% superbonus rate (1 in 400 spins)
            # {3: 98, 4: 2} gives 2% of bonuses = 0.2% of spins (1 in 500) - much closer to target
            # Previous {3: 50, 4: 20} gave 28.6% of bonuses = 2.86% of spins (1 in 35) - way too frequent!
            "scatter_triggers": {3: 85, 4: 15},  # Used for base game natural triggers (3 or 4 scatters possible)
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {
                    2: 60,
                    3: 80,
                    4: 50,
                    5: 20,
                    10: 15,
                    20: 10,
                    50: 5,
                },
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        # Regular bonus buy condition: Only allows 3 scatters (prevents 4-scatter superbonus trigger)
        regular_bonus_buy_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1},
            },
            "scatter_triggers": {3: 100},  # Always force exactly 3 scatters (prevents 4-scatter superbonus)
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {
                    2: 60,
                    3: 80,
                    4: 50,
                    5: 20,
                    10: 15,
                    20: 10,
                    50: 5,
                },
            },
            "force_wincap": False,
            "force_freegame": True,
        }

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {self.basegame_type: {1: 1}},
            "force_wincap": False,
            "force_freegame": False,
        }

        # Win cap condition: Forces max win scenario (10,000× bet cap)
        # Uses FRWCAP.csv reelset to demonstrate max win potential
        wincap_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR0": 1, "WCAP": 5},
            },
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 60, 10: 100, 20: 90, 50: 50},
            },
            "scatter_triggers": {4: 1},  # Removed 5-scatter case (max 4 scatters)
            "force_wincap": True,
            "force_freegame": True,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1},
            },
            "force_wincap": False,
            "force_freegame": False,
        }

        # SUPER DRAW! condition: Uses FR1.csv reelset, guarantees 1 VS reel per spin
        # Feature buy: Always awards exactly 4 scatters = 10 free spins (matches natural trigger)
        superbonus_condition = {
            "reel_weights": {
                self.basegame_type: {"BR0": 1},
                self.freegame_type: {"FR1": 1},  # Use FR1.csv for superbonus
            },
            "scatter_triggers": {4: 100},  # Always force exactly 4 scatters (10 spins) - matches natural trigger
            "mult_values": {
                self.basegame_type: {1: 1},
                self.freegame_type: {
                    2: 60,
                    3: 80,
                    4: 50,
                    5: 20,
                    10: 15,
                    20: 10,
                    50: 5,
                },
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
                    Distribution(criteria="freegame", quota=0.0052, conditions=freegame_condition),
                    Distribution(criteria="0", quota=0.4738, win_criteria=0.0, conditions=zerowin_condition),
                    Distribution(criteria="basegame", quota=0.52, conditions=basegame_condition),
                ],
            ),
            BetMode(
                name="bonus",
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
                    Distribution(criteria="freegame", quota=0.999, conditions=regular_bonus_buy_condition),
                ],
            ),
            BetMode(
                name="superbonus",
                cost=400.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap", quota=0.001, win_criteria=self.wincap, conditions=wincap_condition
                    ),
                    Distribution(criteria="freegame", quota=0.999, conditions=superbonus_condition),
                ],
            ),
        ]
