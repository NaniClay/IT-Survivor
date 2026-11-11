import os
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "assets", "sprites")
_cache = {}


def load_sprite(name, size, fallback_color):
    """Carga assets/sprites/<name>.png a size x size.
    Si el archivo no existe, regresa un cuadro de color para que el juego no truene."""
    key = (name, size)
    if key in _cache:
        return _cache[key]
    path = os.path.join(SPRITES, name + ".png")
    try:
        img = pygame.image.load(path).convert_alpha()
        if img.get_size() != (size, size):
            img = pygame.transform.scale(img, (size, size))
    except Exception:                                        # noqa: BLE001
        img = pygame.Surface((size, size), pygame.SRCALPHA)
        img.fill(fallback_color)
    _cache[key] = img
    return img


def load_background(width, height, fallback_color):
    """Arma el fondo repitiendo bg_tile.png. Se llama una sola vez al iniciar."""
    surface = pygame.Surface((width, height))
    surface.fill(fallback_color)
    try:
        tile = pygame.image.load(os.path.join(SPRITES, "bg_tile.png")).convert()
    except Exception:                                        # noqa: BLE001
        return surface
    tw, th = tile.get_size()
    for x in range(0, width, tw):
        for y in range(0, height, th):
            surface.blit(tile, (x, y))
    return surface
