"""Lectura y escritura de los datos locales (leaderboard y progreso de aprendizaje).

En escritorio se guardan como archivos junto al juego. En el navegador se intenta usar el
localStorage de la página (para que los datos sobrevivan al recargar) y, si no está disponible,
se usa el sistema de archivos virtual del navegador (dura mientras la pestaña esté abierta).
"""
import os

from settings import IS_WEB


def _local_storage():
    if not IS_WEB:
        return None
    try:
        import platform
        return platform.window.localStorage
    except Exception:                                        # noqa: BLE001
        return None


def _key(path):
    return "itsurvivor:" + os.path.basename(path)


def read_text(path):
    """Regresa el texto guardado, o None si no existe."""
    storage = _local_storage()
    if storage is not None:
        try:
            value = storage.getItem(_key(path))
            if value:
                return str(value)
        except Exception:                                    # noqa: BLE001
            pass
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def write_text(path, text):
    """Guarda el texto. Regresa True si se pudo guardar."""
    storage = _local_storage()
    if storage is not None:
        try:
            storage.setItem(_key(path), text)
            return True
        except Exception:                                    # noqa: BLE001
            pass
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except OSError:
        return False
