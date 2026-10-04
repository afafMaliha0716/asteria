import os
from typing import List

def get_sprite_manifest() -> List[str]:
    """Scans the assets directory and returns a list of all image filenames."""
    
    # 1. Get the directory where this script resides (e.g., Backend/assets)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Construct the target directory path (e.g., Backend/assets/images)
    # The image folder is a subdirectory of the script's location.
    assets_dir = os.path.join(base_dir, "images") 
    
    # 3. CRITICAL CHECK: Ensure the directory exists
    if not os.path.isdir(assets_dir):
        # Create the directory if it doesn't exist and return an empty list
        os.makedirs(assets_dir, exist_ok=True)
        return []

    image_files = []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    
    # 4. Walk through the directory and collect filenames
    for filename in os.listdir(assets_dir):
        # Use os.path.isfile to skip subdirectories within 'images' if any exist
        if os.path.isfile(os.path.join(assets_dir, filename)) and filename.lower().endswith(valid_extensions):
            image_files.append(filename)
            
    return image_files