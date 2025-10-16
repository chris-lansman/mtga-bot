"""
Utility to set the MTGA window to a specific size and position.

This ensures consistent screen coordinates for all bot operations.
"""
import win32gui


def set_mtga_window(x=0, y=0, width=1920, height=1080):
    """Set the MTGA window to a specific size and position.
    
    Args:
        x: X position of window (default: 0)
        y: Y position of window (default: 0)
        width: Window width (default: 1920)
        height: Window height (default: 1080)
        
    Returns:
        tuple: Window coordinates (x1, y1, x2, y2) or None if window not found
    """
    try:
        # First find the 'MTGA' window
        # Note: If the window title changes, you'll need to update this
        window_handle = win32gui.FindWindow(None, "MTGA")
        
        if not window_handle:
            print("Error: MTGA window not found")
            print("Make sure the game is running and in windowed mode")
            return None
        
        # Move the window to a known offset and force a resize
        # so this works on every system every time
        win32gui.SetWindowPos(window_handle, None, x, y, width, height, 0)
        
        # Verify the coordinates
        window_coordinates = win32gui.GetWindowRect(window_handle)
        print(f"MTGA window set to: {window_coordinates}")
        return window_coordinates
    
    except Exception as e:
        print(f"Error setting MTGA window: {e}")
        return None


def main():
    """Set the MTGA window to default position and size."""
    print("Setting MTGA window to 0,0 at 1920x1080...")
    coords = set_mtga_window()
    if coords:
        print("Success!")
    else:
        print("Failed to set window")


if __name__ == "__main__":
    main()