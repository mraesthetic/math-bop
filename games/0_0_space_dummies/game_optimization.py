"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """"""

    def __init__(self, game_config):
        self.game_config = game_config
        base_scaling = ConstructScaling(
            [
                {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                {"criteria": "basegame", "scale_factor": 1.5, "win_range": (10, 20), "probability": 1.0},
                {
                    "criteria": "freegame",
                    "scale_factor": 0.8,
                    "win_range": (1000, 2000),
                    "probability": 1.0,
                },
                {
                    "criteria": "freegame",
                    "scale_factor": 1.2,
                    "win_range": (3000, 4000),
                    "probability": 1.0,
                },
            ]
        ).return_dict()

        base_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
        ).return_dict()

        bonus_scaling = ConstructScaling(
            [
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (1, 20), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.5, "win_range": (20, 50), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.8, "win_range": (50, 100), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.8, "win_range": (1000, 2000), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (3000, 4000), "probability": 1.0},
            ]
        ).return_dict()

        bonus_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
        ).return_dict()

        wincap_win = self.game_config.wincap

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.54, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.2, rtp=0.42).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(2.0, 3.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "bonus_hunt": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0.0, av_win=0.0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.74, hr=150, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.5, rtp=0.22).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(1.5, 2.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "rocket_buy": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "rocket_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["rocket_entry"],
                    bias_ranges=[(200.0, 350.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
            "hyper_buy": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.002, av_win=wincap_win, search_conditions=wincap_win
                    ).return_dict(),
                    "hyper_entry": ConstructConditions(rtp=0.96, hr="x").return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["hyper_entry"],
                    bias_ranges=[(250.0, 400.0)],
                    bias_weights=[0.3],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
