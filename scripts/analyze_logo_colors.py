"""
Analyze the colors in the Monash logo to understand what we're working with.
"""
from PIL import Image
from collections import Counter

def analyze_colors():
    img = Image.open("monash_logo.png").convert("RGBA")
    pixels = list(img.getdata())
    
    # Sample every 100th pixel to get color distribution
    sampled = pixels[::1000]
    
    # Count unique colors
    color_counts = Counter(sampled)
    
    print("Top 20 colors in the image:")
    print("-" * 60)
    for (r, g, b, a), count in color_counts.most_common(20):
        print(f"RGB({r:3d}, {g:3d}, {b:3d}, {a:3d}) - #{r:02X}{g:02X}{b:02X}")
    
    # Also check specific regions
    width, height = img.size
    pixel_data = img.load()
    
    print("\n" + "=" * 60)
    print("Sampling specific regions:")
    print("=" * 60)
    
    # Top-left corner (likely background)
    print(f"\nTop-left corner (10,10): {pixel_data[10, 10]}")
    print(f"Top-left corner (100,100): {pixel_data[100, 100]}")
    
    # Center area (likely has text and crest)
    center_x, center_y = width // 2, height // 2
    print(f"\nCenter ({center_x},{center_y}): {pixel_data[center_x, center_y]}")
    
    # Text area (right side, middle height)
    text_x, text_y = int(width * 0.6), int(height * 0.45)
    print(f"Text area ({text_x},{text_y}): {pixel_data[text_x, text_y]}")
    
    # Check a range of pixels in the background area
    print("\n" + "=" * 60)
    print("Background color samples (top-left region):")
    bg_colors = []
    for y in range(50, 200, 50):
        for x in range(50, 200, 50):
            color = pixel_data[x, y]
            bg_colors.append(color)
            print(f"  ({x:4d}, {y:4d}): RGB{color}")
    
    print("\n" + "=" * 60)
    print("Text color samples (right side, 'MONASH' area):")
    for y in range(int(height * 0.4), int(height * 0.5), 50):
        for x in range(int(width * 0.55), int(width * 0.75), 100):
            color = pixel_data[x, y]
            if color[3] > 128:  # Only non-transparent
                print(f"  ({x:4d}, {y:4d}): RGB{color}")

if __name__ == "__main__":
    analyze_colors()
