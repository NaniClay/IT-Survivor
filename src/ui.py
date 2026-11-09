import pygame
from settings import *

PANEL = (28, 34, 54)
BORDER = (110, 130, 190)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 80)
GREEN = (80, 200, 120)
RED = (220, 60, 60)
GREY = (170, 175, 190)


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 24)
        self.small = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 64, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 30, bold=True)

    # ------------------------------------------------------------ utilidades
    @staticmethod
    def format_time(seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def draw_centered(self, screen, text, font, y, color=WHITE):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))

    def wrap(self, text, font, max_width):
        """Parte un texto largo en líneas que quepan en max_width."""
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def draw_block(self, screen, text, font, x, y, max_width, color=WHITE, line_h=28):
        """Dibuja texto con salto de línea automático. Regresa la y donde termina."""
        for line in self.wrap(text, font, max_width):
            screen.blit(font.render(line, True, color), (x, y))
            y += line_h
        return y

    def dim(self, screen, alpha=200):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def panel(self, screen, rect, border=BORDER):
        pygame.draw.rect(screen, PANEL, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 3, border_radius=10)

    # ------------------------------------------------------------------ HUD
    def draw_hud(self, screen, player, elapsed, bugs_fixed):
        bar_w, bar_h = 200, 20
        ratio = max(0, player.hp) / PLAYER_MAX_HP
        pygame.draw.rect(screen, (60, 60, 60), (20, 20, bar_w, bar_h))
        pygame.draw.rect(screen, (220, 60, 60), (20, 20, bar_w * ratio, bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, bar_w, bar_h), 2)
        timer = self.font.render(f"Tiempo: {self.format_time(elapsed)}", True, WHITE)
        screen.blit(timer, (20, 50))
        bugs = self.font.render(f"Bugs resueltos: {bugs_fixed}", True, WHITE)
        screen.blit(bugs, (20, 80))
        hint = self.small.render("F11 = pantalla completa", True, (110, 115, 135))
        screen.blit(hint, (WIDTH - hint.get_width() - 20, 20))

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
        text = self.font.render(label, True, WHITE)
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
            ratio = 1 - rollback.cooldown_timer / rollback.cooldown_total
            ratio = max(0, min(1, ratio))
            color, label = (70, 100, 130), "Rollback cargando..."
        pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, w * ratio, h))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
        text = self.font.render(label, True, WHITE)
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
        text = self.font.render(label, True, WHITE)
        screen.blit(text, (x, y + 20))

    def draw_perks(self, screen, items, revives):
        """Mejoras activas, debajo de las barras de habilidad."""
        if not items:
            return
        y = 296
        screen.blit(self.small.render("Mejoras:", True, YELLOW), (20, y))
        y += 22
        for name, count in items:
            label = name if count == 1 else f"{name} x{count}"
            screen.blit(self.small.render(label, True, WHITE), (20, y))
            y += 20
        if revives > 0:
            screen.blit(self.small.render(f"Backups listos: {revives}", True, GREEN), (20, y + 4))

    # ------------------------------------------------------- avisos en juego
    def draw_banner(self, screen, entry):
        """Ficha nueva de la Bugpedia (no pausa el juego). La caja se ajusta al texto."""
        width, pad = 900, 20
        inner = width - 2 * pad
        title_lines = self.wrap(f"{entry['name']}  ({entry['real']})", self.font, inner)
        text_lines = self.wrap(entry["que"], self.small, inner)
        height = pad + 22 + len(title_lines) * 28 + 6 + len(text_lines) * 22 + pad
        x = (WIDTH - width) // 2
        y = HEIGHT - 20 - height          # pegada abajo, crece hacia arriba
        rect = pygame.Rect(x, y, width, height)
        self.panel(screen, rect, YELLOW)

        cy = y + pad
        screen.blit(self.small.render("NUEVO EN LA BUGPEDIA", True, YELLOW), (x + pad, cy))
        cy += 22
        for line in title_lines:
            screen.blit(self.font.render(line, True, WHITE), (x + pad, cy))
            cy += 28
        cy += 6
        for line in text_lines:
            screen.blit(self.small.render(line, True, GREY), (x + pad, cy))
            cy += 22
        return rect

    def draw_toast(self, screen, text, color):
        surf = self.title_font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, 60))
        box = rect.inflate(40, 20)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, color, box, 2, border_radius=8)
        screen.blit(surf, rect)

    # ---------------------------------------------------------------- retos
    def draw_quiz(self, screen, q, time_left):
        self.dim(screen)
        self.panel(screen, (120, 50, 1040, 620), YELLOW)
        title = f"STACK OVERFLOW  ·  {q['topic']}"
        screen.blit(self.title_font.render(title, True, YELLOW), (150, 72))

        ratio = max(0, time_left / QUIZ_TIME)
        color = GREEN if time_left > 4 else RED
        pygame.draw.rect(screen, (60, 60, 60), (150, 120, 980, 14))
        pygame.draw.rect(screen, color, (150, 120, 980 * ratio, 14))
        pygame.draw.rect(screen, WHITE, (150, 120, 980, 14), 2)

        y = self.draw_block(screen, q["question"], self.font, 150, 155, 980, WHITE, 32)
        y = max(y + 20, 255)
        for i, option in enumerate(q["options"]):
            rect = pygame.Rect(150, y, 980, 74)
            pygame.draw.rect(screen, (40, 48, 76), rect, border_radius=8)
            pygame.draw.rect(screen, BORDER, rect, 2, border_radius=8)
            self.draw_block(screen, f"{i + 1}. {option}", self.font, 170, y + 10, 940, WHITE, 28)
            y += 86
        self.draw_centered(screen, "Presiona 1, 2, 3 o 4", self.small, 645, GREY)

    def draw_quiz_result(self, screen, c, fb):
        self.dim(screen)
        color = GREEN if fb["ok"] else RED
        self.panel(screen, (120, 60, 1040, 600), color)
        if fb["ok"]:
            title = "¡CORRECTO!"
        elif fb["timeout"]:
            title = "TIEMPO AGOTADO"
        else:
            title = "INCORRECTO"
        screen.blit(self.title_font.render(title, True, color), (150, 85))

        y = self.draw_block(screen, c["question"], self.small, 150, 140, 980, GREY, 24) + 16
        screen.blit(self.font.render("Respuesta correcta:", True, YELLOW), (150, y))
        y += 34
        y = self.draw_block(screen, c["options"][c["correct"]], self.font, 150, y, 980, GREEN, 30) + 16
        screen.blit(self.font.render("Por qué:", True, YELLOW), (150, y))
        y += 34
        y = self.draw_block(screen, c["explanation"], self.font, 150, y, 980, WHITE, 30) + 18
        if fb["reward"]:
            y = self.draw_block(screen, fb["reward"], self.font, 150, y, 980, GREEN, 30)
        if fb["review"]:
            y = self.draw_block(screen, fb["review"], self.font, 150, y, 980, YELLOW, 30)
        self.draw_centered(screen, "ENTER = continuar", self.small, 635, GREY)

    # -------------------------------------------------------------- mejoras
    def draw_upgrade(self, screen, choices):
        self.dim(screen)
        self.draw_centered(screen, "MEJORA: BUENAS PRÁCTICAS", self.title_font, 70, YELLOW)
        self.draw_centered(
            screen, "Elige una. Cada una explica por qué importa en el desarrollo de software.",
            self.small, 108, GREY,
        )
        card_w, card_h, gap = 350, 460, 30
        x0 = (WIDTH - (3 * card_w + 2 * gap)) // 2
        for i, u in enumerate(choices):
            x = x0 + i * (card_w + gap)
            self.panel(screen, (x, 150, card_w, card_h))
            screen.blit(self.title_font.render(f"[{i + 1}]", True, YELLOW), (x + 20, 170))
            y = self.draw_block(screen, u["name"], self.title_font, x + 20, 215, card_w - 40, WHITE, 36) + 10
            y = self.draw_block(screen, u["effect"], self.font, x + 20, y, card_w - 40, GREEN, 28) + 16
            screen.blit(self.small.render("Por qué:", True, YELLOW), (x + 20, y))
            self.draw_block(screen, u["why"], self.small, x + 20, y + 26, card_w - 40, WHITE, 24)
        self.draw_centered(screen, "Presiona 1, 2 o 3", self.font, 650, GREY)

    # ------------------------------------------------------------ game over
    def draw_game_over(self, screen, elapsed, bugs_fixed, score, entering_name,
                       name, entries, page, learning, perk_items):
        self.dim(screen, 215)
        self.draw_centered(screen, "SYSTEM CRASH", self.big_font, 90, RED)
        self.draw_centered(
            screen,
            f"Tiempo {self.format_time(elapsed)}   Bugs {bugs_fixed}   Puntos {score}",
            self.font, 155,
        )

        if entering_name:
            self.draw_centered(screen, "TOP 5! Escribe tu nombre:", self.font, 290, YELLOW)
            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
            self.draw_centered(screen, name + cursor, self.big_font, 350)
            self.draw_centered(screen, "ENTER = guardar    ESC = omitir", self.font, 430)
            return

        total_pages = 2 + len(learning.unlocked)
        page = page % total_pages
        if page == 0:
            self._page_leaderboard(screen, entries)
        elif page == 1:
            self._page_learning(screen, learning, perk_items)
        else:
            self._page_bugpedia(screen, learning, learning.unlocked[page - 2])
        hint = f"TAB = cambiar vista ({page + 1}/{total_pages})    R = reintentar    ESC = salir"
        self.draw_centered(screen, hint, self.small, 685, GREY)

    def _page_leaderboard(self, screen, entries):
        self.draw_centered(screen, "MEJORES PUNTAJES", self.font, 230, YELLOW)
        if not entries:
            self.draw_centered(screen, "(sin registros todavia)", self.font, 290)
        for i, e in enumerate(entries):
            line = (
                f"{i + 1}. {e['name']:<{NAME_MAX_LEN}} {e['score']:>5} pts  "
                f"{self.format_time(e['time'])}  {e['bugs']:>3} bugs"
            )
            self.draw_centered(screen, line, self.font, 285 + i * 36)

    def _page_learning(self, screen, learning, perk_items):
        self.draw_centered(screen, "RESUMEN DE APRENDIZAJE", self.title_font, 230, YELLOW)
        y = 285
        answered_total = 0
        for topic in TOPIC_ENEMY:
            s = learning.stats.get(topic, {"answered": 0, "correct": 0})
            answered_total += s["answered"]
            screen.blit(self.font.render(topic, True, WHITE), (300, y))
            if s["answered"]:
                ratio = s["correct"] / s["answered"]
                pygame.draw.rect(screen, (60, 60, 60), (580, y + 4, 240, 20))
                pygame.draw.rect(screen, GREEN if ratio >= 0.5 else RED, (580, y + 4, 240 * ratio, 20))
                pygame.draw.rect(screen, WHITE, (580, y + 4, 240, 20), 2)
                label = f"{s['correct']}/{s['answered']}"
            else:
                label = "sin preguntas"
            screen.blit(self.font.render(label, True, GREY), (840, y))
            y += 42

        y += 10
        if perk_items:
            texto = ", ".join(n if c == 1 else f"{n} x{c}" for n, c in perk_items)
            y = self.draw_block(screen, f"Buenas prácticas aplicadas: {texto}", self.small, 300, y, 700, WHITE, 24)
        else:
            y += 4
            screen.blit(self.small.render("No elegiste mejoras esta partida.", True, GREY), (300, y))
            y += 24

        weak = [(t, s) for t, s in learning.stats.items() if s["answered"] and s["correct"] < s["answered"]]
        if weak:
            worst = min(weak, key=lambda ts: ts[1]["correct"] / ts[1]["answered"])
            msg, color = f"Para repasar: {worst[0]}", YELLOW
        elif answered_total:
            msg, color = "¡Sin fallos esta partida!", GREEN
        else:
            msg, color = "No te tocó ningún reto esta vez: sobrevive más de 40 s.", GREY
        screen.blit(self.font.render(msg, True, color), (300, y + 14))

    def _page_bugpedia(self, screen, learning, kind):
        e = learning.bugpedia.get(kind)
        if not e:
            self.draw_centered(screen, "BUGPEDIA", self.title_font, 230, YELLOW)
            return
        self.draw_centered(screen, f"BUGPEDIA  ·  {e['name']}", self.title_font, 230, YELLOW)
        self.draw_centered(screen, f"Error real: {e['real']}", self.font, 272, WHITE)
        y = 320
        for label, key in (("Qué es", "que"), ("Por qué pasa", "por_que"), ("Cómo se arregla", "como")):
            screen.blit(self.font.render(label + ":", True, YELLOW), (200, y))
            y = self.draw_block(screen, e[key], self.font, 200, y + 32, 880, WHITE, 28) + 14
