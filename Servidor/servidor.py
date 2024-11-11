import socket
import threading
from parques import Parques
import time

class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(4)  # Máximo de 4 jugadores
        self.clients = []
        self.parques = Parques()
        self.lock = threading.Lock() # Para sincronizar el acceso a los datos
        self.juego_iniciado = False

    def broadcast(self, message, exclude_client=None):
        for client in self.clients:
            if client != exclude_client:
                try:
                    print(f"Enviando mensaje a {client.getpeername()}: {message}")
                    client.sendall(message.encode('utf-8'))
                except:
                    self.clients.remove(client)

    def recibir_respuestas(self):
        respuestas = []
        for client in self.clients:
            respuesta = client.recv(1024).decode('utf-8')
            respuestas.append(respuesta)
        return respuestas

    def handle_client(self, client_socket, address):
        try:
            nombre = client_socket.recv(1024).decode('utf-8')
            color = len(self.clients) + 1
            self.parques.agregar_jugador(nombre, color)
            if len(self.clients) == 1:
                self.parques.iniciar(self.parques.jugadores[0])

            welcome_msg = f"Bienvenido, {nombre}!"
            client_socket.sendall(welcome_msg.encode('utf-8')) 
            self.broadcast(f"{nombre} se ha unido al juego.", exclude_client=client_socket)
            
            if len(self.clients) == 1:
                self.broadcast("Esperando más jugadores...", exclude_client=None)
            elif len(self.clients) >= 2:
                self.broadcast("¿Desean iniciar el juego ahora? (si/no)")
                respuestas = []
                respuestas = self.recibir_respuestas() # Recibir respuesta de cada jugador

                if len(respuestas) == len(self.clients): 
                    if all([r == 'si' for r in respuestas]) or len(self.clients) == 4: 
                        self.juego_iniciado = True
                        self.broadcast("El juego ha comenzado!", exclude_client=None)
                    else:
                        self.broadcast("Esperando más jugadores...", exclude_client=None)
                        time.sleep(10) # Esperar 10 segundos
                        self.broadcast("¿Desean iniciar el juego ahora? (si/no)")
                        respuestas = []
                        respuestas = self.recibir_respuestas()  # Vuelve a recibir las respuestas

                        # Verifica si todos han dicho 'si' después de esperar
                        if all([r == 'si' for r in respuestas]) or len(self.clients) == 4:
                            self.juego_iniciado = True
                            self.broadcast("El juego ha comenzado!", exclude_client=None)
                        else:
                            self.juego_iniciado = True
                            self.broadcast("El juego ha comenzado, con los jugadores actuales.", exclude_client=None)

            if self.juego_iniciado:
                while not self.parques.ganador:
                    with self.lock:
                        jugador = self.parques.jugador_actual
                        if jugador.nombre == nombre:
                            client_socket.sendall("Es tu turno. Presiona Enter para lanzar los dados.".encode('utf-8'))
                            client_socket.recv(1024)  # Espera a que el jugador presione Enter

                            valor_dados = self.parques.lanzar_dados()
                            self.parques.movimiento_fichas(sum(valor_dados))
                            turn_message = f"{nombre} lanza {valor_dados} y mueve sus fichas."
                            print(turn_message)
                            self.broadcast(turn_message)

                            if self.parques.ganador:
                                winner_message = f"El ganador es {nombre}!"
                                self.broadcast(winner_message)
                                break

                            self.parques.cambiar_turno()
                        else:
                            client_socket.sendall("Espera tu turno.".encode('utf-8'))

                client_socket.close()
        except Exception as e:
            print(f"Error al manejar al cliente {address}: {str(e)}")
            self.broadcast(f"{nombre} ha abandonado el juego.")
            time.sleep(3)
            #Reiniciar servidor
            self.juego_iniciado = False
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()

    def start(self):
        print("Servidor iniciado. Esperando jugadores...")
        while len(self.clients) < 4:
            client_socket, address = self.server.accept()
            print(f"Jugador conectado desde {address}")
            self.clients.append(client_socket)
            thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()