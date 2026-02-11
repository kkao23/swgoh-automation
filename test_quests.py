#!/usr/bin/env python3
"""
Test script for SWGOH Automation
Tests window detection, keyboard input, and game state reading
Setup: 3440x1440 screen, SWGOH windowed at 1952x1096
"""

import time
import logging
import pyautogui
import cv2
import numpy as np
from PIL import Image
import pygetwindow as gw
import mss
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SWGOHWindow:
    """Handles SWGOH window detection and interaction"""
    
    def __init__(self, target_width=1952, target_height=1096):
        self.target_width = target_width
        self.target_height = target_height
        self.window = None
        self.window_rect = None
        
    def find_swgo_window(self):
        """Find SWGOH window by size or title"""
        logger.info("Looking for SWGOH window...")
        
        # Try to find by window title
        window_titles = [
            "Star Wars: Galaxy of Heroes",
            "Galaxy of Heroes",
            "SWGOH",
            "Star Wars"
        ]
        
        for title in window_titles:
            try:
                windows = gw.getWindowsWithTitle(title)
                for window in windows:
                    logger.info(f"Found window: {window.title} - Size: {window.width}x{window.height}")
                    
                    # Check if size matches expected SWGOH window
                    if (abs(window.width - self.target_width) < 50 and 
                        abs(window.height - self.target_height) < 50):
                        self.window = window
                        self.window_rect = {
                            'left': window.left,
                            'top': window.top,
                            'width': window.width,
                            'height': window.height
                        }
                        logger.info(f"SWGOH window found at: {self.window_rect}")
                        return True
            except Exception as e:
                logger.debug(f"Error searching for title '{title}': {e}")
                
        # If not found by title, look for window with matching dimensions
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if window.width > 0 and window.height > 0:  # Valid window
                    if (abs(window.width - self.target_width) < 50 and 
                        abs(window.height - self.target_height) < 50):
                        self.window = window
                        self.window_rect = {
                            'left': window.left,
                            'top': window.top,
                            'width': window.width,
                            'height': window.height
                        }
                        logger.info(f"Found window by dimensions: {window.title} at {self.window_rect}")
                        return True
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            
        logger.error("Could not find SWGOH window")
        return False
        
    def focus_window(self):
        """Bring window to foreground"""
        if self.window:
            try:
                self.window.activate()
                time.sleep(0.5)  # Wait for window to focus
                logger.info("Window focused")
                return True
            except Exception as e:
                logger.error(f"Could not focus window: {e}")
        return False
        
    def capture_window(self):
        """Capture screenshot of the SWGOH window"""
        if not self.window_rect:
            logger.error("No window detected")
            return None
            
        try:
            with mss.mss() as sct:
                monitor = {
                    'left': self.window_rect['left'],
                    'top': self.window_rect['top'],
                    'width': self.window_rect['width'],
                    'height': self.window_rect['height']
                }
                
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                logger.info(f"Screenshot captured: {img.shape}")
                return img
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
            
    def press_key(self, key):
        """Press a key while window is focused"""
        if self.focus_window():
            time.sleep(0.2)
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            time.sleep(0.5)  # Wait for UI response
            return True
        return False

class GameStateAnalyzer:
    """Analyzes game state using AI"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("AI analyzer initialized")
        
    def analyze_quests_screen(self, screenshot):
        """Analyze the quests menu screen"""
        if screenshot is None:
            return "No screenshot available"
            
        # Convert numpy array to PIL Image
        rgb_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Convert to bytes for Gemini API
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        prompt = """
        Analyze this Star Wars Galaxy of Heroes quests/daily activities screen.
        
        Provide a detailed breakdown of:
        1. What quest categories are visible (Daily, Weekly, Guild, etc.)
        2. Which quests are completed vs incomplete
        3. Any rewards ready to claim
        4. Current progress on active quests
        5. Time remaining for daily reset if visible
        
        Format your response clearly with bullet points.
        """
        
        try:
            image_data = {'mime_type': 'image/png', 'data': img_byte_arr.getvalue()}
            response = self.model.generate_content([prompt, image_data])
            return response.text
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"Analysis error: {e}"
            
    def analyze_general_state(self, screenshot):
        """General game state analysis"""
        if screenshot is None:
            return "No screenshot available"
            
        rgb_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Convert to bytes for Gemini API
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        prompt = """
        Analyze this Star Wars Galaxy of Heroes screen.
        
        Tell me:
        1. What screen/menu is currently open?
        2. What buttons or options are visible?
        3. Are there any notifications or alerts?
        4. What's the general state of the game interface?
        
        Be specific about UI elements you can see.
        """
        
        try:
            image_data = {'mime_type': 'image/png', 'data': img_byte_arr.getvalue()}
            response = self.model.generate_content([prompt, image_data])
            return response.text
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"Analysis error: {e}"

def save_screenshot(screenshot, filename="test_screenshot.png"):
    """Save screenshot for debugging"""
    try:
        cv2.imwrite(filename, screenshot)
        logger.info(f"Screenshot saved: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        return False

def main():
    """Main test sequence"""
    logger.info("="*50)
    logger.info("SWGOH Automation Test - Quest Menu Test")
    logger.info("="*50)
    
    # Initialize components
    window = SWGOHWindow(target_width=1952, target_height=1096)
    
    try:
        analyzer = GameStateAnalyzer()
    except ValueError as e:
        logger.error(f"Failed to initialize AI: {e}")
        return
    
    # Step 1: Find SWGOH window
    logger.info("\n[Step 1] Finding SWGOH window...")
    if not window.find_swgo_window():
        logger.error("Could not find SWGOH window. Make sure the game is open.")
        return
        
    # Step 2: Capture initial state
    logger.info("\n[Step 2] Capturing initial game state...")
    initial_screenshot = window.capture_window()
    if initial_screenshot is not None:
        save_screenshot(initial_screenshot, "initial_state.png")
        
        logger.info("Analyzing initial state...")
        initial_analysis = analyzer.analyze_general_state(initial_screenshot)
        logger.info(f"\nInitial State Analysis:\n{initial_analysis}")
    
    # Step 3: Press 'C' to open quests
    logger.info("\n[Step 3] Pressing 'C' to open quests menu...")
    if not window.press_key('c'):
        logger.error("Failed to press 'C' key")
        return
        
    # Wait for menu to open
    logger.info("Waiting for quests menu to open...")
    time.sleep(2)
    
    # Step 4: Capture quests menu
    logger.info("\n[Step 4] Capturing quests menu...")
    quests_screenshot = window.capture_window()
    if quests_screenshot is not None:
        save_screenshot(quests_screenshot, "quests_menu.png")
        
        # Step 5: Analyze quests menu
        logger.info("\n[Step 5] Analyzing quests menu with AI...")
        quests_analysis = analyzer.analyze_quests_screen(quests_screenshot)
        logger.info(f"\nQuests Analysis:\n{quests_analysis}")
        
        # Display results
        print("\n" + "="*50)
        print("TEST RESULTS")
        print("="*50)
        print(f"\nWindow found: {window.window_rect}")
        print(f"Initial screenshot: initial_state.png")
        print(f"Quests screenshot: quests_menu.png")
        print(f"\nAI Analysis:\n{quests_analysis}")
        print("\n" + "="*50)
    else:
        logger.error("Failed to capture quests menu screenshot")
        
    logger.info("\nTest completed!")

if __name__ == "__main__":
    # Safety check
    print("WARNING: This script will take control of your mouse and keyboard.")
    print("Make sure SWGOH is open and visible.")
    print("You have 3 seconds to cancel (Ctrl+C)...")
    
    try:
        time.sleep(3)
        main()
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
