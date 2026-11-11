"""Pruebas de funcionalidad de IT Survivor.

Uso (desde la raíz del repo, con el entorno virtual activo):
    python tests/run_tests.py          pruebas en modo escritorio
    python tests/run_tests.py --web    las mismas pruebas simulando el modo navegador (audio OGG, sin salir, etc.)

No abre ventana ni hace ruido. Imprime una tabla y guarda tests/resultados.md,
que se puede usar como evidencia de las pruebas de funcionalidad.
No toca tus archivos de juego: usa una carpeta temporal para el leaderboard y el progreso.
"""
import asyncio
import os
import sys
import tempfile
import time
import traceback

WEB = "--web" in sys.argv
if WEB:
    os.environ["ITS_WEB"] = "1"            # settings.py lo lee para activar IS_WEB
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame

pygame.init()

from settings import *
import src.game as M
import src.learning as learning_module
import src.storage as storage
import src.fonts as fonts
from src import leaderboard
from src.audio import audio
import src.audio as audio_module
from src.enemy import Enemy
from src.learning import Learning
from src.ui import UI
from src.upgrades import UPGRADES
from src.weapons import Bullet

pygame.display.set_mode((WIDTH, HEIGHT))
CANVAS = pygame.Surface((WIDTH, HEIGHT))
TMP = tempfile.mkdtemp(prefix="itsurvivor_tests_")
learning_module.ROOT = TMP                       # el progreso de aprendizaje se guarda aquí, no en tu carpeta
leaderboard.PATH = os.path.join(TMP, "leaderboard.json")
DT = 1 / 60


class Keys:
    """Teclado falso: keys.d[pygame.K_d] = 1 simula tener la tecla presionada."""
    def __init__(self):
        self.d = {}

    def __getitem__(self, key):
        return self.d.get(key, 0)


KEYS = Keys()
pygame.key.get_pressed = lambda: KEYS


class Ev:
    def __init__(self, key, uni=""):
        self.key, self.unicode = key, uni


def new_game(playing=True):
    KEYS.d = {}
    if os.path.exists(leaderboard.PATH):
        os.remove(leaderboard.PATH)
    game = M.Game(CANVAS, UI(), Learning())
    if playing:
        game.handle_key(Ev(pygame.K_RETURN))     # ENTER en el menú
        quiet(game)
    return game


def quiet(game):
    """Evita que aparezcan enemigos, retos o mejoras solos mientras se prueba otra cosa."""
    game.spawner.interval = 10 ** 9
    game.next_quiz = 10 ** 9
    game.next_upgrade = 10 ** 9


def step(game, seconds):
    for _ in range(int(seconds / DT)):
        game.update(DT)


def add_enemy(game, kind, pos, still=True):
    e = Enemy(pos, game.player, kind)
    if still:
        e.speed = 0
    game.enemies.add(e)
    game.all_sprites.add(e)
    return e


# ================================================================== pruebas
def t_movimiento():
    g = new_game()
    start = g.player.pos.copy()
    KEYS.d = {pygame.K_d: 1}
    step(g, 0.5)
    dx = g.player.pos.x - start.x
    assert abs(dx - PLAYER_SPEED * 0.5) < 3, f"a la derecha se movió {dx:.1f}"
    for key, axis, sign in ((pygame.K_a, "x", -1), (pygame.K_s, "y", 1), (pygame.K_w, "y", -1)):
        g.player.pos = start.copy()
        KEYS.d = {key: 1}
        step(g, 0.3)
        delta = getattr(g.player.pos, axis) - getattr(start, axis)
        assert delta * sign > 0, f"la tecla {pygame.key.name(key)} no mueve en la dirección correcta"
    g.player.pos = start.copy()
    KEYS.d = {pygame.K_d: 1, pygame.K_s: 1}
    step(g, 0.5)
    dist = g.player.pos.distance_to(start)
    assert abs(dist - PLAYER_SPEED * 0.5) < 3, f"en diagonal recorrió {dist:.1f} (debe ser igual que en línea recta)"
    KEYS.d = {pygame.K_a: 1}
    step(g, 8)
    assert g.player.pos.x == 0, "el jugador debe quedarse en el borde izquierdo"


def t_disparo_cercano():
    g = new_game()
    add_enemy(g, "bug", (900, 360))
    near = add_enemy(g, "bug", (700, 360))
    g.shooter.timer = 10
    g.shooter.update(DT)
    assert len(g.bullets) == 1, "debió disparar una bala"
    bullet = g.bullets.sprites()[0]
    expected = (near.pos - g.player.pos).normalize()
    assert bullet.direction.distance_to(expected) < 0.01, "debe apuntar al enemigo más cercano"


