import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.base_color = (80, 200, 120)
        self.image.fill(self.base_color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.hp = PLAYER_MAX_HP
        self.invuln_timer = 0

    def take_damage(self, amount, force=False):
        """Regresa True si el golpe sí conectó."""
        if self.invuln_timer > 0 and not force:
            return False
        self.hp -= amount
        self.invuln_timer = INVULN_TIME
        return True

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

        # parpadea en blanco mientras es invulnerable
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            self.image.fill((255, 255, 255))
        else:
            self.image.fill(self.base_color)