import pygame
import sys

def crear_ventana(x, y, valor1, valor2, screen, font):
    pygame.draw.rect(screen, (255, 255, 255), (x-30, y-30, 60, 30)) # Dibujar el rectángulo
    screen.blit(valor1, (x-30, y-30, x, y)) # Dibujar el valor del dado 1
    screen.blit(valor2, (x, y-30, x+30, y)) # Dibujar el valor del dado 2


# Inicializar Pygame
pygame.init()

# Definir dimensiones de la ventana
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
font = pygame.font.Font(None, 36)
dado1 = pygame.transform.scale(pygame.image.load("images/1_dot.png"), (30, 30))
dado2 = pygame.transform.scale(pygame.image.load("images/2_dots.png"), (30, 30))

# Establecer el título de la ventana
pygame.display.set_caption("Mi Ventana Pygame")

# Definir el color de fondo (RGB)
background_color = (0, 0, 0)  # Negro
x = 145
y = 390
turno = True
mostrar_ventana = False

# Bucle principal del juego
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: 
            if x <= event.pos[0] <= x+20 and y <= event.pos[1] <= y+20 and turno:
                if turno:
                    mostrar_ventana = True
                    if x-10 <= event.pos[0] <= x+10 and y-20 <= event.pos[1] <= y:
                        print("Ficha seleccionada con valor de dado 1", dado1)
                    if x+10 <= event.pos[0] <= x+30 and y-20 <= event.pos[1] <= y:
                        print("Ficha seleccionada con valor de dado 2", dado2)
                else:
                    running = False

    # Rellenar la pantalla con el color de fondo
    screen.fill(background_color)

    if mostrar_ventana:
        crear_ventana(x, y, dado1, dado2, screen, font)

    # Obtener las coordenadas del mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Renderizar el texto con las coordenadas del mouse
    text = font.render(f'X: {mouse_x}, Y: {mouse_y}', True, (255, 255, 255))

    # Dibujar el texto en la pantalla
    screen.blit(text, (10, 10))
    # Actualizar la pantalla
    pygame.display.flip()

# Salir de Pygame
pygame.quit()
sys.exit()
