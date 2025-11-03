#!/usr/bin/env python3
"""Console-based maze search visualizer using BFS and DFS."""

from collections import deque


def parse_maze(maze_str):
    """Convert the multiline text maze into a 2D grid."""
    lines = maze_str.strip().splitlines()
    rows = []
    for line in lines:
        line = line.strip()
        if line:
            row = list(line)
            rows.append(row)

    if len(rows) == 0:
        raise ValueError("Maze string is empty.")

    expected_width = len(rows[0])
    for row in rows:
        if len(row) != expected_width:
            raise ValueError("Maze rows must all be the same length.")

    return rows


def locate_points(maze):
    """Find the positions of the start 'A' and goal 'B' in the grid."""
    start = None
    goal = None

    for row_index in range(len(maze)):
        for col_index in range(len(maze[row_index])):
            cell = maze[row_index][col_index]
            if cell == "A":
                start = (row_index, col_index)
            elif cell == "B":
                goal = (row_index, col_index)

    if start is None or goal is None:
        raise ValueError("Maze must contain both 'A' (start) and 'B' (goal).")
    return start, goal


def is_walkable(cell_value):
    """Return True if the cell can be traversed."""
    return cell_value != "0"


def neighbors(maze, node):
    """Return a list with the walkable neighbors in NESW order."""
    r, c = node
    deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Up, Right, Down, Left
    result = []
    for dr, dc in deltas:
        nr = r + dr
        nc = c + dc
        inside_rows = 0 <= nr < len(maze)
        inside_cols = 0 <= nc < len(maze[0])
        if inside_rows and inside_cols and is_walkable(maze[nr][nc]):
            result.append((nr, nc))
    return result


def reconstruct_path(parent_map, start, goal):
    """Rebuild the path from goal back to start using the recorded parents."""
    if goal not in parent_map:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent_map[current]
    path.reverse()

    if not path or path[0] != start:
        return []
    return path


def format_frontier(structure):
    """Render the queue/stack contents for the console output."""
    pieces = []
    for coord in structure:
        pieces.append(str(coord))
    return "[" + ", ".join(pieces) + "]"


def bfs_search(maze, start, goal):
    """Breadth-first search that prints its exploration in detail."""
    queue = deque([start])
    parent = {start: None}

    step = 0
    while queue:
        print("[BFS] Step " + str(step) + ": frontier before visit: " + format_frontier(queue))
        current = queue.popleft()
        print("[BFS] Visiting " + str(current))

        if current == goal:
            print("[BFS] Goal reached at " + str(current))
            return reconstruct_path(parent, start, goal)

        for neighbor in neighbors(maze, current):
            if neighbor in parent:
                continue
            parent[neighbor] = current
            queue.append(neighbor)
            print("[BFS]   Enqueued " + str(neighbor))

        print("[BFS] Frontier after expansion: " + format_frontier(queue) + "\n")
        step += 1

    print("[BFS] Goal not reachable from start.")
    return []


def dfs_search(maze, start, goal):
    """Depth-first search (iterative) with detailed console output."""
    stack = [start]
    parent = {start: None}

    step = 0
    while stack:
        print("[DFS] Step " + str(step) + ": frontier before visit: " + format_frontier(stack))
        current = stack.pop()
        print("[DFS] Visiting " + str(current))

        if current == goal:
            print("[DFS] Goal reached at " + str(current))
            return reconstruct_path(parent, start, goal)

        for neighbor in neighbors(maze, current):
            if neighbor in parent:
                continue
            parent[neighbor] = current
            stack.append(neighbor)
            print("[DFS]   Pushed " + str(neighbor))

        print("[DFS] Frontier after expansion: " + format_frontier(stack) + "\n")
        step += 1

    print("[DFS] Goal not reachable from start.")
    return []


def path_to_directions(path):
    """Translate the path into cardinal directions."""
    direction_map = {
        (-1, 0): "U",
        (1, 0): "D",
        (0, -1): "L",
        (0, 1): "R",
    }
    moves = []
    for index in range(len(path) - 1):
        r1, c1 = path[index]
        r2, c2 = path[index + 1]
        delta = (r2 - r1, c2 - c1)
        if delta in direction_map:
            moves.append(direction_map[delta])
        else:
            moves.append("?")
    return "".join(moves)


def describe_path(label, path):
    """Print the resulting path in coordinates and directions."""
    if not path:
        print(label + " path: No path found.\n")
        return

    directions = path_to_directions(path)
    if directions == "":
        directions = "(start equals goal)"
    print(label + " path (coordinates): " + str(path))
    print(label + " path (directions): " + directions + "\n")


def main():
    maze_text = """
    0001001
    1001010
    100B100
    0001000
    000A100
    """
    maze = parse_maze(maze_text)
    start, goal = locate_points(maze)

    print("=== Breadth-First Search ===")
    bfs_path = bfs_search(maze, start, goal)
    describe_path("BFS", bfs_path)

    print("=== Depth-First Search ===")
    dfs_path = dfs_search(maze, start, goal)
    describe_path("DFS", dfs_path)


if __name__ == "__main__":
    main()
