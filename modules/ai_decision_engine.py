"""
AI Decision Engine for SWGOH Automation
Uses Google Generative AI to make intelligent decisions about game state and actions
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from main import SWGOHAutomator

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions the AI can recommend"""
    ENERGY_REFILL = "energy_refill"
    START_BATTLE = "start_battle"
    COMPLETE_DAILY = "complete_daily"
    COLLECT_REWARDS = "collect_rewards"
    WAIT_ENERGY = "wait_energy"
    FARM_STAGE = "farm_stage"
    GUILD_ACTIVITY = "guild_activity"
    UPGRADE_CHARACTER = "upgrade_character"
    SIM_BATTLE = "sim_battle"
    NONE = "none"

@dataclass
class AIAction:
    """AI-recommended action"""
    action_type: ActionType
    priority: int  # 1-10, 10 being highest
    description: str
    parameters: Dict
    confidence: float  # 0.0-1.0

@dataclass
class GameState:
    """Current game state analysis"""
    energy_levels: Dict[str, int]
    available_activities: List[str]
    current_screen: str
    pending_rewards: List[str]
    character_status: Dict[str, Dict]
    guild_status: Dict
    battle_history: List[Dict]

class AIDecisionEngine:
    """AI-powered decision making for SWGOH automation"""
    
    def __init__(self, automator: SWGOHAutomator):
        self.automator = automator
        self.action_history = []
        self.last_analysis_time = 0
        
    def analyze_game_state(self) -> Optional[GameState]:
        """Comprehensive analysis of current game state"""
        logger.info("Analyzing game state with AI")
        
        screenshot = self.automator.capture_screen()
        prompt = """
        Analyze this Star Wars Galaxy of Heroes screen comprehensively. Provide:
        
        1. Current screen type (main menu, battle, collection, guild, etc.)
        2. Energy levels visible (cantina, regular, fleet)
        3. Available activities/buttons visible
        4. Any pending rewards or notifications
        5. Character information if on character screen
        6. Guild information if on guild screen
        
        Format your response as:
        screen: [screen type]
        energy: cantina:X/Y regular:X/Y fleet:X/Y
        activities: [activity1, activity2, ...]
        rewards: [reward1, reward2, ...]
        characters: [character info if visible]
        guild: [guild info if visible]
        """
        
        try:
            response = self.automator.analyze_screen_with_ai(screenshot, prompt)
            return self.parse_game_state(response)
        except Exception as e:
            logger.error(f"Game state analysis failed: {e}")
            return None
            
    def parse_game_state(self, response: str) -> GameState:
        """Parse AI response into GameState object"""
        state = GameState(
            energy_levels={},
            available_activities=[],
            current_screen="unknown",
            pending_rewards=[],
            character_status={},
            guild_status={},
            battle_history=[]
        )
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('screen:'):
                    state.current_screen = line.replace('screen:', '').strip()
                elif line.startswith('energy:'):
                    energy_str = line.replace('energy:', '').strip()
                    state.energy_levels = self.parse_energy_levels(energy_str)
                elif line.startswith('activities:'):
                    activities_str = line.replace('activities:', '').strip()
                    state.available_activities = [a.strip() for a in activities_str.split(',')]
                elif line.startswith('rewards:'):
                    rewards_str = line.replace('rewards:', '').strip()
                    state.pending_rewards = [r.strip() for r in rewards_str.split(',')]
                elif line.startswith('characters:'):
                    characters_str = line.replace('characters:', '').strip()
                    state.character_status = self.parse_character_info(characters_str)
                elif line.startswith('guild:'):
                    guild_str = line.replace('guild:', '').strip()
                    state.guild_status = self.parse_guild_info(guild_str)
                    
        except Exception as e:
            logger.error(f"Failed to parse game state: {e}")
            
        return state
        
    def parse_energy_levels(self, energy_str: str) -> Dict[str, int]:
        """Parse energy levels from string"""
        energy_levels = {}
        parts = energy_str.split()
        for part in parts:
            if ':' in part:
                energy_type, levels = part.split(':')
                if '/' in levels:
                    current, _ = levels.split('/')
                    energy_levels[energy_type] = int(current)
        return energy_levels
        
    def parse_character_info(self, characters_str: str) -> Dict[str, Dict]:
        """Parse character information"""
        # Simplified parsing - would need more complex logic for full character data
        return {"info": characters_str}
        
    def parse_guild_info(self, guild_str: str) -> Dict:
        """Parse guild information"""
        return {"info": guild_str}
        
    def get_recommended_actions(self, game_state: GameState) -> List[AIAction]:
        """Get AI-recommended actions based on game state"""
        logger.info("Getting AI recommendations")
        
        # Create context for AI decision making
        context = self.create_decision_context(game_state)
        
        prompt = f"""
        Based on this SWGOH game state, recommend the best actions to take:
        
        Current State:
        - Screen: {game_state.current_screen}
        - Energy: {game_state.energy_levels}
        - Available Activities: {game_state.available_activities}
        - Pending Rewards: {game_state.pending_rewards}
        
        Recent Actions: {self.action_history[-5:] if self.action_history else 'None'}
        
        Recommend 3-5 actions with priorities (1-10, 10 highest) and confidence (0.0-1.0).
        Consider energy efficiency, reward value, and time sensitivity.
        
        Format each action as:
        action: [action_type]
        priority: [1-10]
        description: [brief description]
        parameters: [key:value pairs]
        confidence: [0.0-1.0]
        """
        
        screenshot = self.automator.capture_screen()
        
        try:
            response = self.automator.analyze_screen_with_ai(screenshot, prompt)
            return self.parse_ai_actions(response)
        except Exception as e:
            logger.error(f"AI recommendation failed: {e}")
            return []
            
    def create_decision_context(self, game_state: GameState) -> str:
        """Create context string for AI decision making"""
        context = f"""
        Game Analysis:
        - Current screen: {game_state.current_screen}
        - Energy status: {game_state.energy_levels}
        - Available activities: {len(game_state.available_activities)} options
        - Pending rewards: {len(game_state.pending_rewards)} items
        
        Recent performance: {len(self.action_history)} actions taken
        """
        return context
        
    def parse_ai_actions(self, response: str) -> List[AIAction]:
        """Parse AI response into AIAction objects"""
        actions = []
        current_action = {}
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('action:'):
                    if current_action:  # Save previous action
                        actions.append(self.create_ai_action(current_action))
                    current_action = {'action_type': line.replace('action:', '').strip()}
                elif line.startswith('priority:'):
                    current_action['priority'] = int(line.replace('priority:', '').strip())
                elif line.startswith('description:'):
                    current_action['description'] = line.replace('description:', '').strip()
                elif line.startswith('parameters:'):
                    params_str = line.replace('parameters:', '').strip()
                    current_action['parameters'] = self.parse_parameters(params_str)
                elif line.startswith('confidence:'):
                    current_action['confidence'] = float(line.replace('confidence:', '').strip())
                    
            # Add last action
            if current_action:
                actions.append(self.create_ai_action(current_action))
                
        except Exception as e:
            logger.error(f"Failed to parse AI actions: {e}")
            
        return actions
        
    def parse_parameters(self, params_str: str) -> Dict:
        """Parse parameters string into dictionary"""
        params = {}
        try:
            if params_str and ':' in params_str:
                for param in params_str.split(','):
                    if ':' in param:
                        key, value = param.split(':', 1)
                        params[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Failed to parse parameters: {e}")
        return params
        
    def create_ai_action(self, action_data: Dict) -> AIAction:
        """Create AIAction from parsed data"""
        action_type_str = action_data.get('action_type', 'none')
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            action_type = ActionType.NONE
            
        return AIAction(
            action_type=action_type,
            priority=action_data.get('priority', 5),
            description=action_data.get('description', ''),
            parameters=action_data.get('parameters', {}),
            confidence=action_data.get('confidence', 0.5)
        )
        
    def execute_action(self, action: AIAction) -> bool:
        """Execute AI-recommended action"""
        logger.info(f"Executing action: {action.description}")
        
        try:
            if action.action_type == ActionType.ENERGY_REFILL:
                return self.execute_energy_refill(action.parameters)
            elif action.action_type == ActionType.START_BATTLE:
                return self.execute_start_battle(action.parameters)
            elif action.action_type == ActionType.COMPLETE_DAILY:
                return self.execute_complete_daily(action.parameters)
            elif action.action_type == ActionType.COLLECT_REWARDS:
                return self.execute_collect_rewards(action.parameters)
            elif action.action_type == ActionType.FARM_STAGE:
                return self.execute_farm_stage(action.parameters)
            elif action.action_type == ActionType.GUILD_ACTIVITY:
                return self.execute_guild_activity(action.parameters)
            else:
                logger.warning(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return False
            
    def execute_energy_refill(self, params: Dict) -> bool:
        """Execute energy refill action"""
        from modules.energy_manager import EnergyManager
        energy_manager = EnergyManager(self.automator)
        
        energy_type = params.get('type', 'regular')
        return energy_manager.refill_energy(energy_type)
        
    def execute_start_battle(self, params: Dict) -> bool:
        """Execute start battle action"""
        from modules.battle_automation import BattleAutomation
        battle_automation = BattleAutomation(self.automator)
        
        mode = params.get('mode', 'regular')
        stage = params.get('stage', '1-A')
        team = params.get('team', 'regular')
        
        results = battle_automation.run_battle_sequence(mode, stage, team, 1)
        return len(results) > 0
        
    def execute_complete_daily(self, params: Dict) -> bool:
        """Execute daily completion action"""
        from modules.collection_manager import CollectionManager
        collection_manager = CollectionManager(self.automator)
        
        results = collection_manager.auto_complete_dailies()
        return any(results.values())
        
    def execute_collect_rewards(self, params: Dict) -> bool:
        """Execute reward collection action"""
        # Look for and click various reward buttons
        reward_buttons = [
            "assets/claim_rewards.png",
            "assets/collect_button.png", 
            "assets/gift_box.png",
            "assets/notification.png"
        ]
        
        for button in reward_buttons:
            if self.automator.click_image(button):
                time.sleep(0.5)
                return True
                
        return False
        
    def execute_farm_stage(self, params: Dict) -> bool:
        """Execute stage farming action"""
        from modules.battle_automation import BattleAutomation
        battle_automation = BattleAutomation(self.automator)
        
        mode = params.get('mode', 'regular')
        stage = params.get('stage', '1-A')
        team = params.get('team', 'regular')
        repetitions = int(params.get('repetitions', '3'))
        
        results = battle_automation.run_battle_sequence(mode, stage, team, repetitions)
        return len(results) > 0
        
    def execute_guild_activity(self, params: Dict) -> bool:
        """Execute guild activity action"""
        from modules.collection_manager import CollectionManager
        collection_manager = CollectionManager(self.automator)
        
        return collection_manager.check_guild_activities()
        
    def run_ai_automation(self, max_actions: int = 10, time_limit: int = 3600) -> Dict:
        """Run AI-driven automation session"""
        logger.info("Starting AI-driven automation")
        
        start_time = time.time()
        actions_executed = 0
        successful_actions = 0
        action_results = []
        
        while actions_executed < max_actions and time.time() - start_time < time_limit:
            # Analyze current state
            game_state = self.analyze_game_state()
            if not game_state:
                logger.warning("Could not analyze game state, waiting...")
                time.sleep(5)
                continue
                
            # Get AI recommendations
            recommended_actions = self.get_recommended_actions(game_state)
            if not recommended_actions:
                logger.info("No AI recommendations available")
                break
                
            # Execute highest priority action
            best_action = max(recommended_actions, key=lambda a: (a.priority, a.confidence))
            
            logger.info(f"AI recommends: {best_action.description} (Priority: {best_action.priority}, Confidence: {best_action.confidence})")
            
            # Execute action
            success = self.execute_action(best_action)
            
            # Record action
            action_result = {
                "action": best_action.description,
                "success": success,
                "timestamp": time.time()
            }
            action_results.append(action_result)
            self.action_history.append(action_result)
            
            if success:
                successful_actions += 1
                logger.info("Action executed successfully")
            else:
                logger.warning("Action execution failed")
                
            actions_executed += 1
            time.sleep(2)  # Brief pause between actions
            
        duration = time.time() - start_time
        
        return {
            "actions_executed": actions_executed,
            "successful_actions": successful_actions,
            "success_rate": successful_actions / actions_executed if actions_executed > 0 else 0,
            "duration": duration,
            "action_results": action_results
        }
        
    def get_optimization_suggestions(self) -> List[str]:
        """Get AI suggestions for optimization"""
        screenshot = self.automator.capture_screen()
        
        prompt = """
        Analyze this SWGOH screen and provide optimization suggestions.
        Focus on:
        1. Energy efficiency
        2. Resource management
        3. Character progression
        4. Missing opportunities
        
        Provide 3-5 specific suggestions.
        """
        
        try:
            response = self.automator.analyze_screen_with_ai(screenshot, prompt)
            return [line.strip() for line in response.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {e}")
            return []
