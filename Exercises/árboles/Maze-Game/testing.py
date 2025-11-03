with open("laberinto_1.in.txt", "r", encoding="utf8") as f:
    firstLine = f.readline().strip()
    rows, cols = map(int, firstLine.split())
    print(rows, cols)
