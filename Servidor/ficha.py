class Ficha:

    def __init__(self, color, numero, casilla):
        self.numero = numero # 1, 2, 3, 4
        self.color = color # 1: Rojo, 2: Amarillo, 3: Azul, 4: Verde
        self.casilla = casilla # Celda actual
        self.contador = 0 # -1, -2, -3, -4 , ...
        self.puede_moverse = False
    
    def mover(self, valor):
        self.contador -= valor
        if self.contador == -72 :
            self.puede_moverse = False # Llego a la meta
        