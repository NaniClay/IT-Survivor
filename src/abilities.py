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