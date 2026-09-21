import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((80, 200, 120))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w],
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * PLAYER_SPEED * dt
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))
        self.rect.center = self.pos