def t_disparo_ignora_fuera():
    g = new_game()
    add_enemy(g, "bug", (-30, 360))
    g.shooter.timer = 10
    g.shooter.update(DT)
    assert len(g.bullets) == 0, "no debe disparar a enemigos que aún están fuera de la pantalla"


def t_perforacion():
    g = new_game()
    g.player.pos = pygame.Vector2(600, 360)
    enemies = [add_enemy(g, "error500", (x, 360)) for x in (700, 760, 820)]
    for e in enemies:
        e.hp = 100
    bullet = Bullet((650, 360), pygame.Vector2(1, 0), BULLET_PIERCE)
    g.bullets.add(bullet)
    g.all_sprites.add(bullet)
    step(g, 0.6)
    hit = [e.hp < 100 for e in enemies]
    assert hit[:BULLET_PIERCE] == [True] * BULLET_PIERCE, f"debe pegar a los primeros {BULLET_PIERCE}: {hit}"
    assert not any(hit[BULLET_PIERCE:]), "no debe pegar a más enemigos que su perforación"
    assert not bullet.alive(), "la bala debe desaparecer al agotar su perforación"


def t_enemigos_desbloqueo():
    g = new_game()
    g.spawner.elapsed = 0
    kinds = {g.spawner.pick_kind() for _ in range(400)}
    assert kinds == {"bug"}, f"al inicio solo debe salir bug: {kinds}"
    g.spawner.elapsed = max(c["unlock"] for c in ENEMY_TYPES.values()) + 1
    kinds = {g.spawner.pick_kind() for _ in range(3000)}
    assert kinds == set(ENEMY_TYPES), f"deben salir los {len(ENEMY_TYPES)} tipos: {kinds}"
    for kind, cfg in ENEMY_TYPES.items():
        e = Enemy((0, 0), g.player, kind)
        assert e.hp == cfg["hp"] and e.speed == cfg["speed"] and e.damage == cfg["damage"], kind


def t_dano_e_invulnerabilidad():
    g = new_game()
    g.player.hp = 50
    e1 = add_enemy(g, "bug", g.player.pos)
    g.update(DT)
    assert g.player.hp < 50 and abs(50 - g.player.hp - ENEMY_TYPES["bug"]["damage"]) < 1, "debe recibir el daño del bug"
    assert not e1.alive(), "el enemigo desaparece al golpear"
    assert g.player.invuln_timer > 0, "debe quedar invulnerable un momento"
    hp = g.player.hp
    add_enemy(g, "bug", g.player.pos)
    g.update(DT)
    assert g.player.hp >= hp, "durante la invulnerabilidad no debe recibir más daño"


def t_regeneracion():
    g = new_game()
    g.player.hp = 50
    step(g, 2)
    assert abs(g.player.hp - (50 + PLAYER_REGEN * 2)) < 0.5, f"vida {g.player.hp:.2f}"
    g.player.hp = g.player.max_hp
    step(g, 1)
    assert g.player.hp == g.player.max_hp, "la vida no debe pasar del máximo"


def t_coffee():
    g = new_game()
    assert g.coffee.ready
    g.handle_key(Ev(pygame.K_SPACE))
    g.update(DT)
    assert g.coffee.active and g.player.speed_mult == COFFEE_SPEED_MULT
    assert abs(g.shooter.fire_mult - COFFEE_FIRE_MULT) < 1e-6, "la cadencia debe duplicarse"
    step(g, COFFEE_DURATION + 0.2)
    assert not g.coffee.active and g.player.speed_mult == 1, "el efecto termina"
    assert not g.coffee.ready, "debe estar en recarga"
    step(g, COFFEE_COOLDOWN)
    assert g.coffee.ready, "debe volver a estar lista"


def t_rollback():
    g = new_game()
    g.player.pos = pygame.Vector2(300, 360)
    KEYS.d = {pygame.K_d: 1}
    step(g, 3)
    KEYS.d = {}
    now_x = g.player.pos.x
    assert g.rollback.ready
    g.handle_key(Ev(pygame.K_g))
    assert g.player.pos.x < now_x - 100, "debe regresar a una posición anterior"
    assert g.player.invuln_timer > 0
    assert not g.rollback.ready
    step(g, ROLLBACK_COOLDOWN + 1)
    assert g.rollback.ready, "debe recargar"


def t_refactor():
    g = new_game()
    inside = [add_enemy(g, "bug", g.player.pos + pygame.Vector2(100, 0)) for _ in range(3)]
    outside = add_enemy(g, "bug", g.player.pos + pygame.Vector2(REFACTOR_RADIUS + 250, 0))
    g.handle_key(Ev(pygame.K_e))
    assert not any(e.alive() for e in inside), "deben morir los enemigos dentro del radio"
    assert outside.alive(), "no debe tocar a los de fuera"
    assert g.bugs_fixed == 3, "cuenta como bugs resueltos"
    assert not g.refactor.ready


