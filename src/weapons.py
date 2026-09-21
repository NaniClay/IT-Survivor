import pygame
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill((255, 220, 80))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.life = BULLET_LIFETIME

    def update(self, dt):
        self.pos += self.direction * BULLET_SPEED * dt
        self.rect.center = self.pos
        self.life -= dt
        if self.life <= 0:
            self.kill()


class AutoShooter:
    def __init__(self, player, enemies, bullets, all_sprites):
        self.player = player
        self.enemies = enemies
        self.bullets = bullets
        self.all_sprites = all_sprites
        self.timer = 0

    def nearest_enemy(self):
        # solo apunta a enemigos que ya están dentro de la pantalla
        visible = [
            e for e in self.enemies
            if 0 <= e.pos.x <= WIDTH and 0 <= e.pos.y <= HEIGHT
        ]
        if not visible:
            return None
        return min(visible, key=lambda e: e.pos.distance_squared_to(self.player.pos))

    def update(self, dt):
        self.timer += dt
        if self.timer < FIRE_RATE:
            return
        target = self.nearest_enemy()
        if target is None:
            return

        direction = target.pos - self.player.pos
        if direction.length_squared() == 0:
            return

        self.timer = 0
        bullet = Bullet(self.player.pos, direction.normalize())
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)