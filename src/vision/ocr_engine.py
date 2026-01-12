"""
OCR engine using EasyOCR for license plate text recognition.
Handles text extraction from cropped license plate images.
"""
from typing import Optional, Tuple, List
import numpy as np
import cv2
import easyocr

from utils.logger import logger


class OCREngine:
    """EasyOCR-based OCR engine for license plate text recognition."""
    
    # Common OCR character confusion pairs (what OCR sees → what it should be)
    # Based on visual similarity
    CHAR_CORRECTIONS = {
        'H': 'M',  # H often misread as M in plates (context-dependent)
        '0': 'O',  # Zero often misread as letter O
        'O': '0',  # Letter O often misread as zero (context-dependent)
        '1': 'I',  # One often misread as I
        'I': '1',  # I often misread as 1
        '5': 'S',  # Five often misread as S
        'S': '5',  # S often misread as 5
        '8': 'B',  # Eight often misread as B
        'B': '8',  # B often misread as 8
        'Z': '2',  # Z often misread as 2
        '2': 'Z',  # 2 often misread as Z
    }
    
    # Character similarity groups (characters that look similar)
    SIMILAR_CHARS = {
        'M': ['H', 'N', 'W'],
        'H': ['M', 'N'],
        'N': ['M', 'H'],
        '0': ['O', 'D', 'Q'],
        'O': ['0', 'D', 'Q'],
        '1': ['I', 'L'],
        'I': ['1', 'L'],
        '5': ['S'],
        'S': ['5'],
        '8': ['B'],
        'B': ['8'],
    }
    
    def __init__(self):
        """Initialize EasyOCR reader for English language."""
        try:
            self.reader = easyocr.Reader(['en'], gpu=False)  # CPU mode for laptop compatibility
            logger.info("OCR engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OCR engine: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray, method: str = "clahe") -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image (BGR format)
            method: Preprocessing method ('clahe', 'adaptive', 'morphology', 'sharpen', 'denoise')
        
        Returns:
            Preprocessed image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        if method == "clahe":
            # Contrast Limited Adaptive Histogram Equalization
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
        elif method == "adaptive":
            # Adaptive thresholding
            enhanced = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        elif method == "morphology":
            # Morphological operations to enhance text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            # Apply opening to remove noise
            opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            # Apply closing to fill gaps
            enhanced = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        elif method == "sharpen":
            # Sharpen the image
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            enhanced = cv2.filter2D(gray, -1, kernel)
        elif method == "denoise":
            # Denoise and enhance
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
        else:
            enhanced = gray
        
        # Convert back to BGR for EasyOCR
        if len(enhanced.shape) == 2:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return enhanced
    
    def _try_ocr_with_preprocessing(self, image: np.ndarray, method: str) -> List[Tuple[str, float]]:
        """
        Try OCR with specific preprocessing method.
        
        Returns:
            List of (text, confidence) tuples
        """
        try:
            preprocessed = self._preprocess_image(image, method)
            
            results = self.reader.readtext(
                preprocessed,
                allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                paragraph=False,
                width_ths=0.7,
                height_ths=0.7
            )
            
            texts = []
            for (bbox, text, confidence) in results:
                cleaned = text.replace(" ", "").replace("-", "").upper().strip()
                if cleaned and len(cleaned) >= 2 and confidence > 0.2:
                    texts.append((cleaned, confidence))
            
            return texts
        except Exception as e:
            logger.debug(f"OCR failed with {method} preprocessing: {e}")
            return []
    
    def read_text(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Extract text from a license plate image using multiple preprocessing strategies.
        
        Args:
            image: Cropped license plate image as NumPy array (BGR format)
        
        Returns:
            Tuple of (text, confidence). Returns (None, 0.0) if no text found.
        """
        try:
            # Ensure minimum size for OCR
            h, w = image.shape[:2] if len(image.shape) == 2 else image.shape[:2]
            if h < 20 or w < 50:
                # Resize if too small
                scale = max(50 / w, 20 / h, 2.0)
                new_w = int(w * scale)
                new_h = int(h * scale)
                image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                logger.info(f"Resized image from {w}x{h} to {new_w}x{new_h}")
            
            # Optimized: Try best method first, early exit on high confidence
            # Try CLAHE first (best performing), then original, skip denoise if confidence is high
            all_results = []
            high_confidence_threshold = 0.85  # Early exit threshold
            
            # Try CLAHE first (best performing method)
            results = self._try_ocr_with_preprocessing(image, "clahe")
            all_results.extend(results)
            if results:
                # Check if we have high confidence result
                best_clahe = max(results, key=lambda x: x[1]) if results else None
                if best_clahe and best_clahe[1] >= high_confidence_threshold and 3 <= len(best_clahe[0]) <= 15:
                    # Early exit - high confidence result found
                    corrected_text = self._correct_characters(best_clahe[0])
                    logger.info(f"OCR result (early exit): {corrected_text} (confidence: {best_clahe[1]:.2f})")
                    return corrected_text, best_clahe[1]
                logger.debug(f"Method clahe found {len(results)} text(s)")
            
            # Try original image (faster than denoise)
            try:
                original_results = self.reader.readtext(
                    image,
                    allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    paragraph=False,
                    width_ths=0.7,
                    height_ths=0.7
                )
                for (bbox, text, confidence) in original_results:
                    cleaned = text.replace(" ", "").replace("-", "").upper().strip()
                    if cleaned and len(cleaned) >= 2 and confidence > 0.2:
                        all_results.append((cleaned, confidence))
                        # Early exit check
                        if confidence >= high_confidence_threshold and 3 <= len(cleaned) <= 15:
                            corrected_text = self._correct_characters(cleaned)
                            logger.info(f"OCR result (early exit): {corrected_text} (confidence: {confidence:.2f})")
                            return corrected_text, confidence
            except:
                pass
            
            if not all_results:
                logger.debug("No text detected by OCR with any preprocessing method")
                return None, 0.0
            
            # Remove duplicates and aggregate confidences
            text_confidence_map = {}
            for text, conf in all_results:
                if text in text_confidence_map:
                    # Take maximum confidence for duplicate texts
                    text_confidence_map[text] = max(text_confidence_map[text], conf)
                else:
                    text_confidence_map[text] = conf
            
            # Sort by confidence
            sorted_results = sorted(
                text_confidence_map.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Find best result that looks like a license plate
            best_text = None
            best_conf = 0.0
            
            for text, conf in sorted_results:
                # License plates are typically 3-15 characters
                # Prefer longer, more confident results
                if 3 <= len(text) <= 15:
                    # Weight by both confidence and length
                    score = conf * (1 + len(text) * 0.05)
                    if score > best_conf:
                        best_text = text
                        best_conf = conf
            
            if best_text:
                # Apply character correction for common OCR mistakes
                corrected_text = self._correct_characters(best_text)
                if corrected_text != best_text:
                    logger.info(f"Character correction: {best_text} → {corrected_text}")
                    best_text = corrected_text
                
                logger.info(f"OCR result: {best_text} (confidence: {best_conf:.2f})")
                return best_text, best_conf
            elif sorted_results:
                # Fallback to highest confidence
                best_text, best_conf = sorted_results[0]
                # Apply character correction
                corrected_text = self._correct_characters(best_text)
                if corrected_text != best_text:
                    logger.info(f"Character correction: {best_text} → {corrected_text}")
                    best_text = corrected_text
                
                logger.info(f"OCR result (fallback): {best_text} (confidence: {best_conf:.2f})")
                return best_text, best_conf
            else:
                return None, 0.0
            
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, 0.0
    
    def _correct_characters(self, text: str) -> str:
        """
        Correct common OCR character recognition errors based on Indian plate format.
        
        Indian plate format: XX##XX#### (e.g., MH12AB1234)
        - First 2 chars: State code (letters)
        - Next 2 chars: District code (digits)
        - Next 1-2 chars: Series (letters)
        - Last 1-4 chars: Number (digits)
        
        Args:
            text: OCR result text
        
        Returns:
            Corrected text
        """
        if not text or len(text) < 3:
            return text
        
        corrected = list(text)
        
        # Indian plate format analysis
        # Format: XX##XX#### (e.g., MH12AB1234)
        # Position 0-1: State code (letters) - MH, DL, etc.
        # Position 2-3: District code (digits) - 01, 12, etc.
        # Position 4-5: Series (letters) - AB, A, etc.
        # Position 6+: Number (digits) - 1234, etc.
        
        for i, char in enumerate(corrected):
            # Position 0-1: Must be letters (state code)
            if i < 2:
                if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    # Digit in letter position - likely OCR error
                    # Try to correct based on context
                    if char == '0':
                        corrected[i] = 'O'  # 0 → O in letter position
                    elif char == '1':
                        corrected[i] = 'I'  # 1 → I in letter position
                    elif char == '5':
                        corrected[i] = 'S'  # 5 → S in letter position
                elif char == 'H' and i == 0:
                    # First character H might be M (common mistake: MH → HH)
                    # Check if second char is H (likely MH → HH)
                    if len(corrected) > 1 and corrected[1] == 'H':
                        corrected[i] = 'M'  # HH → MH
                    # Also check if it's a known state code starting with M
                    elif len(corrected) > 1:
                        potential_state = 'M' + corrected[1]
                        if potential_state in ['MH', 'MP', 'MN', 'ML', 'ME']:
                            corrected[i] = 'M'  # H → M if it forms valid state code
                elif char == 'H' and i == 1:
                    # Second char H - check if first char was corrected to M
                    # Or if it's part of valid state code
                    if corrected[0] == 'M':
                        # Keep H (MH is valid)
                        pass
                    elif corrected[0] == 'H':
                        # HH might be MH, but we already corrected first char
                        pass
            
            # Position 2-3: Must be digits (district code)
            elif 2 <= i < 4:
                if char in ['O', 'I', 'S', 'Z']:
                    # Letter in digit position - likely OCR error
                    if char == 'O':
                        corrected[i] = '0'  # O → 0 in digit position
                    elif char == 'I':
                        corrected[i] = '1'  # I → 1 in digit position
                    elif char == 'S':
                        corrected[i] = '5'  # S → 5 in digit position
                    elif char == 'Z':
                        corrected[i] = '2'  # Z → 2 in digit position
            
            # Position 4-5: Must be letters (series)
            elif 4 <= i < 6:
                if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    # Digit in letter position
                    if char == '0':
                        corrected[i] = 'O'
                    elif char == '1':
                        corrected[i] = 'I'
                    elif char == '5':
                        corrected[i] = 'S'
                elif char == 'H':
                    # H in series position might be M (common: MF → HF)
                    # Check if followed by F (HF → MF is common)
                    if i + 1 < len(corrected) and corrected[i + 1] == 'F':
                        corrected[i] = 'M'  # HF → MF
                    # Also check if it's followed by other common letters after M
                    elif i + 1 < len(corrected) and corrected[i + 1] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
                        # Common pattern: M followed by letter, but OCR read as H
                        # Check if previous char in series is also suspicious
                        if i > 4 and corrected[i-1] == 'H':
                            # Double H in series is unlikely, might be M
                            corrected[i] = 'M'
            
            # Position 6+: Must be digits (number)
            else:
                if char in ['O', 'I', 'S', 'Z', 'B']:
                    # Letter in digit position
                    if char == 'O':
                        corrected[i] = '0'
                    elif char == 'I':
                        corrected[i] = '1'
                    elif char == 'S':
                        corrected[i] = '5'
                    elif char == 'Z':
                        corrected[i] = '2'
                    elif char == 'B':
                        corrected[i] = '8'
        
        result = ''.join(corrected)
        
        # Additional pattern-based corrections
        # Fix common patterns like HHO4HF → MH04MF
        if len(result) >= 6:
            # Pattern: HHO... → MHO... (first H should be M in state code)
            if result.startswith('HH') and len(result) >= 3:
                if result[2].isdigit() or result[2] == 'O':
                    result = 'M' + result[1:]
                    logger.debug(f"Pattern correction: HH → MH")
            
            # Pattern: ...O4... → ...04... (O in digit position)
            if len(result) >= 4 and result[2] == 'O' and result[3].isdigit():
                result = result[:2] + '0' + result[3:]
                logger.debug(f"Pattern correction: O → 0 in digit position")
            
            # Pattern: ...HF... → ...MF... (in series position)
            if len(result) >= 6:
                # Check position 4-5 (series position)
                if result[4:6] == 'HF':
                    result = result[:4] + 'MF' + result[6:]
                    logger.debug(f"Pattern correction: HF → MF")
                # Also check if it's H followed by any letter (common M misread)
                elif len(result) >= 5 and result[4] == 'H' and result[5].isalpha():
                    # If previous digit position has O (likely 0), this H is likely M
                    if len(result) >= 4 and (result[2] == 'O' or result[3] == 'O'):
                        result = result[:4] + 'M' + result[5:]
                        logger.debug(f"Pattern correction: H → M in series position")
        
        return result