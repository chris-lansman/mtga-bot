import PIL
import numpy
from PIL import ImageGrab
from PIL import ImageOps

class Zone:

    # Maintain co-ordinates of zones/boxes that will be analyzed for grayscale value

    but_play = (1705, 1000, 1708, 1005)         # On opening screen at game launch
    but_play_sidebar = (1900, 670, 1905, 675)   # After you press play to choose deck
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

while total_samples:
    but_play_value = get_grey_scale_value(Zone.but_play)
    print(but_play_value)
    if but_play_value > max:
        max = but_play_value
    if min > but_play_value:
        min = but_play_value
    total_samples -= 1

print(f"min:{min}, max:{max}")