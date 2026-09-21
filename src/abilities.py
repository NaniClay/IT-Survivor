import pygame
from collections import deque
from settings import *


class CoffeeBoost:
    def __init__(self):
        self.active_timer = 0
        self.cooldown_timer = 0

    @property
    def active(self):
        return self.active_timer > 0

    @property
    def ready(self):
        return self.cooldown_timer <= 0

    def activate(self):
        if self.ready:
            self.active_timer = COFFEE_DURATION
            self.cooldown_timer = COFFEE_COOLDOWN

    def update(self, dt):
        if self.active_timer > 0:
            self.active_timer -= dt
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt


class GitRollback:
    def __init__(self):
        # historial de "commits": (posición, vida). Al llenarse, borra el más viejo.
        max_snapshots = int(ROLLBACK_SECONDS / ROLLBACK_SAVE_INTERVAL)
        self.history = deque(maxlen=max_snapshots)
        self.save_timer = 0
        self.cooldown_timer = 0

    @property
    def ready(self):
        return self.cooldown_timer <= 0 and len(self.history) > 0

    @property
    def target_pos(self):
        """Posición a la que regresarías (None si no hay historial)."""
        return self.history[0][0] if self.history else None

    def update(self, dt, player):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

        self.save_timer += dt
        if self.save_timer >= ROLLBACK_SAVE_INTERVAL:
            self.save_timer = 0
            self.history.append((player.pos.copy(), player.hp))

    def activate(self, player):
        if not self.ready:
            return False
        pos, hp = self.history[0]          # el commit más viejo = hace ~5 s
        player.pos = pos.copy()
        player.rect.center = player.pos
        player.hp = max(player.hp, hp)     # nunca te quita vida
        player.invuln_timer = ROLLBACK_INVULN
        self.history.clear()
        self.cooldown_timer = ROLLBACK_COOLDOWN
        return True

class Refactor:
    def __init__(self):
        self.cooldown_timer = 0
        self.wave_timer = 0
        self.wave_pos = pygame.Vector2()

    @property
    def ready(self):
        return self.cooldown_timer <= 0

    def activate(self, player, enemies):
        """Regresa cuántos enemigos murieron."""
        if not self.ready:
            return 0

        self.cooldown_timer = REFACTOR_COOLDOWN
        self.wave_timer = REFACTOR_WAVE_TIME
        self.wave_pos = player.pos.copy()

        killed = 0
        for enemy in list(enemies):   # copia de la lista, porque vamos a borrar mientras recorremos
            if enemy.pos.distance_to(player.pos) <= REFACTOR_RADIUS:
                if enemy.take_damage(REFACTOR_DAMAGE):
                    enemy.kill()
                    killed += 1
        return killed

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        if self.wave_timer > 0:
            self.wave_timer -= dt