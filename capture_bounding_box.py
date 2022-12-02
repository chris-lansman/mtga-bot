# This code was modified from the original answer found here on stack-overflow
# https://stackoverflow.com/questions/25848951/python-get-mouse-x-y-position-on-click

# Attempt to import the required libraries else prompt to install them
try:
    import win32api
except ModuleNotFoundError:
    print("win32api not found, to install do pip install pywin32")
try:
    import time
except ModuleNotFoundError:
    print("time not found, to install do pip install time?")
try:
    import pyautogui
except ModuleNotFoundError:
    print("py auto gui not found, to install do pip install pyautogui")
    
# Capture the upper left and lower right coordinate values of the window we want to bound ourselves to
def capture_bounding_box(WhatToGet="First right-click the upper left corner of the MTGA window then right-click the lower right corner", 
                         GetXOnly=False, 
                         GetYOnly=False, 
                         GetColor=False, 
                         Mouse_Key='Right', 
                         OverrideMouse_Key=False):
    
    # Used to store values which will be returned to the calling function
    pixel_box_coordinates = []
    pixel_box_color_values = []
    
    print(WhatToGet)
    # We can override the default mouse click-style. Default is a right-click.
    if OverrideMouse_Key:
        Mouse_Key_To_click = Mouse_Key
    if Mouse_Key == 'Left':
        Mouse_Key_To_click = 0x01
    if Mouse_Key == 'Right':
        Mouse_Key_To_click = 0x02
    if Mouse_Key == 'Wheel':
        Mouse_Key_To_click = 0x04
    # This captures the current state of the mouse key selected above, if not clicked the default value is usually 0,1
    # When a mouse button is clicked the value normally changes to -127 or -128
    def_click_state = win32api.GetKeyState(Mouse_Key_To_click)
    
    # Keep looping until we receive two different mouse clicks
    coordinate_count = 0
    while coordinate_count < 2:
        # Capture the current state of the mouse buttons state
        curr_click_state = win32api.GetKeyState(Mouse_Key_To_click)
        # See if a mouse key state has changed, if it has a click was detected
        if curr_click_state != def_click_state:
            # Update the default to the current so we dont accidentally double bounce the click
            def_click_state = curr_click_state
            
            # Make sure a full click was detected in the state change
            if curr_click_state < 0:
                # Add into our click counter
                coordinate_count += 1
                # Get the current value of the cursor on the screen when the Mouse_Key was pressed
                pixel_box_coordinates.append(win32api.GetCursorPos())
        time.sleep(0.001)

    # Returns the two sets of coordinates for the window corners
    return pixel_box_coordinates

print(capture_bounding_box())