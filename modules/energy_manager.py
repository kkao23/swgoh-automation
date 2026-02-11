"""
Energy Management Module for SWGOH Automation
Handles automatic energy refills and usage optimization
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from main import SWGOHAutomator

logger = logging.getLogger(__name__)

@dataclass
class EnergyInfo:
    """Energy information structure"""
    cantina_energy: int
    cantina_max: int
    regular_energy: int
    regular_max: int
    fleet_energy: int
    fleet_max: int

class EnergyManager:
    """Manages energy usage and refills for SWGOH"""
    
    def __init__(self, automator: SWGOHAutomator):
        self.automator = automator
        
    def get_current_energy(self) -> Optional[EnergyInfo]:
        """Analyze current energy levels using AI"""
        screenshot = self.automator.capture_screen()
        prompt = """
        Analyze this Star Wars Galaxy of Heroes screen and extract the current energy levels.
        Look for:
        - Cantina energy (current/max)
        - Regular energy (current/max) 
        - Fleet energy (current/max)
        
        Return the results in this format:
        cantina: X/Y
        regular: X/Y
        fleet: X/Y
        """
        
        response = self.automator.analyze_screen_with_ai(screenshot, prompt)
        
        try:
            lines = response.strip().split('\n')
            energy_data = {}
            
            for line in lines:
                if ':' in line:
                    key, values = line.split(':', 1)
                    if '/' in values:
                        current, max_val = values.split('/', 1)
                        energy_data[key.strip()] = (int(current), int(max_val))
            
            return EnergyInfo(
                cantina_energy=energy_data.get('cantina', (0, 0))[0],
                cantina_max=energy_data.get('cantina', (0, 0))[1],
                regular_energy=energy_data.get('regular', (0, 0))[0],
                regular_max=energy_data.get('regular', (0, 0))[1],
                fleet_energy=energy_data.get('fleet', (0, 0))[0],
                fleet_max=energy_data.get('fleet', (0, 0))[1]
            )
        except Exception as e:
            logger.error(f"Failed to parse energy info: {e}")
            return None
            
    def should_refill_energy(self, energy_type: str, threshold: float = 0.8) -> bool:
        """Check if energy should be refilled"""
        energy_info = self.get_current_energy()
        if not energy_info:
            return False
            
        if energy_type == 'cantina':
            current = energy_info.cantina_energy
            max_val = energy_info.cantina_max
        elif energy_type == 'regular':
            current = energy_info.regular_energy
            max_val = energy_info.regular_max
        elif energy_type == 'fleet':
            current = energy_info.fleet_energy
            max_val = energy_info.fleet_max
        else:
            return False
            
        usage_ratio = current / max_val if max_val > 0 else 0
        return usage_ratio < threshold
        
    def refill_energy(self, energy_type: str) -> bool:
        """Refill specified energy type"""
        logger.info(f"Attempting to refill {energy_type} energy")
        
        # Navigate to energy refill screen
        if not self.automator.click_image("assets/energy_button.png"):
            logger.error("Could not find energy button")
            return False
            
        time.sleep(1)
        
        # Select refill type based on energy type
        if energy_type == 'cantina':
            if not self.automator.click_image("assets/cantina_refill.png"):
                logger.error("Could not find cantina refill option")
                return False
        elif energy_type == 'regular':
            if not self.automator.click_image("assets/regular_refill.png"):
                logger.error("Could not find regular refill option")
                return False
        elif energy_type == 'fleet':
            if not self.automator.click_image("assets/fleet_refill.png"):
                logger.error("Could not find fleet refill option")
                return False
                
        # Confirm refill
        time.sleep(0.5)
        if self.automator.click_image("assets/confirm_button.png"):
            logger.info(f"Successfully refilled {energy_type} energy")
            return True
        else:
            logger.error(f"Failed to confirm {energy_type} energy refill")
            return False
            
    def auto_manage_energy(self, refill_threshold: float = 0.2):
        """Automatically manage all energy types"""
        energy_types = ['cantina', 'regular', 'fleet']
        
        for energy_type in energy_types:
            if self.should_refill_energy(energy_type, refill_threshold):
                logger.info(f"Auto-refilling {energy_type} energy")
                self.refill_energy(energy_type)
                time.sleep(2)  # Wait between refills
                
    def wait_for_energy_regen(self, target_energy: int = None, max_wait: int = 3600):
        """Wait for energy to regenerate to target level"""
        if target_energy is None:
            target_energy = self.get_current_energy().regular_max
            
        start_time = time.time()
        while time.time() - start_time < max_wait:
            energy_info = self.get_current_energy()
            if energy_info and energy_info.regular_energy >= target_energy:
                logger.info(f"Target energy reached: {energy_info.regular_energy}")
                return True
                
            logger.info(f"Waiting for energy regen... Current: {energy_info.regular_energy if energy_info else 'Unknown'}")
            time.sleep(60)  # Check every minute
            
        logger.warning("Energy regen timeout")
        return False
