from collections import deque


class Node:
    # nodo simple con hijos y padre
    def __init__(self, coord, parent=None):
        self.coord = coord
        self.parent = parent
        self.hijos = []


def read_maze(path):
    # lee datos del laberinto
    with open(path, "r", encoding="utf-8") as fh:
        header = fh.readline().strip()
        if not header:
            raise ValueError("archivo vacío: " + path)
        filas, cols = map(int, header.split())

        grid = []
        start = None
        goal = None

        for r in range(filas):
            line = fh.readline()
            if not line:
                raise ValueError("faltan filas en " + path)
            row = list(line.strip())
            if len(row) != cols:
                raise ValueError(
                    f"ancho raro en fila {r} ({len(row)} vs {cols}) en {path}"
                )
            grid.append(row)
            for c, ch in enumerate(row):
                if ch == "A":
                    start = (r, c)
                elif ch == "B":
                    goal = (r, c)

        if start is None or goal is None:
            raise ValueError("sin A o B en " + path)

    return grid, start, goal


def walkable(ch):
    # celdas donde se puede pasar
    return ch in {"1", "A", "B"}


def vecinos(grid, r, c):
    # usa nesw para explorar rapido
    moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    filas, cols = len(grid), len(grid[0])
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < filas and 0 <= nc < cols and walkable(grid[nr][nc]):
            yield nr, nc


def reconstruir(desde):
    # arma ruta subiendo por padres
    if desde is None:
        return []
    ruta = []
    nodo = desde
    while nodo is not None:
        ruta.append(nodo.coord)
        nodo = nodo.parent
    ruta.reverse()
    return ruta


def dfs_pre(grid, start, goal):
    # dfs iterativo en preorden
    raiz = Node(start)
    stack = [raiz]
    visitados = []
    vistos = {start}
    meta = None

    while stack:
        nodo = stack.pop()
        visitados.append(nodo.coord)
        if nodo.coord == goal:
            meta = nodo
            break
        r, c = nodo.coord
        hijos = list(vecinos(grid, r, c))
        for nr, nc in reversed(hijos):
            if (nr, nc) not in vistos:
                child = Node((nr, nc), parent=nodo)
                nodo.hijos.append(child)
                vistos.add((nr, nc))
                stack.append(child)

    return visitados, raiz, meta


def bfs(grid, start, goal):
    # bfs usando queue
    raiz = Node(start)
    queue = deque([raiz])
    visitados = []
    vistos = {start}
    meta = None

    while queue:
        nodo = queue.popleft()
        visitados.append(nodo.coord)
        if nodo.coord == goal:
            meta = nodo
            break
        r, c = nodo.coord
        for nr, nc in vecinos(grid, r, c):
            if (nr, nc) not in vistos:
                child = Node((nr, nc), parent=nodo)
                nodo.hijos.append(child)
                vistos.add((nr, nc))
                queue.append(child)

    return visitados, raiz, meta


def fmt_coords(coords):
    # formato simple de coordenadas
    return "[" + ", ".join(f"({r},{c})" for r, c in coords) + "]"


def solve_file(path):
    # carga laberinto y muestra recorridos
    grid, start, goal = read_maze(path)

    dfs_order, _dfs_raiz, dfs_meta = dfs_pre(grid, start, goal)
    bfs_order, _bfs_raiz, bfs_meta = bfs(grid, start, goal)

    dfs_path = reconstruir(dfs_meta)
    bfs_path = reconstruir(bfs_meta)

    print(f"\n=== {path} ===")
    print("dfs_preorden:", fmt_coords(dfs_order))
    print("dfs_camino:", fmt_coords(dfs_path))
    print("bfs_recorrido:", fmt_coords(bfs_order))
    print("bfs_camino:", fmt_coords(bfs_path))


def main():
    # lista fija de archivos
    archivos = [
        "laberinto_1.in.txt",
        "laberinto_2.in.txt",
        "laberinto_3.in.txt",
    ]
    for archivo in archivos:
        try:
            solve_file(archivo)
        except FileNotFoundError:
            print(f"\n(no se encontró {archivo})")
        except Exception as err:
            print(f"\nerror con {archivo}: {err}")


if __name__ == "__main__":
    main()

# para correr en la terminal:
# python3 mazevis.py
