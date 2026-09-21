import random
from settings import *
from src.enemy import Enemy


class Spawner:
    def __init__(self, target, enemies, all_sprites):
        self.target = target
        self.enemies = enemies
        self.all_sprites = all_sprites
        self.timer = 0
        self.interval = SPAWN_INTERVAL

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

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            enemy = Enemy(self.random_edge_pos(), self.target)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            # cada spawn acelera un poquito el siguiente
            self.interval = max(SPAWN_MIN_INTERVAL, self.interval * 0.97)