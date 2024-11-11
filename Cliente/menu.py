import pygame 
import sys
import os

class Menu:
    def __init__(self, cliente):
        pygame.init()
        self.pantalla = pygame.display.set_mode((700, 700))
        self.fuente = pygame.font.Font(None, 36)
        self.imagen_fondo = pygame.transform.scale(pygame.image.load(os.path.join('images/menu-carga.jpeg')), (700, 700))
        self.imagen = pygame.transform.scale(pygame.image.load(os.path.join('images/menu-cambio.jpeg')), (700, 700))
        self.imagen_cambio = pygame.transform.scale(pygame.image.load(os.path.join('images/menu.jpeg')), (700, 700))
        self.salir_cambio = pygame.transform.scale(pygame.image.load(os.path.join('images/salir-cambio.jpeg')), (700, 700))
        self.jugar_iniciado = False
        self.cliente = cliente

    def entrada_texto(self, mensaje, tipo):
        texto = ''  # Texto del input
        activo = True  # Control del input

        # Función de verificación de finalización del input según el tipo
        def es_valido(texto):
            if tipo == "unica":
                return False  # Continua hasta presionar Enter
            elif tipo == "condicional":
                return texto.lower() in ["si", "no"]  # Termina si el texto es "si" o "no"
            return False  # Por defecto, no termina

        while activo:
            self.pantalla.blit(self.imagen_fondo, (0, 0))  # Mostrar la imagen de fondo

            # Capturar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and tipo == "unica":  # Presionar Enter en "unica" termina el input
                        activo = False
                    elif event.key == pygame.K_BACKSPACE:  # Si presiona Backspace
                        texto = texto[:-1]
                    else:
                        texto += event.unicode

            # Verificar si la entrada es válida según el tipo
            if es_valido(texto):
                activo = False

            self.mostrar_mensaje(mensaje + texto)

            pygame.display.update()

        return texto

    def mostrar_mensaje(self, mensaje):
        """ Renderiza el mensaje en la pantalla y muestra el texto completo """
        # Limpiar la pantalla y mostrar fondo
        self.pantalla.blit(self.imagen_fondo, (0, 0))

        if mensaje:
            texto_renderizado = self.fuente.render(mensaje, True, (0, 0, 0))
            self.pantalla.blit(texto_renderizado, (50, 300))  # Dibuja el texto
            pygame.display.update()  # Actualiza la pantalla para mostrar el mensaje

    def menu(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            # Verificar si el mouse está sobre el área de "Play"
            if 186 <= mouse_pos[0] <= 514 and 22 <= mouse_pos[1] <= 102:
                self.pantalla.blit(self.imagen_cambio, (0, 0))  
            elif 186 <= mouse_pos[0] <= 514 and 604 <= mouse_pos[1] <= 684:
                self.pantalla.blit(self.salir_cambio, (0, 0))
            else:
                self.pantalla.blit(self.imagen, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.cliente:  # Si el cliente está inicializado, cerramos la conexión
                        print("Cerrando conexión con el servidor...")
                        self.cliente.cerrar_conexion()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if event.button == 1:
                        # Si el clic ocurre en el área de "Jugar"
                        if 186 <= event.pos[0] <= 514 and 22 <= event.pos[1] <= 102:
                            self.jugar_iniciado = True
                            return self.jugar_iniciado
                        elif 186 <= event.pos[0] <= 514 and 604 <= event.pos[1] <= 684:
                            if self.cliente:  # Si el cliente está inicializado, cerramos la conexión
                                print("Cerrando conexión con el servidor...")
                                self.cliente.cerrar_conexion()
                            pygame.quit()
                            return False

            pygame.display.update()

    def close(self):
        pygame.quit()
