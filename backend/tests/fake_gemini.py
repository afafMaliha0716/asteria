"""A stand-in for the Gemini client so the whole pipeline can be tested without an API key."""

import json
from types import SimpleNamespace

CONCEPT = {
    "title": "Turtle Dash",
    "description": "Guide a turtle to the sea.",
    "genre": "adventure",
    "theme": "beach",
    "objective": "Reach the water",
    "mechanics": ["movement", "avoidance"],
    "enemies": [{"name": "Crab", "behavior": "patrols", "difficulty": "easy"}],
    "powerups": [{"name": "Shell", "effect": "restores health"}],
}

LEVEL = {
    "level_number": 1,
    "name": "The Beach",
    "size": {"width": 800, "height": 600},
    "enemies": [{"x": 350, "y": 250, "type": "basic"}],
    "difficulty": "easy",
}

ASSETS = {
    "player_sprite": "turtle.png",
    "enemies": {"basic": "SIMPLE_SHAPE, Red", "aggressive": "not_a_real_file.png"},
    "powerups": {"health": "apple.png"},
    "background_asset": "SIMPLE_SHAPE, Blue",
}

# A small but real game. It loads a sprite through resource_path, the same way a
# generated game does, and writes a marker file so tests can prove the sprite loaded.
GOOD_GAME = '''
import os
import sys
import pygame

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', relative_path)

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
player = pygame.transform.smoothscale(pygame.image.load(resource_path("turtle.png")), (48, 48))

marker = os.environ.get("ASTERIA_TEST_MARKER")
if marker:
    with open(marker, "w") as f:
        f.write("sprite loaded %dx%d" % player.get_size())

frames = 0
max_frames = int(os.environ.get("ASTERIA_TEST_FRAMES", "0"))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((20, 60, 120))
    screen.blit(player, (100, 100))
    pygame.display.flip()
    clock.tick(60)
    frames += 1
    if max_frames and frames >= max_frames:
        running = False
pygame.quit()
'''

SYNTAX_ERROR_GAME = "import pygame\ndef broken(:\n    pass\n"
CRASHING_GAME = "import pygame\npygame.init()\nraise RuntimeError('boom')\n"


class FakeGemini:
    """
    Answers each pipeline prompt with a canned response.

    code_responses: what to return for each successive code request (the last one repeats).
    fail: raise on every call, like an outage or a bad API key.
    """

    def __init__(self, code_responses=None, fail=False, plan=None):
        self.code_responses = list(code_responses or [GOOD_GAME])
        self.fail = fail
        self.plan = plan
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate)

    def _generate(self, model, contents):
        kind = self._kind(contents)
        self.calls.append((kind, model, contents))
        if self.fail:
            raise RuntimeError("API unavailable")
        if kind == "plan":
            plan = self.plan or ["A_CORE_SETUP", "C_MOVEMENT_PLATFORMER"]
            return SimpleNamespace(text="Here you go:\n```json\n" + json.dumps(plan) + "\n```")
        if kind == "concept":
            return SimpleNamespace(text="```json\n" + json.dumps(CONCEPT) + "\n```")
        if kind == "level":
            return SimpleNamespace(text=json.dumps(LEVEL))
        if kind == "assets":
            return SimpleNamespace(text=json.dumps(ASSETS))
        if kind == "code":
            index = min(self.count("code") - 1, len(self.code_responses) - 1)
            return SimpleNamespace(text="```python\n" + self.code_responses[index] + "\n```")
        return SimpleNamespace(text="{}")

    @staticmethod
    def _kind(prompt):
        if "specialized Pygame coder" in prompt:
            return "code"
        if "SPRITE LIBRARY" in prompt:
            return "assets"
        if "build system architect" in prompt:
            return "plan"
        if "expert game designer" in prompt:
            return "concept"
        if "design level" in prompt:
            return "level"
        return "other"

    def count(self, kind):
        return sum(1 for call in self.calls if call[0] == kind)

    def prompts(self, kind):
        return [call[2] for call in self.calls if call[0] == kind]
