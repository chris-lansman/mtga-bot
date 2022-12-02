"""
Used to determine the min/max intensity of a given "zone"
on the screen.

Increase/decrease total_samples to allow for more samples
"""
import PIL
import numpy
from PIL import ImageGrab
from PIL import ImageOps
import win32gui

def configure_mtga_window():
    # First find the 'MTGA' window, if the name in the upper left corner of the game window
    # when in windowed mode every changes you will need to update this screen
    window_handle = win32gui.FindWindow(None, "MTGA")
    # Move the window to a known offset (0,0) for the upper left corner, 
    # and force a resize so this works on every system every time
    win32gui.SetWindowPos(window_handle,None,0,0,1280,720,0)
    # Verify the coordinates are at (0,0,1920,1080)
    window_coordinates = win32gui.GetWindowRect(window_handle)
    
class Cord:

    # Maintain co-ordinates of locations to mouse click
#----verified
    bt_play =            (1160, 660) # The play button on the dashboard, bottom right, point is at the edge of the button
    bt_edit =            (155,665)   # The edit deck button on the left side of the screen
    bt_table_icon =      (1155,102)  # Table icon in the upper right of the screen after the main screen
    bt_recently_played = (1240,115)  # Recently played flag found on the screen after the main screen
    std_ply_chk =        (1065,330) # Standard play choice check mark on table screen
    alc_ply_chk =        (1065,370) # Alchemy play choice check mark on table screen
    his_ply_chk =        (1065,410) # History play choice check mark on table screen
    exp_ply_chk =        (1065,450) # Explorer play choice check mark on table screen
    bot_ply_chk =        (1065,480) # Bot play choice check mark on table screen
    def_deck =           (290,370)     # Deck just left of the big '+'
#----unverified       
    
    keep_bt = (1130,900)      # Keep button at start of match when cards are ready to pick
    mulligan_bt = (780,900)   # Mulligan button at start of match when cards are ready to pick
    # Card positions to play. Remove [::2] for all positions (less likely to need a 2nd cycle, but slower)
    cards_in_hand = ((1000,1079), 
                     (890,1079), 
                     (1050,1079), 
                     (840,1079), 
                     (1160,1079), 
                     (720,1079), 
                     (1225,1079), 
                     (660,1079),
                     (1325,1079), 
                     (540,1079), 
                     (1425,1079), 
                     (490,1079), 
                     (1550,1079), 
                     (360,1079))

    undo_button = (1870, 840)           # Undo button when casting a spell
    no_attacks_button = (1770, 880)     # During combat phase, the No Attacks button
    order_blockers_done = (970, 840)    # Click done to auto-assign damage to multiple blockers
    resolve_button = (1770, 950)        # Resolve button, also No Blocks during opponent combat
    keep_draw = (1140, 870)             # Accept drawn cards at start of match
    pass_turn = (1850, 1030)            # Pass turn button (during both player's turns)
    
    deck_select = (1750, 800)           # Click to select which deck to use
    white_deck = (450, 500)             # Todo - never used, purpose?
    green_deck = (760, 500)             # Todo - never used, purpose?
    black_deck = (1055, 500)            # Todo - never used, purpose?
    blue_deck = (1350, 500)             # Todo - never used, purpose?
    red_deck = (170, 685)               # Above decks not actually required, this cord always selects the next in cycle
    
    smiley_face_continue = (960, 850)   # Skip on smiley face screen
    opponent_avatar = (955, 105)        # To select when attacking in case opponent has Planeswalker in play
    cancel_area = (1730, 1030)          # Just a blank area to click to cancel
    p1_main = (840,877)


class Zone:
    """
    Maintain co-ordinates of zones/boxes that will be analyzed for grayscale value
    """
    # Define bounding box sizes in pixel offsets (i.e. a 5 means 5x5 pixels)
    BB_TINY = 2
    BB_SMALL = 5
    BB_MEDIUM = 10
    BB_LARGE = 15
        
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

#--Verified in the correct place as of 11/16/22
    # On opening screen at game launch
    bt_play =      create_bb(Cord.bt_play, BB_SMALL)    # Main screen play button
    edit_deck_bt = create_bb(Cord.bt_edit, BB_SMALL)      # After you press play on the main screen the edit button shows
    table_bt =     create_bb(Cord.bt_table_icon, BB_TINY) # After you press play on the main screen the table icon shows
    rec_bt =       create_bb(Cord.bt_recently_played, BB_TINY)   # After you press play on the main screen the recently played icon shows
#--broken-needs_fixing
    
#--NOT_VERIFIED yet
    friends_icon = (30, 1005, 35, 1015)         # In match, Match Victory, or Match Defeat
    match_result = (1835, 1020, 1868, 1038)     # Match is over and awaiting click
    undo_but = (1860, 830, 1870, 840)           # Undo button, appears when not sufficient mana to cast card
    p1_main_phase = (830, 872, 840, 882)        # Main phase icon, indicating your turn, or not first main
    p1_second_phase = (1080, 870, 1090, 880)    # Second phase icon
    p2_main_phase = (850, 118, 860, 128)        # Opponent Main phase icon
    p2_second_phase = (1058, 118, 1068, 128)    # Opponent Second phase icon
    mulligan_button = (764, 857, 766, 877)      # Confirms start of match Mulligan/Keep
    shield_icon = (1770, 824, 1780, 834)        # Shield icon, black when having to choose No/All Attack
    block_order = (1316, 783, 1329, 785)        # Screen when opponent chooses multiple blockers
    harmonix_name = (98, 1030, 99, 1040)        # Player name at bottom left of combat screen
    smiley_face = (1236, 426, 1240, 455)        # Last 'h' on smiley face "Did you have fun" screen
    
    p1_main = create_bb(Cord.p1_main, BB_SMALL)
    
def get_grey_scale_value(bbox):
    # bbox - list of 4 values defining the x,y of the upper left corner and lower right corners of a box (x,y,x,y)
    
    # Grab an RGB image defined by the bounding box (bbox)
    RGB_image = PIL.ImageGrab.grab(bbox)
    # Convert the rgb image into a grey-scale image
    # We do this to get the "intensity" values for each pixel in the box we defined
    # Now the color in the box does not matter but the intensity of the collective pixels does.
    GS_image = PIL.ImageOps.grayscale(RGB_image)
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

min = 9999
max = 0
total_samples = 100

#configure_mtga_window()

while total_samples:
    but_play_value = get_grey_scale_value(Zone.p1_main)
    print(but_play_value)
    if but_play_value > max:
        max = but_play_value
    if min > but_play_value:
        min = but_play_value
    total_samples -= 1

print(f"Value Range - min:{min}, max:{max}")