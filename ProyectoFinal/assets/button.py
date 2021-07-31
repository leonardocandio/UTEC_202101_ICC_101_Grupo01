import pygame

# button class
class Button:
    def __init__(self, x, y, image):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width), int(height))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if (
            self.rect.collidepoint(pos)
            and pygame.mouse.get_pressed()[0] == 1
            and self.clicked == False
        ):
            action = True
            self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action