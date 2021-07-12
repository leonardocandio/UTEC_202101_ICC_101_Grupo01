# pip install pygame
import pygame

# inicializamos puntaje
score_player_one = 0
score_player_two = 0
number_of_game = 1
total_points = 0
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
game_over = False
while not game_over:
    while total_points < 10:

        # Gestionar eventos: detecta las acciones de los usuarios
        for evento in pygame.event.get():
            print(evento)
            # Cuando presione X, debe salir
            if evento.type == pygame.WINDOWCLOSE:
                game_over = True
                total_points = 99
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

        if pelota_y > pantalla_y or pelota_y < 0:
            mov_pelota_y *= -1
        # Si la pelota sale por el lado izquierdo o derecho es porque alguien perdió y guardamos puntaje

        if pelota_x < 0:
            pelota_x = pantalla_x // 2
            pelota_y = pantalla_y // 2
            mov_pelota_x *= -1
            mov_pelota_y *= -1
            score_player_one += 1
            total_points += 1
        elif pelota_x > pantalla_x:
            pelota_x = pantalla_x // 2
            pelota_y = pantalla_y // 2
            mov_pelota_x *= -1
            mov_pelota_y *= -1
            score_player_two += 1
            total_points += 1

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
        total_points_display = pygame.font.SysFont("Arial", 20).render(
            str(total_points), 2, (255, 255, 255)
        )
        number_of_game_display = pygame.font.SysFont("Arial", 20).render(
            str(number_of_game), 2, (255, 255, 255)
        )
        speed_text = pygame.font.SysFont("Arial", 20).render(
            str("Velocidad: "), 2, (255, 255, 255)
        )
        total_points_text = pygame.font.SysFont("Arial", 20).render(
            str("Puntos totales: "), 2, (255, 255, 255)
        )

        number_of_game_text = pygame.font.SysFont("Arial", 20).render(
            str("Número de partido: "), 2, (255, 255, 255)
        )

        # Resfrescar pantalla

        pantalla.blit(scored_player_one, (100, 10))
        pantalla.blit(scored_player_two, (pantalla_x - 100, 10))
        pantalla.blit(speed, (380, pantalla_y - 50))
        pantalla.blit(number_of_game_display, (600, pantalla_y - 50))
        pantalla.blit(total_points_display, (200, pantalla_y - 50))
        pantalla.blit(speed_text, (300, pantalla_y - 50))
        pantalla.blit(total_points_text, (50, pantalla_y - 50))
        pantalla.blit(number_of_game_text, (420, pantalla_y - 50))

        pygame.display.flip()
        # FPS
        reloj.tick(60)

    if total_points >= 10:

        pygame.display.flip()
        pantalla.fill((0, 0, 0))
        gameover_text = pygame.font.SysFont("Arial", 100).render(
            str("GAMEOVER"), 2, (255, 255, 255)
        )
        gameover_text_rect = gameover_text.get_rect(
            center=(pantalla_x // 2, pantalla_y // 2)
        )

        press_any_key = pygame.font.SysFont("Arial", 25).render(
            str("Presione cualquier tecla para ir al siguiente partido"),
            2,
            (255, 255, 255),
        )
        press_any_key_rect = press_any_key.get_rect(
            center=(pantalla_x // 2, pantalla_y // 2 + 250)
        )

        pantalla.blit(gameover_text, gameover_text_rect)
        pantalla.blit(press_any_key, press_any_key_rect)

        for evento in pygame.event.get():
            print(evento)
            if evento.type == pygame.WINDOWCLOSE:
                game_over = True
            if evento.type == pygame.KEYDOWN:
                number_of_game += 1
                game_over = False
                if number_of_game % 3 == 0:
                    mov_pelota_x = 3 + (number_of_game - 1)
                    mov_pelota_y = 3 + (number_of_game - 1)
                score_player_one = 0
                score_player_two = 0
                total_points = 0
                jugador1_x = 50
                jugador1_y = (pantalla_y // 2) - (alto_jugador // 2)
                jugador2_x = (pantalla_x - 50) - ancho_jugador
                jugador2_y = (pantalla_y // 2) - (alto_jugador // 2)
            pygame.display.flip()
        pygame.display.flip()
