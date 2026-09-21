WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "IT Survivor"
BG_COLOR = (20, 24, 38)

PLAYER_SPEED = 260   # píxeles por segundo
PLAYER_SIZE = 32

ENEMY_SPEED = 90
ENEMY_SIZE = 24
SPAWN_INTERVAL = 1.5       # segundos entre enemigos al inicio
SPAWN_MIN_INTERVAL = 0.3   # el límite más rápido al que puede llegar

PLAYER_MAX_HP = 100
ENEMY_DAMAGE = 10
INVULN_TIME = 0.5   # segundos de invulnerabilidad después de un golpe

FIRE_RATE = 0.4        # segundos entre disparos
BULLET_SPEED = 500
BULLET_SIZE = 8
BULLET_DAMAGE = 1
BULLET_LIFETIME = 2.0  # segundos antes de desaparecer si no pega

ENEMY_HP = 2

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
        "color": (60, 140, 230), "unlock": 70, "weight": 3,
    },
}

DEADLINE_TIME = 8.0      # segundos antes de que la entrega "venza"
DEADLINE_PENALTY = 30    # daño al jugador si vence

COFFEE_DURATION = 5.0      # segundos que dura el boost
COFFEE_COOLDOWN = 15.0     # segundos desde que lo activas hasta poder usarlo otra vez
COFFEE_SPEED_MULT = 1.5    # +50% de velocidad
COFFEE_FIRE_MULT = 2.0     # dispara al doble de rápido

ROLLBACK_SECONDS = 5.0           # a cuántos segundos atrás regresas
ROLLBACK_SAVE_INTERVAL = 0.25    # cada cuánto se guarda un "commit"
ROLLBACK_COOLDOWN = 30.0
ROLLBACK_INVULN = 1.0            # invulnerabilidad después de regresar

REFACTOR_RADIUS = 220
REFACTOR_DAMAGE = 3
REFACTOR_COOLDOWN = 20.0
REFACTOR_WAVE_TIME = 0.35   # lo que dura la animación de la onda

LEADERBOARD_FILE = "leaderboard.json"
LEADERBOARD_SIZE = 5
NAME_MAX_LEN = 10
SCORE_PER_SECOND = 1
SCORE_PER_BUG = 10