import time
import math
import random
import hashlib
from multiprocessing import Process, Manager
import cProfile
from warnings import warn
import shutil
import asyncio
from typing import Dict
from datetime import datetime
import psutil

from src.write_data.write_data import output_lookup_and_force_files


def create_books(
    gamestate: object,
    config: object,
    num_sim_args: dict,
    batch_size: int,
    threads: int,
    compress: bool,
    profiling: bool,
):
    """Main run-function for simulating game outcomes and outputting all files."""
    for key, ns in num_sim_args.items():
        if all([ns > 0, ns > batch_size * batch_size]):
            assert (
                ns % (threads * batch_size) == 0
            ), "mode-sims/(batch * threads) must be divisible with no remainder"
        num_sim_args[key] = int(ns)

    if not compress and sum(num_sim_args.values()) > 1e4:
        warn("Generating large number of uncompressed books!")

    if profiling and threads > 1:
        raise RuntimeError("Multithread profiling not supported, threads must = 1 with profiling enabled")

    startTime = time.time()
    print("\nCreating books...")
    mode_count = 0
    total_modes = len([k for k, v in num_sim_args.items() if v > 0])
    for betmode_name in num_sim_args:
        sim_counter = 0
        for bm in config.bet_modes:
            if bm.get_name() == betmode_name:
                for d in bm.get_distributions():
                    if d.get_fixed_amt() is not None:
                        sim_counter += d.get_fixed_amt()
        set_sim_amount = False
        if sim_counter > 0:
            set_sim_amount = True

        if num_sim_args[betmode_name] > 0:
            mode_count += 1
            mode_start_time = time.time()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing mode {mode_count}/{total_modes}: {betmode_name}")
            print(f"   - Requested simulations: {num_sim_args[betmode_name]:,}")
            gamestate.betmode = betmode_name
            nsims = max(num_sim_args[betmode_name], sim_counter)
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Starting run_multi_process_sims()...")
            run_multi_process_sims(
                threads,
                batch_size,
                config.game_id,
                betmode_name,
                gamestate,
                num_sims=nsims,
                compress=compress,
                write_event_list=config.write_event_list,
                profiling=profiling,
                set_sim_amount=set_sim_amount,
            )
            sim_elapsed = time.time() - mode_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] run_multi_process_sims() completed (took {sim_elapsed:.1f} seconds)")
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Starting output_lookup_and_force_files()...")
            output_start_time = time.time()
            output_lookup_and_force_files(
                threads,
                batch_size,
                config.game_id,
                betmode_name,
                gamestate,
                num_sims=nsims,
                compress=compress,
            )
            output_elapsed = time.time() - output_start_time
            mode_total_elapsed = time.time() - mode_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] output_lookup_and_force_files() completed (took {output_elapsed:.1f} seconds)")
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Mode {betmode_name} complete! Total time: {mode_total_elapsed:.1f} seconds\n")
    shutil.rmtree(gamestate.output_files.temp_path)
    print("\nFinished creating books in", time.time() - startTime, "seconds.\n")


def get_sim_splits(gamestate: object, num_sims: int, betmode_name: str) -> Dict[str, int]:
    """Ensure assignment of criteria to all simulations numbers."""
    betmode_distributions = gamestate.get_betmode(betmode_name).get_distributions()
    num_sims_criteria = {d._criteria: max(int(num_sims * d._quota), 1) for d in betmode_distributions}
    total_sims = sum(num_sims_criteria.values())
    reduce_sims = total_sims > num_sims
    listedCriteria = [d._criteria for d in betmode_distributions]
    criteria_weights = [d._quota for d in betmode_distributions]
    random.seed(0)
    while sum(num_sims_criteria.values()) != num_sims:
        c = random.choices(listedCriteria, criteria_weights)[0]
        if reduce_sims and num_sims_criteria[c] > 1:
            num_sims_criteria[c] -= 1
        elif not reduce_sims:
            num_sims_criteria[c] += 1

    return num_sims_criteria


def assign_sim_criteria(num_sims_criteria: Dict[str, int], sims: int) -> Dict[int, str]:
    """Assign criteria randomly to simulations based on quota defined in config."""
    sim_allocation = [criteria for criteria, count in num_sims_criteria.items() for _ in range(count)]
    random.shuffle(sim_allocation)
    return {i: sim_allocation[i] for i in range(min(sims, len(sim_allocation)))}


def string_to_int(s: str) -> int:
    "Convert criteria name to large integer value"
    h = hashlib.sha256(s.encode()).hexdigest()
    return int(h[:12], 16)


