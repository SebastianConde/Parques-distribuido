from ficha import Ficha
from constantes import Color, TipoDeCelda
from casilla import Casilla


class Tablero:
    def __init__(self):
        self.casillas = dict(
            {
                TipoDeCelda.NORMAL: [],
                TipoDeCelda.CAMINO_CIELO: [],
                TipoDeCelda.CARCEL: [],
                TipoDeCelda.CIELO: [],
            }
        )
        self.construir_tablero()

    def construir_tablero(self):
        for i in range(1, 69):
            tipo_celda = None
            if i in [6, 23, 40, 57]:
                tipo_celda = TipoDeCelda.SALIDA
            elif i in [13, 30, 47, 64]:
                tipo_celda = TipoDeCelda.SEGURO
            elif i in [1, 18, 35, 52]:
                tipo_celda = TipoDeCelda.LLEGADA
            else:
                tipo_celda = TipoDeCelda.NORMAL
            self.casillas[TipoDeCelda.NORMAL].append(Casilla(i, tipo_celda))
        colores = Color().colores
        for index_color in range(1, len(colores) + 1):
            for i in range(1, 9):
                self.casillas[TipoDeCelda.CAMINO_CIELO].append(
                    Casilla(i, TipoDeCelda.CAMINO_CIELO, index_color)
                )
            self.casillas[TipoDeCelda.CIELO].append(
                Casilla(index_color, TipoDeCelda.CIELO, index_color)
            )
            self.casillas[TipoDeCelda.CARCEL].append(
                Casilla(index_color, TipoDeCelda.CARCEL, index_color)
            )
        #print(self.casillas)

    def __str__(self):
        return str(self.casillas)

    def salir_de_carcel(self, ficha):
        ficha.contador = -1
        if ficha.color == 1:
            ficha.casilla = self.casillas[TipoDeCelda.NORMAL][5]
        elif ficha.color == 2:
            ficha.casilla = self.casillas[TipoDeCelda.NORMAL][22]
        elif ficha.color == 3:
            ficha.casilla = self.casillas[TipoDeCelda.NORMAL][39]
        elif ficha.color == 4:
            ficha.casilla = self.casillas[TipoDeCelda.NORMAL][56]
        ficha.casilla.agregar_ficha(ficha)
        ficha.puede_moverse = True

    def enviar_a_carcel(self, ficha):
        ficha.contador = 0
        ficha.casilla.quitar_ficha(ficha)
        ficha.casilla = self.casillas[TipoDeCelda.CARCEL][ficha.color - 1]
        ficha.casilla.agregar_ficha(ficha)
        ficha.puede_moverse = False

    def comer_ficha(self, ficha_nueva):
        # Verificar si la casilla a la que se mueve tiene fichas de otro color
        if len(ficha_nueva.casilla.fichas) > 1 and not self.verificar_seguro(ficha_nueva):
            # Hacer una copia de las fichas para iterar de forma segura
            fichas_a_comer = list(ficha_nueva.casilla.fichas)
            for ficha in fichas_a_comer:
                if ficha.color != ficha_nueva.color:
                    self.enviar_a_carcel(ficha)
                    print(f"La ficha {ficha.color} ha sido enviada a la carcel")


    def verificar_ganador(self, color):
        casilla = self.casillas[TipoDeCelda.CIELO][color - 1]
        if len(casilla.fichas) == 4:
            return True
        return False

    def verificar_seguro(self, ficha):
        if (
            ficha.casilla.tipo == TipoDeCelda.SEGURO
            or ficha.casilla.tipo == TipoDeCelda.LLEGADA
            or ficha.casilla.tipo == TipoDeCelda.SALIDA
        ):
            return True
        return False
    
    def mover_ficha(self, ficha, cantidad):
        if cantidad - ficha.contador > 72:
            print("Movimiento no permitido")
            print("Como quedaría el contador si se mueve", ficha.contador - cantidad)
            return False
        key_casillas = TipoDeCelda.NORMAL if (ficha.casilla.tipo == TipoDeCelda.SEGURO
            or ficha.casilla.tipo == TipoDeCelda.LLEGADA
            or ficha.casilla.tipo == TipoDeCelda.SALIDA) else ficha.casilla.tipo
        index_casilla = self.casillas[key_casillas].index(ficha.casilla)
        ficha.casilla.quitar_ficha(ficha)
        ficha.mover(cantidad)
        if ficha.contador < -64 and ficha.contador > -72:
            print("Contador actual: ", ficha.contador)
            index = 8 * (ficha.color - 1) + abs(ficha.contador + 64) - 1
            print("index en el cielo: ", index)
            ficha.casilla = self.casillas[TipoDeCelda.CAMINO_CIELO][index]
        elif ficha.contador == -72:
            ficha.casilla = self.casillas[TipoDeCelda.CIELO][ficha.color-1]
        else:
            if index_casilla + cantidad > 67:
                index_casilla = index_casilla + cantidad - 68
            else:
                index_casilla = index_casilla + cantidad
            ficha.casilla = self.casillas[TipoDeCelda.NORMAL][index_casilla]
        ficha.casilla.agregar_ficha(ficha)
        self.comer_ficha(ficha) # Retorna el número y color de la ficha comida y si no hay retorna None
        self.verificar_ganador(ficha.color)
        return True
        



if __name__ == "__main__":
    tablero = Tablero()
    # for i in tablero.casillas[TipoDeCelda.CAMINO_CIELO]:
    #     print(i.numero, i.tipo, i.color)