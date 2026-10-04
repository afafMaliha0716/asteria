"""
Basic Asset Generation System
Creates simple visual assets for games using pygame and basic shapes
"""

import pygame
import os
import json
import random
from typing import Dict, List, Any, Tuple, Optional
from PIL import Image, ImageDraw
import numpy as np

class AssetGenerator:
    """Generates basic visual assets for games"""
    
    def __init__(self):
        self.assets_dir = "assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Color palettes for different themes
        self.color_palettes = {
            "fantasy": {
                "primary": (100, 50, 200),      # Purple
                "secondary": (50, 150, 50),     # Green
                "accent": (255, 215, 0),        # Gold
                "background": (20, 20, 40),     # Dark blue
                "text": (255, 255, 255)         # White
            },
            "sci-fi": {
                "primary": (0, 255, 255),       # Cyan
                "secondary": (255, 0, 255),      # Magenta
                "accent": (255, 255, 0),        # Yellow
                "background": (10, 10, 30),     # Dark blue
                "text": (255, 255, 255)         # White
            },
            "horror": {
                "primary": (139, 0, 0),         # Dark red
                "secondary": (75, 0, 130),       # Indigo
                "accent": (255, 140, 0),        # Dark orange
                "background": (0, 0, 0),        # Black
                "text": (255, 255, 255)         # White
            },
            "nature": {
                "primary": (34, 139, 34),       # Forest green
                "secondary": (255, 165, 0),      # Orange
                "accent": (255, 215, 0),        # Gold
                "background": (135, 206, 235),  # Sky blue
                "text": (0, 0, 0)               # Black
            },
            "urban": {
                "primary": (128, 128, 128),     # Gray
                "secondary": (255, 0, 0),       # Red
                "accent": (0, 0, 255),          # Blue
                "background": (50, 50, 50),     # Dark gray
                "text": (255, 255, 255)         # White
            }
        }
    
    def generate_player_sprite(self, theme: str = "fantasy", size: Tuple[int, int] = (32, 32)) -> str:
        """Generate a player sprite"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        # Create surface
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Draw player as a simple character
        center_x, center_y = size[0] // 2, size[1] // 2
        
        # Body (circle)
        pygame.draw.circle(surface, palette["primary"], (center_x, center_y), size[0] // 3)
        
        # Head (smaller circle)
        pygame.draw.circle(surface, palette["secondary"], (center_x, center_y - 4), size[0] // 4)
        
        # Eyes
        pygame.draw.circle(surface, palette["text"], (center_x - 3, center_y - 6), 2)
        pygame.draw.circle(surface, palette["text"], (center_x + 3, center_y - 6), 2)
        
        # Save sprite
        filename = f"player_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_enemy_sprite(self, enemy_type: str, theme: str = "fantasy", size: Tuple[int, int] = (24, 24)) -> str:
        """Generate an enemy sprite"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center_x, center_y = size[0] // 2, size[1] // 2
        
        if enemy_type == "basic":
            # Simple square enemy
            pygame.draw.rect(surface, palette["primary"], 
                           (center_x - 8, center_y - 8, 16, 16))
            pygame.draw.rect(surface, palette["accent"], 
                           (center_x - 6, center_y - 6, 12, 12))
        elif enemy_type == "aggressive":
            # Spiky enemy
            points = [
                (center_x, center_y - 10),
                (center_x + 8, center_y + 2),
                (center_x - 8, center_y + 2)
            ]
            pygame.draw.polygon(surface, palette["primary"], points)
            pygame.draw.polygon(surface, palette["accent"], 
                              [(center_x, center_y - 6), (center_x + 4, center_y), (center_x - 4, center_y)])
        elif enemy_type == "fast":
            # Diamond-shaped enemy
            points = [
                (center_x, center_y - 8),
                (center_x + 8, center_y),
                (center_x, center_y + 8),
                (center_x - 8, center_y)
            ]
            pygame.draw.polygon(surface, palette["primary"], points)
        
        filename = f"enemy_{enemy_type}_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_powerup_sprite(self, powerup_type: str, theme: str = "fantasy", size: Tuple[int, int] = (20, 20)) -> str:
        """Generate a powerup sprite"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center_x, center_y = size[0] // 2, size[1] // 2
        
        if powerup_type == "health":
            # Heart shape
            pygame.draw.circle(surface, palette["secondary"], (center_x - 3, center_y), 4)
            pygame.draw.circle(surface, palette["secondary"], (center_x + 3, center_y), 4)
            pygame.draw.polygon(surface, palette["secondary"], 
                              [(center_x, center_y + 6), (center_x - 6, center_y - 2), (center_x + 6, center_y - 2)])
        elif powerup_type == "speed":
            # Lightning bolt
            points = [
                (center_x - 2, center_y - 8),
                (center_x + 4, center_y - 2),
                (center_x - 1, center_y + 2),
                (center_x + 3, center_y + 8)
            ]
            pygame.draw.polygon(surface, palette["accent"], points)
        elif powerup_type == "score":
            # Star shape
            points = []
            for i in range(10):
                angle = i * 36 * np.pi / 180
                if i % 2 == 0:
                    radius = 8
                else:
                    radius = 4
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, palette["accent"], points)
        else:
            # Default circle
            pygame.draw.circle(surface, palette["accent"], (center_x, center_y), 8)
        
        filename = f"powerup_{powerup_type}_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_obstacle_sprite(self, obstacle_type: str, theme: str = "fantasy", size: Tuple[int, int] = (40, 40)) -> str:
        """Generate an obstacle sprite"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        if obstacle_type == "wall":
            # Brick pattern
            pygame.draw.rect(surface, palette["primary"], (0, 0, size[0], size[1]))
            for i in range(0, size[0], 8):
                pygame.draw.line(surface, palette["secondary"], (i, 0), (i, size[1]), 2)
            for i in range(0, size[1], 8):
                pygame.draw.line(surface, palette["secondary"], (0, i), (size[0], i), 2)
        elif obstacle_type == "rock":
            # Irregular rock shape
            points = []
            for i in range(8):
                angle = i * 45 * np.pi / 180
                radius = random.randint(15, 20)
                x = size[0] // 2 + radius * np.cos(angle)
                y = size[1] // 2 + radius * np.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, palette["primary"], points)
        elif obstacle_type == "tree":
            # Simple tree
            # Trunk
            pygame.draw.rect(surface, (139, 69, 19), (size[0]//2 - 4, size[1]//2, 8, size[1]//2))
            # Leaves
            pygame.draw.circle(surface, palette["secondary"], (size[0]//2, size[1]//3), size[0]//3)
        else:
            # Default rectangle
            pygame.draw.rect(surface, palette["primary"], (0, 0, size[0], size[1]))
        
        filename = f"obstacle_{obstacle_type}_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_background(self, theme: str = "fantasy", size: Tuple[int, int] = (800, 600)) -> str:
        """Generate a background texture"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        surface = pygame.Surface(size)
        
        # Base background
        surface.fill(palette["background"])
        
        # Add some texture based on theme
        if theme == "fantasy":
            # Add mystical patterns
            for _ in range(20):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1])
                pygame.draw.circle(surface, palette["primary"], (x, y), random.randint(2, 8), 1)
        elif theme == "sci-fi":
            # Add grid pattern
            for i in range(0, size[0], 50):
                pygame.draw.line(surface, palette["primary"], (i, 0), (i, size[1]), 1)
            for i in range(0, size[1], 50):
                pygame.draw.line(surface, palette["primary"], (0, i), (size[0], i), 1)
        elif theme == "nature":
            # Add grass-like pattern
            for _ in range(100):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1])
                pygame.draw.line(surface, palette["secondary"], (x, y), (x, y + 10), 2)
        
        filename = f"background_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_ui_element(self, element_type: str, theme: str = "fantasy", size: Tuple[int, int] = (200, 50)) -> str:
        """Generate UI elements"""
        palette = self.color_palettes.get(theme, self.color_palettes["fantasy"])
        
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        if element_type == "button":
            # Button with border
            pygame.draw.rect(surface, palette["primary"], (0, 0, size[0], size[1]))
            pygame.draw.rect(surface, palette["accent"], (2, 2, size[0] - 4, size[1] - 4))
        elif element_type == "health_bar":
            # Health bar background
            pygame.draw.rect(surface, palette["background"], (0, 0, size[0], size[1]))
            pygame.draw.rect(surface, palette["secondary"], (2, 2, size[0] - 4, size[1] - 4))
        elif element_type == "score_display":
            # Score display background
            pygame.draw.rect(surface, palette["primary"], (0, 0, size[0], size[1]), 2)
        
        filename = f"ui_{element_type}_{theme}_{size[0]}x{size[1]}.png"
        filepath = os.path.join(self.assets_dir, filename)
        pygame.image.save(surface, filepath)
        
        return filepath
    
    def generate_asset_pack(self, game_concept: Dict[str, Any]) -> Dict[str, str]:
        """Generate a complete asset pack for a game"""
        theme = game_concept.get("theme", "fantasy")
        assets = {}
        
        # Generate player sprite
        assets["player"] = self.generate_player_sprite(theme)
        
        # Generate enemy sprites
        enemies = game_concept.get("enemies", [])
        for enemy in enemies:
            enemy_type = enemy.get("name", "basic").lower()
            if "guard" in enemy_type or "basic" in enemy_type:
                enemy_type = "basic"
            elif "hunter" in enemy_type or "aggressive" in enemy_type:
                enemy_type = "aggressive"
            elif "fast" in enemy_type:
                enemy_type = "fast"
            else:
                enemy_type = "basic"
            
            assets[f"enemy_{enemy_type}"] = self.generate_enemy_sprite(enemy_type, theme)
        
        # Generate powerup sprites
        powerups = game_concept.get("powerups", [])
        for powerup in powerups:
            powerup_type = powerup.get("name", "health").lower()
            if "health" in powerup_type:
                powerup_type = "health"
            elif "speed" in powerup_type:
                powerup_type = "speed"
            elif "score" in powerup_type:
                powerup_type = "score"
            else:
                powerup_type = "health"
            
            assets[f"powerup_{powerup_type}"] = self.generate_powerup_sprite(powerup_type, theme)
        
        # Generate obstacle sprites
        assets["obstacle_wall"] = self.generate_obstacle_sprite("wall", theme)
        assets["obstacle_rock"] = self.generate_obstacle_sprite("rock", theme)
        assets["obstacle_tree"] = self.generate_obstacle_sprite("tree", theme)
        
        # Generate background
        assets["background"] = self.generate_background(theme)
        
        # Generate UI elements
        assets["ui_button"] = self.generate_ui_element("button", theme)
        assets["ui_health_bar"] = self.generate_ui_element("health_bar", theme)
        assets["ui_score_display"] = self.generate_ui_element("score_display", theme)
        
        # Save asset manifest
        manifest_path = os.path.join(self.assets_dir, f"manifest_{theme}.json")
        with open(manifest_path, 'w') as f:
            json.dump(assets, f, indent=2)
        
        return assets
    
    def create_sprite_sheet(self, sprites: List[str], output_path: str, cols: int = 4):
        """Create a sprite sheet from individual sprites"""
        if not sprites:
            return None
        
        # Load first sprite to get dimensions
        first_sprite = pygame.image.load(sprites[0])
        sprite_width, sprite_height = first_sprite.get_size()
        
        # Calculate sheet dimensions
        rows = (len(sprites) + cols - 1) // cols
        sheet_width = cols * sprite_width
        sheet_height = rows * sprite_height
        
        # Create sprite sheet
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        
        for i, sprite_path in enumerate(sprites):
            sprite = pygame.image.load(sprite_path)
            row = i // cols
            col = i % cols
            x = col * sprite_width
            y = row * sprite_height
            sheet.blit(sprite, (x, y))
        
        pygame.image.save(sheet, output_path)
        return output_path

class AssetManager:
    """Manages and loads game assets"""
    
    def __init__(self):
        self.assets_dir = "assets"
        self.loaded_assets = {}
    
    def load_asset(self, filepath: str) -> pygame.Surface:
        """Load an asset from file"""
        if filepath in self.loaded_assets:
            return self.loaded_assets[filepath]
        
        try:
            asset = pygame.image.load(filepath)
            self.loaded_assets[filepath] = asset
            return asset
        except Exception as e:
            print(f"Error loading asset {filepath}: {e}")
            # Return a placeholder surface
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for missing assets
            return placeholder
    
    def load_asset_pack(self, manifest_path: str) -> Dict[str, pygame.Surface]:
        """Load a complete asset pack from manifest"""
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        loaded_pack = {}
        for name, filepath in manifest.items():
            loaded_pack[name] = self.load_asset(filepath)
        
        return loaded_pack
    
    def get_asset(self, name: str) -> pygame.Surface:
        """Get a loaded asset by name"""
        return self.loaded_assets.get(name)
    
    def clear_cache(self):
        """Clear the asset cache"""
        self.loaded_assets.clear()
