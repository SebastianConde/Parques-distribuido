import pygame
import sys
import MapeoTablero as MP
import time

class JuegoParques:
    def __init__(self, jugadores, nombre_jugador, color_dict):
        pygame.init()
        self.WIDTH, self.HEIGHT = 900, 700
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Parqués")
        
        # Cargar y escalar imágenes
        self.tablero = pygame.transform.scale(pygame.image.load("images/tablero.jpeg"), (self.WIDTH-200, self.HEIGHT))

        if color_dict == 2:
            self.tablero = pygame.transform.rotate(self.tablero, 90) 
        elif color_dict == 1:
            self.tablero = pygame.transform.rotate(self.tablero, 180)
        elif color_dict == 4:
            self.tablero = pygame.transform.rotate(self.tablero, 270)

        self.ficha_roja = pygame.transform.scale(pygame.image.load("images/ficha_roja.png"), (20, 20))
        self.ficha_amarilla = pygame.transform.scale(pygame.image.load("images/ficha_amarilla.png"), (20, 20))
        self.ficha_verde = pygame.transform.scale(pygame.image.load("images/ficha_verde.png"), (20, 20))
        self.ficha_azul = pygame.transform.scale(pygame.image.load("images/ficha_azul.png"), (20, 20))

        # Cargar imagenes de los dados
        self.dado ={
            0: pygame.transform.scale(pygame.image.load("images/0_dot.png"), (90, 90)),
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
            if self.color_dict == 3:
                if color == 1:  # Rojo
                    pos_nombre = (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 30)
                elif color == 2:  # Amarillo
                    pos_nombre = (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 30)
                elif color == 3:  # Azul
                    pos_nombre = (MP.carceles["AZUL"][0] + 10, MP.carceles["AZUL"][1] + 30)
                elif color == 4:  # Verde
                    pos_nombre = (MP.carceles["VERDE"][0] + 10, MP.carceles["VERDE"][1] + 30)
            elif self.color_dict == 2:
                if color == 1: # Rojo
                    color = 2
                    pos_nombre = (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 30)
                elif color == 2: # Amarillo
                    color = 3
                    pos_nombre = (MP.carceles["AZUL"][0] + 10, MP.carceles["AZUL"][1] + 30)
                elif color == 3: # Azul
                    color = 4
                    pos_nombre = (MP.carceles["VERDE"][0] + 10, MP.carceles["VERDE"][1] + 30)
                elif color == 4: # Verde
                    color = 1
                    pos_nombre = (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 30)
            elif self.color_dict == 4:
                if color == 1: # Rojo
                    color = 4
                    pos_nombre = (MP.carceles["VERDE"][0] + 10, MP.carceles["VERDE"][1] + 30)
                elif color == 2: # Amarillo
                    color = 1
                    pos_nombre = (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 30)
                elif color == 3: # Azul
                    color = 2
                    pos_nombre = (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 30)
                elif color == 4: # Verde
                    color = 3
                    pos_nombre = (MP.carceles["AZUL"][0] + 10, MP.carceles["AZUL"][1] + 30)
            elif self.color_dict == 1: 
                if color == 1: # Rojo
                    color = 3
                    pos_nombre = (MP.carceles["AZUL"][0] + 10, MP.carceles["AZUL"][1] + 30)
                elif color == 2: # Amarillo
                    color = 4
                    pos_nombre = (MP.carceles["VERDE"][0] + 10, MP.carceles["VERDE"][1] + 30)
                elif color == 3: # Azul
                    color = 1
                    pos_nombre = (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 30)
                elif color == 4: # Verde
                    color = 2
                    pos_nombre = (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 30)

            # Dibuja el nombre
            self.window.blit(texto, pos_nombre)

        # Diccionario para contar cuántas fichas hay en cada casilla
        fichas_por_casilla = {}
        # Diccionario para guardar qué fichas están en cada casilla
        fichas_info_por_casilla = {}

        # Cambiar la posición de las fichas si el tablero está rotado
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

            for i, pos in enumerate(self.jugadores[nombre]["posiciones"]):
                if pos == -1: # En la cárcel
                    if self.color_dict == 3:
                        if color == 1:  # Rojo
                            self.window.blit(ficha, (MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100), color)
                        elif color == 2:  # Amarillo
                            self.window.blit(ficha, (MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100), color)
                        elif color == 3:  # Azul
                            self.window.blit(ficha, (MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100), color)
                        elif color == 4:  # Verde
                            self.window.blit(ficha, (MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100), color)
                    elif self.color_dict == 2:
                        if color == 1: # Rojo
                            self.window.blit(ficha, (MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100), color)
                        elif color == 2: # Amarillo
                            self.window.blit(ficha, (MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100), color)
                        elif color == 3: # Azul
                            self.window.blit(ficha, (MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100), color)
                        elif color == 4: # Verde
                            self.window.blit(ficha, (MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100), color)
                    elif self.color_dict == 4:
                        if color == 1: # Rojo
                            self.window.blit(ficha, (MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100), color)
                        elif color == 2: # Amarillo
                            self.window.blit(ficha, (MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100), color)
                        elif color == 3: # Azul
                            self.window.blit(ficha, (MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100), color)
                        elif color == 4: # Verde
                            self.window.blit(ficha, (MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100), color)
                    elif self.color_dict == 1:
                        if color == 1: # Rojo
                            self.window.blit(ficha, (MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AZUL"][0] + i * 40 + 40, MP.carceles["AZUL"][1] + 100), color)
                        elif color == 2: # Amarillo
                            self.window.blit(ficha, (MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["VERDE"][0] + i * 40 + 40, MP.carceles["VERDE"][1] + 100), color)
                        elif color == 3: # Azul
                            self.window.blit(ficha, (MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["ROJA"][0] + i * 40 + 40, MP.carceles["ROJA"][1] + 100), color)
                        elif color == 4: # Verde
                            self.window.blit(ficha, (MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100))
                            self.coordenadas_fichas[i] = ((MP.carceles["AMARILLA"][0] + i * 40 + 40, MP.carceles["AMARILLA"][1] + 100), color)
                elif pos == 0: # En el inicio
                    casilla_inicial = None
                    if self.color_dict == 3:
                        if color == 1:  # Rojo
                            casilla_inicial = 6
                        elif color == 2:  # Amarillo
                            casilla_inicial = 23
                        elif color == 3:  # Azul
                            casilla_inicial = 40
                        elif color == 4:  # Verde
                            casilla_inicial = 57
                    elif self.color_dict == 2:
                        if color == 1: # Rojo
                            casilla_inicial = 23
                        elif color == 2: # Amarillo
                            casilla_inicial = 40
                        elif color == 3: # Azul
                            casilla_inicial = 57
                        elif color == 4: # Verde
                            casilla_inicial = 6
                    elif self.color_dict == 4:
                        if color == 1: # Rojo
                            casilla_inicial = 57
                        elif color == 2: # Amarillo
                            casilla_inicial = 6
                        elif color == 3: # Azul
                            casilla_inicial = 23
                        elif color == 4: # Verde
                            casilla_inicial = 40
                    elif self.color_dict == 1:
                        if color == 1: # Rojo
                            casilla_inicial = 40
                        elif color == 2: # Amarillo
                            casilla_inicial = 57
                        elif color == 3: # Azul
                            casilla_inicial = 6
                        elif color == 4: # Verde
                            casilla_inicial = 23
                            
                        
                    if casilla_inicial is not None:
                        # Verificar si ya existe la casilla en los diccionarios
                        if casilla_inicial not in fichas_por_casilla:
                            fichas_por_casilla[casilla_inicial] = 0
                            fichas_info_por_casilla[casilla_inicial] = []
                            
                        # Verificar si esta ficha específica ya está en la lista
                        ficha_existente = False
                        for ficha_info in fichas_info_por_casilla[casilla_inicial]:
                            if ficha_info[2] == nombre and ficha_info[3] == i:  # Comparar nombre del jugador e índice de ficha
                                ficha_existente = True
                                break
                                
                        if not ficha_existente:
                            fichas_por_casilla[casilla_inicial] += 1
                            fichas_info_por_casilla[casilla_inicial].append((ficha, color, nombre, i))
                else: # En una casilla regular
                    if pos not in fichas_por_casilla:
                        fichas_por_casilla[pos] = 0
                        fichas_info_por_casilla[pos] = []
                    fichas_info_por_casilla[pos].append((ficha, color, nombre, i))
                    fichas_por_casilla[pos] += 1
        
        # Ahora dibujamos las fichas en las casillas regulares
        for casilla, fichas in fichas_info_por_casilla.items():
            # Obtener coordenadas de la casilla
            coords = None
            especial = False
            llegada = False
            if casilla in MP.casillas:
                coords = MP.casillas[casilla]
            elif casilla in MP.seguros:
                coords = MP.seguros[casilla]
            elif str(casilla) in MP.camino_cielo:
                coords = MP.camino_cielo[str(casilla)]
            elif casilla in MP.entrada_camino_cielo:
                coords = MP.entrada_camino_cielo[casilla]
            elif casilla in MP.esquinas:
                coords = MP.esquinas[casilla]
                especial = True
            elif casilla in MP.meta:
                coords = MP.meta[casilla]
                llegada = True
            
            if not coords:
                continue 

            # Calcular dimensiones de la casilla
            ancho_casilla = coords[2] - coords[0]
            alto_casilla = coords[3] - coords[1]

            tipo_casilla = None
            if ancho_casilla == 30:
                tipo_casilla = "vertical"
            else:
                tipo_casilla = "horizontal"                

            num_fichas = len(fichas)

            # Calcular posiciones según el número de fichas y orientación
            if not llegada:
                if num_fichas == 1:
                    x = coords[0] + (ancho_casilla - 20) / 2
                    y = coords[1] + (alto_casilla - 20) / 2
                    posiciones = [(x, y)]
                elif num_fichas == 2:
                    if not especial:
                        if tipo_casilla == "horizontal":
                            x1 = coords[0] + 5
                            x2 = coords[0] + ancho_casilla - 25
                            y = coords[1] + (alto_casilla - 20) / 2
                            posiciones = [(x1, y), (x2, y)]
                        else:  # vertical
                            x = coords[0] + (ancho_casilla - 20) / 2
                            y1 = coords[1] + 5
                            y2 = coords[1] + alto_casilla - 25
                            posiciones = [(x, y1), (x, y2)]
                    else:  # Esquina
                        if casilla == 9:
                            x1 = coords[0] + ancho_casilla - 50
                            x2 = coords[0] + ancho_casilla - 25
                            y = coords[1] + (alto_casilla - 20) / 2
                            posiciones = [(x1, y), (x2, y)]
                        elif casilla == 10:
                            x = coords[0] + (ancho_casilla - 20) / 2
                            y1 = coords[1] + alto_casilla - 50
                            y2 = coords[1] + alto_casilla - 25
                            posiciones = [(x, y1), (x, y2)]
                        elif casilla == 26:
                            x = coords[0] + (ancho_casilla - 20) / 2
                            y1 = coords[1] - alto_casilla + 5
                            y2 = coords[1] - alto_casilla + (alto_casilla / 2) - 10
                            posiciones = [(x, y1), (x, y2)]
                        elif casilla == 27:
                            x1 = coords[0] + (ancho_casilla / 2) - 10
                            x2 = coords[2] - 25
                            y = coords[3] + 5
                            posiciones = [(x1, y), (x2, y)]
                        elif casilla == 43:
                            x1 = coords[0] + 5
                            x2 = coords[0] + 30
                            y = coords[1] + (alto_casilla / 2) - 10
                            posiciones = [(x1, y), (x2, y)]
                        elif casilla == 44:
                            x = coords[0] + (ancho_casilla - 20) / 2
                            y1 = coords[1] + 5
                            y2 = coords[1] + 30
                            posiciones = [(x, y1), (x, y2)]
                        elif casilla == 60:
                            x = coords[0] + (ancho_casilla - 20) / 2
                            y1 = coords[3] + 30
                            y2 = coords[3] + 55
                            posiciones = [(x, y1), (x, y2)]
                        elif casilla == 61:
                            x1 = coords[0] + 5
                            x2 = coords[0] + (ancho_casilla / 2) - 10
                            y = coords[3] + 5
                            posiciones = [(x1, y), (x2, y)]
                elif num_fichas == 3:
                    if tipo_casilla == "horizontal":
                        ancho_total_fichas = 60  # 3 fichas * 20px
                        x_inicial = coords[0] + (ancho_casilla - ancho_total_fichas) / 2
                        y = coords[1] + (alto_casilla - 20) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 60, 20)]
                    else:  # vertical
                        alto_total_fichas = 60  # 3 fichas * 20px
                        x = coords[0] + (ancho_casilla - 20) / 2
                        y_inicial = coords[1] + (alto_casilla - alto_total_fichas) / 2
                        posiciones = [(x, y_inicial + y) for y in range(0, 60, 20)]
                elif num_fichas == 4:  # 4 fichas
                    if tipo_casilla == "horizontal":
                        x_inicial = coords[0] + (ancho_casilla - 80) / 2  # 80 = 4 fichas * 20px
                        y = coords[1] + (alto_casilla - 20) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 80, 20)]
                    else:  # vertical
                        x = coords[0] + (ancho_casilla - 20) / 2
                        y_inicial = coords[1] + (alto_casilla - 80) / 2  # 80 = 4 fichas * 20px
                        posiciones = [(x, y_inicial + y) for y in range(0, 80, 20)]
                elif num_fichas == 5:  # 5 fichas
                    fichas = [(pygame.transform.scale(ficha, (16, 16)), color, nombre, i) for ficha, color, nombre, i in fichas]
                    if tipo_casilla == "horizontal":
                        x_inicial = coords[0] + (ancho_casilla - 80) / 2 # 80 = 5 fichas * 16px
                        y = coords[1] + (alto_casilla - 16) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 80, 16)]
                    else:  # vertical
                        x = coords[0] + (ancho_casilla - 16) / 2
                        y_inicial = coords[1] + (alto_casilla - 80) / 2 # 80 = 5 fichas * 16px
                        posiciones = [(x, y_inicial + y) for y in range(0, 80, 16)]
                elif num_fichas == 6:  # 6 fichas
                    fichas = [(pygame.transform.scale(ficha, (13, 13)), color, nombre, i) for ficha, color, nombre, i in fichas]
                    if tipo_casilla == "horizontal":
                        x_inicial = coords[0] + (ancho_casilla - 78) / 2 # 78 = 6 fichas * 13px
                        y = coords[1] + (alto_casilla - 13) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 78, 13)]
                    else:  # vertical
                        x = coords[0] + (ancho_casilla - 13) / 2
                        y_inicial = coords[1] + (alto_casilla - 78) / 2 # 78 = 6 fichas * 13px
                        posiciones = [(x, y_inicial + y) for y in range(0, 78, 13)]
                elif num_fichas == 7:  # 7 fichas
                    fichas = [(pygame.transform.scale(ficha, (11, 11)), color, nombre, i) for ficha, color, nombre, i in fichas]
                    if tipo_casilla == "horizontal":
                        x_inicial = coords[0] + (ancho_casilla - 77) / 2 # 77 = 7 fichas * 11px
                        y = coords[1] + (alto_casilla - 11) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 77, 11)]
                    else:  # vertical
                        x = coords[0] + (ancho_casilla - 11) / 2
                        y_inicial = coords[1] + (alto_casilla - 77) / 2 # 77 = 7 fichas * 11px
                        posiciones = [(x, y_inicial + y) for y in range(0, 77, 11)]
                elif num_fichas == 8:  # 8 fichas
                    fichas = [(pygame.transform.scale(ficha, (10, 10)), color, nombre, i) for ficha, color, nombre, i in fichas]
                    if tipo_casilla == "horizontal":
                        x_inicial = coords[0] + (ancho_casilla - 80) / 2
                        y = coords[1] + (alto_casilla - 10) / 2
                        posiciones = [(x_inicial + x, y) for x in range(0, 80, 10)]
                    else:  # vertical
                        x = coords[0] + (ancho_casilla - 10) / 2
                        y_inicial = coords[1] + (alto_casilla - 80) / 2
                        posiciones = [(x, y_inicial + y) for y in range(0, 80, 10)]

                # Dibujar fichas y guardar coordenadas
                for (ficha, color, nombre, indice), pos in zip(fichas, posiciones):
                    if nombre == self.nombre_jugador:
                        self.coordenadas_fichas[indice] = (pos, color)
                    self.window.blit(ficha, pos)
            else:  # Casilla de llegada
                for (ficha, color, nombre, indice) in fichas:
                    self.dibujar_metas(indice, casilla, fichas[0][0], color, nombre)
                
                                    
    def crear_ventana_dados(self, x, y, valor1, valor2, valor_disponible):
        """Crea la ventana de los dados y obtiene los valores de los dados"""
        if valor2 != 0:
            if valor_disponible == []:
                dado1 = pygame.transform.scale(self.dado[valor1], (30,30))
                dado2 = pygame.transform.scale(self.dado[valor2], (30,30))
                pygame.draw.rect(self.window, (255, 255, 255), (x-20, y-30, 60, 30), border_radius=2) # Dibujar el rectángulo
                self.window.blit(dado1, (x-20, y-30, x, y)) # Dibujar el valor del dado 1
                self.window.blit(dado2, (x+10, y-30, x+40, y)) # Dibujar el valor del dado 2
                pygame.draw.polygon(self.window, (255, 128, 0), [(x, y), (x+10, y+10), (x+20, y)]) #Dibujar triangulo/flecha
            else:
                for valor in valor_disponible:
                    if valor == 1:
                        dado1 = pygame.transform.scale(self.dado[valor1], (30,30))
                        pygame.draw.rect(self.window, (255, 255, 255), (x-5, y-30, 30, 30), border_radius=2) # Dibujar el rectángulo
                        self.window.blit(dado1, (x-5, y-30, x+25, y)) # Dibujar el valor del dado 1
                        pygame.draw.polygon(self.window, (255, 128, 0), [(x, y), (x+10, y+10), (x+20, y)]) #Dibujar triangulo/flecha
                    else:
                        dado2 = pygame.transform.scale(self.dado[valor2], (30,30))
                        pygame.draw.rect(self.window, (255, 255, 255), (x-5, y-30, 30, 30), border_radius=2) # Dibujar el rectángulo
                        self.window.blit(dado2, (x-5, y-30, x+25, y)) # Dibujar el valor del dado 2
                        pygame.draw.polygon(self.window, (255, 128, 0), [(x, y), (x+10, y+10), (x+20, y)]) #Dibujar triangulo/flecha
        else:
            dado = pygame.transform.scale(self.dado[valor1], (30,30))
            pygame.draw.rect(self.window, (255, 255, 255), (x-5, y-30, 30, 30), border_radius=2) # Dibujar el rectángulo
            self.window.blit(dado, (x-5, y-30, x+25, y)) # Dibujar el valor del dado
            pygame.draw.polygon(self.window, (255, 128, 0), [(x, y), (x+10, y+10), (x+20, y)]) #Dibujar triangulo/flecha

    def dibujar_metas(self, i, casilla, ficha, color, nombre):
        if casilla == "CIELO1":
            self.window.blit(ficha, (35 + MP.meta[casilla][0] + i * 30, MP.meta[casilla][1] + 20))
            if nombre == self.nombre_jugador:
                self.coordenadas_fichas[i] = ((35 + MP.meta[casilla][0] + i * 30, MP.meta[casilla][1] + 20), color)
        elif casilla == "CIELO3":
            self.window.blit(ficha, (35 + MP.meta[casilla][0] + i * 30, MP.meta[casilla][1] - 40))
            if nombre == self.nombre_jugador:
                self.coordenadas_fichas[i] = ((35 + MP.meta[casilla][0] + i * 30, MP.meta[casilla][1] - 40), color)
        elif casilla == "CIELO2":
            self.window.blit(ficha, (20 + MP.meta[casilla][0], 35 + MP.meta[casilla][1] + i * 30))
            if nombre == self.nombre_jugador:
                self.coordenadas_fichas[i] = ((20 + MP.meta[casilla][0], 35 + MP.meta[casilla][1] + i * 30), color)
        elif casilla == "CIELO4":
            self.window.blit(ficha, (-40 + MP.meta[casilla][0], 35 + MP.meta[casilla][1] + i * 30))
            if nombre == self.nombre_jugador:
                self.coordenadas_fichas[i] = ((-40 + MP.meta[casilla][0], 35 + MP.meta[casilla][1] + i * 30), color)

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

    def dibujar_dados(self, dado1, dado2=None):
        """Dibuja los dados en la pantalla y muestra el mensaje"""
        self.dibujar_mensaje_dados(120)
        if dado2 is None:
            self.window.blit(self.dado[dado1], (705, 500))
        else:
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