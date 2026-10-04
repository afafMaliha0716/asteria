"""
Agentic Game Creation System
Autonomous agents that can create complete games using Gemini AI
"""

import os
import json
import time
import random
import textwrap
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from assets.asset_manager import get_sprite_manifest

from generators.gemini_generator import GeminiGameGenerator
from engine.game_engine import GameEngine

logger = logging.getLogger(__name__)

class GameCreationAgent:
    """Main agent for autonomous game creation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.generator = GeminiGameGenerator(api_key)
        self.created_games = []
        self.current_game = None

    @staticmethod
    def _read_template_file(template_id: str) -> str:
        """Reads the content of a specific template file."""
        # Maps template ID to the actual file name
        template_map = {
            "A_CORE_SETUP": "template_A_core_setup.py",
            "B_MOVEMENT_TOPDOWN": "template_B_movement_topdown.py",
            "C_MOVEMENT_PLATFORMER": "template_C_movement_platformer.py",
            "D_HEALTH_DAMAGE": "template_D_health_damage.py",
            "E_BASIC_COLLISION": "template_E_basic_collision.py",
            "F_GAME_STATES": "template_F_game_states.py",
            "G_ASSET_PATH_HANDLER": "template_G_asset_path_handler.py",
        }
        
        filename = template_map.get(template_id)
        if not filename:
            return f"# ERROR: Template ID '{template_id}' not found.\n"

        # CRITICAL: Construct the path relative to the current file's directory
        # Assumes 'templates' folder is a sibling of 'agents' or relative to the script root.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "..", "templates", filename)
        
        # Fallback path if templates folder is in the root directory (where main.py is)
        if not os.path.exists(template_path):
            root_dir = os.path.abspath(os.path.join(base_dir, ".."))
            template_path = os.path.join(root_dir, "templates", filename)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"# ERROR: Template file not found at {template_path}\n"
        except Exception as e:
            return f"# ERROR reading template {filename}: {str(e)}\n"

    @staticmethod
    def stitch_templates(template_ids: list) -> str:
        """Combines template code into a single string for the LLM."""
        stitched_code = ["# --- START GENERATED GAME CODE TEMPLATE ---"]
        
        for template_id in template_ids:
            # Add a clear marker before each template for debugging/review
            stitched_code.append(f"\n# --- TEMPLATE: {template_id} ---")
            stitched_code.append(GameCreationAgent._read_template_file(template_id))
            
        stitched_code.append("\n# --- END GENERATED GAME CODE TEMPLATE ---")
        
        return "\n".join(stitched_code)
        
    def create_game_autonomously(self, theme: str, existing_concept: Optional[dict] = None) -> Dict[str, Any]:
        """Orchestrates game creation using templates."""
        
        # 1. GENERATE GAME CONCEPT
        # This step remains the same:
        game_concept = existing_concept or self.generator.generate_game_concept(theme)
        
        # 2. GENERATE TEMPLATE PLAN (New Step)
        template_ids = self.generator.generate_template_plan(game_concept)
        logger.info(f"Templates selected: {template_ids}")
        
        # 3. STITCH TEMPLATES (New Step)
        stitched_template_code = GameCreationAgent.stitch_templates(template_ids)
        
        # 4. GENERATE LEVEL DESIGN (This remains the same)
        level_design = self.generator.generate_level_design(game_concept)
        
        # 5. GENERATE FINAL CODE (CRITICAL CHANGE)
        # We pass the stitched code to the LLM
        final_code_blocks = self.generator.generate_game_code(
            game_concept, 
            level_design, 
            stitched_template_code  # <-- NEW ARGUMENT
        )

        sprite_manifest = get_sprite_manifest()

    # 6. ASSEMBLE FINAL SCRIPT
        final_script = final_code_blocks 
        final_script = textwrap.dedent(final_script).strip()
        
        # --- CRITICAL NEW LOGGING STEP ---
        logger.info("-" * 50)
        logger.info(f"FINAL SCRIPT CODE GENERATED:\n{final_script[:2100]}...\n(Code snippet truncated for log brevity)")
        logger.info("-" * 50)
        # -----------------------------------

        # 7. GENERATE ASSETS & PACKAGE 
        asset_descriptions = self.generator.generate_asset_descriptions(game_concept, sprite_manifest)
        
        # 8. PACKAGE AND SAVE
        game_package = {
            "concept": game_concept,
            "level_design": level_design,
            "code": final_script, # <-- The code string is stored here
            "assets": asset_descriptions,
            "created_at": datetime.now().isoformat(),
            "theme": theme
        }
        return game_package
    
    def save_game(self, game_package: Dict[str, Any], filename: str = None) -> str:
        """Save game to file"""
        if not filename:
            title = game_package["concept"].get("title", "Unknown")
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.py"
        
        filepath = os.path.join("games", filename)
        
        # Ensure games directory exists
        os.makedirs("games", exist_ok=True)
        
        # Write the game code
        with open(filepath, 'w') as f:
            f.write(game_package["code"])
        
        # Save metadata
        metadata_path = filepath.replace('.py', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump({
                "concept": game_package["concept"],
                "level_design": game_package["level_design"],
                "assets": game_package["assets"],
                "created_at": game_package["created_at"],
                "theme": game_package["theme"]
            }, f, indent=2)
        
        logger.info(f"Game saved to {filepath}")
        return filepath
    
    def run_game(self, game_package: Dict[str, Any]) -> None:
        """Run the generated game"""
        try:
            # Create a temporary file to run the game
            temp_file = "temp_game.py"
            with open(temp_file, 'w') as f:
                f.write(game_package["code"])
            
            # Import and run the game
            import importlib.util
            spec = importlib.util.spec_from_file_location("temp_game", temp_file)
            game_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(game_module)
            
            # Clean up temp file
            os.remove(temp_file)
            
        except Exception as e:
            logger.error(f"Error running game: {e}")
            # Fallback: run with our engine
            self._run_with_engine(game_package)
    
    def _run_with_engine(self, game_package: Dict[str, Any]):
        """Run game using our engine as fallback"""
        try:
            engine = GameEngine(
                width=game_package["level_design"]["size"]["width"],
                height=game_package["level_design"]["size"]["height"],
                title=game_package["concept"]["title"]
            )
            engine.load_level(game_package["level_design"])
            engine.run()
        except Exception as e:
            logger.error(f"Error running with engine: {e}")

class GameDesignAgent:
    """Specialized agent for game design decisions"""
    
    def __init__(self, gemini_generator: GeminiGameGenerator):
        self.gemini = gemini_generator
    
    def analyze_and_improve_game(self, game_concept: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze game concept and suggest improvements"""
        prompt = f"""
        Analyze this game concept and suggest improvements:
        
        {json.dumps(game_concept, indent=2)}
        
        Consider:
        1. Gameplay balance
        2. Player engagement
        3. Difficulty progression
        4. Replayability
        5. Technical feasibility
        
        Provide a JSON response with:
        {{
            "analysis": "Overall analysis",
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "improvements": [
                {{"area": "mechanics", "suggestion": "improvement suggestion"}},
                {{"area": "balance", "suggestion": "balance improvement"}}
            ],
            "risk_level": "low/medium/high",
            "recommendation": "proceed/revise/reject"
        }}
        """
        
        try:
            response = self.gemini.model.generate_content(prompt)
            content = response.text.strip()
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            return {
                "analysis": "Analysis failed",
                "strengths": [],
                "weaknesses": [],
                "improvements": [],
                "risk_level": "medium",
                "recommendation": "proceed"
            }
    
    def generate_multiple_concepts(self, theme: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple game concepts for comparison"""
        concepts = []
        for i in range(count):
            concept = self.gemini.generate_game_concept(f"{theme} - variant {i+1}")
            concepts.append(concept)
        return concepts

class LevelDesignAgent:
    """Specialized agent for level design"""
    
    def __init__(self, gemini_generator: GeminiGameGenerator):
        self.gemini = gemini_generator
    
    def create_level_sequence(self, game_concept: Dict[str, Any], num_levels: int = 5) -> List[Dict[str, Any]]:
        """Create a sequence of levels with increasing difficulty"""
        levels = []
        
        for i in range(1, num_levels + 1):
            # Adjust difficulty based on level number
            difficulty_modifier = min(1.0 + (i - 1) * 0.2, 2.0)  # Cap at 2x difficulty
            
            level = self.gemini.generate_level_design(game_concept, i)
            
            # Apply difficulty scaling
            level = self._scale_difficulty(level, difficulty_modifier)
            levels.append(level)
        
        return levels
    
    def _scale_difficulty(self, level: Dict[str, Any], modifier: float) -> Dict[str, Any]:
        """Scale level difficulty"""
        # Scale enemy count
        if "enemies" in level:
            enemy_count = int(len(level["enemies"]) * modifier)
            if enemy_count > len(level["enemies"]):
                # Add more enemies
                for _ in range(enemy_count - len(level["enemies"])):
                    x = random.randint(50, level["size"]["width"] - 50)
                    y = random.randint(50, level["size"]["height"] - 50)
                    level["enemies"].append({
                        "x": x, "y": y, "type": "basic",
                        "patrol_path": [[x, y], [x + 50, y]]
                    })
        
        # Scale time limit
        if "time_limit" in level:
            level["time_limit"] = max(60, int(level["time_limit"] / modifier))
        
        return level

class AssetGenerationAgent:
    """Specialized agent for asset generation"""
    
    def __init__(self, gemini_generator: GeminiGameGenerator):
        self.gemini = gemini_generator
    
    def generate_visual_style_guide(self, game_concept: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive visual style guide"""
        prompt = f"""
        Create a detailed visual style guide for this game:
        
        {json.dumps(game_concept, indent=2)}
        
        Provide JSON with:
        {{
            "color_palette": {{
                "primary": "main color",
                "secondary": "secondary color",
                "accent": "accent color",
                "background": "background color",
                "text": "text color"
            }},
            "art_style": "detailed art style description",
            "ui_style": "UI design guidelines",
            "animation_style": "animation guidelines",
            "particle_effects": "particle effect suggestions",
            "lighting": "lighting style",
            "mood": "overall mood/atmosphere"
        }}
        """
        
        try:
            response = self.gemini.model.generate_content(prompt)
            content = response.text.strip()
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            style_guide = json.loads(content)
            return style_guide
            
        except Exception as e:
            logger.error(f"Error generating style guide: {e}")
            return self._get_fallback_style_guide()
    
    def _get_fallback_style_guide(self) -> Dict[str, Any]:
        """Fallback style guide"""
        return {
            "color_palette": {
                "primary": "Blue",
                "secondary": "Green",
                "accent": "Yellow",
                "background": "Black",
                "text": "White"
            },
            "art_style": "Simple geometric shapes with bright colors",
            "ui_style": "Clean, minimal interface",
            "animation_style": "Smooth, simple animations",
            "particle_effects": "Basic particle effects for collectibles",
            "lighting": "Flat lighting",
            "mood": "Energetic and fun"
        }

class AutonomousGameDirector:
    """Main director that orchestrates all agents for complete game creation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.gemini = GeminiGameGenerator(api_key)
        self.design_agent = GameDesignAgent(self.gemini)
        self.level_agent = LevelDesignAgent(self.gemini)
        self.asset_agent = AssetGenerationAgent(self.gemini)
        self.creation_agent = GameCreationAgent(api_key)
        
    def create_complete_game(self, theme: str = None, num_levels: int = 3) -> Dict[str, Any]:
        """Create a complete game with multiple levels"""
        logger.info(f"Creating complete game with theme: {theme}")
        
        # Step 1: Generate and analyze game concept
        concepts = self.design_agent.generate_multiple_concepts(theme, 3)
        best_concept = self._select_best_concept(concepts)
        
        # Step 2: Analyze and improve concept
        analysis = self.design_agent.analyze_and_improve_game(best_concept)
        if analysis["recommendation"] == "reject":
            logger.warning("Game concept rejected, using fallback")
            best_concept = self.gemini._get_fallback_concept(theme)
        
        # Step 3: Create level sequence
        levels = self.level_agent.create_level_sequence(best_concept, num_levels)
        
        # Step 4: Generate visual style guide
        style_guide = self.asset_agent.generate_visual_style_guide(best_concept)
        
        # Step 5: Generate complete game package
        complete_game = {
            "concept": best_concept,
            "analysis": analysis,
            "levels": levels,
            "style_guide": style_guide,
            "created_at": datetime.now().isoformat(),
            "theme": theme,
            "num_levels": num_levels
        }
        
        logger.info(f"Complete game created: {best_concept.get('title', 'Unknown')}")
        return complete_game
    
    def _select_best_concept(self, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best concept from multiple options"""
        # Simple scoring system
        best_concept = concepts[0]
        best_score = 0
        
        for concept in concepts:
            score = 0
            
            # Score based on mechanics count
            score += len(concept.get("mechanics", [])) * 2
            
            # Score based on enemy variety
            score += len(concept.get("enemies", [])) * 3
            
            # Score based on powerup variety
            score += len(concept.get("powerups", [])) * 2
            
            # Bonus for creative themes
            if concept.get("theme") and len(concept["theme"]) > 10:
                score += 5
            
            if score > best_score:
                best_score = score
                best_concept = concept
        
        return best_concept
    
    def save_complete_game(self, complete_game: Dict[str, Any]) -> str:
        """Save complete game with all levels"""
        title = complete_game["concept"].get("title", "Unknown")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create game directory
        game_dir = f"games/{safe_title}_{timestamp}"
        os.makedirs(game_dir, exist_ok=True)
        
        # Save main game file (first level)
        main_game_path = os.path.join(game_dir, "main.py")
        first_level_code = self.gemini.generate_game_code(
            complete_game["concept"], 
            complete_game["levels"][0]
        )
        
        with open(main_game_path, 'w') as f:
            f.write(first_level_code)
        
        # Save additional levels
        for i, level in enumerate(complete_game["levels"][1:], 1):
            level_code = self.gemini.generate_game_code(
                complete_game["concept"], 
                level
            )
            level_path = os.path.join(game_dir, f"level_{i+1}.py")
            with open(level_path, 'w') as f:
                f.write(level_code)
        
        # Save metadata
        metadata_path = os.path.join(game_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(complete_game, f, indent=2)
        
        logger.info(f"Complete game saved to {game_dir}")
        return game_dir
