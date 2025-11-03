#!/usr/bin/env python3


from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import pygame

from mazevis import bfs, read_maze, reconstruir

Coord = Tuple[int, int]
Grid = List[List[str]]

CELL_SIZE = 48
OUTER_MARGIN = 24
HEADER_HEIGHT = 96
FONT_SIZE = 20
FPS = 30
INFO_WIDTH = 220
PATH_STEP_MS = 220
HOLD_AFTER_MAZE_MS = 1400

COLOR_BG = (20, 23, 32)
COLOR_FLOOR = (223, 223, 223)
COLOR_WALL = (48, 52, 70)
COLOR_START = (102, 187, 106)
COLOR_GOAL = (239, 83, 80)
COLOR_GRID = (15, 17, 24)
COLOR_TEXT = (235, 235, 235)
COLOR_INFO = (144, 164, 174)
COLOR_PATH_TRAIL = (255, 213, 79)
COLOR_PATH_ACTIVE = (255, 241, 118)

DEFAULT_FILES = [
    "laberinto_1.in.txt",
    "laberinto_2.in.txt",
    "laberinto_3.in.txt",
]


@dataclass
class MazeEntry:
    file_path: Path
    grid: Grid
    start: Coord
    goal: Coord
    path: List[Coord]
    path_lookup: Dict[Coord, int]

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0


class AnimationController:
    """Controls the progression of the path animation across all mazes."""

    def __init__(self, mazes: List[MazeEntry]):
        self.mazes = mazes
        self.index = 0
        self.step_index = 0
        self.step_timer = 0.0
        self.hold_timer = 0.0
        self.state = "animating"
        self._configure_maze(0)

    def _configure_maze(self, index: int) -> None:
        self.index = index
        current_path_len = len(self.current.path)
        if current_path_len:
            self.step_index = 1  # show start cell immediately
            self.state = "animating" if current_path_len > 1 else "hold"
        else:
            self.step_index = 0
            self.state = "hold"
        self.step_timer = 0.0
        self.hold_timer = 0.0

    @property
    def current(self) -> MazeEntry:
        return self.mazes[self.index]

    def update(self, dt_ms: float) -> Tuple[bool, bool]:
        """Advance animation clocks; returns (finished_all, switched_maze)."""
        switched = False
        if self.state == "animating":
            self.step_timer += dt_ms
            path_len = len(self.current.path)
            while self.step_timer >= PATH_STEP_MS and self.step_index < path_len:
                self.step_timer -= PATH_STEP_MS
                self.step_index += 1
            if self.step_index >= path_len:
                self.state = "hold"
                self.hold_timer = 0.0

        if self.state == "hold":
            self.hold_timer += dt_ms
            if self.hold_timer >= HOLD_AFTER_MAZE_MS:
                if self.index + 1 >= len(self.mazes):
                    return True, switched
                self._configure_maze(self.index + 1)
                switched = True

        return False, switched


def load_mazes(paths: Sequence[Path]) -> List[MazeEntry]:
    """Read mazes and compute BFS paths using the existing solver logic."""
    loaded: List[MazeEntry] = []
    for path in paths:
        try:
            grid, start, goal = read_maze(str(path))
            _visitados, _raiz, meta = bfs(grid, start, goal)
            solution = reconstruir(meta)
            lookup = {coord: idx for idx, coord in enumerate(solution)}
            loaded.append(MazeEntry(path, grid, start, goal, solution, lookup))
        except Exception as exc:
            print(f"[ignorado] {path}: {exc}")
    if not loaded:
        raise RuntimeError("no se pudo cargar ningún laberinto válido")
    return loaded


def compute_window_size(entry: MazeEntry) -> Tuple[int, int]:
    """Return window size (width, height) for the given maze."""
    width = entry.cols * CELL_SIZE + OUTER_MARGIN * 2 + INFO_WIDTH
    height = entry.rows * CELL_SIZE + OUTER_MARGIN + HEADER_HEIGHT
    return width, height


