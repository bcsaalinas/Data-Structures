from dynamicArr import Arreglo_Dinamico


class Stack(Arreglo_Dinamico):
    def __init__(self):
        super().__init__()

    def push(self, x):
        return self.insertar_elemento(x)

    def pop(self):
        return self.eliminar_elemento()

    def size(self):
        return len(self)


if __name__ == "__main__":
    s = Stack()
    for v in [1, 2, 3]:
        s.push(v)
    print(s)
    print(s.pop())
    print(s)
    