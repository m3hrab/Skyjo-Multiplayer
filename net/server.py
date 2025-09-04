import socket
import threading
import json
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.rules import Rules

HOST = 'localhost'
PORT = 12345

clients = []
player_names = []
MAX_PLAYERS = None
lock = threading.Lock()
rules = Rules()

def send_game_state_to_all():
    """Send updated game state to all connected clients"""
    with lock:
        for i, conn in enumerate(clients):
            if i < len(player_names):
                name = player_names[i]
                try:
                    state = rules.get_game_state_for_player(name)
                    message = json.dumps(state) + '\n'
                    conn.send(message.encode())
                except Exception as e:
                    print(f"Error sending state to {name}: {e}")
                    if conn in clients:
                        clients.remove(conn)

def handle_client(conn, addr):
    global MAX_PLAYERS
    name = ""
    try:
        with lock:
            is_first = len(clients) == 0

        # Handle player count selection (only for first player)
        if is_first:
            conn.send("choose_players".encode())
            try:
                MAX_PLAYERS = int(conn.recv(1024).decode())
                print(f"Game set for {MAX_PLAYERS} players")
            except ValueError:
                print("Error: Invalid player count")
                conn.close()
                return
        else:
            conn.send("enter_name".encode())

        # Get player name
        name = conn.recv(1024).decode().strip()
        if not name or name in player_names:
            print(f"Error: Invalid or duplicate player name: {name}")
            conn.close()
            return

        # Add player to game
        with lock:
            player_names.append(name)
            rules.add_player(name)
            clients.append(conn)

        print(f"{name} connected from {addr}")

        # Wait for all players to join
        while len(clients) < MAX_PLAYERS:
            time.sleep(0.1)

        # Start game when all players are connected
        if len(clients) == MAX_PLAYERS and len(player_names) == MAX_PLAYERS:
            print("All players connected, starting game...")
            rules.start_game()
            send_game_state_to_all()

        # Handle client messages
        while True:
            try:
                data = conn.recv(4096).decode().strip()
                if not data:
                    break
                    
                action_data = json.loads(data)
                action = action_data.get("action")
                
                success = False
                
                # Handle different action types
                if action == "select_initial_card":
                    row = action_data.get("row")
                    col = action_data.get("col")
                    success = rules.handle_initial_card_selection(name, row, col)
                
                elif action == "draw_from_deck":
                    success = rules.handle_draw_pile_action(name)
                
                elif action == "draw_from_discard":
                    success = rules.handle_discard_pile_action(name)
                
                elif action == "keep_card":
                    success = rules.handle_keep_card_action(name)
                
                elif action == "discard_card":
                    success = rules.handle_discard_drawn_card_action(name)
                
                elif action == "swap_card":
                    row = action_data.get("row")
                    col = action_data.get("col")
                    success = rules.handle_card_swap(name, row, col)
                
                elif action == "flip_card":
                    row = action_data.get("row")
                    col = action_data.get("col")
                    success = rules.handle_card_flip(name, row, col)
                
                elif action == "start_new_round":
                    success = rules.start_new_round()
                
                else:
                    print(f"Unknown action from {name}: {action}")
                
                if success:
                    # Broadcast updated game state to all players
                    send_game_state_to_all()
                else:
                    print(f"Action failed for {name}: {action}")
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON from {name}")
            except Exception as e:
                print(f"Error handling action from {name}: {e}")
                break

    except Exception as e:
        print(f"Error with client {name}: {e}")
    finally:
        conn.close()
        with lock:
            if conn in clients:
                clients.remove(conn)
            if name in player_names:
                player_names.remove(name)
        print(f"{name} disconnected")

def start_server():
    """Start the game server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Skyjo server started on {HOST}:{PORT}")
        print("Waiting for players to connect...")

        try:
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")

if __name__ == "__main__":
    start_server()
