"""Main entry point for Space Dummies math runs."""

import json
import os
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.validation.reel_validator import validate_reels_for_game
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

FAST_SIM_DEFAULT = True
FAST_SIM_ANALYSIS = True  # set False to keep analysis disabled in fast mode


def print_fast_summary(config: GameConfig) -> None:
    """Pretty-print core stats from the last fast simulation run."""

    summary_files = [
        Path(config.library_path).joinpath("statistics_summary.json"),
        Path(config.library_path).joinpath("stats_summary.json"),
    ]
    stats_path = next((p for p in summary_files if p.exists()), None)
    if stats_path is None:
        print("[summary] No statistics summary found. Skipping display.")
        return

    try:
        data = json.loads(stats_path.read_text())
    except json.JSONDecodeError:
        print(f"[summary] Could not parse {stats_path}.")
        return

    print("\n=== Fast Simulation Summary ===")
    modes = data.get("modes") or data.get("modeSummaries") or []
    for mode in modes:
        name = mode.get("name") or mode.get("mode") or "unknown"
        spins = mode.get("spins") or mode.get("totalSpins")
        rtp = mode.get("rtp") or mode.get("totalRtp")
        hit_rate = mode.get("hitRate") or mode.get("hit_rate")
        bonus_rate = mode.get("bonusFrequency") or mode.get("bonusRate")
        print(f"Mode: {name}")
        if spins is not None:
            print(f"  Spins: {spins:,}")
        if rtp is not None:
            print(f"  RTP: {float(rtp):.4f}")
        if hit_rate is not None:
            print(f"  Hit Rate: {hit_rate}")
        if bonus_rate is not None:
            print(f"  Bonus Frequency: {bonus_rate}")
    print("=== End Summary ===\n")

if __name__ == "__main__":

    num_threads = int(os.getenv("SIM_THREADS", 10))
    rust_threads = int(os.getenv("SIM_RUST_THREADS", 20))
    batching_size = int(os.getenv("SIM_BATCH_SIZE", 5000))
    compression = True
    profiling = False

    fast_sim = os.getenv("FAST_SIM", "1" if FAST_SIM_DEFAULT else "0") != "0"
    fast_spin_count = int(float(os.getenv("FAST_SIM_SPINS", "20000")))
    default_spin_count = int(float(os.getenv("DEFAULT_SIM_SPINS", "10000")))
    sim_count = fast_spin_count if fast_sim else default_spin_count

    num_sim_args = {
        "base": sim_count,
        "bonus_hunt": sim_count,
        "rocket_buy": sim_count,
        "hyper_buy": sim_count,
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": not fast_sim,
        "run_analysis": (FAST_SIM_ANALYSIS or not fast_sim),
        "run_format_checks": not fast_sim,
    }
    target_modes = list(num_sim_args.keys())

    config = GameConfig()
    validate_reels_for_game(config)
    gamestate = GameState(config)
    if run_conditions["run_optimization"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)
    elif fast_sim:
        print_fast_summary(config)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