async def profile_and_visualize(
    game_id,
    gamestate,
    all_betmode_configs,
    betmode,
    sim_allocation,
    threads,
    num_repeats,
    sims_per_thread,
    repeat,
    compress,
    write_event_list,
    simulation_seeds,
):
    """Create flame-graph, automatically opens output on localhost."""
    output_string = f"games/{game_id}/simulationProfile_{betmode}.prof"
    cProfile.runctx(
        "gamestate.run_sims(all_betmode_configs, betmode, sim_allocation, threads, num_repeats, sims_per_thread, 0, repeat, compress, write_event_list, simulation_seeds)",
        globals(),
        locals(),
        output_string,
    )
    await asyncio.create_subprocess_exec("snakeviz", output_string)


def run_multi_process_sims(
    threads: int,
    batching_size: int,
    game_id: str,
    betmode: str,
    gamestate: object,
    num_sims: int = 1000000,
    compress: bool = True,
    write_event_list: bool = False,
    profiling: bool = False,
    set_sim_amount=False,
):
    """Setup multiprocessing manager for running all game-mode simulations."""
    print("\nCreating books for", game_id, "in", betmode)
    print(f"   [{datetime.now().strftime('%H:%M:%S')}] Calculating simulation parameters...")
    num_repeats = max(int(round(num_sims / threads / batching_size, 0)), 1)
    sims_per_thread = int(num_sims / threads / num_repeats)
    print(f"   - Total simulations: {num_sims:,}")
    print(f"   - Threads: {threads}")
    print(f"   - Batch size: {batching_size:,}")
    print(f"   - Repeats: {num_repeats}")
    print(f"   - Simulations per thread per repeat: {sims_per_thread:,}")
    if not set_sim_amount:
        num_sims_criteria = get_sim_splits(gamestate, num_sims, betmode)
        sim_criteria = assign_sim_criteria(num_sims_criteria, num_sims)
        simulation_seeds = [i for i in range(len(sim_criteria))]
        criteria_assignment = list(sim_criteria.values())
    else:
        for bm in gamestate.config.bet_modes:
            if bm.get_name() == betmode:
                dists = bm.get_distributions()
                criteria_assignment, simulation_seeds = [], []
                total_quota = 0.0
                # populate fixed amount first
                for d in dists:
                    dist_criteria = d.get_criteria()
                    if d.get_fixed_amt() is not None:
                        criteria_assignment.extend([str(dist_criteria) for _ in range(d.get_fixed_amt())])
                    else:
                        total_quota += d.get_quota()
                # populate remaining with quota
                if len(criteria_assignment) < num_sims:
                    quota_assignment = []
                    quota_probs = []
                    for d in dists:
                        dist_criteria = d.get_criteria()
                        if d.get_quota() is not None:
                            quota_assignment.append(dist_criteria)
                            quota_probs.append(d.get_quota())
                            ncriteria = math.floor(
                                max(1, (d.get_quota() / total_quota) * (num_sims - len(criteria_assignment)))
                            )
                            counter = 0
                            while (len(criteria_assignment) < num_sims) and (counter < ncriteria):
                                criteria_assignment.append(dist_criteria)
                                counter += 1
                    while len(criteria_assignment) < num_sims:
                        criteria_assignment.append(random.choices(quota_assignment, quota_probs, k=1)[0])

                    random.shuffle(criteria_assignment)
                break

        unique_criteria = set(criteria_assignment)
        criteria_offset = {}
        criteria_counter = {}
        for c in unique_criteria:
            criteria_offset[c] = string_to_int(c)
            criteria_counter[c] = 0
        simulation_seeds = []
        for c in criteria_assignment:
            offset_val = criteria_offset[c] + criteria_counter[c]
            criteria_counter[c] += 1
            simulation_seeds.append(offset_val)

    for repeat in range(num_repeats):
        batch_start_time = time.time()
        print(f"\n   [{datetime.now().strftime('%H:%M:%S')}] Starting Batch {repeat + 1} of {num_repeats}")
        processes = []
        manager = Manager()
        all_betmode_configs = manager.list()
        print(f"   [{datetime.now().strftime('%H:%M:%S')}] Created Manager and shared list")
        if profiling:
            asyncio.run(
                profile_and_visualize(
                    game_id=game_id,
                    gamestate=gamestate,
                    all_betmode_configs=all_betmode_configs,
                    betmode=betmode,
                    sim_allocation=criteria_assignment,
                    threads=threads,
                    num_repeats=num_repeats,
                    sims_per_thread=sims_per_thread,
                    repeat=repeat,
                    compress=compress,
                    write_event_list=write_event_list,
                    simulation_seeds=simulation_seeds,
                )
            )
        elif threads == 1:
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Running single-threaded simulation...")
            single_start_time = time.time()
            gamestate.run_sims(
                betmode_copy_list=all_betmode_configs,
                betmode=betmode,
                sim_to_criteria=criteria_assignment,
                total_threads=threads,
                total_repeats=num_repeats,
                num_sims=sims_per_thread,
                thread_index=0,
                repeat_count=repeat,
                compress=compress,
                write_event_list=write_event_list,
                simulation_seeds=simulation_seeds,
            )
            single_elapsed = time.time() - single_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Single-threaded simulation completed (took {single_elapsed:.1f} seconds)")
            gamestate.combine(all_betmode_configs, betmode)
            gamestate.get_betmode(betmode).lock_force_keys()
            manager.shutdown()
            batch_elapsed = time.time() - batch_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Batch {repeat + 1} complete! Time: {batch_elapsed:.1f} seconds")
        else:
            thread_start_time = time.time()
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Starting {threads} worker processes...")
            for thread in range(threads):
                process = Process(
                    target=gamestate.run_sims,
                    args=(
                        all_betmode_configs,
                        betmode,
                        criteria_assignment,
                        threads,
                        num_repeats,
                        sims_per_thread,
                        thread,
                        repeat,
                        compress,
                        write_event_list,
                        simulation_seeds,
                    ),
                )
                print(f"   [{datetime.now().strftime('%H:%M:%S')}] Started thread {thread}")
                process.start()
                processes += [process]
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] All threads are online. Waiting for threads to complete...")
            print(f"   - This may take a while depending on number of simulations per thread ({sims_per_thread:,})")
            join_start_time = time.time()
            last_status_time = time.time()
            completed_processes = set()
            
            # Join processes with periodic status updates
            while len(completed_processes) < len(processes):
                current_time = time.time()
                elapsed = current_time - join_start_time
                
                # Periodic status update every 30 seconds
                if current_time - last_status_time >= 30:
                    alive_count = sum(1 for p in processes if p.is_alive())
                    elapsed_min = int(elapsed // 60)
                    elapsed_sec = int(elapsed % 60)
                    
                    # Get remaining thread IDs and their runtimes
                    remaining_threads = []
                    for i, process in enumerate(processes):
                        if i not in completed_processes and process.is_alive():
                            thread_elapsed = elapsed  # All threads started at the same time
                            remaining_threads.append((i, thread_elapsed))
                    
                    # Get CPU and memory usage for remaining processes
                    cpu_percents = []
                    mem_mbs = []
                    for i, process in enumerate(processes):
                        if i not in completed_processes and process.is_alive():
                            try:
                                proc = psutil.Process(process.pid)
                                cpu_percents.append(proc.cpu_percent(interval=0.1))
                                mem_mbs.append(proc.memory_info().rss / (1024 * 1024))
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    
                    # Build status message
                    status_msg = f"   [{datetime.now().strftime('%H:%M:%S')}] Status: {alive_count} threads still running, {len(completed_processes)} completed (elapsed: {elapsed_min}m {elapsed_sec}s)"
                    if remaining_threads:
                        thread_list = ", ".join([f"Thread {tid} ({int(te//60)}m {int(te%60)}s)" for tid, te in remaining_threads])
                        status_msg += f"\n      Still running: {thread_list}"
                    if cpu_percents:
                        avg_cpu = sum(cpu_percents) / len(cpu_percents) if cpu_percents else 0
                        avg_mem = sum(mem_mbs) / len(mem_mbs) if mem_mbs else 0
                        status_msg += f"\n      Avg CPU usage: {avg_cpu:.1f}%, Avg memory: {avg_mem:.1f} MB"
                        if avg_cpu < 1.0 and elapsed_min > 5:
                            status_msg += " ⚠️ LOW CPU - thread may be stuck!"
                    
                    print(status_msg)
                    last_status_time = current_time
                
                # Try joining each remaining process with a short timeout
                for i, process in enumerate(processes):
                    if i not in completed_processes:
                        process.join(timeout=1.0)
                        # Check if process finished (join returns immediately if already done, or after timeout if still running)
                        if not process.is_alive() and i not in completed_processes:
                            completed_processes.add(i)
                            elapsed = time.time() - join_start_time
                            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Thread {i} completed! (elapsed: {elapsed:.1f}s, {len(completed_processes)}/{len(processes)} done)")
                            last_status_time = time.time()
                            break  # Break to restart the loop and check all processes again
            
            join_elapsed = time.time() - join_start_time
            thread_total_elapsed = time.time() - thread_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] All threads finished! Total thread time: {thread_total_elapsed:.1f} seconds")
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Combining results...")
            combine_start_time = time.time()
            gamestate.combine(all_betmode_configs, betmode)
            combine_elapsed = time.time() - combine_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Results combined (took {combine_elapsed:.1f} seconds)")
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Locking force keys...")
            gamestate.get_betmode(betmode).lock_force_keys()
            manager.shutdown()
            batch_elapsed = time.time() - batch_start_time
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Batch {repeat + 1} complete! Time: {batch_elapsed:.1f} seconds")
