"""Convierte los WAV de assets/sounds/ a OGG (el navegador solo reproduce OGG).

Uso (desde la raíz del repo):
    pip install soundfile
    python tools/wav_to_ogg.py
"""
import glob
import os
import sys

import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "sounds")

for wav in sorted(glob.glob(os.path.join(FOLDER, "*.wav"))):
    data, rate = sf.read(wav)
    ogg = os.path.splitext(wav)[0] + ".ogg"
    sf.write(ogg, data, rate, format="OGG", subtype="VORBIS")
    print(f"{os.path.basename(ogg):22s} {os.path.getsize(wav) // 1024:5d} KB -> {os.path.getsize(ogg) // 1024:4d} KB")
