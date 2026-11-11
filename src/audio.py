import os
import pygame
from settings import SFX_VOLUME, MUSIC_VOLUME, IS_WEB

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS = os.path.join(ROOT, "assets", "sounds")

# el navegador solo acepta OGG; en escritorio se usa WAV (los dos juegos de archivos vienen incluidos)
EXT = ".ogg" if IS_WEB else ".wav"

# separación mínima (ms) entre dos reproducciones del mismo sonido, para que no se amontonen
MIN_GAP = {"shoot": 110, "hit": 70, "kill": 60, "hurt": 150}


class Audio:
    """Sonido con respaldo: si no hay tarjeta de audio o faltan los archivos, el juego sigue en silencio."""

    def __init__(self):
        self.ready = False
        self.tried = False         # ya se intentó iniciar el audio (para no reintentar en cada tecla)
        self.muted = False
        self.sounds = {}
        self._last = {}

    def init(self):
        self.tried = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:                                    # noqa: BLE001  (sin audio, el juego sigue en silencio)
            return
        self.ready = True
        if os.path.isdir(SOUNDS):
            for filename in os.listdir(SOUNDS):
                name, ext = os.path.splitext(filename)
                if ext.lower() == EXT and name != "music":
                    try:
                        sound = pygame.mixer.Sound(os.path.join(SOUNDS, filename))
                        sound.set_volume(SFX_VOLUME)
                        self.sounds[name] = sound
                    except Exception:                        # noqa: BLE001
                        pass

    def music(self):
        if not self.ready:
            return
        path = os.path.join(SOUNDS, "music" + EXT)
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        except Exception:                                    # noqa: BLE001
            pass

    def play(self, name):
        if not self.ready or self.muted:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        now = pygame.time.get_ticks()
        if now - self._last.get(name, -10**6) < MIN_GAP.get(name, 40):
            return
        self._last[name] = now
        try:
            sound.play()
        except Exception:                                    # noqa: BLE001
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.ready:
            try:
                pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
            except Exception:                                # noqa: BLE001
                pass
        return self.muted


audio = Audio()