def t_deadline_vence():
    g = new_game()
    g.player.hp = 80
    g.player.invuln_timer = 5
    e = Enemy((50, 50), g.player, "deadline", deadline_time=0.2)
    g.enemies.add(e)
    g.all_sprites.add(e)
    step(g, 0.4)
    assert not e.alive(), "el deadline vencido desaparece"
    assert abs(80 - g.player.hp - DEADLINE_PENALTY) < 1.5, f"debe aplicar {DEADLINE_PENALTY} de daño aun con invulnerabilidad"


def t_deadline_prioridad():
    g = new_game()
    add_enemy(g, "bug", (700, 360))
    urgent = Enemy((1100, 600), g.player, "deadline", deadline_time=URGENT_DEADLINE - 1)
    g.enemies.add(urgent)
    g.all_sprites.add(urgent)
    assert g.shooter.pick_target() is urgent, "un deadline por vencer debe pasar al frente"
    relaxed = Enemy((1100, 600), g.player, "deadline", deadline_time=DEADLINE_TIME)
    urgent.kill()
    g.enemies.add(relaxed)
    assert g.shooter.pick_target() is not relaxed, "con tiempo de sobra no tiene prioridad"


def t_deadline_alcanzable():
    farthest = (WIDTH / 2 + 40)                     # lo más lejos que puede nacer (borde izquierdo o derecho)
    seconds = farthest / ENEMY_TYPES["deadline"]["speed"]
    assert seconds < DEADLINE_TIME - 2, f"tardaría {seconds:.1f} s en llegar con una cuenta de {DEADLINE_TIME} s"


def t_reto_preguntas():
    g = new_game()
    g.next_quiz = QUIZ_FIRST
    g.elapsed = QUIZ_FIRST - 0.01
    g.update(DT)
    g.update(DT)
    assert g.state == "quiz", f"estado: {g.state}"
    q = g.learning.current
    assert len(q["options"]) == 4 and 0 <= q["correct"] < 4
    g.player.hp = 40
    g.handle_key(Ev(pygame.K_1 + q["correct"]))
    assert g.state == "quiz_result" and g.quiz_feedback["ok"]
    assert g.player.hp >= 40 + QUIZ_HEAL - 1, "acertar cura"
    g.handle_key(Ev(pygame.K_RETURN))
    assert g.state == "playing"
    # fallo: sube la frecuencia del enemigo del tema
    g.learning.pick()
    q = g.learning.current
    topic = q["topic"]
    g.state = "quiz"
    g.quiz_timer = QUIZ_TIME
    g.handle_key(Ev(pygame.K_1 + (q["correct"] + 1) % 4))
    assert not g.quiz_feedback["ok"]
    assert g.learning.bias(TOPIC_ENEMY[topic]) > 1, "fallar un tema debe repetir más su enemigo"
    # tiempo agotado
    g.state = "quiz"
    g.learning.pick()
    g.quiz_timer = 0.02
    g.update(0.05)
    assert g.state == "quiz_result" and g.quiz_feedback["timeout"], "sin responder cuenta como fallo"


def t_reto_teclado_numerico():
    g = new_game()
    g.learning.pick()
    g.state = "quiz"
    g.quiz_timer = QUIZ_TIME
    g.handle_key(Ev(pygame.K_KP2))
    assert g.state == "quiz_result", "el teclado numérico también responde"


def t_mejora_aparece():
    g = new_game()
    g.next_upgrade = UPGRADE_FIRST
    g.elapsed = UPGRADE_FIRST - 0.01
    g.update(DT)
    g.update(DT)
    assert g.state == "upgrade"
    ids = [u["id"] for u in g.upgrade_choices]
    assert len(ids) == 3 and len(set(ids)) == 3, "deben ser 3 opciones distintas"
    g.handle_key(Ev(pygame.K_2))
    assert g.state == "playing" and sum(g.perks.taken.values()) == 1


def apply_one(uid):
    g = new_game()
    choice = next(u for u in UPGRADES if u["id"] == uid)
    g.upgrade_choices = [choice] * 3
    g.state = "upgrade"
    g.player.hp = 60
    g.handle_key(Ev(pygame.K_1))
    g.update(DT)
    return g


