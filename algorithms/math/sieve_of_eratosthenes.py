n = int(input())
if n <= 10 or n % 10 != 0:
    print("Error")
else:
    es_primo = [True] * n
    es_primo[0] = False
    es_primo[1] = False
    limite = int((n - 1) ** 0.5) + 1
    for i in range(2, limite):
        if es_primo[i]:
            for j in range(i * i, n, i):
                es_primo[j] = False
    for i in range(n):
        print(0 if es_primo[i] else 1, end=" ")
        if (i + 1) % 10 == 0:
            print()
