import pygame
from settings import *

_font = None


def get_font():
    # se crea la primera vez que se necesita (ya con pygame iniciado)
    global _font
    if _font is None:
        _font = pygame.font.SysFont("consolas", 18, bold=True)
    return _font


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, target, kind="bug"):
        super().__init__()
        cfg = ENEMY_TYPES[kind]
        self.kind = kind
        self.hp = cfg["hp"]
        self.speed = cfg["speed"]
        self.damage = cfg["damage"]

        size = cfg["size"]
        self.base_image = pygame.Surface((size, size))
        self.base_image.fill(cfg["color"])
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.target = target
        self.deadline_timer = DEADLINE_TIME if kind == "deadline" else None

    def take_damage(self, amount):
        """Regresa True si el enemigo murió."""
        self.hp -= amount
        return self.hp <= 0

    def update(self, dt):
        direction = self.target.pos - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * dt
        self.rect.center = self.pos

        if self.deadline_timer is not None:
            self.deadline_timer -= dt
            if self.deadline_timer <= 0:
                # se venció la entrega: golpe directo, ignora la invulnerabilidad
                self.target.take_damage(DEADLINE_PENALTY, force=True)
                self.kill()
                return
            # dibuja la cuenta regresiva encima del cuadro
            self.image = self.base_image.copy()
            text = get_font().render(str(int(self.deadline_timer) + 1), True, (255, 255, 255))
            self.image.blit(text, text.get_rect(center=self.image.get_rect().center))