"""
Checks that this machine can run Asteria, without generating a whole game.

    python check_setup.py

It confirms the API key is set, that both Gemini models answer, and that
PyInstaller is installed. Each failure says what to do about it.
"""

import importlib.util
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from generators.gemini_generator import GeminiGameGenerator  # noqa: E402


def main() -> int:
    ok = True

    key = os.getenv("GEMINI_API_KEY", "")
    if not key or key == "your_api_key_here":
        print("FAIL  GEMINI_API_KEY is not set.")
        print("      Copy .env.example to .env and paste a key from https://aistudio.google.com/app/apikey")
        return 1
    print("ok    GEMINI_API_KEY is set")

    generator = GeminiGameGenerator(key)
    for role, model in (("planning", generator.planning_model), ("coding", generator.coding_model)):
        try:
            reply = model.generate_content("Reply with the single word: ready").text
            print(f"ok    {role} model {model.name} answered: {reply.strip()[:40]}")
        except Exception as e:
            ok = False
            print(f"FAIL  {role} model {model.name}: {str(e)[:300]}")
            print(f"      If the key is valid, the model may be retired or not on your plan. Pick another one")
            print(f"      by setting ASTERIA_{role.upper()}_MODEL in .env. Models your key can use:")
            try:
                names = sorted(m.name.replace("models/", "") for m in generator.client.models.list())
                print("      " + ", ".join(n for n in names if "gemini" in n and "flash" in n)[:600])
            except Exception as list_error:
                print(f"      (could not list models: {str(list_error)[:200]})")

    if importlib.util.find_spec("PyInstaller") is None:
        ok = False
        print("FAIL  PyInstaller is not installed. Run: pip install -r requirements.txt")
    else:
        print("ok    PyInstaller is installed")

    print("\nAll good. Start the server with: python main.py --server" if ok else "\nFix the items marked FAIL, then run this again.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
