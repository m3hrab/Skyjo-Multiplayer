import socket
import threading
import pygame
import sys
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.buttons import Button
from ui.screen import (
    draw_player_grids, get_clicked_card, load_card_images, 
    draw_game_info, draw_center_area, draw_game_over_screen, draw_held_card
)

HOST = 'localhost'
PORT = 12345
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Game state variables
deck_images = load_card_images()
player_name = ""
game_state = {}
buttons = []
card_rects = {}

def gui_register_player():
    """Handle player registration GUI"""
    global player_name
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Skyjo - Player Registration")
    font = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()

    input_box = pygame.Rect(50, 200, 300, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''

    # Buttons for player count selection
    button_font = pygame.font.SysFont(None, 36)
    player_count_buttons = {
        2: pygame.Rect(50, 100, 80, 40),
        3: pygame.Rect(150, 100, 80, 40),
        4: pygame.Rect(250, 100, 80, 40),
    }

    # Get initial message from server
    expecting = client.recv(1024).decode()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle player count selection
                if expecting == "choose_players":
                    for count, rect in player_count_buttons.items():
                        if rect.collidepoint(event.pos):
                            client.sendall(str(count).encode())
                            expecting = "enter_name"
                            break

                # Handle name input box
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.strip():
                    player_name = text.strip()
                    client.sendall(player_name.encode())
                    return
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        screen.fill((30, 30, 30))

        # Draw player count selection
        if expecting == "choose_players":
            label = font.render("Choose number of players:", True, (255, 255, 255))
            screen.blit(label, (50, 50))
            for count, rect in player_count_buttons.items():
                pygame.draw.rect(screen, (0, 128, 0), rect)
                txt = button_font.render(str(count), True, (255, 255, 255))
                screen.blit(txt, (rect.x + 20, rect.y + 5))

        # Draw name input
        if expecting == "enter_name":
            label = font.render("Enter your name:", True, (255, 255, 255))
            screen.blit(label, (50, 160))
            txt_surface = font.render(text, True, color)
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

def receive_data():
    """Receive game state updates from server"""
    global game_state
    while True:
        try:
            data = client.recv(4096).decode()
            if data:
                # Handle multiple JSON messages in one packet
                messages = data.strip().split('\n')
                for message in messages:
                    if message:
                        try:
                            game_state = json.loads(message)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error receiving data from server: {e}")
            break

def setup_buttons(screen):
    """Setup UI buttons based on current game state"""
    global buttons
    buttons = []
    
    if not game_state:
        return
    
    board_info = game_state.get('board_info', {})
    current_player_index = board_info.get('current_player', -1)
    state = board_info.get('state', '')
    phase = board_info.get('phase', '')
    
    # Get current player name
    players = list(game_state.get('players', {}).keys())
    current_player_name = players[current_player_index] if 0 <= current_player_index < len(players) else ""
    
    # Only show buttons if it's the player's turn
    if current_player_name != player_name:
        return
    
    screen_width, screen_height = screen.get_size()
    button_width = 120
    button_height = 35
    spacing = 10
    y = screen_height - button_height - 20
    
    # Buttons based on game state and phase
    if state == "playing" or state == "end_round":
        if phase == "choose_pile":
            # Choose between draw pile and discard pile
            buttons.append(Button(50, y, button_width, button_height, "Draw Deck", 
                                lambda: send_action("draw_from_deck")))
            buttons.append(Button(50 + button_width + spacing, y, button_width, button_height, "Take Discard", 
                                lambda: send_action("draw_from_discard")))
        
        elif phase == "decide_card":
            # Decide what to do with drawn card
            buttons.append(Button(50, y, button_width, button_height, "Keep Card", 
                                lambda: send_action("keep_card")))
            buttons.append(Button(50 + button_width + spacing, y, button_width, button_height, "Discard Card", 
                                lambda: send_action("discard_card")))
    
    elif state == "round_end":
        # Option to start new round
        buttons.append(Button(50, y, button_width * 2, button_height, "Start New Round", 
                            lambda: send_action("start_new_round")))

def send_action(action, row=None, col=None):
    """Send action to server"""
    action_data = {'action': action}
    if row is not None:
        action_data['row'] = row
    if col is not None:
        action_data['col'] = col
    
    try:
        client.sendall(json.dumps(action_data).encode())
    except Exception as e:
        print(f"Error sending action: {e}")

def handle_card_click(row, col):
    """Handle clicking on a card"""
    if not game_state:
        return
    
    board_info = game_state.get('board_info', {})
    current_player_index = board_info.get('current_player', -1)
    state = board_info.get('state', '')
    phase = board_info.get('phase', '')
    
    # Get current player name
    players = list(game_state.get('players', {}).keys())
    current_player_name = players[current_player_index] if 0 <= current_player_index < len(players) else ""
    
    # Only handle clicks if it's the player's turn
    if current_player_name != player_name:
        return
    
    # Handle different phases
    if state == "select_initial_cards":
        send_action("select_initial_card", row, col)
    elif phase == "swap_card":
        send_action("swap_card", row, col)
    elif phase == "flip_card":
        send_action("flip_card", row, col)

def is_game_over():
    """Check if the game is over"""
    if not game_state:
        return False
    
    board_info = game_state.get('board_info', {})
    return board_info.get('state') == 'game_over'

def game_loop():
    """Main game loop with basic UI"""
    global player_name, card_rects
    pygame.init()
    screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
    pygame.display.set_caption("Skyjo")
    clock = pygame.time.Clock()

    while True:
        # Handle events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and is_game_over():
                    # Return to menu or exit
                    pygame.quit()
                    sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle game action buttons
                for btn in buttons:
                    if btn.rect.collidepoint(event.pos):
                        btn.callback()
                        break
                else:
                    # Handle card clicks if no button was clicked
                    row_col = get_clicked_card(event.pos, card_rects)
                    if row_col:
                        row, col = row_col
                        handle_card_click(row, col)

        # Clear screen
        screen.fill((0, 100, 0))  # Dark green background
        
        if game_state:
            # Check if game is over
            if is_game_over():
                draw_game_over_screen(screen, game_state)
            else:
                # Draw normal game elements
                players_data = game_state.get('players', {})
                
                # Get current player name for turn highlighting
                board_info = game_state.get('board_info', {})
                current_player_index = board_info.get('current_player', -1)
                players = list(players_data.keys())
                current_player_name = players[current_player_index] if 0 <= current_player_index < len(players) else ""
                
                # Draw player grids with turn highlighting
                card_rects = draw_player_grids(screen, players_data, player_name, deck_images, current_player_name)
                
                # Draw game info
                draw_game_info(screen, game_state, player_name)
                
                # Draw held card
                draw_held_card(screen, game_state, deck_images)
                
                # Draw center area with deck and discard
                draw_center_area(screen, game_state, deck_images)
                
                # Setup and draw action buttons
                setup_buttons(screen)
                for btn in buttons:
                    btn.draw(screen)
        else:
            # Show waiting message
            font = pygame.font.SysFont(None, 36)
            text = font.render("Waiting for game to start...", True, (255, 255, 255))
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, screen.get_height()//2))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    gui_register_player()
    threading.Thread(target=receive_data, daemon=True).start()
    game_loop()
