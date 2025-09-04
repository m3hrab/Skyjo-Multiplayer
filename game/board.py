# game/board.py
class Board:
    def __init__(self):
        self.players = []
        self.current_player_index = 0
        self.state = "waiting"  # States: "waiting", "select_initial_cards", "playing", "end_round", "round_end", "game_over"
        self.phase = None  # Phases: "choose_pile", "decide_card", "swap_card", "flip_card"
        self.round_number = 0
        self.trigger_player_index = None  # Player who triggered round end
        self.final_turn_players = []  # Players who have completed their final turn
        self.selected_cards_count = 0  # For initial card selection

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        if len(self.players) >= 2:
            self.state = "select_initial_cards"
            self.current_player_index = 0
            self.round_number = 1
            self.selected_cards_count = 0
            return True
        return False

    def start_new_round(self):
        """Start a new round"""
        self.round_number += 1
        
        # For the first round, use card selection to determine starting player
        if self.round_number == 1:
            self.state = "select_initial_cards"
            self.current_player_index = 0
            self.selected_cards_count = 0
        else:
            # For subsequent rounds, the trigger player starts immediately
            self.state = "playing"
            self.current_player_index = self.trigger_player_index if self.trigger_player_index is not None else 0
            self.phase = "choose_pile"
        
        self.trigger_player_index = None
        self.final_turn_players = []
        
        # Reset all players for new round
        for player in self.players:
            player.reset_for_new_round()

    def finish_initial_selection(self):
        """Complete initial card selection and determine starting player"""
        if self.state == "select_initial_cards":
            # Find player with highest initial score
            initial_scores = [player.get_initial_score() for player in self.players]
            max_score = max(initial_scores)
            starting_player = initial_scores.index(max_score)
            
            self.current_player_index = starting_player
            self.state = "playing"
            self.phase = "choose_pile"
            return starting_player
        return None

    def next_player(self):
        """Move to next player"""
        if self.state == "end_round":
            # During end round, skip players who already completed final turn
            original_player = self.current_player_index
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            
            # Skip players who already completed their final turn
            while (self.current_player_index in self.final_turn_players and 
                   len(self.final_turn_players) < len(self.players)):
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                
                # Prevent infinite loop
                if self.current_player_index == original_player:
                    break
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_current_player(self):
        if self.players:
            return self.players[self.current_player_index]
        return None

    def all_players(self):
        return self.players

    def has_game_started(self):
        return self.state in ["select_initial_cards", "playing", "end_round"]

    def trigger_round_end(self):
        """Trigger the end of round when a player reveals all cards"""
        if self.state == "playing":
            self.state = "end_round"
            self.trigger_player_index = self.current_player_index
            self.final_turn_players = [self.current_player_index]
            self.next_player()
            self.phase = "choose_pile"

    def complete_final_turn(self):
        """Mark current player as having completed their final turn"""
        if self.current_player_index not in self.final_turn_players:
            self.final_turn_players.append(self.current_player_index)

    def should_end_round(self):
        """Check if round should end (all players completed final turn)"""
        return (self.state == "end_round" and 
                len(self.final_turn_players) == len(self.players))

    def end_round(self):
        """End the current round and calculate scores"""
        if self.should_end_round():
            # Reveal all cards for all players
            for player in self.players:
                player.reveal_all_cards()
            
            # Calculate scores
            trigger_player = self.players[self.trigger_player_index]
            scores = [player.get_current_score() for player in self.players]
            min_score = min(scores)
            
            # Apply scoring rules
            for i, player in enumerate(self.players):
                player.score = scores[i]
                
                # Double trigger player's score if they don't have the lowest score
                if i == self.trigger_player_index and player.score > min_score:
                    player.score *= 2
                
                player.total_score += player.score
            
            self.state = "round_end"
            return True
        return False

    def should_end_game(self):
        """Check if game should end (any player >= 100 points)"""
        return any(player.total_score >= 100 for player in self.players)

    def end_game(self):
        """End the game and determine winner"""
        self.state = "game_over"
        min_total = min(player.total_score for player in self.players)
        winners = [player for player in self.players if player.total_score == min_total]
        return winners

    def reset_round(self):
        """Reset for a new round"""
        if self.should_end_game():
            self.end_game()
        else:
            self.start_new_round()

    def get_game_info(self):
        """Get current game information"""
        return {
            "state": self.state,
            "phase": self.phase,
            "round_number": self.round_number,
            "current_player": self.current_player_index,
            "trigger_player": self.trigger_player_index,
            "final_turn_players": self.final_turn_players.copy(),
            "selected_cards_count": self.selected_cards_count
        }
