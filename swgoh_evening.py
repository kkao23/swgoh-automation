"""
SWGOH Evening Routine Automation
Based on swgoh_morning.py structure
"""
import time
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import numpy as np
import io
from PIL import Image

try:
    import win32gui
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("Warning: pywin32 not available")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("Warning: mss not available")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: opencv not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SWGOHController:
    """Handles game interaction and AI analysis"""
    
    def __init__(self):
        self.window_rect = None
        self.model = None
        self.setup_ai()
        
    def setup_ai(self):
        """Initialize Google Generative AI"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Google Generative AI initialized")
        
    def find_window(self):
        """Find SWGOH window"""
        if not WINDOWS_AVAILABLE:
            return False
            
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Star Wars" in title or "SWGOH" in title or "Galaxy of Heroes" in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    self.window_rect = {
                        'left': rect[0],
                        'top': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1]
                    }
                    logger.info(f"Found window: {title} at {self.window_rect}")
                    return False
            return True
        
        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            
        if self.window_rect:
            self.focus_window()
            return True
        return False
        
    def focus_window(self):
        """Focus the game window"""
        if not WINDOWS_AVAILABLE or not self.window_rect:
            return
        try:
            hwnd = win32gui.FindWindow(None, "Star Wars: Galaxy of Heroes")
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Could not focus window: {e}")
            
    def press_key(self, key, times=1, delay=0.5):
        """Press a key one or more times"""
        if not PYAUTOGUI_AVAILABLE:
            return
        self.focus_window()
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(delay)
        logger.info(f"Pressed key: {key} x{times}")
        
    def click_at(self, x_percent, y_percent, description=""):
        """Click at percentage position within window"""
        if not PYAUTOGUI_AVAILABLE or not self.window_rect:
            logger.error("Cannot click - pyautogui or window not available")
            return
            
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
        target_x = win_x + (x_percent * win_w)
        target_y = win_y + (y_percent * win_h)

        # Perform the click
        pyautogui.click(target_x, target_y)
        logger.info(f"Targeted Window Pixel {description}: ({target_x}, {target_y})")
        
    def capture_screen(self):
        """Capture screen screenshot"""
        if not MSS_AVAILABLE:
            return None
        try:
            with mss.mss() as sct:
                # Capture game window area
                if self.window_rect:
                    monitor = {
                        "top": self.window_rect['top'],
                        "left": self.window_rect['left'],
                        "width": self.window_rect['width'],
                        "height": self.window_rect['height']
                    }
                else:
                    monitor = sct.monitors[1]
                    
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                if CV2_AVAILABLE:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
            
    def analyze_screen(self, prompt):
        """Send screenshot to AI for analysis"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return "No screenshot available"
            
        # Convert numpy array to PIL Image
        if CV2_AVAILABLE:
            rgb_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = screenshot
            
        pil_image = Image.fromarray(rgb_image)
        
        # Convert to bytes for Gemini API
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        try:
            image_data = {'mime_type': 'image/png', 'data': img_byte_arr.getvalue()}
            response = self.model.generate_content([prompt, image_data])
            return response.text
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"Analysis error: {e}"


