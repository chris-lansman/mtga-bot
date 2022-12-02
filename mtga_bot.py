"""
Magic The Gathering Arena bot that auto-plays to brute force daily and weekly rewards for gold/XP.
MTGA should be in windowed mode.
Program assumes a default size of 1600 x 900, on primary monitor, and graphics adjusted to low. 
Note: All scaling will be done from a 1600x900 offset of where the original pixels were at this resolution
MTGA client needs to
be already launched and signed into (or you can use a BAT file to launch this script and game simultaneously as a
scheduled task).
This bot will not work out of the box if you run it now. It's dependant on grayscale values at various points on
the screen. I'm not providing the values I used in the code, firstly because it's dependant on screen resolution and
untested on any machine other than my own, and second because I don't want just anybody who comes across this to be
able to take advantage and run a MTGA bot. I'm posting this primarily as a record of the code, not because I want to
distribute a bot. You will have to figure out the grayscale values in the Range class for yourself. I've left some
in for reference.
~ defaultroot - 8th Feb 2020
"""


from PIL import ImageGrab, ImageOps
import numpy # gives us access to array
import time
import win32api, win32con
from random import randrange
from datetime import datetime
import logging
import win32gui
import pyautogui

# ----- SETTINGS -----
# These settings can be used to fine tune how the bot acts. It may be the case that the bot is clicking too fast or slow
# on your machine, resulting in loops being broken. Below are the settings that worked on my own machine.

ATTACK_PROBABILITY = 100            # Percentage chance that the bot will attack with all creatures

MAX_CARD_CYCLES = 2                 # Maximum number of times the bot will cycle through cards attempting to play them

DAILY_FULL_GAMES = 30               # How many full games will be played in a rotation before going to slow play mode
SECONDS_UNTIL_ROTATION = 43200      # How often the bot will switch from slow play mode (86400 = 1 day, 3600 = 1 hour)

SPEED_PLAY_CARD = 0.5               # Delay between attempting to play a card
SPEED_DECK_SELECT = 1               # Delay between clicks on deck select screen
SPEED_OPPONENT_TURN_CLICK = 1       # Delay between clicking Resolve button during opponents turn

SLOW_PLAY_MODE = False              # When True, don't accept draw at Mulligan and don't play (STATIC_CLICK_DRAW_ACCEPT must be False)
STATIC_CLICK_DRAW_ACCEPT = True     # A fix for difficulty detecting draw accept. Clicks Accept after x seconds delay.
SLOW_DRAW_bt_play_MULLIGAN_PRESS_DELAY = 10    # Delay before pressing the accept draw button (may not always hit)

CLICKS_DISABLED = False             # Mouse clicks will not register, for testing
MOUSE_MOVE_DISABLE = False          # Mouse movement will not register, for testing

LOG_LEVEL = logging.INFO

WINDOW_LOC_REZ = (0,0,1920,1080) # Expected resolution and location of game window
# ----- GLOBALS -----

DECK_COLORS = ['Green', 'Black', 'White', 'Blue', 'Red'] # Decks for auto select
GAME_COUNT = 0                                           # Keep track of full games
start_time_utc = (datetime.today()).timestamp()          # Time when bot started in UTC

# ----- SET UP LOGGING -----

