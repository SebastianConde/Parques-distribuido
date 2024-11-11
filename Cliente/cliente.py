import socket
from juego import JuegoParques
from menu import Menu
import time
import threading
import queue
import pygame

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
        self.estado_actual = "MENU"  # Estados: MENU, ENTRADA_NOMBRE, JUGANDO, ESPERANDO_INICIO
        self.ultimo_mensaje = None
        self.tiempo_mensaje = 0
        self.ventana_actual = "MENU"  # Estados: MENU, JUEGO

    def recibir_mensajes(self):
        """Thread worker para recibir mensajes del servidor"""
        while self.running:
            try:
                if self.client_socket:
                    mensaje = self.client_socket.recv(1024).decode('utf-8')
                    if mensaje:
                        self.mensaje_queue.put(mensaje)
            except:
                if self.running:
                    print("Error al recibir el mensaje.")
                break

    def mostrar_mensaje_con_delay(self, mensaje):
        """Muestra un mensaje y espera el tiempo especificado"""
        if mensaje != self.ultimo_mensaje:
            if self.ventana_actual == "MENU" and self.menu:
                self.menu.mostrar_mensaje(mensaje)
            elif self.ventana_actual == "JUEGO" and self.juego:
                self.juego.mostrar_mensaje(mensaje)
            
            self.ultimo_mensaje = mensaje
            self.tiempo_mensaje = time.time()
            time.sleep(3)

    def procesar_mensajes(self):
        """Procesa los mensajes recibidos sin bloquear"""
        while not self.mensaje_queue.empty():
            mensaje = self.mensaje_queue.get()
            print(f"Mensaje recibido: {mensaje}")  # Debug
            
            # Verificar si el juego ha comenzado
            if "El juego ha comenzado" in mensaje:
                self.mostrar_mensaje_con_delay(mensaje)
                self.estado_actual = "JUGANDO"
                self.esperando_inicio = False
                self.transicion_a_juego()
            else:
                self.mostrar_mensaje_con_delay(mensaje)
            
            if "¿Desean iniciar el juego ahora? (si/no)" in mensaje:
                self.estado_actual = "ESPERANDO_INICIO"
                self.esperando_inicio = True
            
            if "Es tu turno" in mensaje:
                self.turno = True
                self.esperando_respuesta = True
                self.mostrar_mensaje_con_delay(mensaje)
            elif "Espera tu turno" in mensaje:
                self.turno = False
                self.mostrar_mensaje_con_delay(mensaje)
            else:
                self.mostrar_mensaje_con_delay(mensaje)

    def transicion_a_juego(self):
        """Maneja la transición de la ventana de menú a la ventana de juego"""
        print("Ejecutando transición a juego...")  # Debug
        
        if self.menu:
            self.menu.close()
            self.menu = None
        
        # Inicializar la ventana de juego
        self.juego = JuegoParques()
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
            self.estado_actual = "JUGANDO"

            # Bucle principal del juego
            while self.running:
                # Procesar mensajes pendientes
                self.procesar_mensajes()

                # Manejar estados específicos
                if self.estado_actual == "ESPERANDO_INICIO" and self.esperando_inicio:
                    respuesta = self.entrada_texto_con_delay("¿Deseas iniciar el juego ahora? (si/no): ", "condicional")
                    if respuesta.lower() in ['si', 'no']:
                        self.enviar_respuesta(respuesta.lower())
                        self.esperando_inicio = False
                        time.sleep(3)

                # Manejar eventos de Pygame
                ventana_actual = self.juego if self.ventana_actual == "JUEGO" else self.menu
                if ventana_actual:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            break
                    if self.ventana_actual == "JUEGO":
                        self.juego.actualizar_pantalla()
                        

                    # Actualizar la pantalla según la ventana actual
                    if ventana_actual:
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