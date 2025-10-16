"""
Utility for extracting text from screen regions using OCR.

This is a work-in-progress utility for testing text recognition.
"""
import os
from PIL import ImageGrab, Image, ImageOps, ImageFilter
import pytesseract
import re 

# Try to auto-detect tesseract path
HOME_DIR = os.path.expanduser('~')
possible_paths = [
    r'C:\Users\clansman\AppData\Local\Tesseract-OCR\tesseract.exe',
    HOME_DIR + r'\AppData\Local\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    '/usr/bin/tesseract',
    '/usr/local/bin/tesseract'
]

for path in possible_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

# Dictionary of bounding box offsets that should resolve to specific text if it's on the screen
text_loc_dict = {
    "play":           (1650, 980, 1830, 1020),
    "home":           (80, 75, 140, 95),
    "keep":           (1070, 855, 1186, 984),
    "mulligan":       (714, 854, 881, 893),
    "no_blocks":      (1694, 928, 1864, 961),
    "cancel":         (906, 856, 1020, 893),  # Removed duplicate
    "attacker":       (1693, 925, 1865, 966),
    "all atta":       (1693, 925, 1865, 966),
    "no attacks":     (1691, 865, 1861, 900),
    "ancel attack":   (1691, 865, 1861, 900),
    "undo_button":    (1765, 739, 1812, 756),
    "caneel":         (906, 856, 1020, 893),
    "last played":    (1562, 203, 1746, 237),
    "standard play":  (1635, 480, 1763, 504),  # Standard match under table icon match type
    "alchemy play":   (1635, 536, 1763, 564),  # Alchemy match under table icon match type
    "historic play":  (1635, 592, 1763, 624),  # Historic match under table icon match type
    "explorer play":  (1635, 648, 1763, 684),  # Explorer match under table icon match type
    "bot match":      (1635, 704, 1763, 744),  # Bot match under table icon match type
    "brawl":          (1563, 205, 1681, 237),  # Brawl under table icon match type (removed duplicate)
    "ranked":         (1563, 205, 1681, 237),  # Ranked under table icon match type
    }

def extract_text(bb_coordinates=(1730, 979, 1818, 996), threshold=75):
    """Extract text from a screen region using OCR.
    
    Args:
        bb_coordinates: Tuple of (x1, y1, x2, y2) defining the bounding box
        threshold: Pixel intensity threshold for text detection
        
    Returns:
        str: Cleaned text found in the region
    """
    img = ImageGrab.grab(bb_coordinates)
    img = ImageOps.grayscale(img)   
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    img = img.convert('L')    
    
    width, height = img.size
    # Invert pixels since text is white on the screen
    for x in range(width):
        for y in range(height):
            # if intensity less than threshold, assign black
            if img.getpixel((x, y)) < threshold:
                img.putpixel((x, y), 255)
            # if intensity greater than threshold, assign white
            else:
                img.putpixel((x, y), 0)
    
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.EDGE_ENHANCE)            
    
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
    return re.sub(r'[^A-Za-z0-9 ]+', '', text.lower().strip())


def main():
    """Test the text extraction function."""
    # Threshold values for different text types
    FAINT_THRESHOLD = 75   # Used to detect faint text on the screen
    BRIGHT_THRESHOLD = 238  # Used to detect bright text on the screen
    BLOCK_THRESHOLD = 200   # Used on the order blocker screen as the text is slightly greyed out
    
    # Test extraction
    print("Testing text extraction...")
count = 0
    max_iterations = 20
    
    while count < max_iterations:
    text = extract_text()
        if 'combat' not in text:
            print(f"Extracted text: {text}")
        break
    count += 1
    
    print(f"Iterations: {count}")


if __name__ == "__main__":
    main()