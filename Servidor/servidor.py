import socket
import threading
from parques import Parques
import time
import queue
import random
from constantes import TipoDeCelda

class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(4)
        self.reset_game_state()
        self.lock = threading.Lock()

    def reset_game_state(self):
        """Reinicia todos los estados del juego"""
        self.clients = []  # Lista de tuplas (socket, nombre)
        self.parques = Parques()
        self.juego_iniciado = False
        self.respuestas = []
        self.jugadores = []
        self.message_queues = {}  # Diccionario para almacenar colas de mensajes por cliente
        self.player_colors_and_positions = {}  # Diccionario para almacenar colores y posiciones de los jugadores
        self.dados_inicio = []
        self.intentos_fallidos = 0
        self.intentos_maximos = 3

    def broadcast(self, message, exclude_socket=None):
        for client_socket, _ in self.clients:
            if client_socket != exclude_socket:
                try:
                    if client_socket not in self.message_queues:
                        self.message_queues[client_socket] = queue.Queue()
                    self.message_queues[client_socket].put(message)
                    time.sleep(0.1)
                    print(f"Encolando mensaje para {client_socket.getpeername()}: {message}")
                    self.send_queued_messages(client_socket)
                except:
                    self.handle_disconnect(client_socket)

    def handle_disconnect(self, client_socket):
        """Maneja la desconexión de un cliente"""
        with self.lock:
            nombre = self.get_player_name(client_socket)
            if nombre:
                print(f"Desconectando a {nombre}")
                self.broadcast(f"{nombre} ha abandonado el juego.")
                self.clients = [(s, n) for s, n in self.clients if s != client_socket]
                self.jugadores = [(n, c) for n, c in self.jugadores if n != nombre]
                self.message_queues.pop(client_socket, None)

                try:
                    client_socket.close()
                except:
                    pass

                # Si no quedan jugadores o solo queda uno, reiniciar el juego
                if len(self.clients) < 2:
                    print("Reiniciando estado del juego por falta de jugadores")
                    self.reset_game_state()
                    if len(self.clients) == 1:
                        remaining_socket, _ = self.clients[0]
                        self.send_message(remaining_socket, "Esperando más jugadores...")
    
    def send_queued_messages(self, client_socket):
        """Envía los mensajes encolados para un cliente específico"""
        if client_socket in self.message_queues:
            try:
                while not self.message_queues[client_socket].empty():
                    message = self.message_queues[client_socket].get()
                    client_socket.sendall(message.encode('utf-8'))
                    time.sleep(0.2)  # Pausa entre envíos de mensajes
            except Exception as e:
                print(f"Error enviando mensajes encolados: {e}")
    
    def send_message(self, client_socket, message):
        """Envía un mensaje a un cliente específico usando la cola"""
        try:
            if client_socket not in self.message_queues:
                self.message_queues[client_socket] = queue.Queue()
            self.message_queues[client_socket].put(message)
            time.sleep(0.1)  # Pequeña pausa antes de enviar
            self.send_queued_messages(client_socket)
        except Exception as e:
            print(f"Error enviando mensaje: {e}")

    def recibir_respuestas(self, client_socket):
        respuesta = client_socket.recv(1024).decode('utf-8')
        with self.lock:
            self.respuestas.append(respuesta)

    def get_player_name(self, client_socket):
        """Obtiene el nombre del jugador asociado a un socket"""
        for socket, nombre in self.clients:
            if socket == client_socket:
                return nombre
        return None

    def handle_client(self, client_socket, address):
        try:
            if self.juego_iniciado:
                mensaje = "Lo sentimos, hay un juego en curso."
                self.send_message(client_socket, mensaje)
                client_socket.close()
                return 
            nombre = client_socket.recv(1024).decode('utf-8')

            if nombre:
                self.send_message(client_socket, "Espere...")
            
            with self.lock:
                # Verificar si es el primer jugador después de un reinicio
                if len(self.clients) == 0:
                    self.reset_game_state()
                
                self.clients.append((client_socket, nombre))
                colores_usados = [str(c) for _, c in self.jugadores]

                # Lista completa de colores disponibles
                todos_los_colores = ["rojo", "amarillo", "azul", "verde"]
                colores_disponibles = [color for i, color in enumerate(todos_los_colores, 1) 
                                    if str(i) not in colores_usados]
                cadena_colores = ", ".join(colores_disponibles)

                # Enviar mensaje al cliente para elegir un color
                self.send_message(client_socket, "Elija un color, disponibles: " + cadena_colores)
                color_elegido = client_socket.recv(1024).decode('utf-8')
                color = int(color_elegido.split(":")[1])
                
                if str(color) in colores_usados:
                    print(f'Soy el jugador {nombre} y el color {color} ya está en uso')
                    self.send_message(client_socket, "Elija otro color, disponibles: " + cadena_colores)
                    color_elegido = client_socket.recv(1024).decode('utf-8')
                    color = int(color_elegido.split(":")[1])

                    if str(color) in colores_usados:
                        self.send_message(client_socket, "Color asignado automáticamente.")
                        color = random.choice(colores_disponibles)
                        if color == "rojo":
                            color = 1
                        elif color == "amarillo":
                            color = 2
                        elif color == "azul":
                            color = 3
                        elif color == "verde":
                            color = 4
                
                print(f"{nombre} eligió el color {color}")
    
                self.parques.agregar_jugador(nombre, color)
                self.jugadores.append((nombre, color))
                self.player_colors_and_positions[nombre] = (color, [-1, -1, -1, -1])
                self.send_message(client_socket, f"Color:{self.player_colors_and_positions[self.get_player_name(client_socket)][0]}")
                
                if len(self.clients) == 1:
                    self.send_message(client_socket, f"Bienvenid@, {nombre}!")
                    self.send_message(client_socket, "Esperando más jugadores...")
                else:
                    self.broadcast(f"{nombre} se ha unido al juego.", client_socket)
                    self.send_message(client_socket, f"Bienvenid@, {nombre}!")

            while not self.juego_iniciado and client_socket in [s for s, _ in self.clients]:
                if len(self.clients) == 1:
                    time.sleep(1)
                    continue
                elif len(self.clients) >= 2:
                    while len(self.jugadores) != len(self.clients):
                        time.sleep(0.2)
                    self.send_message(client_socket, "¿Desean iniciar el juego ahora? (si/no)")
                    try:
                        self.respuestas = []
                        self.recibir_respuestas(client_socket)
                        
                        while len(self.respuestas) < len(self.clients):
                            time.sleep(0.2)
                        
                        if all([r == 'si' for r in self.respuestas]) or len(self.clients) == 4:
                            self.juego_iniciado = True
                            jugadores = "Los jugadores son: " + ", ".join([f"{nombre} {color}" for nombre, color in self.jugadores])
                            self.broadcast(jugadores, client_socket)
                            time.sleep(0.2)
                            self.broadcast("El juego ha comenzado!")
                            break
                        else:
                            self.send_message(client_socket, "Esperando más jugadores...")
                            time.sleep(10)
                    except:
                        self.handle_disconnect(client_socket)
                        return

            if self.juego_iniciado:
                self.broadcast("Tira los dados. El primer turno es para: ")
                tiro = client_socket.recv(1024).decode('utf-8')
                if tiro == "dados":
                    with self.lock:  # Usar lock para sincronización
                        valor_dados = self.parques.lanzar_dados()
                        self.send_message(client_socket, f"{nombre} ha sacado esto ({valor_dados[0]}, {valor_dados[1]})")
                        valor_dados = sum(valor_dados)
                        self.dados_inicio.append((client_socket, valor_dados))
                        
                        # Esperar a que todos los jugadores tiren
                        current_players = len(self.dados_inicio)
                        total_players = len(self.clients)
                        
                        if current_players == total_players:
                            # Determinar ganador
                            mayor_tiro = max(self.dados_inicio, key=lambda x: x[1])
                            ganador = self.get_player_name(mayor_tiro[0])
                            color_ganador = self.player_colors_and_positions[ganador][0]
                            
                            # Iniciar el juego con el ganador
                            self.parques.iniciar(self.parques.jugadores[
                                self.jugadores.index((ganador, color_ganador))
                            ])
                            
                            # Anunciar el ganador
                            self.broadcast(f"{ganador} ha sacado el mayor tiro y comienza el juego.")
                            
                            # Agregar una bandera para indicar que el juego está listo para comenzar
                            self.juego_listo_para_comenzar = True
                        
                # Esperar a que el juego esté listo para comenzar
                while not hasattr(self, 'juego_listo_para_comenzar'):
                    time.sleep(0.1)
                    
                # Ahora todos los sockets pueden proceder al manejo de turno
                self.manejar_turno(client_socket)

        except Exception as e:
            print(f"Error al manejar al cliente {address}: {str(e)}")
            self.handle_disconnect(client_socket)


    def manejar_turno(self, client_socket):
        while not self.parques.ganador:
            jugador = self.parques.jugador_actual
            if jugador:
                current_player_name = jugador.nombre
                print(f"Turno de {current_player_name}, socket_name: {self.get_player_name(client_socket)}")
                socket_player_name = self.get_player_name(client_socket)
                
                if current_player_name == socket_player_name:
                    if jugador.en_carcel:
                        for i in range(3):
                            time.sleep(0.2)
                            self.send_message(client_socket, f"Es tu turno. Lanza los dados. Tienes {3-i} intentos para salir de la carcél.")
                            respuesta = client_socket.recv(1024).decode('utf-8')
                            if respuesta == "dados":
                                valor_dados = self.parques.lanzar_dados()
                                if self.parques.dados.es_par:
                                    for ficha in jugador.fichas:
                                        self.parques.tablero.salir_de_carcel(ficha)
                                    jugador.en_carcel = False
                                    turn_message = f"{socket_player_name} lanza {valor_dados} y ha salido de la cárcel."
                                    time.sleep(0.2)  # Pausa antes de anunciar resultado
                                    self.broadcast(turn_message)
                                    color, posiciones = self.player_colors_and_positions[socket_player_name]
                                    posiciones = [0, 0, 0, 0]
                                    self.player_colors_and_positions[socket_player_name] = (color, posiciones)
                                    initial_positions_message = "Posiciones iniciales: "
                                    for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                                        initial_positions_message += f"{nombre}.{color}.{posiciones};"
                                    time.sleep(0.2)  # Pausa antes de enviar posiciones iniciales
                                    self.broadcast(initial_positions_message)
                                    break
                                else:
                                    turn_message = f"{socket_player_name} lanza {valor_dados} y no ha podido salir de la cárcel."
                                    time.sleep(0.2)  # Pausa antes de anunciar resultado
                                    self.broadcast(turn_message)
                        self.send_message(client_socket, "Espera tu turno.")
                        time.sleep(0.2)  # Pausa antes de cambiar de turno
                        if not self.parques.dados.es_par:
                            turn_message = f"{socket_player_name} no ha podido salir de la cárcel."
                            time.sleep(0.2)
                            self.broadcast(turn_message)
                            self.parques.cambiar_turno()
                            continue
                    else:
                        if self.parques.verificar_condicion_un_dado(jugador):
                            time.sleep(0.2)
                            self.send_message(client_socket, "Es tu turno. Lanza el dado y cuenta con tu ficha.")
                        else:
                            time.sleep(0.2)  # Pausa antes de anunciar turno
                            self.send_message(client_socket, "Es tu turno. Lanza los dados y cuenta con tus fichas.")

                        respuesta = client_socket.recv(1024).decode('utf-8')

                        if respuesta == "dados":
                            valor_dados = self.parques.lanzar_dados()
                            if self.parques.verificar_condicion_un_dado(jugador):
                                self.intentos_maximos = 1
                                turn_message = f"{socket_player_name} lanza ({valor_dados[0]}) y cuenta con su ficha."
                            else:
                                turn_message = f"{socket_player_name} lanza {valor_dados} y mueve sus fichas."
                            time.sleep(0.2)  # Pausa antes de anunciar resultado
                            self.broadcast(turn_message)
                            
                            def solicitar_y_mover_fichas(client_socket, socket_player_name, valor_dados):
                                """Maneja la solicitud y movimiento de fichas"""
                                time.sleep(0.2)
                                self.send_message(client_socket, "Dame las fichas")
                                
                                # Obtener fichas válidas
                                pos_fichas = False
                                while not pos_fichas:
                                    respuesta_fichas = client_socket.recv(1024).decode('utf-8')
                                    while "mover_fichas:" not in respuesta_fichas:
                                        time.sleep(0.2)
                                        self.send_message(client_socket, "Dame las fichas")
                                        respuesta_fichas = client_socket.recv(1024).decode('utf-8')
                                    
                                    # Procesar respuesta
                                    if self.parques.verificar_condicion_un_dado(jugador):
                                        partes = respuesta_fichas.split(":")[1].split(",")
                                        ficha = int(partes[0])  
                                        dado = int(partes[1])
                                        print("Tengo la ficha: ", ficha)

                                        # Validar movimiento
                                        print("Dados: ", valor_dados, "Dado: ", dado)
                                        pos_fichas = self.parques.movimiento_fichas(dado, 0, ficha, ficha)
                                    else:
                                        partes = respuesta_fichas.split(":")[1].split(",") 
                                        ficha1 = int(partes[0])
                                        dado1 = int(partes[1])
                                        ficha2 = int(partes[2])
                                        dado2 = int(partes[3])
                                        print("Tengo las fichas: ", ficha1, ficha2)
                                        
                                        # Validar movimiento
                                        pos_fichas = self.parques.movimiento_fichas(dado1, dado2, ficha1, ficha2)
                                    if not pos_fichas:
                                        self.send_message(client_socket, "Movimiento de fichas no válido. Inténtalo de nuevo.")
                                        self.intentos_fallidos += 1
                                        if self.intentos_fallidos == self.intentos_maximos:
                                            self.intentos_fallidos = 0
                                            return
                                        time.sleep(0.2)
                                        self.send_message(client_socket, "Dame las fichas")
                                
                                # Actualizar posiciones y notificar
                                self.player_colors_and_positions[socket_player_name] = (
                                    self.player_colors_and_positions[socket_player_name][0], 
                                    pos_fichas
                                )
                                print("Movimiento de fichas exitoso")
                                
                                return pos_fichas

                            if self.parques.dados.es_par:  # Par
                                salio_de_carcel = False
                                # Sacar fichas de la cárcel si lanzó par
                                for ficha in jugador.fichas: 
                                    if ficha.casilla == self.parques.tablero.casillas[TipoDeCelda.CARCEL][ficha.color - 1]:
                                        self.parques.tablero.salir_de_carcel(ficha)
                                        salio_de_carcel = True
                                        self.player_colors_and_positions[socket_player_name] = (ficha.color, self.parques.obtener_posiciones_fichas())
                                
                                if not salio_de_carcel:
                                    jugador.pares_consecutivos += 1
                                    if jugador.pares_consecutivos == 3:
                                        # Lógica para sacar una ficha
                                        jugador.pares_consecutivos = 0
                                        self.send_message(client_socket, "Tienes 3 pares consecutivos. Selecciona una ficha para sacar.")
                                        respuesta = client_socket.recv(1024).decode('utf-8')
                                        if "sacar_ficha" in respuesta:
                                            ficha_sacar = int(respuesta.split(":")[1]) 
                                            print(f"Sacando ficha {ficha_sacar}")
                                            self.parques.sacar_ficha(ficha_sacar)
                                            ficha_sacar = jugador.fichas[ficha_sacar]
                                            self.player_colors_and_positions[socket_player_name] = (ficha_sacar.color, self.parques.obtener_posiciones_fichas())
                                        self.parques.cambiar_turno()
                                        self.intentos_fallidos = 0
                                    else:
                                        if self.parques.verificar_condicion_un_dado(jugador):
                                            solicitar_y_mover_fichas(client_socket, socket_player_name, valor_dados)
                                            jugador.pares_consecutivos = 0
                                            self.parques.cambiar_turno()
                                            self.intentos_fallidos = 0
                                        else:
                                            solicitar_y_mover_fichas(client_socket, socket_player_name, valor_dados)
                            else: # Impar
                                if self.parques.verificar_si_alguna_ficha_puede_moverse(jugador): 
                                    solicitar_y_mover_fichas(client_socket, socket_player_name, valor_dados)
                                    jugador.pares_consecutivos = 0
                                    self.parques.cambiar_turno()
                                    self.intentos_fallidos = 0
                                else:
                                    self.parques.cambiar_turno()
                                    self.intentos_fallidos = 0
                                    jugador.pares_consecutivos = 0

                            if self.parques.ganador:
                                fichas_en_carcel = []
                                fichas_en_cielo = []
                                fichas_cielo = []

                                for jugador in self.parques.jugadores:
                                    for ficha in jugador.fichas:
                                        if ficha.casilla == self.parques.tablero.casillas[TipoDeCelda.CARCEL][ficha.color - 1]:
                                            fichas_en_carcel.append({
                                                'numero': ficha.numero, 
                                                'color': ficha.color, 
                                                'pos': -1
                                            })
                                        
                                        for casilla_cielo in self.parques.tablero.casillas[TipoDeCelda.CAMINO_CIELO]:
                                            if ficha.casilla == casilla_cielo:
                                                fichas_en_cielo.append({
                                                    'numero': ficha.numero, 
                                                    'color': ficha.color, 
                                                    'pos': str(casilla_cielo.numero)
                                                })

                                        for cielo in self.parques.tablero.casillas[TipoDeCelda.CIELO]:
                                            if ficha.casilla == cielo:
                                                fichas_cielo.append({
                                                    'numero': ficha.numero, 
                                                    'color': ficha.color, 
                                                    'pos': f"CIELO{cielo.numero}"
                                                })

                                initial_positions_message = "Posiciones iniciales: "
                                for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                                    for ficha in fichas_en_carcel + fichas_en_cielo + fichas_cielo: 
                                        if ficha['color'] == color:
                                            if isinstance(ficha['pos'], int):
                                                posiciones[ficha['numero'] - 1] = ficha['pos']
                                            elif isinstance(ficha['pos'], str):
                                                if "CIELO" in ficha['pos']:
                                                    posiciones[ficha['numero'] - 1] = f"{ficha['pos']}"
                                                else:
                                                    posiciones[ficha['numero'] - 1] = f"CAMINO_CIELO:{ficha['pos']}"
                                    
                                    initial_positions_message += f"{nombre}.{color}.{posiciones};"

                                self.broadcast(initial_positions_message)

                                time.sleep(0.3)  # Pausa más larga antes de anunciar ganador
                                winner_message = f"El ganador es {socket_player_name}!"
                                self.broadcast(winner_message)
                                break
                            else:
                                fichas_en_carcel = []
                                fichas_en_cielo = []
                                fichas_cielo = []

                                for jugador in self.parques.jugadores:
                                    for ficha in jugador.fichas:
                                        if ficha.casilla == self.parques.tablero.casillas[TipoDeCelda.CARCEL][ficha.color - 1]:
                                            fichas_en_carcel.append({
                                                'numero': ficha.numero, 
                                                'color': ficha.color, 
                                                'pos': -1
                                            })
                                        
                                        for casilla_cielo in self.parques.tablero.casillas[TipoDeCelda.CAMINO_CIELO]:
                                            if ficha.casilla == casilla_cielo:
                                                fichas_en_cielo.append({
                                                    'numero': ficha.numero, 
                                                    'color': ficha.color, 
                                                    'pos': str(casilla_cielo.numero)
                                                })

                                        for cielo in self.parques.tablero.casillas[TipoDeCelda.CIELO]:
                                            if ficha.casilla == cielo:
                                                fichas_cielo.append({
                                                    'numero': ficha.numero, 
                                                    'color': ficha.color, 
                                                    'pos': f"CIELO{cielo.numero}"
                                                })

                                initial_positions_message = "Posiciones iniciales: "
                                for nombre, (color, posiciones) in self.player_colors_and_positions.items():
                                    for ficha in fichas_en_carcel + fichas_en_cielo + fichas_cielo: 
                                        if ficha['color'] == color:
                                            if isinstance(ficha['pos'], int):
                                                posiciones[ficha['numero'] - 1] = ficha['pos']
                                            elif isinstance(ficha['pos'], str):
                                                if "CIELO" in ficha['pos']:
                                                    posiciones[ficha['numero'] - 1] = f"{ficha['pos']}"
                                                else:
                                                    posiciones[ficha['numero'] - 1] = f"CAMINO_CIELO:{ficha['pos']}"
                                    
                                    initial_positions_message += f"{nombre}.{color}.{posiciones};"

                                self.broadcast(initial_positions_message)
                else:
                    time.sleep(0.2)  # Pausa antes de mensaje de espera
                    self.send_message(client_socket, "Espera tu turno.")
                    while self.parques.jugador_actual.nombre != socket_player_name:
                        time.sleep(0.5)  # Reducir la frecuencia de verificación


    def start(self):
        print("Servidor iniciado. Esperando jugadores...")
        while True:
            try:
                client_socket, address = self.server.accept()
                print(f"Jugador conectado desde {address}")
                thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                thread.start()
            except Exception as e:
                print(f"Error en la conexión: {str(e)}")
                continue

if __name__ == "__main__":
    server = Server()
    server.start()