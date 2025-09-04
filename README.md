Skyjo Multiplayer (Minimal Release)

Quick start to run the local host/client version.

Requirements
- Python 3.9+
- pip
- pygame (`pip install pygame`)

Install dependencies
```bash
pip install -r requirements.txt || pip install pygame
```

Run
- Start the menu:
```bash
python3 main.py
```
- Click "Spiel erstellen (Host)" to start the server.
- Click "Spiel beitreten (Client)" to start a client.

Notes
- On Windows, use `python` instead of `python3`.
- Assets are in `assets/`; game logic is in `game/`; networking is in `net/`.

