import pygame
import sys
import MapeoTablero as MP

class JuegoParques:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 700, 700
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Parqués")
        
        # Cargar y escalar imágenes
        self.tablero = pygame.transform.scale(pygame.image.load("images/tablero.jpeg"), (self.WIDTH, self.HEIGHT))
        self.ficha_roja = pygame.transform.scale(pygame.image.load("images/ficha_roja.png"), (20, 20))
        self.ficha_amarilla = pygame.transform.scale(pygame.image.load("images/ficha_amarilla.png"), (20, 20))
        self.ficha_verde = pygame.transform.scale(pygame.image.load("images/ficha_verde.png"), (20, 20))
        self.ficha_azul = pygame.transform.scale(pygame.image.load("images/ficha_azul.png"), (20, 20))

        self.jugadores = {
            "Jugador1": {"nombre": "Jugador 1", "color": (244, 110, 110), "pos": MP.carceles["ROJA"]},
            "Jugador2": {"nombre": "Jugador 2", "color": (255, 255, 255), "pos": MP.carceles["AMARILLA"]},
            "Jugador3": {"nombre": "Jugador 3", "color": (0, 0, 255), "pos": MP.carceles["AZUL"]},
            "Jugador4": {"nombre": "Jugador 4", "color": (0, 255, 0), "pos": MP.carceles["VERDE"]}
        }

        self.num_fichas = 4
        self.font = pygame.font.Font(None, 36)
        self.font_mensajes = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
        # Nuevas variables para manejo de mensajes y entrada de texto
        self.mensaje_actual = ""
        self.tiempo_mensaje = 0
        self.input_text = ""
        self.input_active = False
        self.input_rect = pygame.Rect(10, self.HEIGHT - 40, 680, 30)
        self.input_type = None
        self.input_callback = None

    def dibujar_tablero(self):
        self.window.blit(self.tablero, (0, 0))

    def dibujar_jugadores(self):
        for jugador, datos in self.jugadores.items():
            texto = self.font.render(datos["nombre"], True, datos["color"])
            self.window.blit(texto, (datos["pos"][0] + 10, datos["pos"][1] + 10))

    def dibujar_fichas(self):
        for i in range(self.num_fichas):
            self.window.blit(self.ficha_roja, (40 + MP.carceles["ROJA"][0] + i * 40, MP.carceles["ROJA"][1] + 100))
            self.window.blit(self.ficha_azul, (40 + MP.carceles["AZUL"][0] + i * 40, MP.carceles["AZUL"][1] + 100))
            self.window.blit(self.ficha_amarilla, (40 + MP.carceles["AMARILLA"][0] + i * 40, MP.carceles["AMARILLA"][1] + 100))
            self.window.blit(self.ficha_verde, (40 + MP.carceles["VERDE"][0] + i * 40, MP.carceles["VERDE"][1] + 100))

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
        """Muestra un mensaje en la pantalla"""
        self.mensaje_actual = mensaje
        self.tiempo_mensaje = pygame.time.get_ticks()

    def dibujar_mensaje(self):
        """Dibuja el mensaje actual en la pantalla"""
        if self.mensaje_actual:
            mensaje_superficie = self.font_mensajes.render(self.mensaje_actual, True, (255, 255, 255))
            mensaje_rect = mensaje_superficie.get_rect(center=(self.WIDTH // 2, 550))
            self.window.blit(mensaje_superficie, mensaje_rect)

    def entrada_texto(self, mensaje, tipo):
        """Maneja la entrada de texto del usuario"""
        self.input_active = True
        self.input_text = ""
        self.input_type = tipo
        self.mostrar_mensaje(mensaje)

        while self.input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.input_type == "condicional":
                            if self.input_text.lower() in ['si', 'no']:
                                self.input_active = False
                                return self.input_text
                        else:
                            self.input_active = False
                            return self.input_text
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

            # Actualizar pantalla
            self.actualizar_pantalla()

            # Dibujar entrada de texto
            pygame.draw.rect(self.window, (255, 255, 255), self.input_rect, 2)
            text_surface = self.font.render(self.input_text, True, (255, 255, 255))
            self.window.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
            
            pygame.display.flip()
            self.clock.tick(60)

    def actualizar_pantalla(self):
        """Actualiza todos los elementos en la pantalla"""
        self.dibujar_tablero()
        self.dibujar_jugadores()
        self.dibujar_fichas()
        self.dibujar_seguros_iniciales()
        self.dibujar_metas()
        self.dibujar_mensaje()

    def close(self):
        """Cierra la ventana del juego"""
        pygame.quit()

    def correr_juego(self):
        """Ejecuta el bucle principal del juego"""
        print("Iniciando bucle del juego...")  # Debug
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break

            # Actualizar el estado del juego
            self.actualizar_pantalla()
            
            # Refrescar la pantalla
            pygame.display.flip()
            self.clock.tick(60)

        print("Saliendo del bucle del juego...")  # Debug

if __name__ == "__main__":
    juego = JuegoParques()
    juego.correr_juego()