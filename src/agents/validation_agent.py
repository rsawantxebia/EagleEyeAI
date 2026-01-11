"""
Validation Agent - Regex-based validation of Indian number plates.
Validates license plate formats without ML.
"""
import re
from typing import Dict, Optional

from utils.logger import logger


class ValidationAgent:
    """Agent responsible for validating license plate formats."""
    
    # Indian number plate patterns
    # Format: XX##XX#### or XX##X#### (e.g., MH12AB1234, DL01A2345)
    PATTERNS = [
        # Standard format: State Code (2 letters) + District Code (2 digits) + Series (1-2 letters) + Number (1-4 digits)
        re.compile(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$'),
        # Alternative format with spaces: XX ## XX ####
        re.compile(r'^[A-Z]{2}\s?\d{2}\s?[A-Z]{1,2}\s?\d{1,4}$'),
        # Older format variations
        re.compile(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{1,4}$'),
    ]
    
    # Indian state codes (first 2 letters)
    STATE_CODES = [
        'AP', 'AR', 'AS', 'BR', 'CG', 'CH', 'DD', 'DH', 'DL', 'GA', 'GJ', 'HP',
        'HR', 'JH', 'JK', 'KA', 'KL', 'LA', 'LD', 'MH', 'ML', 'MN', 'MP', 'MZ',
        'NL', 'OR', 'PB', 'PY', 'RJ', 'SK', 'TN', 'TR', 'TS', 'UK', 'UP', 'WB',
        'AN', 'DN', 'DD'
    ]
    
    def __init__(self):
        """Initialize validation agent."""
        logger.info("Validation agent initialized")
    
    def validate(self, plate_text: str) -> Dict:
        """
        Validate license plate text against Indian formats.
        
        Args:
            plate_text: License plate text to validate
        
        Returns:
            Dictionary with 'is_valid', 'normalized_text', and 'message'
        """
        try:
            # Clean input text
            cleaned_text = plate_text.replace(" ", "").replace("-", "").upper().strip()
            
            if not cleaned_text:
                return {
                    "is_valid": False,
                    "normalized_text": plate_text,
                    "message": "Empty plate text"
                }
            
            # Check against patterns
            matches_pattern = False
            for pattern in self.PATTERNS:
                if pattern.match(cleaned_text):
                    matches_pattern = True
                    break
            
            if not matches_pattern:
                return {
                    "is_valid": False,
                    "normalized_text": cleaned_text,
                    "message": "Plate format does not match Indian number plate patterns"
                }
            
            # Check state code (first 2 characters)
            if len(cleaned_text) >= 2:
                state_code = cleaned_text[:2]
                if state_code not in self.STATE_CODES:
                    return {
                        "is_valid": False,
                        "normalized_text": cleaned_text,
                        "message": f"Invalid state code: {state_code}"
                    }
            
            # Valid plate
            logger.debug(f"Plate validated: {cleaned_text}")
            return {
                "is_valid": True,
                "normalized_text": cleaned_text,
                "message": "Valid Indian number plate format"
            }
            
        except Exception as e:
            logger.error(f"Error in validation agent: {e}")
            return {
                "is_valid": False,
                "normalized_text": plate_text,
                "message": f"Validation error: {str(e)}"
            }
