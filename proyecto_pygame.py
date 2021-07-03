# pip install pygame
import pygame

# inicializamos puntaje
score_player_one = 0
score_player_two = 0
number_of_game = 0
# Incializar
pygame.init()
# Colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
# Pantalla
pantalla_x = 800
pantalla_y = 600
tamanho_pantalla = (pantalla_x, pantalla_y)
# Paleta
ancho_jugador = 15
alto_jugador = 90
# Creamos una pantalla
pantalla = pygame.display.set_mode(tamanho_pantalla)
scored_static = pygame.font.SysFont("Arial", 20).render("Puntaje", 2, (255, 255, 255))
# Reloj: FPS
reloj = pygame.time.Clock()
# Coordenadas de Jugador 1
jugador1_x = 50
jugador1_y = (pantalla_y // 2) - (alto_jugador // 2)
# Coordenadas de Jugador 2
jugador2_x = (pantalla_x - 50) - ancho_jugador
jugador2_y = (pantalla_y // 2) - (alto_jugador // 2)
# Movimientos de los jugadores
mov_jugador1 = 0
mov_jugador2 = 0
# Coordenadas de la pelota
pelota_x = pantalla_x // 2
pelota_y = pantalla_y // 2
mov_pelota_x = 3
mov_pelota_y = 3
# Flag: bandera de fin de juego
force_game_over = False
game_over = False
while not force_game_over:
    while not game_over:

        # Gestionar eventos: detecta las acciones de los usuarios
        for evento in pygame.event.get():
            # print(evento)
            # Cuando presione X, debe salir
            if evento.type == pygame.QUIT:
                force_game_over = True
            # Si se presiona una tecla
            if evento.type == pygame.KEYDOWN:
                # Jugador 1
                if evento.key == pygame.K_w:
                    mov_jugador1 = -3
                if evento.key == pygame.K_s:
                    mov_jugador1 = 3
                # Jugador 2
                if evento.key == pygame.K_UP:
                    mov_jugador2 = -3
                if evento.key == pygame.K_DOWN:
                    mov_jugador2 = 3
            # Si se deja de presionar la tecla:
            if evento.type == pygame.KEYUP:
                # Jugador 1
                if evento.key == pygame.K_w:
                    mov_jugador1 = 0
                if evento.key == pygame.K_s:
                    mov_jugador1 = 0
                # Jugador 2
                if evento.key == pygame.K_UP:
                    mov_jugador2 = 0
                if evento.key == pygame.K_DOWN:
                    mov_jugador2 = 0

        if number_of_game % 2 == 0 and (pelota_x < 0 or pelota_x > pantalla_x):
            mov_pelota_x += number_of_game
            mov_pelota_y += number_of_game
        # Validación

        if pelota_y > pantalla_y or pelota_y < 0:
            mov_pelota_y *= -1
        # Si la pelota sale por el lado izquierdo o derecho es porque alguien perdió y guardamos puntaje

        if pelota_x < 0:
            pelota_x = pantalla_x // 2
            pelota_y = pantalla_y // 2
            mov_pelota_x *= -1
            mov_pelota_y *= -1
            score_player_one += 1
            number_of_game += 1
        elif pelota_x > pantalla_x:
            pelota_x = pantalla_x // 2
            pelota_y = pantalla_y // 2
            mov_pelota_x *= -1
            mov_pelota_y *= -1
            score_player_two += 1
            number_of_game += 1

        if number_of_game == 10:
            game_over = True
        # Mover a los jugadores|
        jugador1_y += mov_jugador1
        jugador2_y += mov_jugador2
        # Mover a la pelota
        pelota_x += mov_pelota_x
        pelota_y += mov_pelota_y
        # Gráficos
        pantalla.fill(negro)
        # Dibujamos Jugador 1
        jugador1 = pygame.draw.rect(
            pantalla, blanco, (jugador1_x, jugador1_y, ancho_jugador, alto_jugador)
        )
        # Dibujamos Jugador 2
        jugador2 = pygame.draw.rect(
            pantalla, blanco, (jugador2_x, jugador2_y, ancho_jugador, alto_jugador)
        )
        # Dibujamos la pelota
        pelota = pygame.draw.circle(pantalla, blanco, (pelota_x, pelota_y), 10)
        # Colisiones
        if pelota.colliderect(jugador1) or pelota.colliderect(jugador2):
            mov_pelota_x *= -1

        # creamos objeto de score
        scored_player_one = pygame.font.SysFont("Arial", 40).render(
            str(score_player_one), 2, (255, 255, 255)
        )
        scored_player_two = pygame.font.SysFont("Arial", 40).render(
            str(score_player_two), 2, (255, 255, 255)
        )
        speed = pygame.font.SysFont("Arial", 20).render(
            str(abs(mov_pelota_x)), 2, (255, 255, 255)
        )
        ngame = pygame.font.SysFont("Arial", 20).render(
            str(number_of_game), 2, (255, 255, 255)
        )
        speed_text = pygame.font.SysFont("Arial", 20).render(
            str("Velocidad: "), 2, (255, 255, 255)
        )
        ngame_text = pygame.font.SysFont("Arial", 20).render(
            str("Número de partido: "), 2, (255, 255, 255)
        )

        # Resfrescar pantalla

        pantalla.blit(scored_player_one, (100, 10))
        pantalla.blit(scored_player_two, (pantalla_x - 100, 10))
        pantalla.blit(speed, (380, pantalla_y - 50))
        pantalla.blit(ngame, (200, pantalla_y - 50))
        pantalla.blit(speed_text, (300, pantalla_y - 50))
        pantalla.blit(ngame_text, (50, pantalla_y - 50))

        pygame.display.flip()
        # FPS
        reloj.tick(60)

    pygame.display.flip()
    pantalla.fill((0, 0, 0))
    gameover_text = pygame.font.SysFont("Arial", 100).render(
        str("GAMEOVER"), 2, (255, 255, 255)
    )
    gameover_text_rect = gameover_text.get_rect(
        center=(pantalla_x // 2, pantalla_y // 2)
    )

    press_any_key = pygame.font.SysFont("Arial", 25).render(
        str("Press Any Key to try again"), 2, (255, 255, 255)
    )
    press_any_key_rect = press_any_key.get_rect(
        center=(pantalla_x // 2, pantalla_y // 2 + 250)
    )

    pantalla.blit(gameover_text, gameover_text_rect)
    pantalla.blit(press_any_key, press_any_key_rect)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            force_game_over = True
        if evento.type == pygame.KEYUP:
            game_over = False
            mov_pelota_x = 3
            mov_pelota_y = 3
            score_player_one = 0
            score_player_two = 0
            number_of_game = 0
            jugador1_x = 50
            jugador1_y = (pantalla_y // 2) - (alto_jugador // 2)
            jugador2_x = (pantalla_x - 50) - ancho_jugador
            jugador2_y = (pantalla_y // 2) - (alto_jugador // 2)
        break
pygame.display.flip()
