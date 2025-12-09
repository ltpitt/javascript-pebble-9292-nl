#!/usr/bin/env python3
"""
Bus Icon Generator for Pebble NextRide App
Creates pixel-art style bus icons for different Pebble platforms

Usage:
    python3 generate_bus_icon.py
    
Generates:
    - bus_25x25_bw.png    (Menu icon - B&W)
    - bus_28x28_rgba.png  (Original style - Color with transparency)
    - bus_25x25_color.png (Menu icon - Color version)
"""

from PIL import Image, ImageDraw

def create_bus_icon_28x28():
    """Create 28x28 bus icon with transparency (original style)"""
    # Create image with transparency
    img = Image.new('RGBA', (28, 28), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bus body (blue-gray color)
    bus_color = (70, 130, 180, 255)  # Steel blue
    window_color = (200, 220, 255, 255)  # Light blue
    wheel_color = (40, 40, 40, 255)  # Dark gray
    
    # Main bus body
    draw.rectangle([4, 6, 23, 22], fill=bus_color)
    
    # Windows (2x2 grid)
    draw.rectangle([7, 9, 11, 13], fill=window_color)
    draw.rectangle([16, 9, 20, 13], fill=window_color)
    
    # Front windshield
    draw.rectangle([7, 15, 20, 18], fill=window_color)
    
    # Wheels
    draw.ellipse([5, 20, 10, 25], fill=wheel_color)
    draw.ellipse([17, 20, 22, 25], fill=wheel_color)
    
    # Headlights
    draw.ellipse([6, 19, 8, 21], fill=(255, 255, 0, 255))  # Yellow
    draw.ellipse([19, 19, 21, 21], fill=(255, 255, 0, 255))
    
    # Roof detail
    draw.line([4, 6, 23, 6], fill=(100, 100, 100, 255), width=1)
    
    return img

def create_bus_icon_25x25_bw():
    """Create 25x25 B&W menu icon (optimized for Pebble Aplite)"""
    img = Image.new('1', (25, 25), 1)  # 1-bit B&W, white background
    draw = ImageDraw.Draw(img)
    
    # Main bus body
    draw.rectangle([3, 5, 21, 20], fill=0, outline=0)
    
    # Windows (white)
    draw.rectangle([6, 8, 9, 11], fill=1)
    draw.rectangle([15, 8, 18, 11], fill=1)
    
    # Windshield
    draw.rectangle([6, 13, 18, 16], fill=1)
    
    # Wheels
    draw.ellipse([4, 18, 8, 22], fill=0, outline=0)
    draw.ellipse([16, 18, 20, 22], fill=0, outline=0)
    
    # Wheel centers (white)
    draw.ellipse([5, 19, 7, 21], fill=1)
    draw.ellipse([17, 19, 19, 21], fill=1)
    
    return img

def create_bus_icon_25x25_color():
    """Create 25x25 color menu icon (Pebble 64-color palette)"""
    # Using Pebble-safe colors (from 64-color palette)
    img = Image.new('RGB', (25, 25), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Pebble 64-color safe palette
    bus_color = (85, 85, 255)      # Blue
    window_color = (170, 170, 255)  # Light blue
    wheel_color = (0, 0, 0)         # Black
    yellow = (255, 255, 0)          # Yellow
    
    # Main bus body
    draw.rectangle([3, 5, 21, 20], fill=bus_color)
    
    # Windows
    draw.rectangle([6, 8, 9, 11], fill=window_color)
    draw.rectangle([15, 8, 18, 11], fill=window_color)
    
    # Windshield
    draw.rectangle([6, 13, 18, 16], fill=window_color)
    
    # Wheels
    draw.ellipse([4, 18, 8, 22], fill=wheel_color)
    draw.ellipse([16, 18, 20, 22], fill=wheel_color)
    
    # Headlights
    draw.rectangle([5, 17, 6, 18], fill=yellow)
    draw.rectangle([18, 17, 19, 18], fill=yellow)
    
    return img

def main():
    print("🚌 Generating bus icons for Pebble...")
    
    # Generate 28x28 RGBA (original style)
    print("  Creating bus_28x28_rgba.png (28×28 color with transparency)...")
    bus_28 = create_bus_icon_28x28()
    bus_28.save('bus_28x28_rgba.png', 'PNG')
    
    # Generate 25x25 B&W (menu icon for Aplite)
    print("  Creating bus_25x25_bw.png (25×25 B&W for Aplite)...")
    bus_25_bw = create_bus_icon_25x25_bw()
    bus_25_bw.save('bus_25x25_bw.png', 'PNG')
    
    # Generate 25x25 color (menu icon for color Pebbles)
    print("  Creating bus_25x25_color.png (25×25 color for Basalt/Chalk)...")
    bus_25_color = create_bus_icon_25x25_color()
    bus_25_color.save('bus_25x25_color.png', 'PNG')
    
    print("\n✅ Icons generated successfully!")
    print("\nFiles created:")
    print("  • bus_28x28_rgba.png    - 28×28 with transparency")
    print("  • bus_25x25_bw.png      - 25×25 B&W (for Aplite)")
    print("  • bus_25x25_color.png   - 25×25 color (for Basalt/Chalk)")
    print("\nTo use as menu icon, add to appinfo.json:")
    print('  "menuIcon": true')

if __name__ == '__main__':
    main()
