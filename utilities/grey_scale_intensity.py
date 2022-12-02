"""
Utility to constantly generate the grey scale intensity value of a given 5x5 pixel box on the screen
"""
import numpy
import pyautogui
from PIL import ImageGrab
from PIL import ImageOps


def get_grey_scale_sum(bbox):
    # bbox - list of 4 values defining the x,y of the upper left corner and lower right corners of a box (x,y,x,y)
    
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

bound_box_size = 5

while True:
    # First get the current mouse position
    cur_pos = pyautogui.position()
    # Form a basic 3x3 box around the current mouse pixel coordinates
    box = (cur_pos.x, cur_pos.y, cur_pos.x+bound_box_size, cur_pos.y+bound_box_size) 
    print(f"{get_grey_scale_sum(box)}, {cur_pos}")