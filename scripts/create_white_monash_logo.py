"""
Process the Monash logo:
1. Crop out the white border
2. Make blue background transparent
3. Keep white logo elements (crest and text)
"""
from PIL import Image
import json
import base64
from io import BytesIO

def process_logo():
    # Open original logo
    img = Image.open("monash_logo.png").convert("RGBA")
    width, height = img.size
    
    print(f"[OK] Original logo: {width}x{height} pixels")
    
    # Find the bounding box of non-white content
    pixels = img.load()
    
    # Scan from top to find where white border ends
    top_edge = 0
    for y in range(height):
        has_non_white = False
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # Check if not white and not transparent
            if a > 0 and not (r > 240 and g > 240 and b > 240):
                has_non_white = True
                break
        if has_non_white:
            top_edge = y
            break
    
    # Scan from bottom to find where white border starts
    bottom_edge = height - 1
    for y in range(height - 1, -1, -1):
        has_non_white = False
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 0 and not (r > 240 and g > 240 and b > 240):
                has_non_white = True
                break
        if has_non_white:
            bottom_edge = y
            break
    
    # Scan from left
    left_edge = 0
    for x in range(width):
        has_non_white = False
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0 and not (r > 240 and g > 240 and b > 240):
                has_non_white = True
                break
        if has_non_white:
            left_edge = x
            break
    
    # Scan from right
    right_edge = width - 1
    for x in range(width - 1, -1, -1):
        has_non_white = False
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0 and not (r > 240 and g > 240 and b > 240):
                has_non_white = True
                break
        if has_non_white:
            right_edge = x
            break
    
    print(f"   White border detected:")
    print(f"   Top: {top_edge}px, Bottom: {height - 1 - bottom_edge}px")
    print(f"   Left: {left_edge}px, Right: {width - 1 - right_edge}px")
    
    # Crop to remove white border
    cropped = img.crop((left_edge, top_edge, right_edge + 1, bottom_edge + 1))
    print(f"   Cropped size: {cropped.width}x{cropped.height}")
    
    # Now process the cropped image
    pixels = cropped.load()
    BG_BLUE = (0, 108, 172)
    TOLERANCE = 15
    
    def is_background(r, g, b):
        return (abs(r - BG_BLUE[0]) <= TOLERANCE and 
                abs(g - BG_BLUE[1]) <= TOLERANCE and 
                abs(b - BG_BLUE[2]) <= TOLERANCE)
    
    bg_count = 0
    for y in range(cropped.height):
        for x in range(cropped.width):
            r, g, b, a = pixels[x, y]
            if is_background(r, g, b):
                pixels[x, y] = (r, g, b, 0)
                bg_count += 1
    
    print(f"   Blue background pixels made transparent: {bg_count}")
    
    # Save processed PNG
    cropped.save("monash_logo_white.png")
    print("[OK] Saved monash_logo_white.png")
    
    # Convert to base64 data URI
    buffer = BytesIO()
    cropped.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    data_uri = f"data:image/png;base64,{img_base64}"
    
    # Save to JSON
    with open("monash_logo_white.json", "w", encoding="utf-8") as f:
        json.dump({"logo": data_uri}, f)
    
    print("[OK] Saved monash_logo_white.json")
    print(f"   Data URI length: {len(data_uri)} chars")

if __name__ == "__main__":
    process_logo()
