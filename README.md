# IT Survivor

Videojuego arcade de supervivencia donde sobrevives a los fallos de TI (bugs, errores 500, bases de datos corruptas y entregas con deadline) y **aprendes en el camino**: retos de preguntas, mejoras que son buenas prácticas de desarrollo, una Bugpedia con los errores reales y un resumen de lo que dominas al terminar.

Proyecto de la materia **Diseño de la Interacción**, BUAP.
Equipo: Luis Antonio Nani Herrera, Braulio Emilio Marrón Pérez, Cristhian Rios Hernández y Paulo Ivan Gasparillo Morales.

## Cómo correrlo

Requiere Python 3.12 o superior.

```bat
git clone https://github.com/NaniClay/IT-Survivor.git
cd IT-Survivor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Versión para navegador

El juego también corre en el navegador (Python compilado a WebAssembly con [pygbag](https://github.com/pygame-web/pygbag)), sin instalar nada.

**Probarlo en tu compu** (necesita internet la primera vez, para bajar el motor de Python del navegador):

```bat
pip install pygbag
python tools/build_web.py
```

Abre `http://localhost:8000` en Chrome o Edge. Haz clic en la página para empezar (los navegadores no dejan sonar nada antes del primer clic).

**Publicarlo con GitHub Pages** (para compartir un link):

```bat
python tools/build_web.py --pages
git add docs
git commit -m "Version web"
git push
```

Luego, en GitHub: *Settings → Pages → Build and deployment → Source: Deploy from a branch*, elige tu rama y la carpeta `/docs`, y guarda. El link queda como `https://<tu-usuario>.github.io/IT-Survivor/` (tarda 1 a 2 minutos en activarse).

**Alternativa, itch.io:** `python tools/build_web.py --archive` genera un `web.zip` que se sube como proyecto de tipo HTML.

Diferencias en el navegador: no hay "Salir" ni `F11` (la página ya ocupa todo el espacio y el navegador tiene su propia pantalla completa), el sonido usa los OGG, y el top 5 y el progreso se guardan en el almacenamiento del navegador (`localStorage`); si el navegador no lo permite, duran solo mientras la pestaña esté abierta.

## Controles

| Tecla | Acción |
|---|---|
| `W` `A` `S` `D` | Moverte (el disparo es automático) |
| `ESPACIO` | Coffee Boost: más velocidad y cadencia |
| `G` | Git Rollback: regresas a donde estabas hace ~5 s |
| `E` | Refactorizar: onda que limpia a los enemigos cercanos |
| `1` `2` `3` `4` | Responder retos y elegir mejoras |
| `ENTER` | Continuar / confirmar |
| `ESC` | Pausa |
| `TAB` | Cambiar de vista en la pantalla final |
| `M` | Silencio |
| `F11` | Pantalla completa (la ventana también se puede agrandar) |

## Qué se aprende

- **Retos "Stack Overflow"**: cada ~60 s el juego se pausa y sale una pregunta de HTTP, SQL, depuración o Git y proyectos. Si aciertas te curas y se recarga una habilidad. Si fallas, el enemigo de ese tema aparece más (dificultad adaptativa).
- **Mejoras = buenas prácticas**: cada ~30 s eliges 1 de 3 (tests unitarios, CI/CD, arquitectura modular, code review, backups, commits frecuentes, refactorización, descanso y sprints). Cada una explica por qué importa.
- **Bugpedia**: cada enemigo nuevo trae su ficha (qué es, por qué pasa, cómo se arregla).
- **Resumen de aprendizaje**: al terminar, `TAB` muestra aciertos por tema y qué repasar.

## Estructura

```
main.py            punto de entrada (escritorio y navegador)
settings.py        TODO el balance y los tiempos del juego
src/               game.py (bucle y estados), jugador, enemigos, armas, habilidades, mejoras,
                   aprendizaje, interfaz, audio, tipografía y almacenamiento
data/              questions.json (preguntas) y bugpedia.json (fichas)
assets/sprites/    texturas
assets/sounds/     efectos y música (WAV para escritorio, OGG para el navegador)
assets/fonts/      tipografía DejaVu Sans Mono (licencia incluida)
tools/             generadores de sprites y sonidos, conversor a OGG y empaquetador web
tests/             pruebas de funcionalidad automáticas
```

## Ajustar y ampliar

- **Balance**: todo está en `settings.py` (vida, velocidad, cadencia, cada cuánto salen retos y mejoras, curva de dificultad).
- **Más preguntas**: copia un bloque de `data/questions.json`. `answer` es el índice de la opción correcta (0 a 3); el juego baraja las opciones solo.
- **Arte y sonido finales**: reemplaza los PNG de `assets/sprites/` o los WAV de `assets/sounds/` conservando el nombre (y el tamaño, en el caso de los sprites).
- **Regenerar las texturas o los sonidos de relleno**: `python tools/generate_sprites.py` (requiere `pip install pillow`) y `python tools/generate_sounds.py` (después, `pip install soundfile` y `python tools/wav_to_ogg.py` para crear los OGG del navegador).

## Pruebas

```bat
python tests/run_tests.py
```

Corre 36 pruebas de funcionalidad sin abrir ventana ni hacer ruido, imprime una tabla y guarda `tests/resultados.md`.
Con `python tests/run_tests.py --web` repite las mismas pruebas simulando el modo navegador (guarda `tests/resultados_web.md`).

## Datos locales

El juego guarda `leaderboard.json` (top 5) y `learning_progress.json` (aciertos por tema y registro de partidas) en la carpeta del proyecto. No se suben a git.
