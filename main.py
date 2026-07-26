import random
import sys
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

# '#' = wall, '.' = floor with a pellet, ' ' = open floor (no pellet, e.g. ghost house)
MAZE = [
    "####################",
    "#........##........#",
    "#.##.###.##.###.##.#",
    "#..................#",
    "#.###.#.#  #.#.###.#",
    "#.....#.#  #.#.....#",
    "#####.#.#  #.#.#####",
    "#  #..#.####.#..#  #",
    "#####.#.#  #.#.#####",
    "#.....#.#  #.#.....#",
    "#.###.#.#  #.#.###.#",
    "#..................#",
    "#.##.###.##.###.##.#",
    "#........##........#",
    "####################",
]

CELL_SIZE = 64
WIDTH = len(MAZE[0]) * CELL_SIZE
HEIGHT = len(MAZE) * CELL_SIZE
HUD_HEIGHT = 80
FPS = 60

PLAYER_SIZE = 52
GHOST_SIZE = 52
STARTING_LIVES = 3
TILE_CENTER_OFFSET = CELL_SIZE // 2
CLYDE_SCATTER_DISTANCE = 8
PELLET_SIZE = 24
PELLET_IMAGE_PATH = Path(__file__).parent / "assets" / "chowda_pellet.png"
PLAYER_IMAGE_PATH = Path(__file__).parent / "assets" / "corey_player.png"
KENNY_GHOST_IMAGE_PATH = Path(__file__).parent / "assets" / "kenny_ghost.png"
CARA_GHOST_IMAGE_PATH = Path(__file__).parent / "assets" / "cara_ghost.png"
SAL_GHOST_IMAGE_PATH = Path(__file__).parent / "assets" / "sal_ghost.png"

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class GameState:
    def __init__(self) -> None:
        self.running = True
        self.game_over = False
        self.score = 0
        self.lives = STARTING_LIVES
        self.level = build_level()
        self.player_speed = 5
        self.ghost_speed = 4
        self.reset_positions()

    def reset_positions(self) -> None:
        # (12, 7) is the walkable floor tile closest to the maze's true center
        # (row 7 of 15 is the exact middle row; the middle column is blocked
        # by the ghost house, so this is the nearest open tile beside it).
        self.player_pos = tile_center(12, 7)
        self.player_facing = 1
        self.ghosts = [
            {
                "pos": tile_center(9, 5),
                "dir": (0, -1),
                "color": (255, 0, 0),
                "role": "chase",
                "facing": 1,
            },
            {
                "pos": tile_center(10, 5),
                "dir": (0, 1),
                "color": (0, 255, 255),
                "role": "ambush",
                "ambush_offset": (-4, -4),
                "facing": 1,
            },
            {
                "pos": tile_center(9, 8),
                "dir": (1, 0),
                "color": (255, 165, 0),
                "role": "clyde",
                "scatter_target": (1, 13),
                "facing": 1,
            },
        ]


def tile_center(col: int, row: int) -> Tuple[int, int]:
    return (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)


def build_level() -> Dict[str, object]:
    grid: List[List[str]] = []
    pellets: List[Tuple[int, int]] = []

    for row_index, row_text in enumerate(MAZE):
        row: List[str] = []
        for col_index, char in enumerate(row_text):
            if char == "#":
                row.append("wall")
            elif char == ".":
                row.append("pellet")
                pellets.append(tile_center(col_index, row_index))
            else:
                row.append("floor")
        grid.append(row)

    return {
        "grid": grid,
        "pellets": pellets,
        "remaining_pellets": len(pellets),
    }


def consume_pellet(level: Dict[str, object], pellet: Tuple[int, int]) -> Dict[str, object]:
    pellets = list(level["pellets"])
    if pellet in pellets:
        pellets.remove(pellet)
    updated_level = dict(level)
    updated_level["pellets"] = pellets
    updated_level["remaining_pellets"] = len(pellets)
    return updated_level


def collides(pos_a: Tuple[int, int], pos_b: Tuple[int, int], size_a: int, size_b: int) -> bool:
    ax, ay = pos_a
    bx, by = pos_b
    return abs(ax - bx) < (size_a + size_b) // 2 and abs(ay - by) < (size_a + size_b) // 2


def player_hits_ghost(player_pos: Tuple[int, int], ghosts: List[Dict[str, object]]) -> bool:
    return any(
        collides(player_pos, ghost["pos"], PLAYER_SIZE, GHOST_SIZE) for ghost in ghosts
    )


def is_wall_tile(grid: List[List[str]], col: int, row: int) -> bool:
    if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[0]):
        return True
    return grid[row][col] == "wall"


