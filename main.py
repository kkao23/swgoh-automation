#!/usr/bin/env python3
"""
Star Wars Galaxy of Heroes Automation Bot
Uses pyautogui and Google Generative AI to automate tedious tasks
"""

import os
import time
import logging
import pyautogui
import cv2
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import mss

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('swgoh_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GameConfig:
    """Configuration for the automation bot"""
    screenshot_delay: float = 0.5
    click_delay: float = 0.2
    confidence_threshold: float = 0.8
    debug_mode: bool = False
    emulator_name: str = "LDPlayer"
    game_package: str = "com.ea.gp.starwarsgalaxyofheroes"

class SWGOHAutomator:
    """Main automation class for Star Wars Galaxy of Heroes"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.setup_ai()
        self.setup_pyautogui()
        
    def setup_ai(self):
        """Initialize Google Generative AI"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        logger.info("Google Generative AI initialized")
        
    def setup_pyautogui(self):
        """Configure pyautogui settings"""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.config.click_delay
        logger.info("PyAutoGUI configured")
        
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen screenshot"""
        with mss.mss() as sct:
            if region:
                monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
                screenshot = sct.grab(monitor)
            else:
                screenshot = sct.grab(sct.monitors[1])  # Assume second monitor is emulator
            
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
            
    def find_image_on_screen(self, template_path: str, confidence: float = None) -> Optional[Tuple[int, int]]:
        """Find template image on screen"""
        if confidence is None:
            confidence = self.config.confidence_threshold
            
        if not os.path.exists(template_path):
            logger.error(f"Template image not found: {template_path}")
            return None
            
        screen = self.capture_screen()
        template = cv2.imread(template_path)
        
        if template is None:
            logger.error(f"Failed to load template: {template_path}")
            return None
            
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            center_x = max_loc[0] + template.shape[1] // 2
            center_y = max_loc[1] + template.shape[0] // 2
            logger.info(f"Found {template_path} at ({center_x}, {center_y}) with confidence {max_val:.2f}")
            return (center_x, center_y)
        else:
            logger.debug(f"Template not found: {template_path} (max confidence: {max_val:.2f})")
            return None
            
    def click_at_position(self, x: int, y: int):
        """Click at specified screen coordinates"""
        pyautogui.click(x, y)
        logger.info(f"Clicked at ({x}, {y})")
        time.sleep(self.config.click_delay)
        
    def click_image(self, template_path: str, confidence: float = None) -> bool:
        """Click on image if found on screen"""
        position = self.find_image_on_screen(template_path, confidence)
        if position:
            self.click_at_position(position[0], position[1])
            return True
        return False
        
    def analyze_screen_with_ai(self, screenshot: np.ndarray, prompt: str) -> str:
        """Use AI to analyze current game state"""
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
        
        try:
            response = self.model.generate_content([prompt, pil_image])
            return response.text
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return ""
            
    def wait_for_image(self, template_path: str, timeout: int = 30, confidence: float = None) -> bool:
        """Wait for an image to appear on screen"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_image_on_screen(template_path, confidence):
                return True
            time.sleep(self.config.screenshot_delay)
        return False
        
    def is_game_running(self) -> bool:
        """Check if SWGOH is running"""
        # This would need to be customized based on your emulator
        return self.click_image("assets/game_icon.png", confidence=0.7)

def main():
    """Main entry point"""
    config = GameConfig()
    automator = SWGOHAutomator(config)
    
    logger.info("SWGOH Automation Bot started")
    
    try:
        # Example usage
        if automator.is_game_running():
            logger.info("Game detected, starting automation...")
            # Add automation logic here
        else:
            logger.warning("Game not detected")
            
    except KeyboardInterrupt:
        logger.info("Automation stopped by user")
    except Exception as e:
        logger.error(f"Automation error: {e}")
    finally:
        logger.info("SWGOH Automation Bot stopped")

if __name__ == "__main__":
    main()
