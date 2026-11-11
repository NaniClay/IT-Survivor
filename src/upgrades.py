import random

# Cada mejora es una buena práctica de desarrollo. "why" es lo que el jugador aprende al elegirla.
UPGRADES = [
    {
        "id": "tests",
        "name": "Tests unitarios",
        "effect": "+1 bala por disparo",
        "why": "Más pruebas cubren más casos: cada disparo ataca varios frentes a la vez y detecta fallos antes de que lleguen a producción.",
    },
    {
        "id": "ci",
        "name": "Automatización (CI/CD)",
        "effect": "+30% de cadencia de disparo",
        "why": "Automatizar las tareas repetitivas ahorra tiempo y reduce los errores humanos.",
    },
    {
        "id": "modular",
        "name": "Arquitectura modular",
        "effect": "Las balas atraviesan 1 enemigo más",
        "why": "Un buen diseño en módulos hace que un cambio llegue más lejos sin romper todo lo demás.",
    },
    {
        "id": "review",
        "name": "Code review",
        "effect": "+25 de vida máxima y te curas 25",
        "why": "Una segunda mirada atrapa errores cuando todavía son baratos de arreglar y hace al equipo más resistente.",
    },
    {
        "id": "backups",
        "name": "Backups",
        "effect": "Revives una vez con 50% de vida",
        "why": "Un respaldo reciente te permite recuperarte de un desastre. Hay que hacerlo antes de que algo falle.",
    },
    {
        "id": "commits",
        "name": "Commits frecuentes",
        "effect": "Git Rollback recarga 30% más rápido",
        "why": "Guardar el estado con frecuencia hace barato volver a una versión estable.",
    },
    {
        "id": "refactor",
        "name": "Refactorización continua",
        "effect": "Refactorizar recarga 30% más rápido y abarca 20% más",
        "why": "Limpiar el código poco a poco evita que la deuda técnica se acumule y se vuelva imposible de pagar.",
    },
    {
        "id": "coffee",
        "name": "Cafetera industrial",
        "effect": "Coffee Boost dura 2 s más y recarga 30% más rápido",
        "why": "Descansar y mantener el ritmo también es parte del trabajo sostenible: un equipo cansado comete más errores.",
    },
    {
        "id": "sprints",
        "name": "Planificación en sprints",
        "effect": "Los deadlines tardan 50% más en vencer",
        "why": "Dividir el trabajo en entregas pequeñas da margen y hace visibles los retrasos a tiempo.",
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
    def extra_bullets(self):
        return min(4, self._n("tests"))

    @property
    def fire_mult(self):
        return 1.3 ** self._n("ci")

    @property
    def pierce_bonus(self):
        return self._n("modular")

    @property
    def rollback_cd_mult(self):
        return max(0.3, 0.7 ** self._n("commits"))

    @property
    def refactor_cd_mult(self):
        return max(0.3, 0.7 ** self._n("refactor"))

    @property
    def refactor_radius_mult(self):
        return 1.2 ** self._n("refactor")

    @property
    def coffee_cd_mult(self):
        return max(0.3, 0.7 ** self._n("coffee"))

    @property
    def coffee_duration_bonus(self):
        return 2.0 * self._n("coffee")

    @property
    def deadline_time_mult(self):
        return 1.5 ** self._n("sprints")
