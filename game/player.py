# game/player.py
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.grid = [[None for _ in range(4)] for _ in range(3)]  # 3x4 Raster
        self.revealed = [[False for _ in range(4)] for _ in range(3)]
        self.ready = False
        self.score = 0  # Current round score
        self.total_score = 0  # Total score across all rounds
        self.has_completed_final_turn = False  # For end-round tracking

    def place_card(self, row, col, value):
        self.grid[row][col] = value

    def reveal_card(self, row, col):
        self.revealed[row][col] = True

    def replace_card(self, row, col, new_value):
        old_value = self.grid[row][col]
        self.grid[row][col] = new_value
        self.revealed[row][col] = True
        return old_value

    def reveal_random(self):
        unrevealed = [(r, c) for r in range(3) for c in range(4) 
                     if not self.revealed[r][c] and self.grid[r][c] is not None]
        if unrevealed:
            r, c = random.choice(unrevealed)
            self.revealed[r][c] = True
            return r, c
        return None

    def get_current_score(self):
        """Calculate total score for current round (all cards, including unrevealed)"""
        return sum(
            self.grid[r][c] if self.grid[r][c] is not None else 0
            for r in range(3)
            for c in range(4)
        )

    def get_revealed_score(self):
        """Calculate real-time score from only revealed cards"""
        score = 0
        for r in range(3):
            for c in range(4):
                if self.revealed[r][c] and self.grid[r][c] is not None:
                    score += self.grid[r][c]
        return score

    def get_initial_score(self):
        """Calculate score from initially revealed cards"""
        score = 0
        for r in range(3):
            for c in range(4):
                if self.revealed[r][c] and self.grid[r][c] is not None:
                    score += self.grid[r][c]
        return score

    def all_cards_revealed(self):
        """Check if all remaining cards are revealed"""
        return all(self.revealed[r][c] or self.grid[r][c] is None 
                  for r in range(3) for c in range(4))

    def check_column_triple(self, col):
        """Check if a specific column has three identical revealed cards"""
        if col < 0 or col >= 4:
            return False
            
        col_vals = [self.grid[r][col] for r in range(3)]
        col_revealed = [self.revealed[r][col] for r in range(3)]
        
        # Check if all 3 cards in column are revealed and identical
        if (all(col_revealed) and col_vals[0] is not None and 
            col_vals[0] == col_vals[1] == col_vals[2]):
            # Remove the column
            for r in range(3):
                self.grid[r][col] = None
                self.revealed[r][col] = False
            return True
        return False

    def check_all_columns(self):
        """Check all columns for triples and remove them"""
        removed_columns = []
        for col in range(4):
            if self.check_column_triple(col):
                removed_columns.append(col)
        return removed_columns

    def reveal_all_cards(self):
        """Reveal all remaining cards (used at round end)"""
        for r in range(3):
            for c in range(4):
                if self.grid[r][c] is not None:
                    self.revealed[r][c] = True

    def reset_for_new_round(self):
        """Reset player state for a new round"""
        self.grid = [[None for _ in range(4)] for _ in range(3)]
        self.revealed = [[False for _ in range(4)] for _ in range(3)]
        self.score = 0
        self.has_completed_final_turn = False