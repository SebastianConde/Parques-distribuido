from tablero import Tablero
from jugador import Jugador
from dados import Dados  
from constantes import TipoDeCelda

class Parques:
    def __init__(self):
        self.tablero = Tablero()
        self.jugadores = []
        self.dados = Dados()
        self.jugador_actual = None
        self.ganador = None
    
    def agregar_jugador(self, nombre, color):
        jugador = Jugador(nombre, color, self.tablero.casillas[TipoDeCelda.CARCEL][color - 1])
        self.jugadores.append(jugador)
    def iniciar(self, jugador):
        self.jugador_actual = jugador
        jugador.turno = True
    def lanzar_dados(self):
        return self.dados.lanzar()
    def mover_ficha(self, ficha, cantidad):
        return self.tablero.mover_ficha(ficha, cantidad)
    
    def cambiar_turno(self):
        self.jugador_actual.turno = False
        self.jugador_actual = self.jugadores[(self.jugadores.index(self.jugador_actual) + 1) % len(self.jugadores)]
        self.jugador_actual.turno = True

    def movimiento_fichas(self, valor_dado1, valor_dado2, ficha1, ficha2):
        ficha1 = self.jugador_actual.fichas[ficha1]
        ficha2 = self.jugador_actual.fichas[ficha2]
        # Mover la primera ficha
        if ficha1.puede_moverse:
            print(f"Ficha {ficha1.numero} se mueve {valor_dado1} casillas")
            if not self.mover_ficha(ficha1, valor_dado1):
                return False  
            print(f"Posición actual: {ficha1.casilla.numero}")
    
        # Mover la segunda ficha
        if ficha2.puede_moverse:
            print(f"Ficha {ficha2.numero} se mueve {valor_dado2} casillas")
            if not self.mover_ficha(ficha2, valor_dado2):
                return False  
            print(f"Posición actual: {ficha2.casilla.numero}")

        nuevas_pos_fichas = self.obtener_posiciones_fichas()

        if self.tablero.verificar_ganador(self.jugador_actual.color):
            self.ganador = self.jugador_actual
        return nuevas_pos_fichas
    
    def obtener_posiciones_fichas(self):
        return [ficha.casilla.numero for ficha in self.jugador_actual.fichas]

    def jugar(self):
        while self.ganador is None:
            print(f"Turno de {self.jugador_actual.nombre}")
            input("Presione Enter para lanzar los dados")
            if self.jugador_actual.en_carcel:
                for i in range(3):
                    valor = self.lanzar_dados()
                    suma_dados = sum(valor)
                    print(f"Valor de los dados: {valor}")
                    if self.dados.es_par:
                        for ficha in self.jugador_actual.fichas:
                            self.tablero.salir_de_carcel(ficha)
                            print(f"Ficha {ficha.numero} ha salido de la carcel")
                        self.jugador_actual.en_carcel = False
                        break
                if not self.dados.es_par:
                    self.cambiar_turno()
                    continue
            else:
                valor = self.lanzar_dados()
                suma_dados = sum(valor)
                print(f"Valor de los dados: {valor}")
                if self.dados.es_par:
                    self.jugador_actual.pares_consecutivos += 1
                    if self.jugador_actual.pares_consecutivos == 3:
                        # Agregar lógica para sacar una ficha
                        self.jugador_actual.pares_consecutivos = 0
                        self.cambiar_turno()
                        #continue
                    else:
                        mover = self.movimiento_fichas(suma_dados)
                else:
                    self.jugador_actual.pares_consecutivos = 0
                    mover = self.movimiento_fichas(suma_dados)
                    self.cambiar_turno()
                if not mover:
                    print("Jugada inválida")
            

if __name__ == "__main__":
    parques = Parques()
    parques.agregar_jugador("Jugador 1", 1)
    parques.agregar_jugador("Jugador 2", 2)
    parques.agregar_jugador("Jugador 3", 3)
    parques.agregar_jugador("Jugador 4", 4)
    parques.iniciar(parques.jugadores[0])
    parques.jugar()
    print(f"El ganador es {parques.ganador.nombre}")