def t_mejoras_efectos():
    failures = []

    def check(uid, cond, msg):
        if not cond:
            failures.append(f"{uid}: {msg}")

    g = apply_one("tests")
    g.shooter.timer = 10
    add_enemy(g, "bug", (800, 360))
    g.shooter.update(DT)
    check("tests", len(g.bullets) == 2, f"debe disparar 2 balas, disparó {len(g.bullets)}")

    g = apply_one("ci")
    check("ci", abs(g.shooter.fire_mult - 1.3) < 1e-6, "la cadencia debe subir 30%")

    g = apply_one("modular")
    check("modular", g.shooter.pierce == BULLET_PIERCE + 1, "la perforación debe subir 1")

    g = apply_one("review")
    check("review", g.player.max_hp == PLAYER_MAX_HP + REVIEW_HP, "la vida máxima debe subir")
    check("review", g.player.hp > 60 + REVIEW_HP - 2, "debe curar")

    g = apply_one("backups")
    check("backups", g.perks.revives == 1, "debe dar un revive")

    g = apply_one("commits")
    check("commits", abs(g.rollback.cooldown_mult - 0.7) < 1e-6, "el Rollback debe recargar 30% más rápido")

    g = apply_one("refactor")
    check("refactor", abs(g.refactor.cooldown_mult - 0.7) < 1e-6 and abs(g.refactor.radius - REFACTOR_RADIUS * 1.2) < 1e-6,
          "Refactorizar debe recargar más rápido y abarcar 20% más")

    g = apply_one("coffee")
    g.handle_key(Ev(pygame.K_SPACE))
    check("coffee", abs(g.coffee.active_total - (COFFEE_DURATION + 2)) < 1e-6 and abs(g.coffee.cooldown_timer - COFFEE_COOLDOWN * 0.7) < 1e-6,
          "Coffee debe durar 2 s más y recargar 30% más rápido")

    g = apply_one("sprints")
    g.spawner.pick_kind = lambda: "deadline"
    g.spawner.interval = 0.01
    g.spawner.timer = 1
    e = g.spawner.update(DT)
    check("sprints", e is not None and abs(e.deadline_timer - DEADLINE_TIME * 1.5) < 1e-6, "los deadlines deben durar 50% más")

    assert not failures, "; ".join(failures)


def t_backup_revive():
    g = new_game()
    g.perks.apply("backups")
    near = add_enemy(g, "bug", g.player.pos + pygame.Vector2(60, 0))
    g.player.hp = 0
    g.update(DT)
    assert g.state == "playing", "con Backup no debe terminar la partida"
    assert abs(g.player.hp - g.player.max_hp * REVIVE_HP_RATIO) < 1
    assert g.perks.revives == 0 and not near.alive(), "gasta el backup y limpia a los enemigos cercanos"
    g.player.hp = 0
    g.update(DT)
    assert g.state == "game_over", "sin más backups, la partida termina"


def t_game_over_y_leaderboard():
    g = new_game()
    g.elapsed = 42
    g.bugs_fixed = 7
    g.player.hp = 0
    g.update(DT)
    assert g.state == "game_over"
    expected = leaderboard.calc_score(g.elapsed, 7) + g.learning.total_correct() * QUIZ_POINTS
    assert g.score == expected, f"puntaje {g.score} != {expected}"
    assert g.entering_name, "un puntaje en el top debe pedir el nombre"
    for ch in "Ana":
        g.handle_key(Ev(pygame.K_a, ch))
    g.handle_key(Ev(pygame.K_RETURN))
    top = leaderboard.load()
    assert top and top[0]["name"] == "Ana" and top[0]["score"] == expected
    for score in (10, 500, 20, 900, 30, 700):
        leaderboard.add_entry(f"J{score}", score, 1, 1)
    top = leaderboard.load()
    scores = [e["score"] for e in top]
    assert len(top) == LEADERBOARD_SIZE and scores == sorted(scores, reverse=True), f"top: {scores}"


def t_bugpedia():
    kinds = set(ENEMY_TYPES)
    data = Learning().bugpedia
    assert kinds <= set(data), "debe haber una ficha por cada tipo de enemigo"
    for kind in kinds:
        for field in ("name", "real", "que", "por_que", "como"):
            assert data[kind].get(field), f"falta {field} en la ficha de {kind}"
    g = new_game()
    g.spawner.interval = 0.01
    g.spawner.timer = 1
    g.update(DT)
    assert g.banner is not None, "el primer enemigo de cada tipo muestra su aviso"
    g.banner = None
    g.spawner.timer = 1
    g.update(DT)
    assert g.banner is None, "el mismo tipo no repite el aviso en la partida"


def t_resumen_aprendizaje():
    g = new_game()
    answers = [True, True, False]
    for ok in answers:
        q = g.learning.pick()
        g.learning.answer(q["correct"] if ok else (q["correct"] + 1) % 4)
    stats = g.learning.stats
    assert sum(s["answered"] for s in stats.values()) == 3
    assert g.learning.total_correct() == 2
    g.player.hp = 0
    g.update(DT)
    g.page = 1
    g.draw()                                   # la página de resumen se dibuja sin errores
    for i in range(2 + len(g.learning.unlocked)):
        g.page = i
        g.draw()


