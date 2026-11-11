import pygame
from settings import *
from src.assets import load_sprite
from src.audio import audio


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, pierce):
        super().__init__()
        self.image = load_sprite("bullet", BULLET_SIZE, (255, 220, 80))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.direction = direction
        self.life = BULLET_LIFETIME
        self.pierce_left = pierce     # a cuántos enemigos más puede pegar
        self.already_hit = set()      # para no pegarle dos veces al mismo enemigo

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
        # los modifican las habilidades y las mejoras
        self.fire_mult = 1
        self.extra_bullets = 0
        self.pierce = BULLET_PIERCE

    def pick_target(self):
        # solo apunta a enemigos que ya están dentro de la pantalla
        visible = [
            e for e in self.enemies
            if 0 <= e.pos.x <= WIDTH and 0 <= e.pos.y <= HEIGHT
        ]
        if not visible:
            return None
        # un deadline a punto de vencer pasa por delante de todos los demás
        urgent = [
            e for e in visible
            if e.deadline_timer is not None and e.deadline_timer < URGENT_DEADLINE
        ]
        pool = urgent or visible
        return min(pool, key=lambda e: e.pos.distance_squared_to(self.player.pos))

    def update(self, dt):
        self.timer += dt
        if self.timer < FIRE_RATE / self.fire_mult:
            return
        target = self.pick_target()
        if target is None:
            return

        direction = target.pos - self.player.pos
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()

        self.timer = 0
        count = 1 + self.extra_bullets
        for i in range(count):
            # las balas salen en abanico, centradas en la dirección del objetivo
            angle = (i - (count - 1) / 2) * BULLET_SPREAD
            bullet = Bullet(self.player.pos, direction.rotate(angle), self.pierce)
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)
        audio.play("shoot")
