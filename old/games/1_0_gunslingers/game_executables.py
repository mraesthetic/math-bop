import random
from game_calculations import GameCalculations
from src.calculations.lines import Lines
from src.calculations.statistics import get_random_outcome


class GameExecutables(GameCalculations):

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Override draw_board to inject VS symbol in superbonus mode before reveal."""
        # Call parent draw_board but don't emit reveal yet
        super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
        
        # SUPER DRAW! mode: Force exactly ONE VS reel per spin (before reveal event)
        # Only force VS during free spins, NOT on the basegame trigger spin
        # Check both betmode == "superbonus" (feature buy) and is_superbonus_from_scatter (4-scatter trigger)
        is_superbonus = (
            (hasattr(self, 'betmode') and self.betmode == "superbonus") or
            (hasattr(self, 'is_superbonus_from_scatter') and getattr(self, 'is_superbonus_from_scatter', False))
        )
        if is_superbonus and self.gametype == self.config.freegame_type:
            # Count how many reels already have VS symbols (from natural landing)
            vs_reels = []
            for reel_idx, reel in enumerate(self.board):
                for symbol in reel:
                    if symbol.name == "VS":
                        vs_reels.append(reel_idx)
                        break  # Only count each reel once
            
            # Ensure exactly ONE reel has VS (forced if none exist naturally)
            if len(vs_reels) == 0:
                # No VS found: force exactly one VS on a random reel
                forced_reel_idx = random.randint(0, len(self.board) - 1)
                forced_row_idx = random.randint(0, len(self.board[forced_reel_idx]) - 1)
                
                # Track the original symbol before replacing with VS
                original_symbol = self.board[forced_reel_idx][forced_row_idx]
                original_symbol_name = original_symbol.name if original_symbol else None
                
                # Create the VS symbol
                vs_symbol = self.create_symbol("VS")
                
                # If the original symbol was a scatter, set underlyingSymbol attribute
                if original_symbol_name == "S":
                    vs_symbol.assign_attribute({"underlyingSymbol": "S"})
                
                # Replace the symbol with VS
                self.board[forced_reel_idx][forced_row_idx] = vs_symbol
            elif len(vs_reels) > 1:
                # Multiple VS reels found: keep only the first one, remove VS from others
                # Keep the first VS reel, remove VS from all other reels
                for reel_idx in vs_reels[1:]:
                    # Remove VS symbols from this reel, replace with a low symbol
                    for row_idx in range(len(self.board[reel_idx])):
                        if self.board[reel_idx][row_idx].name == "VS":
                            self.board[reel_idx][row_idx] = self.create_symbol("L1")
            # If exactly one VS reel exists, do nothing (already correct)
        
        # Assign multipliers to ALL VS symbols BEFORE reveal event (for frontend display)
        # This ensures the reveal event includes VS symbols with their multipliers
        if not hasattr(self, 'vs_reel_multipliers'):
            self.vs_reel_multipliers = {}
        else:
            self.vs_reel_multipliers = {}  # Reset for each spin
        
        # Find all reels with VS symbols and assign multipliers
        for reel_idx, reel in enumerate(self.board):
            has_vs = False
            for symbol in reel:
                if symbol.name == "VS":
                    has_vs = True
                    break
            
            if has_vs:
                # Get multiplier for this VS reel from distribution
                # Use superbonus-specific multipliers if in superbonus mode, otherwise use regular
                is_superbonus = (
                    (hasattr(self, 'betmode') and self.betmode == "superbonus") or
                    (hasattr(self, 'is_superbonus_from_scatter') and getattr(self, 'is_superbonus_from_scatter', False))
                )
                if is_superbonus:
                    vs_mult_dist = getattr(self.config, 'superbonus_vs_multipliers', {2: 500, 3: 350, 4: 80, 5: 40, 8: 20, 10: 10})
                else:
                    vs_mult_dist = self.config.padding_symbol_values.get("VS", {}).get("multiplier", {})
                
                # Get the multiplier for this reel
                if not vs_mult_dist:
                    reel_multiplier = 1
                else:
                    vs_mult_dist_copy = dict(vs_mult_dist)
                    reel_multiplier = get_random_outcome(vs_mult_dist_copy)
                
                # Store multiplier for this reel (for later use in win calculation)
                self.vs_reel_multipliers[reel_idx] = reel_multiplier
                
                # Assign multiplier attribute to ALL VS symbols on this reel (for frontend display)
                for row_idx in range(len(reel)):
                    if reel[row_idx].name == "VS":
                        reel[row_idx].assign_attribute({"multiplier": reel_multiplier})
        
        # Now emit the reveal event with the (possibly modified) board
        # The VS symbols now have multiplier attributes attached for the frontend
        if emit_event:
            from src.events.events import reveal_event
            reveal_event(self)

    def ensure_superbonus_vs(self):
        """SUPER DRAW! mode: Ensure at least one VS symbol lands on the board.
        This is called BEFORE evaluation so the VS symbol appears visually.
        """
        if not (hasattr(self, 'betmode') and self.betmode == "superbonus"):
            return
        
        # Check if any VS symbols already exist on the board
        has_vs = False
        for reel in self.board:
            for symbol in reel:
                if symbol.name == "VS":
                    has_vs = True
                    break
            if has_vs:
                break
        
        # If no VS found, place one on a random reel at a random row
        if not has_vs:
            forced_reel_idx = random.randint(0, len(self.board) - 1)
            forced_row_idx = random.randint(0, len(self.board[forced_reel_idx]) - 1)
            
            # Place VS symbol on the board
            self.board[forced_reel_idx][forced_row_idx] = self.create_symbol("VS")

    def expand_vs_reels(self):
        """Expand VS reels to wilds with multipliers.
        For each reel containing at least one VS symbol:
        - Expand entire reel to wilds (multipliers already assigned in draw_board before reveal)
        - Use the multipliers already stored in self.vs_reel_multipliers
        - Track VS reel multipliers for line win calculation
        """
        # VS multipliers are already assigned in draw_board() before reveal event
        # We just need to expand VS reels to wilds for evaluation
        # The multipliers are already stored in self.vs_reel_multipliers
        
        # Find all reels with VS symbols and expand them to wilds
        for reel_idx, reel in enumerate(self.board):
            has_vs = False
            for symbol in reel:
                if symbol.name == "VS":
                    has_vs = True
                    break
            
            if has_vs:
                # Expand entire reel to wilds
                # Note: Multipliers are already assigned to VS symbols in draw_board()
                # and stored in self.vs_reel_multipliers for win calculation
                for row_idx in range(len(reel)):
                    self.board[reel_idx][row_idx] = self.create_symbol("W")

    def calculate_vs_line_multiplier(self, positions):
        """Calculate the product of VS reel multipliers for a winning line.
        Args:
            positions: List of position dicts with 'reel' and 'row' keys
        Returns:
            Product of multipliers from unique VS reels used in this line
        """
        if not hasattr(self, 'vs_reel_multipliers') or not self.vs_reel_multipliers:
            return 1
        
        # Get unique reels used in this line
        reels_in_line = set(pos["reel"] for pos in positions)
        
        # Multiply multipliers from VS reels used in this line
        combined_mult = 1
        for reel_idx in reels_in_line:
            if reel_idx in self.vs_reel_multipliers:
                combined_mult *= self.vs_reel_multipliers[reel_idx]
        
        # Cap at 500× (increased from 250× to allow max win of 10,000× bet)
        if combined_mult > 500:
            combined_mult = 500
        
        return combined_mult

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""
        # Expand VS reels before evaluation
        # Note: VS symbol injection for superbonus is now handled in draw_board() before reveal
        self.expand_vs_reels()
        
        # Evaluate line wins (using "symbol" method to get base win)
        self.win_data = Lines.get_lines(
            self.board, 
            self.config, 
            global_multiplier=1,  # Will apply VS multipliers separately
            multiplier_method="symbol"
        )
        
        # Apply VS reel multipliers to each win
        for win in self.win_data["wins"]:
            vs_mult = self.calculate_vs_line_multiplier(win["positions"])
            if vs_mult > 1:
                # Apply VS multiplier to the win
                win["win"] = round(win["win"] * vs_mult, 2)
                # Update meta information
                original_mult = win["meta"].get("multiplier", 1)
                win["meta"]["multiplier"] = round(original_mult * vs_mult, 2)
                win["meta"]["vsMultiplier"] = vs_mult
        
        # Recalculate totalWin after applying VS multipliers
        self.win_data["totalWin"] = round(sum(w["win"] for w in self.win_data["wins"]), 2)
        
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)