def t_progreso_guardado():
    g = new_game()
    g.learning.pick()
    g.learning.answer(g.learning.current["correct"])
    g.player.hp = 0
    g.update(DT)
    path = os.path.join(TMP, PROGRESS_FILE)
    assert os.path.exists(path), "debe guardar learning_progress.json"
    reloaded = Learning()
    assert reloaded.games >= 1 and reloaded.runs and "temas" in reloaded.runs[-1]


def t_pantallas():
    g = new_game(playing=False)
    assert g.state == "menu"
    g.draw()
    g.handle_key(Ev(pygame.K_t))
    assert g.state == "tutorial"
    for _ in range(3):
        g.draw()
        g.handle_key(Ev(pygame.K_RETURN))
    assert g.state == "menu", "tras la última página del tutorial vuelve al menú"
    g.handle_key(Ev(pygame.K_l))
    assert g.state == "scores"
    g.draw()
    g.handle_key(Ev(pygame.K_ESCAPE))
    assert g.state == "menu"
    g.handle_key(Ev(pygame.K_RETURN))
    assert g.state == "playing"


def t_pausa():
    g = new_game()
    step(g, 1)
    g.handle_key(Ev(pygame.K_ESCAPE))
    assert g.state == "paused"
    t = g.elapsed
    step(g, 2)
    g.draw()
    assert g.elapsed == t, "en pausa el tiempo no avanza"
    g.handle_key(Ev(pygame.K_ESCAPE))
    assert g.state == "playing"
    g.handle_key(Ev(pygame.K_ESCAPE))
    g.handle_key(Ev(pygame.K_r))
    assert g.state == "playing" and g.elapsed == 0, "R en pausa reinicia"
    g.handle_key(Ev(pygame.K_ESCAPE))
    assert g.handle_key(Ev(pygame.K_q)) is IS_WEB, "Q en pausa cierra el juego (en el navegador no hace nada)"


def t_menu_desde_game_over():
    g = new_game()
    g.player.hp = 0
    g.update(DT)
    g.entering_name = False
    g.handle_key(Ev(pygame.K_TAB))
    g.handle_key(Ev(pygame.K_ESCAPE))
    assert g.state == "menu"


def t_audio():
    audio.init()
    assert audio.ready, "el mezclador de audio debe iniciar"
    needed = ["shoot", "hit", "kill", "hurt", "coffee", "rollback", "refactor", "quiz_open", "correct", "wrong",
              "upgrade_open", "upgrade_pick", "revive", "bugpedia", "deadline_fail", "gameover", "select", "menu_move"]
    missing = [n for n in needed if n not in audio.sounds]
    assert not missing, f"faltan sonidos: {missing}"
    assert os.path.exists(os.path.join(ROOT, "assets", "sounds", "music" + audio_module.EXT)), "falta la música"
    audio.music()
    for name in needed:
        audio.play(name)
    assert audio.toggle_mute() is True and audio.toggle_mute() is False


