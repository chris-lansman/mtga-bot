"""
Enhanced MTGA Bot with improved features.

This version includes:
- Resolution scaling support
- Improved OCR preprocessing
- State machine for game flow
- Better error handling
"""
import time
import os
import sys
import logging

# Import base bot functionality
import mtga_bot_image_rec as base_bot

# Import new modules
from resolution_manager import ResolutionManager, create_scaled_coordinates
from ocr_preprocessor import OCRPreprocessor, create_default_preprocessor
from state_machine import GameStateMachine, StartScreenState

# Try to import config with new settings
try:
    from config import (
        MTGA_USER_NAME, TESSERACT_PATH, ATTACK_PROBABILITY,
        MAX_CARD_CYCLES, CLICKS_DISABLED, WINDOW_LOC_REZ, LOG_LEVEL,
        OCR_PREPROCESSING, OCR_ADAPTIVE_THRESHOLD, 
        AUTO_SCALE_COORDINATES, USE_STATE_MACHINE
    )
except ImportError:
    # Fall back to defaults if new settings not in config
    from config import *
    OCR_PREPROCESSING = True
    OCR_ADAPTIVE_THRESHOLD = False
    AUTO_SCALE_COORDINATES = True
    USE_STATE_MACHINE = True

logger = logging.getLogger('mtgalog')


class EnhancedBotActions:
    """
    Enhanced bot actions with resolution scaling and improved OCR.
    
    This class wraps the base bot functionality and adds new features.
    """
    
    def __init__(self, resolution_manager=None, ocr_preprocessor=None):
        """Initialize enhanced bot actions.
        
        Args:
            resolution_manager: ResolutionManager for coordinate scaling
            ocr_preprocessor: OCRPreprocessor for improved OCR
        """
        self.resolution_manager = resolution_manager
        self.ocr_preprocessor = ocr_preprocessor
        
        # Setup scaled coordinates if resolution manager provided
        if resolution_manager and AUTO_SCALE_COORDINATES:
            self.setup_scaled_coordinates()
        else:
            # Use base coordinates
            self.text_loc_dict = base_bot.text_loc_dict
            self.cord = base_bot.Cord
    
    def setup_scaled_coordinates(self):
        """Setup scaled coordinates for current resolution."""
        logger.info("Setting up scaled coordinates")
        scaled_text_loc, scaled_cord = create_scaled_coordinates(
            self.resolution_manager,
            base_bot.text_loc_dict,
            base_bot.Cord
        )
        self.text_loc_dict = scaled_text_loc
        # Update Cord class attributes
        for key, value in scaled_cord.items():
            setattr(base_bot.Cord, key, value)
        self.cord = base_bot.Cord
    
    def extract_text_enhanced(self, bb_coordinates, threshold=235):
        """Extract text with optional preprocessing.
        
        Args:
            bb_coordinates: Bounding box coordinates
            threshold: Pixel intensity threshold
            
        Returns:
            str: Extracted text
        """
        if self.ocr_preprocessor and OCR_PREPROCESSING:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab(bb_coordinates)
                
                # Apply preprocessing
                if OCR_ADAPTIVE_THRESHOLD:
                    img = self.ocr_preprocessor.preprocess_with_adaptive_threshold(img)
                else:
                    img = self.ocr_preprocessor.preprocess(img)
                
                # Use pytesseract on preprocessed image
                import pytesseract
                import re
                text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
                return re.sub(r'[^A-Za-z0-9 ]+', '', text.lower().strip())
            except Exception as e:
                logger.error(f"Error in enhanced OCR: {e}")
                # Fall back to base extraction
                return base_bot.extract_text(bb_coordinates, threshold)
        else:
            return base_bot.extract_text(bb_coordinates, threshold)
    
    # Wrapper methods for state machine
    def click_play(self):
        """Click play button."""
        base_bot.click_play()
    
    def select_deck_and_play_style(self):
        """Select deck and play style."""
        base_bot.select_deck_and_play_style(base_bot.Cord.bot_ply_chk)
    
    def check_if_card_draw_screen(self):
        """Check if we're on card draw screen."""
        try:
            found_text = []
            found_text.append(self.extract_text_enhanced(self.text_loc_dict['keep'], base_bot.BRIGHT_THRESHOLD))
            found_text.append(self.extract_text_enhanced(self.text_loc_dict['mulligan'], base_bot.BRIGHT_THRESHOLD))
            return 'keep' in found_text or 'mulligan' in found_text
        except Exception as e:
            logger.error(f"Error checking card draw screen: {e}")
            return False
    
    def check_if_my_card_draw_done(self):
        """Check if card draw is complete."""
        return base_bot.check_if_my_card_draw_done()
    
    def check_in_match(self):
        """Check if we're in a match."""
        return base_bot.check_in_match()
    
    def check_if_my_turn(self):
        """Check if it's my turn."""
        return base_bot.check_if_my_turn()
    
    def determine_turn_phase(self):
        """Determine current turn phase."""
        return base_bot.turn_phase()
    
    def play_my_cards(self):
        """Play cards from hand."""
        base_bot.play_my_cards()
    
    def play_attack_phase(self):
        """Handle attack phase."""
        base_bot.play_attack_phase()
    
    def end_turn(self):
        """End turn."""
        base_bot.leftClick(base_bot.Cord.next_button)
    
    def handle_opponent_prompts(self):
        """Handle prompts during opponent's turn."""
        base_bot.leftClick(base_bot.Cord.next_button)
    
    def match_result_actions(self):
        """Handle match results."""
        base_bot.match_result_actions()
    
    def check_for_rewards(self):
        """Check if rewards screen is showing."""
        # Placeholder - would need actual detection logic
        return False
    
    def rewards_actions(self):
        """Handle rewards screen."""
        base_bot.rewards_actions()
    
    def detect_current_state(self):
        """Detect current game state for error recovery."""
        screen = base_bot.scan_screen_for_text()
        
        if screen == "Start":
            from state_machine import StartScreenState
            return StartScreenState(None)
        elif screen == "Deck Select":
            from state_machine import DeckSelectState
            return DeckSelectState(None)
        elif screen == "In Match":
            from state_machine import InMatchState
            return InMatchState(None)
        elif screen == "match results":
            from state_machine import MatchResultsState
            return MatchResultsState(None)
        
        return None


