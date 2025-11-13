"""Main file for generating results for sample lines-pay game."""

import os
import psutil

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    print("\n" + "="*60)
    print("🚀 SPACE DUMMIES - Game Generation Pipeline")
    print("="*60 + "\n")

    # System Resource Check
    cpu_count = os.cpu_count() or 1
    memory = psutil.virtual_memory()
    print("💻 System Resources:")
    print(f"   - CPU cores available: {cpu_count}")
    print(f"   - Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"   - Available RAM: {memory.available / (1024**3):.1f} GB ({memory.percent}% used)")
    print()

    # PC-OPTIMIZED SETTINGS
    # Higher thread counts for more powerful machines:
    # - num_threads: 10 (production)
    # - rust_threads: 20 (production)
    # - simulations: 10000 per mode (production)
    
    num_threads = 10
    rust_threads = 20
    batching_size = 5000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e4),
        "extra_feature_spin": int(1e4),
        "rocket_riot_buy": int(1e4),
        "hyperdrive_buy": int(1e4),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = list(num_sim_args.keys())

    print("📋 Configuration:")
    print(f"   - Threads: {num_threads}")
    print(f"   - Rust threads: {rust_threads}")
    print(f"   - Batch size: {batching_size}")
    print(f"   - Compression: {compression}")
    print(f"   - Target modes: {', '.join(target_modes)}")
    
    # Resource warnings
    total_threads = num_threads + rust_threads
    if num_threads > cpu_count:
        print(f"\n⚠️  WARNING: num_threads ({num_threads}) > CPU cores ({cpu_count})")
        print("   This may cause performance issues. Consider reducing num_threads.")
    if total_threads > cpu_count * 2:
        print(f"\n⚠️  WARNING: Total threads ({total_threads}) >> CPU cores ({cpu_count})")
        print("   This may overwhelm your system. Consider reducing thread counts.")
    if memory.available < 4 * (1024**3):  # Less than 4GB available
        print(f"\n⚠️  WARNING: Low available RAM ({memory.available / (1024**3):.1f} GB)")
        print("   Consider closing other applications or reducing simulation count.")
    print()

    print("⚙️  Initializing game configuration and state...")
    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)
    print("✅ Configuration complete\n")

    if run_conditions["run_sims"]:
        print("🎲 Starting simulations...")
        print(f"   - Running {sum(num_sim_args.values()):,} total simulations across {len(num_sim_args)} modes")
        for mode, count in num_sim_args.items():
            print(f"   - {mode}: {count:,} simulations")
        print()
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )
        print("✅ Simulations complete\n")

    print("📝 Generating configuration files...")
    generate_configs(gamestate)
    print("✅ Configuration files generated\n")

    if run_conditions["run_optimization"]:
        print("🔧 Starting optimization process...")
        print(f"   - Using {rust_threads} Rust threads")
        print(f"   - Optimizing modes: {', '.join(target_modes)}")
        print()
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        print("\n📝 Regenerating configuration files after optimization...")
        generate_configs(gamestate)
        print("✅ Optimization complete\n")

    if run_conditions["run_analysis"]:
        print("📊 Running game analysis...")
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)
        print("✅ Analysis complete\n")

    if run_conditions["run_format_checks"]:
        print("🔍 Running format validation checks...")
        execute_all_tests(config)
        print("✅ Format checks complete\n")

    print("="*60)
    print("✨ SPACE DUMMIES - Pipeline Complete!")
    print("="*60 + "\n")
