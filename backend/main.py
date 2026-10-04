"""
Main Interface for Agentic Game Generator
Command-line interface and Web Server for creating and managing AI-generated games.
"""

import os
import sys
import argparse
import json
from typing import Optional
import logging
import uvicorn
import uuid
import subprocess
import shutil
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables from the .env file in the same directory as main.py
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.game_agents import AutonomousGameDirector, GameCreationAgent
from generators.gemini_generator import GeminiGameGenerator
from engine.game_engine import GameEngine

# --- Web Server Setup (FastAPI) ---

app = FastAPI()

# In-memory storage for task statuses
# For a production application, you would use a more robust solution like Redis or a database.
tasks = {}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class GameSettings(BaseModel):
    horrorLevel: int
    puzzleComplexity: int
    ageGroup: int
    speedChaos: int

class GenerationRequest(BaseModel):
    worldDescription: str
    uploadedImage: Optional[str] = None
    imageDescription: str
    imageCategory: str
    gameMode: str
    settings: GameSettings

import subprocess
import shutil

def run_game_generation(task_id: str, request: GenerationRequest):
    """The actual game generation logic that runs in the background."""
    logger.info(f"[{task_id}] Starting game generation...")
    tasks[task_id] = {'status': 'IN_PROGRESS', 'result': None}
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not found on the server.")

        creation_agent = GameCreationAgent(api_key)
        theme = request.worldDescription
        if request.imageDescription:
            theme += f" with an image of {request.imageDescription}"

        logger.info(f"[{task_id}] Generating game package...")
        game_package = creation_agent.create_game_autonomously(theme)
        filepath = creation_agent.save_game(game_package)
        logger.info(f"[{task_id}] Game package saved to {filepath}")
        
        # --- Create Executable ---
        logger.info(f"[{task_id}] Starting packaging process...")
        tasks[task_id]['status'] = 'PACKAGING'
        game_filename = os.path.basename(filepath)
        game_name = os.path.splitext(game_filename)[0]
        
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        pyinstaller_exe_path = os.path.expanduser("~/AppData/Roaming/Python/Python312/Scripts/pyinstaller.exe")
        if not os.path.exists(pyinstaller_exe_path):
            pyinstaller_exe_path = "pyinstaller"

        pyinstaller_command = [
            pyinstaller_exe_path,
            "--onefile",
            "--name", game_name,
            "--distpath", os.path.join(backend_dir, "dist"),
            "--workpath", os.path.join(backend_dir, "build"),
            "--specpath", os.path.join(backend_dir, "spec"),
            os.path.abspath(filepath)  # Use absolute path here
        ]

        process = subprocess.run(pyinstaller_command, capture_output=True, encoding="utf-8", text=True, cwd=backend_dir)
        logger.info(f"[{task_id}] PyInstaller finished.")

        if process.returncode != 0:
            logger.error(f"[{task_id}] PyInstaller failed: {process.stderr}")
            raise Exception(f"PyInstaller failed: {process.stderr}")

        exe_filename = f"{game_name}.exe"
        dist_path = os.path.join(backend_dir, "dist", exe_filename)
        final_exe_path = os.path.join(backend_dir, "games", exe_filename)

        shutil.move(dist_path, final_exe_path)

        # exe_filename_only = os.path.basename(final_exe_path)
        # result = {
        #     "message": "Game generated and packaged successfully!",
        #     "title": game_package.get('concept', {}).get('title', 'Unknown'),
        #     "description": game_package.get('concept', {}).get('description', 'Unknown'),
        #     "python_script": exe_filename_only,
        #     "executable_file": final_exe_path 
        # }
        # tasks[task_id] = {'status': 'SUCCESS', 'result': result}
        exe_filename_only = os.path.basename(final_exe_path)

        result = {
            "message": "Game generated and packaged successfully!",
            "title": game_package.get('concept', {}).get('title', 'Unknown'),
            "description": game_package.get('concept', {}).get('description', 'Unknown'),
            "python_script": exe_filename_only, 
            "executable_file": exe_filename_only
        }
        tasks[task_id] = {'status': 'SUCCESS', 'result': result}
        logger.info(f"[{task_id}] Game generation successful.")

    except Exception as e:
        logger.error(f"Error during game generation for task {task_id}: {e}")
        tasks[task_id] = {'status': 'FAILURE', 'result': {'error': str(e)}}

