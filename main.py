import pygame
from settings import *
from src.player import Player
from src.spawner import Spawner
from src.weapons import AutoShooter
from src.abilities import CoffeeBoost, GitRollback, Refactor
from src.learning import Learning
from src.upgrades import Perks, UPGRADES_BY_ID, roll_choices
from src.audio import audio
from src import assets, leaderboard
from src.ui import UI, GREEN, YELLOW, TUTORIAL_PAGES

# teclas numéricas (fila superior y teclado numérico) -> índice de la opción
NUM_KEYS = {
    pygame.K_1: 0, pygame.K_KP1: 0, pygame.K_2: 1, pygame.K_KP2: 1,
    pygame.K_3: 2, pygame.K_KP3: 2, pygame.K_4: 3, pygame.K_KP4: 3,
}
ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)


class Game:
    """Estados: menu, tutorial, scores, playing, paused, quiz, quiz_result, upgrade, game_over."""

    def __init__(self, screen, ui, learning):
        self.screen = screen
        self.ui = ui
        self.learning = learning
        self.background = assets.load_background(WIDTH, HEIGHT, BG_COLOR)
        self.reset("menu")

    def reset(self, state="playing"):
        self.player = Player((WIDTH // 2, HEIGHT // 2))
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.learning.reset_run()
        self.perks = Perks()
        self.spawner = Spawner(self.player, self.enemies, self.all_sprites, bias=self.learning.bias)
        self.shooter = AutoShooter(self.player, self.enemies, self.bullets, self.all_sprites)
        self.coffee = CoffeeBoost()
        self.rollback = GitRollback()
        self.refactor = Refactor()

        self.state = state
        self.elapsed = 0
        self.bugs_fixed = 0
        self.next_quiz = QUIZ_FIRST
        self.next_upgrade = UPGRADE_FIRST
        self.pending = []            # eventos en cola: "upgrade" o "quiz"
        self.quiz_timer = 0
        self.quiz_feedback = None
        self.upgrade_choices = []
        self.banner = None           # [ficha de la Bugpedia, segundos restantes]
        self.toast = None            # [texto, color, segundos restantes]

        self.score = 0
        self.entering_name = False
        self.name_text = ""
        self.entries = []
        self.page = 0
        self.tut_page = 0

    # -------------------------------------------------------------- entradas
    def handle_key(self, event):
        """Regresa False si hay que cerrar el juego."""
        key = event.key
        state = self.state

        # escribiendo el nombre para el leaderboard
        if state == "game_over" and self.entering_name:
            if key in ENTER_KEYS:
                self.entries = leaderboard.add_entry(
                    self.name_text.strip(), self.score, self.elapsed, self.bugs_fixed)
                self.entering_name = False
            elif key == pygame.K_ESCAPE:
                self.entries = leaderboard.load()
                self.entering_name = False
            elif key == pygame.K_BACKSPACE:
                self.name_text = self.name_text[:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.name_text) < NAME_MAX_LEN:
                self.name_text += event.unicode
            return True

        if key == pygame.K_m:
            audio.toggle_mute()
            return True

        if state == "menu":
            if key in ENTER_KEYS:
                audio.play("select")
                self.reset("playing")
            elif key == pygame.K_t:
                audio.play("menu_move")
                self.tut_page = 0
                self.state = "tutorial"
            elif key == pygame.K_l:
                audio.play("menu_move")
                self.entries = leaderboard.load()
                self.state = "scores"
            elif key == pygame.K_ESCAPE:
                return False

        elif state == "tutorial":
            audio.play("menu_move") if key in ENTER_KEYS + (pygame.K_RIGHT, pygame.K_LEFT) else None
            if key in ENTER_KEYS or key == pygame.K_RIGHT:
                if self.tut_page >= TUTORIAL_PAGES - 1:
                    self.state = "menu"
                else:
                    self.tut_page += 1
            elif key == pygame.K_LEFT:
                self.tut_page = max(0, self.tut_page - 1)
            elif key == pygame.K_ESCAPE:
                self.state = "menu"

        elif state == "scores":
            if key in ENTER_KEYS or key == pygame.K_ESCAPE:
                self.state = "menu"

        elif state == "playing":
            if key == pygame.K_ESCAPE:
                self.state = "paused"
            elif key == pygame.K_SPACE:
                if self.coffee.activate():
                    audio.play("coffee")
            elif key == pygame.K_g:
                if self.rollback.activate(self.player):
                    audio.play("rollback")
            elif key == pygame.K_e:
                was_ready = self.refactor.ready
                self.bugs_fixed += self.refactor.activate(self.player, self.enemies)
                if was_ready:
                    audio.play("refactor")

        elif state == "paused":
            if key in (pygame.K_ESCAPE,) + ENTER_KEYS:
                self.state = "playing"
            elif key == pygame.K_r:
                self.reset("playing")
            elif key == pygame.K_q:
                return False

        elif state == "quiz":
            index = NUM_KEYS.get(key)
            if index is not None and index < len(self.learning.current["options"]):
                self.finish_quiz(index)

        elif state == "quiz_result":
            if key in ENTER_KEYS:
                self.state = "playing"

        elif state == "upgrade":
            index = NUM_KEYS.get(key)
            if index is not None and index < len(self.upgrade_choices):
                self.choose_upgrade(index)

        elif state == "game_over":
            if key == pygame.K_TAB:
                self.page += 1
            elif key == pygame.K_r:
                self.reset("playing")
            elif key == pygame.K_ESCAPE:
                self.state = "menu"

        return True

    # ----------------------------------------------------------- actualizar
    def update(self, dt):
        if self.state == "quiz":
            self.quiz_timer -= dt
            if self.quiz_timer <= 0:
                self.finish_quiz(None)
            return
        if self.state != "playing":
            return

        self.elapsed += dt

        # los avisos solo avanzan mientras se juega: no se pierden durante un reto o una mejora
        if self.banner:
            self.banner[1] -= dt
            if self.banner[1] <= 0:
                self.banner = None
        if self.toast:
            self.toast[2] -= dt
            if self.toast[2] <= 0:
                self.toast = None

        # eventos de aprendizaje: se ponen en cola y salen de uno en uno
        if self.elapsed >= self.next_upgrade:
            self.pending.append("upgrade")
            self.next_upgrade += UPGRADE_INTERVAL
        if self.elapsed >= self.next_quiz:
            self.pending.append("quiz")
            self.next_quiz += QUIZ_INTERVAL
        if self.pending:
            self.start_event(self.pending.pop(0))
            return

        player = self.player
        self.apply_perks()
        self.coffee.update(dt)
        self.refactor.update(dt)
        coffee_fire = COFFEE_FIRE_MULT if self.coffee.active else 1
        self.shooter.fire_mult = coffee_fire * self.perks.fire_mult
        player.speed_mult = COFFEE_SPEED_MULT if self.coffee.active else 1
        player.boosted = self.coffee.active

        spawned = self.spawner.update(dt)
        if spawned is not None:
            entry = self.learning.see_enemy(spawned.kind)
            if entry:
                self.banner = [entry, 7.0]
                audio.play("bugpedia")

        self.shooter.update(dt)
        self.all_sprites.update(dt)
        self.rollback.update(dt, player)

        # balas vs enemigos: cada bala puede atravesar varios enemigos
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, False, False)
        for bullet, hit_enemies in hits.items():
            for enemy in hit_enemies:
                if not enemy.alive() or enemy in bullet.already_hit:
                    continue
                bullet.already_hit.add(enemy)
                if enemy.take_damage(BULLET_DAMAGE):
                    enemy.kill()
                    self.bugs_fixed += 1
                    audio.play("kill")
                else:
                    audio.play("hit")
                bullet.pierce_left -= 1
                if bullet.pierce_left <= 0:
                    bullet.kill()
                    break

        # enemigos vs jugador
        for enemy in pygame.sprite.spritecollide(player, self.enemies, False):
            if player.take_damage(enemy.damage):
                enemy.kill()
                audio.play("hurt")

        if player.hp <= 0:
            self.handle_death()

    def apply_perks(self):
        """Pasa los efectos de las mejoras a cada pieza del juego."""
        perks = self.perks
        self.shooter.extra_bullets = perks.extra_bullets
        self.shooter.pierce = BULLET_PIERCE + perks.pierce_bonus
        self.coffee.set_cooldown_mult(perks.coffee_cd_mult)
        self.coffee.duration_bonus = perks.coffee_duration_bonus
        self.rollback.set_cooldown_mult(perks.rollback_cd_mult)
        self.refactor.set_cooldown_mult(perks.refactor_cd_mult)
        self.refactor.radius_mult = perks.refactor_radius_mult
        self.spawner.deadline_time_mult = perks.deadline_time_mult

    def start_event(self, kind):
        if kind == "upgrade":
            self.upgrade_choices = roll_choices()
            self.state = "upgrade"
            audio.play("upgrade_open")
        else:
            if self.learning.pick() is None:   # sin banco de preguntas: no pasa nada
                return
            self.quiz_timer = QUIZ_TIME
            self.state = "quiz"
            audio.play("quiz_open")

    def choose_upgrade(self, index):
        chosen = self.upgrade_choices[index]
        self.perks.apply(chosen["id"])
        if chosen["id"] == "review":
            self.player.max_hp += REVIEW_HP
            self.player.heal(REVIEW_HP)
        audio.play("upgrade_pick")
        self.show_toast(f"MEJORA: {chosen['name']}", YELLOW)
        self.state = "playing"

    def finish_quiz(self, choice):
        ok = self.learning.answer(choice)
        c = self.learning.current
        reward, review = "", ""
        if ok:
            self.player.heal(QUIZ_HEAL)
            reward = f"+{QUIZ_HEAL} de vida"
            # además, se reinicia la habilidad que más tardaba en recargar
            abilities = [self.coffee, self.rollback, self.refactor]
            slowest = max(abilities, key=lambda a: a.cooldown_timer)
            if slowest.cooldown_timer > 0:
                slowest.cooldown_timer = 0
                reward += " y se reinició una habilidad"
            audio.play("correct")
        else:
            kind = TOPIC_ENEMY.get(c["topic"])
            name = self.learning.bugpedia.get(kind, {}).get("name", kind)
            review = f"Repaso: aparecerán más enemigos de tipo {name}."
            audio.play("wrong")
        self.quiz_feedback = {"ok": ok, "timeout": choice is None, "reward": reward, "review": review}
        self.state = "quiz_result"

    def handle_death(self):
        if self.perks.revives > 0:
            self.perks.revives -= 1
            player = self.player
            player.hp = player.max_hp * REVIVE_HP_RATIO
            player.invuln_timer = REVIVE_INVULN
            for enemy in list(self.enemies):
                if enemy.pos.distance_to(player.pos) <= REVIVE_CLEAR_RADIUS:
                    enemy.kill()
            self.show_toast("BACKUP RESTAURADO", GREEN)
            audio.play("revive")
            return
        self.state = "game_over"
        audio.play("gameover")
        self.score = (leaderboard.calc_score(self.elapsed, self.bugs_fixed)
                      + self.learning.total_correct() * QUIZ_POINTS)
        self.learning.save(self.score, self.elapsed, self.bugs_fixed, self.perks.taken)
        if leaderboard.qualifies(self.score):
            self.entering_name = True
            self.name_text = ""
        else:
            self.entries = leaderboard.load()

    def show_toast(self, text, color):
        self.toast = [text, color, 2.5]

    # --------------------------------------------------------------- dibujar
    def perk_items(self):
        return [(UPGRADES_BY_ID[uid]["name"], n) for uid, n in self.perks.taken.items()]

    def stats_text(self):
        rate = self.shooter.fire_mult / FIRE_RATE
        return (f"Balas {1 + self.perks.extra_bullets}  ·  "
                f"Perfora {BULLET_PIERCE + self.perks.pierce_bonus}  ·  "
                f"Cadencia {rate:.1f}/s")

    def draw(self):
        screen, ui = self.screen, self.ui
        screen.blit(self.background, (0, 0))

        if self.state == "menu":
            ui.draw_menu(screen)
            return
        if self.state == "tutorial":
            ui.draw_menu(screen)
            ui.draw_tutorial(screen, self.tut_page)
            return
        if self.state == "scores":
            ui.draw_menu(screen)
            ui.draw_scores(screen, self.entries)
            return

        self.all_sprites.draw(screen)
        ui.draw_hud(screen, self.player, self.elapsed, self.bugs_fixed)
        ui.draw_stats(screen, self.stats_text())
        ui.draw_coffee(screen, self.coffee)
        ui.draw_rollback(screen, self.rollback)
        ui.draw_refactor(screen, self.refactor)
        ui.draw_perks(screen, self.perk_items(), self.perks.revives)
        if self.state == "playing":
            if self.banner:
                ui.draw_banner(screen, self.banner[0])
            if self.toast:
                ui.draw_toast(screen, self.toast[0], self.toast[1])

        if self.state == "paused":
            ui.draw_pause(screen)
        elif self.state == "quiz":
            ui.draw_quiz(screen, self.learning.current, self.quiz_timer)
        elif self.state == "quiz_result":
            ui.draw_quiz_result(screen, self.learning.current, self.quiz_feedback)
        elif self.state == "upgrade":
            ui.draw_upgrade(screen, self.upgrade_choices)
        elif self.state == "game_over":
            ui.draw_game_over(screen, self.elapsed, self.bugs_fixed, self.score,
                              self.entering_name, self.name_text, self.entries,
                              self.page, self.learning, self.perk_items())


def make_window(fullscreen):
    """Ventana redimensionable, o pantalla completa con la resolución del escritorio."""
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)


def present(canvas):
    """Escala el lienzo de 1280x720 al tamaño de la ventana, sin deformarlo (barras negras si hace falta)."""
    window = pygame.display.get_surface()
    ww, wh = window.get_size()
    scale = min(ww / WIDTH, wh / HEIGHT)
    size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))

    if size == (WIDTH, HEIGHT):
        frame = canvas
    elif scale == int(scale):
        frame = pygame.transform.scale(canvas, size)         # escala entera: píxeles nítidos
    else:
        frame = pygame.transform.smoothscale(canvas, size)   # escala fraccionaria: suave

    window.fill((0, 0, 0))
    window.blit(frame, frame.get_rect(center=window.get_rect().center))


def main():
    pygame.init()
    audio.init()
    audio.music()
    fullscreen = False
    make_window(fullscreen)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # el juego se dibuja siempre en un lienzo de 1280x720; present() lo ajusta a la ventana
    canvas = pygame.Surface((WIDTH, HEIGHT))
    game = Game(canvas, UI(), Learning())

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    make_window(fullscreen)
                elif not game.handle_key(event):
                    running = False

        game.update(dt)
        game.draw()
        present(canvas)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
