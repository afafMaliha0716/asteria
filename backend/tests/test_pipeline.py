"""End-to-end tests of the generation pipeline with a fake Gemini."""

import json
import os

import pytest

from agents.game_agents import AutonomousGameDirector, GameCreationAgent
from generators.gemini_generator import GeminiGameGenerator, extract_code
from generators.validator import check_game_code
from tests.fake_gemini import CRASHING_GAME, GOOD_GAME, SYNTAX_ERROR_GAME, FakeGemini


def make_agent(fake):
    agent = GameCreationAgent.__new__(GameCreationAgent)
    agent.generator = GeminiGameGenerator(client=fake)
    agent.created_games = []
    agent.current_game = None
    return agent


def test_happy_path_builds_a_game_that_runs(workdir):
    fake = FakeGemini()
    agent = make_agent(fake)

    package = agent.create_game_autonomously("a turtle on a beach")
    filepath = agent.save_game(package)

    assert package["concept"]["title"] == "Turtle Dash"
    assert os.path.isfile(filepath)
    # Only real library files are kept, and they are staged next to the game
    assert package["sprites"] == ["turtle.png", "apple.png"]
    assert os.path.isfile(workdir / "games" / "assets" / "turtle.png")
    # The saved game starts and loads its sprite
    saved = open(filepath, encoding="utf-8").read()
    assert check_game_code(saved, str(workdir / "games" / "assets")) is None

    metadata = json.load(open(filepath.replace(".py", "_metadata.json"), encoding="utf-8"))
    assert metadata["sprites"] == ["turtle.png", "apple.png"]


def test_model_gets_the_templates_and_the_sprite_list(workdir):
    fake = FakeGemini()
    make_agent(fake).create_game_autonomously("a turtle on a beach")

    prompt = fake.prompts("code")[0]
    assert "# --- TEMPLATE: C_MOVEMENT_PLATFORMER ---" in prompt
    assert "# --- TEMPLATE: G_ASSET_PATH_HANDLER ---" in prompt
    assert "turtle.png" in prompt and "not_a_real_file.png" not in prompt


def test_template_plan_always_has_core_templates_and_one_movement_style(workdir):
    fake = FakeGemini(plan=["B_MOVEMENT_TOPDOWN", "C_MOVEMENT_PLATFORMER", "MADE_UP"])
    package = make_agent(fake).create_game_autonomously("anything")

    plan = package["templates"]
    assert {"A_CORE_SETUP", "D_HEALTH_DAMAGE", "E_BASIC_COLLISION", "F_GAME_STATES", "G_ASSET_PATH_HANDLER"} <= set(plan)
    assert len([t for t in plan if "MOVEMENT" in t]) == 1
    assert "MADE_UP" not in plan


@pytest.mark.parametrize("bad_game", [SYNTAX_ERROR_GAME, CRASHING_GAME])
def test_broken_game_is_sent_back_and_fixed(workdir, bad_game):
    fake = FakeGemini(code_responses=[bad_game, GOOD_GAME])
    package = make_agent(fake).create_game_autonomously("a turtle on a beach")

    assert fake.count("code") == 2
    assert "previous attempt did not work" in fake.prompts("code")[1]
    assert "resource_path" in package["code"]


def test_game_that_never_works_falls_back_to_a_playable_game(workdir):
    fake = FakeGemini(code_responses=[CRASHING_GAME])
    agent = make_agent(fake)
    package = agent.create_game_autonomously("a turtle on a beach")

    assert "class Game" in package["code"]  # the built-in fallback game
    assert check_game_code(package["code"]) is None


def test_total_api_outage_still_produces_a_playable_game(workdir):
    fake = FakeGemini(fail=True)
    agent = make_agent(fake)
    package = agent.create_game_autonomously("space")
    filepath = agent.save_game(package)

    assert package["concept"]["title"].startswith("Adventure Quest")
    assert package["sprites"] == []
    assert check_game_code(open(filepath, encoding="utf-8").read()) is None


def test_missing_api_key_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiGameGenerator()


def test_models_can_be_swapped_with_environment_variables(monkeypatch, workdir):
    monkeypatch.setenv("ASTERIA_PLANNING_MODEL", "planner-x")
    monkeypatch.setenv("ASTERIA_CODING_MODEL", "coder-y")
    fake = FakeGemini()
    make_agent(fake).create_game_autonomously("anything")

    models_by_kind = {kind: model for kind, model, _ in fake.calls}
    assert models_by_kind["concept"] == "planner-x"
    assert models_by_kind["assets"] == "planner-x"
    assert models_by_kind["code"] == "coder-y"


def test_multi_level_game_saves_every_level(workdir):
    fake = FakeGemini()
    director = AutonomousGameDirector.__new__(AutonomousGameDirector)
    from agents.game_agents import AssetGenerationAgent, GameDesignAgent, LevelDesignAgent
    director.gemini = GeminiGameGenerator(client=fake)
    director.design_agent = GameDesignAgent(director.gemini)
    director.level_agent = LevelDesignAgent(director.gemini)
    director.asset_agent = AssetGenerationAgent(director.gemini)

    game = director.create_complete_game("beach", num_levels=2)
    game_dir = director.save_complete_game(game)

    assert os.path.isfile(os.path.join(game_dir, "main.py"))
    assert os.path.isfile(os.path.join(game_dir, "level_2.py"))
    assert os.path.isfile(os.path.join(game_dir, "metadata.json"))


@pytest.mark.parametrize("response, expected", [
    ("```python\nprint(1)\n```", "print(1)"),
    ("Sure!\n```python\nprint(1)\n```\nEnjoy.", "print(1)"),
    ("```\nprint(1)\n```", "print(1)"),
    ("print(1)", "print(1)"),
    ("```python\nprint(1)\n", "print(1)"),  # cut-off response with no closing fence
])
def test_extract_code_handles_messy_responses(response, expected):
    assert extract_code(response) == expected
