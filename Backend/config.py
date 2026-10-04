"""
Configuration file for the Agentic Game Generator
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "gemini": {
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30
    },
    "game": {
        "default_width": 800,
        "default_height": 600,
        "default_fps": 60,
        "max_levels": 10,
        "default_levels": 3
    },
    "assets": {
        "sprite_size": (32, 32),
        "enemy_size": (24, 24),
        "powerup_size": (20, 20),
        "obstacle_size": (40, 40),
        "ui_size": (200, 50)
    },
    "directories": {
        "games": "games",
        "assets": "assets",
        "templates": "templates",
        "logs": "logs"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "game_generator.log"
    }
}

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self.config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini-specific configuration"""
        return self.config.get("gemini", {})
    
    def get_game_config(self) -> Dict[str, Any]:
        """Get game-specific configuration"""
        return self.config.get("game", {})
    
    def get_asset_config(self) -> Dict[str, Any]:
        """Get asset-specific configuration"""
        return self.config.get("assets", {})
    
    def get_directory_config(self) -> Dict[str, str]:
        """Get directory configuration"""
        return self.config.get("directories", {})

# Global config instance
config = Config()

# Environment variable mappings
ENV_MAPPINGS = {
    "GEMINI_API_KEY": "gemini.api_key",
    "GAME_WIDTH": "game.default_width",
    "GAME_HEIGHT": "game.default_height",
    "GAME_FPS": "game.default_fps",
    "LOG_LEVEL": "logging.level"
}

def load_from_env():
    """Load configuration from environment variables"""
    for env_var, config_key in ENV_MAPPINGS.items():
        value = os.getenv(env_var)
        if value:
            # Convert string values to appropriate types
            if config_key in ["game.default_width", "game.default_height", "game.default_fps"]:
                try:
                    value = int(value)
                except ValueError:
                    continue
            elif config_key == "gemini.temperature":
                try:
                    value = float(value)
                except ValueError:
                    continue
            
            config.set(config_key, value)

# Load environment variables on import
load_from_env()