@app.post("/api/generate/start")
async def start_generation_endpoint(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Starts the game generation as a background task and returns a task ID.
    """
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'PENDING', 'result': None}
    background_tasks.add_task(run_game_generation, task_id, request)
    
    return {"task_id": task_id}

@app.get("/api/generate/status/{task_id}")
async def get_generation_status(task_id: str):
    """
    Checks the status of a game generation task.
    """
    task = tasks.get(task_id)
    if not task:
        return {"error": "Task not found."}
    return task


@app.get("/api/game/{game_filename}")
async def download_game_file(game_filename: str):
    """
    Serves the generated game file for download.
    """
    games_dir = "games"
    game_filename = os.path.basename(game_filename)
    filepath = os.path.join(games_dir, game_filename)
    
    if os.path.exists(filepath):
        return FileResponse(path=filepath, media_type='application/octet-stream', filename=game_filename)
    
    return {"error": "File not found."}


@app.get("/api/game/download/{game_filename}")
async def download_executable_file(game_filename: str):
    # Get the absolute path of the directory where main.py is running
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # CRITICAL: Construct the full absolute path to the file in the 'games' folder
    games_dir = "games"
    filepath = os.path.join(backend_dir, games_dir, os.path.basename(game_filename))
    
    # DEBUG: Log the exact path being checked
    logger.info(f"Checking for file at: {filepath}")
    
    # Check for file existence
    if os.path.exists(filepath):
        logger.info(f"File FOUND. Serving: {game_filename}")
        return FileResponse(
            path=filepath, 
            media_type='application/vnd.microsoft.portable-executable', 
            filename=game_filename
        )
    
    logger.error(f"File NOT found: {filepath}")
    return {"error": "File not found."}

# --- Existing CLI Code ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GameGeneratorCLI:
    """Command-line interface for the game generator"""
    
    def __init__(self):
        self.director = None
        self.api_key = None
        
    def setup_api_key(self, api_key: Optional[str] = None):
        """Setup Gemini API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("Error: Gemini API key not found!")
            print("Please set the GEMINI_API_KEY environment variable or provide it as an argument.")
            print("You can get an API key from: https://makersuite.google.com/app/apikey")
            return False
        
        try:
            self.director = AutonomousGameDirector(self.api_key)
            print("✓ Gemini API key configured successfully")
            return True
        except Exception as e:
            print(f"Error setting up API key: {e}")
            return False
    
    def create_simple_game(self, theme: str = None):
        """Create a simple single-level game"""
        print(f"\n🎮 Creating simple game with theme: {theme or 'Random'}")
        
        if not self.director:
            print("Error: API key not configured")
            return
        
        try:
            # Use the creation agent for simple games
            creation_agent = GameCreationAgent(self.api_key)
            game_package = creation_agent.create_game_autonomously(theme)
            
            # Save the game
            filepath = creation_agent.save_game(game_package)
            
            print(f"✓ Game created successfully!")
            print(f"📁 Saved to: {filepath}")
            print(f"🎯 Game: {game_package['concept']['title']}")
            print(f"📝 Description: {game_package['concept']['description']}")
            
            # Ask if user wants to run the game
            if input("\n🚀 Run the game now? (y/n): ").lower().startswith('y'):
                self.run_game(filepath)
                
        except Exception as e:
            print(f"❌ Error creating game: {e}")
            logger.error(f"Error creating simple game: {e}")
    
    def create_complete_game(self, theme: str = None, num_levels: int = 3):
        """Create a complete multi-level game"""
        print(f"\n🎮 Creating complete game with theme: {theme or 'Random'}")
        print(f"📊 Levels: {num_levels}")
        
        if not self.director:
            print("Error: API key not configured")
            return
        
        try:
            complete_game = self.director.create_complete_game(theme, num_levels)
            
            # Save the complete game
            game_dir = self.director.save_complete_game(complete_game)
            
            print(f"✓ Complete game created successfully!")
            print(f"📁 Saved to: {game_dir}")
            print(f"🎯 Game: {complete_game['concept']['title']}")
            print(f"📝 Description: {complete_game['concept']['description']}")
            print(f"📊 Analysis: {complete_game['analysis']['analysis']}")
            print(f"🎨 Style: {complete_game['style_guide']['art_style']}")
            
            # Ask if user wants to run the game
            if input("\n🚀 Run the main game now? (y/n): ").lower().startswith('y'):
                main_game_path = os.path.join(game_dir, "main.py")
                self.run_game(main_game_path)
                
        except Exception as e:
            print(f"❌ Error creating complete game: {e}")
            logger.error(f"Error creating complete game: {e}")
    
    def run_game(self, filepath: str):
        """Run a generated game"""
        print(f"\n🚀 Running game: {filepath}")
        
        try:
            # Import and run the game
            import importlib.util
            spec = importlib.util.spec_from_file_location("generated_game", filepath)
            game_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(game_module)
            
        except Exception as e:
            print(f"❌ Error running game: {e}")
            logger.error(f"Error running game: {e}")
            print("💡 Try running the game manually with: python " + filepath)
    
    def list_games(self):
        """List all generated games"""
        games_dir = "games"
        if not os.path.exists(games_dir):
            print("📁 No games directory found. Create some games first!")
            return
        
        print(f"\n📁 Generated Games in {games_dir}:")
        print("-" * 50)
        
        game_files = []
        for filename in os.listdir(games_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(games_dir, filename)
                metadata_path = filepath.replace('.py', '_metadata.json')
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        title = metadata.get('concept', {}).get('title', 'Unknown')
                        created_at = metadata.get('created_at', 'Unknown')
                        print(f"🎮 {title}")
                        print(f"   📁 {filename}")
                        print(f"   📅 {created_at}")
                        print()
                    except Exception as e:
                        print(f"📄 {filename} (metadata error)")
                else:
                    print(f"📄 {filename}")
        
        if not game_files:
            print("No games found. Create some games first!")
    
    def interactive_mode(self):
        """Interactive mode for game creation"""
        print("\n🎮 Welcome to the Agentic Game Generator!")
        print("=" * 50)
        
        while True:
            print("\nChoose an option:")
            print("1. Create simple game")
            print("2. Create complete multi-level game")
            print("3. List generated games")
            print("4. Run a specific game")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                theme = input("Enter game theme (or press Enter for random): ").strip()
                theme = theme if theme else None
                self.create_simple_game(theme)
            
            elif choice == '2':
                theme = input("Enter game theme (or press Enter for random): ").strip()
                theme = theme if theme else None
                
                try:
                    num_levels = int(input("Number of levels (default 3): ") or "3")
                except ValueError:
                    num_levels = 3
                
                self.create_complete_game(theme, num_levels)
            
            elif choice == '3':
                self.list_games()
            
            elif choice == '4':
                filepath = input("Enter game file path: ").strip()
                if os.path.exists(filepath):
                    self.run_game(filepath)
                else:
                    print("❌ File not found!")
            
            elif choice == '5':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

def main_cli():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Agentic Game Generator with Gemini AI")
    parser.add_argument("--api-key", help="Gemini API key")
    parser.add_argument("--theme", help="Game theme")
    parser.add_argument("--levels", type=int, default=3, help="Number of levels for complete game")
    parser.add_argument("--simple", action="store_true", help="Create simple single-level game")
    parser.add_argument("--complete", action="store_true", help="Create complete multi-level game")
    parser.add_argument("--list", action="store_true", help="List generated games")
    parser.add_argument("--run", help="Run a specific game file")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--server", action="store_true", help="Run the FastAPI web server")
    
    args = parser.parse_args()
    
    if args.server:
        print("🚀 Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return 0

    cli = GameGeneratorCLI()
    
    # Setup API key
    if not cli.setup_api_key(args.api_key):
        return 1
    
    # Handle command line arguments
    if args.list:
        cli.list_games()
    elif args.run:
        cli.run_game(args.run)
    elif args.simple:
        cli.create_simple_game(args.theme)
    elif args.complete:
        cli.create_complete_game(args.theme, args.levels)
    elif args.interactive:
        cli.interactive_mode()
    else:
        # Default to interactive mode
        cli.interactive_mode()
    
    return 0

if __name__ == "__main__":
    sys.exit(main_cli())
