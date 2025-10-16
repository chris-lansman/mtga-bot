"""
Simple utility to display mouse coordinates on the screen.

This is useful for determining coordinate values for UI elements.
Run the program and move the mouse around. Press Ctrl+C to exit.
"""
import pyautogui


def main():
    """Display mouse position continuously."""
    print("Move your mouse around to see coordinates.")
    print("Press Ctrl+C to exit.")
    pyautogui.displayMousePosition()


if __name__ == "__main__":
    main()