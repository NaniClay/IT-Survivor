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
        self.hp = ENEMY_HP

    def take_damage(self, amount):
        """Regresa True si el enemigo murió."""
        self.hp -= amount
        return self.hp <= 0

    def update(self, dt):
        direction = self.target.pos - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * ENEMY_SPEED * dt
        self.rect.center = self.pos