def t_escalado_ventana():
    g = new_game()
    g.draw()
    ref = pygame.transform.average_color(CANVAS)[:3]
    if IS_WEB:
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        M.present(CANVAS)
        got = pygame.transform.average_color(window)[:3]
        assert max(abs(a - b) for a, b in zip(got, ref)) <= 1, "en el navegador el lienzo se copia tal cual"
        return
    for size in [(1280, 720), (1920, 1080), (2560, 1440), (1000, 800), (640, 360)]:
        window = pygame.display.set_mode(size, pygame.RESIZABLE)
        M.present(CANVAS)
        ww, wh = window.get_size()
        scale = min(ww / WIDTH, wh / HEIGHT)
        area = pygame.Rect(0, 0, int(WIDTH * scale), int(HEIGHT * scale))
        area.center = (ww // 2, wh // 2)
        got = pygame.transform.average_color(window, area)[:3]
        assert max(abs(a - b) for a, b in zip(got, ref)) <= 6, f"{size}: {got} vs {ref}"
    pygame.display.set_mode((WIDTH, HEIGHT))


def t_banco_preguntas():
    bank = Learning().bank
    assert len(bank) >= 20, f"solo hay {len(bank)} preguntas"
    ids = [q["id"] for q in bank]
    assert len(ids) == len(set(ids)), "ids repetidos"
    for topic in TOPIC_ENEMY:
        assert sum(1 for q in bank if q["topic"] == topic) >= 5, f"pocas preguntas de {topic}"
    for q in bank:
        assert len(q["options"]) == 4 and len(set(q["options"])) == 4, q["id"]
        assert 0 <= q["answer"] < 4 and q["explanation"].strip(), q["id"]


def t_sin_archivos_de_datos():
    """Sin banco de preguntas o fichas el juego no debe tronar."""
    real = learning_module.DATA
    learning_module.DATA = os.path.join(TMP, "no_existe")
    try:
        L = Learning()
        assert L.pick() is None and L.bugpedia == {}
        g = M.Game(CANVAS, UI(), L)
        g.handle_key(Ev(pygame.K_RETURN))
        g.elapsed = QUIZ_FIRST + 1
        g.next_upgrade = 10 ** 9
        for _ in range(10):
            g.update(DT)
        g.draw()
    finally:
        learning_module.DATA = real


def t_fuentes():
    for path in (fonts.REGULAR, fonts.BOLD):
        assert os.path.exists(path), f"falta {path}"
    for size, bold in ((18, False), (24, False), (30, True), (64, True), (96, True)):
        font = fonts.get_font(size, bold)
        w, h = font.size("Sobrevive: ¿Qué significa un código 500? ñ á é í ó ú")
        assert w > 100 and h > 5, f"la fuente {size} no dibuja bien"
    # los textos de la interfaz caben en su contenedor con la fuente incluida
    ui = UI()
    assert ui.font.size("Refactorizar listo [E]")[0] < 340
    assert ui.big_font.size("SYSTEM CRASH")[0] < WIDTH - 200
    assert ui.huge_font.size("IT SURVIVOR")[0] < WIDTH - 200


def t_almacenamiento():
    path = os.path.join(TMP, "datos_prueba.json")
    if os.path.exists(path):
        os.remove(path)
    assert storage.read_text(path) is None, "sin datos debe regresar None"
    assert storage.write_text(path, "hola") and storage.read_text(path) == "hola", "ida y vuelta en archivo"

    class FakeLocalStorage:
        def __init__(self):
            self.items = {}

        def getItem(self, key):
            return self.items.get(key)

        def setItem(self, key, value):
            self.items[key] = value

    class BrokenLocalStorage:
        def getItem(self, key):
            raise RuntimeError("sin acceso")

        def setItem(self, key, value):
            raise RuntimeError("sin acceso")

    real = storage._local_storage
    try:
        fake = FakeLocalStorage()
        storage._local_storage = lambda: fake
        assert storage.write_text(path, "desde el navegador")
        assert fake.items.get("itsurvivor:datos_prueba.json") == "desde el navegador", "debe usar localStorage si existe"
        assert storage.read_text(path) == "desde el navegador"
        storage._local_storage = lambda: BrokenLocalStorage()
        assert storage.write_text(path, "respaldo en archivo"), "si localStorage falla usa el archivo"
        assert storage.read_text(path) == "respaldo en archivo"
    finally:
        storage._local_storage = real


def reinit_after_quit(muted_before=False):
    """run_game termina con pygame.quit(): se reinicia lo que quedó invalidado para las pruebas siguientes."""
    import src.enemy as enemy_module
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT))
    fonts._cache.clear()
    enemy_module._font = None
    audio.ready, audio.tried, audio.sounds = False, False, {}
    audio.init()
    audio.muted = muted_before


def run_scripted(script, expect_frames=None):
    """Corre run_game con eventos falsos por número de cuadro. Regresa lo que se observó en cada cuadro."""
    counter = {"n": 0}
    seen = {}
    real_get = pygame.event.get

    def fake_get(*args, **kwargs):
        counter["n"] += 1
        seen[counter["n"]] = (audio.tried, audio.ready)
        return script.get(counter["n"], [])

    pygame.event.get = fake_get
    try:
        asyncio.run(M.run_game())
    finally:
        pygame.event.get = real_get
    return counter["n"], seen


def t_arranque_real():
    """El programa completo corre: ventana, audio, música, menú, juego, pausa y cierre (bucle asíncrono)."""
    script = {
        5: [Ev(pygame.K_t, "t")], 10: [Ev(pygame.K_RETURN)], 15: [Ev(pygame.K_RETURN)], 20: [Ev(pygame.K_RETURN)],
        25: [Ev(pygame.K_RETURN)], 120: [Ev(pygame.K_ESCAPE)], 140: [Ev(pygame.K_ESCAPE)],
        150: [Ev(pygame.K_m, "m")], 180: [Ev(pygame.K_SPACE, " "), Ev(pygame.K_g, "g"), Ev(pygame.K_e, "e")],
        200: [pygame.event.Event(pygame.QUIT)],
    }
    for events in script.values():
        for i, ev in enumerate(events):
            if isinstance(ev, Ev):
                events[i] = pygame.event.Event(pygame.KEYDOWN, key=ev.key, unicode=ev.unicode)
    counter = {"n": 0}
    real_get = pygame.event.get

    def fake_get(*args, **kwargs):
        counter["n"] += 1
        return script.get(counter["n"], [])

    pygame.event.get = fake_get
    muted_before = audio.muted
    try:
        # se avanza la corrutina a mano: en el navegador el bucle debe ceder el control en CADA cuadro
        coro = M.run_game()
        frames_per_turn = []
        try:
            while True:
                before = counter["n"]
                coro.send(None)
                frames_per_turn.append(counter["n"] - before)
        except StopIteration:
            pass
        assert frames_per_turn and max(frames_per_turn) <= 1, "el bucle debe ceder el control (await) en cada cuadro"
    finally:
        pygame.event.get = real_get
        reinit_after_quit(muted_before)
    assert counter["n"] == 200, f"el bucle corrió {counter['n']} cuadros"


