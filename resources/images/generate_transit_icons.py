#!/usr/bin/env python3
"""
Transit Icon Generator - Inspired by Emoji & Material Design
Creates multiple transit-themed icons for Pebble NextRide app

Designs inspired by:
- 🚌 Bus emoji (Unicode)
- 🚃 Railway car emoji
- 🚏 Bus stop emoji
- Material Design transit icons
- Google Maps transit icons

Usage: python3 generate_transit_icons.py
"""

from PIL import Image, ImageDraw

def create_bus_front_view_25x25():
    """Bus front view - inspired by emoji 🚌"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Outer body (rounded rectangle)
    draw.rectangle([5, 3, 19, 21], fill=0)
    draw.rectangle([4, 5, 20, 19], fill=0)
    
    # Large windshield (curved top)
    draw.rectangle([7, 6, 17, 13], fill=1)
    draw.rectangle([6, 8, 18, 12], fill=1)
    
    # Front bumper area
    draw.rectangle([7, 14, 17, 16], fill=1)
    
    # Wheels (bottom)
    draw.ellipse([6, 18, 10, 22], fill=0)
    draw.ellipse([14, 18, 18, 22], fill=0)
    
    # Headlights (small rectangles)
    draw.rectangle([7, 17, 8, 18], fill=1)
    draw.rectangle([16, 17, 17, 18], fill=1)
    
    return img

def create_tram_side_view_25x25():
    """Tram/train side view - inspired by 🚃"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Main body
    draw.rectangle([2, 6, 22, 18], fill=0)
    
    # Three windows
    draw.rectangle([4, 9, 7, 14], fill=1)
    draw.rectangle([10, 9, 14, 14], fill=1)
    draw.rectangle([17, 9, 20, 14], fill=1)
    
    # Wheels
    draw.ellipse([4, 16, 8, 20], fill=0)
    draw.ellipse([16, 16, 20, 20], fill=0)
    
    # Wheel centers
    draw.ellipse([5, 17, 7, 19], fill=1)
    draw.ellipse([17, 17, 19, 19], fill=1)
    
    # Roof line
    draw.line([2, 6, 22, 6], fill=0, width=2)
    
    return img

def create_bus_stop_25x25():
    """Bus stop sign - inspired by 🚏"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Pole
    draw.rectangle([11, 8, 13, 23], fill=0)
    
    # Sign board (rounded)
    draw.rectangle([5, 4, 19, 12], fill=0)
    draw.ellipse([3, 4, 7, 12], fill=0)
    draw.ellipse([17, 4, 21, 12], fill=0)
    
    # Bus symbol on sign (simplified)
    draw.rectangle([8, 6, 16, 10], fill=1)
    draw.rectangle([9, 7, 10, 9], fill=0)
    draw.rectangle([14, 7, 15, 9], fill=0)
    
    return img

def create_location_pin_transit_25x25():
    """Location pin with transit symbol"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Pin shape
    draw.ellipse([7, 3, 17, 13], fill=0)
    draw.polygon([(12, 21), (8, 14), (16, 14)], fill=0)
    
    # Pin center (white)
    draw.ellipse([9, 5, 15, 11], fill=1)
    
    # Small bus icon in center
    draw.rectangle([10, 7, 14, 10], fill=0)
    draw.rectangle([11, 8, 11, 9], fill=1)
    draw.rectangle([13, 8, 13, 9], fill=1)
    
    return img

def create_departure_board_25x25():
    """Digital departure board style"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Board frame
    draw.rectangle([3, 4, 21, 20], fill=0)
    draw.rectangle([4, 5, 20, 19], fill=1)
    
    # Display lines (like LED display)
    for y in [7, 10, 13, 16]:
        draw.rectangle([6, y, 18, y+1], fill=0)
    
    # Border details
    draw.rectangle([3, 4, 21, 5], fill=0)
    draw.rectangle([3, 19, 21, 20], fill=0)
    
    return img

def create_route_line_25x25():
    """Route/line path icon"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Curved route line
    draw.ellipse([8, 3, 14, 9], fill=0, outline=0)
    draw.ellipse([9, 4, 13, 8], fill=1, outline=1)
    
    draw.rectangle([10, 7, 12, 17], fill=0)
    
    draw.ellipse([8, 15, 14, 21], fill=0, outline=0)
    draw.ellipse([9, 16, 13, 20], fill=1, outline=1)
    
    # Connecting dots
    draw.ellipse([9, 5, 13, 7], fill=0)
    draw.ellipse([9, 17, 13, 19], fill=0)
    
    return img

def create_clock_transit_25x25():
    """Clock with bus/tram - real-time concept"""
    img = Image.new('1', (25, 25), 1)
    draw = ImageDraw.Draw(img)
    
    # Clock circle
    draw.ellipse([2, 2, 22, 22], fill=0)
    draw.ellipse([4, 4, 20, 20], fill=1)
    
    # Clock hands (showing ~3:00)
    draw.line([12, 12, 12, 8], fill=0, width=2)  # Hour
    draw.line([12, 12, 16, 12], fill=0, width=2)  # Minute
    
    # Center dot
    draw.ellipse([11, 11, 13, 13], fill=0)
    
    return img

def main():
    print("🚌 🚃 🚏 Generating transit-themed icons...\n")
    
    icons = [
        ("bus_front_25x25.png", create_bus_front_view_25x25, "Bus front view (emoji style)"),
        ("tram_side_25x25.png", create_tram_side_view_25x25, "Tram/train side view"),
        ("bus_stop_25x25.png", create_bus_stop_25x25, "Bus stop sign"),
        ("location_transit_25x25.png", create_location_pin_transit_25x25, "Location pin with transit"),
        ("departure_board_25x25.png", create_departure_board_25x25, "Departure board"),
        ("route_line_25x25.png", create_route_line_25x25, "Route line/path"),
        ("clock_transit_25x25.png", create_clock_transit_25x25, "Clock (real-time)"),
    ]
    
    for filename, create_func, description in icons:
        print(f"  Creating {filename:30} - {description}")
        img = create_func()
        img.save(filename, 'PNG')
    
    print("\n✅ All icons generated!")
    print("\nPreview them all and pick your favorite for the menu icon!")
    print("\nRecommendations:")
    print("  • bus_front_25x25.png     - Classic, instantly recognizable")
    print("  • bus_stop_25x25.png      - Represents transit stops well")
    print("  • departure_board_25x25.png - Represents schedules/departures")
    print("  • location_transit_25x25.png - Represents finding nearby transit")

if __name__ == '__main__':
    main()
