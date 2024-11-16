import pygame
import sys
import MapeoTablero as MP

class JuegoParques:
    def __init__(self, jugadores, nombre_jugador, color_dict):
        pygame.init()
        self.WIDTH, self.HEIGHT = 900, 700
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Parqués")
        
        # Cargar y escalar imágenes
        self.tablero = pygame.transform.scale(pygame.image.load("images/tablero.jpeg"), (self.WIDTH-200, self.HEIGHT))
        self.ficha_roja = pygame.transform.scale(pygame.image.load("images/ficha_roja.png"), (20, 20))
        self.ficha_amarilla = pygame.transform.scale(pygame.image.load("images/ficha_amarilla.png"), (20, 20))
        self.ficha_verde = pygame.transform.scale(pygame.image.load("images/ficha_verde.png"), (20, 20))
        self.ficha_azul = pygame.transform.scale(pygame.image.load("images/ficha_azul.png"), (20, 20))

        # Cargar imagenes de los dados
        self.dado ={
            1: pygame.transform.scale(pygame.image.load("images/1_dot.png"), (90, 90)),
            2: pygame.transform.scale(pygame.image.load("images/2_dots.png"), (90, 90)),
            3: pygame.transform.scale(pygame.image.load("images/3_dots.png"), (90, 90)),
            4: pygame.transform.scale(pygame.image.load("images/4_dots.png"), (90, 90)),
            5: pygame.transform.scale(pygame.image.load("images/5_dots.png"), (90, 90)),
            6: pygame.transform.scale(pygame.image.load("images/6_dots.png"), (90, 90))
        }
        
        # Modificar la estructura de jugadores para incluir más información
        self.jugadores = {}
        
        # Mapeo de colores numéricos a valores RGB
        colores = {
            1: (244, 110, 110),  # Rojo
            2: (255, 255, 255),    # Amarillo
            3: (0, 0, 255),      # Azul
            4: (0, 255, 0)       # Verde
        }
        
        # Lista de posiciones asociadas a cada color
        posiciones = {
            1: MP.carceles["ROJA"],
            2: MP.carceles["AMARILLA"],
            3: MP.carceles["AZUL"],
            4: MP.carceles["VERDE"]
        }
        
        # Asignar nombre y color a cada jugador
        for nombre, color_num in jugadores:
            self.jugadores[nombre] = {
                "nombre": nombre,
                "color_num": int(color_num),
                "color": colores.get(int(color_num), (0, 0, 0)), 
                "pos": posiciones.get(int(color_num), (0, 0)), # Posición de su carcel
                "posiciones": [-1, -1, -1, -1]  # Posiciones iniciales de las fichas
            }

        self.num_fichas = 4
        self.font = pygame.font.Font(None, 36)
        self.font_mensajes = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
        # Nuevas variables para manejo de mensajes y entrada de texto
        self.mensaje_actual = ""
        self.mensaje_dados = ""
        self.tiempo_mensaje_dados = 0
        self.tiempo_mensaje = 0

        self.nombre_jugador = nombre_jugador
        self.color_dict = color_dict

        #Posición de las fichas en pixeles
        self.coordenadas_fichas = {}

    def actualizar_posiciones(self, nombre_jugador, nuevas_posiciones):
        """Actualiza las posiciones de las fichas de un jugador específico"""
        if nombre_jugador in self.jugadores:
            self.jugadores[nombre_jugador]["posiciones"] = nuevas_posiciones

    def dibujar_tablero(self):
        self.window.blit(self.tablero, (0, 0))
        pygame.draw.rect(self.window, (192, 192, 192), (700, 0, 200, 700))

    def dibujar_jugadores(self): 
        """Dibuja los nombres y fichas de todos los jugadores según su color y posición"""
        for datos in self.jugadores.values(): 
            nombre = datos["nombre"]
            color = datos.get("color_num", 1)  # Obtiene el número de color, default 1
            
            # Dibuja el nombre del jugador
            texto = self.font.render(nombre, True, datos["color"])
            
            # Determinar la posición del nombre según el color
            if color == 1:  # Rojo
                pos_nombre = (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 30)
                ficha = self.ficha_roja
            elif color == 2:  # Amarillo
                pos_nombre = (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 30)
                ficha = self.ficha_amarilla
            elif color == 3:  # Azul
                pos_nombre = (MP.carceles["AZUL"][0], MP.carceles["AZUL"][1] + 30)
                ficha = self.ficha_azul
            elif color == 4:  # Verde
                pos_nombre = (MP.carceles["VERDE"][0], MP.carceles["VERDE"][1] + 30)
                ficha = self.ficha_verde
                
            # Dibuja el nombre
            self.window.blit(texto, pos_nombre)

        for datos in self.jugadores.values():
            nombre = datos["nombre"]
            color = datos.get("color_num", 1)  # Obtiene el número de color, default 1
            ficha = None
            if color == 1:  # Rojo
                ficha = self.ficha_roja
            elif color == 2:  # Amarillo
                ficha = self.ficha_amarilla
            elif color == 3:  # Azul
                ficha = self.ficha_azul
            elif color == 4:  # Verde
                ficha = self.ficha_verde
            for pos in self.jugadores[nombre]["posiciones"]: 
                if pos == -1: # En la cárcel
                    for i in range(self.num_fichas):
                        pos_x = self.jugadores[nombre]["pos"][0] + i * 40 + 40
                        pos_y =self.jugadores[nombre]["pos"][1] + 100
                        self.window.blit(ficha, (pos_x, pos_y))
                elif pos == 0: # En el inicio
                    if color == 1:  # Rojo
                        for i in range(self.num_fichas):
                            self.coordenadas_fichas[i] = (MP.seguros_inicios["ROJO_INICIO"][0] + i * 20, MP.seguros_inicios["ROJO_INICIO"][1] + 5)
                            self.window.blit(ficha, (MP.seguros_inicios["ROJO_INICIO"][0] + i * 20, 
                                            MP.seguros_inicios["ROJO_INICIO"][1] + 5))
                    elif color == 2:  # Amarillo
                        for i in range(self.num_fichas):
                            self.coordenadas_fichas[i] = (MP.seguros_inicios["AMARILLO_INICIO"][0] + 5, MP.seguros_inicios["AMARILLO_INICIO"][1] + i * 20)
                            self.window.blit(ficha, (MP.seguros_inicios["AMARILLO_INICIO"][0] + 5, 
                                            MP.seguros_inicios["AMARILLO_INICIO"][1] + i * 20))
                    elif color == 3:  # Azul
                        for i in range(self.num_fichas):
                            self.coordenadas_fichas[i] = (MP.seguros_inicios["AZUL_INICIO"][0] + i * 20, MP.seguros_inicios["AZUL_INICIO"][1] + 5)
                            self.window.blit(ficha, (MP.seguros_inicios["AZUL_INICIO"][0] + i * 20, 
                                            MP.seguros_inicios["AZUL_INICIO"][1] + 5))
                    elif color == 4:  # Verde
                        for i in range(self.num_fichas):
                            self.coordenadas_fichas[i] = (MP.seguros_inicios["VERDE_INICIO"][0] + 5, MP.seguros_inicios["VERDE_INICIO"][1] + i * 20)
                            self.window.blit(ficha, (MP.seguros_inicios["VERDE_INICIO"][0] + 5, 
                                            MP.seguros_inicios["VERDE_INICIO"][1] + i * 20))

                                    
    def crear_ventana_dados(self, x, y, valor1, valor2):
        """Crea la ventana de los dados y obtiene los valores de los dados"""
        pygame.draw.rect(self.window, (255, 255, 255), (x-10, y-20, x+30, y), 5) # Dibujar el rectángulo
        self.window.blit(self.font.render(valor1, True, (0,0,0)), (x-10, y-20, x+10, y)) # Dibujar el valor del dado 1
        self.window.blit(self.font.render(valor2, True, (0,0,0)), (x+10, y-20, x+30, y)) # Dibujar el valor del dado 2

    def dibujar_seguros_iniciales(self):
        for i in range(self.num_fichas):
            self.window.blit(self.ficha_roja, (MP.seguros_inicios["ROJO_INICIO"][0] + i * 20, MP.seguros_inicios["ROJO_INICIO"][1] + 5))
            self.window.blit(self.ficha_azul, (MP.seguros_inicios["AZUL_INICIO"][0] + i * 20, MP.seguros_inicios["AZUL_INICIO"][1] + 5))
            self.window.blit(self.ficha_amarilla, (MP.seguros_inicios["AMARILLO_INICIO"][0] + 5, MP.seguros_inicios["AMARILLO_INICIO"][1] + i * 20))
            self.window.blit(self.ficha_verde, (MP.seguros_inicios["VERDE_INICIO"][0] + 5, MP.seguros_inicios["VERDE_INICIO"][1] + i * 20))

    def dibujar_metas(self):
        for i in range(self.num_fichas):
            self.window.blit(self.ficha_roja, (35 + MP.meta["ROJO8"][0] + i * 30, MP.meta["ROJO8"][1] + 20))
            self.window.blit(self.ficha_azul, (35 + MP.meta["AZUL8"][0] + i * 30, MP.meta["AZUL8"][1] - 40))
            self.window.blit(self.ficha_amarilla, (20 + MP.meta["AMARILLO8"][0], 35 + MP.meta["AMARILLO8"][1] + i * 30))
            self.window.blit(self.ficha_verde, (-40 + MP.meta["VERDE8"][0], 35 + MP.meta["VERDE8"][1] + i * 30))

    def mostrar_mensaje(self, mensaje):
        """Actualiza el mensaje actual y el tiempo de visualización"""
        self.mensaje_actual = mensaje
        self.tiempo_mensaje = pygame.time.get_ticks()

    def mostrar_mensaje_dados(self, mensaje):
        """Actualiza el mensaje actual y el tiempo de visualización"""
        self.mensaje_dados = mensaje
        self.tiempo_mensaje_dados = pygame.time.get_ticks()

    def dibujar_mensaje(self, y):
        """Dibuja el mensaje actual en el panel lateral con salto de línea automático"""
        if self.mensaje_actual:
            palabras = self.mensaje_actual.split()
            lineas = []
            linea_actual = []
            ancho_actual = 0
            
            # Procesar cada palabra
            for palabra in palabras:
                # Obtener el ancho de la palabra con el espacio
                palabra_surface = self.font_mensajes.render(palabra + " ", True, (0, 0, 0))
                ancho_palabra = palabra_surface.get_width()
                
                # Si agregar la palabra excede el ancho máximo, comenzar nueva línea
                if ancho_actual + ancho_palabra > 190:  # 190 para dejar un pequeño margen
                    lineas.append(" ".join(linea_actual)) 
                    linea_actual = [palabra] 
                    ancho_actual = ancho_palabra
                else:
                    linea_actual.append(palabra)
                    ancho_actual += ancho_palabra
            
            # Agregar la última línea si existe
            if linea_actual:
                lineas.append(" ".join(linea_actual))
            
            # Dibujar cada línea
            for linea in lineas:
                mensaje_surface = self.font_mensajes.render(linea, True, (0, 0, 0))
                self.window.blit(mensaje_surface, (705, y))
                y += self.font_mensajes.get_linesize()  # Aumentar y por el alto de la línea

    def dibujar_mensaje_dados(self, y):
        # Dibuja el mensaje de los dados si existe
        if self.mensaje_dados:
            palabras = self.mensaje_dados.split()
            lineas = []
            linea_actual = []
            ancho_actual = 0
            
            # Procesar cada palabra
            for palabra in palabras:
                # Obtener el ancho de la palabra con el espacio
                palabra_surface = self.font_mensajes.render(palabra + " ", True, (0, 0, 0))
                ancho_palabra = palabra_surface.get_width()
                
                # Si agregar la palabra excede el ancho máximo, comenzar nueva línea
                if ancho_actual + ancho_palabra > 190:  # 190 para dejar un pequeño margen
                    lineas.append(" ".join(linea_actual)) 
                    linea_actual = [palabra] 
                    ancho_actual = ancho_palabra
                else:
                    linea_actual.append(palabra)
                    ancho_actual += ancho_palabra
            
            # Agregar la última línea si existe
            if linea_actual:
                lineas.append(" ".join(linea_actual))
            
            # Dibujar cada línea
            for linea in lineas:
                mensaje_surface = self.font_mensajes.render(linea, True, (0, 0, 0))
                self.window.blit(mensaje_surface, (705, y))
                y += self.font_mensajes.get_linesize()  # Aumentar y por el alto de la línea

    def dibujar_dados(self, dado1, dado2):
        """Dibuja los dados en la pantalla y muestra el mensaje"""
        self.dibujar_mensaje_dados(120)

        self.window.blit(self.dado[dado1], (705, 500))
        self.window.blit(self.dado[dado2], (805, 500))

    def actualizar_pantalla(self):
        """Actualiza todos los elementos en la pantalla"""
        self.dibujar_tablero()
        self.dibujar_jugadores()
        self.dibujar_mensaje(30)

    def close(self):
        """Cierra la ventana del juego"""
        pygame.quit()

if __name__ == "__main__":
    juego = JuegoParques()
    juego.correr_juego()