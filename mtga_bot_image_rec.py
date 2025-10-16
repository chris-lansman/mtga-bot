# MTGA bot that uses image recognition to determine where we are in the game and what we will do next.
# The game does not have to be in a specific window mode, it will attempt to re-size and move the window to the place
# where the program needs it to be. 
# Windowed mode is recommended.

import time
import os
import re
import logging
from random import randrange
from datetime import datetime
import win32gui
import pyautogui
from PIL import ImageGrab, Image, ImageOps, ImageFilter
import pytesseract

# Try to import config, fall back to defaults if not found
try:
    from config import (
        MTGA_USER_NAME, TESSERACT_PATH, ATTACK_PROBABILITY,
        MAX_CARD_CYCLES, CLICKS_DISABLED, WINDOW_LOC_REZ, LOG_LEVEL
    )
except ImportError:
    # Default configuration if config.py is not found
    MTGA_USER_NAME = "chriscas"
    TESSERACT_PATH = None
    ATTACK_PROBABILITY = 100
    MAX_CARD_CYCLES = 2
    CLICKS_DISABLED = False
    WINDOW_LOC_REZ = (0, 0, 1920, 1080)
    LOG_LEVEL = "INFO"
    print("Warning: config.py not found, using default settings")

# Convert LOG_LEVEL string to logging constant if needed
if isinstance(LOG_LEVEL, str):
    LOG_LEVEL = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

# ----- SET UP LOGGING -----

