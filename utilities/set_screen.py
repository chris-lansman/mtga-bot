import win32gui

# First find the 'MTGA' window, if the name in the upper left corner of the game window
# when in windowed mode every changes you will need to update this screen
window_handle = win32gui.FindWindow(None, "MTGA")
# Move the window to a known offset (0,0) for the upper left corner, 
# and force a resize so this works on every system every time
win32gui.SetWindowPos(window_handle,None,0,0,1920,1080,0)
# Verify the coordinates are at (0,0,1920,1080)
window_coordinates = win32gui.GetWindowRect(window_handle)