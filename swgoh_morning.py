#!/usr/bin/env python3
"""
SWGOH Daily Automation - 7 Step Routine
Automates the complete daily sequence for Star Wars Galaxy of Heroes
Screen: 3440x1440, Game Window: 1952x1096
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

class SWGOHController:
    """Main controller for SWGOH automation"""
    
    def __init__(self, target_width=1952, target_height=1096):
        self.target_width = target_width
        self.target_height = target_height
        self.window = None
        self.window_rect = None
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Initialize AI
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def find_window(self):
        """Find SWGOH window"""
        logger.info("Finding SWGOH window...")
        window_titles = ["Star Wars: Galaxy of Heroes", "Galaxy of Heroes", "SWGOH", "Star Wars"]
        
        for title in window_titles:
            try:
                windows = gw.getWindowsWithTitle(title)
                for window in windows:
                    if (abs(window.width - self.target_width) < 100 and 
                        abs(window.height - self.target_height) < 100):
                        self.window = window
                        self.window_rect = {
                            'left': window.left,
                            'top': window.top,
                            'width': window.width,
                            'height': window.height
                        }
                        logger.info(f"Found window: {window.title} at {self.window_rect}")
                        return True
            except Exception as e:
                continue
                
        # Search by dimensions
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if (abs(window.width - self.target_width) < 100 and 
                    abs(window.height - self.target_height) < 100):
                    self.window = window
                    self.window_rect = {
                        'left': window.left,
                        'top': window.top,
                        'width': window.width,
                        'height': window.height
                    }
                    logger.info(f"Found window by size: {window.title} at {self.window_rect}")
                    return True
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            
        return False
        
    def focus_window(self):
        """Focus the game window"""
        if self.window:
            try:
                self.window.activate()
                time.sleep(0.5)
                return True
            except:
                pass
        return False
        
    def capture_window(self):
        """Take screenshot of game window"""
        if not self.window_rect:
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
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
            
    def analyze_screen(self, prompt_text):
        """Analyze current screen with AI"""
        screenshot = self.capture_window()
        if screenshot is None:
            return None
            
        rgb_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        try:
            image_data = {'mime_type': 'image/png', 'data': img_byte_arr.getvalue()}
            response = self.model.generate_content([prompt_text, image_data])
            return response.text
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
            
    def press_key(self, key, times=1, delay=0.3):
        """Press keyboard key"""
        self.focus_window()
        time.sleep(0.2)
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(delay)
        logger.info(f"Pressed key: {key} x{times}")
        
    def click_at(self, ai_x, ai_y, description=""):
        # Ensure window rect exists
        if not self.window_rect:
            logger.error("Window rect not found")
            return

        # Access window_rect using dictionary keys
        win_x = self.window_rect['left']
        win_y = self.window_rect['top']
        win_w = self.window_rect['width']
        win_h = self.window_rect['height']

        # Calculate target pixels (Input is 0.0 to 1.0 float)
        target_x = win_x + (ai_x * win_w)
        target_y = win_y + (ai_y * win_h)

        # Perform the click
        pyautogui.click(target_x, target_y)
        logger.info(f"Targeted Window Pixel {description}: ({target_x}, {target_y})")
        
    def wait_for_screen_change(self, timeout=5):
        """Wait for screen to change"""
        time.sleep(timeout)
        
    def is_popup_present(self):
        """Check if a popup/modal is present"""
        analysis = self.analyze_screen("""
        Is there a popup dialog, modal, or notification visible on this screen?
        Look for:
        - Centered dialog boxes
        - Notification popups
        - Confirmation dialogs
        - Overlay screens
        
        Answer ONLY with: YES or NO
        """)
        return analysis and "YES" in analysis.upper()
        
    def find_button_with_ai(self, button_description, min_y=0.0, max_y=1.0):
        """Use AI to find button coordinates, filtering by vertical position"""
        analysis = self.analyze_screen(f"""
        Find the "{button_description}" on this SWGOH screen.
        
        Return the coordinates of the center of the button as percentages:
        - x_percent: percentage from left (0-100)
        - y_percent: percentage from top (0-100)
        
        Format: x_percent,y_percent
        Example: 50,60
        
        If button not found, return: NOT_FOUND
        """)
        
        if not analysis or "NOT_FOUND" in analysis.upper():
            logger.warning(f"AI could not find button: {button_description}")
            return None
            
        try:
            import re
            match = re.search(r'(\d{1,3})[,.]\s*(\d{1,3})', analysis)
            if match:
                x = int(match.group(1)) / 100.0
                y = int(match.group(2)) / 100.0
                
                # NEW: Validate coordinates against constraints
                if y < min_y or y > max_y:
                    logger.warning(f"AI found object at {y*100}% height, but we expected between {min_y*100}%-{max_y*100}%. Ignoring.")
                    return None
                    
                logger.info(f"AI found '{button_description}' at ({x*100:.0f}%, {y*100:.0f}%)")
                return (x, y)
        except Exception as e:
            logger.error(f"Failed to parse coordinates: {e}")
            
        return None
    
    # Update the definition line to include y_offset (default 0)
    def click_button_with_ai(self, button_description, fallback_x=0.8, fallback_y=0.9, y_offset=0):
        """Click button using AI-detected coordinates, with fallback and offset"""
        coords = self.find_button_with_ai(button_description)
        
        if coords:
            # Apply the offset to the AI's detected Y coordinate
            adjusted_y = coords[1] + y_offset
            return self.click_at(coords[0], adjusted_y, button_description)
        else:
            logger.warning(f"Using fallback coordinates for {button_description}")
            return self.click_at(fallback_x, fallback_y, f"{button_description} (fallback)")

class DailyRoutine:
    """Implements the 7-step daily routine"""
    
    def __init__(self, controller):
        self.controller = controller
        
    def step1_claim_quests(self):
        """Step 1: Claim daily quest rewards"""
        logger.info("\n=== STEP 1: Claim Daily Quests ===")
        
        # Open quests menu
        self.controller.press_key('c')
        time.sleep(2)
        
        logger.info("Clicking at (0.25, 0.95)...")
        self.controller.click_at(0.25, 0.95, "Claim Energy step 3")
        time.sleep(1)
            
        # Return to home screen
        self.controller.press_key('esc', times=1, delay=0.5)
        time.sleep(1)
        
    def step2_energy_refill(self):
        """Step 2: Energy already purchased manually, skip to battles"""
        logger.info("\n=== STEP 2: Energy ===")
        logger.info("Skipping - energy already purchased manually")
        time.sleep(0.5)
        
    def step3_mod_battles(self):
        """Step 3: Mod Battles Multi-Sim"""
        logger.info("\n=== STEP 3: Mod Battles ===")
        
        # 1. Open Mod Battles
        self.controller.press_key('e')
        time.sleep(2)
        
        # 2. CLICK MULTI SIM (Fixed Coordinate)
        # The button is always in the bottom right. 
        # 0.82 (82% across) and 0.85 (85% down) is the "Safe Zone" 
        # that hits the button but avoids the bottom window border.
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # 3. CONFIRM POPUP (Keep AI here, as popups can vary)
        logger.info("Clicking Sim button (Static Config)...")
        self.controller.click_at(0.5, 0.63, "Sim Button")

        time.sleep(3)
        
        # ... (rest of the energy check code remains the same) ...
        analysis = self.controller.analyze_screen("""
        Is there a popup asking if you want to buy more energy or refill energy?
        Look for text about "Buy Energy" or "Refill" or "Not enough energy".
        
        Answer: YES or NO
        """)
        
        if analysis and "YES" in analysis.upper():
            logger.info("Energy popup detected, closing...")
            self.controller.press_key('esc')
            time.sleep(0.5)
            
        self.controller.press_key('esc', times=2, delay=0.5)
        time.sleep(1)
        
    def step4_fleet_battles(self):
        """Step 4: Fleet Battles Multi-Sim"""
        logger.info("\n=== STEP 4: Fleet Battles ===")
        
        # Press U then S for Fleet Battles
        self.controller.press_key('u')
        time.sleep(1)
        self.controller.press_key('s')
        time.sleep(2)
        
        # Use AI to find Multi Sim button
        # CONSTRAINT ADDED: min_y=0.80 (Must be in bottom 20% of screen)
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # 3. CONFIRM POPUP (Keep AI here, as popups can vary)
        logger.info("Clicking Sim button (Static Config)...")
        self.controller.click_at(0.5, 0.63, "Sim Button")
        time.sleep(3)
        
        # Check for energy popup
        analysis = self.controller.analyze_screen("""
        Is there a popup asking if you want to buy more energy or refill energy?
        Answer: YES or NO
        """)
        
        if analysis and "YES" in analysis.upper():
            logger.info("Energy popup detected, closing...")
            self.controller.press_key('esc')
            time.sleep(0.5)
            
        # Return to home screen
        self.controller.press_key('esc', times=3, delay=1)
        time.sleep(1)
        
    def step5_light_side_battles(self):
        """Step 5: Light Side Battles Multi-Sim"""
        logger.info("\n=== STEP 5: Light Side Battles ===")
        
        # Press D for Campaigns
        self.controller.press_key('d')
        time.sleep(2)
        
        # Use AI to find Light Side Play button
        logger.info("Finding Light Side Play button with AI...")
        self.controller.click_at(0.3, 0.75, "Play")
        time.sleep(2)
        
# Use AI to find Multi Sim button
        # CONSTRAINT ADDED: min_y=0.80 (Must be in bottom 20% of screen)
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # 3. CONFIRM POPUP (Keep AI here, as popups can vary)
        logger.info("Clicking Sim button (Static Config)...")
        self.controller.click_at(0.5, 0.63, "Sim Button")
        time.sleep(3)
        
        # Check for energy popup
        analysis = self.controller.analyze_screen("""
        Is there a popup asking if you want to buy more energy?
        Answer: YES or NO
        """)
        
        if analysis and "YES" in analysis.upper():
            logger.info("Energy popup detected, closing...")
            self.controller.press_key('esc')
            time.sleep(0.5)
            
        # Return to home screen
        self.controller.press_key('esc', times=3, delay=1)
        time.sleep(1)
        
    def step6_cantina_battles(self):
        """Step 6: Cantina Battles Multi-Sim"""
        logger.info("\n=== STEP 6: Cantina Battles ===")
        
        # Press D for Campaigns
        self.controller.press_key('d')
        time.sleep(2)
        
        # Use AI to find Cantina Play button
        logger.info("Finding Cantina Play button with AI...")
        self.controller.click_at(0.7, 0.75, "Play")
        time.sleep(2)
        
# Use AI to find Multi Sim button
        # CONSTRAINT ADDED: min_y=0.80 (Must be in bottom 20% of screen)
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # 3. CONFIRM POPUP (Keep AI here, as popups can vary)
        logger.info("Clicking Sim button (Static Config)...")
        self.controller.click_at(0.5, 0.63, "Sim Button")
        time.sleep(3)
        
        # Check for energy popup
        analysis = self.controller.analyze_screen("""
        Is there a popup asking if you want to buy more energy?
        Answer: YES or NO
        """)
        
        if analysis and "YES" in analysis.upper():
            logger.info("Energy popup detected, closing...")
            self.controller.press_key('esc')
            time.sleep(0.5)
            
        # Return to home screen
        self.controller.press_key('esc', times=3, delay=1)
        time.sleep(1)
        
    def run_full_routine(self):
        """Execute all 7 steps in sequence"""
        logger.info("="*60)
        logger.info("STARTING SWGOH DAILY ROUTINE")
        logger.info("="*60)
        
        steps = [
            self.step1_claim_quests,
            self.step2_energy_refill,
            self.step3_mod_battles,
            self.step4_fleet_battles,
            self.step5_light_side_battles,
            self.step6_cantina_battles,
        ]
        
        for i, step in enumerate(steps, 1):
            try:
                logger.info(f"\n--- Executing Step {i}/{len(steps)} ---")
                step()
                time.sleep(1)  # Brief pause between steps
            except Exception as e:
                logger.error(f"Step {i} failed: {e}")
                # Try to recover to home screen
                try:
                    self.controller.press_key('esc', times=5, delay=0.3)
                except:
                    pass
                    
        logger.info("\n" + "="*60)
        logger.info("DAILY ROUTINE COMPLETED")
        logger.info("="*60)

def main():
    """Main entry point with multi-step support"""
    import sys
    
    # Define available steps
    steps_map = {
        1: "Claim Quests",
        2: "Energy (skipped)",
        3: "Mod Battles",
        4: "Fleet Battles",
        5: "Light Side Battles",
        6: "Cantina Battles",
    }
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        try:
            # Parse all arguments as step numbers
            step_nums = [int(arg) for arg in sys.argv[1:]]
            
            # Validate all step numbers
            invalid_steps = [n for n in step_nums if n < 1 or n > 6]
            if invalid_steps:
                print(f"Invalid step numbers: {invalid_steps}")
                print("Step numbers must be between 1 and 6")
                return
            
            step_names = [steps_map[n] for n in step_nums]
            print(f"SWGOH Daily Automation - Running Steps: {', '.join(map(str, step_nums))}")
            print(f"Steps: {', '.join(step_names)}")
            print("Make sure the game is open and visible!")
            print("Starting in 5 seconds... (Press Ctrl+C to cancel)")
            time.sleep(5)
            
            controller = SWGOHController()
            if not controller.find_window():
                logger.error("Could not find SWGOH window. Is the game open?")
                return
                
            routine = DailyRoutine(controller)
            steps = [
                routine.step1_claim_quests,
                routine.step2_energy_refill,
                routine.step3_mod_battles,
                routine.step4_fleet_battles,
                routine.step5_light_side_battles,
                routine.step6_cantina_battles,
            ]
            
            for i, step_num in enumerate(step_nums, 1):
                logger.info(f"\n--- Executing Step {i}/{len(step_nums)} (Step {step_num}: {steps_map[step_num]}) ---")
                try:
                    steps[step_num - 1]()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Step {step_num} failed: {e}")
                    # Try to recover to home screen
                    try:
                        controller.press_key('esc', times=5, delay=0.3)
                    except:
                        pass
                        
            logger.info(f"\n--- Selected Steps Complete ---")
            return
            
        except ValueError:
            # Not all arguments are valid integers, show usage
            pass
    
    # Show usage if invalid arguments or no arguments provided
    if len(sys.argv) > 1:
        print("Usage: python swgoh_morning.py [step_numbers...]")
        print("Examples:")
        print("  python swgoh_morning.py           # Run all steps")
        print("  python swgoh_morning.py 3         # Run step 3 only")
        print("  python swgoh_morning.py 3 4 5 6  # Run steps 3, 4, 5, and 6")
        print("\nSteps:")
        for num, name in steps_map.items():
            print(f"  {num}: {name}")
        return
    
    # Full routine (no arguments)
    print("SWGOH Daily Automation")
    print("Make sure the game is open and visible!")
    print("Starting in 5 seconds... (Press Ctrl+C to cancel)")
    
    try:
        time.sleep(5)
        
        # Initialize controller
        controller = SWGOHController()
        
        # Find game window
        if not controller.find_window():
            logger.error("Could not find SWGOH window. Is the game open?")
            return
            
        # Run routine
        routine = DailyRoutine(controller)
        routine.run_full_routine()
        
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
