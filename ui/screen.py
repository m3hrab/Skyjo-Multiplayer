import pygame
from ui.buttons import Button

# Constants
CARD_WIDTH = 60
CARD_HEIGHT = 90
CARD_MARGIN = 5
GRID_ROWS = 3
GRID_COLS = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)

def load_card_images():
    """Load card images from assets folder"""
    images = {}
    card_values = ["-2", "-1", "0"] + [str(i) for i in range(1, 13)]
    
    for val in card_values:
        try:
            img = pygame.image.load(f"assets/cards/card_{val}.png")
            images[val] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
        except:
            print(f"[WARNING] Card {val} not found!")
    
    # Add card back image
    try:
        img = pygame.image.load("assets/cards/card_back.png")
        images["back"] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
    except:
        print("[WARNING] Card back not found!")
    
    return images

def draw_player_grid(screen, player_name, player_data, x, y, card_images, is_current_player=False, is_current_turn=False):
    """Draw a single player's grid with turn highlighting"""
    font = pygame.font.SysFont(None, 24)
    
    # Calculate grid dimensions
    grid_width = GRID_COLS * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    grid_height = GRID_ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    
    # Add padding around the grid
    padding = 15
    total_width = grid_width + 2 * padding
    total_height = grid_height + 2 * padding + 50  # Extra space for name and score
    
    # Draw turn highlighting background
    if is_current_turn:
        # Draw glowing background for current turn
        highlight_rect = pygame.Rect(x - padding, y - 50, total_width, total_height)
        
        # Draw multiple layers for glow effect
        for i in range(3):
            glow_color = (255, 215, 0, 100 - i * 30)  # Gold with decreasing alpha
            glow_rect = pygame.Rect(
                highlight_rect.x - i * 2, 
                highlight_rect.y - i * 2, 
                highlight_rect.width + i * 4, 
                highlight_rect.height + i * 4
            )
            pygame.draw.rect(screen, GOLD, glow_rect, 3)
        
        # Draw main background
        pygame.draw.rect(screen, (255, 255, 200), highlight_rect)
        pygame.draw.rect(screen, GOLD, highlight_rect, 4)
    
    # Draw player name with turn indication
    name_color = GOLD if is_current_turn else (YELLOW if is_current_player else WHITE)
    name_prefix = ">>> " if is_current_turn else ""
    name_text = font.render(f"{name_prefix}{player_name}", True, name_color)
    screen.blit(name_text, (x, y - 30))
    
    # Draw score
    score = player_data.get("score", 0)
    total_score = player_data.get("total_score", 0)
    score_text = f"Score: {score} | Total: {total_score}"
    score_color = GOLD if is_current_turn else LIGHT_GRAY
    score_surface = font.render(score_text, True, score_color)
    screen.blit(score_surface, (x, y - 10))
    
    # Draw grid
    grid = player_data.get("grid", [])
    revealed = player_data.get("revealed", [])
    
    card_rects = {}
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            card_x = x + col * (CARD_WIDTH + CARD_MARGIN)
            card_y = y + row * (CARD_HEIGHT + CARD_MARGIN)
            
            # Always draw cards for the full 3x4 grid
            card_value = None
            is_revealed = False
            
            # Get card value if it exists
            if (row < len(grid) and col < len(grid[row])):
                card_value = grid[row][col]
            
            # Get revealed status if it exists
            if (row < len(revealed) and col < len(revealed[row])):
                is_revealed = revealed[row][col]
            
            if card_value is None:
                # Empty slot (removed card) - draw gray rectangle
                pygame.draw.rect(screen, GRAY, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))
            elif is_revealed:
                # Show card value
                draw_card_image(screen, card_images, card_value, card_x, card_y)
            else:
                # Show card back for unrevealed cards
                draw_card_back(screen, card_images, card_x, card_y)
            
            # Add subtle highlight border for current turn player's cards
            if is_current_turn and card_value is not None:
                pygame.draw.rect(screen, GOLD, (card_x - 1, card_y - 1, CARD_WIDTH + 2, CARD_HEIGHT + 2), 1)
            
            # Store card rect for click detection (only for current player)
            if is_current_player and card_value is not None:
                card_rects[(row, col)] = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
    
    return card_rects

