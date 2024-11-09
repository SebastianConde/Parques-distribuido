from constantes import *


class Casilla:

    def __init__(self, numero, tipo, color=0):
        self.numero = numero
        self.tipo = tipo
        self.color = color # 0: Sin color, 1: Rojo, 2: Amarillo, 3: Azul, 4: Verde
        self.fichas = set()

    def agregar_ficha(self, ficha):
        self.fichas.add(ficha)
    def quitar_ficha(self, ficha):
        self.fichas.remove(ficha)