def tile_of(pos: Tuple[int, int]) -> Tuple[int, int]:
    return (pos[0] // CELL_SIZE, pos[1] // CELL_SIZE)


def is_centered_on_tile(pos: Tuple[int, int]) -> bool:
    x, y = pos
    return (x - TILE_CENTER_OFFSET) % CELL_SIZE == 0 and (y - TILE_CENTER_OFFSET) % CELL_SIZE == 0


def nearest_tile_center(value: int) -> int:
    tile_index = round((value - TILE_CENTER_OFFSET) / CELL_SIZE)
    return tile_index * CELL_SIZE + TILE_CENTER_OFFSET


def bfs_next_direction(
    grid: List[List[str]], start: Tuple[int, int], target: Tuple[int, int]
) -> Optional[Tuple[int, int]]:
    """Return the first-step direction along the shortest path from start to target."""
    if start == target:
        return None

    rows = len(grid)
    cols = len(grid[0])
    visited = {start}
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        if current == target:
            break
        cx, cy = current
        for dx, dy in DIRECTIONS:
            neighbor = (cx + dx, cy + dy)
            nx, ny = neighbor
            if (
                0 <= nx < cols
                and 0 <= ny < rows
                and grid[ny][nx] != "wall"
                and neighbor not in visited
            ):
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    if target not in visited:
        return None

    step = target
    while parent[step] != start:
        step = parent[step]

    return (step[0] - start[0], step[1] - start[1])


def bfs_distance_map(
    grid: List[List[str]], target: Tuple[int, int]
) -> Dict[Tuple[int, int], int]:
    """Return shortest-path distances from every reachable tile to target."""
    rows = len(grid)
    cols = len(grid[0])
    distances = {target: 0}
    queue = deque([target])

    while queue:
        current = queue.popleft()
        cx, cy = current
        for dx, dy in DIRECTIONS:
            neighbor = (cx + dx, cy + dy)
            nx, ny = neighbor
            if (
                0 <= nx < cols
                and 0 <= ny < rows
                and grid[ny][nx] != "wall"
                and neighbor not in distances
            ):
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances


def get_ghost_target(
    ghost: Dict[str, object],
    ghost_tile: Tuple[int, int],
    player_tile: Tuple[int, int],
    grid: List[List[str]],
) -> Tuple[int, int]:
    """Give each ghost a distinct personality so they spread out instead of chasing identically."""
    role = ghost.get("role", "chase")

    if role == "ambush":
        dx, dy = ghost.get("ambush_offset", (0, 0))
        cols = len(grid[0])
        rows = len(grid)
        tx = min(max(player_tile[0] + dx, 0), cols - 1)
        ty = min(max(player_tile[1] + dy, 0), rows - 1)
        if grid[ty][tx] != "wall":
            return (tx, ty)
        return player_tile

    if role == "clyde":
        distance = abs(ghost_tile[0] - player_tile[0]) + abs(ghost_tile[1] - player_tile[1])
        if distance > CLYDE_SCATTER_DISTANCE:
            return player_tile
        return ghost.get("scatter_target", player_tile)

    return player_tile


def can_move_to(level: Dict[str, object], pos: Tuple[int, int], size: int) -> bool:
    grid = level["grid"]
    half = size // 2
    x, y = pos
    corners = [
        (x - half, y - half),
        (x + half - 1, y - half),
        (x - half, y + half - 1),
        (x + half - 1, y + half - 1),
    ]
    for cx, cy in corners:
        if is_wall_tile(grid, cx // CELL_SIZE, cy // CELL_SIZE):
            return False
    return True


def move_player(
    level: Dict[str, object],
    pos: Tuple[int, int],
    size: int,
    speed: int,
    keys,
) -> Tuple[int, int]:
    # Only one axis moves per frame so Pac-Man never cuts diagonally through walls.
    dx, dy = 0, 0
    if keys[pygame.K_a]:
        dx, dy = -1, 0
    elif keys[pygame.K_d]:
        dx, dy = 1, 0
    elif keys[pygame.K_w]:
        dx, dy = 0, -1
    elif keys[pygame.K_s]:
        dx, dy = 0, 1

    if dx == 0 and dy == 0:
        return pos

    x, y = pos

    # Snap the cross-axis coordinate to its tile center when close enough so
    # turning at an intersection isn't blocked by a few pixels of drift picked
    # up while traveling (the player's speed doesn't evenly divide CELL_SIZE).
    if dx != 0:
        snapped_y = nearest_tile_center(y)
        if abs(y - snapped_y) <= speed:
            y = snapped_y
    else:
        snapped_x = nearest_tile_center(x)
        if abs(x - snapped_x) <= speed:
            x = snapped_x

    new_pos = (x + dx * speed, y + dy * speed)
    if can_move_to(level, new_pos, size):
        return new_pos
    return pos


def move_ghost(
    level: Dict[str, object],
    ghost: Dict[str, object],
    speed: int,
    player_tile: Tuple[int, int],
    other_ghost_positions: List[Tuple[int, int]],
) -> None:
    grid = level["grid"]
    x, y = ghost["pos"]

    # Only re-evaluate the chase direction while centered on a tile, so ghosts
    # commit to a direction instead of jittering mid-corridor.
    if is_centered_on_tile((x, y)):
        current_tile = tile_of((x, y))
        target = get_ghost_target(ghost, current_tile, player_tile, grid)
        distances = bfs_distance_map(grid, target)

        candidates = []
        for d in DIRECTIONS:
            neighbor = (current_tile[0] + d[0], current_tile[1] + d[1])
            if neighbor in distances:
                candidates.append((distances[neighbor], d, neighbor))

        if candidates:
            best_distance = min(c[0] for c in candidates)
            best_options = [c for c in candidates if c[0] == best_distance]

            # Prefer a direction that doesn't land on a tile another ghost is
            # currently occupying, so ghosts spread out instead of stacking.
            other_tiles = {tile_of(p) for p in other_ghost_positions}
            free_options = [c for c in best_options if c[2] not in other_tiles]
            chosen = random.choice(free_options) if free_options else random.choice(best_options)
            ghost["dir"] = chosen[1]

    dx, dy = ghost["dir"]
    if dx != 0:
        ghost["facing"] = 1 if dx > 0 else -1
    new_pos = (x + dx * speed, y + dy * speed)

    if can_move_to(level, new_pos, GHOST_SIZE):
        ghost["pos"] = new_pos
        return

    # Fallback for the rare case the chosen direction is blocked mid-tile.
    valid_dirs = [
        d
        for d in DIRECTIONS
        if can_move_to(level, (x + d[0] * speed, y + d[1] * speed), GHOST_SIZE)
    ]
    if valid_dirs:
        ghost["dir"] = random.choice(valid_dirs)


def draw_wall(surface: pygame.Surface, col: int, row: int) -> None:
    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, (33, 33, 222), rect)


def draw_player(surface: pygame.Surface, pos: Tuple[int, int], image: pygame.Surface) -> None:
    rect = image.get_rect(center=pos)
    surface.blit(image, rect)


def draw_ghost(surface: pygame.Surface, pos: Tuple[int, int], image: pygame.Surface) -> None:
    rect = image.get_rect(center=pos)
    surface.blit(image, rect)


def draw_pellet(surface: pygame.Surface, pos: Tuple[int, int], image: pygame.Surface) -> None:
    rect = image.get_rect(center=pos)
    surface.blit(image, rect)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, score: int, lives: int) -> None:
    text = font.render(f"Score: {score}   Lives: {lives}", True, (255, 255, 255))
    surface.blit(text, (8, HEIGHT + 10))


