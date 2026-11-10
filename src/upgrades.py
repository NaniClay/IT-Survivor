import random

# Cada mejora es una buena práctica de desarrollo. "why" es lo que el jugador aprende al elegirla.
UPGRADES = [
    {
        "id": "tests",
        "name": "Tests unitarios",
        "effect": "+50% de daño a los enemigos",
        "why": "Las pruebas unitarias verifican cada pieza del código y detectan fallos antes de que lleguen a producción.",
    },
    {
        "id": "backups",
        "name": "Backups",
        "effect": "Revives una vez con 50% de vida",
        "why": "Un respaldo reciente te permite recuperarte de un desastre. Hay que hacerlo antes de que algo falle.",
    },
    {
        "id": "review",
        "name": "Code review",
        "effect": "Recibes 25% menos de daño",
        "why": "Una segunda mirada atrapa errores cuando todavía son baratos de arreglar.",
    },
    {
        "id": "sprints",
        "name": "Planificación en sprints",
        "effect": "Los deadlines tardan 50% más en vencer",
        "why": "Dividir el trabajo en entregas pequeñas da margen y hace visibles los retrasos a tiempo.",
    },
    {
        "id": "commits",
        "name": "Commits frecuentes",
        "effect": "Git Rollback recarga 30% más rápido",
        "why": "Guardar el estado con frecuencia hace barato volver a una versión estable.",
    },
    {
        "id": "ci",
        "name": "Automatización (CI/CD)",
        "effect": "+25% de cadencia de disparo",
        "why": "Automatizar las tareas repetitivas ahorra tiempo y reduce los errores humanos.",
    },
]
UPGRADES_BY_ID = {u["id"]: u for u in UPGRADES}


def roll_choices(n=3):
    return random.sample(UPGRADES, n)


class Perks:
    """Mejoras elegidas en la partida. Cada una se puede tomar varias veces."""

    def __init__(self):
        self.taken = {}      # id -> cuántas veces
        self.revives = 0     # Backups disponibles

    def apply(self, uid):
        self.taken[uid] = self.taken.get(uid, 0) + 1
        if uid == "backups":
            self.revives += 1

    def _n(self, uid):
        return self.taken.get(uid, 0)

    @property
    def damage_mult(self):
        return 1.5 ** self._n("tests")

    @property
    def damage_taken_mult(self):
        return max(0.4, 0.75 ** self._n("review"))

    @property
    def deadline_time_mult(self):
        return 1.5 ** self._n("sprints")

    @property
    def rollback_cd_mult(self):
        return max(0.3, 0.7 ** self._n("commits"))

    @property
    def fire_mult(self):
        return 1.25 ** self._n("ci")
