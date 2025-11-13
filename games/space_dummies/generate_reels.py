"""
Generate AAA-quality reel strips for Space Dummies.
Creates extensive reels with proper symbol distribution, premium clustering,
and strategic wild/scatter placement for high-volatility gameplay.
"""

import random
import csv
from typing import List, Dict

# Symbol definitions
LOW_SYMBOLS = ["s10", "sj", "sq", "sk", "sa"]
MID_SYMBOLS = ["sc1", "sc2", "sc3"]
PREMIUM_SYMBOLS = ["chip", "zog"]
SPECIAL_SYMBOLS = ["wild", "scatter"]

# Reel constraints: wilds only on reels 2-4 (index 1, 2, 3)
WILD_REELS = [1, 2, 3]  # 0-indexed
NO_WILD_REELS = [0, 4]  # Reels 1 and 5

def create_base_reel(num_stops: int, reel_index: int, is_bonus: bool = False) -> List[str]:
    """Create a single reel with proper symbol distribution."""
    reel = []
    
    # Base distribution weights (will be adjusted per reel)
    if reel_index in NO_WILD_REELS:
        # Reels 1 and 5: no wilds, higher scatter chance
        weights = {
            "low": 50,
            "mid": 25,
            "premium": 3,
            "scatter": 8,
            "wild": 0
        }
    elif reel_index in WILD_REELS:
        # Reels 2-4: can have wilds
        if is_bonus:
            weights = {
                "low": 35,
                "mid": 30,
                "premium": 5,
                "scatter": 5,
                "wild": 15  # Higher wild density in bonus
            }
        else:
            weights = {
                "low": 45,
                "mid": 25,
                "premium": 3,
                "scatter": 7,
                "wild": 10
            }
    else:
        weights = {
            "low": 50,
            "mid": 25,
            "premium": 3,
            "scatter": 7,
            "wild": 0
        }
    
    # Create weighted pool
    pool = []
    pool.extend(["low"] * weights["low"])
    pool.extend(["mid"] * weights["mid"])
    pool.extend(["premium"] * weights["premium"])
    pool.extend(["scatter"] * weights["scatter"])
    if weights["wild"] > 0:
        pool.extend(["wild"] * weights["wild"])
    
    # Generate reel with clustering
    for i in range(num_stops):
        if i < num_stops - 1 and random.random() < 0.15:  # 15% chance of clustering
            # Cluster with previous symbol
            if reel and reel[-1] not in SPECIAL_SYMBOLS:
                reel.append(reel[-1])
                continue
        
        symbol_type = random.choice(pool)
        
        if symbol_type == "low":
            reel.append(random.choice(LOW_SYMBOLS))
        elif symbol_type == "mid":
            reel.append(random.choice(MID_SYMBOLS))
        elif symbol_type == "premium":
            reel.append(random.choice(PREMIUM_SYMBOLS))
        elif symbol_type == "scatter":
            reel.append("scatter")
        elif symbol_type == "wild":
            reel.append("wild")
    
    return reel

def add_premium_clusters(reel: List[str], num_clusters: int = 3):
    """Add strategic premium symbol clusters for anticipation."""
    premium_symbols = PREMIUM_SYMBOLS + MID_SYMBOLS
    positions = sorted(random.sample(range(len(reel) - 1), min(num_clusters, len(reel) // 20)))
    
    for pos in positions:
        if random.random() < 0.7:  # 70% chance of 2-symbol cluster
            reel[pos] = random.choice(premium_symbols)
            reel[pos + 1] = reel[pos]
        else:  # 30% chance of 3-symbol cluster
            reel[pos] = random.choice(premium_symbols)
            reel[pos + 1] = reel[pos]
            if pos + 2 < len(reel):
                reel[pos + 2] = reel[pos]

def add_scatter_positions(reel: List[str], target_count: int):
    """Strategically place scatter symbols."""
    scatter_positions = sorted(random.sample(range(len(reel)), min(target_count, len(reel))))
    for pos in scatter_positions:
        reel[pos] = "scatter"

def create_reel_strip(name: str, num_stops: int, is_bonus: bool = False, 
                     remove_lows: bool = False, is_wincap: bool = False):
    """Create a complete 5-reel strip."""
    reels = []
    
    for reel_idx in range(5):
        reel = create_base_reel(num_stops, reel_idx, is_bonus)
        
        # Remove low symbols if needed (Hyperdrive)
        if remove_lows:
            reel = [s for s in reel if s not in LOW_SYMBOLS]
            # Fill gaps with mids/premiums
            while len(reel) < num_stops:
                reel.append(random.choice(MID_SYMBOLS + PREMIUM_SYMBOLS))
        
        # Add premium clusters (except for wincap which is deterministic)
        if not is_wincap:
            add_premium_clusters(reel, num_clusters=num_stops // 30)
        
        # Adjust scatter distribution
        if is_wincap:
            # Wincap: specific scatter placement for max win
            if reel_idx == 0:  # Reel 1
                reel[0] = "scatter"
            elif reel_idx == 4:  # Reel 5
                reel[0] = "scatter"
        else:
            scatter_count = num_stops // 25  # ~4% scatter density
            add_scatter_positions(reel, scatter_count)
        
        reels.append(reel)
    
    # Write to CSV (transposed format: each line is one stop across all reels)
    filename = f"reels/{name}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for stop in range(num_stops):
            row = [reels[reel_idx][stop] for reel_idx in range(5)]
            writer.writerow(row)
    
    print(f"Created {filename} with {num_stops} stops per reel")

if __name__ == "__main__":
    random.seed(42)  # Reproducible for testing
    
    # Base game: 350 stops per reel (AAA standard)
    create_reel_strip("BR0", num_stops=350, is_bonus=False)
    
    # Rocket Riot bonus: 300 stops, higher wild density
    create_reel_strip("RR0", num_stops=300, is_bonus=True, remove_lows=False)
    
    # Hyperdrive Havoc: 280 stops, no low symbols
    create_reel_strip("HD0", num_stops=280, is_bonus=True, remove_lows=True)
    
    # Wincap: 10 stops, deterministic max win setup
    create_reel_strip("WCAP", num_stops=10, is_bonus=True, is_wincap=True)
    
    print("\nAll reel strips generated successfully!")