logger = logging.getLogger('mtgalog')
hdlr = logging.FileHandler('mtgalog.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(LOG_LEVEL)

# -------------------


class Cord:

    # Maintain co-ordinates of locations to mouse click
    play_button_edge =  (1614, 980) # The play button on the dashboard, bottom right, point is at the edge of the button
    play_button =       (1665,1000)
    click_to_continue = (250, 200)   # Clicking (almost) anywhere on the screen to advance (usually after a match)
    edit_deck =         (238,1035)   # The edit deck button on the left side of the screen
    table_icon_illum =  (1740,145)  # Table icon in the upper right of the screen after the main screen
    recently_played =   (1872,167)  # Recently played flag found on the screen after the main screen
    gold_coins =        (1447,67)
    gems =              (1566,70)
    home_tab_main =     (111,104) # Home button in the upper left on the main screen
    
    # Sub-main screen items
    deck_select =          (460,580) # Deck just left of the big '+'
    sub_screen_empty_pt1 = (60,240)  # Empty area on the left side of the screen
    sub_screen_empty_pt2 = (60,380)
    sub_screen_empty_pt3 = (60,550)
    sub_screen_empty_pt4 = (60,750)
    
    # Mode icon diamonds
    std_ply_chk =        (1600,510) # Standard play choice check mark on table screen
    alc_ply_chk =        (1600,570) # Alchemy play choice check mark on table screen
    his_ply_chk =        (1600,630) # History play choice check mark on table screen
    exp_ply_chk =        (1600,690) # Explorer play choice check mark on table screen
    bot_ply_chk =        (1600,750) # Bot play choice check mark on table screen
    
    # In-game items
    keep_draw_button =      (1130, 870)  # Accept drawn cards at start of match
    mulligan_button =       (681,847)    # Mulligan button at start of match when cards are ready to pick
    question_mark_area =    (610,876)    # dark spot next to the question mark icon on the select card screen at start of match
    friends_icon =          (40,1030)    # Friends icon in the lower left corner
    pass_turn =             (1850, 1030) # Pass turn button (during both player's turns)
    no_attacks_button =     (1770, 880)  # During combat phase, the No Attacks button
    opponent_avatar =       (970, 136)   # To select when attacking in case opponent has Planeswalker in play
    undo_button =           (1864, 747)  # Undo button when casting a spell
    resolve_button =        (1770, 950)  # Resolve button, also No Blocks during opponent combat
    cancel_area =           (1730, 1030) # Just a blank area to click to cancel
    order_blockers_done =   (970, 840)   # Click done to auto-assign damage to multiple blockers
    p1_main_phase =         (840,878)
    p1_second_phase =       (1081,877)
    p2_main_phase =         (859,151)
    p2_second_phase =       (1062,151)
    card_option_left =      (623,316)
    card_option_left_click = (751,483)
    shield_icon =           (1758,832)
    cancel_button =         (959,871)
    next_button =           (1780,940)
    sword_icon =            (1726,830)
    block_order =           (1316, 783)
    blocking_shield =       (1759,895)

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

class Zone:
    """
    Maintain co-ordinates of zones/boxes that will be analyzed for grayscale value
    """
    # Define bounding box sizes in pixel offsets (i.e. a 5 means 5x5 pixels)
    BB_2X2 = 2
    BB_5X5 = 5
    BB_10x10 = 10
        
    def create_bb(m_pt, bb_size):
        """Returns a bounding box given a current x,y coordinate

        Args:
            m_pt (x,y): coordinate on the screen
            bb_size (int): size in pixels of a bounding box

        Returns:
            tuple: bounding box coordinates (upper left x, upper left y, lower right x, lower right y)
        """
        return (m_pt[0], 
                m_pt[1], 
                m_pt[0]+bb_size, 
                m_pt[1]+bb_size)
    # Pre-match items
    play_button_edge = create_bb(Cord.play_button_edge, BB_5X5)      # Main screen play button
    edit_deck_button = create_bb(Cord.edit_deck, BB_5X5)        # After you press play on the main screen the edit button shows
    table_button =     create_bb(Cord.table_icon_illum, BB_2X2) # After you press play on the main screen the table icon shows
    favorite_button =  create_bb(Cord.recently_played, BB_2X2)  # After you press play on the main screen the recently played button
    gold_coins =       create_bb(Cord.gold_coins, BB_2X2)       # Gold coins found before you start a match
    gems =             create_bb(Cord.gems, BB_2X2)             # gems found before you start a match
    home_tab_main =    create_bb(Cord.home_tab_main, BB_5X5)    # Home tab on the upper left on the main screen

    # Modes
    standard_play = create_bb(Cord.std_ply_chk, BB_2X2)
    alchemy_play =  create_bb(Cord.alc_ply_chk, BB_2X2)
    historic_play = create_bb(Cord.his_ply_chk, BB_2X2)
    explorer_play = create_bb(Cord.exp_ply_chk, BB_2X2)
    bot_play =      create_bb(Cord.bot_ply_chk, BB_2X2)
    
    # Empty area on the left side of the screen on the sub-main screen
    sub_screen_empty_pt1 = create_bb(Cord.sub_screen_empty_pt1, BB_5X5)
    sub_screen_empty_pt2 = create_bb(Cord.sub_screen_empty_pt2, BB_5X5)
    sub_screen_empty_pt3 = create_bb(Cord.sub_screen_empty_pt3, BB_5X5)
    sub_screen_empty_pt4 = create_bb(Cord.sub_screen_empty_pt4, BB_5X5)
    
    # In-game items
    keep_draw_button =      create_bb(Cord.keep_draw_button, BB_5X5)
    mulligan_button =       create_bb(Cord.mulligan_button, BB_5X5)
    question_mark_area =    create_bb(Cord.question_mark_area, BB_5X5) 
    friends_icon =          create_bb(Cord.friends_icon, BB_2X2)
    opponent_avatar =       create_bb(Cord.opponent_avatar, BB_5X5)
    next_button =           create_bb(Cord.next_button, BB_5X5)
    cancel_button =         create_bb(Cord.cancel_button, BB_5X5)
    no_attacks_button =     create_bb(Cord.no_attacks_button, BB_5X5)
    blocking_shield =       create_bb(Cord.blocking_shield, BB_5X5)
    
    # End-game items
    
    # In-match items
    undo_button = create_bb(Cord.undo_button, BB_5X5)
    p1_main_phase = create_bb(Cord.p1_main_phase, BB_5X5)       # Main phase icon, indicating your turn, or not first main
    p1_second_phase = create_bb(Cord.p1_second_phase, BB_5X5)   # Second phase icon
    p2_main_phase = create_bb(Cord.p2_main_phase, BB_5X5)       # Opponent Main phase icon
    p2_second_phase = create_bb(Cord.p2_second_phase, BB_5X5)   # Opponent Second phase icon
    card_has_play_option = create_bb(Cord.card_option_left, BB_2X2) # Some cards have two play options, this is the left option corner that glows
    shield_icon = create_bb(Cord.shield_icon, BB_5X5)           # Shield icon, black when having to choose No/All Attack
    sword_icon =  create_bb(Cord.sword_icon, BB_2X2)
    
    #Not verified
    block_order = create_bb(Cord.block_order, BB_2X2)

class Range:
    """
    Range of grey scale intensity values that a Zone should fall within to trigger a positive match\n
    Any (0, 0) values below need to be amended with the correct range
    
    """
    play_button_edge = (1500,3000)  # Range if the button is present
    edit_deck_button = (500,800)   # If we are on the main screen the intensity should be < 500, else we have the button there
    gold_coins =       (500,700)
    gems =             (600,700)
    recently_played =  (200,300)    # Recently played button on screen after main screen
    table_icon_illum = (200,300) # Table button on screen after main screen
    play_style_illum = (200,600)
    sub_screen_empty_pt = (0,50) # Should be nearly black if we are on the sub-main screen
    home_tab_main =    (1000,1500)
    
    # In-game items
    keep_draw_button =      (3000,4000)
    mulligan_button =       (3000,5000)
    question_mark_area =    (0,200)
    friends_icon_in_match = (200,500)
    p1_main_phase =         (500, 600)
    p1_second_phase =       (500, 600)
    p2_main_phase =         (700, 800)
    p2_second_phase =       (700, 800)
    undo_button =           (500, 800)
    opponent_avatar =       (1000,1300)
    choose_one_option =     (500,600)
    combat_shield_icon =    (500, 600)
    sword_icon =            (500,1000)
    next_button =           (1500,3500)
    cancel_button =         (2300,2600)
    no_attacks_button =     (1000,2500)
    blocking_shield =       (500,600)
    # End-game items
    friends_icon_match_result = (0, 70)
    friends_icon_rewards =      (0, 70)

#TODO Unverified
    block_order = (500, 600)

# This is sketchy update
def check_if_new_day(start_time_utc):
    split = (datetime.today()).timestamp()

    print(f"The last mode change was {start_time}")
    print(f"The current time is {split}")
    print(f"The difference is {split - start_time} seconds")

    if (split - start_time) > SECONDS_UNTIL_ROTATION:
        print("It's been longer than a day")
        global start
        start = (datetime.today()).timestamp()
        return True
    else:
        print("It hasn't been a day yet")
        return False

def new_day_actions():
    global SLOW_PLAY_MODE
    print(f"SLOW_PLAY_MODE pre function: {SLOW_PLAY_MODE}")
    if SLOW_PLAY_MODE == False:
        SLOW_PLAY_MODE = True
    else:
        SLOW_PLAY_MODE = False

    print(f"SLOW_PLAY_MODE post function: {SLOW_PLAY_MODE}")

def leftClick(p):
    """Performs a single left click of the mouse at position p

    Args:
        p (x,y): coordinate on screen where we want the mouse to click
    """
    if CLICKS_DISABLED:
        pass
    else:
        pyautogui.mouseDown(x=p[0], y=p[1]); 
        pyautogui.mouseUp(x=p[0], y=p[1])

def doubleLeftClick(p):
    """Performs a double left click of the mouse at position p

    Args:
        p (x,y): coordinate on screen where we want the mouse to click
    """
    if CLICKS_DISABLED:
        pass
    else:
        pyautogui.doubleClick(x=p[0], y=p[1], interval=0.25)

def mousePos(cord):
    """Sets the mouse cursor to a specific set of coordinates on the screen

    Args:
        cord (x,y): position on the screen
    """
    if MOUSE_MOVE_DISABLE:
        pass
    else:
        win32api.SetCursorPos((cord[0], cord[1]))

def get_grey_scale_sum(bbox):
    """Calculates the greyscale value sum of a bounding box given a set of x,y coordinates

    Args:
        bbox (ul_x,ul_y,lr_x,lr_y): two sets of coordinates which define a bounding box\n
        ul - upper left\n
        lr - lower right

    Returns:
        int: sum of pixel values found within the bounding box
    """
    
    # Grab an RGB image defined by the bounding box (bbox)
    RGB_image = ImageGrab.grab(bbox)
    # Convert the rgb image into a grey-scale image
    # We do this to get the "intensity" values for each pixel in the box we defined
    # Now the color in the box does not matter but the intensity of the collective pixels does.
    GS_image = ImageOps.grayscale(RGB_image)
    # Returns a list of (# pixels with value, value)
    pixel_intensity_counts = GS_image.getcolors()
    # Converts the list into a numpy array of arrays
    # Note: a list that looks like [(1,33), (2,44)] turns into
    #    a == [array([1,33]), array([2,44])]
    # We have to do this because python cannot natively add a bunch of tuples together
    a = numpy.array(pixel_intensity_counts)
    # Now that we have an array of arrays sum up everything in the newly flattened array
    # Note: This also adds in '# pixels with value` to the total so an array like:
    #   [array([1,33]), array([2,44])] 
    #   sums to -> 1+33+2+44 = 80
    a = a.sum()
    # Returns the "total intensity" found within the boundbox provided to this function.
    # The individual intensity values are in grey scale going from 0(black) to 255(white)
    return a

def check_mtga_window_size():
    # First find the 'MTGA' window, if the name in the upper left corner of the game window
    # when in windowed mode every changes you will need to update this screen
    # We only need to set this once.
    window_handle = win32gui.FindWindow(None, "MTGA")
    # Get the windows coordinates
    window_coordinates = win32gui.GetWindowRect(window_handle)
    # Verify the window is in the upper left corner of the screen 
    # and that it is the correct size, if not set it properly.
    if (WINDOW_LOC_REZ != window_coordinates):
        # Move the window to a known offset (0,0) for the upper left corner, 
        # and force a resize so this works on every system every time
        win32gui.SetWindowPos(window_handle, None,0,0,1920,1080,0)
        # Verify the coordinates are at (0,0,1920,1080)
        

def scan_screen():
    """Calculate total intensities (in grey scale) for various buttons which\n
       may or may not be on the screen in the location where we expect to find them.\n
       We use "zones" to define small bounding boxes around the pixel where we expect\n
       to find the item in question.\n
       Then use logic to try and deduce which screen the game is currently sitting on.
    """
    play_button_value = get_grey_scale_sum(Zone.play_button_edge)
    favorite_button_value = get_grey_scale_sum(Zone.favorite_button)
    table_button_value = get_grey_scale_sum(Zone.table_button)
    
    standard_play_value = get_grey_scale_sum(Zone.standard_play)
    alchemy_play_value = get_grey_scale_sum(Zone.alchemy_play)
    historic_play_value = get_grey_scale_sum(Zone.historic_play)
    explorer_play_value = get_grey_scale_sum(Zone.explorer_play)
    bot_play_value = get_grey_scale_sum(Zone.bot_play)
    
    sub_screen_empty_pt1_value = get_grey_scale_sum(Zone.sub_screen_empty_pt1)
    sub_screen_empty_pt2_value = get_grey_scale_sum(Zone.sub_screen_empty_pt2)
    sub_screen_empty_pt3_value = get_grey_scale_sum(Zone.sub_screen_empty_pt3)
    sub_screen_empty_pt4_value = get_grey_scale_sum(Zone.sub_screen_empty_pt4)
    
    friends_icon_value = get_grey_scale_sum(Zone.friends_icon)

    ###########################################################################################################
    # Now that we have calculated a bunch of grey scale total intensity values, lets try and reason out which 
    # screen we might be sitting on
    ###########################################################################################################
    
    # The main screen when the game first starts and the sub-main after you click the play button once are
    # fairly difficult to tell apart, not too many things change between the two. Lets try and solve for
    # the main screen when the game starts or you end a match
    if ((play_button_value in range(Range.play_button_edge[0], Range.play_button_edge[1])) and \
          ((sub_screen_empty_pt1_value not in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
           (sub_screen_empty_pt2_value not in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
           (sub_screen_empty_pt3_value not in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
           (sub_screen_empty_pt4_value not in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])))
       ):
        print("On start screen with Play button")
        return("Start")
    
    elif ( (play_button_value in range(Range.play_button_edge[0], Range.play_button_edge[1])) and \
            ((sub_screen_empty_pt1_value in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
             (sub_screen_empty_pt2_value in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
             (sub_screen_empty_pt3_value in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])) and
             (sub_screen_empty_pt4_value in range(Range.sub_screen_empty_pt[0], Range.sub_screen_empty_pt[1])))
         ):
        print("On Recently Played screen and Play button Illuminated")
        return("Replay")
    
    elif ( (table_button_value in range(Range.table_icon_illum[0], Range.table_icon_illum[1])) and \
            ((standard_play_value in range(Range.play_style_illum[0], Range.play_style_illum[1])) or
             (alchemy_play_value in range(Range.play_style_illum[0], Range.play_style_illum[1])) or
             (historic_play_value in range(Range.play_style_illum[0], Range.play_style_illum[1])) or
             (explorer_play_value in range(Range.play_style_illum[0], Range.play_style_illum[1])) or
             (bot_play_value in range(Range.play_style_illum[0], Range.play_style_illum[1])))
         ):
        print("On deck select screen table selected but no deck picked, Play Button dark")
        return("Deck Select")
    
    elif check_in_match():
        print("In Match")
        return("In Match")

    elif (friends_icon_value in range(Range.friends_icon_match_result[0], Range.friends_icon_match_result[1])):
        print("On match result screen")
        return("Match Result")
    
    elif friends_icon_value in range(Range.friends_icon_rewards[0], Range.friends_icon_rewards[1]):
        print("On Rewards Screen")
        return("Rewards")


def click_play():
    """
    Click the "Play" button and then click the 'Table' icon so we can get our game\n
    into a known state before we get going.
    """
    print("Clicking Play Button")
    leftClick(Cord.play_button)

def match_result_actions():

    # Just click anywhere to proceed
    print("Clicking to continue")
    leftClick(Cord.click_to_continue)


def rewards_actions():

    # Click Start (Claim Prize)

    print("Clicking Play (Claim) Button")
    leftClick(Cord.bt_play)
    
def select_deck_and_play_style(play_style):
    """Picks our default deck and 
    """
    leftClick(Cord.deck_select)
    leftClick(play_style)

def check_if_my_turn():
    # TODO Update the logic here, as there is a situation in which none of these icons are illuminated but 
    # the opponent is waiting for US to make a choice on which of our creatures on the board will block or not
    # the logic needs to be updated to check for this case and make the correct clicks
    
    p1_main_phase_grayscale =   get_grey_scale_sum(Zone.p1_main_phase)
    p1_second_phase_grayscale = get_grey_scale_sum(Zone.p1_second_phase)
    p2_main_phase_value =       get_grey_scale_sum(Zone.p2_main_phase)
    p2_second_phase_value =     get_grey_scale_sum(Zone.p2_second_phase)
    blocking_shield_value =     get_grey_scale_sum(Zone.blocking_shield)

    if ((p2_main_phase_value in range(Range.p2_main_phase[0], Range.p2_main_phase[1])) or
        (p2_second_phase_value in range(Range.p2_second_phase[0], Range.p2_second_phase[1]))) \
            and ((p1_main_phase_grayscale not in range(Range.p1_main_phase[0], Range.p1_main_phase[1])) or
                 (p1_second_phase_grayscale not in range(Range.p1_second_phase[0], Range.p1_second_phase[1]))):
        print("*** OPPONENT TURN ***")
        leftClick(Cord.resolve_button)
        return False
    elif ((blocking_shield_value in range(Range.blocking_shield[0], Range.blocking_shield[1]))):
        print("*** OPPONENT TURN NO BLOCKS***")
        leftClick(Cord.resolve_button)
        return False
    else:
        return True


def check_in_match():
    """Check the color of the friends icon in the lower left of the screen.
    During a match it will be brighter than when the match is over.

    Returns:
        True/False: if we are in a match or not
    """
    
    in_match_friend_icon_value = get_grey_scale_sum(Zone.friends_icon)
    home_tab_value =             get_grey_scale_sum(Zone.home_tab_main)

    if (in_match_friend_icon_value in range(Range.friends_icon_in_match[0], Range.friends_icon_in_match[1]) and
         (home_tab_value not in range(Range.home_tab_main[0], Range.home_tab_main[1]))):
        return True
    else:
        return False

def check_if_in_combat_phase():
    
    shield_icon_value =      get_grey_scale_sum(Zone.shield_icon)
    sword_icon_value =       get_grey_scale_sum(Zone.sword_icon)
    no_attack_button_value = get_grey_scale_sum(Zone.no_attacks_button)
    p1_main_phase_grayscale = get_grey_scale_sum(Zone.p1_main_phase)
    
    if ( ((shield_icon_value in range(Range.combat_shield_icon[0], Range.combat_shield_icon[1])) and
            ((p1_main_phase_grayscale not in range(Range.p1_main_phase[0], Range.p1_main_phase[1])))) or
           ( (sword_icon_value in range(Range.sword_icon[0], Range.sword_icon[1])) and
             (no_attack_button_value in range(Range.no_attacks_button[0], Range.no_attacks_button[1])) and
             ((p1_main_phase_grayscale not in range(Range.p1_main_phase[0], Range.p1_main_phase[1]))))):
        print("Confirmed combat phase")
        return True
    else:
        return False
    
def check_if_card_action_and_perform():
    
    # Now that we may or may not have played a card, check for a number of possible
    # game states, i.e. cant play the card (undo)or  card has two choices when played 
    # and I can play it (click the left option), or I cant (click undo). This does not
    # support playing the right choice if there are two so dont make decks that expect it.
    undo_button_value =          get_grey_scale_sum(Zone.undo_button)
    card_has_play_option_value = get_grey_scale_sum(Zone.card_has_play_option)
    next_button_value =          get_grey_scale_sum(Zone.next_button)
    cancel_button_value =        get_grey_scale_sum(Zone.cancel_button)
    # First check if the card cant be played due to the mana cost being more than we have on the board
    if (undo_button_value in range(Range.undo_button[0], Range.undo_button[1])):
        print("Detected Undo button, so pressing it...")
        leftClick(Cord.undo_button)
    # Check if the card played has an option to play it two ways, and if the left option is glowing
    elif (card_has_play_option_value in range(Range.choose_one_option[0], Range.choose_one_option[1])):
        print("Card had choose one option value! Clicking the left option")
        leftClick(Cord.card_option_left_click)
    # Check if the card played has an option to play it two ways, and if the left option is NOT glowing
    elif (card_has_play_option_value not in range(Range.choose_one_option[0], Range.choose_one_option[1]) and
            (next_button_value not in range(Range.next_button[0], Range.next_button[1])) and
            (cancel_button_value in range(Range.cancel_button[0], Range.cancel_button[1]))):
        print("Card had choose one option value! But I can't play it, click cancel")
        leftClick(Cord.cancel_button)

def check_if_my_card_draw_done():
    """Check if its our turn to draw cards or we detected we are returning to a 
    previously started match.
    """
    
    # The game window can be resized back to your default settings at different times.
    # Check the size and position on screen and reset if necessary
    check_mtga_window_size()
    
    keep_draw_button_value =      get_grey_scale_sum(Zone.keep_draw_button)
    mulligan_button_value =       get_grey_scale_sum(Zone.mulligan_button)
    question_mark_area_value = get_grey_scale_sum(Zone.question_mark_area)
    opponent_avatar_value =       get_grey_scale_sum(Zone.opponent_avatar)
    friends_icon_value =          get_grey_scale_sum(Zone.friends_icon)
    
    if ( (keep_draw_button_value in range(Range.keep_draw_button[0], Range.keep_draw_button[1])) and
            (mulligan_button_value in range(Range.mulligan_button[0], Range.mulligan_button[1])) and
            (question_mark_area_value in range(Range.question_mark_area[0], Range.question_mark_area[1]))
        ):
        print("Yey, its our turn to draw cards!")
        leftClick(Cord.keep_draw_button)
        return True
        
    elif ( (opponent_avatar_value in range(Range.opponent_avatar[0], Range.opponent_avatar[1])) and
            (friends_icon_value in range(Range.friends_icon_in_match[0], Range.friends_icon_in_match[1]))
            ):
        print("Returning to an in progress match")
        return True
    
    return False

def play_my_cards():
    """Keep trying to play cards from hand, if we have exhausted our cards to play but can attack
    trigger the attack phase button clicks, else move on.
    """
    
    # Its our turn, reset card cycles and start trying to play cards
    card_cycles = 1
    # Loop over our cards MAX_CARD_CYCLES times trying to play cards
    while(card_cycles <= MAX_CARD_CYCLES):

        print("Beginning card cycle phase...")

        # Iterate over possible cards in our hand, this just picks spots on the screen
        # that may or may not have cards sitting where it clicks.
        for card in (Cord.cards_in_hand):
            
            # If at any time the match has ended, immediately break
            if check_in_match() == False:
                break
            
            # See if we have entered the combat phase, i.e. we have no cards left to play
            # and there is a creature on the board who can attack
            if (check_if_in_combat_phase() == True):
                # Allow possibly not attacking on a given turn if the randomly generated range is less than ATTACK_PROBABILITY
                x = randrange(1, 101)
                if x <= ATTACK_PROBABILITY:
                    leftClick(Cord.resolve_button)
                    time.sleep(1)
                    # In case opponent has a planeswalker, always select the player as the attack target
                    leftClick(Cord.opponent_avatar)
                    leftClick(Cord.resolve_button)
                    
                    # If the opponent has chosen multiple blockers just click the done button
                    block_order_value = get_grey_scale_sum(Zone.block_order)
                    if block_order_value in range(Range.block_order[0], Range.block_order[1]):
                        print("Detected Block Order, clicking done...")
                        leftClick(Cord.order_blockers_done)
                else:
                    print("Clicking No Attack Button")
                    leftClick(Cord.no_attacks_button)
                # Prevent trying to play cards again the next time around and leave this card cycle
                card_cycles += 99
                break

            elif (check_if_my_turn() == False):
                print("Cant play any more cards and cant attack and its auto-moved to my opponents turn, ending my card play loop")
                card_cycles += 99
                break

            # Attempt to play a card from our hand
            time.sleep(SPEED_PLAY_CARD)
            doubleLeftClick(card)
            time.sleep(1)
            
            # If playing a card required an action (undo, select card option), check for it
            # and perform the action to continue game play. 
            check_if_card_action_and_perform()

        print("Gone through all cards in hand, so incrementing card_cycles by 1")
        card_cycles += 1
        print("Card cycles is now {}/{}".format(card_cycles, MAX_CARD_CYCLES))

def match_actions():
    """Main match flow function. We dont leave here until a match has ended.
    """
    global GAME_COUNT
    print("Starting match_actions...")

    # Keep looping until we have drawn our cards or determined we are returning to an in progress game.
    while(check_if_my_card_draw_done() == False):
        None

    # MAIN match loop
    while(check_in_match() == True):
        print("Beginning In-Match Loop")
        
        # The game window can be resized back to your default settings at different times.
        # Check the size and position on screen and reset if necessary
        check_mtga_window_size()
        
        # See if it's our opponent's turn and keep trying to press the resolve button
        # in the case where they have made an action that requires our response.
        while(check_if_my_turn() == False):
            None

        # Attempt to play the cards in our hand
        play_my_cards()

        print("Should have completed all card_cycles, so now clicking resolve_button")
        leftClick(Cord.resolve_button)

    else:
        print("Match is over, going back to main loop")

logger.info("*** Started mgta_bot ***")
while True:
    # This bot is going to assume its started while sitting at the main screen. DO NOT attempt to 
    # start it from any other screen.
    check_mtga_window_size()
    screen = scan_screen()
    
    if screen == "Start":
        click_play()
    
    elif screen == "Deck Select":
        select_deck_and_play_style(Cord.bot_ply_chk)
        click_play()
        
    elif screen == "Replay":
        click_play()

    elif (screen == "In Match"):
        if (SLOW_PLAY_MODE and not STATIC_CLICK_DRAW_ACCEPT):
            pass
            if check_if_new_day(start_time_utc):
                SLOW_PLAY_MODE = False
        else:
            match_actions()
            GAME_COUNT += 1
            logger.info(f"Incremented GAME_COUNT to {GAME_COUNT}/{DAILY_FULL_GAMES}")
            if GAME_COUNT >= DAILY_FULL_GAMES:
                SLOW_PLAY_MODE = True
                GAME_COUNT = 0

    elif screen == "Match Result":
        logger.info("Match end")
        match_result_actions()

    elif screen == "Rewards":
        rewards_actions()

    print(f"***** GAME COUNT: {GAME_COUNT} / {DAILY_FULL_GAMES} ***** SLOW MODE: {SLOW_PLAY_MODE} *****")

    time.sleep(1)