caso = 1
while True:
    s = input()
    if s == "fin":
        break
    n_distinct = len(set(s))
    posible = []
    for i in range(0, len(s)):
        found = False
        for j in range(len(posible)):
            if ord(s[i]) <= posible[j]:
                posible[j] = ord(s[i])
                found = True
                break
        if not found:
            posible.append(ord(s[i]))
    print(f"Caso {caso}: {min(len(posible), n_distinct)}")
    caso += 1