def draw_game_over(surface: pygame.Surface, font: pygame.font.Font) -> None:
    text = font.render("GAME OVER", True, (255, 0, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(text, rect)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Corey Chowda Pacman Clone")
    screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
    clock = pygame.time.Clock()
    hud_font = pygame.font.SysFont(None, 56)
    game_over_font = pygame.font.SysFont(None, 144)
    pellet_image = pygame.image.load(str(PELLET_IMAGE_PATH)).convert_alpha()
    player_image_right = pygame.image.load(str(PLAYER_IMAGE_PATH)).convert_alpha()
    player_image_left = pygame.transform.flip(player_image_right, True, False)

    ghost_images = []
    for path in (KENNY_GHOST_IMAGE_PATH, CARA_GHOST_IMAGE_PATH, SAL_GHOST_IMAGE_PATH):
        image_right = pygame.image.load(str(path)).convert_alpha()
        image_left = pygame.transform.flip(image_right, True, False)
        ghost_images.append((image_right, image_left))

    state = GameState()

    while state.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False

        if not state.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                state.player_facing = -1
            elif keys[pygame.K_d]:
                state.player_facing = 1
            state.player_pos = move_player(
                state.level, state.player_pos, PLAYER_SIZE, state.player_speed, keys
            )

            player_tile = tile_of(state.player_pos)
            for i, ghost in enumerate(state.ghosts):
                other_positions = [
                    g["pos"] for j, g in enumerate(state.ghosts) if j != i
                ]
                move_ghost(state.level, ghost, state.ghost_speed, player_tile, other_positions)

            for pellet in list(state.level["pellets"]):
                if collides(state.player_pos, pellet, PLAYER_SIZE, PELLET_SIZE):
                    state.level = consume_pellet(state.level, pellet)
                    state.score += 10

            if player_hits_ghost(state.player_pos, state.ghosts):
                state.lives -= 1
                if state.lives <= 0:
                    state.game_over = True
                else:
                    state.reset_positions()

        screen.fill((0, 0, 0))
        grid = state.level["grid"]
        for row_index, row in enumerate(grid):
            for col_index, cell in enumerate(row):
                if cell == "wall":
                    draw_wall(screen, col_index, row_index)

        for pellet in state.level["pellets"]:
            draw_pellet(screen, pellet, pellet_image)

        player_image = player_image_right if state.player_facing >= 0 else player_image_left
        draw_player(screen, state.player_pos, player_image)
        for i, ghost in enumerate(state.ghosts):
            image_right, image_left = ghost_images[i]
            ghost_image = image_right if ghost["facing"] >= 0 else image_left
            draw_ghost(screen, ghost["pos"], ghost_image)

        draw_hud(screen, hud_font, state.score, state.lives)
        if state.game_over:
            draw_game_over(screen, game_over_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
