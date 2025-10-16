"""
Configuration file for MTGA Bot.

Copy this file and customize the settings for your system.
"""

# ===== USER CONFIGURATION =====
# Your MTGA username (used for text recognition to determine if you're in a match)
MTGA_USER_NAME = "chriscas"

# Tesseract OCR path
# Set to None to auto-detect from common installation paths
# Or provide the full path to tesseract.exe
TESSERACT_PATH = None
# Example for Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example for Linux: '/usr/bin/tesseract'

# ===== GAME SETTINGS =====
# Percentage chance that the bot will attack with all creatures (0-100)
ATTACK_PROBABILITY = 100

# Maximum number of times the bot will cycle through cards attempting to play them
MAX_CARD_CYCLES = 2

# Disable mouse clicks for testing (True/False)
CLICKS_DISABLED = False

# ===== WINDOW SETTINGS =====
# Expected resolution and location of game window (x1, y1, x2, y2)
WINDOW_LOC_REZ = (0, 0, 1920, 1080)

# ===== LOGGING SETTINGS =====
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Set to DEBUG for detailed output, INFO for normal operation
LOG_LEVEL = "INFO"

# ===== ADVANCED SETTINGS =====
# Enable OCR preprocessing for better accuracy
OCR_PREPROCESSING = True

# Use adaptive thresholding (better for varying lighting)
OCR_ADAPTIVE_THRESHOLD = False

# Auto-scale coordinates for different resolutions
AUTO_SCALE_COORDINATES = True

# Use state machine for game flow (recommended)
USE_STATE_MACHINE = True

