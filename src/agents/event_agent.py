"""
Event Agent - Rule-based event decision making.
Determines actions (ALLOW, ALERT, LOG_ONLY) based on rules.
"""
import json
from pathlib import Path
from typing import Dict, Optional

from utils.logger import logger


class EventAgent:
    """Agent responsible for making event decisions based on rules."""
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize event agent with rules.
        
        Args:
            rules_path: Path to rules JSON file. Defaults to config/rules.json
        """
        if rules_path is None:
            rules_path = Path(__file__).parent.parent.parent / "config" / "rules.json"
        
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        logger.info("Event agent initialized")
    
    def _load_rules(self) -> Dict:
        """Load rules from JSON file."""
        try:
            if self.rules_path.exists():
                with open(self.rules_path, 'r') as f:
                    rules = json.load(f)
                logger.info(f"Rules loaded from {self.rules_path}")
                return rules
            else:
                logger.warning(f"Rules file not found: {self.rules_path}, using defaults")
                return {
                    "event_rules": [],
                    "blacklisted_plates": [],
                    "authorized_plates": []
                }
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            return {
                "event_rules": [],
                "blacklisted_plates": [],
                "authorized_plates": []
            }
    
    def decide(self, plate_text: str, is_valid: bool, vehicle_info: Optional[Dict] = None) -> Dict:
        """
        Make a decision based on rules.
        
        Args:
            plate_text: Normalized license plate text
            is_valid: Whether plate format is valid
            vehicle_info: Optional vehicle information (is_authorized, is_blacklisted)
        
        Returns:
            Dictionary with 'action' (ALLOW, ALERT, LOG_ONLY), 'rule_name', and 'description'
        """
        try:
            # If plate is invalid, log only
            if not is_valid:
                return {
                    "action": "LOG_ONLY",
                    "rule_name": "invalid_plate_format",
                    "description": "Invalid plate format detected"
                }
            
            # Check blacklisted plates
            blacklisted = self.rules.get("blacklisted_plates", [])
            if plate_text in blacklisted or (vehicle_info and vehicle_info.get("is_blacklisted")):
                return {
                    "action": "ALERT",
                    "rule_name": "blacklisted_vehicle",
                    "description": f"Blacklisted vehicle detected: {plate_text}"
                }
            
            # Check authorized plates (if applicable)
            authorized = self.rules.get("authorized_plates", [])
            if authorized:  # Only if authorization list is defined
                if plate_text not in authorized and (not vehicle_info or not vehicle_info.get("is_authorized")):
                    return {
                        "action": "ALERT",
                        "rule_name": "unauthorized_entry",
                        "description": f"Unauthorized vehicle detected: {plate_text}"
                    }
            
            # Default: Allow normal entry
            return {
                "action": "ALLOW",
                "rule_name": "normal_entry",
                "description": f"Vehicle allowed: {plate_text}"
            }
            
        except Exception as e:
            logger.error(f"Error in event agent decision: {e}")
            return {
                "action": "LOG_ONLY",
                "rule_name": "error",
                "description": f"Error making decision: {str(e)}"
            }
