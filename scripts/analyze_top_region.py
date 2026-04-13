"""
Analyze the top region of the logo to find any lines or borders.
"""
from PIL import Image

def analyze_top_region():
    img = Image.open("monash_logo.png").convert("RGBA")
    pixel_data = img.load()
    width, height = img.size
    
    print("Scanning top 50 pixels row by row...")
    print("=" * 70)
    
    # Scan top 50 pixels
    for y in range(50):
        colors_in_row = {}
        for x in range(0, width, 100):  # Sample every 100 pixels
            color = pixel_data[x, y]
            if color[3] > 0:  # Non-transparent
                key = f"RGB({color[0]:3d}, {color[1]:3d}, {color[2]:3d})"
                colors_in_row[key] = colors_in_row.get(key, 0) + 1
        
        if colors_in_row:
            print(f"Row {y:2d}: {colors_in_row}")
    
    print("\n" + "=" * 70)
    print("Checking for horizontal line at top (scanning full width at y=20)...")
    
    # Check a specific row in detail
    y_check = 20
    unique_colors = {}
    for x in range(width):
        color = pixel_data[x, y_check]
        if color[3] > 0:
            key = f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
            if key not in unique_colors:
                unique_colors[key] = []
            unique_colors[key].append(x)
    
    print(f"\nUnique colors at y={y_check}:")
    for color, positions in sorted(unique_colors.items()):
        print(f"  {color}: {len(positions)} pixels, positions: {positions[:10]}...")

if __name__ == "__main__":
    analyze_top_region()
