#!/usr/bin/env python3
"""Quick test script to run 30000 spins per mode without optimization for Gunslingers: DRAW!"""

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from game_stats_summary import print_rtp_summary

if __name__ == "__main__":
    
    print("="*80)
    print("GUNSLINGERS: DRAW! - QUICK TEST (30,000 SPINS, NO OPTIMIZATION)")
    print("="*80)
    print()

    # Simulation settings
    num_threads = 10
    batching_size = 5000
    compression = True
    profiling = False

    # Set to 30,000 spins per mode
    num_sim_args = {
        "base": 30000,
        "bonus": 30000,
        "superbonus": 30000,
    }

    # Initialize game
    config = GameConfig()
    gamestate = GameState(config)

    print(f"Running simulations: {num_sim_args}")
    print(f"Threads: {num_threads}, Batch size: {batching_size}")
    print()

    # Run simulations (no optimization)
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )

    # Generate configs
    print("\nGenerating config files...")
    generate_configs(gamestate)

    # Print RTP and statistics summary
    print("\n" + "="*80)
    print("SIMULATION RESULTS SUMMARY")
    print("="*80)
    print_rtp_summary(config)

    print("\n" + "="*80)
    print("TEST COMPLETE! (30,000 spins per mode)")
    print("="*80)
    print("\nResults saved to:")
    print(f"  - Books: games/1_0_gunslingers/library/books/")
    print(f"  - Lookup tables: games/1_0_gunslingers/library/lookup_tables/")
    print(f"  - Configs: games/1_0_gunslingers/library/configs/")