class EveningRoutine:
    """Implements the 5-step evening routine"""
    
    def __init__(self, controller):
        self.controller = controller
        
    def step1_coliseum(self):
        # """Step 1: Coliseum"""
        logger.info("\n=== STEP 1: Coliseum ===")
        
        # Press F, wait 2 seconds
        self.controller.press_key('f')
        time.sleep(10)
        
        # Click at (.9, .95) twice
        logger.info("Clicking at (.9, .95) first time...")
        self.controller.click_at(0.9, 0.95, "Coliseum action 1")
        time.sleep(1)
        
        logger.info("Clicking at (.9, .95) second time...")
        self.controller.click_at(0.9, 0.95, "Coliseum action 2")
        time.sleep(1)
        
        # Wait 10 seconds
        logger.info("Waiting 10 seconds...")
        time.sleep(10)
        
        # Press C, wait 3 minutes
        self.controller.press_key('c')
        logger.info("Waiting 3 minutes...")
        time.sleep(180)  # 3 minutes = 180 seconds

        # Click anywhere on screen once
        logger.info("Clicking anywhere on screen once...")
        self.controller.click_at(0.5, 0.7, "Continue")
        time.sleep(2)
        # Click anywhere on screen once
        logger.info("Clicking continue...")
        self.controller.click_at(0.5, 0.7, "Continue")
        time.sleep(3)

        logger.info("Returning to home screen...")
        self.controller.press_key('esc', times=1, delay=3)
        
    def step2_claim_quests(self):
        """Step 2: Claim existing quests"""
        logger.info("\n=== STEP 2: Claim Existing Quests ===")
        
        # Press C, wait a second
        self.controller.press_key('c')
        time.sleep(1)
        
        # Send screenshot to AI to count green Claim buttons on the right side
        logger.info("Asking AI to count green Claim buttons on the right side...")
        analysis = self.controller.analyze_screen("""
        Look at the right side of this SWGOH quests screen.
        Count how many green "Claim" buttons are visible on the right side.
        These are usually rectangular green buttons with white "Claim" text.
        
        Respond with ONLY a single number representing the count.
        Example: 5
        If no claim buttons are visible, respond with: 0
        """)
        
        logger.info(f"AI response: {analysis}")
        
        # Parse the number from AI response
        import re
        match = re.search(r'(\d+)', analysis)
        if match:
            claim_count = int(match.group(1))
        else:
            logger.warning("Could not parse claim count from AI response, defaulting to 5")
            claim_count = 5
            
        logger.info(f"Found {claim_count} claim buttons to click")
        
        # Click at (.9, .2) that many times, pausing 2 seconds between each
        for i in range(claim_count):
            logger.info(f"Clicking claim button {i+1}/{claim_count} at (.9, .27)...")
            self.controller.click_at(0.9, 0.27, f"Claim button {i+1}")
            time.sleep(2)
            
    def step3_galactic_war(self):
        """Step 3: Galactic War battle"""
        logger.info("\n=== STEP 3: Galactic War Battle ===")
        
        # Click sequence: (.9, .2), (.1, .95), (.5, .95), (0.5, 0.63)
        logger.info("Clicking at (.9, .27)...")
        self.controller.click_at(0.9, 0.27, "Galactic War step 1")
        time.sleep(1)
        
        logger.info("Clicking at (.1, .95)...")
        self.controller.click_at(0.1, 0.95, "Galactic War step 2")
        time.sleep(1)
        
        logger.info("Clicking at (.5, .95)...")
        self.controller.click_at(0.5, 0.95, "Galactic War step 3")
        time.sleep(1)
        
        logger.info("Clicking at (0.5, 0.63)...")
        self.controller.click_at(0.5, 0.63, "Galactic War step 4")
        time.sleep(1)
        
        # Press esc several times to return to the home screen
        logger.info("Returning to home screen...")
        self.controller.press_key('esc', times=3, delay=1)
        
    def step4_challenges(self):
        """Step 4: Finish 2 challenges"""
        logger.info("\n=== STEP 4: Finish 2 Challenges ===")
        
        # Press C
        self.controller.press_key('c')
        time.sleep(1)
        
        # Click sequence: (.9, .2), (.9, .2), (.9, .15), (0.5, 0.63)
        logger.info("Clicking at (.9, .27) first time...")
        self.controller.click_at(0.9, 0.27, "Challenges step 1")
        time.sleep(1)
        
        logger.info("Clicking at (.9, .27) second time...")
        self.controller.click_at(0.9, 0.27, "Challenges step 2")
        time.sleep(1)
        
        logger.info("Clicking at (.9, .15)...")
        self.controller.click_at(0.9, 0.15, "Challenges step 3")
        time.sleep(1)
        
        logger.info("Clicking at (0.5, 0.63)...")
        self.controller.click_at(0.5, 0.63, "Challenges step 4")
        time.sleep(1)
        
        # Press esc several times to return to the home screen
        logger.info("Returning to home screen...")
        self.controller.press_key('esc', times=5, delay=1.5)
        
    def step5_fleet_challenge(self):
        """Step 5: Finish 1 fleet challenge"""
        logger.info("\n=== STEP 5: Finish 1 Fleet Challenge ===")
        
        # Press C
        self.controller.press_key('c')
        time.sleep(1)
        
        # Click sequence: (.9, .2), (.9, .2), (.9, .15), (0.5, 0.63)
        logger.info("Clicking at (.9, .27) first time...")
        self.controller.click_at(0.9, 0.27, "Fleet Challenge step 1")
        time.sleep(1)
        
        logger.info("Clicking at (.9, .27) second time...")
        self.controller.click_at(0.9, 0.27, "Fleet Challenge step 2")
        time.sleep(1)
        
        logger.info("Clicking at (.9, .15)...")
        self.controller.click_at(0.9, 0.15, "Fleet Challenge step 3")
        time.sleep(1)
        
        logger.info("Clicking at (0.5, 0.63)...")
        self.controller.click_at(0.5, 0.63, "Fleet Challenge step 4")
        time.sleep(1)
        
        # Press esc several times to return to the home screen
        logger.info("Returning to home screen...")
        self.controller.press_key('esc', times=4, delay=0.5)
        
    def step6_claim_energy(self):
        """Step 6: Claim Energy"""
        logger.info("\n=== STEP 6: Claim Energy ===")
        
        # Press C
        self.controller.press_key('c')
        time.sleep(1)
                
        logger.info("Clicking at (0.25, 0.95)...")
        self.controller.click_at(0.25, 0.95, "Claim Energy step 3")
        time.sleep(1)
        
        # Click sequence: (0.9, 0.27), (0.25, 0.45), (0.25, 0.95)
        logger.info("Clicking at (0.9, 0.27)...")
        self.controller.click_at(0.9, 0.27, "Claim Energy step 1")
        time.sleep(1)
        
        logger.info("Clicking at (0.25, 0.45)...")
        self.controller.click_at(0.25, 0.45, "Claim Energy step 2")
        time.sleep(1)
        
        logger.info("Pressing esc...")
        self.controller.press_key('esc', times=2, delay=0.5)
        time.sleep(1)
        
    def step7_fleet_battles(self):
        """Step 7: Fleet Battles Multi-Sim"""
        logger.info("\n=== STEP 7: Fleet Battles ===")
        
        # Press U then S for Fleet Battles
        self.controller.press_key('u')
        time.sleep(1)
        self.controller.press_key('s')
        time.sleep(2)
        
        # Click Multi Sim button
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # Click Sim button on modal
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
        
    def step8_light_side_battles(self):
        """Step 8: Light Side Battles Multi-Sim"""
        logger.info("\n=== STEP 8: Light Side Battles ===")
        
        # Press D for Campaigns
        self.controller.press_key('d')
        time.sleep(2)
        
        # Click Light Side Play button
        logger.info("Clicking Light Side Play button...")
        self.controller.click_at(0.3, 0.75, "Play")
        time.sleep(2)
        
        # Click Multi Sim button
        logger.info("Clicking Multi Sim button (Static Config)...")
        self.controller.click_at(0.82, 0.87, "Multi Sim Button")
        time.sleep(2)
        
        # Click Sim button on modal
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
        self.controller.press_key('esc', times=4, delay=0.5)
        time.sleep(1)
        
    def run_full_routine(self):
        """Execute all 8 steps in sequence"""
        logger.info("="*60)
        logger.info("STARTING SWGOH EVENING ROUTINE")
        logger.info("="*60)
        
        steps = [
            self.step1_coliseum,
            self.step2_claim_quests,
            self.step3_galactic_war,
            self.step4_challenges,
            self.step5_fleet_challenge,
            self.step6_claim_energy,
            self.step7_fleet_battles,
            self.step8_light_side_battles,
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
        logger.info("EVENING ROUTINE COMPLETED")
        logger.info("="*60)


def main():
    """Main entry point with multi-step support"""
    
    # Define available steps
    steps_map = {
        1: ("Coliseum", "step1_coliseum"),
        2: ("Claim Existing Quests", "step2_claim_quests"),
        3: ("Galactic War Battle", "step3_galactic_war"),
        4: ("Finish 2 Challenges", "step4_challenges"),
        5: ("Finish 1 Fleet Challenge", "step5_fleet_challenge"),
        6: ("Claim Energy", "step6_claim_energy"),
        7: ("Fleet Battles", "step7_fleet_battles"),
        8: ("Light Side Battles", "step8_light_side_battles"),
    }
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        try:
            # Parse all arguments as step numbers
            step_nums = [int(arg) for arg in sys.argv[1:]]
            
            # Validate all step numbers
            invalid_steps = [n for n in step_nums if n < 1 or n > 8]
            if invalid_steps:
                print(f"Invalid step numbers: {invalid_steps}")
                print("Step numbers must be between 1 and 8")
                return
            
            step_names = [steps_map[n][0] for n in step_nums]
            print(f"SWGOH Evening Automation - Running Steps: {', '.join(map(str, step_nums))}")
            print(f"Steps: {', '.join(step_names)}")
            print("Make sure the game is open and visible!")
            print("Starting in 5 seconds... (Press Ctrl+C to cancel)")
            time.sleep(5)
            
            controller = SWGOHController()
            if not controller.find_window():
                logger.error("Could not find SWGOH window. Is the game open?")
                return
                
            routine = EveningRoutine(controller)
            steps = [
                routine.step1_coliseum,
                routine.step2_claim_quests,
                routine.step3_galactic_war,
                routine.step4_challenges,
                routine.step5_fleet_challenge,
                routine.step6_claim_energy,
                routine.step7_fleet_battles,
                routine.step8_light_side_battles,
            ]
            
            for i, step_num in enumerate(step_nums, 1):
                logger.info(f"\n--- Executing Step {i}/{len(step_nums)} (Step {step_num}: {steps_map[step_num][0]}) ---")
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
        print("Usage: python swgoh_evening.py [step_numbers...]")
        print("Examples:")
        print("  python swgoh_evening.py           # Run all steps")
        print("  python swgoh_evening.py 5         # Run step 5 only")
        print("  python swgoh_evening.py 5 6 7     # Run steps 5, 6, and 7")
        print("\nSteps:")
        for num, (name, _) in steps_map.items():
            print(f"  {num}: {name}")
        return
    
    # Full routine (no arguments)
    print("SWGOH Evening Automation")
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
        routine = EveningRoutine(controller)
        routine.run_full_routine()
        
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
