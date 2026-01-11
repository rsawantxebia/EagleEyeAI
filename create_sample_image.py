#!/usr/bin/env python3
"""
Create a sample license plate image for testing.
"""
import cv2
import numpy as np
from pathlib import Path

# Create sample directory
sample_dir = Path(__file__).parent / "samples"
sample_dir.mkdir(exist_ok=True)

# Create a sample image with a license plate
width, height = 800, 600
image = np.ones((height, width, 3), dtype=np.uint8) * 240  # Light gray background

# Draw a car-like shape
cv2.rectangle(image, (100, 200), (700, 450), (50, 50, 50), -1)  # Car body
cv2.rectangle(image, (150, 150), (650, 200), (100, 100, 100), -1)  # Windshield

# Draw license plate area
plate_x, plate_y = 300, 350
plate_w, plate_h = 200, 80
cv2.rectangle(image, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (255, 255, 255), -1)
cv2.rectangle(image, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (0, 0, 0), 3)

# Add text "MH12AB1234" on the plate
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.2
thickness = 3
text = "MH12AB1234"
text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
text_x = plate_x + (plate_w - text_size[0]) // 2
text_y = plate_y + (plate_h + text_size[1]) // 2
cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)

# Save the image
output_path = sample_dir / "sample_license_plate.jpg"
cv2.imwrite(str(output_path), image)
print(f"Sample image created at: {output_path}")
print(f"Image size: {width}x{height}")
