"""Genera los efectos de sonido y la música de IT Survivor (estilo chiptune, sin dependencias extra).

Uso (desde la raíz del repo):
    python tools/generate_sounds.py

Escribe archivos WAV en assets/sounds/. Son sonidos de relleno: cuando haya sonidos finales,
basta con reemplazar los WAV conservando el nombre (music.wav es el loop de fondo).
"""
import math
import os
import random
import struct
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "sounds")
RATE = 22050
random.seed(11)


# ---------------------------------------------------------------- síntesis
def wave_value(kind, phase, duty=0.5):
    p = phase % 1.0
    if kind == "square":
        # se le resta la media para que el pulso quede centrado en 0 (sin desfase DC) con cualquier duty
        return (1.0 if p < duty else -1.0) - (2.0 * duty - 1.0)
    if kind == "saw":
        return 2.0 * p - 1.0
    if kind == "tri":
        return 4.0 * abs(p - 0.5) - 1.0
    return math.sin(2 * math.pi * p)          # sine


def note(freq, dur, kind="square", vol=0.4, end_freq=None, attack=0.004, release=0.04,
         duty=0.5, vibrato=0.0):
    """Una nota. Si end_freq existe, el tono se desliza de freq a end_freq."""
    n = int(RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / RATE
        if end_freq:
            f = freq * (end_freq / freq) ** (t / dur)
        else:
            f = freq
        if vibrato:
            f *= 1 + vibrato * math.sin(2 * math.pi * 6 * t)
        phase += f / RATE
        a = min(1.0, t / attack) if attack > 0 else 1.0
        r = min(1.0, (dur - t) / release) if release > 0 else 1.0
        out.append(wave_value(kind, phase, duty) * vol * a * max(0.0, r))
    return out


def noise(dur, vol=0.3, lowpass=0.0, highpass=False, release=0.03):
    """Ruido blanco. lowpass entre 0 y 1: más alto = más grave. highpass deja solo lo agudo."""
    n = int(RATE * dur)
    out = []
    y = 0.0
    for i in range(n):
        x = random.uniform(-1, 1)
        if lowpass:
            y += (1 - lowpass) * (x - y)
            x = (x - y) if highpass else y
        t = i / RATE
        env = max(0.0, min(1.0, (dur - t) / release)) if release > 0 else 1.0
        out.append(x * vol * env * (1 - i / n) ** 1.2)
    return out


def mix(*parts):
    """Suma pistas. Cada parte es (muestras, segundo_de_inicio) o solo muestras."""
    items = [p if isinstance(p, tuple) else (p, 0.0) for p in parts]
    total = max(int(start * RATE) + len(samples) for samples, start in items)
    out = [0.0] * total
    for samples, start in items:
        offset = int(start * RATE)
        for i, v in enumerate(samples):
            out[offset + i] += v
    return out


def seq(notes, gap=0.0):
    """Notas una detrás de otra."""
    out, t = [], 0.0
    parts = []
    for n, dur in notes:
        parts.append((n, t))
        t += dur + gap
    return mix(*parts)


def save(name, samples, peak=0.85):
    top = max(abs(v) for v in samples) or 1.0
    scale = min(1.0, peak / top) if top > peak else 1.0
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        data = b"".join(struct.pack("<h", int(max(-1, min(1, v * scale)) * 32767)) for v in samples)
        w.writeframes(data)
    print(f"{name}.wav  {len(samples) / RATE:.2f} s")


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ----------------------------------------------------------------- efectos
def make_effects():
    save("shoot", note(900, 0.07, "square", 0.22, end_freq=420, duty=0.25, release=0.03))
    save("hit", mix(noise(0.05, 0.25, 0.4), note(240, 0.05, "square", 0.2, end_freq=120)))
    save("kill", mix(note(560, 0.10, "square", 0.28, end_freq=170, release=0.05),
                     noise(0.06, 0.18, 0.5, highpass=True)))
    save("hurt", mix(note(220, 0.20, "saw", 0.45, end_freq=70, release=0.08), noise(0.10, 0.25, 0.6)))
    save("coffee", seq([(note(midi(m), 0.055, "tri", 0.38), 0.055) for m in (72, 76, 79, 84)]))
    save("rollback", mix(note(1100, 0.38, "tri", 0.38, end_freq=260, vibrato=0.02, release=0.12),
                         (note(1100, 0.38, "tri", 0.16, end_freq=260, vibrato=0.02, release=0.12), 0.09)))
    save("refactor", mix(note(130, 0.45, "sine", 0.7, end_freq=38, release=0.2),
                         noise(0.35, 0.35, 0.82, release=0.15)))
    save("quiz_open", seq([(note(660, 0.08, "square", 0.3, duty=0.25), 0.09),
                           (note(880, 0.13, "square", 0.3, duty=0.25), 0.13)]))
    save("correct", seq([(note(midi(m), 0.085, "square", 0.32, duty=0.25), 0.085) for m in (72, 76, 79, 84)]))
    save("wrong", mix(note(150, 0.38, "saw", 0.42, end_freq=95, release=0.12),
                      note(158, 0.38, "saw", 0.3, end_freq=100, release=0.12)))
    save("upgrade_open", seq([(note(midi(m), 0.07, "tri", 0.4), 0.07) for m in (67, 72, 76)]
                              + [(note(midi(79), 0.2, "tri", 0.4, release=0.12), 0.2)]))
    save("upgrade_pick", seq([(note(784, 0.06, "square", 0.3, duty=0.25), 0.06),
                              (note(1047, 0.14, "square", 0.3, duty=0.25), 0.14)]))
    save("revive", mix(note(200, 0.5, "tri", 0.45, end_freq=900, release=0.1),
                       (seq([(note(midi(m), 0.09, "square", 0.25, duty=0.25), 0.09) for m in (79, 84, 88)]), 0.4)))
    save("bugpedia", mix(note(1320, 0.30, "sine", 0.3, attack=0.004, release=0.28),
                         (note(1980, 0.22, "sine", 0.14, release=0.2), 0.05)))
    save("deadline_fail", seq([(note(f, 0.08, "square", 0.34), 0.08) for f in (720, 520, 720, 520, 720, 520)]))
    save("gameover", seq([(note(midi(m), 0.22, "tri", 0.5, release=0.1), 0.22) for m in (67, 64, 60, 55)]
                         + [(note(midi(48), 0.5, "tri", 0.5, release=0.3), 0.5)]))
    save("select", note(700, 0.05, "square", 0.25, duty=0.25))
    save("menu_move", note(520, 0.04, "square", 0.3, duty=0.25))


# ------------------------------------------------------------------ música
def make_music():
    bpm = 124
    step = 60.0 / bpm / 4                     # un "paso" = una semicorchea
    steps_per_bar = 16
    bars = 8
    total_steps = steps_per_bar * bars
    length = int(total_steps * step * RATE)
    out = [0.0] * length

    # progresión en La menor: Am - F - C - G (cada acorde dura 2 compases)
    chords = [(57, (0, 3, 7)), (53, (0, 4, 7)), (60, (0, 4, 7)), (55, (0, 4, 7))]
    bass_pattern = [0, 0, 12, 0, 0, 12, 7, 0]
    arp_pattern = [0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 3, 2, 1, 0, 1]

    def add(samples, step_index, offset_steps=0.0):
        start = int((step_index + offset_steps) * step * RATE)
        for i, v in enumerate(samples):
            j = start + i
            if j < length:
                out[j] += v

    kick = note(130, 0.13, "sine", 0.55, end_freq=42, attack=0.001, release=0.05)
    snare = mix(noise(0.11, 0.26, 0.45, highpass=True), note(190, 0.08, "tri", 0.18, end_freq=120))
    hat = noise(0.035, 0.11, 0.6, highpass=True)

    for bar in range(bars):
        root, tones = chords[(bar // 2) % len(chords)]
        for s in range(steps_per_bar):
            idx = bar * steps_per_bar + s
            if s % 4 == 0:
                add(kick, idx)
            if s in (4, 12):
                add(snare, idx)
            if s % 2 == 0 and s not in (4, 12):
                add(hat, idx)
            if s % 2 == 0:                    # bajo en corcheas
                semitone = bass_pattern[(s // 2) % len(bass_pattern)]
                add(note(midi(root - 12 + semitone), step * 1.8, "square", 0.20, duty=0.5, release=0.03), idx)
            tone = tones[arp_pattern[s] % len(tones)]
            octave = 12 if arp_pattern[s] < 3 else 24
            add(note(midi(root + tone + octave), step * 0.9, "square", 0.085, duty=0.25, release=0.02), idx)

    # un pequeño "pad" suave para dar cuerpo, sigue los acordes
    for bar in range(bars):
        root, tones = chords[(bar // 2) % len(chords)]
        for tone in tones:
            add(note(midi(root + tone), step * steps_per_bar, "tri", 0.05, attack=0.05, release=0.12),
                bar * steps_per_bar)

    # el final se apaga un poco para que el loop no suene a corte
    fade = int(0.02 * RATE)
    for i in range(fade):
        out[length - 1 - i] *= i / fade
    save("music", out, peak=0.8)


if __name__ == "__main__":
    make_effects()
    make_music()
