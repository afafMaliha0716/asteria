"""
Checks that a generated game is real, runnable Python before we package it.

Two checks, cheapest first:
1. The code compiles.
2. The game starts and survives a few seconds headless (no window, no audio).

Returns None when the game is fine, or a short error message that can be fed
back to the model for another attempt.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

# Set ASTERIA_SMOKE_TEST=0 to skip actually running generated code on this machine.
SMOKE_TEST_ENABLED = os.getenv("ASTERIA_SMOKE_TEST", "1") != "0"
SMOKE_TEST_SECONDS = float(os.getenv("ASTERIA_SMOKE_TEST_SECONDS", "3"))


def check_syntax(code: str) -> Optional[str]:
    """Return an error message if the code is not valid Python."""
    if not code or not code.strip():
        return "The response contained no code."
    try:
        compile(code, "<generated game>", "exec")
    except SyntaxError as e:
        return f"SyntaxError on line {e.lineno}: {e.msg}"
    return None


def check_runs(code: str, assets_dir: Optional[str] = None,
               seconds: float = SMOKE_TEST_SECONDS) -> Optional[str]:
    """Run the game headless. A game that is still running after `seconds` passes."""
    workdir = tempfile.mkdtemp(prefix="asteria_check_")
    try:
        script = os.path.join(workdir, "game.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(code)
        if assets_dir and os.path.isdir(assets_dir):
            shutil.copytree(assets_dir, os.path.join(workdir, "assets"))

        env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        proc = subprocess.Popen(
            [sys.executable, script], cwd=workdir, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
        )
        try:
            _, stderr = proc.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            return None  # Still running: the game loop is alive.

        if proc.returncode != 0:
            tail = "\n".join((stderr or "").strip().splitlines()[-6:])
            return f"The game crashed on startup:\n{tail}"
        return ("The game exited immediately. It must start its game loop when run "
                "as a script (if __name__ == '__main__').")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def check_game_code(code: str, assets_dir: Optional[str] = None) -> Optional[str]:
    """Full check. Returns None if the game is good to package."""
    error = check_syntax(code)
    if error or not SMOKE_TEST_ENABLED:
        return error
    return check_runs(code, assets_dir)