def draw_card_image(screen, card_images, card_value, x, y):
    """Draw a card image or fallback rectangle"""
    val_str = str(card_value)
    if val_str in card_images:
        screen.blit(card_images[val_str], (x, y))
    else:
        # Fallback rectangle with value
        pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        font = pygame.font.SysFont(None, 16)
        text = font.render(val_str, True, BLACK)
        text_rect = text.get_rect(center=(x + CARD_WIDTH//2, y + CARD_HEIGHT//2))
        screen.blit(text, text_rect)

def draw_card_back(screen, card_images, x, y):
    """Draw card back or fallback rectangle"""
    if "back" in card_images:
        screen.blit(card_images["back"], (x, y))
    else:
        # Fallback rectangle
        pygame.draw.rect(screen, BLUE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

def draw_player_grids(screen, players_data, self_name, card_images, current_player_name=None):
    """Draw all player grids with improved layout and turn highlighting"""
    if not players_data:
        return {}
    
    screen_width, screen_height = screen.get_size()
    num_players = len(players_data)
    
    # Calculate grid dimensions
    grid_width = GRID_COLS * (CARD_WIDTH + CARD_MARGIN) - CARD_MARGIN
    grid_height = GRID_ROWS * (CARD_HEIGHT + CARD_MARGIN) - CARD_MARGIN
    padding = 15
    total_grid_width = grid_width + 2 * padding
    total_grid_height = grid_height + 2 * padding + 50  # Extra space for name and score
    
    # Calculate layout based on number of players
    if num_players <= 2:
        # Two players side by side
        spacing = 50
        total_width = 2 * total_grid_width + spacing
        start_x = (screen_width - total_width) // 2
        positions = [
            (start_x, 120),
            (start_x + total_grid_width + spacing, 120)
        ]
    elif num_players == 3:
        # Three players in a single row
        spacing = 30
        total_width = 3 * total_grid_width + 2 * spacing
        
        # Check if we need to scale down
        if total_width > screen_width - 40:
            # Scale down slightly
            scale_factor = (screen_width - 40) / total_width
            scaled_width = int(total_grid_width * scale_factor)
            spacing = int(spacing * scale_factor)
            total_width = 3 * scaled_width + 2 * spacing
            start_x = (screen_width - total_width) // 2
            positions = [
                (start_x, 120),
                (start_x + scaled_width + spacing, 120),
                (start_x + 2 * (scaled_width + spacing), 120)
            ]
        else:
            start_x = (screen_width - total_width) // 2
            positions = [
                (start_x, 120),
                (start_x + total_grid_width + spacing, 120),
                (start_x + 2 * (total_grid_width + spacing), 120)
            ]
    else:  # 4 players
        # Four players in a single row
        spacing = 20
        total_width = 4 * total_grid_width + 3 * spacing
        
        # Check if we need to scale down
        if total_width > screen_width - 40:
            # Scale down to fit
            scale_factor = (screen_width - 40) / total_width
            scaled_width = int(total_grid_width * scale_factor)
            spacing = int(spacing * scale_factor)
            total_width = 4 * scaled_width + 3 * spacing
            start_x = (screen_width - total_width) // 2
            positions = [
                (start_x, 120),
                (start_x + scaled_width + spacing, 120),
                (start_x + 2 * (scaled_width + spacing), 120),
                (start_x + 3 * (scaled_width + spacing), 120)
            ]
        else:
            start_x = (screen_width - total_width) // 2
            positions = [
                (start_x, 120),
                (start_x + total_grid_width + spacing, 120),
                (start_x + 2 * (total_grid_width + spacing), 120),
                (start_x + 3 * (total_grid_width + spacing), 120)
            ]
    
    all_card_rects = {}
    
    # Draw each player's grid
    for idx, (player_name, player_data) in enumerate(players_data.items()):
        if idx < len(positions):
            x, y = positions[idx]
            is_current = (player_name == self_name)
            is_current_turn = (player_name == current_player_name)
            
            card_rects = draw_player_grid(
                screen, player_name, player_data, x, y, card_images, 
                is_current_player=is_current, is_current_turn=is_current_turn
            )
            
            if is_current:
                all_card_rects.update(card_rects)
    
    return all_card_rects

def get_clicked_card(pos, card_rects):
    """Get the card position that was clicked"""
    for (row, col), rect in card_rects.items():
        if rect.collidepoint(pos):
            return (row, col)
    return None

def draw_game_info(screen, game_state, player_name):
    """Draw basic game information"""
    font = pygame.font.SysFont(None, 24)
    
    board_info = game_state.get('board_info', {})
    message = game_state.get('message', '')
    
    # Get current player info
    current_player_index = board_info.get('current_player', -1)
    players = list(game_state.get('players', {}).keys())
    current_player_name = players[current_player_index] if 0 <= current_player_index < len(players) else ""
    
    state = board_info.get('state', '')
    phase = board_info.get('phase', '')
    round_number = board_info.get('round_number', 1)
    
    # Draw basic info at top
    info_text = f"Round {round_number} | Current Player: {current_player_name}"
    info_surface = font.render(info_text, True, WHITE)
    screen.blit(info_surface, (10, 10))
    
    # Draw state info
    state_text = f"State: {state} | Phase: {phase}"
    state_surface = font.render(state_text, True, LIGHT_GRAY)
    screen.blit(state_surface, (10, 35))
    
    # Draw pile info
    deck_size = game_state.get('deck_size', 0)
    discard_size = game_state.get('discard_size', 0)
    pile_text = f"Deck: {deck_size} | Discard: {discard_size}"
    pile_surface = font.render(pile_text, True, LIGHT_GRAY)
    screen.blit(pile_surface, (10, 60))
    
    # Draw message at bottom
    if message:
        screen_height = screen.get_size()[1]
        message_surface = font.render(message, True, YELLOW)
        screen.blit(message_surface, (10, screen_height - 30))

def draw_held_card(screen, game_state, card_images):
    """Draw the held card visually"""
    drawn_card = game_state.get('drawn_card')
    if drawn_card is not None:
        # Position the held card in the top-right area
        screen_width = screen.get_size()[0]
        held_x = screen_width - CARD_WIDTH - 20
        held_y = 10
        
        # Draw the held card
        draw_card_image(screen, card_images, drawn_card, held_x, held_y)
        
        # Draw label
        font = pygame.font.SysFont(None, 16)
        label = font.render("HELD CARD", True, YELLOW)
        screen.blit(label, (held_x + 5, held_y + CARD_HEIGHT + 5))

def draw_center_area(screen, game_state, card_images):
    """Draw the center area with deck and discard pile"""
    screen_width, screen_height = screen.get_size()
    
    # Position center area below the player grids
    center_x = screen_width // 2
    center_y = screen_height - 180  # Moved up to give more space for buttons
    
    # Draw deck
    deck_x = center_x - CARD_WIDTH - 20
    deck_y = center_y
    
    deck_size = game_state.get('deck_size', 0)
    if deck_size > 0:
        draw_card_back(screen, card_images, deck_x, deck_y)
        font = pygame.font.SysFont(None, 16)
        deck_label = font.render("DECK", True, WHITE)
        screen.blit(deck_label, (deck_x + 5, deck_y - 20))
        
        # Draw deck size
        size_text = font.render(f"({deck_size})", True, WHITE)
        screen.blit(size_text, (deck_x + 5, deck_y + CARD_HEIGHT + 5))
    
    # Draw discard pile
    discard_x = center_x + 20
    discard_y = center_y
    
    top_discard = game_state.get('top_discard')
    if top_discard is not None:
        draw_card_image(screen, card_images, top_discard, discard_x, discard_y)
        font = pygame.font.SysFont(None, 16)
        discard_label = font.render("DISCARD", True, WHITE)
        screen.blit(discard_label, (discard_x + 5, discard_y - 20))
        
        # Draw discard size
        discard_size = game_state.get('discard_size', 0)
        size_text = font.render(f"({discard_size})", True, WHITE)
        screen.blit(size_text, (discard_x + 5, discard_y + CARD_HEIGHT + 5))

def draw_game_over_screen(screen, game_state):
    """Draw simple game over screen"""
    screen.fill(BLACK)
    
    font = pygame.font.SysFont(None, 48)
    screen_width, screen_height = screen.get_size()
    
    # Draw title
    title_text = font.render("GAME OVER", True, WHITE)
    title_rect = title_text.get_rect(center=(screen_width // 2, 100))
    screen.blit(title_text, title_rect)
    
    # Draw final scores
    players_data = game_state.get('players', {})
    sorted_players = sorted(players_data.items(), key=lambda x: x[1].get('total_score', 0))
    
    if sorted_players:
        winner_name = sorted_players[0][0]
        winner_score = sorted_players[0][1].get('total_score', 0)
        
        winner_text = f"{winner_name} wins with {winner_score} points!"
        winner_surface = font.render(winner_text, True, GREEN)
        winner_rect = winner_surface.get_rect(center=(screen_width // 2, 200))
        screen.blit(winner_surface, winner_rect)
    
    # Draw instruction
    instruction_text = "Press ESC to exit"
    instruction_surface = font.render(instruction_text, True, WHITE)
    instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height - 50))
    screen.blit(instruction_surface, instruction_rect)

# Legacy functions for compatibility
def handle_scroll_click(pos):
    """Legacy function - no scrolling in basic version"""
    return False

def draw_scroll_buttons(screen):
    """Legacy function - no scrolling in basic version"""
    pass

def draw_status_bar(screen, current_player, self_name):
    """Legacy function - functionality moved to draw_game_info"""
    pass
