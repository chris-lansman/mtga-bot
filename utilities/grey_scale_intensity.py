"""
Utility to constantly generate the grey scale intensity value of a given 5x5 pixel box on the screen.

This is useful for determining threshold values for different UI elements.
"""
import numpy
import pyautogui
from PIL import ImageGrab, ImageOps


def get_grey_scale_sum(bbox):
    """Calculate the sum of greyscale intensity values for a bounding box.
    
    Args:
        bbox: Tuple of 4 values defining the (x1, y1, x2, y2) corners of a box
        
    Returns:
        int: Total intensity found within the bounding box
    """
    # Grab an RGB image defined by the bounding box (bbox)
    rgb_image = ImageGrab.grab(bbox)
    
    # Convert the rgb image into a grey-scale image
    # We do this to get the "intensity" values for each pixel in the box we defined
    # Now the color in the box does not matter but the intensity of the collective pixels does.
    gs_image = ImageOps.grayscale(rgb_image)
    
    # Returns a list of (# pixels with value, value)
    pixel_intensity_counts = gs_image.getcolors()
    
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
    
    # Returns the "total intensity" found within the bounding box provided to this function.
    # The individual intensity values are in grey scale going from 0(black) to 255(white)
    return a


def main():
    """Display greyscale intensity values at the mouse cursor position."""
    bound_box_size = 5
    
    print("Move your mouse to different UI elements to see their intensity values.")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            # First get the current mouse position
            cur_pos = pyautogui.position()
            # Form a basic 5x5 box around the current mouse pixel coordinates
            box = (cur_pos.x, cur_pos.y, cur_pos.x + bound_box_size, cur_pos.y + bound_box_size)
            print(f"Intensity: {get_grey_scale_sum(box)}, Position: {cur_pos}")
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()