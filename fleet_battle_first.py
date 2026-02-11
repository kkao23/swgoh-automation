"""
Fleet Battle First - Key Sequence Script
Presses a series of keys with 3-second pauses
"""
import time
import logging

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available")

try:
    import win32gui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def focus_window():
    """Focus the game window"""
    if not WINDOWS_AVAILABLE:
        return
    try:
        hwnd = win32gui.FindWindow(None, "Star Wars: Galaxy of Heroes")
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Could not focus window: {e}")


def press_key(key):
    """Press a single key"""
    if not PYAUTOGUI_AVAILABLE:
        return
    focus_window()
    pyautogui.press(key)
    logger.info(f"Pressed: {key}")


def main():
    """Execute the key sequence"""
    print("Fleet Battle First Key Sequence")
    print("Make sure the game is open and visible!")
    print("Starting in 5 seconds... (Press Ctrl+C to cancel)")
    
    try:
        time.sleep(5)
        
        # Key sequence: E S W W E Q Q Q T Down Arrow Down Arrow C
        keys = [
            'e', 's', 'w', 'w', 'e', 'q', 'q', 'q', 't', 'down', 'down', 'c'
        ]
        
        for i, key in enumerate(keys, 1):
            press_key(key)
            if i < len(keys):  # Don't pause after the last key
                time.sleep(7)
        
        logger.info("\nKey sequence completed!")
        
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