def cell_color(char: str) -> Tuple[int, int, int]:
    """Base color for a maze cell."""
    if char == "0":
        return COLOR_WALL
    if char == "A":
        return COLOR_START
    if char == "B":
        return COLOR_GOAL
    return COLOR_FLOOR


def draw_header(
    surface: pygame.Surface, font: pygame.font.Font, lines: Iterable[str]
) -> None:
    """Draw informational lines at the top of the window."""
    y = OUTER_MARGIN // 2
    for line in lines:
        text = font.render(line, True, COLOR_TEXT)
        surface.blit(text, (OUTER_MARGIN, y))
        y += text.get_height() + 4


def draw_legend(
    surface: pygame.Surface, font: pygame.font.Font, top: int, left: int
) -> None:
    """Render a legend explaining colors."""
    legend_items = [
        ("Pared", COLOR_WALL),
        ("Transitable", COLOR_FLOOR),
        ("Ruta BFS", COLOR_PATH_TRAIL),
        ("Inicio (A)", COLOR_START),
        ("Meta (B)", COLOR_GOAL),
    ]
    y = top
    for label, color in legend_items:
        rect = pygame.Rect(left, y, 20, 20)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, COLOR_GRID, rect, 1)
        text = font.render(label, True, COLOR_INFO)
        surface.blit(text, (rect.right + 8, y - 1))
        y += 26


def draw_maze(
    surface: pygame.Surface, font: pygame.font.Font, entry: MazeEntry, step_index: int
) -> None:
    # render the maze grid and the progressively drawn solution path
    surface.fill(COLOR_BG)

    path_len = len(entry.path)
    progress = min(step_index, path_len)
    header_lines = [
        f"{entry.file_path} — {entry.rows} filas x {entry.cols} columnas",
    ]
    if path_len:
        header_lines.append(f"Ruta BFS: {path_len} casillas")
        header_lines.append(f"Progreso: {progress}/{path_len}")
    else:
        header_lines.append("Ruta BFS: sin solución")
    draw_header(surface, font, header_lines)

    origin_x = OUTER_MARGIN
    origin_y = HEADER_HEIGHT
    active_index = progress - 1 if progress else -1

    for row_index, row in enumerate(entry.grid):
        for col_index, char in enumerate(row):
            x = origin_x + col_index * CELL_SIZE
            y = origin_y + row_index * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            pygame.draw.rect(surface, cell_color(char), rect)
            pygame.draw.rect(surface, COLOR_GRID, rect, 1)

            path_order = entry.path_lookup.get((row_index, col_index))
            if path_order is not None and path_order < progress:
                shrink = max(10, CELL_SIZE // 3)
                overlay_rect = rect.inflate(-shrink, -shrink)
                color = (
                    COLOR_PATH_ACTIVE
                    if path_order == active_index
                    else COLOR_PATH_TRAIL
                )
                pygame.draw.rect(surface, color, overlay_rect, border_radius=6)

    legend_x = origin_x + entry.cols * CELL_SIZE + 28
    legend_y = HEADER_HEIGHT
    draw_legend(surface, font, legend_y, legend_x)


def main() -> None:
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("Menlo", FONT_SIZE)

    if len(sys.argv) > 1:
        files = [Path(arg) for arg in sys.argv[1:]]
    else:
        files = [Path(name) for name in DEFAULT_FILES]

    mazes = load_mazes(files)
    controller = AnimationController(mazes)

    current_entry = controller.current
    window_size = compute_window_size(current_entry)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption(f"Maze Path Animation — {current_entry.file_path.name}")

    clock = pygame.time.Clock()
    current_size = window_size

    running = True
    finished = False
    while running and not finished:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        finished, switched = controller.update(dt)
        if switched:
            current_entry = controller.current
            new_size = compute_window_size(current_entry)
            if new_size != current_size:
                screen = pygame.display.set_mode(new_size)
                current_size = new_size
            pygame.display.set_caption(
                f"Maze Path Animation — {current_entry.file_path.name}"
            )

        draw_maze(screen, font, controller.current, controller.step_index)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
