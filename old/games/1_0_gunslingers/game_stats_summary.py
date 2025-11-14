"""Custom RTP and statistics summary for Gunslingers game.
Prints detailed statistics including VS usage and feature statistics.
"""

import json
import os
import zstandard as zst
from io import TextIOWrapper
from collections import defaultdict
from utils.rgs_verification import verify_lookup_format
from utils.analysis.distribution_functions import calculate_rtp, non_zero_hitrate


def analyze_books_for_vs_stats(book_file_path: str):
    """Analyze books to extract VS usage statistics.
    Returns:
        dict with VS statistics: spins_with_vs, total_spins, vs_reels_per_spin, vs_multipliers
    """
    vs_stats = {
        'spins_with_vs': 0,
        'total_spins': 0,
        'vs_reels_per_spin': [],
        'vs_multipliers': [],
        'feature_wins': [],  # For bonus/superbonus: track total win per feature
    }
    
    if not os.path.exists(book_file_path):
        return vs_stats
    
    try:
        with open(book_file_path, "rb") as f:
            decompressor = zst.ZstdDecompressor()
            with decompressor.stream_reader(f) as reader:
                txt_stream = TextIOWrapper(reader, encoding="UTF-8")
                for line in txt_stream:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        blob = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    events = blob.get("events", [])
                    payout_mult = blob.get("payoutMultiplier", 0) / 100.0  # Convert from cents to bet multiplier
                    
                    vs_reels_this_spin = set()  # Track unique reels with VS
                    vs_multipliers_this_spin = []
                    reveal_board = None
                    
                    # First pass: collect VS info from reveal and win events
                    for event in events:
                        event_type = event.get("type", "")
                        
                        # Check for VS symbols in reveal events (before expansion)
                        # VS symbols appear as "VS" in the reveal, then expand to wilds
                        if event_type == "reveal":
                            reveal_board = event.get("board", [])
                            for reel_idx, reel in enumerate(reveal_board):
                                for symbol in reel:
                                    if isinstance(symbol, dict) and symbol.get("name") == "VS":
                                        vs_reels_this_spin.add(reel_idx)
                                        break
                        
                        # Check win events for VS multipliers (stored in meta.vsMultiplier)
                        if event_type == "winInfo":
                            wins = event.get("wins", [])
                            for win in wins:
                                meta = win.get("meta", {})
                                vs_mult = meta.get("vsMultiplier")
                                if vs_mult and vs_mult > 1:
                                    vs_multipliers_this_spin.append(vs_mult)
                    
                    # Count spins (each book entry is a spin/round)
                    vs_stats['total_spins'] += 1
                    
                    # Track VS usage
                    if len(vs_reels_this_spin) > 0:
                        vs_stats['spins_with_vs'] += 1
                        vs_stats['vs_reels_per_spin'].append(len(vs_reels_this_spin))
                        vs_stats['vs_multipliers'].extend(vs_multipliers_this_spin)
                    
                    # For bonus/superbonus: each book entry is a complete feature
                    # The finalWin event contains the total win for that feature
                    for event in events:
                        if event.get("type") == "finalWin":
                            final_win = event.get("amount", 0) / 100.0  # Convert from cents to bet multiplier
                            vs_stats['feature_wins'].append(final_win)
                            break
                    
    except Exception as e:
        print(f"Warning: Error analyzing books for VS stats: {e}")
        import traceback
        traceback.print_exc()
    
    return vs_stats


