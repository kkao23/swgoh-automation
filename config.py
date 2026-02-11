"""
Configuration Management for SWGOH Automation Bot
Handles user preferences and settings
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

@dataclass
class AutomationConfig:
    """Main automation configuration"""
    # General Settings
    debug_mode: bool = False
    screenshot_delay: float = 0.5
    click_delay: float = 0.2
    confidence_threshold: float = 0.8
    
    # Energy Management
    auto_refill_energy: bool = True
    energy_refill_threshold: float = 0.2
    max_daily_refills: int = 3
    
    # Battle Settings
    auto_battles: bool = True
    preferred_battle_mode: str = "regular"
    auto_farm_stage: str = "1-A"
    farm_repetitions: int = 3
    battle_strategy: str = "auto"
    
    # Daily Activities
    auto_dailies: bool = True
    auto_guild: bool = True
    auto_login_rewards: bool = True
    
    # AI Settings
    ai_enabled: bool = True
    ai_decision_threshold: float = 0.7
    max_ai_actions: int = 10
    ai_session_duration: int = 3600
    
    # Safety Settings
    safe_mode: bool = True
    max_daily_actions: int = 1000
    break_interval: int = 3600  # 1 hour breaks
    break_duration: int = 300   # 5 minute breaks
    
    # Notification Settings
    enable_notifications: bool = True
    notification_level: str = "important"  # all, important, errors

@dataclass
class TeamConfig:
    """Team configuration for battles"""
    name: str
    characters: list[str]
    strategy: str = "auto"
    target_stages: list[str] = None
    
@dataclass
class UserPreferences:
    """User-specific preferences"""
    username: str = "Player"
    preferred_farming_modes: list[str] = None
    priority_characters: list[str] = None
    guild_participation: bool = True
    pvp_participation: bool = False
    
    def __post_init__(self):
        if self.preferred_farming_modes is None:
            self.preferred_farming_modes = ["regular", "cantina"]
        if self.priority_characters is None:
            self.priority_characters = []

class ConfigManager:
    """Manages configuration and user preferences"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.automation_config = AutomationConfig()
        self.user_preferences = UserPreferences()
        self.team_configs = {}
        
        load_dotenv()  # Load environment variables
        self.load_config()
        
    def load_config(self):
        """Load configuration from file and environment"""
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                # Update automation config
                if 'automation' in config_data:
                    for key, value in config_data['automation'].items():
                        if hasattr(self.automation_config, key):
                            setattr(self.automation_config, key, value)
                            
                # Update user preferences
                if 'user_preferences' in config_data:
                    for key, value in config_data['user_preferences'].items():
                        if hasattr(self.user_preferences, key):
                            setattr(self.user_preferences, key, value)
                            
                # Load team configs
                if 'teams' in config_data:
                    self.team_configs = config_data['teams']
                    
                logger.info("Configuration loaded from file")
                
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                
        # Override with environment variables
        self.load_from_env()
        
    def load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'DEBUG_MODE': ('debug_mode', bool),
            'SCREENSHOT_DELAY': ('screenshot_delay', float),
            'CLICK_DELAY': ('click_delay', float),
            'CONFIDENCE_THRESHOLD': ('confidence_threshold', float),
            'AUTO_REFILL_ENERGY': ('auto_refill_energy', bool),
            'AUTO_BATTLES': ('auto_battles', bool),
            'AI_ENABLED': ('ai_enabled', bool),
            'SAFE_MODE': ('safe_mode', bool),
        }
        
        for env_var, (config_key, var_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if var_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = var_type(value)
                    setattr(self.automation_config, config_key, value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
                    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                'automation': asdict(self.automation_config),
                'user_preferences': asdict(self.user_preferences),
                'teams': self.team_configs
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            logger.info("Configuration saved to file")
            
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
            
    def get_automation_config(self) -> AutomationConfig:
        """Get automation configuration"""
        return self.automation_config
        
    def get_user_preferences(self) -> UserPreferences:
        """Get user preferences"""
        return self.user_preferences
        
    def add_team_config(self, team: TeamConfig):
        """Add or update team configuration"""
        self.team_configs[team.name] = asdict(team)
        self.save_config()
        logger.info(f"Team configuration added/updated: {team.name}")
        
    def get_team_config(self, team_name: str) -> Optional[TeamConfig]:
        """Get team configuration by name"""
        if team_name in self.team_configs:
            team_data = self.team_configs[team_name]
            return TeamConfig(**team_data)
        return None
        
    def list_team_configs(self) -> list[str]:
        """List all available team configurations"""
        return list(self.team_configs.keys())
        
    def update_automation_setting(self, key: str, value: Any):
        """Update a specific automation setting"""
        if hasattr(self.automation_config, key):
            setattr(self.automation_config, key, value)
            self.save_config()
            logger.info(f"Automation setting updated: {key} = {value}")
        else:
            logger.warning(f"Unknown automation setting: {key}")
            
    def update_user_preference(self, key: str, value: Any):
        """Update a specific user preference"""
        if hasattr(self.user_preferences, key):
            setattr(self.user_preferences, key, value)
            self.save_config()
            logger.info(f"User preference updated: {key} = {value}")
        else:
            logger.warning(f"Unknown user preference: {key}")
            
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.automation_config = AutomationConfig()
        self.user_preferences = UserPreferences()
        self.team_configs = {}
        self.save_config()
        logger.info("Configuration reset to defaults")
        
    def validate_config(self) -> list[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check required files/directories
        required_dirs = ['assets', 'assets/characters', 'assets/stages', 'assets/challenges']
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                issues.append(f"Missing directory: {dir_path}")
                
        # Check API key
        if not os.getenv('GOOGLE_API_KEY'):
            issues.append("GOOGLE_API_KEY not set in environment variables")
            
        # Validate numeric ranges
        if self.automation_config.confidence_threshold < 0 or self.automation_config.confidence_threshold > 1:
            issues.append("Confidence threshold must be between 0 and 1")
            
        if self.automation_config.screenshot_delay < 0:
            issues.append("Screenshot delay must be positive")
            
        if self.automation_config.click_delay < 0:
            issues.append("Click delay must be positive")
            
        # Validate team configurations
        for team_name, team_data in self.team_configs.items():
            if not isinstance(team_data.get('characters'), list) or len(team_data.get('characters', [])) == 0:
                issues.append(f"Team '{team_name}' has invalid character configuration")
                
        return issues
        
    def get_config_summary(self) -> str:
        """Get configuration summary for display"""
        summary = f"""
SWGOH Automation Configuration:
===============================
Debug Mode: {self.automation_config.debug_mode}
AI Enabled: {self.automation_config.ai_enabled}
Safe Mode: {self.automation_config.safe_mode}

Energy Management:
- Auto Refill: {self.automation_config.auto_refill_energy}
- Refill Threshold: {self.automation_config.energy_refill_threshold * 100:.0f}%
- Max Daily Refills: {self.automation_config.max_daily_refills}

Battle Settings:
- Auto Battles: {self.automation_config.auto_battles}
- Preferred Mode: {self.automation_config.preferred_barming_mode}
- Farm Stage: {self.automation_config.auto_farm_stage}
- Repetitions: {self.automation_config.farm_repetitions}

Daily Activities:
- Auto Dailies: {self.automation_config.auto_dailies}
- Auto Guild: {self.automation_config.auto_guild}
- Auto Login: {self.automation_config.auto_login_rewards}

User Preferences:
- Username: {self.user_preferences.username}
- Guild Participation: {self.user_preferences.guild_participation}
- PvP Participation: {self.user_preferences.pvp_participation}

Teams Configured: {len(self.team_configs)}
"""
        return summary.strip()

# Global config instance
config_manager = ConfigManager()