def t_sin_salida_en_navegador():
    g = new_game(playing=False)
    result = g.handle_key(Ev(pygame.K_ESCAPE))
    assert result is IS_WEB, "ESC en el menú: cierra en escritorio, no hace nada en el navegador"
    g.draw()
    g.handle_key(Ev(pygame.K_RETURN))
    g.handle_key(Ev(pygame.K_ESCAPE))
    g.draw()                                   # el menú de pausa se dibuja sin la opción de salir en el navegador


def t_pantalla_de_error():
    """Si algo falla al arrancar, en el navegador se ve el error en pantalla (no una pantalla gris)."""
    real_learning = M.Learning

    class Roto:
        def __init__(self):
            raise RuntimeError("falla de prueba al arrancar")

    M.Learning = Roto
    try:
        coro = M.run_game()
        if not IS_WEB:
            try:
                for _ in range(10):
                    coro.send(None)
                raise AssertionError("en escritorio el error debe propagarse")
            except RuntimeError as exc:
                assert "falla de prueba" in str(exc)
            return
        for _ in range(6):
            coro.send(None)                                     # sigue vivo, mostrando el error
        surface = pygame.display.get_surface()
        assert surface.get_at((3, 3))[:3] == (90, 20, 20), "el fondo de error debe ser rojo oscuro"
        lit = sum(1 for x in range(20, 700, 3) for y in range(20, 200, 3) if surface.get_at((x, y))[:3] == (255, 255, 255))
        assert lit > 50, "debe haber texto del error dibujado"
        coro.close()
    finally:
        M.Learning = real_learning
        reinit_after_quit()


def t_audio_diferido():
    """En el navegador el audio inicia hasta el primer toque; en escritorio, desde el principio."""
    audio.ready, audio.tried, audio.sounds = False, False, {}
    key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r")
    quit_event = pygame.event.Event(pygame.QUIT)
    try:
        frames, seen = run_scripted({5: [key], 8: [quit_event]})
        before_key = seen[3]
        after_key = seen[7]
        if IS_WEB:
            assert before_key == (False, False), f"antes del primer toque no debe tocar el audio: {before_key}"
        assert after_key[1], "después del primer toque el audio debe estar listo"
        assert len(audio.sounds) >= 18, f"solo cargaron {len(audio.sounds)} sonidos"
    finally:
        reinit_after_quit()


def t_error_de_importacion():
    """Si falla al importar los archivos del juego, en el navegador se ve el error (no una pantalla gris)."""
    source = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read().replace("asyncio.run(start())", "")
    namespace = {"__name__": "main_de_prueba"}
    exec(compile(source, "main.py", "exec"), namespace)
    saved = sys.modules.get("src.game")
    sys.modules["src.game"] = None                       # hace que "from src.game import ..." falle
    try:
        coro = namespace["start"]()
        if not IS_WEB:
            try:
                coro.send(None)
                raise AssertionError("en escritorio el error de importación debe propagarse")
            except ImportError:
                return
        for _ in range(4):
            coro.send(None)
        surface = pygame.display.get_surface()
        assert surface.get_at((3, 3))[:3] == (90, 20, 20), "debe mostrar la pantalla de error"
        coro.close()
    finally:
        sys.modules["src.game"] = saved
        reinit_after_quit()


