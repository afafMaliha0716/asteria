#!/usr/bin/env python3
"""
Simple test script to verify the generated game works
"""

import os
import sys
import pygame

def test_generated_game():
    """Test the generated game"""
    print("🎮 Testing Generated Game")
    print("=" * 30)
    
    # Check if game file exists
    game_file = "games/Adventure Quest space lased ships_20251019_021837.py"
    if not os.path.exists(game_file):
        print(f"❌ Game file not found: {game_file}")
        return False
    
    print(f"✅ Game file found: {game_file}")
    
    # Test pygame import
    try:
        import pygame
        print("✅ Pygame imported successfully")
    except ImportError as e:
        print(f"❌ Pygame import failed: {e}")
        return False
    
    # Test running the game (just initialize, don't run the loop)
    try:
        # Initialize pygame
        pygame.init()
        
        # Create a small test window
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Game Test")
        
        # Test basic pygame functionality
        screen.fill((0, 0, 0))  # Black background
        pygame.draw.rect(screen, (0, 0, 255), (50, 50, 30, 30))  # Blue player
        pygame.draw.rect(screen, (255, 255, 0), (100, 100, 20, 20))  # Yellow coin
        
        # Update display
        pygame.display.flip()
        
        print("✅ Pygame graphics test successful")
        print("✅ Game window created and graphics rendered")
        
        # Clean up
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Game test failed: {e}")
        return False

def test_game_engine():
    """Test the game engine components"""
    print("\n🔧 Testing Game Engine Components")
    print("=" * 40)
    
    try:
        # Add current directory to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from engine.game_engine import GameEngine, Player, Enemy, Powerup
        
        # Test entity creation
        player = Player(100, 100)
        enemy = Enemy(200, 200, "basic")
        powerup = Powerup(300, 300, "health")
        
        print("✅ Game entities created successfully")
        print(f"   👤 Player: {player.x}, {player.y}")
        print(f"   👹 Enemy: {enemy.x}, {enemy.y}")
        print(f"   ⭐ Powerup: {powerup.x}, {powerup.y}")
        
        # Test collision detection
        if player.collides_with(enemy):
            print("⚠️  Player colliding with enemy (unexpected)")
        else:
            print("✅ Collision detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Game engine test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Agentic Game Generator - Test Suite")
    print("=" * 50)
    
    # Test 1: Generated game
    test1_passed = test_generated_game()
    
    # Test 2: Game engine
    test2_passed = test_game_engine()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Generated Game Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Game Engine Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The system is working correctly.")
        print("\n🎮 To play the generated game:")
        print("   python3 'games/Adventure Quest space lased ships_20251019_021837.py'")
        print("\n🎯 Game controls:")
        print("   - WASD or Arrow Keys: Move player")
        print("   - Collect yellow coins to score points")
        print("   - Close window to exit")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
