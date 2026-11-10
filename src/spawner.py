import random
from settings import *
from src.enemy import Enemy


class Spawner:
    def __init__(self, target, enemies, all_sprites, bias=None):
        self.target = target
        self.enemies = enemies
        self.all_sprites = all_sprites
        self.timer = 0
        self.elapsed = 0
        self.interval = SPAWN_INTERVAL
        # bias(kind) -> multiplicador de frecuencia (dificultad adaptativa)
        self.bias = bias or (lambda kind: 1.0)
        # lo sube la mejora "Planificación en sprints"
        self.deadline_time_mult = 1.0

    def random_edge_pos(self):
        margin = 40
        side = random.choice(("top", "bottom", "left", "right"))
        if side == "top":
            return (random.randint(0, WIDTH), -margin)
        if side == "bottom":
            return (random.randint(0, WIDTH), HEIGHT + margin)
        if side == "left":
            return (-margin, random.randint(0, HEIGHT))
        return (WIDTH + margin, random.randint(0, HEIGHT))

    def pick_kind(self):
        # solo los tipos ya desbloqueados, con probabilidad según su peso y el repaso del jugador
        available = [
            (kind, cfg["weight"] * self.bias(kind))
            for kind, cfg in ENEMY_TYPES.items()
            if self.elapsed >= cfg["unlock"]
        ]
        kinds, weights = zip(*available)
        return random.choices(kinds, weights=weights)[0]

    def update(self, dt):
        """Regresa el enemigo que acaba de aparecer, o None."""
        self.elapsed += dt
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            enemy = Enemy(
                self.random_edge_pos(),
                self.target,
                self.pick_kind(),
                deadline_time=DEADLINE_TIME * self.deadline_time_mult,
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.interval = max(SPAWN_MIN_INTERVAL, self.interval * 0.97)
            return enemy
        return None