logger = logging.getLogger('mtgalog')
hdlr = logging.FileHandler('mtgalog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(LOG_LEVEL)

# ----- TESSERACT CONFIGURATION -----
# Set tesseract path if provided, otherwise assume it's in system PATH
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    # Try common installation paths
    HOME_DIR = os.path.expanduser('~')
    possible_paths = [
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

# Dictionary list of keywords and their pixel box location on the screen (upper left x,y upper right x,y)
# Note: Some entries have comments like [FAINT_THRESHOLD] or [BRIGHT_THRESHOLD] to indicate which threshold to use
text_loc_dict = {
    MTGA_USER_NAME:     (90, 1000, 260, 1040),    # Username in the lower left corner while in match
    "play":             (1650, 980, 1830, 1020),  # Play button on the lower right on main screen or sub-main screen
    "home":             (80, 75, 140, 95),        # Home tab on the main screen and sub-main screen
    "keep":             (1070, 855, 1186, 984),   # Keep button when a match starts
    "mulligan":         (714, 854, 881, 893),     # Mulligan button when a match starts
    "cancel":           (1693, 925, 1865, 966),   # Cancel button during a match
    "attacker":         (1722, 929, 1854, 964),   # Attacker text during combat
    "all attack":       (1695, 928, 1850, 960),   # All attack button during combat
    "no attacks":       (1691, 865, 1861, 900),   # No attacks button during combat
    "cancel attacks":   (1667, 865, 1883, 900),   # Cancel attacks button
    "undo_button":      (1765, 739, 1812, 756),   # Undo button location
    "last played":      (1562, 203, 1746, 237),   # Last played indicator
    "standard play":    (1635, 480, 1763, 504),   # Standard match under table icon match type
    "alchemy play":     (1635, 536, 1763, 564),   # Alchemy match under table icon match type
    "historic play":    (1635, 592, 1763, 624),   # Historic match under table icon match type
    "explorer play":    (1635, 648, 1763, 684),   # Explorer match under table icon match type
    "bot match":        (1635, 704, 1763, 744),   # Bot match under table icon match type
    "brawl":            (1563, 205, 1681, 237),   # Brawl under table icon match type
    "ranked":           (1563, 205, 1681, 237),   # Ranked under table icon match type
    "view battlefield": (1590, 100, 1800, 140),   # View battlefield during card selection
    "next":             (1740, 934, 1810, 960),   # Next button in combat
    "pass":             (1735, 931, 1814, 968),   # Pass button in game
    "no blocks":        (1700, 929, 1849, 963),   # No blocks button in game
    "my turn":          (1710, 929, 1837, 965),   # My turn indicator in game
    "to combat":        (1730, 979, 1818, 996),   # [FAINT_THRESHOLD]
    "to end":           (1725, 977, 1820, 996),   # [FAINT_THRESHOLD]
    "to blockers":      (1725, 977, 1820, 996),   # [FAINT_THRESHOLD]
    "to damage":        (1725, 977, 1820, 996),   # [FAINT_THRESHOLD]
    "to attackers":     (1725, 977, 1820, 996),   # [FAINT_THRESHOLD]
    "end turn":         (1725, 977, 1820, 996),   # [FAINT_THRESHOLD]
    "opponent's turn":  (1684, 931, 1861, 967),   # Opponent's turn indicator [FAINT_THRESHOLD]
    "resolve":          (1716, 932, 1835, 965),   # Resolve button
    "click to continue": (855, 1022, 1062, 1055), # Click to continue at match end [FAINT_THRESHOLD]
    "defeat":           (778, 492, 1141, 603),    # Defeat on results screen
    "victory":          (704, 491, 1212, 620),    # Victory on results screen
    "choose one":       (802, 87, 1119, 143),     # Choose one text for multi-choice card
    "done":             (913, 855, 1010, 892),    # Done button on order blockers screen
    "first":            (543, 723, 634, 768),     # First on order blockers screen
    "order blockers":   (758, 84, 1161, 143),     # Order blockers text [BLOCK_THRESHOLD=200]
    }
FAINT_THRESHOLD =   75  # Used to detect faint text on the screen
BRIGHT_THRESHOLD = 238  # Used to detect bright text on the screen
BLOCK_THRESHOLD =  200  # Used on the order blocker screen as the text is slightly greyed out


def extract_text(bb_coordinates, threshold=235):
    """Extract text from a screen region using OCR.
    
    Args:
        bb_coordinates: Tuple of (x1, y1, x2, y2) defining the bounding box
        threshold: Pixel intensity threshold for text detection (default: 235)
        
    Returns:
        str: Cleaned text found in the region, or empty string on error
    """
    try:
        # Grab a box based on (x,y,x,y) coordinates
        img = ImageGrab.grab(bb_coordinates)
        img = ImageOps.grayscale(img)
        img = img.filter(ImageFilter.SMOOTH)
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        img = img.convert('L')
        
        # Invert pixels since text is white on the screen
        # This will leave you with black text and a white background
        # which pytesseract does a better job with
        width, height = img.size
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
        
        # Use pytesseract directly without saving to disk
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
        return re.sub(r'[^A-Za-z0-9 ]+', '', text.lower().strip())
    
    except Exception as e:
        logger.error(f"Error extracting text from coordinates {bb_coordinates}: {e}")
        return ""


class Cord:

    # Maintain co-ordinates of locations to mouse click
    #play_button_edge =  (1614, 980) # The play button on the dashboard, bottom right, point is at the edge of the button
    play_button =       (1665,1000)
    click_to_continue = (250, 200)   # Clicking (almost) anywhere on the screen to advance (usually after a match)
    #edit_deck =         (238,1035)   # The edit deck button on the left side of the screen
    table_icon_illum =  (1740,145)  # Table icon in the upper right of the screen after the main screen
    #recently_played =   (1872,167)  # Recently played flag found on the screen after the main screen
    #gold_coins =        (1447,67)
    #gems =              (1566,70)
    #home_tab_main =     (111,104) # Home button in the upper left on the main screen
    
    # Sub-main screen items
    deck_select =          (460,580) # Deck just left of the big '+'
    #sub_screen_empty_pt1 = (60,240)  # Empty area on the left side of the screen
    #sub_screen_empty_pt2 = (60,380)
    #sub_screen_empty_pt3 = (60,550)
    #sub_screen_empty_pt4 = (60,750)
    
    # Mode icon diamonds
    std_ply_chk =        (1600,490) # Standard play choice check mark on table screen
    alc_ply_chk =        (1600,550) # Alchemy play choice check mark on table screen
    his_ply_chk =        (1600,607) # History play choice check mark on table screen
    exp_ply_chk =        (1600,665) # Explorer play choice check mark on table screen
    bot_ply_chk =        (1600,725) # Bot play choice check mark on table screen
    
    # In-game items
    cancel_button =         (1770,950)
    #done_button =           (963,872)
    keep_draw_button =      (1130, 870)  # Accept drawn cards at start of match
    #mulligan_button =       (681,847)    # Mulligan button at start of match when cards are ready to pick
    #question_mark_area =    (610,876)    # dark spot next to the question mark icon on the select card screen at start of match
    #friends_icon =          (40,1030)    # Friends icon in the lower left corner
    #pass_turn =             (1850, 1030) # Pass turn button (during both player's turns)
    no_attacks_button =     (1770, 880)  # During combat phase, the No Attacks button
    opponent_avatar =       (970, 136)   # To select when attacking in case opponent has Planeswalker in play
    undo_button =           (1864, 747)  # Undo button when casting a spell
    resolve_button =        (1770, 950)  # Resolve button, also No Blocks during opponent combat
    #cancel_area =           (1730, 1030) # Just a blank area to click to cancel
    order_blockers_done =   (970, 840)   # Click done to auto-assign damage to multiple blockers
    #p1_main_phase =         (840,878)
    #p1_second_phase =       (1081,877)
    #p2_main_phase =         (859,151)
    #p2_second_phase =       (1062,151)
    card_option_left =      (623,316)
    card_option_left_click = (751,483)
    #shield_icon =           (1758,832)
    next_button =           (1780,940)
    #sword_icon =            (1726,830)
    #block_order =           (1316, 783)
    #blocking_shield =       (1759,895)

    # Card positions to play. There may or may not be a card at these spots but try anyway
    cards_in_hand = ((1000,1050), 
                     (890,1050), 
                     (1050,1050), 
                     (840,1050), 
                     (1160,1050), 
                     (720,1050), 
                     (1225,1050), 
                     (660,1050),
                     (1325,1050), 
                     (540,1050), 
                     (1425,1050), 
                     (490,1050), 
                     (1550,1050), 
                     (360,1050))

def leftClick(p):
    """Performs a single left click of the mouse at position p.

    Args:
        p (tuple): (x, y) coordinate on screen where we want the mouse to click
    """
    if not CLICKS_DISABLED:
        try:
            pyautogui.mouseDown(x=p[0], y=p[1])
            pyautogui.mouseUp(x=p[0], y=p[1])
        except Exception as e:
            logger.error(f"Error clicking at position {p}: {e}")


def doubleLeftClick(p):
    """Performs a double left click of the mouse at position p.

    Args:
        p (tuple): (x, y) coordinate on screen where we want the mouse to click
    """
    if not CLICKS_DISABLED:
        try:
            pyautogui.doubleClick(x=p[0], y=p[1], interval=0.25)
        except Exception as e:
            logger.error(f"Error double-clicking at position {p}: {e}")


def check_mtga_window_size():
    """Check and adjust the MTGA window size and position.
    
    Returns:
        bool: True if window was found and adjusted (if needed), False otherwise
    """
    try:
        # First find the 'MTGA' window
        # Note: If the window title changes, you'll need to update this
        window_handle = win32gui.FindWindow(None, "MTGA")
        
        if not window_handle:
            logger.warning("MTGA window not found")
            return False
        
        # Get the window's coordinates
        window_coordinates = win32gui.GetWindowRect(window_handle)
        
        # Verify the window is in the expected position and size
        if WINDOW_LOC_REZ != window_coordinates:
            logger.info(f"Adjusting window from {window_coordinates} to {WINDOW_LOC_REZ}")
            # Move the window to a known offset (0,0) for the upper left corner,
            # and force a resize so this works on every system every time
            win32gui.SetWindowPos(window_handle, None, 0, 0, 1920, 1080, 0)
        
        return True
    
    except Exception as e:
        logger.error(f"Error checking/adjusting MTGA window: {e}")
        return False
        

def scan_screen_for_text():
    """Scan the screen to determine which game state we're in.
    
    This method has no idea where we are in the game so it looks for
    any possible combinations of places we could be. The first one that
    matches we tell the calling code and exit.
    
    The found_text checks were broken up to speed up the call to this method.
    Calls to pytesseract are very costly time wise.
    
    Returns:
        str: Game state identifier ('Start', 'Deck Select', 'In Match', 'match results', or None)
    """
    try:
        found_text = []
        found_text.append(extract_text(text_loc_dict['play'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['last played'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['standard play'], BRIGHT_THRESHOLD))
        
        if ('play' in found_text and 
            'last played' not in found_text and
            'standard play' not in found_text):
            logger.info("On start screen with Play button")
            return "Start"
        
        found_text.append(extract_text(text_loc_dict['home'], BRIGHT_THRESHOLD))
        if 'home' in found_text and 'last played' in found_text:
            logger.info("On sub-main screen last played")
            return "Deck Select"
        
        found_text.append(extract_text(text_loc_dict['alchemy play'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['historic play'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['explorer play'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['bot match'], BRIGHT_THRESHOLD))
        
        # Fixed operator precedence - added proper parentheses
        if ('home' in found_text and 
            ('standard play' in found_text or
             'alchemy play' in found_text or
             'historic play' in found_text or
             'explorer play' in found_text or
             'bot match' in found_text)):
            logger.info("On sub-main screen table tab")
            return "Deck Select"
        
        found_text.append(extract_text(text_loc_dict['keep'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['mulligan'], BRIGHT_THRESHOLD))
        
        if 'keep' in found_text or 'mulligan' in found_text:
            logger.info("In Match")
            return "In Match"
        
        found_text.append(extract_text(text_loc_dict[MTGA_USER_NAME], BRIGHT_THRESHOLD))
        if MTGA_USER_NAME in found_text:
            logger.info("In Match")
            return "In Match"
        
        found_text.append(extract_text(text_loc_dict['defeat'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['victory'], BRIGHT_THRESHOLD))
        
        if 'defeat' in found_text or 'victory' in found_text:
            logger.info("Match results screen")
            return "match results"
        
        return None
    
    except Exception as e:
        logger.error(f"Error scanning screen for text: {e}")
        return None
    

def click_play():
    """Click the Play button."""
    logger.info("Clicking Play Button")
    leftClick(Cord.play_button)


def match_result_actions():
    """Handle actions after match results are displayed."""
    logger.info("Clicking to continue from match results")
    leftClick(Cord.click_to_continue)


def rewards_actions():
    """Handle rewards screen actions."""
    logger.info("Clicking Play (Claim) Button")
    leftClick(Cord.play_button)
    
def select_deck_and_play_style(play_style):
    """Selects the table tab, then the specified game type.
    
    Args:
        play_style: Coordinate tuple for the desired play style
    """
    logger.info("Selecting deck and play style")
    leftClick(Cord.table_icon_illum)
    time.sleep(0.25)
    leftClick(Cord.deck_select)
    time.sleep(0.25)
    leftClick(play_style)

def check_if_my_turn():

    check_mtga_window_size()
    # Look for a subset of items on the screen now that we already know we are in game
    found_text = []

    # Possible text states on screen:
    # During out turn:
        # 'next' + 'to combat'
        # 'no attacks' + 'all attack'
        # '# attackers' + 'to blockers'
        # 'next' + 'to blockers'
        # 'next' + 'to damage'
        # 'next' + 'to end'
    # Opponents turn:
        # 'opponents turn'
        # 'pass' + 'to attackers'
        # 'pass' + 'to blockers'
        # 'pass' + 'to damage'
        # 'my turn' + 'end turn'
    # NOTE: 
    # There are times where the 'to' in 'to xxxx' cant be found so we just look
    # for the second part of the phrase ex) instead of 'to block' just 'block'
    # TODO WHY IS THIS NOT FINDING COMBAT!?!?!
    found_text.append(extract_text(text_loc_dict['next'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['to combat'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('combat' in found_text)):
        print("*** MY TURN ***")
        return True
    
    found_text.append(extract_text(text_loc_dict['no attacks'], BRIGHT_THRESHOLD))    
    found_text.append(extract_text(text_loc_dict['all attack'], BRIGHT_THRESHOLD))
    if (('no attacks' in found_text) and ('all attack' in found_text)):
        print("*** MY TURN ***")
        return True
    
    found_text.append(extract_text(text_loc_dict['attacker'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['to blockers'], FAINT_THRESHOLD))    
    if ( (('attacker' in found_text) and ('to blockers' in found_text)) or
         (('next' in found_text) and ('blockers' in found_text)) ):
        print("*** MY TURN ***")
        return True
    
    found_text.append(extract_text(text_loc_dict['cancel attacks'], FAINT_THRESHOLD))
    if (('cancel attacks' in found_text) and ('blockers' in found_text)):
        print("*** MY TURN ***")
        return True
         
    found_text.append(extract_text(text_loc_dict['to damage'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('damage' in found_text)):
        print("*** MY TURN ***")
        return True
    
    found_text.append(extract_text(text_loc_dict['to end'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('end' in found_text)):
        print("*** MY TURN ***")
        return True
         
    found_text.append(extract_text(text_loc_dict['cancel'], BRIGHT_THRESHOLD))
    if (('cancel' in found_text)):
        print("*** MY TURN ***")
        return True
    
    # If none of the above were found then its our opponents turn
    print("*** OPPONENTS TURN ***")
    return False

def check_in_match():

    # If we are in match only certain text will be on the screen, check for:
    # MTGA_USER_NAME, mulligan, keep, next, pass, no block, no attack, all attack.
    # To speed up this call, only check if the match ended since we already "know"
    # we are in a match. So only look for 'defeat' or 'victory' 
    global MTGA_USER_NAME
    
    # Window may have changed, verify and re-set if needed.
    check_mtga_window_size()
    # Look for a subset of items on the screen now that we already know we are in game
    found_text = []
    
    found_text.append(extract_text(text_loc_dict['click to continue'], FAINT_THRESHOLD))                                           
    if ('click to continue' in found_text):
        return False
    else:
        return True
    
def check_if_card_action_and_perform():
    
    # Three possible paths when playing cards:
        # If the card could not be played the cancel button will be on screen.
        # If the card had a multiple choice we first address that and then re-evaluate.
        # Else the card played and we do nothing and move on
    
    found_text = []
        
    found_text.append(extract_text(text_loc_dict['cancel'], BRIGHT_THRESHOLD))
    if (('cancel' in found_text)):
            leftClick(Cord.cancel_button)
            return True
        
    found_text.append(extract_text(text_loc_dict['choose one'], BRIGHT_THRESHOLD))
    if (('choose one' in found_text)):
        # Regardless if we can play the card or not just click the left option
        # If it doesn't play we will be prompted with the cancel button
        leftClick(Cord.card_option_left_click)
        time.sleep(0.5)
        # Now check for the cancel button, if its there we could not play the card so 
        # click cancel and move on, if not the card played and do nothing.
        found_text.append(extract_text(text_loc_dict['cancel'], BRIGHT_THRESHOLD))
        if (('cancel' in found_text)):
            leftClick(Cord.cancel_button)
            return True
    
    return False

def check_if_my_card_draw_done():
    """Check if its our turn to draw cards or we detected we are returning to a 
    previously started match.
    """
    
    # The game window can be resized back to your default settings at different times.
    # Check the size and position on screen and reset if necessary
    check_mtga_window_size()
    
    # Lets see what we find on the screen
    found_text = []
    found_text.append(extract_text(text_loc_dict['keep'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['mulligan'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['view battlefield'], BRIGHT_THRESHOLD))
    
    if ( ("keep" in found_text) or
         ("mulligan" in found_text)):
        print("Selecting our cards")
        leftClick(Cord.keep_draw_button)
        return True
    elif ("view battlefield" in found_text):
        print("Waiting to pick our cards")
        return False
    else: 
        print("Assuming we are returning to an in-progress match")
        return True

def turn_phase():
    
    # Possible text states on screen:
    # During out turn:
        # 'next' + 'to combat'
        # 'no attacks' + 'all attack'
        # '# attackers' + 'to blockers'
        # 'next' + 'to blockers'
        # 'next' + 'to damage'
        # 'next' + 'to end'
    # Look for a subset of items on the screen now that we already know we are in game
    found_text = []
    #found_text.append(extract_text(text_loc_dict['resolve'], BRIGHT_THRESHOLD))

    # NOTE: 
    # There are times were the 'to' in 'to xxxx' cant be found so we just look
    # for the second part of the phrase ex) instead of 'to block' just 'block'
    
    found_text.append(extract_text(text_loc_dict['next'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['to combat'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('combat' in found_text)):
        return "play cards"
    
    found_text.append(extract_text(text_loc_dict['cancel'], BRIGHT_THRESHOLD))
    if (('cancel' in found_text)):
        return "play cards"
    
    # found_text.append(extract_text(text_loc_dict['choose one'], BRIGHT_THRESHOLD))
    # if (('choose one' in found_text)):
    #     return "play cards"
    
    found_text.append(extract_text(text_loc_dict['no attacks'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['all attack'], BRIGHT_THRESHOLD))
    if (('no attacks' in found_text) and ('all attack' in found_text)):
        return "attack phase"
    
    found_text.append(extract_text(text_loc_dict['attacker'], BRIGHT_THRESHOLD))
    found_text.append(extract_text(text_loc_dict['to blockers'], FAINT_THRESHOLD))
    if ( (('attacker' in found_text) and ('to blockers' in found_text)) or
         (('next' in found_text) and ('blockers' in found_text)) ):
        return "attack phase"
    
    found_text.append(extract_text(text_loc_dict['to damage'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('damage' in found_text)):
        return "attack phase"
    
    found_text.append(extract_text(text_loc_dict['to end'], FAINT_THRESHOLD))
    if (('next' in found_text) and ('end' in found_text)):
        return "end turn"
    
    # Assume our turn ended suddenly for some reason
    return "opponents turn"
    
def play_attack_phase():
    # Allow possibly not attacking on a given turn if the randomly generated range is less than ATTACK_PROBABILITY
    x = randrange(1, 101)
    if x <= ATTACK_PROBABILITY:
        leftClick(Cord.resolve_button)
        time.sleep(0.5)
        time.sleep(0.5)
        # In case opponent has a planeswalker, always select the player as the attack target
        leftClick(Cord.opponent_avatar)
        leftClick(Cord.resolve_button)
        
        # If the opponent has chosen multiple blockers just click the done button
        found_text = []
        found_text.append(extract_text(text_loc_dict['order blockers'], BLOCK_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['done'], BRIGHT_THRESHOLD))
        found_text.append(extract_text(text_loc_dict['first'], BRIGHT_THRESHOLD))
        if ( ('order blockers' in found_text) or
                ('done' in found_text) or
                ('first' in found_text)):
            print("Detected Block Order, clicking done...")
            leftClick(Cord.order_blockers_done)
    else:
        print("Clicking No Attack Button")
        leftClick(Cord.no_attacks_button)

def play_my_cards():
    """Keep trying to play cards from hand, if we have exhausted our cards to play but can attack
    trigger the attack phase button clicks, else move on.
    """
    # Its our turn, reset card cycles and start trying to play cards
    card_cycles = 1
    
    # Loop over our cards MAX_CARD_CYCLES times trying to play cards
    while card_cycles <= MAX_CARD_CYCLES:
        logger.info("Beginning play_my_cards phase...")
        
        # Keep track of times we hit cancel, if we hit it 0 times in a given
        # play through don't bother playing a second time through
        cancel_count = 0

        # Iterate over possible cards in our hand, this just picks spots on the screen
        # that may or may not have cards sitting where it clicks.
        for card in Cord.cards_in_hand:
            
            # If at any time the match has ended, immediately break
            if (check_in_match() == False):
                print("in the middle of playing cards but i think the match ended!")
            
            # Determine which phase we are in on our turn
            phase = turn_phase()
            if ("play cards" == phase):
                # Attempt to play a card from our hand
                doubleLeftClick(card)
                time.sleep(0.25)
                # If playing a card required an action (undo, select card option), check for it
                # and perform the action to continue game play. 
                if (check_if_card_action_and_perform()):
                    cancel_count += 1
                    
                if (check_if_card_action_and_perform()):
                    cancel_count += 1
                    
            elif ("attack phase" == phase):
                play_attack_phase()
                # Our turn is done, trigger leaving the card play loop
                card_cycles += 99
            
            elif ("opponents turn" == phase):
                print("Cant play any more cards and cant attack and its auto-moved to my opponents turn, ending my card play loop")
                card_cycles += 99

        # This is an attempt at speeding up the card play logic.
        # No cards were played this pass so none will be played next pass, exit loop
        if (0 != cancel_count):
            card_cycles += 1
            print("Card cycles is now {}/{}".format(card_cycles, MAX_CARD_CYCLES))
        else:
            card_cycles += 99
    else:
        print("Card cycles exceeded clicking next!")
        leftClick(Cord.next_button)

def match_actions():
    """Main match flow function. We don't leave here until a match has ended."""
    logger.info("Starting match_actions...")

    # Keep looping until we have drawn our cards or determined we are returning to an in progress game.
    while not check_if_my_card_draw_done():
        time.sleep(0.5)

    # MAIN match loop
    while check_in_match():
        logger.info("Beginning In-Match Loop")
        
        # The game window can be resized back to your default settings at different times.
        # Check the size and position on screen and reset if necessary
        check_mtga_window_size()
        
        # See if it's our opponent's turn and keep trying to press the resolve button
        # in the case where they have made an action that requires our response.
        while not check_if_my_turn():
            # Double check if it's actually our opponent's turn
            # There is a bit of a race condition here where we accidentally
            # skip our first stage of our turn.
            if not check_if_my_turn():
                # Just keep clicking "next" if we get any prompts
                leftClick(Cord.next_button)
            time.sleep(0.5)
        
        # Now it's our turn, determine phase of play
        phase = turn_phase()
        
        if phase == "play cards":
            # Attempt to play the cards in our hand
            play_my_cards()
        elif phase == "attack phase":
            play_attack_phase()
        elif phase == "end turn":
            leftClick(Cord.next_button)
    
    logger.info("Match is over, going back to main loop")


#########################################################
# MAIN
#########################################################

def main():
    """Main bot loop."""
    logger.info("*** Started MTGA Bot ***")
    
    # Check if MTGA window is available
    if not check_mtga_window_size():
        logger.error("Failed to find MTGA window. Please ensure the game is running.")
        return
    
    try:
        while True:
            # Verify the window is properly sized and its position on the screen is correct
            check_mtga_window_size()
            
            # We have no idea where we are, look for text all over the place
            screen = scan_screen_for_text()
            
            if screen == "Start":
                click_play()
            
            elif screen == "Deck Select":
                select_deck_and_play_style(Cord.bot_ply_chk)
                click_play()
                
            elif screen == "Replay":
                click_play()

            elif screen == "In Match":
                match_actions()

            elif screen == "match results":
                logger.info("Match end")
                match_result_actions()

            elif screen == "Rewards":
                rewards_actions()
            
            else:
                logger.warning(f"Unknown screen state: {screen}")

            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Bot shutting down")


if __name__ == "__main__":
    main()