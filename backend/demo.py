#!/usr/bin/env python3
"""
Demo script for the Agentic Game Generator
Creates a simple game without requiring Gemini API key
"""

import os
import sys
import pygame

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from templates.game_templates import TemplateManager, get_random_theme
from engine.game_engine import GameEngine

def create_demo_game():
    """Create a demo game using templates (no API key required)"""
    print("🎮 Creating demo game using templates...")
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Get available templates
    templates = template_manager.list_templates()
    print(f"📋 Available templates: {', '.join(templates)}")
    
    # Generate game from adventure template
    theme = get_random_theme("fantasy")
    print(f"🎨 Theme: {theme}")
    
    try:
        game_data = template_manager.generate_game_from_template("adventure", theme, 1)
        
        print(f"✅ Demo game created: {game_data['concept']['title']}")
        print(f"📝 Description: {game_data['concept']['description']}")
        
        return game_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def run_demo_game(game_data):
    """Run the demo game"""
    if not game_data:
        print("❌ No game data to run")
        return
    
    print("🚀 Starting demo game...")
    print("Controls: WASD or Arrow Keys to move")
    print("Objective: Collect all treasures!")
    print("Press ESC to pause, Close window to exit")
    
    try:
        # Create game engine
        engine = GameEngine(
            width=game_data['levels'][0]['size']['width'],
            height=game_data['levels'][0]['size']['height'],
            title=game_data['concept']['title']
        )
        
        # Load the level
        engine.load_level(game_data['levels'][0])
        
        # Run the game
        engine.run()
        
    except Exception as e:
        print(f"❌ Error running game: {e}")
        print("💡 Make sure pygame is installed: pip install pygame")

def main():
    """Main demo function"""
    print("🎮 Agentic Game Generator - Demo Mode")
    print("=" * 50)
    print("This demo creates a game using templates (no API key required)")
    print()
    
    # Create demo game
    game_data = create_demo_game()
    
    if game_data:
        # Ask if user wants to run the game
        response = input("\n🚀 Run the demo game now? (y/n): ").lower()
        if response.startswith('y'):
            run_demo_game(game_data)
        else:
            print("Demo game created but not run.")
            print("To run it manually, use the game engine with the generated data.")
    else:
        print("❌ Failed to create demo game")

if __name__ == "__main__":
    main()
