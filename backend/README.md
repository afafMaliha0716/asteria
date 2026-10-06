# Asteria backend

Python and FastAPI. See the [main README](../README.md) for what Asteria does
and how to run the whole app.

## Layout

```
main.py                         API server and command-line interface
check_setup.py                  Confirms your API key, models, and PyInstaller work
agents/game_agents.py           Design, level, asset, and creation agents
generators/gemini_generator.py  Gemini prompts, response parsing, retries, fallbacks
generators/validator.py         Compiles and test-runs each generated game
engine/game_engine.py           Pygame engine: entities, collision, game states
templates/                      Seven tested building blocks every game starts from
assets/images/                  Sprite library the asset agent picks from
tests/                          Test suite (runs without an API key)
```

## The templates

| Template | What it provides |
|----------|------------------|
| `A_CORE_SETUP` | Window, clock, and main loop |
| `B_MOVEMENT_TOPDOWN` | Free movement on both axes |
| `C_MOVEMENT_PLATFORMER` | Gravity, jumping, and ground collision |
| `D_HEALTH_DAMAGE` | Health, damage, healing, and a health bar |
| `E_BASIC_COLLISION` | Collision with walls, resolved per axis |
| `F_GAME_STATES` | Menu, playing, and game over screens |
| `G_ASSET_PATH_HANDLER` | Finds sprites both in development and inside a packaged executable |

A planning model picks top-down or platformer movement. The other five are
always included. Each gameplay template is a small game that runs on its own:

```bash
python templates/template_C_movement_platformer.py
```

## Command line

```bash
python main.py --server                              # API on http://localhost:8000
python main.py --simple --theme "Space Adventure"    # one game, saved to games/
python main.py --complete --theme "Fantasy Quest" --levels 3
python main.py --list
python main.py --run "games/<file>.py"
python main.py --interactive
```

## Configuration

Set these in `backend/.env` (see `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `GEMINI_API_KEY` | none | Required |
| `ASTERIA_PLANNING_MODEL` | `gemini-3.5-flash-lite` | Concepts, levels, template and sprite choices |
| `ASTERIA_CODING_MODEL` | `gemini-3.8-flash` | Writes the game code |
| `ASTERIA_SMOKE_TEST` | `1` | Set to `0` to skip test-running generated games |

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

The tests swap Gemini for a fake, so they need no API key. They cover the
templates, the retry and fallback paths, and the full web flow: generate,
package with PyInstaller, download, and run the packaged game to confirm its
sprite loads. That last test takes about a minute.
