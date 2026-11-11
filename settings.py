# ======================= IT Survivor: configuración y balance =======================
# Todos los números del juego viven aquí. Cámbialos, guarda y vuelve a correr main.py.
import os
import sys

# True cuando el juego corre en el navegador (pygbag). Con ITS_WEB=1 se puede simular en escritorio.
IS_WEB = sys.platform == "emscripten" or os.environ.get("ITS_WEB") == "1"

# --- ventana
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "IT Survivor"
BG_COLOR = (20, 24, 38)

# --- jugador
PLAYER_SPEED = 260        # píxeles por segundo
PLAYER_SIZE = 32
PLAYER_MAX_HP = 100
PLAYER_REGEN = 1.0        # vida que recuperas por segundo
INVULN_TIME = 0.5         # segundos de invulnerabilidad después de un golpe

# --- disparo automático
FIRE_RATE = 0.35          # segundos entre disparos
BULLET_SPEED = 520
BULLET_SIZE = 8
BULLET_DAMAGE = 1
BULLET_LIFETIME = 2.0
BULLET_PIERCE = 2         # a cuántos enemigos puede pegar cada bala
BULLET_SPREAD = 9         # grados entre balas cuando disparas varias a la vez
URGENT_DEADLINE = 7.0     # el disparo prioriza deadlines con menos de estos segundos

# --- oleadas
SPAWN_INTERVAL = 1.5      # segundos entre enemigos al empezar
SPAWN_MIN_INTERVAL = 0.55  # lo más rápido que puede llegar a salir uno
SPAWN_DECAY = 0.985       # cada enemigo acelera un poco el siguiente
ENEMY_HP_PER_MIN = 0.3    # los enemigos ganan esta fracción de vida por minuto de partida (0.5 = +50%)
ENEMY_HP_ACCEL = 0.2      # y esta otra, que crece con el cuadrado de los minutos (frena las partidas largas)

ENEMY_TYPES = {
    "bug": {
        "hp": 2, "speed": 90, "size": 24, "damage": 10,
        "color": (220, 60, 60), "unlock": 0, "weight": 10,
    },
    "db": {
        "hp": 1, "speed": 170, "size": 18, "damage": 8,
        "color": (170, 90, 220), "unlock": 20, "weight": 5,
    },
    "error500": {
        "hp": 6, "speed": 55, "size": 38, "damage": 20,
        "color": (240, 150, 40), "unlock": 45, "weight": 4,
    },
    "deadline": {
        "hp": 3, "speed": 70, "size": 34, "damage": 15,
        "color": (60, 140, 230), "unlock": 60, "weight": 3,
    },
}

DEADLINE_TIME = 15.0      # segundos de la cuenta regresiva de una entrega
DEADLINE_PENALTY = 25     # daño directo si la cuenta llega a 0

# --- habilidades
COFFEE_DURATION = 5.0
COFFEE_COOLDOWN = 15.0
COFFEE_SPEED_MULT = 1.5
COFFEE_FIRE_MULT = 2.0

ROLLBACK_SECONDS = 5.0
ROLLBACK_SAVE_INTERVAL = 0.25
ROLLBACK_COOLDOWN = 30.0
ROLLBACK_INVULN = 1.0

REFACTOR_RADIUS = 220
REFACTOR_DAMAGE = 3
REFACTOR_COOLDOWN = 20.0
REFACTOR_WAVE_TIME = 0.35

# --- puntaje y leaderboard
LEADERBOARD_FILE = "leaderboard.json"
LEADERBOARD_SIZE = 5
NAME_MAX_LEN = 10
SCORE_PER_SECOND = 1
SCORE_PER_BUG = 10

# --- aprendizaje: retos de preguntas
QUIZ_FIRST = 35           # segundo en que sale el primer reto
QUIZ_INTERVAL = 60        # segundos entre retos
QUIZ_TIME = 12.0          # segundos para contestar
QUIZ_HEAL = 30            # vida que recuperas al acertar
QUIZ_POINTS = 50          # puntos extra por respuesta correcta

# --- aprendizaje: mejoras (buenas prácticas)
UPGRADE_FIRST = 15        # segundo en que sale la primera mejora
UPGRADE_INTERVAL = 30     # segundos entre mejoras
REVIEW_HP = 25            # vida máxima que da "Code review"

# tema de las preguntas -> enemigo que se repite más si fallas ese tema
TOPIC_ENEMY = {
    "HTTP": "error500",
    "SQL": "db",
    "Depuración": "bug",
    "Git y proyectos": "deadline",
}
BIAS_PER_MISS = 0.6       # cuánto sube la frecuencia del enemigo por cada fallo
BIAS_MAX = 3.0            # tope de ese aumento (x3)

REVIVE_HP_RATIO = 0.5     # vida con la que revives usando el Backup
REVIVE_INVULN = 2.0
REVIVE_CLEAR_RADIUS = 250

PROGRESS_FILE = "learning_progress.json"

# --- sonido
SFX_VOLUME = 0.55
MUSIC_VOLUME = 0.30
