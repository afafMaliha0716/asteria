import os
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

# Never open a real window or audio device during tests.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Run each test in an empty folder so generated games never land in the repo."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
