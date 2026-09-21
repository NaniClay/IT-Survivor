import pygame
from settings import *


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, target):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill((220, 60, 60))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.target = target

    def update(self, dt):
        direction = self.target.pos - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * ENEMY_SPEED * dt
        self.rect.center = self.pos