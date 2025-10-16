"""
Utilities for working with the MTGA window in windowed mode.

Provides functions to get window size and position.
"""
import win32gui


def get_window_rez(corner_coordinates):
    """Determine the resolution of the window for scaling later.
    
    Args:
        corner_coordinates: Tuple of (x1, y1, x2, y2) window coordinates
        
    Returns:
        tuple: (width, height) rounded to nearest 100 pixels
    """
    x_rez = int((corner_coordinates[2] - corner_coordinates[0]) / 100) * 100
    y_rez = int((corner_coordinates[3] - corner_coordinates[1]) / 100) * 100
    return (x_rez, y_rez)


def get_mtga_window_corners():
    """Get the MTGA window corners.
    
    This method assumes the MTGA window is open and somewhere on-screen.
    If the window is minimized, the values returned will be incorrect.
    
    Returns:
        tuple: Window coordinates (x1, y1, x2, y2) or None if window not found or invalid
    """
    try:
        window_handle = win32gui.FindWindow(None, "MTGA")
        
        if not window_handle:
            print("Error: MTGA window not found")
            return None
        
        window_coordinates = win32gui.GetWindowRect(window_handle)
        print(f"Window coordinates: {window_coordinates}")
        
        # Check if any coordinate is suspiciously negative (window might be minimized)
        for pixel_coordinate in window_coordinates:
            if pixel_coordinate < -200:
                print("Error: Pixel coordinate is negative! Is your MTGA window minimized?")
                return None
        
        return window_coordinates
    
    except Exception as e:
        print(f"Error getting MTGA window corners: {e}")
        return None


def main():
    """Display MTGA window information."""
    print("Getting MTGA window information...")
    coords = get_mtga_window_corners()
    
    if coords:
        rez = get_window_rez(coords)
        print(f"Window resolution: {rez[0]}x{rez[1]}")
    else:
        print("Failed to get window information")


if __name__ == "__main__":
    main()
    