from PIL import ImageGrab, Image, ImageOps, ImageFilter
import pytesseract
import re 

######
# WIP adding text recognition to improve the bot
#####

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\clansman\AppData\Local\Tesseract-OCR\tesseract.exe'

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
    # img = ImageGrab.grab((1650,980,1830,1020)) # Finds 'play' in lower right corner
    # img = ImageGrab.grab((80,75,140,95))       # Finds 'Home' in the upper left
    # img = ImageGrab.grab((1070,855,1186,984))  # Finds 'Keep 7' pre-match
    # img = ImageGrab.grab((714,854,881,893))    # Finds 'Mulligan' pre match
    # img = ImageGrab.grab((1694,928,1864,961))  # finds 'no blocks' in match
    img = ImageGrab.grab((1695,928,1850,960))  # Finds 'all attack'
    # img = ImageGrab.grab((1667,865,1883,900))  # Finds 'no attacks' or 'Cancel attacks'
    # img = ImageGrab.grab((1765,739,1812,756))  # Finds 'undo'
    # img = ImageGrab.grab((906,856,1020,893))   # Finds 'caneel' or 'cancel' when there is a card with two options DO NOT USE THIS
    # img = ImageGrab.grab((1562,203,1746,237))  # Finds "last Played" on screen
    # img = ImageGrab.grab((1635,480,1763,504))  # Finds "standard play" 
    # img = ImageGrab.grab((1635,536,1763,564))  # Finds "alchemy play" 
    # img = ImageGrab.grab((1635,592,1763,624))  # Finds "historic play" 
    # img = ImageGrab.grab((1635,648,1763,684))  # Finds "explorer play" 
    # img = ImageGrab.grab((1635,704,1763,744))  # Finds "bot match"
    # img = ImageGrab.grab((62,133,216,182))     # Finds "brawl"
    # img = ImageGrab.grab((90,1000,260,1040))   # Finds user name in match
    # img = ImageGrab.grab((1590,100,1800,140))  # Finds 'view battlefield' during prematch card selection
    # img = ImageGrab.grab((1698,925,1843,969))  # Finds "auto pay" in game
    # img = ImageGrab.grab((1740,934,1810,960))  # Finds "next" in game
    # img = ImageGrab.grab((1705,930,1845,966))  # Finds "end turn" in game
    # img = ImageGrab.grab((1684,931,1861,967))  # Finds "opponent's turn" in game
    # img = ImageGrab.grab((1740,930,1808,962))  # Finds "pass" on opponents turn
    # img = ImageGrab.grab((1700,929,1849,963))  # Finds "no blocks" in game
    # img = ImageGrab.grab((1710,929,1837,965))  # Finds "my turn" in game
    img = ImageGrab.grab((1730,979,1818,996))  # Finds "to combat" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996))  # Finds "to end" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996))  # Finds "to blockers" in game under next button
    # img = ImageGrab.grab((1725,977,1820,996))  # Finds "to attackers" in game under next button
    # img = ImageGrab.grab((1716,932,1835,965))  # Finds "resolve" in game
    # img = ImageGrab.grab((802,87,1119,143))    # Finds "choose one" in game center of screen
    # img = ImageGrab.grab((856,1023,1067,1056)) # Finds "Click to Continue" after a match has ended
    # img = ImageGrab.grab((778,492,1141,603))   # Finds "defeat" on results screen
    # img = ImageGrab.grab((758,84,1161,143))    # Finds 'order blockers' (not 100%)
    # img = ImageGrab.grab((913,855,1010,892))   # Finds 'done' on order blockers screen
    # img = ImageGrab.grab((543,723,634,768))    # Finds 'first' on order blockers screen
    # img = ImageGrab.grab((704,491,1212,620))   # Finds 'order blockers' (not 100%)
    # img = ImageGrab.grab((1722,929,1854,964))  # Finds 'all atta' or '# attacker' or 'cancel' (not 100%)
    # img = ImageGrab.grab((855,1022,1062,1055))   # Finds 'click to continue' at match end
    

    # for key, button in button_dict.items():
    # img = ImageGrab.grab(button)
    img = ImageOps.grayscale(img)   
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.EDGE_ENHANCE)
    img = img.convert('L')    
    # Threshold
    FAINT_THRESHOLD =   75  # Used to detect faint text on the screen
    BRIGHT_THRESHOLD = 238  # Used to detect bright text on the screen
    BLOCK_THRESHOLD =  200  # Used on the order blocker screen as the text is slightly greyed out
    
    width, height = img.size
    # Invert pixels since text is white on the screen
    for x in range(width):
        for y in range(height):
            #if intensity less than threshold, assign black
            if img.getpixel((x,y)) < FAINT_THRESHOLD: #Threshold when trying to find text under the button in game
                img.putpixel((x,y),255)

            #if intensity greater than threshold, assign white 
            else:
                img.putpixel((x,y),0)
    img = img.filter(ImageFilter.SMOOTH)
    img = img.filter(ImageFilter.EDGE_ENHANCE)            
    img.save("capture.jpg")
    img = Image.open("capture.jpg")
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
    return re.sub(r'[^A-Za-z0-9 ]+', '', text.lower().strip())


# print(extract_text())
# Iterate up to 100 times to verify the threshold value and the
# pixel locations we set finds the text we expect
count = 0
while(1):
    if (count == 20):
        break
    text = extract_text()
    # if (text.find('combat') == -1):
    if ('combat' not in text):
        print(text)
        break
    count += 1
print(count)