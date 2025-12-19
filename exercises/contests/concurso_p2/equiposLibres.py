from collections import Counter

apariciones = Counter()
proyectos = {}
llaveActual = None

while True:
    inp = input().strip()
    if inp == "1":
        break
    elif inp.isupper() == True:
        llaveActual = inp
        proyectos.setdefault(llaveActual, set())
    else:
        if not proyectos:
            print("Error, animal, escribe bien ")
            break
        else:
            proyectos[llaveActual].add(inp)

for integrantes in proyectos.values():
    apariciones.update(integrantes)

duplicados = {alumno for alumno, veces in apariciones.items() if veces > 1}


for llave in proyectos:
    proyectos[llave] -= duplicados


ordenados = sorted(proyectos.items(), key=lambda item: (-len(item[1]), item[0]))

for llave, miembros in ordenados:
    print(f"{llave} {len(miembros)}")
