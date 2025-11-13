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
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "hyperdrive": ConstructConditions(
                        rtp=0.074, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "rocket": ConstructConditions(
                        rtp=0.296, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.582).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 1.5, "win_range": (10, 20), "probability": 1.0},
                        {
                            "criteria": "hyperdrive",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "hyperdrive",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "rocket",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "rocket",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(2.0, 3.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "extra_feature_spin": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "tease": ConstructConditions(rtp=0.15, hr=50).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.802).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "tease", "scale_factor": 1.5, "win_range": (1, 5), "probability": 1.0},
                        {"criteria": "tease", "scale_factor": 0.9, "win_range": (100, 300), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 1.1, "win_range": (5, 10), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=3000,
                    num_per_fence=7500,
                    min_m2m=3.5,
                    max_m2m=7,
                    pmb_rtp=1.0,
                    sim_trials=4000,
                    test_spins=[25, 50, 100],
                    test_weights=[0.4, 0.35, 0.25],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["tease"],
                    bias_ranges=[(1.0, 2.0)],
                    bias_weights=[0.6],
                ).return_dict(),
            },
            "rocket_riot_buy": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "rocket": ConstructConditions(rtp=0.952, hr=150, search_conditions={"bonus_mode": "rocket"}).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "rocket", "scale_factor": 1.1, "win_range": (5, 20), "probability": 1.0},
                        {"criteria": "rocket", "scale_factor": 0.9, "win_range": (200, 400), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=4000,
                    num_per_fence=9000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=4500,
                    test_spins=[25, 50, 100],
                    test_weights=[0.4, 0.35, 0.25],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["rocket"],
                    bias_ranges=[(3.0, 5.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "hyperdrive_buy": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "hyperdrive": ConstructConditions(
                        rtp=0.952, hr=120, search_conditions={"bonus_mode": "hyperdrive"}
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "hyperdrive", "scale_factor": 1.15, "win_range": (5, 15), "probability": 1.0},
                        {"criteria": "hyperdrive", "scale_factor": 0.85, "win_range": (250, 450), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=4000,
                    num_per_fence=9000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=4500,
                    test_spins=[25, 50, 100],
                    test_weights=[0.4, 0.35, 0.25],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["hyperdrive"],
                    bias_ranges=[(4.0, 6.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
