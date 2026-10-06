"""
The full web flow: start a job, poll it, download the packaged game, and run it.

This really runs PyInstaller, so it takes about a minute.
"""

import os
import stat
import subprocess

import pytest
from fastapi.testclient import TestClient

import main
from tests.fake_gemini import FakeGemini
from tests.test_pipeline import make_agent

REQUEST = {
    "worldDescription": "a turtle on a beach",
    "imageDescription": "",
    "imageCategory": "",
    "gameMode": "adventure",
    "settings": {"horrorLevel": 1, "puzzleComplexity": 2, "ageGroup": 3, "speedChaos": 4},
}


@pytest.fixture
def client(workdir, monkeypatch):
    # Keep every generated file inside the temporary folder
    monkeypatch.setattr(main, "__file__", str(workdir / "main.py"))
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    return TestClient(main.app)


def test_generate_package_download_and_play(client, workdir, monkeypatch):
    monkeypatch.setattr(main, "GameCreationAgent", lambda api_key: make_agent(FakeGemini()))

    task_id = client.post("/api/generate/start", json=REQUEST).json()["task_id"]
    status = client.get(f"/api/generate/status/{task_id}").json()
    assert status["status"] == "SUCCESS", status
    assert status["result"]["title"] == "Turtle Dash"

    filename = status["result"]["executable_file"]
    download = client.get(f"/api/game/download/{filename}")
    assert download.status_code == 200
    assert len(download.content) > 1_000_000  # a real bundled executable

    # Play the downloaded game from an unrelated folder, the way a user would.
    # This is the packaging bug from the hackathon: the sprite must load from inside the bundle.
    elsewhere = workdir / "downloads"
    elsewhere.mkdir()
    game = elsewhere / filename
    game.write_bytes(download.content)
    game.chmod(game.stat().st_mode | stat.S_IEXEC)
    marker = elsewhere / "marker.txt"

    env = dict(os.environ, ASTERIA_TEST_MARKER=str(marker), ASTERIA_TEST_FRAMES="5",
               SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    result = subprocess.run([str(game)], cwd=elsewhere, env=env, capture_output=True, text=True, timeout=120)

    assert result.returncode == 0, result.stderr
    assert marker.read_text() == "sprite loaded 48x48"


def test_missing_api_key_fails_the_job_with_a_clear_message(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY")
    task_id = client.post("/api/generate/start", json=REQUEST).json()["task_id"]
    status = client.get(f"/api/generate/status/{task_id}").json()
    assert status["status"] == "FAILURE"
    assert "API key" in status["result"]["error"]


def test_unknown_task_and_missing_file(client):
    assert "error" in client.get("/api/generate/status/nope").json()
    assert "error" in client.get("/api/game/download/nope.exe").json()


def test_download_cannot_escape_the_games_folder(client, workdir):
    (workdir / "secret.txt").write_text("secret")
    response = client.get("/api/game/download/..%2Fsecret.txt")
    assert "secret" not in response.text
