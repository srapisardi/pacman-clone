# pacman-clone

A custom Pac-Man clone built with Python and Pygame, made to eventually swap in
custom sprites: a friend's face as the player, three more friends as the
ghosts, and bowls of clam chowder in place of the dots.

## Current status

The game is fully playable with placeholder shapes (circles) standing in for
the final artwork. Core Pac-Man mechanics are implemented and tested.

### Features implemented so far

- **Maze** — a 20x15 tile maze (`MAZE` in [main.py](main.py)) with walls,
  corridors, and a center "ghost house" with gated exits.
- **Player movement** — WASD controls, one axis per frame (no diagonal
  cutting through walls), with forgiving corner-turning so the player doesn't
  get stuck when slightly off a tile's center.
- **Pellets** — every open floor tile starts with a pellet ("bowl of chowder"
  placeholder); walking over one removes it and adds to the score.
- **Ghosts** — 3 ghosts with distinct chase personalities instead of random
  wandering or identical behavior:
  - **Red ("chase")** — goes directly after the player using BFS pathfinding
    through the maze.
  - **Cyan ("ambush")** — targets a tile offset ahead of the player to try to
    cut them off.
  - **Orange ("clyde")** — chases when far from the player, retreats to a
    scatter corner when close.
  - Ghosts also avoid stacking on the same tile as each other so they visibly
    spread out instead of overlapping.
- **Collision & lives** — touching a ghost costs the player one of 3 lives;
  losing all 3 ends the game with a "GAME OVER" screen. Losing a life resets
  player/ghost positions without resetting the score or pellets.
- **HUD** — a bar below the maze shows the current score and remaining lives.

### Controls

| Key | Action     |
|-----|------------|
| W   | Move up    |
| A   | Move left  |
| S   | Move down  |
| D   | Move right |

### Running the game

**With Python installed:**

- **Windows:** double-click `run.bat` (uses `dist/CoreyChowda.exe` if you've
  built it locally — see below — otherwise runs from source)
- **macOS/Linux:** run `./run.sh` in a terminal

**Manual way**, if you'd rather manage dependencies yourself:

```bash
pip install -r requirements.txt
python main.py
```

#### Building a standalone .exe (no Python required to run it)

A prebuilt `.exe` isn't checked into this repo — GitHub's push scanning
rejects raw PyInstaller binaries pushed via git (a common false-positive for
this kind of self-extracting build). To get a no-Python-required build,
make it yourself:

```bash
pip install pyinstaller
pyinstaller --onefile --name CoreyChowda --add-data "assets;assets" main.py
```

This produces `dist/CoreyChowda.exe`, which `run.bat` will pick up
automatically. If you want to share a build with others, upload it as an
asset on a [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github)
rather than committing it — releases aren't subject to the same push
scanning as regular commits.

### Running the tests

Core game logic (level building, pellet consumption, collision detection,
and ghost pathfinding) is covered by unit tests in
[tests/test_game_logic.py](tests/test_game_logic.py):

```bash
python -m pytest -q tests/test_game_logic.py
```

## Project structure

```
corey-chowda/
├── main.py                    # Game loop, maze, movement, ghost AI, rendering
├── assets/                    # Sprite, image, and sound assets
├── dist/                      # Local PyInstaller output (gitignored, not committed)
├── run.bat                    # Windows launcher (uses dist/CoreyChowda.exe if present)
├── run.sh                     # macOS/Linux launcher (runs from source)
├── tests/
│   └── test_game_logic.py     # Unit tests for core game logic
├── requirements.txt
└── README.md
```

## Planned next steps

- Replace the placeholder circles with generic face sprites first, then swap
  in actual friend photos for the player and each ghost.
- Replace the dot pellets with clam chowder bowl images.
- Possibly add a restart option from the game-over screen.
