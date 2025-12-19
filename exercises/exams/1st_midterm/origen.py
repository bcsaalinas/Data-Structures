t = int(input())
stack = []
for i in range(t):
    s = input()
    ws = s.split()
    if ws[0] == "Durmiente":
        stack.append(ws[1])
    elif ws[0] == "Escaneo":
        if len(stack):
            print(stack[-1])
        else:
            print("REALIDAD")
    elif stack:
        stack.pop()
