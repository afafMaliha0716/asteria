# Agentic Game Generator with Gemini Integration

A powerful system that uses Google's Gemini AI to autonomously generate complete topdown games using pygame. This system features multiple AI agents that can create games from concept to playable code entirely autonomously.

## 🎮 Features

- **🤖 Agentic Game Creation**: Multiple AI agents that autonomously design and implement games
- **🧠 Gemini Integration**: Uses Google's Gemini API for intelligent game generation
- **🎯 Topdown Game Engine**: Built on pygame for 2D topdown games with collision detection
- **🎨 Asset Generation**: Automatic generation of sprites, backgrounds, and UI elements
- **📋 Game Templates**: Pre-built templates for adventure, action, and puzzle games
- **🔧 Modular Design**: Easy to extend and customize with new agents and templates

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your Gemini API key:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```
Get your API key from: https://makersuite.google.com/app/apikey

3. **Run the game generator:**
```bash
python main.py --interactive
```

## 🎯 Usage Examples

### Command Line Interface
```bash
# Create a simple game
python main.py --simple --theme "Space Adventure"

# Create a complete multi-level game
python main.py --complete --theme "Fantasy Quest" --levels 5

# List generated games
python main.py --list

# Run a specific game
python main.py --run games/MyGame_20241201_143022.py
```

### Interactive Mode
```bash
python main.py --interactive
```

### Python API
```python
from agents.game_agents import AutonomousGameDirector

# Create game director
director = AutonomousGameDirector(api_key="your_key")

# Generate complete game
game = director.create_complete_game("Cyberpunk", 3)
game_dir = director.save_complete_game(game)
```

## 🏗️ System Architecture

### AI Agents
- **GameCreationAgent**: Main agent for autonomous game creation
- **GameDesignAgent**: Analyzes and improves game concepts
- **LevelDesignAgent**: Creates level sequences with difficulty scaling
- **AssetGenerationAgent**: Generates visual style guides
- **AutonomousGameDirector**: Orchestrates all agents

### Game Engine
- **Entity System**: Base classes for all game objects
- **Collision Detection**: Built-in collision handling
- **Game States**: Menu, playing, paused, game over, victory
- **UI System**: Health bars, score display, time limits

### Templates
- **Adventure Template**: Exploration-based games with collection mechanics
- **Action Template**: Fast-paced games with combat and quick reflexes
- **Puzzle Template**: Logic-based games requiring problem-solving

## 📁 Project Structure

```
Game/
├── main.py                 # Main entry point
├── example.py              # Usage examples
├── config.py              # Configuration management
├── requirements.txt        # Dependencies
├── agents/                # AI agent implementations
│   └── game_agents.py
├── engine/                # Game engine components
│   └── game_engine.py
├── generators/            # Game generation modules
│   └── gemini_generator.py
├── templates/             # Game templates and patterns
│   └── game_templates.py
├── assets/                # Asset generation system
│   └── asset_generator.py
├── games/                 # Generated game files
└── README.md              # This file
```

## 🎨 Generated Game Features

Each generated game includes:
- **Complete pygame implementation** with all necessary imports
- **Player movement** (WASD or arrow keys)
- **Enemy AI** with different behavior patterns
- **Powerup system** with various effects
- **Collision detection** and response
- **Scoring system** and UI elements
- **Game states** (menu, playing, game over, victory)
- **Level progression** with increasing difficulty

## 🔧 Configuration

The system can be configured through:
- Environment variables
- `config.json` file
- Command line arguments

Key configuration options:
- `GEMINI_API_KEY`: Your Gemini API key
- `GAME_WIDTH`: Default game width (default: 800)
- `GAME_HEIGHT`: Default game height (default: 600)
- `GAME_FPS`: Default FPS (default: 60)

## 🎯 Game Types Supported

- **Adventure Games**: Exploration, collection, discovery mechanics
- **Action Games**: Fast-paced combat, evasion, power-ups
- **Puzzle Games**: Logic-based challenges, block pushing, switch activation
- **Custom Games**: AI-generated unique concepts based on themes

## 🚀 Advanced Usage

### Creating Custom Agents
```python
from agents.game_agents import GameDesignAgent

class CustomAgent(GameDesignAgent):
    def analyze_and_improve_game(self, game_concept):
        # Custom analysis logic
        return super().analyze_and_improve_game(game_concept)
```

### Using Templates
```python
from templates.game_templates import TemplateManager

template_manager = TemplateManager()
game_data = template_manager.generate_game_from_template(
    "adventure", "Space Exploration", 5
)
```

### Asset Generation
```python
from assets.asset_generator import AssetGenerator

asset_gen = AssetGenerator()
assets = asset_gen.generate_asset_pack(game_concept)
```

## 🤝 Contributing

This is a hackathon project demonstrating agentic AI systems for game generation. Feel free to extend and improve!

## 📄 License

This project is open source and available under the MIT License.
