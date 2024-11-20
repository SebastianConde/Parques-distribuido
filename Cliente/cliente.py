import socket
from juego import JuegoParques
from menu import Menu
import time
import threading
import queue
import pygame
import ast

class Cliente:
    def __init__(self, host='127.0.0.1', port=65432):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nombre = ''
        self.color = None
        self.menu = Menu(self)
        self.juego = None
        self.turno = False
        self.mensaje_queue = queue.Queue()
        self.running = True
        self.esperando_respuesta = False # Bandera para esperar respuesta del jugador
        self.esperando_inicio = False
        self.esperando_color = False
        self.esperando_dados_inicio = False
        self.mensaje_color = None
        self.estado_actual = "MENU"  # Estados: MENU, ENTRADA_NOMBRE, JUGANDO, ESPERANDO_INICIO
        self.ultimo_mensaje = None
        self.ultimo_mensaje_dados = None
        self.tiempo_mensaje = 0
        self.ventana_actual = "MENU"  # Estados: MENU, JUEGO
        self.jugadores = []
        self.dado1 = 0
        self.dado2 = 0
        self.mensaje_dados = None
        self.tiempo_dados = None
        self.dados_actualizados = False
        self.posiciones_fichas = []
        self.player_colors_and_positions = None
        self.ventana_dados = False

        # Variables x y y para las coordenadas de la ventana dados por ficha
        self.x_ventana = 0
        self.y_ventana = 0
        self.actualizar_ventana_dados = []
        self.estoy_ventana_dados = False

        #Fichas a mover
        self.fichas_a_mover = []
        self.esperando_fichas = False
        self.ficha_a_guardar = None

    def recibir_mensajes(self):
        """Thread worker para recibir mensajes del servidor"""
        while self.running:
            try:
                if self.client_socket:
                    mensaje = self.client_socket.recv(1024).decode('utf-8')
                    if mensaje:
                        # Función para reducir un mensaje repetido a una sola subcadena
                        def reducir_a_subcadena_unica(mensaje):
                            subcadena_delimitador = mensaje.split(".")[0] + "."
                            if mensaje == subcadena_delimitador * (len(mensaje) // len(subcadena_delimitador)):
                                return subcadena_delimitador
                            return mensaje

                        mensaje = reducir_a_subcadena_unica(mensaje)

                        if mensaje != self.ultimo_mensaje:
                            self.mensaje_queue.put(mensaje)

            except Exception as e:
                if self.running:
                    print("Error al recibir el mensaje:", e)
                break

    def mostrar_mensaje_con_delay(self, mensaje):
        """Muestra un mensaje y espera el tiempo especificado"""
        print(f"Mostrando mensaje con delay: {mensaje}")  # Debug print
        if mensaje != self.ultimo_mensaje:
            if self.ventana_actual == "MENU" and self.menu:
                self.menu.mostrar_mensaje(mensaje)
                time.sleep(3)
            elif self.ventana_actual == "JUEGO" and self.juego:
                self.juego.mostrar_mensaje(mensaje)
            
            self.ultimo_mensaje = mensaje
            self.tiempo_mensaje = time.time()
            
            # Usar threading.Event para sincronizar el delay
            stop_event = threading.Event()
            def delay_thread():
                stop_event.wait(10)  # Espera 10 segundos
                stop_event.set()
            
            threading.Thread(target=delay_thread).start()

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje en la pantalla"""
        if mensaje != self.ultimo_mensaje:
            if "lanza" in mensaje and "dados" in mensaje.lower():
                self.mensaje_dados = mensaje
                return
            if self.ventana_actual == "JUEGO" and self.juego:
                self.juego.mostrar_mensaje(mensaje)

            self.ultimo_mensaje = mensaje
            self.tiempo_mensaje = time.time() 

    def actualizar_dados_y_mensaje(self):
        """Actualiza los dados y su mensaje de forma sincronizada"""
        if self.dados_actualizados and self.mensaje_dados:
            # Esperamos un pequeño momento para que los dados se actualicen visualmente
            if time.time() - self.tiempo_dados >= 0.1:  # 100ms de delay
                if self.ventana_actual == "JUEGO" and self.juego:
                    self.juego.mostrar_mensaje_dados(self.mensaje_dados)
                    self.ultimo_mensaje_dados = self.mensaje_dados
                    self.tiempo_dados = time.time()
                self.mensaje_dados = None
                self.dados_actualizados = False

    def separar_jugadores(self, mensaje):
        jugadores = mensaje.split(":")[1].split(", ")
        self.jugadores = [(j.split()[0], int(j.split()[1])) for j in jugadores]
        self.player_colors_and_positions = {}
        for name, color in self.jugadores:
            self.player_colors_and_positions[name] = [0, 0, 0, 0]

    def procesar_mensajes(self):
        """Procesa los mensajes recibidos sin bloquear"""
        while not self.mensaje_queue.empty(): 
            mensaje = self.mensaje_queue.get() 
            print("Mensaje recibido:", mensaje)  # Debug
            # Verificar si el juego ha comenzado
            if "El juego ha comenzado" in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
                self.estado_actual = "JUGANDO"
                self.esperando_inicio = False
                self.transicion_a_juego()
            elif "Los jugadores son:" in mensaje:
                self.separar_jugadores(mensaje)
            elif "Color:" in mensaje:
                self.color = int(mensaje.split(":")[1].strip())
            elif any(frase in mensaje for frase in ["se ha unido al juego.", "Bienvenid@,", "Esperando más jugadores...", "ha abandonado el juego.", "Espere..."]):
                self.mostrar_mensaje_con_delay(mensaje)
            elif "Elija" in mensaje:
                self.mensaje_color = mensaje
                self.estado_actual = "ESPERANDO_COLOR"
                self.esperando_color = True
            elif "Color asignado automáticamente." in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
            elif "¿Desean iniciar el juego ahora? (si/no)" in mensaje:
                self.estado_actual = "ESPERANDO_INICIO"
                self.esperando_inicio = True
            elif "El primer turno es para:" in mensaje:
                self.mostrar_mensaje(mensaje)
                self.esperando_dados_inicio = True
            elif "ha sacado esto" in mensaje:
                valores = mensaje.split('(')[1].replace(')', '').split(',')
                self.dado1 = int(valores[0])
                self.dado2 = int(valores[1].strip()) 
                self.mostrar_mensaje_con_delay(mensaje)
            elif "ha sacado el mayor tiro y comienza el juego." in mensaje:
                self.dado1 = 6
                self.dado2 = 6
                self.esperando_dados_inicio = False
                self.mostrar_mensaje_con_delay(mensaje)
                time.sleep(3)
            elif "Esperando a que tiren los dados" in mensaje:
                self.mostrar_mensaje(mensaje)
            elif "Es tu turno" in mensaje:
                self.turno = True
                self.esperando_respuesta = True
                self.mostrar_mensaje(mensaje)
            elif "Espera tu turno" in mensaje:
                self.mostrar_mensaje(mensaje)
            elif "lanza" in mensaje:
                self.obtener_dados(mensaje)
                if "ha salido de la cárcel" in mensaje:
                    self.turno = False
                    self.esperando_respuesta = False
                elif "y no ha podido salir de la cárcel" in mensaje:
                    self.turno = True
                    self.esperando_respuesta = True
            elif "no ha podido salir de la cárcel." in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
                self.turno = False
                self.esperando_respuesta = False
            elif "Posiciones iniciales:" in mensaje:
                mensaje_filtrado = mensaje.replace("Posiciones iniciales: ", "").strip()
                segmentos = mensaje_filtrado.split(";")
                for segmento in segmentos:
                    if segmento:
                        #Separar nombre, color y posiciones
                        nombre, color, posiciones_str = segmento.split(".")
                        posiciones = ast.literal_eval(posiciones_str)

                        # Agregar al diccionario de posiciones
                        self.player_colors_and_positions[nombre] = (color, posiciones) 
                for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                    self.juego.jugadores[nombre]["posiciones"] = self.player_colors_and_positions[nombre][1]

                # Rotar las posiciones de los jugadores según su color
                if self.color == 2:
                    for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                        nuevas_posiciones = []
                        for pos in posiciones:
                            if pos == -1 or pos == 0:
                                nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                            else:
                                nuevo_pos = (pos + 17) % 68  # Rotar 17 posiciones
                                nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                        self.juego.jugadores[nombre]["posiciones"] = nuevas_posiciones

                elif self.color == 1:
                    for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                        nuevas_posiciones = []
                        for pos in posiciones:
                            if pos == -1 or pos == 0:
                                nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                            else:
                                nuevo_pos = (pos + 34) % 68  # Rotar 34 posiciones
                                nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                        self.juego.jugadores[nombre]["posiciones"] = nuevas_posiciones

                elif self.color == 4:
                    for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                        nuevas_posiciones = []
                        for pos in posiciones:
                            if pos == -1 or pos == 0:
                                nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                            else:
                                nuevo_pos = (pos + 51) % 68  # Rotar 51 posiciones
                                nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                        self.juego.jugadores[nombre]["posiciones"] = nuevas_posiciones

            elif "Dame las fichas":
                self.esperando_fichas = True
            elif "Lo sentimos, hay un juego en curso." in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
                self.estado_actual = "MENU"
            else:
                self.mostrar_mensaje(mensaje)

    def obtener_dados(self, mensaje):
        partes = mensaje.split("(")
        if len(partes) > 1:
            valores_dados = partes[1].split(")")[0]  
            dado1, dado2 = map(int, valores_dados.split(","))
            self.dado1 = dado1
            self.dado2 = dado2
            self.mensaje_dados = mensaje
            self.tiempo_dados = time.time()
            self.dados_actualizados = True

    def transicion_a_juego(self):
        """Maneja la transición de la ventana de menú a la ventana de juego"""
        print("Ejecutando transición a juego...")  # Debug

        if self.menu:
            self.menu.close()
            self.menu = None
        
        # Inicializar la ventana de juego
        self.juego = JuegoParques(self.jugadores, self.nombre, self.color)
        self.ventana_actual = "JUEGO"
        
    def enviar_respuesta(self, mensaje):
        """Envía la respuesta del jugador"""
        if self.client_socket:
            self.client_socket.sendall(mensaje.encode('utf-8'))

    def entrada_texto_con_delay(self, mensaje, tipo, delay_antes=True):
        """Wrapper para entrada_texto con delay configurable"""
        if delay_antes:
            self.mostrar_mensaje_con_delay(mensaje)
        else:
            if self.menu:
                self.menu.mostrar_mensaje(mensaje)

        # Obtener la entrada del usuario
        if self.ventana_actual == "MENU":
            respuesta = self.menu.entrada_texto(mensaje, tipo)
        else:
            respuesta = self.juego.entrada_texto(mensaje, tipo)
        
        return respuesta

    def conectar(self):
        respuesta_menu = self.menu.menu()
        self.client_socket.connect((self.host, self.port))

        if respuesta_menu:
            # Iniciar thread para recibir mensajes
            self.thread_recibir = threading.Thread(target=self.recibir_mensajes)
            self.thread_recibir.daemon = True
            self.thread_recibir.start()

            # Estado inicial: entrada de nombre
            self.estado_actual = "ENTRADA_NOMBRE"
            self.nombre = self.entrada_texto_con_delay("Ingresa tu nombre: ", "unica", delay_antes=False)
            self.client_socket.sendall(self.nombre.encode('utf-8'))

            # Bucle principal del juego
            while self.running:
                # Procesar mensajes pendientes
                self.procesar_mensajes()
                # Actualizar dados y mensaje de forma sincronizada
                self.actualizar_dados_y_mensaje()

                # Manejar estados específicos
                if self.estado_actual == "ESPERANDO_COLOR" and self.esperando_color:
                    respuesta = self.entrada_texto_con_delay(self.mensaje_color, "color")
                    if respuesta.lower() in ['rojo', 'amarillo', 'azul', 'verde']:
                        if respuesta.lower() == 'rojo':
                            self.client_socket.sendall("color:1".encode('utf-8'))
                        elif respuesta.lower() == 'amarillo':
                            self.client_socket.sendall("color:2".encode('utf-8'))
                        elif respuesta.lower() == 'azul':
                            self.client_socket.sendall("color:3".encode('utf-8'))
                        elif respuesta.lower() == 'verde':
                            self.client_socket.sendall("color:4".encode('utf-8'))
                        self.esperando_color = False
                        time.sleep(0.2)

                if self.estado_actual == "ESPERANDO_INICIO" and self.esperando_inicio:
                    respuesta = self.entrada_texto_con_delay("¿Deseas iniciar el juego ahora? (si/no): ", "condicional")
                    if respuesta.lower() in ['si', 'no']:
                        self.enviar_respuesta(respuesta.lower())
                        self.esperando_inicio = False
                        time.sleep(0.2)

                if self.juego:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            break
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if 700 <= event.pos[0] <= 900 and 500 <= event.pos[1] <= 700:
                                if self.esperando_respuesta and self.turno and not self.esperando_fichas:
                                    self.client_socket.sendall("dados".encode('utf-8'))
                                    time.sleep(0.2)
                                elif self.esperando_dados_inicio:
                                    self.client_socket.sendall("dados".encode('utf-8'))
                                    self.esperando_dados_inicio = False
                                    time.sleep(0.2)
                            
                            if self.x_ventana-20 <= event.pos[0] <= self.x_ventana+10 and self.y_ventana-30 <= event.pos[1] <= self.y_ventana and self.x_ventana != 0 and self.y_ventana != 0 and self.ventana_dados and len(self.actualizar_ventana_dados) == 0:
                                self.estoy_ventana_dados = True
                                self.actualizar_ventana_dados.append(2)
                                tupla = (self.ficha_a_guardar, self.dado1)
                                self.fichas_a_mover.append(tupla)
                                self.ventana_dados = False
                            elif self.x_ventana+10 <= event.pos[0] <= self.x_ventana+40 and self.y_ventana-30 <= event.pos[1] <= self.y_ventana and self.x_ventana != 0 and self.y_ventana != 0 and self.ventana_dados and len(self.actualizar_ventana_dados) == 0:
                                self.estoy_ventana_dados = True
                                self.actualizar_ventana_dados.append(1)
                                tupla = (self.ficha_a_guardar, self.dado2)
                                self.fichas_a_mover.append(tupla)
                                self.ventana_dados = False

                            if self.x_ventana-5 <= event.pos[0] <= self.x_ventana+25 and self.y_ventana-30 <= event.pos[1] <= self.y_ventana and len(self.actualizar_ventana_dados) > 0 and self.x_ventana != 0 and self.y_ventana != 0 and self.ventana_dados:
                                self.estoy_ventana_dados = True
                                if 1 in self.actualizar_ventana_dados:
                                    self.actualizar_ventana_dados.append(2)
                                    tupla = (self.ficha_a_guardar, self.dado1)
                                    self.fichas_a_mover.append(tupla)
                                else:
                                    self.actualizar_ventana_dados.append(1)
                                    tupla = (self.ficha_a_guardar, self.dado2)
                                    self.fichas_a_mover.append(tupla)

                            if self.actualizar_ventana_dados != []:
                                self.ventana_dados = False
                                self.x_ventana = 0
                                self.y_ventana = 0
                                self.estoy_ventana_dados = False

                            for key, value in self.juego.coordenadas_fichas.items():
                                x, y = value
                                if x <= event.pos[0] <= x+20 and y <= event.pos[1] <= y+20 and self.turno and not self.estoy_ventana_dados and len(self.actualizar_ventana_dados) < 2 and self.esperando_fichas:
                                    self.x_ventana = x
                                    self.y_ventana = y 
                                    self.ficha_a_guardar = key
                                    self.ventana_dados = True


                    if self.ventana_actual == "JUEGO":
                        self.juego.actualizar_pantalla()
                        if self.dado1 and self.dado2:
                            self.juego.dibujar_dados(self.dado1, self.dado2)
                        else:
                            self.juego.dibujar_dados(6, 6)
                        if self.x_ventana != 0 and self.y_ventana != 0 and self.ventana_dados:
                            self.juego.crear_ventana_dados(self.x_ventana, self.y_ventana, self.dado1, self.dado2, self.actualizar_ventana_dados)
                            self.estoy_ventana_dados = False
                        if len(self.actualizar_ventana_dados) == 2:
                            self.actualizar_ventana_dados = []
                            self.ventana_dados = False
                            self.x_ventana = 0
                            self.y_ventana = 0
                        if len(self.fichas_a_mover) == 2 and self.esperando_fichas:
                            self.client_socket.sendall(f"mover_fichas:{self.fichas_a_mover[0][0]},{self.fichas_a_mover[0][1]},{self.fichas_a_mover[1][0]},{self.fichas_a_mover[1][1]}".encode('utf-8'))
                            self.fichas_a_mover = []
                            self.esperando_fichas = False
                            if self.dado1 == self.dado2:
                                self.esperando_respuesta = True
                                self.turno = True
                            else:
                                self.esperando_respuesta = False
                                self.turno = False

                    pygame.display.flip()
                
                # Control de FPS
                pygame.time.Clock().tick(60)

    def cerrar_conexion(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if hasattr(self, 'thread_recibir'):
            self.thread_recibir.join(timeout=1)
        if self.juego:
            self.juego.close()

if __name__ == "__main__":
    cliente = Cliente()
    try:
        cliente.conectar()
    finally:
        cliente.cerrar_conexion()