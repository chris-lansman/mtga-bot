def scan_screen_for_text(items_to_scan=text_loc_dict):
    
    # items_to_scan - dictionary of the items we want to look for
    
    text_found = []
    # Look over the screen and see if we find anything we know about
    for key, bb_values in items_to_scan.items():
        img = ImageGrab.grab(bb_values)
        img = ImageOps.grayscale(img)   
        img = img.filter(ImageFilter.SMOOTH)
        img = img.filter(ImageFilter.EDGE_ENHANCE)
        img = img.convert('L')    
        # Invert pixels since text is white on the screen
        # This will leave you with black text and a white background 
        # which pytesseract does a better job with
        width, height = img.size
        for x in range(width):
            for y in range(height):
                #if intensity less than threshold, assign black
                if img.getpixel((x,y)) < 235:
                    img.putpixel((x,y),255)
                #if intensity greater than threshold, assign white 
                else:
                    img.putpixel((x,y),0)
        img.save("capture.jpg")
        img = Image.open("capture.jpg")
        text = pytesseract.image_to_string(img, lang='eng', config='--psm 12 --oem 3')
        # Only add text to our text_found list if we match a known text value
        if key in text.lower().strip():
            print(f"{key}: {text.lower().strip()}")
            text_found.append(key)
    return text_found