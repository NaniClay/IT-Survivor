"""Genera las texturas temporales (pixel-art) de IT Survivor.

Uso (desde la raíz del repo):
    pip install pillow
    python tools/generate_sprites.py

Escribe los PNG en assets/sprites/. Son texturas de relleno: cuando el equipo de
diseño tenga el arte final en Aseprite, basta con reemplazar los PNG conservando
el mismo nombre y tamaño.
"""
import os
import random
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "sprites")
SCALE = 2                          # cada "pixel de arte" se dibuja de 2x2 pixeles
OUTLINE = (15, 18, 30, 255)


# ---------------------------------------------------------------- utilidades
def canvas(n):
    return Image.new("RGBA", (n, n), (0, 0, 0, 0))


def rect(d, x0, y0, x1, y1, color):
    d.rectangle([x0, y0, x1, y1], fill=color)


def px(d, points, color):
    for x, y in points:
        d.point((x, y), fill=color)


def add_outline(img, color=OUTLINE):
    """Dibuja un contorno oscuro de 1 pixel alrededor de lo que ya está dibujado."""
    src = img.copy()
    w, h = src.size
    read = src.load()
    write = img.load()
    for y in range(h):
        for x in range(w):
            if read[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and read[nx, ny][3] > 0:
                        write[x, y] = color
                        break
    return img


def save(img, name):
    big = img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    big.save(os.path.join(OUT, name + ".png"))
    print(f"{name}.png  {big.width}x{big.height}")


FONT = {
    "5": ["###", "#..", "###", "..#", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
}


def text(d, x, y, s, color):
    for ch in s:
        for r, row in enumerate(FONT[ch]):
            for c, v in enumerate(row):
                if v == "#":
                    d.point((x + c, y + r), fill=color)
        x += 4


# ------------------------------------------------------------------- sprites
def make_player():
    """Estudiante con sudadera verde y laptop. 16x16 -> 32x32."""
    im = canvas(16)
    d = ImageDraw.Draw(im)
    hair = (70, 45, 35, 255)
    skin = (240, 200, 160, 255)
    skin_d = (200, 140, 110, 255)
    green = (80, 200, 120, 255)
    green_d = (50, 140, 80, 255)
    jeans = (60, 85, 160, 255)
    shoe = (235, 235, 240, 255)

    rect(d, 4, 1, 11, 3, hair)                 # pelo
    rect(d, 4, 4, 4, 5, hair)
    rect(d, 11, 4, 11, 5, hair)
    rect(d, 5, 4, 10, 4, hair)
    rect(d, 5, 5, 10, 7, skin)                 # cara
    px(d, [(6, 6), (9, 6)], OUTLINE)           # ojos
    px(d, [(7, 7), (8, 7)], skin_d)            # boca
    rect(d, 3, 8, 12, 12, green)               # sudadera
    rect(d, 3, 8, 3, 12, green_d)
    rect(d, 12, 8, 12, 12, green_d)
    rect(d, 6, 8, 9, 8, green_d)               # capucha
    rect(d, 2, 9, 2, 12, green_d)              # brazos
    rect(d, 13, 9, 13, 12, green_d)
    px(d, [(2, 12), (13, 12)], skin)           # manos
    rect(d, 5, 9, 10, 11, (40, 55, 85, 255))   # pantalla de la laptop
    px(d, [(6, 10), (7, 10), (9, 10)], (90, 255, 150, 255))  # "codigo"
    rect(d, 4, 12, 11, 12, (200, 205, 215, 255))              # base de la laptop
    rect(d, 5, 13, 6, 13, jeans)               # piernas
    rect(d, 9, 13, 10, 13, jeans)
    rect(d, 5, 14, 6, 14, shoe)                # tenis
    rect(d, 9, 14, 10, 14, shoe)
    return add_outline(im)


def make_bug():
    """Bug de sintaxis: insecto rojo. 12x12 -> 24x24."""
    im = canvas(12)
    d = ImageDraw.Draw(im)
    red = (220, 60, 60, 255)
    red_d = (150, 30, 40, 255)
    red_l = (255, 120, 110, 255)
    head = (90, 20, 30, 255)

    for y in (5, 7, 9):                        # patas
        px(d, [(1, y), (10, y)], red_d)
    d.ellipse([2, 4, 9, 10], fill=red)         # caparazón
    rect(d, 5, 4, 6, 10, red_d)                # línea central
    px(d, [(3, 6), (8, 6), (3, 8), (8, 8)], red_d)   # manchas
    px(d, [(4, 5)], red_l)                     # brillo
    d.ellipse([3, 2, 8, 4], fill=head)         # cabeza
    px(d, [(4, 3), (7, 3)], (255, 255, 255, 255))    # ojos
    px(d, [(3, 1), (8, 1)], head)              # antenas
    return add_outline(im)


def make_db():
    """Base de datos corrupta: cilindro morado con grieta. 9x9 -> 18x18."""
    im = canvas(9)
    d = ImageDraw.Draw(im)
    purple = (170, 90, 220, 255)
    purple_d = (110, 50, 160, 255)
    purple_l = (215, 160, 255, 255)
    crack = (255, 90, 130, 255)

    rect(d, 1, 2, 7, 7, purple)
    rect(d, 1, 2, 1, 7, purple_d)
    rect(d, 7, 2, 7, 7, purple_d)
    px(d, [(x, 4) for x in range(1, 8)], purple_d)
    px(d, [(x, 6) for x in range(1, 8)], purple_d)
    d.ellipse([1, 1, 7, 3], fill=purple_l)
    px(d, [(5, 2), (4, 3), (5, 4), (4, 5), (5, 6)], crack)   # grieta
    return add_outline(im)


def make_error500():
    """Ventana de error 500: caja naranja con el texto '500'. 19x19 -> 38x38."""
    im = canvas(19)
    d = ImageDraw.Draw(im)
    orange = (240, 150, 40, 255)
    orange_d = (170, 90, 20, 255)
    orange_l = (255, 200, 110, 255)
    white = (255, 255, 255, 255)

    rect(d, 1, 1, 17, 17, orange)
    rect(d, 1, 1, 17, 3, orange_d)             # barra de título
    px(d, [(3, 2), (5, 2), (7, 2)], orange_l)
    px(d, [(15, 2)], white)                    # botón de cerrar
    rect(d, 1, 4, 17, 4, orange_l)
    text(d, 4, 9, "500", white)
    px(d, [(x, 15) for x in range(3, 8)], orange_d)
    px(d, [(x, 15) for x in range(10, 16)], orange_d)
    return add_outline(im)


def make_deadline():
    """Entrega con deadline: calendario azul. 17x17 -> 34x34.
    El centro queda despejado porque el juego dibuja la cuenta regresiva encima."""
    im = canvas(17)
    d = ImageDraw.Draw(im)
    blue = (60, 140, 230, 255)
    blue_d = (30, 80, 160, 255)
    blue_l = (110, 180, 250, 255)
    ring = (220, 225, 235, 255)

    rect(d, 1, 2, 15, 15, blue)
    rect(d, 1, 2, 15, 5, blue_d)               # encabezado del calendario
    rect(d, 4, 1, 5, 3, ring)                  # argollas
    rect(d, 11, 1, 12, 3, ring)
    px(d, [(x, 6) for x in range(2, 15)], blue_l)
    px(d, [(3, 13), (5, 13), (11, 13), (13, 13)], blue_l)
    return add_outline(im)


def make_bullet():
    """Parche de código: orbe amarillo. 4x4 -> 8x8."""
    im = canvas(4)
    d = ImageDraw.Draw(im)
    yellow = (255, 200, 60, 255)
    white = (255, 245, 170, 255)
    px(d, [(1, 0), (2, 0), (0, 1), (3, 1), (0, 2), (3, 2), (1, 3), (2, 3)], yellow)
    rect(d, 1, 1, 2, 2, white)
    return im


def make_background():
    """Mosaico de 64x64 tipo placa de circuitos. Se repite sin costuras."""
    rnd = random.Random(7)
    im = Image.new("RGBA", (64, 64), (20, 24, 38, 255))
    d = ImageDraw.Draw(im)
    grid = (26, 31, 48, 255)
    trace = (33, 42, 68, 255)
    dot = (48, 62, 98, 255)
    noise = (23, 28, 44, 255)

    for _ in range(90):
        d.point((rnd.randrange(64), rnd.randrange(64)), fill=noise)
    d.line([(0, 0), (63, 0)], fill=grid)
    d.line([(0, 0), (0, 63)], fill=grid)
    d.line([(0, 32), (63, 32)], fill=grid)
    d.line([(32, 0), (32, 63)], fill=grid)

    traces = [
        [(8, 10), (22, 10), (22, 24)],
        [(40, 42), (54, 42), (54, 56)],
        [(10, 50), (10, 58), (24, 58)],
        [(44, 8), (44, 18), (56, 18)],
    ]
    for pts in traces:
        d.line(pts, fill=trace, width=2)
        for x, y in (pts[0], pts[-1]):
            d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=dot)
    return im


if __name__ == "__main__":
    save(make_player(), "player")
    save(make_bug(), "bug")
    save(make_db(), "db")
    save(make_error500(), "error500")
    save(make_deadline(), "deadline")
    save(make_bullet(), "bullet")
    os.makedirs(OUT, exist_ok=True)
    make_background().save(os.path.join(OUT, "bg_tile.png"))
    print("bg_tile.png  64x64")
