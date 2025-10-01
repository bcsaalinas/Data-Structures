class Mapa:
    def __init__(self, tam):
        self.mapa = [False] * tam
        self.tamaño = tam

    def numerificar(self, elemento):
        return hash(elemento)

    def agregar(self, elemento):
        pos = self.numerificar(elemento) % self.tamaño

    def buscar(self, elemento):
        pos = self.numerificar(elemento) % self.tamaño
        if self.mapa[pos] == True:
            print("Si esta apa")
            return True
        else:
            print("No esta pa")
            return False

    def __getitem__(self, elemento):
        return self.buscar(elemento)


mi_mapa = Mapa(100)
mi_mapa.agregar("Hola")
mi_mapa["Hola"]
