"""IT Survivor: punto de entrada (escritorio y navegador)."""
import asyncio
import os
import sys
import traceback

import pygame


async def fatal(error):
    """Muestra un error de arranque en pantalla (en el navegador, para no quedarse en gris)."""
    print("[IT Survivor] ERROR\n" + error)
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.Font(None, 26)
    lines = ["IT Survivor: ocurrió un error al iniciar", "",
             "Toma una captura de esta pantalla y compártela para poder arreglarlo.", ""]
    lines += [raw[:110] for raw in error.splitlines()[-20:]]
    while True:
        screen.fill((90, 20, 20))
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (255, 255, 255)), (20, 20 + i * 26))
        pygame.display.flip()
        await asyncio.sleep(0)


async def start():
    try:
        from src.game import run_game        # se importa aquí para poder mostrar cualquier error de importación
    except Exception:                        # noqa: BLE001
        if not (sys.platform == "emscripten" or os.environ.get("ITS_WEB") == "1"):
            raise
        await fatal(traceback.format_exc())
        return
    await run_game()


asyncio.run(start())