def initialize_enhanced_bot():
    """Initialize the enhanced bot with all features.
    
    Returns:
        tuple: (resolution_manager, ocr_preprocessor, actions, state_machine)
    """
    logger.info("Initializing enhanced bot")
    
    # Check MTGA window and get resolution
    if not base_bot.check_mtga_window_size():
        logger.error("Failed to find MTGA window")
        return None, None, None, None
    
    # Get actual window size
    try:
        import win32gui
        window_handle = win32gui.FindWindow(None, "MTGA")
        window_coords = win32gui.GetWindowRect(window_handle)
        logger.info(f"MTGA window coordinates: {window_coords}")
    except Exception as e:
        logger.error(f"Error getting window coordinates: {e}")
        window_coords = WINDOW_LOC_REZ
    
    # Initialize resolution manager
    resolution_manager = None
    if AUTO_SCALE_COORDINATES:
        resolution_manager = ResolutionManager.from_window_coordinates(window_coords)
    
    # Initialize OCR preprocessor
    ocr_preprocessor = None
    if OCR_PREPROCESSING:
        ocr_preprocessor = create_default_preprocessor()
    
    # Create actions object
    actions = EnhancedBotActions(resolution_manager, ocr_preprocessor)
    
    # Create state machine if enabled
    state_machine = None
    if USE_STATE_MACHINE:
        state_machine = GameStateMachine(actions)
    
    return resolution_manager, ocr_preprocessor, actions, state_machine


def main():
    """Main enhanced bot loop."""
    logger.info("*** Started Enhanced MTGA Bot ***")
    
    # Initialize all components
    res_mgr, ocr_prep, actions, state_machine = initialize_enhanced_bot()
    
    if actions is None:
        logger.error("Failed to initialize bot")
        return
    
    try:
        if USE_STATE_MACHINE and state_machine:
            # Use state machine mode
            logger.info("Running in state machine mode")
            state_machine.start()
            
            while state_machine.running:
                state_machine.update()
                time.sleep(0.5)
        
        else:
            # Use traditional mode
            logger.info("Running in traditional mode")
            while True:
                base_bot.check_mtga_window_size()
                screen = base_bot.scan_screen_for_text()
                
                if screen == "Start":
                    base_bot.click_play()
                elif screen == "Deck Select":
                    base_bot.select_deck_and_play_style(base_bot.Cord.bot_ply_chk)
                    base_bot.click_play()
                elif screen == "In Match":
                    base_bot.match_actions()
                elif screen == "match results":
                    base_bot.match_result_actions()
                elif screen == "Rewards":
                    base_bot.rewards_actions()
                else:
                    logger.warning(f"Unknown screen state: {screen}")
                
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        if state_machine:
            state_machine.stop()
        logger.info("Enhanced bot shutting down")


if __name__ == "__main__":
    main()

