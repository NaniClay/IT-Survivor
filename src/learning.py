import json
import os
import random
import time

from settings import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def _load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


class Learning:
    """Retos de preguntas, estadísticas por tema, Bugpedia y dificultad adaptativa."""

    def __init__(self):
        self.bank = _load_json(os.path.join(DATA, "questions.json"), [])
        self.bugpedia = _load_json(os.path.join(DATA, "bugpedia.json"), {})

        # progreso guardado de partidas anteriores
        self.path = os.path.join(ROOT, PROGRESS_FILE)
        saved = _load_json(self.path, {})
        self.games = saved.get("games", 0)
        self.seen_ever = set(saved.get("bugpedia", []))
        self.totals = saved.get("topics", {})
        self.runs = saved.get("runs", [])

        self.reset_run()

    # ------------------------------------------------------------ partida
    def reset_run(self):
        self.stats = {t: {"answered": 0, "correct": 0} for t in TOPIC_ENEMY}
        self.misses = {t: 0 for t in TOPIC_ENEMY}
        self.used = set()
        self.unlocked = []        # tipos de enemigo vistos en esta partida
        self.current = None

    def total_correct(self):
        return sum(s["correct"] for s in self.stats.values())

    # ------------------------------------------------------------ preguntas
    def pick(self):
        """Elige una pregunta. Los temas que más fallas salen con más frecuencia."""
        if not self.bank:
            return None
        topics = sorted({q["topic"] for q in self.bank})
        weights = [1 + self.misses.get(t, 0) for t in topics]
        topic = random.choices(topics, weights=weights)[0]

        pool = [q for q in self.bank if q["topic"] == topic and q["id"] not in self.used]
        if not pool:  # ya salieron todas las de ese tema: se vuelven a habilitar
            self.used -= {q["id"] for q in self.bank if q["topic"] == topic}
            pool = [q for q in self.bank if q["topic"] == topic]
        q = random.choice(pool)
        self.used.add(q["id"])

        order = list(range(len(q["options"])))
        random.shuffle(order)  # las opciones cambian de lugar cada vez
        self.current = {
            "id": q["id"],
            "topic": q["topic"],
            "question": q["question"],
            "options": [q["options"][i] for i in order],
            "correct": order.index(q["answer"]),
            "explanation": q["explanation"],
            "chosen": None,
            "ok": None,
        }
        return self.current

    def answer(self, choice):
        """choice = índice de la opción, o None si se acabó el tiempo."""
        c = self.current
        c["chosen"] = choice
        c["ok"] = (choice == c["correct"])
        s = self.stats.setdefault(c["topic"], {"answered": 0, "correct": 0})
        s["answered"] += 1
        if c["ok"]:
            s["correct"] += 1
            self.misses[c["topic"]] = max(0, self.misses.get(c["topic"], 0) - 1)
        else:
            self.misses[c["topic"]] = self.misses.get(c["topic"], 0) + 1
        return c["ok"]

    # ------------------------------------------------- dificultad adaptativa
    def bias(self, kind):
        """Multiplicador de frecuencia de un enemigo según los temas que has fallado."""
        for topic, enemy in TOPIC_ENEMY.items():
            if enemy == kind:
                return min(BIAS_MAX, 1 + BIAS_PER_MISS * self.misses.get(topic, 0))
        return 1.0

    # ------------------------------------------------------------ Bugpedia
    def see_enemy(self, kind):
        """Registra un enemigo visto. Regresa su ficha la primera vez que aparece en cada partida."""
        self.seen_ever.add(kind)
        if kind in self.unlocked:
            return None
        self.unlocked.append(kind)
        return self.bugpedia.get(kind)

    # ------------------------------------------------------------ guardado
    def save(self, score, elapsed, bugs_fixed, perks_taken):
        """Guarda el progreso acumulado y un registro de la partida (sirve para las pruebas)."""
        self.games += 1
        for topic, s in self.stats.items():
            t = self.totals.setdefault(topic, {"answered": 0, "correct": 0})
            t["answered"] += s["answered"]
            t["correct"] += s["correct"]
        self.runs.append({
            "fecha": time.strftime("%Y-%m-%d %H:%M"),
            "puntos": score,
            "tiempo": int(elapsed),
            "bugs": bugs_fixed,
            "temas": {t: dict(s) for t, s in self.stats.items()},
            "mejoras": dict(perks_taken),
        })
        self.runs = self.runs[-50:]
        data = {
            "games": self.games,
            "bugpedia": sorted(self.seen_ever),
            "topics": self.totals,
            "runs": self.runs,
        }
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # si no se puede escribir, el juego sigue