TESTS = [
    ("RF-01", "Movimiento con WASD, en diagonal y límites de pantalla", t_movimiento),
    ("RF-02", "Disparo automático al enemigo más cercano", t_disparo_cercano),
    ("RF-03", "No dispara a enemigos fuera de la pantalla", t_disparo_ignora_fuera),
    ("RF-04", "Las balas atraviesan el número de enemigos configurado", t_perforacion),
    ("RF-05", "Los 4 tipos de enemigo se desbloquean con el tiempo", t_enemigos_desbloqueo),
    ("RF-06", "Daño al jugador e invulnerabilidad tras un golpe", t_dano_e_invulnerabilidad),
    ("RF-07", "Regeneración de vida con tope en el máximo", t_regeneracion),
    ("RF-08", "Habilidad Coffee Boost: efecto, duración y recarga", t_coffee),
    ("RF-09", "Habilidad Git Rollback: regreso, invulnerabilidad y recarga", t_rollback),
    ("RF-10", "Habilidad Refactorizar: daño en radio y conteo de bugs", t_refactor),
    ("RF-11", "Deadline que vence aplica daño directo", t_deadline_vence),
    ("RF-12", "El disparo prioriza deadlines por vencer", t_deadline_prioridad),
    ("RNF-01", "Los deadlines alcanzan al jugador antes de vencer", t_deadline_alcanzable),
    ("RF-13", "Reto de preguntas: acierto, fallo adaptativo y tiempo agotado", t_reto_preguntas),
    ("RF-14", "Reto de preguntas responde con el teclado numérico", t_reto_teclado_numerico),
    ("RF-15", "Menú de mejoras: 3 opciones distintas y selección", t_mejora_aparece),
    ("RF-16", "Cada una de las 9 mejoras produce su efecto", t_mejoras_efectos),
    ("RF-17", "Backup revive una vez y limpia enemigos cercanos", t_backup_revive),
    ("RF-18", "Game Over, puntaje y leaderboard Top 5", t_game_over_y_leaderboard),
    ("RF-19", "Bugpedia: fichas completas y aviso por enemigo nuevo", t_bugpedia),
    ("RF-20", "Resumen de aprendizaje por tema", t_resumen_aprendizaje),
    ("RF-21", "Progreso de aprendizaje guardado entre partidas", t_progreso_guardado),
    ("RF-22", "Menú principal, tutorial y puntajes", t_pantallas),
    ("RF-23", "Pausa: congela el tiempo, reinicia y sale", t_pausa),
    ("RF-24", "Volver al menú desde el Game Over", t_menu_desde_game_over),
    ("RF-25", "Sonido: efectos, música y silencio", t_audio),
    ("RF-26", "Ventana redimensionable y escalado sin deformar", t_escalado_ventana),
    ("RNF-02", "Banco de preguntas válido (4 temas, 4 opciones, explicación)", t_banco_preguntas),
    ("RNF-03", "El juego no truena sin archivos de datos", t_sin_archivos_de_datos),
    ("RF-27", "Tipografía incluida: dibuja acentos y los textos caben", t_fuentes),
    ("RF-28", "Almacenamiento local: archivo, localStorage y respaldo", t_almacenamiento),
    ("RF-29", "Arranque completo del programa (bucle asíncrono)", t_arranque_real),
    ("RF-30", "Salida del juego según la plataforma", t_sin_salida_en_navegador),
    ("RF-31", "Un error de arranque se muestra en pantalla (no queda gris)", t_pantalla_de_error),
    ("RF-32", "El audio inicia en el primer toque (navegador) o al inicio (escritorio)", t_audio_diferido),
    ("RF-33", "Un error al importar los archivos se muestra en pantalla", t_error_de_importacion),
]


def main():
    rows = []
    print(f"{'ID':7s} {'Resultado':10s} {'Prueba'}")
    for tid, name, fn in TESTS:
        t0 = time.time()
        try:
            fn()
            status, detail = "APROBADA", ""
        except Exception as exc:                       # noqa: BLE001
            status = "FALLÓ"
            detail = f"{type(exc).__name__}: {exc}" if str(exc) else traceback.format_exc().splitlines()[-1]
        ms = (time.time() - t0) * 1000
        rows.append((tid, name, status, ms, detail))
        print(f"{tid:7s} {status:10s} {name}" + (f"\n          -> {detail}" if detail else ""))

    passed = sum(1 for r in rows if r[2] == "APROBADA")
    print(f"\n{passed}/{len(rows)} pruebas aprobadas")

    lines = [
        "# Resultados de las pruebas de funcionalidad",
        "",
        f"Fecha: {time.strftime('%Y-%m-%d %H:%M')}  ·  pygame-ce {pygame.version.ver}  ·  Python {sys.version.split()[0]}  ·  modo {'navegador (simulado)' if WEB else 'escritorio'}",
        "",
        f"**{passed} de {len(rows)} pruebas aprobadas.**",
        "",
        "| ID | Prueba | Resultado | Tiempo (ms) |",
        "|---|---|---|---|",
    ]
    for tid, name, status, ms, detail in rows:
        mark = "✔ Aprobada" if status == "APROBADA" else f"✘ Falló: {detail}"
        lines.append(f"| {tid} | {name} | {mark} | {ms:.0f} |")
    with open(os.path.join(ROOT, "tests", "resultados_web.md" if WEB else "resultados.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
