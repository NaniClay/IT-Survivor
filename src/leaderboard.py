import json
import os
from settings import *

# el archivo se guarda en la raíz del proyecto, sin importar desde dónde corras el juego
PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    LEADERBOARD_FILE,
)


def calc_score(elapsed, bugs_fixed):
    return int(elapsed) * SCORE_PER_SECOND + bugs_fixed * SCORE_PER_BUG


def load():
    """Regresa la lista de puntajes, de mayor a menor. Si no hay archivo, lista vacía."""
    try:
        with open(PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    entries = [e for e in data if isinstance(e, dict) and "score" in e]
    return sorted(entries, key=lambda e: e["score"], reverse=True)


def qualifies(score):
    entries = load()
    return len(entries) < LEADERBOARD_SIZE or score > entries[-1]["score"]


def add_entry(name, score, elapsed, bugs_fixed):
    entries = load()
    entries.append({
        "name": name or "ANON",
        "score": score,
        "time": int(elapsed),
        "bugs": bugs_fixed,
    })
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:LEADERBOARD_SIZE]
    try:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # si no se puede escribir, el juego sigue sin tronar
    return entries