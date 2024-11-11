import pygame
import threading
import queue
from juego import JuegoParques
import time

class ClienteJuego:
    def __init__(self, nombres, jugador, client_socket):
        self.juego = JuegoParques(nombres)
        self.jugador = jugador
        self.client_socket = client_socket  # Socket para comunicación con el servidor
        self.mensaje_queue = queue.Queue()
        self.running = True
        self.turno = False
        self.esperando_respuesta = False
        self.ultimo_mensaje = None

    def recibir_mensajes_servidor(self):
        """Thread worker para recibir mensajes del servidor"""
        while self.running:
            try:
                if self.client_socket:
                    mensaje = self.client_socket.recv(1024).decode('utf-8')
                    if mensaje:
                        self.mensaje_queue.put(mensaje)
            except:
                if self.running:
                    print("Error al recibir mensaje del servidor.")
                break

    def enviar_mensaje_servidor(self, mensaje):
        """Envía un mensaje al servidor"""
        try:
            if self.client_socket:
                self.client_socket.sendall(mensaje.encode('utf-8'))
        except:
            print("Error al enviar mensaje al servidor.")

    def procesar_mensajes(self):
        """Procesa los mensajes de la cola"""
        while not self.mensaje_queue.empty():
            mensaje = self.mensaje_queue.get()
            
            if mensaje != self.ultimo_mensaje:
                self.juego.mostrar_mensaje(mensaje)
                self.ultimo_mensaje = mensaje
                
                if "Es tu turno" in mensaje:
                    self.turno = True
                    self.esperando_respuesta = True
                elif "Espera tu turno" in mensaje:
                    self.turno = False
                    self.esperando_respuesta = False
                # Aquí puedes agregar más condiciones según los mensajes que envíe tu servidor

    def ejecutar(self):
        """Ejecuta el cliente de juego"""
        # Iniciar thread para recibir mensajes del servidor
        thread_servidor = threading.Thread(target=self.recibir_mensajes_servidor)
        thread_servidor.daemon = True
        thread_servidor.start()

        # Bucle principal
        while self.running:
            # Procesar mensajes
            self.procesar_mensajes()

            # Manejar eventos de Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                
                # Si es nuestro turno y presionamos ENTER
                if self.esperando_respuesta and self.turno:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("Jugador realizó su turno")
                            self.enviar_mensaje_servidor("TURNO_COMPLETADO")
                            self.esperando_respuesta = False
                            self.turno = False

            # Actualizar pantalla
            self.juego.actualizar_pantalla()
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def cerrar(self):
        """Cierra el cliente de juego"""
        self.running = False
        if self.juego:
            self.juego.close()
