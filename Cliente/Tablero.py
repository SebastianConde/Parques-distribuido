import pygame
import sys
import MapeoTablero as MP

def main():
    pygame.init()

    WIDTH, HEIGHT = 700, 700
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Parqués")

    Tablero = pygame.image.load("tablero.jpeg")
    Tablero = pygame.transform.scale(Tablero, (WIDTH, HEIGHT))

    Num_fichas = 4

    #Nombres de jugadores
    Jugador1 = "Jugador 1"
    Jugador2 = "Jugador 2"
    Jugador3 = "Jugador 3"
    Jugador4 = "Jugador 4"

    Ficha_roja = pygame.image.load("ficha_roja.png")
    Ficha_roja = pygame.transform.scale(Ficha_roja, (20, 20))
    Ficha_amarilla = pygame.image.load("ficha_amarilla.png")
    Ficha_amarilla = pygame.transform.scale(Ficha_amarilla, (20, 20))
    Ficha_verde = pygame.image.load("ficha_verde.png")
    Ficha_verde = pygame.transform.scale(Ficha_verde, (20, 20))
    Ficha_azul = pygame.image.load("ficha_azul.png")
    Ficha_azul = pygame.transform.scale(Ficha_azul, (20, 20))


    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.blit(Tablero, (0, 0))


        #Textos de los nombres de los jugadores
        font = pygame.font.Font(None, 36)  
        texto = font.render(Jugador1, True, (244, 110, 110) )
        window.blit(texto, (MP.carceles["ROJA"][0] + 10, MP.carceles["ROJA"][1] + 10)) 
        texto = font.render(Jugador3, True, (0, 0, 255))
        window.blit(texto, (MP.carceles["AZUL"][0] + 90, MP.carceles["AZUL"][1] + 170))
        texto = font.render(Jugador2, True, (255, 255, 255))
        window.blit(texto, (MP.carceles["AMARILLA"][0] + 10, MP.carceles["AMARILLA"][1] + 170))
        texto = font.render(Jugador4, True, (0, 255, 0))
        window.blit(texto, (MP.carceles["VERDE"][0] + 90, MP.carceles["VERDE"][1] + 10))

        #Fichas en las carceles
        for i in range(Num_fichas):
            window.blit(Ficha_roja, (40 + MP.carceles["ROJA"][0] + i*40, MP.carceles["ROJA"][1] + 100))
            window.blit(Ficha_azul, (40 + MP.carceles["AZUL"][0] + i*40, MP.carceles["AZUL"][1] + 100))
            window.blit(Ficha_amarilla, (40 + MP.carceles["AMARILLA"][0] + i*40, MP.carceles["AMARILLA"][1] + 100))
            window.blit(Ficha_verde, (40 + MP.carceles["VERDE"][0] + i*40, MP.carceles["VERDE"][1] + 100))
        
        #Fichas en los seguros iniciales
        for i in range(Num_fichas):
            window.blit(Ficha_roja, (MP.seguros_inicios["ROJO_INICIO"][0]+i*20, MP.seguros_inicios["ROJO_INICIO"][1] + 5))
            window.blit(Ficha_azul, (MP.seguros_inicios["AZUL_INICIO"][0]+i*20, MP.seguros_inicios["AZUL_INICIO"][1] + 5))
            window.blit(Ficha_amarilla, (MP.seguros_inicios["AMARILLO_INICIO"][0]+5, MP.seguros_inicios["AMARILLO_INICIO"][1] + i*20))
            window.blit(Ficha_verde, (MP.seguros_inicios["VERDE_INICIO"][0]+5, MP.seguros_inicios["VERDE_INICIO"][1] + i*20))

        #Fichas en la meta
        for i in range(Num_fichas):
            window.blit(Ficha_roja, (35 + MP.meta["ROJO8"][0]+i*30, MP.meta["ROJO8"][1] + 20))
            window.blit(Ficha_azul, (35 + MP.meta["AZUL8"][0]+i*30, MP.meta["AZUL8"][1] - 40))
            window.blit(Ficha_amarilla, (20 + MP.meta["AMARILLO8"][0], 35 + MP.meta["AMARILLO8"][1] + i*30))
            window.blit(Ficha_verde, (-40 + MP.meta["VERDE8"][0], 35 + MP.meta["VERDE8"][1] + i*30))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

main()