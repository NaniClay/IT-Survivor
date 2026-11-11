import os
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
REGULAR = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
BOLD = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")

# DejaVu Sans Mono es ~9% más ancha que Consolas; se reduce el tamaño para conservar el diseño original
SCALE = 0.92
_cache = {}


def get_font(size, bold=False):
    """Tipografía incluida con el juego (se ve igual en Windows, Mac, Linux y navegador).
    Si faltara el archivo, usa Consolas y, en último caso, la fuente por defecto de pygame."""
    key = (size, bold)
    if key in _cache:
        return _cache[key]
    try:
        font = pygame.font.Font(BOLD if bold else REGULAR, round(size * SCALE))
    except (FileNotFoundError, OSError, pygame.error):
        try:
            font = pygame.font.SysFont("consolas", size, bold=bold)
        except Exception:                                    # noqa: BLE001
            font = pygame.font.Font(None, size)
    _cache[key] = font
    return font
