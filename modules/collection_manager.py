"""
Collection Manager Module for SWGOH
Handles daily activities, card collection, and resource management
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from main import SWGOHAutomator

logger = logging.getLogger(__name__)

@dataclass
class DailyTask:
    """Daily task structure"""
    name: str
    completed: bool
    last_completed: Optional[datetime]
    reward_claimed: bool

@dataclass
class CollectionItem:
    """Collection item information"""
    name: str
    owned: bool
    shards: int
    shards_needed: int
    rarity: str

class CollectionManager:
    """Manages collections and daily activities"""
    
    def __init__(self, automator: SWGOHAutomator):
        self.automator = automator
        self.daily_tasks = self.load_daily_tasks()
        
    def load_daily_tasks(self) -> Dict[str, DailyTask]:
        """Load daily tasks from storage or initialize defaults"""
        return {
            "daily_login": DailyTask("Daily Login", False, None, False),
            "daily_challenges": DailyTask("Daily Challenges", False, None, False),
            "guild_activities": DailyTask("Guild Activities", False, None, False),
            "fleet_challenges": DailyTask("Fleet Challenges", False, None, False),
            "cantina_challenges": DailyTask("Cantina Challenges", False, None, False),
            "pvp_battles": DailyTask("PVP Battles", False, None, False),
            "ship_challenges": DailyTask("Ship Challenges", False, None, False),
        }
        
    def check_daily_login(self) -> bool:
        """Check and claim daily login rewards"""
        logger.info("Checking daily login rewards")
        
        # Look for daily login popup
        if self.automator.click_image("assets/daily_login.png"):
            logger.info("Daily login popup found")
            
            # Click through login rewards
            for i in range(5):  # Assume max 5 days of rewards
                if self.automator.click_image("assets/claim_daily.png"):
                    time.sleep(0.5)
                    if self.automator.click_image("assets/next_day.png"):
                        time.sleep(0.5)
                    else:
                        break
                else:
                    break
                    
            # Close daily login screen
            self.automator.click_image("assets/close_button.png")
            self.daily_tasks["daily_login"].completed = True
            self.daily_tasks["daily_login"].last_completed = datetime.now()
            return True
            
        return False
        
    def complete_daily_challenges(self) -> bool:
        """Complete daily challenges"""
        logger.info("Completing daily challenges")
        
        # Navigate to challenges screen
        if not self.automator.click_image("assets/challenges_button.png"):
            logger.error("Could not find challenges button")
            return False
            
        time.sleep(1)
        
        # Complete each type of challenge
        challenge_types = [
            ("daily", "assets/daily_challenges.png"),
            ("guild", "assets/guild_challenges.png"),
            ("fleet", "assets/fleet_challenges.png"),
            ("cantina", "assets/cantina_challenges.png")
        ]
        
        completed_challenges = 0
        
        for challenge_type, button_image in challenge_types:
            if self.automator.click_image(button_image):
                time.sleep(1)
                
                # Analyze and complete challenges
                screenshot = self.automator.capture_screen()
                prompt = f"""
                Analyze these {challenge_type} challenges. Which ones are completed?
                Which ones still need to be completed? List them in order of priority.
                
                Return format:
                completed: [challenge names]
                pending: [challenge names]
                """
                
                response = self.automator.analyze_screen_with_ai(screenshot, prompt)
                
                # Try to complete pending challenges
                if "pending:" in response:
                    pending_challenges = self.parse_challenge_list(response, "pending:")
                    for challenge in pending_challenges[:3]:  # Limit to 3 challenges
                        if self.complete_challenge(challenge):
                            completed_challenges += 1
                            
                time.sleep(0.5)
                
        # Go back to main screen
        self.automator.click_image("assets/back_button.png")
        
        if completed_challenges > 0:
            self.daily_tasks["daily_challenges"].completed = True
            self.daily_tasks["daily_challenges"].last_completed = datetime.now()
            
        logger.info(f"Completed {completed_challenges} challenges")
        return completed_challenges > 0
        
    def complete_challenge(self, challenge_name: str) -> bool:
        """Complete a specific challenge"""
        logger.info(f"Attempting to complete: {challenge_name}")
        
        # Try to find challenge by image
        challenge_image = f"assets/challenges/{challenge_name.lower().replace(' ', '_')}.png"
        if self.automator.click_image(challenge_image):
            time.sleep(0.5)
            
            # Look for complete/claim buttons
            if self.automator.click_image("assets/complete_challenge.png"):
                time.sleep(1)
                return self.automator.click_image("assets/claim_reward.png")
                
        return False
        
    def parse_challenge_list(self, response: str, section: str) -> List[str]:
        """Parse challenge list from AI response"""
        try:
            lines = response.split('\n')
            for line in lines:
                if line.startswith(section):
                    challenges_str = line.replace(section, "").strip()
                    # Remove brackets and split by comma
                    challenges_str = challenges_str.replace("[", "").replace("]", "")
                    return [c.strip() for c in challenges_str.split(',') if c.strip()]
        except Exception as e:
            logger.error(f"Failed to parse challenge list: {e}")
            
        return []
        
    def check_guild_activities(self) -> bool:
        """Check and complete guild activities"""
        logger.info("Checking guild activities")
        
        # Navigate to guild screen
        if not self.automator.click_image("assets/guild_button.png"):
            logger.error("Could not find guild button")
            return False
            
        time.sleep(1)
        
        # Check for guild donations
        if self.automator.click_image("assets/guild_donate.png"):
            time.sleep(1)
            
            # Auto-donate resources
            resources = ["assets/donate_credits.png", "assets/donate_materials.png", "assets/donate_ship_parts.png"]
            for resource in resources:
                if self.automator.click_image(resource):
                    time.sleep(0.5)
                    
            # Close donation screen
            self.automator.click_image("assets/close_button.png")
            
        # Check guild raids
        if self.automator.click_image("assets/guild_raids.png"):
            time.sleep(1)
            
            # Check if raid is available
            screenshot = self.automator.capture_screen()
            prompt = """
            Analyze this guild raid screen. Is there an active raid available?
            If so, what phase is it in and can we participate?
            
            Return format:
            raid_available: yes/no
            phase: [phase number]
            can_participate: yes/no
            """
            
            response = self.automator.analyze_screen_with_ai(screenshot, prompt)
            
            if "raid_available: yes" in response and "can_participate: yes" in response:
                # Participate in raid (simplified logic)
                if self.automator.click_image("assets/join_raid.png"):
                    time.sleep(1)
                    self.automator.click_image("assets/start_raid.png")
                    
        # Return to main screen
        self.automator.click_image("assets/back_button.png")
        
        self.daily_tasks["guild_activities"].completed = True
        self.daily_tasks["guild_activities"].last_completed = datetime.now()
        return True
        
    def check_card_collection(self) -> List[CollectionItem]:
        """Analyze current card collection"""
        logger.info("Analyzing card collection")
        
        # Navigate to collection screen
        if not self.automator.click_image("assets/collection_button.png"):
            logger.error("Could not find collection button")
            return []
            
        time.sleep(1)
        
        screenshot = self.automator.capture_screen()
        prompt = """
        Analyze this character collection screen. For each character visible, provide:
        - Character name
        - Number of shards owned
        - Total shards needed for unlock/activation
        - Rarity level (1-7 stars)
        
        Return in format for each character:
        name: [character name]
        shards: [current]/[needed]
        rarity: [stars]
        """
        
        response = self.automator.analyze_screen_with_ai(screenshot, prompt)
        collection_items = self.parse_collection_response(response)
        
        # Return to main screen
        self.automator.click_image("assets/back_button.png")
        
        return collection_items
        
    def parse_collection_response(self, response: str) -> List[CollectionItem]:
        """Parse collection data from AI response"""
        items = []
        current_item = {}
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('name:'):
                    if current_item:  # Save previous item
                        items.append(self.create_collection_item(current_item))
                    current_item = {'name': line.replace('name:', '').strip()}
                elif line.startswith('shards:'):
                    shards_str = line.replace('shards:', '').strip()
                    if '/' in shards_str:
                        current, needed = shards_str.split('/')
                        current_item['shards'] = int(current)
                        current_item['shards_needed'] = int(needed)
                elif line.startswith('rarity:'):
                    current_item['rarity'] = line.replace('rarity:', '').strip()
                    
            # Add last item
            if current_item:
                items.append(self.create_collection_item(current_item))
                
        except Exception as e:
            logger.error(f"Failed to parse collection response: {e}")
            
        return items
        
    def create_collection_item(self, item_data: Dict) -> CollectionItem:
        """Create CollectionItem from parsed data"""
        return CollectionItem(
            name=item_data.get('name', 'Unknown'),
            owned=item_data.get('shards', 0) > 0,
            shards=item_data.get('shards', 0),
            shards_needed=item_data.get('shards_needed', 0),
            rarity=item_data.get('rarity', '1')
        )
        
    def auto_complete_dailies(self) -> Dict[str, bool]:
        """Complete all daily activities"""
        logger.info("Starting daily activities automation")
        
        results = {}
        
        # Daily login
        results["login"] = self.check_daily_login()
        time.sleep(1)
        
        # Daily challenges
        results["challenges"] = self.complete_daily_challenges()
        time.sleep(1)
        
        # Guild activities
        results["guild"] = self.check_guild_activities()
        time.sleep(1)
        
        # Check collection
        collection = self.check_card_collection()
        results["collection_checked"] = len(collection) > 0
        
        logger.info(f"Daily activities completed: {results}")
        return results
        
    def get_collection_progress(self) -> Dict:
        """Get overall collection progress"""
        items = self.check_card_collection()
        
        total_characters = len(items)
        owned_characters = sum(1 for item in items if item.owned)
        max_rarity_characters = sum(1 for item in items if item.rarity == '7')
        
        return {
            "total_characters": total_characters,
            "owned_characters": owned_characters,
            "max_rarity_characters": max_rarity_characters,
            "ownership_rate": owned_characters / total_characters if total_characters > 0 else 0,
            "max_rarity_rate": max_rarity_characters / total_characters if total_characters > 0 else 0,
            "near_completion": [item for item in items if item.shards_needed - item.shards <= 50]
        }
