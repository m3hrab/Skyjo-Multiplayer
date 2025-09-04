# game/rules.py
import random
from .deck import Deck
from .board import Board
from .player import Player

class Rules:
    def __init__(self):
        self.deck = None
        self.discard_pile = []
        self.board = Board()
        self.drawn_card = None  # Card currently held by player
        self.game_message = ""

    def add_player(self, name):
        """Add a player to the game"""
        player = Player(name)
        self.board.add_player(player)

    def start_game(self):
        """Start a new game"""
        if len(self.board.players) < 2:
            return False
            
        # Create and shuffle deck
        self.deck = Deck()
        self.discard_pile = []
        
        # Deal 12 cards to each player
        self.deal_cards()
        
        # Create initial discard pile
        if not self.deck.is_empty():
            self.discard_pile.append(self.deck.draw_card())
        
        # Start the game
        self.board.start_game()
        self.game_message = f"{self.board.get_current_player().name}: Select 2 cards to flip"
        return True

    def deal_cards(self):
        """Deal 12 cards to each player in 3x4 grid"""
        for player in self.board.players:
            # Don't reset here - players should already be reset
            for i in range(3):
                for j in range(4):
                    if not self.deck.is_empty():
                        player.grid[i][j] = self.deck.draw_card()

    def handle_initial_card_selection(self, player_name, row, col):
        """Handle initial card selection phase"""
        if self.board.state != "select_initial_cards":
            return False
            
        current_player = self.board.get_current_player()
        if current_player.name != player_name:
            return False
            
        # Check if position is valid and not already revealed
        if (row < 0 or row >= 3 or col < 0 or col >= 4 or 
            current_player.revealed[row][col]):
            return False
            
        # Reveal the card
        current_player.reveal_card(row, col)
        
        # Check if player has selected 2 cards
        player_selected_count = sum(sum(row) for row in current_player.revealed)
        if player_selected_count == 2:
            # Move to next player or finish selection
            if self.board.current_player_index == len(self.board.players) - 1:
                # All players have selected, determine starting player
                starting_player_index = self.board.finish_initial_selection()
                self.game_message = f"{self.board.get_current_player().name}'s turn: Choose Draw or Discard"
            else:
                # Move to next player
                self.board.next_player()
                self.game_message = f"{self.board.get_current_player().name}: Select 2 cards to flip"
                
        return True

    def handle_draw_pile_action(self, player_name):
        """Handle drawing from draw pile"""
        if not self._is_valid_turn(player_name, "choose_pile"):
            return False
            
        if self.deck.is_empty():
            return False
            
        # Draw card
        self.drawn_card = self.deck.draw_card()
        self.board.phase = "decide_card"
        self.game_message = "Keep card or discard and flip one of yours?"
        return True

    def handle_discard_pile_action(self, player_name):
        """Handle taking from discard pile"""
        if not self._is_valid_turn(player_name, "choose_pile"):
            return False
            
        if not self.discard_pile:
            return False
            
        # Take discard card
        self.drawn_card = self.discard_pile.pop()
        self.board.phase = "swap_card"
        self.game_message = "Choose a card to swap"
        return True

    def handle_keep_card_action(self, player_name):
        """Handle keeping the drawn card"""
        if not self._is_valid_turn(player_name, "decide_card"):
            return False
            
        self.board.phase = "swap_card"
        self.game_message = "Choose a card to swap"
        return True

    def handle_discard_drawn_card_action(self, player_name):
        """Handle discarding the drawn card"""
        if not self._is_valid_turn(player_name, "decide_card"):
            return False
            
        if self.drawn_card is None:
            return False
            
        # Discard the drawn card
        self.discard_pile.append(self.drawn_card)
        self.drawn_card = None
        self.board.phase = "flip_card"
        self.game_message = "Flip one of your face-down cards"
        return True

    def handle_card_swap(self, player_name, row, col):
        """Handle swapping a card"""
        if not self._is_valid_turn(player_name, "swap_card"):
            return False
            
        current_player = self.board.get_current_player()
        
        # Check if position is valid
        if (row < 0 or row >= 3 or col < 0 or col >= 4 or 
            current_player.grid[row][col] is None):
            return False
            
        # Swap cards
        old_card = current_player.replace_card(row, col, self.drawn_card)
        self.discard_pile.append(old_card)
        self.drawn_card = None
        
        # Check for column triples
        removed_columns = current_player.check_all_columns()
        
        # Check if player revealed all cards
        if current_player.all_cards_revealed():
            self._trigger_round_end()
        else:
            self._end_turn()
            
        return True

    def handle_card_flip(self, player_name, row, col):
        """Handle flipping a face-down card"""
        if not self._is_valid_turn(player_name, "flip_card"):
            return False
            
        current_player = self.board.get_current_player()
        
        # Check if card can be flipped
        if (row < 0 or row >= 3 or col < 0 or col >= 4 or 
            current_player.revealed[row][col] or 
            current_player.grid[row][col] is None):
            return False
            
        # Flip card
        current_player.reveal_card(row, col)
        
        # Check for column triples
        removed_columns = current_player.check_all_columns()
        
        # Check if player revealed all cards
        if current_player.all_cards_revealed():
            self._trigger_round_end()
        else:
            self._end_turn()

        return True

    def _trigger_round_end(self):
        """Trigger the end of the round"""
        current_player = self.board.get_current_player()
        
        if self.board.state == "playing":
            # First player to reveal all cards
            self.board.trigger_round_end()
            if self.board.current_player_index < len(self.board.players):
                self.game_message = f"{current_player.name} revealed all cards. {self.board.get_current_player().name}'s last turn"
        elif self.board.state == "end_round":
            # Player in final round completed their turn
            self.board.complete_final_turn()
            if self.board.should_end_round():
                self._complete_round()
            else:
                self.board.next_player()
                self.game_message = f"{self.board.get_current_player().name}'s last turn"
            
        self.board.phase = "choose_pile"

    def _complete_round(self):
        """Complete the round and calculate scores"""
        self.board.end_round()
        
        # Generate score message
        score_messages = []
        for player in self.board.players:
            score_messages.append(f"{player.name}: {player.score}")
            
        self.game_message = " | ".join(score_messages)
        
        # Check if game should end
        if self.board.should_end_game():
            winners = self.board.end_game()
            if len(winners) == 1:
                self.game_message = f"Game Over! {winners[0].name} wins with {winners[0].total_score} points!"
            else:
                winner_names = [w.name for w in winners]
                self.game_message = f"Game Over! Tie between {', '.join(winner_names)} with {winners[0].total_score} points!"
        else:
            self.game_message += " | Click to start new round..."

    def start_new_round(self):
        """Start a new round"""
        if self.board.state == "round_end":
            # Store the trigger player before resetting
            trigger_player_index = self.board.trigger_player_index
            
            # Reset for new round
            self.deck = Deck()
            self.discard_pile = []
            self.drawn_card = None
            
            # Start new round (this resets players and sets up the round)
            self.board.start_new_round()
            
            # Deal new cards (after players are reset)
            self.deal_cards()
            
            # Create initial discard pile
            if not self.deck.is_empty():
                self.discard_pile.append(self.deck.draw_card())
            
            # Set appropriate message based on round type
            if self.board.round_number == 1:
                # First round: players need to select cards
                self.game_message = f"{self.board.get_current_player().name}: Select 2 cards to flip"
            else:
                # Subsequent rounds: trigger player starts immediately
                trigger_player_name = self.board.get_current_player().name
                self.game_message = f"{trigger_player_name}'s turn: Choose Draw or Discard"
            
            return True
        return False

    def _end_turn(self):
        """End current player's turn"""
        if self.board.state == "end_round":
            # In end round, mark player as completed
            self.board.complete_final_turn()
            if self.board.should_end_round():
                self._complete_round()
                return
                
        # Move to next player
        self.board.next_player()
        self.board.phase = "choose_pile"
        
        if self.board.state == "end_round":
            self.game_message = f"{self.board.get_current_player().name}'s last turn"
        else:
            self.game_message = f"{self.board.get_current_player().name}'s turn: Choose Draw or Discard"

    def _is_valid_turn(self, player_name, expected_phase):
        """Check if it's a valid turn for the player"""
        if self.board.state not in ["playing", "end_round"]:
            return False
            
        current_player = self.board.get_current_player()
        if current_player.name != player_name:
            return False
            
        if self.board.phase != expected_phase:
            return False
            
        return True

    def get_game_state_for_player(self, player_name):
        """Get game state from a specific player's perspective"""
        players_data = {}
        for player in self.board.players:
            players_data[player.name] = {
                "grid": player.grid,
                "revealed": player.revealed,
                "score": player.get_revealed_score(),  # Real-time score from revealed cards
                "total_score": player.total_score
            }
        
        return {
            "players": players_data,
            "board_info": {
                "state": self.board.state,
                "phase": self.board.phase,
                "current_player": self.board.current_player_index,
                "round_number": self.board.round_number
            },
            "deck_size": self.deck.cards_left() if self.deck else 0,
            "discard_size": len(self.discard_pile),
            "top_discard": self.discard_pile[-1] if self.discard_pile else None,
            "drawn_card": self.drawn_card,
            "message": self.game_message
        }

    def get_current_player_name(self):
        """Get the name of the current player"""
        current_player = self.board.get_current_player()
        return current_player.name if current_player else None
