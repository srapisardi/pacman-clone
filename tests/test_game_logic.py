from main import build_level, consume_pellet, collides, player_hits_ghost, bfs_next_direction


def test_build_level_creates_pellets():
    level = build_level()

    assert level["remaining_pellets"] > 0
    assert len(level["pellets"]) == level["remaining_pellets"]
    assert any("pellet" in row for row in level["grid"])


def test_consume_pellet_removes_one_pellet():
    level = build_level()
    first_pellet = level["pellets"][0]

    updated = consume_pellet(level, first_pellet)

    assert first_pellet not in updated["pellets"]
    assert updated["remaining_pellets"] == level["remaining_pellets"] - 1


def test_collision_detects_overlapping_positions():
    assert collides((100, 100), (100, 100), 20, 20)
    assert not collides((100, 100), (200, 200), 20, 20)


def test_player_hits_ghost_detects_overlap():
    ghosts = [{"pos": (100, 100), "dir": (0, 0), "color": (255, 0, 0)}]

    assert player_hits_ghost((100, 100), ghosts)
    assert not player_hits_ghost((300, 300), ghosts)


def test_bfs_next_direction_moves_toward_target():
    grid = [
        ["wall", "wall", "wall", "wall", "wall"],
        ["wall", "floor", "floor", "floor", "wall"],
        ["wall", "floor", "wall", "floor", "wall"],
        ["wall", "floor", "floor", "floor", "wall"],
        ["wall", "wall", "wall", "wall", "wall"],
    ]

    assert bfs_next_direction(grid, (1, 1), (3, 1)) == (1, 0)
    assert bfs_next_direction(grid, (1, 1), (1, 1)) is None
    assert bfs_next_direction(grid, (1, 1), (3, 3)) in [(1, 0), (0, 1)]
