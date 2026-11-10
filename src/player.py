import pygame
from settings import *
from src.assets import load_sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.base_color = (80, 200, 120)

        # tres versiones del sprite: normal, golpeado (silueta blanca) y con café (tinte ámbar)
        self.sprite_normal = load_sprite("player", PLAYER_SIZE, self.base_color)
        self.sprite_hit = pygame.mask.from_surface(self.sprite_normal).to_surface(
            setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)
        )
        self.sprite_boost = self.sprite_normal.copy()
        self.sprite_boost.fill((255, 190, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)

        self.image = self.sprite_normal
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.hp = PLAYER_MAX_HP
        self.invuln_timer = 0
        self.speed_mult = 1
        self.boosted = False
        self.damage_taken_mult = 1.0   # lo baja la mejora "Code review"

    def take_damage(self, amount, force=False):
        """Regresa True si el golpe sí conectó."""
        if self.invuln_timer > 0 and not force:
            return False
        self.hp -= amount * self.damage_taken_mult
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

        self.pos += direction * PLAYER_SPEED * self.speed_mult * dt
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))
        self.rect.center = self.pos

        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            self.image = self.sprite_hit
        elif self.boosted:
            self.image = self.sprite_boost
        else:
            self.image = self.sprite_normal
