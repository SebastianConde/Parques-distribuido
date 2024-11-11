import socket
import threading
from parques import Parques
import time

class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(4)
        self.clients = []  # Lista de tuplas (socket, nombre)
        self.parques = Parques()
        self.lock = threading.Lock()
        self.juego_iniciado = False
        self.respuestas = []

    def broadcast(self, message, exclude_socket=None):
        for client_socket, _ in self.clients:
            if client_socket != exclude_socket:
                try:
                    print(f"Enviando mensaje a {client_socket.getpeername()}: {message}")
                    client_socket.sendall(message.encode('utf-8'))
                except:
                    self.clients.remove((client_socket, _))

    def recibir_respuestas(self, client_socket):
        respuesta = client_socket.recv(1024).decode('utf-8')
        self.respuestas.append(respuesta)

    def get_player_name(self, client_socket):
        """Obtiene el nombre del jugador asociado a un socket"""
        for socket, nombre in self.clients:
            if socket == client_socket:
                return nombre
        return None

    def handle_client(self, client_socket, address):
        try:
            nombre = client_socket.recv(1024).decode('utf-8')
            self.broadcast(f"{nombre} se ha unido al juego.", client_socket)
            with self.lock:
                self.clients.append((client_socket, nombre))
                color = len(self.clients)
                self.parques.agregar_jugador(nombre, color)
                if len(self.clients) == 1:
                    self.parques.iniciar(self.parques.jugadores[0])

            welcome_msg = f"Bienvenido, {nombre}!"
            client_socket.sendall(welcome_msg.encode('utf-8'))

            while not self.juego_iniciado:
                if len(self.clients) == 1:
                    client_socket.sendall("Esperando más jugadores...".encode('utf-8'))
                    while len(self.clients) < 2:
                        pass
                elif len(self.clients) >= 2:
                    client_socket.sendall("¿Desean iniciar el juego ahora? (si/no)".encode('utf-8'))
                    self.respuestas = []
                    self.recibir_respuestas(client_socket)
                    
                    while len(self.respuestas) < len(self.clients):
                        pass
                    if len(self.respuestas) == len(self.clients):
                        if all([r == 'si' for r in self.respuestas]) or len(self.clients) == 4:
                            self.juego_iniciado = True
                            client_socket.sendall("El juego ha comenzado!".encode('utf-8'))
                        else:
                            self.broadcast("Esperando más jugadores...")
                            time.sleep(10)
                            client_socket.sendall("Desean iniciar el juego ahora? (si/no)".encode('utf-8'))
                            self.respuestas = []
                            self.recibir_respuestas(client_socket)

                            if all([r == 'si' for r in self.respuestas]) or len(self.clients) == 4:
                                self.juego_iniciado = True
                                client_socket.sendall("El juego ha comenzado!".encode('utf-8'))
                            else:
                                self.juego_iniciado = True
                                client_socket.sendall("El juego ha comenzado con los jugadores actuales.".encode('utf-8'))

            # Si el juego está iniciado, comienza el manejo de turnos
            if self.juego_iniciado:
                self.manejar_turno(client_socket)

        except Exception as e:
            print(f"Error al manejar al cliente {address}: {str(e)}")
            nombre = self.get_player_name(client_socket)
            if nombre:
                self.broadcast(f"{nombre} ha abandonado el juego.")
            time.sleep(3)
            self.juego_iniciado = False
            self.clients = [(s, n) for s, n in self.clients if s != client_socket]
            client_socket.close()


    def manejar_turno(self, client_socket):
        """Lógica para manejar el turno de un jugador."""
        while not self.parques.ganador:
            with self.lock:  
                jugador = self.parques.jugador_actual
                if jugador:
                    current_player_name = jugador.nombre
                    socket_player_name = self.get_player_name(client_socket)
                    
                    if current_player_name == socket_player_name:
                        # Es el turno del jugador, le pedimos que presione Enter para lanzar los dados
                        client_socket.sendall("Es tu turno. Lanza los dados".encode('utf-8'))
                        respuesta = client_socket.recv(1024).decode('utf-8')

                        if respuesta == "dados":
                            # El jugador lanza los dados
                            valor_dados = self.parques.lanzar_dados()
                            self.parques.movimiento_fichas(sum(valor_dados))
                            turn_message = f"{socket_player_name} lanza {valor_dados} y mueve sus fichas."
                            print(turn_message)
                            self.broadcast(turn_message)

                            if self.parques.ganador:
                                # Si hay ganador, se informa y termina el juego
                                winner_message = f"El ganador es {socket_player_name}!"
                                self.broadcast(winner_message)
                                break

                            # Cambiar de turno
                            self.parques.cambiar_turno()
                    else:
                        # El jugador no tiene su turno, se lo indica
                        client_socket.sendall("Espera tu turno.".encode('utf-8'))


    def start(self):
        print("Servidor iniciado. Esperando jugadores...")
        while len(self.clients) < 4:
            client_socket, address = self.server.accept()
            print(f"Jugador conectado desde {address}")
            thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()