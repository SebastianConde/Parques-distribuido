import socket
import time
import threading
import queue
import ast
import random

class Bot:
    def __init__(self, host='127.0.0.1', port=65432):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.nombre = ''
        self.color = None
        self.menu = True
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
        self.un_solo_dado = False

        # Variables x y y para las coordenadas de la ventana dados por ficha
        self.x_ventana = 0
        self.y_ventana = 0
        self.actualizar_ventana_dados = []
        self.estoy_ventana_dados = False

        #Fichas a mover
        self.fichas_a_mover = []
        self.esperando_fichas = False
        self.ficha_a_guardar = None
        self.esperando_ficha_sacar = False

        self.contador = 0
        # Inicializar el estado del juego
        self.juego_estado = {
            'jugadores': {}
        }

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

            self.ultimo_mensaje = mensaje
            self.tiempo_mensaje = time.time() 

    def actualizar_dados_y_mensaje(self):
        """Actualiza los dados y su mensaje de forma sincronizada"""
        if self.dados_actualizados and self.mensaje_dados:
            # Esperamos un pequeño momento para que los dados se actualicen visualmente
            if time.time() - self.tiempo_dados >= 0.1:  # 100ms de delay
                if self.ventana_actual == "JUEGO":
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
            elif "Es tu turno. Lanza los dados" in mensaje:
                self.turno = True
                self.esperando_respuesta = True
                self.mostrar_mensaje(mensaje)
            elif "Es tu turno. Lanza el dado" in mensaje:
                self.turno = True
                self.esperando_respuesta = True
                self.mostrar_mensaje(mensaje)
                self.un_solo_dado = True
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
                self.actualizar_posiciones_fichas(mensaje)
            elif "Dame las fichas" in mensaje:
                self.esperando_fichas = True
                self.turno = True
            elif "Tienes 3 pares consecutivos. Selecciona una ficha para sacar." in mensaje:
                self.esperando_ficha_sacar = True
                self.turno = True
                self.mostrar_mensaje(mensaje)
            elif "Lo sentimos, hay un juego en curso." in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
                self.estado_actual = "MENU"
            else:
                self.mostrar_mensaje(mensaje)

    def actualizar_posiciones_fichas(self, mensaje):
        mensaje_filtrado = mensaje.replace("Posiciones iniciales: ", "").strip()
        segmentos = mensaje_filtrado.split(";")
        for segmento in segmentos:
            if segmento:
                #Separar nombre, color y posiciones
                nombre, color, posiciones_str = segmento.split(".")
                posiciones = ast.literal_eval(posiciones_str)

                # Agregar al diccionario de posiciones
                self.player_colors_and_positions[nombre] = (color, posiciones)

        # Inicializa self.juego_estado['jugadores'] si no está inicializado
        if 'jugadores' not in self.juego_estado:
            self.juego_estado['jugadores'] = {}

        # Inicializa todos los jugadores en self.juego_estado['jugadores']
        for nombre, (color, posiciones) in self.player_colors_and_positions.items():
            if nombre not in self.juego_estado['jugadores']:
                self.juego_estado['jugadores'][nombre] = {'color': color, 'posiciones': [0, 0, 0, 0]}

        # Actualiza las posiciones de los jugadores
        for nombre, (color, posiciones) in self.player_colors_and_positions.items():
            self.juego_estado['jugadores'][nombre]['posiciones'] = posiciones

        if self.color == 3:
            for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                nuevas_posiciones = []
                for pos in posiciones:
                    if isinstance(pos, str):
                        if color == "3":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AZUL"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "3":
                                    nueva_pos = "CIELO3"
                                    nuevas_posiciones.append(nueva_pos)
                        if color == "1":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "ROJO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "1":
                                    nueva_pos = "CIELO1"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "2":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AMARILLO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "2":
                                    nueva_pos = "CIELO2"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "4":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "VERDE"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "4":
                                    nueva_pos = "CIELO4"
                                    nuevas_posiciones.append(nueva_pos)
                    else:
                        nuevas_posiciones.append(pos)
                self.juego_estado['jugadores'][self.nombre]['posiciones'] = nuevas_posiciones

        # Rotar las posiciones de los jugadores según su color
        if self.color == 2:
            for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                nuevas_posiciones = []
                for pos in posiciones:
                    if isinstance(pos, int):
                        if pos == -1 or pos == 0:
                            nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                        else:
                            nuevo_pos = (pos + 17) % 68  # Rotar 17 posiciones
                            nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                    else:
                        if color == "2":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AZUL"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "2":
                                    nueva_pos = "CIELO3"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "1":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AMARILLO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "1":
                                    nueva_pos = "CIELO2"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "3":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "VERDE"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "3":
                                    nueva_pos = "CIELO4"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "4":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "ROJO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "4":
                                    nueva_pos = "CIELO1"
                                    nuevas_posiciones.append(nueva_pos)
                        
                self.juego_estado['jugadores'][nombre]['posiciones'] = nuevas_posiciones

        elif self.color == 1:
            for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                nuevas_posiciones = []
                for pos in posiciones:
                    if isinstance(pos, int):
                        if pos == -1 or pos == 0:
                            nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                        else:
                            nuevo_pos = (pos + 34) % 68  # Rotar 34 posiciones
                            nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                    else:
                        if color == "1":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AZUL"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "1":
                                    nueva_pos = "CIELO3"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "2":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "VERDE"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "2":
                                    nueva_pos = "CIELO4"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "3":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "ROJO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "3":
                                    nueva_pos = "CIELO1"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "4":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AMARILLO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "4":
                                    nueva_pos = "CIELO2"
                                    nuevas_posiciones.append(nueva_pos)

                self.juego_estado['jugadores'][nombre]['posiciones'] = nuevas_posiciones

        elif self.color == 4:
            for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                nuevas_posiciones = []
                for pos in posiciones:
                    if isinstance(pos, int):
                        if pos == -1 or pos == 0:
                            nuevas_posiciones.append(pos)  # Mantener -1 y 0 sin cambios
                        else:
                            nuevo_pos = (pos + 51) % 68  # Rotar 51 posiciones
                            nuevas_posiciones.append(68 if nuevo_pos == 0 else nuevo_pos)
                    else:
                        if color == "4":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AZUL"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "4":
                                    nueva_pos = "CIELO3"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "1":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "VERDE"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "1":
                                    nueva_pos = "CIELO4"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "2":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "ROJO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "2":
                                    nueva_pos = "CIELO1"
                                    nuevas_posiciones.append(nueva_pos)
                        elif color == "3":
                            if "CAMINO_CIELO" in pos:
                                nueva_pos = pos.replace("CAMINO_CIELO:", "").strip()
                                nueva_pos = "AMARILLO"+nueva_pos
                                nuevas_posiciones.append(nueva_pos)
                            else:
                                nueva_pos = pos.replace("CIELO", "").strip()
                                if nueva_pos == "3":
                                    nueva_pos = "CIELO2"
                                    nuevas_posiciones.append(nueva_pos)
                self.juego_estado['jugadores'][nombre]['posiciones'] = nuevas_posiciones

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

    def obtener_fichas_disponibles(self):
        fichas_disponibles = []
        for nombre, jugador in self.juego_estado['jugadores'].items():
            if jugador['color'] == str(self.color):
                for i, pos in enumerate(jugador['posiciones']):
                    if pos != -1:  # Considera que -1 es una posición no válida
                        fichas_disponibles.append(i)
        return fichas_disponibles

    def procesar_turno(self):
        # Lógica del bot para procesar su turno.
        if self.turno:
            if self.esperando_respuesta and not self.esperando_fichas:
                self.client_socket.sendall("dados".encode('utf-8'))
                time.sleep(1)

            if self.esperando_fichas:
                fichas_disponibles = self.obtener_fichas_disponibles()
                if fichas_disponibles:
                    ficha_seleccionada1 = random.choice(fichas_disponibles)
                    ficha_seleccionada2 = random.choice(fichas_disponibles)
                    self.fichas_a_mover.append((ficha_seleccionada1, self.dado1))
                    self.fichas_a_mover.append((ficha_seleccionada2, self.dado2))

            if self.esperando_ficha_sacar:
                fichas_disponibles = self.obtener_fichas_disponibles()
                if fichas_disponibles:
                    ficha_seleccionada = random.choice(fichas_disponibles)
                    self.client_socket.sendall(f"sacar_ficha:{ficha_seleccionada}".encode('utf-8'))
                    self.esperando_ficha_sacar = False
                    self.mostrar_mensaje(f"La ficha {ficha_seleccionada} ha sido retirada.")
                    time.sleep(0.2)

        elif self.esperando_dados_inicio:
            self.client_socket.sendall("dados".encode('utf-8'))
            self.esperando_dados_inicio = False
            time.sleep(0.2)


    def conectar(self):
        respuesta_menu = True
        self.client_socket.connect((self.host, self.port))

        if respuesta_menu:
            # Iniciar thread para recibir mensajes
            self.thread_recibir = threading.Thread(target=self.recibir_mensajes)
            self.thread_recibir.daemon = True
            self.thread_recibir.start()

            # Estado inicial: entrada de nombre
            self.estado_actual = "ENTRADA_NOMBRE"
            self.nombre = f"Bot{random.randint(1, 1000)}"
            self.client_socket.sendall(self.nombre.encode('utf-8'))

            # Bucle principal del juego
            while self.running:
                # Procesar mensajes pendientes
                self.procesar_mensajes()
                # Actualizar dados y mensaje de forma sincronizada
                self.actualizar_dados_y_mensaje()

                # Manejar estados específicos
                if self.estado_actual == "ESPERANDO_COLOR" and self.esperando_color:
                    color_elegido = random.choice([1, 2, 3, 4])
                    self.client_socket.sendall(f"color:{color_elegido}".encode('utf-8'))
                    self.esperando_color = False
                    time.sleep(0.2)

                if self.estado_actual == "ESPERANDO_INICIO" and self.esperando_inicio:
                    self.enviar_respuesta("si")
                    self.esperando_inicio = False
                    time.sleep(0.2)

                self.procesar_turno()

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

                time.sleep(0.2)

    def cerrar_conexion(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if hasattr(self, 'thread_recibir'):
            self.thread_recibir.join(timeout=1)


if __name__ == "__main__":
    bot = Bot()
    try:
        bot.conectar()
    finally:
        bot.cerrar_conexion()