import json
import os
from settings import *
from src import storage

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), LEADERBOARD_FILE)


def calc_score(elapsed, bugs_fixed):
    return int(elapsed) * SCORE_PER_SECOND + bugs_fixed * SCORE_PER_BUG


def load():
    """Regresa la lista de puntajes, de mayor a menor. Si no hay datos, lista vacía."""
    text = storage.read_text(PATH)
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
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
    # si no se puede escribir, el juego sigue sin tronar
    storage.write_text(PATH, json.dumps(entries, indent=2, ensure_ascii=False))
    return entries
