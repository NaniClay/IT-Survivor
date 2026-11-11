"""Empaqueta IT Survivor para el navegador con pygbag (Python -> WebAssembly).

Uso (desde la raíz del repo, con el entorno virtual activo):
    pip install pygbag
    python tools/build_web.py            construye y abre un servidor de prueba en http://localhost:8000
    python tools/build_web.py --build    solo construye (sin servidor)
    python tools/build_web.py --pages    construye y copia el resultado a docs/ (para GitHub Pages)
    python tools/build_web.py --archive  construye y genera un .zip para subir a itch.io

Arma primero una carpeta limpia (build_web/it_survivor) con solo lo que el juego necesita,
sin venv, pruebas ni los WAV (el navegador usa los OGG).
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "build_web")
STAGE = os.path.join(WORK, "it_survivor")          # pygbag usa el nombre de esta carpeta
FILES = ["main.py", "settings.py"]
FOLDERS = ["src", "data", "assets"]


def stage():
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(STAGE)
    for name in FILES:
        shutil.copy(os.path.join(ROOT, name), STAGE)
    for name in FOLDERS:
        shutil.copytree(os.path.join(ROOT, name), os.path.join(STAGE, name),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.wav", "*.md"))
    # el ícono de la pestaña del navegador
    icon = os.path.join(ROOT, "assets", "sprites", "player.png")
    if os.path.exists(icon):
        shutil.copy(icon, os.path.join(STAGE, "favicon.png"))

    ogg = [f for f in os.listdir(os.path.join(STAGE, "assets", "sounds")) if f.endswith(".ogg")]
    if not ogg:
        sys.exit("No hay archivos .ogg en assets/sounds. Corre primero: python tools/wav_to_ogg.py")
    print(f"Carpeta limpia lista en {STAGE}")


def main():
    args = set(sys.argv[1:])
    try:
        import pygbag  # noqa: F401
    except ImportError:
        sys.exit("Falta pygbag. Instálalo con:  pip install pygbag")

    stage()
    cmd = [sys.executable, "-m", "pygbag", "--app_name", "IT Survivor", "--title", "IT Survivor"]
    if args & {"--build", "--pages"}:
        cmd.append("--build")
    if "--archive" in args:
        cmd += ["--build", "--archive"]
    cmd.append(STAGE)
    print("Ejecutando:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

    web = os.path.join(STAGE, "build", "web")
    if not ("--archive" in args) and not os.path.exists(os.path.join(web, "index.html")):
        sys.exit("La construcción quedó incompleta: no se generó index.html.\n"
                 "Casi siempre es porque no pudo bajar la plantilla desde internet. "
                 "Revisa tu conexión y vuelve a correr el comando.")
    if "--pages" in args:
        docs = os.path.join(ROOT, "docs")
        shutil.rmtree(docs, ignore_errors=True)
        shutil.copytree(web, docs)
        open(os.path.join(docs, ".nojekyll"), "w").close()          # GitHub Pages: no procesar con Jekyll
        print(f"Listo: copié el juego web a {docs}")
        print("Ahora sube esa carpeta con git y activa GitHub Pages (ver README).")
    elif os.path.isdir(web):
        print(f"Listo: el juego web está en {web}")


if __name__ == "__main__":
    main()
