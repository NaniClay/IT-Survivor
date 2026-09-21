import pygame
from settings import *


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 24)
        self.big_font = pygame.font.SysFont("consolas", 64, bold=True)

    @staticmethod
    def format_time(seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def draw_centered(self, screen, text, font, y, color=(255, 255, 255)):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))

    def draw_hud(self, screen, player, elapsed, bugs_fixed):
        bar_w, bar_h = 200, 20
        ratio = max(0, player.hp) / PLAYER_MAX_HP
        pygame.draw.rect(screen, (60, 60, 60), (20, 20, bar_w, bar_h))
        pygame.draw.rect(screen, (220, 60, 60), (20, 20, bar_w * ratio, bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, bar_w, bar_h), 2)
        timer = self.font.render(f"Tiempo: {self.format_time(elapsed)}", True, (255, 255, 255))
        screen.blit(timer, (20, 50))
        bugs = self.font.render(f"Bugs resueltos: {bugs_fixed}", True, (255, 255, 255))
        screen.blit(bugs, (20, 80))
    def draw_coffee(self, screen, coffee):
        x, y, w, h = 20, 116, 200, 14
        if coffee.active:
            ratio = coffee.active_timer / COFFEE_DURATION
            color, label = (230, 160, 60), "COFFEE BOOST!"
        elif coffee.ready:
            ratio = 1
            color, label = (80, 200, 120), "Coffee listo [ESPACIO]"
        else:
            ratio = 1 - coffee.cooldown_timer / COFFEE_COOLDOWN
            color, label = (120, 100, 80), "Coffee cargando..."
        pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, w * ratio, h))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
        text = self.font.render(label, True, (255, 255, 255))
        screen.blit(text, (x, y + 20))

    def draw_game_over(self, screen, elapsed, bugs_fixed):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        self.draw_centered(screen, "SYSTEM CRASH", self.big_font, HEIGHT // 2 - 80, (220, 60, 60))
        self.draw_centered(screen, f"Sobreviviste: {self.format_time(elapsed)}", self.font, HEIGHT // 2)
        self.draw_centered(screen, f"Bugs resueltos: {bugs_fixed}", self.font, HEIGHT // 2 + 40)
        self.draw_centered(screen, "R = reintentar    ESC = salir", self.font, HEIGHT // 2 + 90)