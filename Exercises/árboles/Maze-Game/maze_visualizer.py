#!/usr/bin/env python3
"""Simple pygame visualizer for BFS and DFS traversals."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import pygame

from mazevis import bfs, dfs_pre, read_maze, reconstruir

Coord = Tuple[int, int]
Grid = List[List[str]]

PADDING = 32
LABEL_HEIGHT = 72
FONT_SIZE = 24
FPS = 30

MAX_CELL_SIZE = 40
MIN_CELL_SIZE = 4
MAX_WINDOW_WIDTH = 1024
MAX_WINDOW_HEIGHT = 840

VISIT_TOTAL_TARGET_MS = 12000
PATH_TOTAL_TARGET_MS = 4000
VISIT_STEP_MIN_MS = 3
VISIT_STEP_MAX_MS = 160
PATH_STEP_MIN_MS = 4
PATH_STEP_MAX_MS = 200
HOLD_BETWEEN_PHASES_MS = 900

DISPLAY_MARGIN = 80

COLOR_BACKGROUND = (28, 28, 34)
COLOR_WALL = (60, 60, 70)
COLOR_FLOOR = (222, 222, 222)
COLOR_GRID = (90, 90, 100)
COLOR_START = (76, 175, 80)
COLOR_GOAL = (239, 83, 80)
COLOR_TEXT = (245, 245, 245)
COLOR_BFS = (99, 155, 255)
COLOR_DFS = (244, 143, 177)
COLOR_PATH = (255, 214, 0)

# defaults for sample files
DEFAULT_FILES = [
    "laberinto_1.in.txt",
    "laberinto_2.in.txt",
    "laberinto_3.in.txt",
    "laberinto_100x100.in.txt",
    "laberinto6.in.txt",
]


@dataclass
class MazeEntry:
    file_path: Path
    grid: Grid
    start: Coord
    goal: Coord
    bfs_visited: List[Coord]
    bfs_path: List[Coord]
    dfs_visited: List[Coord]
    dfs_path: List[Coord]

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0


class AnimationController:
    """State machine for stepping through BFS and DFS animations."""

    ALGORITHMS = ("bfs", "dfs")

    def __init__(self, mazes: List[MazeEntry]):
        self.mazes = mazes
        self.maze_index = 0
        self.algorithm_index = 0
        self.state = "visit"
        self.step_timer = 0.0
        self.hold_timer = 0.0
        self.visit_index = 0
        self.path_index = 0
        self.visit_delay = VISIT_STEP_MAX_MS
        self.path_delay = PATH_STEP_MAX_MS
        self._configure_maze(0)

    @property
    def current(self) -> MazeEntry:
        return self.mazes[self.maze_index]

    @property
    def current_algorithm(self) -> str:
        return self.ALGORITHMS[self.algorithm_index]

    def _configure_maze(self, index: int) -> None:
        self.maze_index = index
        self._refresh_delays()
        self.algorithm_index = 0
        self._reset_algorithm_state()

    def _reset_algorithm_state(self) -> None:
        self.state = "visit"
        self.step_timer = 0.0
        self.hold_timer = 0.0
        self.visit_index = 0
        self.path_index = 0

    def _refresh_delays(self) -> None:
        entry = self.mazes[self.maze_index]
        self.visit_delay, self.path_delay = compute_step_delays(entry)

    def update(self, dt_ms: float) -> Tuple[bool, bool]:
        """Advance timers; returns (finished_all, switched_maze)."""
        finished = False
        switched = False

        entry = self.current
        if self.current_algorithm == "bfs":
            visited = entry.bfs_visited
            path = entry.bfs_path
        else:
            visited = entry.dfs_visited
            path = entry.dfs_path

        if self.state == "visit":
            if visited:
                self.step_timer += dt_ms
                while self.step_timer >= self.visit_delay and self.visit_index < len(
                    visited
                ):
                    self.step_timer -= self.visit_delay
                    self.visit_index += 1
                if self.visit_index >= len(visited):
                    self.state = "path" if path else "hold"
                    self.step_timer = 0.0
                    self.path_index = 0
                    self.hold_timer = 0.0
            else:
                self.state = "path" if path else "hold"
                self.step_timer = 0.0
                self.hold_timer = 0.0

        elif self.state == "path":
            if path:
                self.step_timer += dt_ms
                while self.step_timer >= self.path_delay and self.path_index < len(
                    path
                ):
                    self.step_timer -= self.path_delay
                    self.path_index += 1
                if self.path_index >= len(path):
                    self.state = "hold"
                    self.hold_timer = 0.0
            else:
                self.state = "hold"
                self.hold_timer = 0.0

        elif self.state == "hold":
            self.hold_timer += dt_ms
            if self.hold_timer >= HOLD_BETWEEN_PHASES_MS:
                if self.algorithm_index + 1 < len(self.ALGORITHMS):
                    self.algorithm_index += 1
                    self._reset_algorithm_state()
                else:
                    if self.maze_index + 1 < len(self.mazes):
                        self._configure_maze(self.maze_index + 1)
                        switched = True
                    else:
                        finished = True

        return finished, switched

    def progress(
        self,
    ) -> Tuple[str, List[Coord], List[Coord], Coord | None, Coord | None]:
        """Return render data for the current frame."""
        entry = self.current
        if self.current_algorithm == "bfs":
            visited_source = entry.bfs_visited
            path_source = entry.bfs_path
        else:
            visited_source = entry.dfs_visited
            path_source = entry.dfs_path

        if self.state == "visit":
            visited_limit = min(self.visit_index, len(visited_source))
        else:
            visited_limit = len(visited_source)
        visited = visited_source[:visited_limit]

        if self.state == "visit":
            path_limit = 0
        elif self.state == "path":
            path_limit = min(self.path_index, len(path_source))
        else:
            path_limit = len(path_source)
        path = path_source[:path_limit]

        visited_active = visited[-1] if visited and self.state == "visit" else None
        path_active = path[-1] if path and self.state == "path" else None

        return self.current_algorithm, visited, path, visited_active, path_active

    def set_algorithm(self, name: str) -> None:
        # restart chosen run
        if name not in self.ALGORITHMS:
            return
        self.algorithm_index = self.ALGORITHMS.index(name)
        self._reset_algorithm_state()

    def next_maze(self) -> bool:
        # step forward in file list
        if self.maze_index + 1 >= len(self.mazes):
            return False
        self._configure_maze(self.maze_index + 1)
        return True

    def prev_maze(self) -> bool:
        # step backward in file list
        if self.maze_index == 0:
            return False
        self._configure_maze(self.maze_index - 1)
        return True


def load_mazes(paths: Sequence[Path]) -> List[MazeEntry]:
    """Read maze files and collect BFS/DFS traversal information."""
    loaded: List[MazeEntry] = []
    for path in paths:
        try:
            grid, start, goal = read_maze(str(path))
            bfs_visitados, _bfs_raiz, bfs_meta = bfs(grid, start, goal)
            dfs_visitados, _dfs_raiz, dfs_meta = dfs_pre(grid, start, goal)
            entry = MazeEntry(
                file_path=path,
                grid=grid,
                start=start,
                goal=goal,
                bfs_visited=bfs_visitados,
                bfs_path=reconstruir(bfs_meta),
                dfs_visited=dfs_visitados,
                dfs_path=reconstruir(dfs_meta),
            )
            loaded.append(entry)
        except Exception as exc:
            print(f"[ignorado] {path}: {exc}")
    if not loaded:
        raise RuntimeError("no se pudo cargar ningún laberinto válido")
    return loaded


def collect_default_files() -> List[Path]:
    """Return default maze paths, including any matching *.in.txt files in cwd."""
    preset = [Path(name) for name in DEFAULT_FILES]
    discovered = sorted(Path.cwd().glob("*.in.txt"))
    seen = set()
    combined: List[Path] = []
    for path in preset + discovered:
        if not path.exists():
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        combined.append(path)
        seen.add(key)
    if not combined:
        raise RuntimeError(
            "no se encontraron laberintos por defecto; pasa archivos como argumentos"
        )
    return combined


def clamp(value: float, lower: int, upper: int) -> int:
    rounded = int(value)
    if rounded < lower:
        return lower
    if rounded > upper:
        return upper
    return rounded


def compute_step_delays(entry: MazeEntry) -> Tuple[int, int]:
    """Pick per-cell delays so big mazes play faster but remain readable."""
    visit_candidates = [len(entry.bfs_visited), len(entry.dfs_visited)]
    max_visits = max(1, *visit_candidates)
    raw_visit = VISIT_TOTAL_TARGET_MS / max_visits
    visit_delay = clamp(raw_visit, VISIT_STEP_MIN_MS, VISIT_STEP_MAX_MS)

    path_candidates = [len(entry.bfs_path), len(entry.dfs_path)]
    max_path = max(path_candidates) if any(path_candidates) else 0
    if max_path:
        raw_path = PATH_TOTAL_TARGET_MS / max_path
        path_delay = clamp(raw_path, PATH_STEP_MIN_MS, PATH_STEP_MAX_MS)
    else:
        path_delay = PATH_STEP_MIN_MS

    return visit_delay, path_delay


def determine_window_limits() -> Tuple[int, int]:
    """Pick a window size budget based on the desktop, keeping a small margin."""
    max_width = MAX_WINDOW_WIDTH
    max_height = MAX_WINDOW_HEIGHT

    try:
        info = pygame.display.Info()
    except pygame.error:
        info = None

    if info:
        min_width = PADDING * 2 + MIN_CELL_SIZE * 4
        min_height = PADDING * 2 + LABEL_HEIGHT + MIN_CELL_SIZE * 4

        if info.current_w:
            margin_w = min(DISPLAY_MARGIN, max(0, info.current_w - min_width))
            candidate_w = info.current_w - margin_w
            max_width = max(candidate_w, min_width)
            max_width = min(max_width, info.current_w)
        if info.current_h:
            margin_h = min(DISPLAY_MARGIN, max(0, info.current_h - min_height))
            candidate_h = info.current_h - margin_h
            max_height = max(candidate_h, min_height)
            max_height = min(max_height, info.current_h)

    return max_width, max_height


def compute_layout(
    entry: MazeEntry, window_limits: Tuple[int, int]
) -> Tuple[int, Tuple[int, int]]:
    # scale cell size so big mazes still fit
    max_width, max_height = window_limits
    grid_width_limit = max(1, max_width - PADDING * 2)
    grid_height_limit = max(1, max_height - (PADDING * 2 + LABEL_HEIGHT))

    if entry.rows == 0 or entry.cols == 0:
        cell_size = MIN_CELL_SIZE
    else:
        raw_cell = min(
            MAX_CELL_SIZE,
            grid_width_limit / entry.cols,
            grid_height_limit / entry.rows,
        )
        if raw_cell >= MIN_CELL_SIZE:
            cell_size = max(MIN_CELL_SIZE, int(raw_cell))
        else:
            cell_size = max(1, int(raw_cell))

        if raw_cell > cell_size and cell_size < MAX_CELL_SIZE:
            test_size = cell_size + 1
            if (
                test_size * entry.cols + PADDING * 2 <= max_width
                and test_size * entry.rows + PADDING * 2 + LABEL_HEIGHT <= max_height
            ):
                cell_size = test_size

    width = cell_size * entry.cols + PADDING * 2
    height = cell_size * entry.rows + PADDING * 2 + LABEL_HEIGHT

    while (width > max_width or height > max_height) and cell_size > 1:
        cell_size -= 1
        width = cell_size * entry.cols + PADDING * 2
        height = cell_size * entry.rows + PADDING * 2 + LABEL_HEIGHT

    return cell_size, (width, height)


def draw_maze(
    surface: pygame.Surface,
    font: pygame.font.Font,
    entry: MazeEntry,
    controller: AnimationController,
    cell_size: int,
) -> None:
    surface.fill(COLOR_BACKGROUND)

    label = font.render(entry.file_path.name, True, COLOR_TEXT)
    label_top = 8
    label_rect = surface.blit(label, (PADDING, label_top))

    algo_text = font.render(f"path: {controller.current_algorithm}", True, COLOR_TEXT)
    algo_y = label_rect.bottom + 4
    max_algo_y = LABEL_HEIGHT - algo_text.get_height()
    if algo_y > max_algo_y:
        algo_y = max_algo_y
    surface.blit(algo_text, (PADDING, algo_y))

    algorithm, visited, path, _visited_active, _path_active = controller.progress()
    visited_set = set(visited)
    path_set = set(path)
    visit_color = COLOR_BFS if algorithm == "bfs" else COLOR_DFS

    origin_x = PADDING
    origin_y = PADDING + LABEL_HEIGHT

    for row_index, row in enumerate(entry.grid):
        for col_index, cell in enumerate(row):
            x = origin_x + col_index * cell_size
            y = origin_y + row_index * cell_size
            rect = pygame.Rect(x, y, cell_size, cell_size)
            coord = (row_index, col_index)

            if cell == "0":
                base_color = COLOR_WALL
            elif coord == entry.start:
                base_color = COLOR_START
            elif coord == entry.goal:
                base_color = COLOR_GOAL
            else:
                base_color = COLOR_FLOOR

            pygame.draw.rect(surface, base_color, rect)

            if coord in visited_set:
                shrink = max(2, cell_size // 3)
                overlay = rect.inflate(-shrink, -shrink)
                pygame.draw.rect(surface, visit_color, overlay)

            if coord in path_set:
                shrink = max(2, cell_size // 2)
                overlay = rect.inflate(-shrink, -shrink)
                pygame.draw.rect(surface, COLOR_PATH, overlay)

            if coord == entry.start:
                shrink = max(2, cell_size // 2)
                marker = rect.inflate(-shrink, -shrink)
                pygame.draw.rect(surface, COLOR_START, marker)
            elif coord == entry.goal:
                shrink = max(2, cell_size // 2)
                marker = rect.inflate(-shrink, -shrink)
                pygame.draw.rect(surface, COLOR_GOAL, marker)

            pygame.draw.rect(surface, COLOR_GRID, rect, width=1)


def main() -> None:
    # setup pygame basics
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont(None, FONT_SIZE)
    window_limits = determine_window_limits()

    if len(sys.argv) > 1:
        files = [Path(arg) for arg in sys.argv[1:]]
    else:
        files = collect_default_files()

    mazes = load_mazes(files)
    controller = AnimationController(mazes)

    current_entry = controller.current
    current_cell_size, window_size = compute_layout(current_entry, window_limits)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption(current_entry.file_path.name)

    current_size = window_size
    clock = pygame.time.Clock()

    running = True
    finished = False
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # listen for simple controls
                if event.key == pygame.K_b:
                    controller.set_algorithm("bfs")
                    finished = False
                elif event.key == pygame.K_d:
                    controller.set_algorithm("dfs")
                    finished = False
                elif event.key == pygame.K_RIGHT:
                    if controller.next_maze():
                        finished = False
                        current_entry = controller.current
                        current_cell_size, new_size = compute_layout(
                            current_entry, window_limits
                        )
                        if new_size != current_size:
                            screen = pygame.display.set_mode(new_size)
                        current_size = new_size
                        pygame.display.set_caption(current_entry.file_path.name)
                elif event.key == pygame.K_LEFT:
                    if controller.prev_maze():
                        finished = False
                        current_entry = controller.current
                        current_cell_size, new_size = compute_layout(
                            current_entry, window_limits
                        )
                        if new_size != current_size:
                            screen = pygame.display.set_mode(new_size)
                        current_size = new_size
                        pygame.display.set_caption(current_entry.file_path.name)

        if not running:
            break

        if not finished:
            finished, switched = controller.update(dt)
            if switched:
                current_entry = controller.current
                current_cell_size, new_size = compute_layout(
                    current_entry, window_limits
                )
                if new_size != current_size:
                    screen = pygame.display.set_mode(new_size)
                current_size = new_size
                pygame.display.set_caption(current_entry.file_path.name)

        draw_maze(screen, font, controller.current, controller, current_cell_size)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
