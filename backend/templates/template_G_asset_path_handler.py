# --- TEMPLATE: G_ASSET_PATH_HANDLER ---

import os
import sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller bundle.
    This function must be called every time a resource file (like an image) is loaded.
    
    CRITICAL NOTE: Assumes all assets are in a subfolder named 'assets' 
    next to the script in dev mode, and inside the bundle in compiled mode.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # We join the base path with the 'assets' subdirectory, then the relative path.
        base_path = sys._MEIPASS 
        return os.path.join(base_path, 'assets', relative_path)
        
    except Exception:
        # Not running as a compiled executable: look next to this script, not in the
        # folder the game was launched from, so the game runs from anywhere.
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'assets', relative_path)
    
# --- END TEMPLATE: G_ASSET_PATH_HANDLER ---