def calculate_mode_statistics(config, mode_name: str):
    """Calculate comprehensive statistics for a game mode.
    Returns:
        dict with all statistics
    """
    cost = None
    for bm in config.bet_modes:
        if bm.get_name() == mode_name:
            cost = bm.get_cost()
            break
    
    if cost is None:
        return None
    
    # Get file paths
    book_name = f"books_{mode_name}.jsonl.zst"
    lookup_name = f"lookUpTable_{mode_name}_0.csv"
    book_file = os.path.join(config.publish_path, book_name)
    lut_file = os.path.join(config.publish_path, lookup_name)
    
    if not os.path.exists(book_file) or not os.path.exists(lut_file):
        return None
    
    # Calculate RTP and basic stats from LUT
    win_dist, lut_payouts, weights_range, min_win, max_win = verify_lookup_format(lut_file)
    rtp = calculate_rtp(win_dist, cost, weights_range)
    hit_rate = non_zero_hitrate(win_dist, weights_range)
    
    # Calculate average win when winning
    total_wins = sum(win * weight for win, weight in win_dist.items())
    total_weight = weights_range
    winning_weight = sum(weight for win, weight in win_dist.items() if win > 0)
    
    if winning_weight > 0:
        avg_win_when_winning = (total_wins / winning_weight) / cost
    else:
        avg_win_when_winning = 0.0
    
    # Analyze VS statistics from books
    vs_stats = analyze_books_for_vs_stats(book_file)
    
    # Calculate VS statistics
    vs_percentage = 0.0
    avg_vs_reels_per_spin = 0.0
    avg_vs_multiplier = 0.0
    
    if vs_stats['total_spins'] > 0:
        vs_percentage = (vs_stats['spins_with_vs'] / vs_stats['total_spins']) * 100.0
        
        if vs_stats['vs_reels_per_spin']:
            avg_vs_reels_per_spin = sum(vs_stats['vs_reels_per_spin']) / len(vs_stats['vs_reels_per_spin'])
        
        if vs_stats['vs_multipliers']:
            avg_vs_multiplier = sum(vs_stats['vs_multipliers']) / len(vs_stats['vs_multipliers'])
    
    # Calculate feature statistics for bonus modes
    avg_feature_win = 0.0
    num_features = 0
    
    if mode_name in ['bonus', 'superbonus']:
        # For bonus modes, each book entry is a feature (since it's a feature buy)
        # Use feature_wins if available, otherwise use payoutMultiplier from books
        if vs_stats['feature_wins']:
            num_features = len(vs_stats['feature_wins'])
            avg_feature_win = sum(vs_stats['feature_wins']) / len(vs_stats['feature_wins'])
        else:
            # Fallback: calculate from total RTP
            # In feature buy modes, each book entry = one feature
            num_features = vs_stats['total_spins']
            if num_features > 0:
                total_win = sum(win * weight for win, weight in win_dist.items()) / weights_range
                avg_feature_win = (total_win / cost) / num_features if num_features > 0 else 0.0
    
    return {
        'mode': mode_name,
        'cost': cost,
        'rtp': rtp,
        'hit_rate': hit_rate,
        'avg_win_when_winning': avg_win_when_winning,
        'total_spins': vs_stats['total_spins'],
        'vs_percentage': vs_percentage,
        'avg_vs_reels_per_spin': avg_vs_reels_per_spin,
        'avg_vs_multiplier': avg_vs_multiplier,
        'avg_feature_win': avg_feature_win,
        'num_features': num_features,
    }


def print_rtp_summary(config):
    """Print comprehensive RTP and statistics summary for all modes."""
    print("\n" + "="*80)
    print("GUNSLINGERS: DRAW! - RTP & STATISTICS SUMMARY")
    print("="*80 + "\n")
    
    for bet_mode in config.bet_modes:
        mode_name = bet_mode.get_name()
        stats = calculate_mode_statistics(config, mode_name)
        
        if stats is None:
            print(f"⚠️  Mode '{mode_name}': Statistics not available (files may not exist)")
            print()
            continue
        
        # Mode header
        mode_display_name = {
            'base': 'BASE GAME',
            'bonus': 'DRAW! YOUR WEAPON (BONUS)',
            'superbonus': 'SUPER DRAW! (SUPERBONUS)'
        }.get(mode_name, mode_name.upper())
        
        print(f"📊 {mode_display_name}")
        print(f"   Mode ID: {mode_name}")
        print(f"   Cost: {stats['cost']}x bet")
        print()
        
        # RTP and Win Statistics
        print(f"   RTP & Win Statistics:")
        print(f"   • Effective RTP: {stats['rtp']*100:.2f}% ({stats['rtp']:.4f})")
        print(f"   • Hit Rate (any win): {stats['hit_rate']*100:.2f}% ({stats['hit_rate']:.4f})")
        print(f"   • Average Win (when winning): {stats['avg_win_when_winning']:.2f}x bet")
        print(f"   • Total Spins Analyzed: {stats['total_spins']:,}")
        print()
        
        # VS Statistics
        print(f"   VS (DRAW!) Statistics:")
        print(f"   • Spins with VS: {stats['vs_percentage']:.2f}%")
        if stats['avg_vs_reels_per_spin'] > 0:
            print(f"   • Avg VS Reels per Spin (when VS appears): {stats['avg_vs_reels_per_spin']:.2f}")
        else:
            print(f"   • Avg VS Reels per Spin (when VS appears): N/A")
        if stats['avg_vs_multiplier'] > 0:
            print(f"   • Avg VS Multiplier (when VS appears): {stats['avg_vs_multiplier']:.2f}x")
        else:
            print(f"   • Avg VS Multiplier (when VS appears): N/A")
        print()
        
        # Feature Statistics (for bonus modes)
        if mode_name in ['bonus', 'superbonus']:
            print(f"   Feature Statistics:")
            if stats['num_features'] > 0:
                print(f"   • Avg Feature Win per Buy: {stats['avg_feature_win']:.2f}x bet")
                print(f"   • Number of Features Analyzed: {stats['num_features']:,}")
            else:
                print(f"   • Feature statistics: N/A")
            print()
        
        print("-"*80 + "\n")

