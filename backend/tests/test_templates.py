"""The templates are the foundation every generated game is built on, so they must stay valid."""

import os

import pytest

from agents.game_agents import GameCreationAgent
from generators.validator import check_runs, check_syntax

TEMPLATE_IDS = [
    "A_CORE_SETUP",
    "B_MOVEMENT_TOPDOWN",
    "C_MOVEMENT_PLATFORMER",
    "D_HEALTH_DAMAGE",
    "E_BASIC_COLLISION",
    "F_GAME_STATES",
    "G_ASSET_PATH_HANDLER",
]


@pytest.mark.parametrize("template_id", TEMPLATE_IDS)
def test_template_exists_and_is_valid_python(template_id):
    code = GameCreationAgent._read_template_file(template_id)
    assert not code.startswith("# ERROR"), code
    assert check_syntax(code) is None


@pytest.mark.parametrize("template_id", [t for t in TEMPLATE_IDS if t != "G_ASSET_PATH_HANDLER"])
def test_template_runs_on_its_own(template_id):
    """Each gameplay template is a tiny runnable game. It should start and keep running."""
    code = GameCreationAgent._read_template_file(template_id)
    assert check_runs(code, seconds=2) is None


def test_stitching_includes_every_requested_template():
    stitched = GameCreationAgent.stitch_templates(TEMPLATE_IDS)
    for template_id in TEMPLATE_IDS:
        assert f"# --- TEMPLATE: {template_id} ---" in stitched
    assert "ERROR" not in stitched


def test_unknown_template_is_reported_not_raised():
    assert "not found" in GameCreationAgent._read_template_file("Z_DOES_NOT_EXIST")


def test_asset_path_helper_looks_next_to_the_script(tmp_path, monkeypatch):
    """The sprite bug: paths must not depend on the folder the game is launched from."""
    code = GameCreationAgent._read_template_file("G_ASSET_PATH_HANDLER")
    script = tmp_path / "game" / "helper.py"
    script.parent.mkdir()
    script.write_text(code, encoding="utf-8")

    namespace = {"__file__": str(script)}
    exec(compile(code, str(script), "exec"), namespace)

    monkeypatch.chdir(tmp_path)  # launched from somewhere else
    expected = os.path.join(str(script.parent), "assets", "turtle.png")
    assert namespace["resource_path"]("turtle.png") == expected

    # Inside a PyInstaller bundle the files live under sys._MEIPASS
    import sys
    monkeypatch.setattr(sys, "_MEIPASS", "/bundle", raising=False)
    assert namespace["resource_path"]("turtle.png") == os.path.join("/bundle", "assets", "turtle.png")
