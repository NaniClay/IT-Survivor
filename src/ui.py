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
        
    def draw_rollback(self, screen, rollback):
        # círculo en el punto al que regresarías
        if rollback.ready:
            pygame.draw.circle(screen, (120, 200, 255), rollback.target_pos, 18, 2)

        x, y, w, h = 20, 176, 200, 14
        if rollback.ready:
            ratio = 1
            color, label = (120, 200, 255), "Rollback listo [G]"
        else:
            ratio = 1 - rollback.cooldown_timer / ROLLBACK_COOLDOWN
            color, label = (70, 100, 130), "Rollback cargando..."
        pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, w * ratio, h))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
        text = self.font.render(label, True, (255, 255, 255))
        screen.blit(text, (x, y + 20))       
        
    def draw_refactor(self, screen, refactor):
        # anillo que crece desde donde activaste la habilidad
        if refactor.wave_timer > 0:
            progress = 1 - refactor.wave_timer / REFACTOR_WAVE_TIME
            radius = max(1, int(REFACTOR_RADIUS * progress))
            pygame.draw.circle(screen, (180, 255, 200), refactor.wave_pos, radius, 4)

        x, y, w, h = 20, 236, 200, 14
        if refactor.ready:
            ratio = 1
            color, label = (180, 255, 200), "Refactorizar listo [E]"
        else:
            ratio = 1 - refactor.cooldown_timer / REFACTOR_COOLDOWN
            color, label = (90, 130, 100), "Refactorizar cargando..."
        pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, w * ratio, h))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
        text = self.font.render(label, True, (255, 255, 255))
        screen.blit(text, (x, y + 20))
        

    def draw_game_over(self, screen, elapsed, bugs_fixed, score,
                       entering_name, name, entries):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        self.draw_centered(screen, "SYSTEM CRASH", self.big_font, 130, (220, 60, 60))
        self.draw_centered(
            screen,
            f"Tiempo {self.format_time(elapsed)}   Bugs {bugs_fixed}   Puntos {score}",
            self.font, 200,
        )

        if entering_name:
            self.draw_centered(screen, "TOP 5! Escribe tu nombre:", self.font, 290, (255, 220, 80))
            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
            self.draw_centered(screen, name + cursor, self.big_font, 350)
            self.draw_centered(screen, "ENTER = guardar    ESC = omitir", self.font, 430)
        else:
            self.draw_centered(screen, "MEJORES PUNTAJES", self.font, 280, (255, 220, 80))
            if not entries:
                self.draw_centered(screen, "(sin registros todavia)", self.font, 330)
            for i, e in enumerate(entries):
                line = (
                    f"{i + 1}. {e['name']:<{NAME_MAX_LEN}} {e['score']:>5} pts  "
                    f"{self.format_time(e['time'])}  {e['bugs']:>3} bugs"
                )
                self.draw_centered(screen, line, self.font, 325 + i * 34)
            self.draw_centered(screen, "R = reintentar    ESC = salir", self.font, 560)