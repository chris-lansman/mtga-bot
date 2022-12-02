import pyautogui
from PIL import ImageGrab, Image, ImageOps, ImageFilter
import pytesseract
import cv2
import win32gui

######
# WIP adding text recognition to improve the bot
#####

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\clansman\AppData\Local\Tesseract-OCR\tesseract.exe'

class Text:
    play_button = (1650,980,1830,1020) # Find 'play' in lower right corner
    home_button = (80,75,140,95) # Find 'Home' in the upper left
    keep_button = (1070,855,1186,984) # Finds 'Keep 7' pre-match
    mulligan_button = (714,854,881,893) # Finds 'Mulligan' pre match
    no_blocks_button = (1694,928,1864,961) # finds 'no blocks' in match
    cancel_numAttacker_allAttack_buttons = (1693,925,1865,966) # Finds 'all atta' or '# attacker' or 'cancel' (not 100%)
    no_attacks_cancel_attack_buttons = (1691,865,1861,900) # Finds 'no attacks' or 'ancel attack'
    undo_button = (1765,739,1812,756) # Finds 'undo'
    cancel_button = (906,856,1020,893) # Finds 'caneel' or 'cancel' when there is a card with two options

# Dictionary of bounding box offsets that should resolve to specific text if its on the screen
text_loc_dict = {
    "play":           (1650,980,1830,1020),
    "home":           (80,75,140,95),
    "keep" :          (1070,855,1186,984), 
    "mulligan" :      (714,854,881,893), 
    "no_blocks" :     (1694,928,1864,961),
    "cancel" :        (1693,925,1865,966), 
    "attacker" :      (1693,925,1865,966), 
    "all atta" :      (1693,925,1865,966), 
    "no attacks" :    (1691,865,1861,900), 
    "ancel attack" :  (1691,865,1861,900), 
    "undo_button" :   (1765,739,1812,756), 
    "caneel" :        (906,856,1020,893),
    "cancel" :        (906,856,1020,893),
    "last played" :   (1562,203,1746,237),
    "standard play" : (1635,480,1763,504), # standard  match under table icon match type
    "alchemy play" :  (1635,536,1763,564), # alchemy match under table icon match type
    "historic play" : (1635,592,1763,624), # historic match under table icon match type
    "explorer play" : (1635,648,1763,684), # explorer match under table icon match type
    "bot match" :     (1635,704,1763,744), # Bot match under table icon match type
    "brawl" :         (62,133,216,182),    # Brawl in the upper left corner of screen
    "ranked" :        (1563,205,1681,237), # Ranked under table icon match type
    "brawl" :         (1563,205,1681,237), # Brawl under table icon match type
    }

def extract_text():
    
    # window_handle = win32gui.FindWindow(None, "MTGA")
    # window_coordinates = win32gui.GetWindowRect(window_handle)
    
    # img = ImageGrab.grab(window_coordinates)
    # img = ImageGrab.grab((1650,980,1830,1020)) # Find 'play' in lower right corner
    # img = ImageGrab.grab((80,75,140,95)) # Find 'Home' in the upper left
    # img = ImageGrab.grab((1070,855,1186,984)) # Finds 'Keep 7' pre-match
    # img = ImageGrab.grab((714,854,881,893)) # Finds 'Mulligan' pre match
    # img = ImageGrab.grab((1694,928,1864,961)) # finds 'no blocks' in match
    # img = ImageGrab.grab((1693,925,1865,966)) # Finds 'all atta' or '# attacker' or 'cancel' (not 100%)
    # img = ImageGrab.grab((1667,865,1883,900)) # Finds 'no attacks' or 'Cancel attacks'
    # img = ImageGrab.grab((1765,739,1812,756)) # Finds 'undo'
    # img = ImageGrab.grab((906,856,1020,893)) # Finds 'caneel' or 'cancel' when there is a card with two options
    # img = ImageGrab.grab((1562,203,1746,237)) # Finds "last Played" on screen
    # img = ImageGrab.grab((1635,480,1763,504)) # Finds "standard play" 
    # img = ImageGrab.grab((1635,536,1763,564)) # Finds "alchemy play" 
    # img = ImageGrab.grab((1635,592,1763,624)) # Finds "historic play" 
    # img = ImageGrab.grab((1635,648,1763,684)) # Finds "explorer play" 
    # img = ImageGrab.grab((1635,704,1763,744)) # Finds "bot match"
    # img = ImageGrab.grab((62,133,216,182)) # Finds "brawl"
    # img = ImageGrab.grab((90,1000,260,1040)) # Finds user name in match
    # img = ImageGrab.grab((1590,100,1800,140)) # Finds 'view battlefield' during prematch card selection
    # img = ImageGrab.grab((1698,925,1843,969)) # Finds "auto pay" in game
    # img = ImageGrab.grab((1735,931,1814,968)) # Finds "next" in game
    # img = ImageGrab.grab((1705,930,1845,966)) # Finds "end turn" in game
    # img = ImageGrab.grab((1684,931,1861,967)) # Finds "opponent's turn" in game
    # img = ImageGrab.grab((1740,930,1808,962)) # Finds "pass" on opponents turn
    # img = ImageGrab.grab((1700,929,1849,963)) # Finds "no blocks" in game
    # img = ImageGrab.grab((1710,929,1837,965)) # Finds "my turn" in game
    # img = ImageGrab.grab((1725,977,1820,996)) # Finds "to combat" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996)) # Finds "to end" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996)) # Finds "to blockers" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996)) # Finds "to attackers" in game under next button
    # img = ImageGrab.grab((1716,932,1835,965)) # Finds "resolve" in game
    img = ImageGrab.grab((802,87,1119,143)) # Finds "cancel" in game center of screen
    
    
    # for key, button in button_dict.items():
    # img = ImageGrab.grab(button)
    img = ImageOps.grayscale(img)   
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    img = img.convert('L')    
    # Threshold
    faint_text_threshold = 75
    bright_text_threshold = 235
    width, height = img.size
    # Invert pixels since text is white on the screen
    for x in range(width):
        for y in range(height):
            #if intensity less than threshold, assign black
            if img.getpixel((x,y)) < bright_text_threshold: #Threshold when trying to find text under the button in game
                img.putpixel((x,y),255)

            #if intensity greater than threshold, assign white 
            else:
                img.putpixel((x,y),0)
                
    img.save("capture.jpg")
    img = Image.open("capture.jpg")
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
    print(text)
    # if text.lower().strip() == key:
    #     print(f"{key}: {text.lower().strip()}")


extract_text()