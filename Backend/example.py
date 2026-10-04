#!/usr/bin/env python3
"""
Example script demonstrating the Agentic Game Generator
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.game_agents import AutonomousGameDirector
from templates.game_templates import TemplateManager, get_random_theme
from assets.asset_generator import AssetGenerator

def example_simple_game():
    """Example of creating a simple game"""
    print("🎮 Creating a simple game example...")
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    try:
        # Create game director
        director = AutonomousGameDirector(api_key)
        
        # Generate a simple game
        theme = get_random_theme("fantasy")
        print(f"🎨 Theme: {theme}")
        
        game_package = director.creation_agent.create_game_autonomously(theme)
        
        # Save the game
        filepath = director.creation_agent.save_game(game_package)
        
        print(f"✅ Game created: {game_package['concept']['title']}")
        print(f"📁 Saved to: {filepath}")
        print(f"📝 Description: {game_package['concept']['description']}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_template_game():
    """Example of creating a game from template"""
    print("🎮 Creating a template-based game...")
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Get available templates
    templates = template_manager.list_templates()
    print(f"📋 Available templates: {', '.join(templates)}")
    
    # Generate game from adventure template
    theme = get_random_theme("fantasy")
    print(f"🎨 Theme: {theme}")
    
    try:
        game_data = template_manager.generate_game_from_template("adventure", theme, 2)
        
        print(f"✅ Template game created: {game_data['concept']['title']}")
        print(f"📊 Levels: {game_data['num_levels']}")
        print(f"📝 Description: {game_data['concept']['description']}")
        
        return game_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_asset_generation():
    """Example of generating game assets"""
    print("🎨 Generating game assets...")
    
    try:
        # Create asset generator
        asset_gen = AssetGenerator()
        
        # Generate assets for fantasy theme
        theme = "fantasy"
        
        # Generate individual sprites
        player_sprite = asset_gen.generate_player_sprite(theme)
        enemy_sprite = asset_gen.generate_enemy_sprite("basic", theme)
        powerup_sprite = asset_gen.generate_powerup_sprite("health", theme)
        background = asset_gen.generate_background(theme)
        
        print(f"✅ Assets generated:")
        print(f"   👤 Player: {player_sprite}")
        print(f"   👹 Enemy: {enemy_sprite}")
        print(f"   ⭐ Powerup: {powerup_sprite}")
        print(f"   🖼️ Background: {background}")
        
        return {
            "player": player_sprite,
            "enemy": enemy_sprite,
            "powerup": powerup_sprite,
            "background": background
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_complete_game():
    """Example of creating a complete multi-level game"""
    print("🎮 Creating a complete multi-level game...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    try:
        # Create game director
        director = AutonomousGameDirector(api_key)
        
        # Generate complete game
        theme = get_random_theme("sci-fi")
        print(f"🎨 Theme: {theme}")
        
        complete_game = director.create_complete_game(theme, 3)
        
        # Save complete game
        game_dir = director.save_complete_game(complete_game)
        
        print(f"✅ Complete game created: {complete_game['concept']['title']}")
        print(f"📁 Saved to: {game_dir}")
        print(f"📊 Levels: {complete_game['num_levels']}")
        print(f"📝 Description: {complete_game['concept']['description']}")
        print(f"🎯 Analysis: {complete_game['analysis']['analysis']}")
        
        return game_dir
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all examples"""
    print("🚀 Agentic Game Generator Examples")
    print("=" * 50)
    
    # Example 1: Simple game
    print("\n1️⃣ Simple Game Example")
    simple_game = example_simple_game()
    
    # Example 2: Template game
    print("\n2️⃣ Template Game Example")
    template_game = example_template_game()
    
    # Example 3: Asset generation
    print("\n3️⃣ Asset Generation Example")
    assets = example_asset_generation()
    
    # Example 4: Complete game (requires API key)
    print("\n4️⃣ Complete Game Example")
    complete_game = example_complete_game()
    
    print("\n🎉 Examples completed!")
    print("\nTo run the full interactive mode:")
    print("python main.py --interactive")

if __name__ == "__main__":
    main()
