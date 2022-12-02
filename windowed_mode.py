import win32gui # Provies access to windows on windows

def get_window_rez(corner_coordinates):
    # Determines the resolution of the window for scaling later
    
    x_rez = int((corner_coordinates[2]-corner_coordinates[0]) / 100)*100
    y_rez = int((corner_coordinates[3]-corner_coordinates[1]) / 100)*100
    return(x_rez, y_rez)
    
# TODO - WIP, use this to find the window anywhere on the screen and then shift the offsets to always find the buttons/cards/etc    
def get_mtga_window_corners():
    # This method assumes the MTGA window is open and somewhere on-screen. If the window is minimized the values 
    # returned will be incorrect and the application will yell at you
    window_handle = win32gui.FindWindow(None, "MTGA")
    window_coordinates = win32gui.GetWindowRect(window_handle)
    print(window_coordinates)
    for pixel_coordinates in window_coordinates:
        if pixel_coordinates < -200:
            print("Error, pixel coordinate negative!~! Is your MTGA window minimized?!?")
            return IndexError
    