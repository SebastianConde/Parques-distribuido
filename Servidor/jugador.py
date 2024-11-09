from ficha import Ficha

class Jugador:

    def __init__(self, nombre, color, casilla_carcel):
        self.nombre = nombre
        self.color = color # 1: Rojo, 2: Amarillo, 3: Azul, 4: Verde
        self.turno = False
        self.pares_consecutivos = 0
        self.en_carcel = True
        self.fichas = [
            Ficha(self.color, 1, casilla_carcel),
            Ficha(self.color, 2, casilla_carcel),
            Ficha(self.color, 3, casilla_carcel),
            Ficha(self.color, 4, casilla_carcel),
        ]
            