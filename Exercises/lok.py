n = int(input())

if n <= 10 or n % 10 != 0:
    print("Error")
else:
    es_primo = [True] * n
    es_primo[0] = False
    es_primo[1] = False
    limite = ((n - 1) * 0.5) + 1
