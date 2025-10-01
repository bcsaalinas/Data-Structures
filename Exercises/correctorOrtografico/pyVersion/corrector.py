file = open("lemario.txt")
datos = file.readlines()

lemario_set = set()
for dato in datos:
    lemario_set.add(dato.rstrip("\n"))


def funciones(palabrasLower):
    letras = "abcdefghijklmnopqrstuvwxyzáéíóúüñ"
    variaciones = set()

    for i in range(len(palabrasLower) - 1):
        variacion = (
            palabrasLower[:i]
            + palabrasLower[i + 1]
            + palabrasLower[i]
            + palabrasLower[i + 2 :]
        )
        if variacion in lemario_set:
            variaciones.add(variacion)

    for i in range(len(palabrasLower) + 1):
        for letra in letras:
            variacion = palabrasLower[:i] + letra + palabrasLower[i:]
            if variacion in lemario_set:
                variaciones.add(variacion)

    for i in range(len(palabrasLower)):
        variacion = palabrasLower[:i] + palabrasLower[i + 1 :]
        if variacion in lemario_set:
            variaciones.add(variacion)

    for i in range(len(palabrasLower)):
        for letra in letras:
            if letra != palabrasLower[i]:
                variacion = palabrasLower[:i] + letra + palabrasLower[i + 1 :]
                if variacion in lemario_set:
                    variaciones.add(variacion)

    return variaciones


def corregir_frase(frase):
    palabras = frase.split()
    palabras_corregidas = []
    for palabra in palabras:
        if palabra in lemario_set:
            palabras_corregidas.append(palabra)
        else:
            variaciones = list(funciones(palabra))
            if variaciones:
                print(
                    f"la palabra '{palabra}' no está en el lemario, variaciones encontradas:"
                )
                for i, var in enumerate(variaciones):
                    print(f"{i + 1}. {var}")
                eleccion = input(
                    "cual palabra quieres (numero o 'igual' para dejarla igual): "
                )
                if eleccion == "igual":
                    palabras_corregidas.append(palabra)
                else:
                    palabras_corregidas.append(variaciones[int(eleccion) - 1])
            else:
                palabras_corregidas.append(palabra)
    return " ".join(palabras_corregidas)


print(corregir_frase(input("Introduce una frase: ")))
