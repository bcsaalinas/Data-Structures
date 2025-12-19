class Arreglo_Dinamico:
    def __init__(self):
        self.datos = []
        self.capacidad = 0
        self.tamano = 0

    def insertar_elemento(self, x):
        if self.capacidad == 0:
            self.capacidad = 1
        if self.capacidad == self.tamano:
            self.capacidad = 2*self.capacidad
        nuevo_arr = [0] * self.capacidad
        for i in range(0,self.tamano):
            nuevo_arr[i] = self.datos[i]
        nuevo_arr[self.tamano] = x
        self.tamano+=1
        self.datos = nuevo_arr

    def __repr__(self):
            return str(self.datos[0:self.tamano])
    
    def eliminar_elemento(self):
        if self.tamano < 1:
            print("no se puede sonso")
            return None
        eliminado = self.datos[self.tamano - 1]
        if (self.capacidad * 1/2) > self.tamano:
            self.capacidad = int(self.capacidad * 3/4) or 1
            self.tamano -= 1
            nuevo_arr = [0] * self.capacidad
            for i in range(0, self.tamano):
                nuevo_arr[i] = self.datos[i]
            self.datos = nuevo_arr
        else:
            self.tamano -= 1
            if self.tamano >= 0:
                self.datos[self.tamano] = 0
        return eliminado


arr = Arreglo_Dinamico()
print(arr)
for i in range(1, 11):
    arr.insertar_elemento(i)
    print(arr)
print(arr.eliminar_elemento())
print(arr)