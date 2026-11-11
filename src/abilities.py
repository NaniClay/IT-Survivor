from collections import deque
import pygame
from settings import *


class Ability:
    """Base de las habilidades: recarga con multiplicador (lo bajan las mejoras)."""
    base_cooldown = 1.0

    def __init__(self):
        self.cooldown_timer = 0
        self.cooldown_mult = 1.0

    @property
    def cooldown_total(self):
        return self.base_cooldown * self.cooldown_mult

    def set_cooldown_mult(self, mult):
        """Cambia el multiplicador y reescala el tiempo que falta, para que la barra no salte
        si la mejora se elige mientras la habilidad ya está recargando."""
        if mult != self.cooldown_mult:
            if self.cooldown_timer > 0 and self.cooldown_mult > 0:
                self.cooldown_timer *= mult / self.cooldown_mult
            self.cooldown_mult = mult


class CoffeeBoost(Ability):
    base_cooldown = COFFEE_COOLDOWN

    def __init__(self):
        super().__init__()
        self.active_timer = 0
        self.active_total = COFFEE_DURATION
        self.duration_bonus = 0.0      # lo sube "Cafetera industrial"

    @property
    def active(self):
        return self.active_timer > 0

    @property
    def ready(self):
        return self.cooldown_timer <= 0

    def activate(self):
        """Regresa True si se activó."""
        if not self.ready:
            return False
        self.active_total = COFFEE_DURATION + self.duration_bonus
        self.active_timer = self.active_total
        self.cooldown_timer = self.cooldown_total
        return True

    def update(self, dt):
        if self.active_timer > 0:
            self.active_timer -= dt
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt


class GitRollback(Ability):
    base_cooldown = ROLLBACK_COOLDOWN

    def __init__(self):
        super().__init__()
        # historial de "commits": (posición, vida). Al llenarse, borra el más viejo.
        max_snapshots = int(ROLLBACK_SECONDS / ROLLBACK_SAVE_INTERVAL)
        self.history = deque(maxlen=max_snapshots)
        self.save_timer = 0

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
        self.cooldown_timer = self.cooldown_total
        return True


class Refactor(Ability):
    base_cooldown = REFACTOR_COOLDOWN

    def __init__(self):
        super().__init__()
        self.wave_timer = 0
        self.wave_pos = pygame.Vector2()
        self.radius_mult = 1.0          # lo sube "Refactorización continua"
        self.wave_radius = REFACTOR_RADIUS

    @property
    def radius(self):
        return REFACTOR_RADIUS * self.radius_mult

    @property
    def ready(self):
        return self.cooldown_timer <= 0

    def activate(self, player, enemies):
        """Regresa cuántos enemigos murieron."""
        if not self.ready:
            return 0

        self.cooldown_timer = self.cooldown_total
        self.wave_timer = REFACTOR_WAVE_TIME
        self.wave_pos = player.pos.copy()
        self.wave_radius = self.radius

        killed = 0
        for enemy in list(enemies):   # copia de la lista, porque vamos a borrar mientras recorremos
            if enemy.pos.distance_to(player.pos) <= self.wave_radius:
                if enemy.take_damage(REFACTOR_DAMAGE):
                    enemy.kill()
                    killed += 1
        return killed

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        if self.wave_timer > 0:
            self.wave_timer -= dt
