import random

class Dados:

    def __init__(self):
        self.dado1 = 0
        self.dado2 = 0
        self.es_par = False

    def lanzar(self):
        self.dado1 = random.randrange(1, 7)
        self.dado2 = random.randrange(1, 7)
        if self.dado1 == self.dado2:
            self.es_par = True
        else:
            self.es_par = False
        return (self.dado1, self.dado2)

    def lanzar_uno(self):
        self.dado1 = random.randrange(1, 7)
        self.dado2 = 0
        self.es_par = False
        return self.dado1

    def valor(self):
        return (self.dado1, self.dado2)