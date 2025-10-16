# MTGA Bot

An automated bot for Magic: The Gathering Arena (MTGA) that uses optical character recognition (OCR) to detect game states and make decisions.

## ⚠️ Disclaimer

**Use at your own risk.** Using automation tools may violate the MTGA Terms of Service and could result in account penalties or bans. This project is for educational purposes only.

## Features

### Core Features
- Automatic game state detection using OCR
- Automated card playing and combat decisions
- Automatic deck selection and matchmaking
- Configurable attack probability and card play cycles
- Comprehensive logging for debugging
- Window management for consistent screen coordinates

### Enhanced Features (New!)
- **Multi-Resolution Support** - Works with any resolution, not just 1920x1080
- **Improved OCR Accuracy** - Advanced image preprocessing for better text recognition
- **State Machine Architecture** - Cleaner, more maintainable game flow
- **Configuration GUI** - Easy setup without editing code
- **Unit Tests** - Comprehensive test coverage for reliability
- **Adaptive Thresholding** - Better OCR in varying lighting conditions

## Requirements

- **Operating System:** Windows (uses win32gui for window management)
- **Python:** 3.8 or higher
- **Tesseract OCR:** Required for text recognition
- **MTGA:** Must be running in windowed mode
  - **Recommended:** 1920x1080 resolution
  - **Supported:** Any common resolution (1280x720 to 1920x1080) with automatic scaling

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to a standard location (e.g., `C:\Program Files\Tesseract-OCR\`)
- The bot will attempt to auto-detect common installation paths

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 3. Configure the Bot

**Option A: Use the Configuration GUI (Recommended)**

```bash
python config_gui.py
```

This will open a user-friendly interface where you can:
- Set your MTGA username
- Configure Tesseract path
- Adjust game settings
- Set resolution preferences
- Enable advanced features

**Option B: Edit config.py manually**

```python
# config.py example
MTGA_USER_NAME = "YourUsername"
TESSERACT_PATH = None  # Auto-detect, or set path manually
ATTACK_PROBABILITY = 100  # 100% chance to attack
MAX_CARD_CYCLES = 2  # Number of times to cycle through cards
WINDOW_LOC_REZ = (0, 0, 1920, 1080)  # Your resolution
OCR_PREPROCESSING = True  # Enable improved OCR
AUTO_SCALE_COORDINATES = True  # Auto-scale for your resolution
USE_STATE_MACHINE = True  # Use new state machine (recommended)
```

## Usage

### Running the Bot

1. Start MTGA and ensure it's in **windowed mode**
2. Navigate to the main menu
3. Run the bot:

**Enhanced Version (Recommended):**
```bash
python mtga_bot_enhanced.py
```

**Original Version:**
```bash
python mtga_bot_image_rec.py
```

4. The bot will automatically:
   - Detect your screen resolution and scale coordinates
   - Resize and position the MTGA window
   - Detect the current game state
   - Navigate menus and play matches
   - Log all actions to `mtgalog.log`

### Stopping the Bot

Press `Ctrl+C` to gracefully stop the bot.

## Configuration Options

Edit `config.py` to customize bot behavior:

| Setting | Description | Default |
|---------|-------------|---------|
| `MTGA_USER_NAME` | Your MTGA username for match detection | "chriscas" |
| `TESSERACT_PATH` | Path to tesseract executable | None (auto-detect) |
| `ATTACK_PROBABILITY` | Chance (0-100) to attack each turn | 100 |
| `MAX_CARD_CYCLES` | How many times to cycle through cards | 2 |
| `CLICKS_DISABLED` | Disable mouse clicks for testing | False |
| `WINDOW_LOC_REZ` | Expected window position and size | (0, 0, 1920, 1080) |
| `LOG_LEVEL` | Logging detail level | "INFO" |
| `OCR_PREPROCESSING` | Enable improved OCR accuracy | True |
| `OCR_ADAPTIVE_THRESHOLD` | Use adaptive thresholding | False |
| `AUTO_SCALE_COORDINATES` | Auto-scale for resolution | True |
| `USE_STATE_MACHINE` | Use state machine architecture | True |

## Project Structure

```
mtga-bot/
├── mtga_bot_image_rec.py    # Original bot script
├── mtga_bot_enhanced.py     # Enhanced bot with new features
├── windowed_mode.py          # Window management utilities
├── config.py                 # Configuration file
├── config_gui.py             # Configuration GUI
├── resolution_manager.py     # Multi-resolution support
├── ocr_preprocessor.py       # Improved OCR preprocessing
├── state_machine.py          # State machine implementation
├── test_mtga_bot.py          # Unit tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── CHANGELOG.md              # Change history
├── .gitignore               # Git ignore patterns
└── utilities/
    ├── extract_text.py              # OCR text extraction utility
    ├── grey_scale_intensity.py      # Intensity measurement tool
    ├── intensity_range.py           # Zone intensity analysis (fixed typo)
    ├── mouse_pos.py                 # Mouse position display tool
    ├── scan_entire_screen_for_text.py  # Screen scanning utility
    └── set_screen.py                # Window positioning utility
```

## New Tools and Scripts

### Configuration GUI
```bash
python config_gui.py
```
User-friendly interface for configuring all bot settings without editing code.

### Run Tests
```bash
python -m pytest test_mtga_bot.py
```
Run unit tests to verify bot functionality.

### Resolution Testing
```bash
python resolution_manager.py
```
Test coordinate scaling for different resolutions.

### OCR Preprocessing Test
```bash
python ocr_preprocessor.py
```
Test different OCR preprocessing strategies.

## Utility Scripts

The `utilities/` folder contains helper scripts for development and calibration:

### Mouse Position Tool
```bash
python utilities/mouse_pos.py
```
Displays mouse coordinates to help identify UI element positions.

### Greyscale Intensity Tool
```bash
python utilities/grey_scale_intensity.py
```
Shows intensity values at cursor position for threshold calibration.

### Intensity Range Analysis
```bash
python utilities/intensity_range.py
```
Samples intensity values from specific zones to determine min/max ranges.

### Window Setup
```bash
python utilities/set_screen.py
```
Manually set MTGA window to the correct position and size.

## How It Works

1. **Screen Capture:** The bot captures specific regions of the MTGA window
2. **OCR Processing:** Uses Tesseract to extract text from captured regions
3. **State Detection:** Compares extracted text against known patterns to determine game state
4. **Decision Making:** Based on the current state, decides which actions to take
5. **Automation:** Uses PyAutoGUI to simulate mouse clicks at predetermined coordinates

### Supported Game States

- **Start Screen:** Detects and clicks the Play button
- **Deck Selection:** Selects deck and game mode
- **In Match:** Handles card drawing, playing cards, combat, and turn management
- **Match Results:** Clicks through victory/defeat screens
- **Rewards:** Claims rewards after matches

## Troubleshooting

### Bot doesn't detect game state
- Ensure MTGA is in windowed mode
- Verify the window is positioned at (0, 0) on your screen
- Check that Tesseract is properly installed and detected
- Enable `OCR_PREPROCESSING` in config for better accuracy
- Review `mtgalog.log` for detailed error messages

### Bot clicks in wrong locations
- Enable `AUTO_SCALE_COORDINATES` in config
- The bot will automatically scale coordinates for your resolution
- Run `utilities/mouse_pos.py` to verify coordinate positions if needed
- For non-standard resolutions, verify window size matches `WINDOW_LOC_REZ`

### Tesseract not found
- Manually set `TESSERACT_PATH` in `config.py`
- Verify Tesseract is installed and in your system PATH
- On Windows, check common installation paths

### Bot gets stuck in loops
- Increase or decrease `time.sleep()` delays in the code
- Adjust `MAX_CARD_CYCLES` setting
- Check if OCR is misreading text (may need threshold adjustments)

## Development

### Adding New Game States

1. Use `utilities/mouse_pos.py` to find UI element coordinates
2. Capture screenshots and add coordinates to `text_loc_dict`
3. Add corresponding detection logic in `scan_screen_for_text()`
4. Add action handlers for the new state

### Adjusting OCR Thresholds

Different UI elements may require different intensity thresholds:
- `FAINT_THRESHOLD = 75` - For faint text
- `BRIGHT_THRESHOLD = 238` - For bright text
- `BLOCK_THRESHOLD = 200` - For order blockers screen

Use `utilities/intensity_range.py` to determine appropriate values.

## Known Limitations

- Requires windowed mode (not fullscreen)
- Windows-only (uses win32gui)
- OCR accuracy depends on screen quality and text clarity
- May not handle all card types or special abilities
- Does not read or respond to opponent's actions strategically
- State machine mode is experimental (traditional mode still available)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add appropriate error handling and logging
5. Update documentation as needed
6. Submit a pull request

## License

This project is provided as-is for educational purposes. Use at your own risk.

## Credits

Created as an educational project to demonstrate:
- Computer vision and OCR techniques
- Game automation strategies
- Python GUI automation
- Screen scraping and image processing

## Version History

### Version 2.0 (Enhanced) - Current
- **Multi-resolution support** with automatic coordinate scaling
- **Improved OCR** with advanced image preprocessing
- **State machine architecture** for cleaner game flow
- **Configuration GUI** for easy setup
- **Unit tests** for reliability
- **Adaptive thresholding** for better OCR accuracy
- All features from Version 1.0

### Version 1.0 (Refactored)
- Complete code refactoring and cleanup
- Added comprehensive error handling
- Improved logging throughout
- Created configuration file system
- Fixed duplicate code and bugs
- Added proper documentation
- Created utility scripts with proper main guards

## Support

For issues, questions, or contributions, please use the project's issue tracker.

---

**Remember:** This bot is for educational purposes only. Always respect the game's Terms of Service and the gaming community.
