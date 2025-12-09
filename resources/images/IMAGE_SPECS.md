# Pebble Image Specifications - Current Resources

## Summary
All images are optimized for Pebble smartwatch displays (low memory, monochrome/basic color).

## Detailed Specifications

### 1. bus.png (EXTRA - restored from history)
- **Dimensions**: 28×28 pixels
- **Color Depth**: 8-bit/color RGBA (32-bit total)
- **Format**: PNG, non-interlaced
- **File Size**: 746 bytes
- **Usage**: Could be used for line/route icons
- **Notes**: Has transparency (RGBA), more complex than needed for Pebble

### 2. logo_splash.png
- **Dimensions**: 120×120 pixels
- **Color Depth**: 1-bit grayscale (black & white only)
- **Format**: PNG, non-interlaced
- **File Size**: 15 KB
- **Usage**: App logo shown on launch
- **Notes**: Perfect for Pebble - monochrome, large enough for splash

### 3. menu_icon.png
- **Dimensions**: 25×25 pixels
- **Color Depth**: 1-bit colormap (2 colors: black & white)
- **Format**: PNG, non-interlaced
- **File Size**: 160 bytes (tiny!)
- **Usage**: Menu icon in Pebble system menu
- **Notes**: Highly optimized - perfect size for menu

### 4. tile_splash.png
- **Dimensions**: 32×32 pixels
- **Color Depth**: 1-bit grayscale (black & white only)
- **Format**: PNG, non-interlaced
- **File Size**: 15 KB
- **Usage**: Timeline tile splash screen
- **Notes**: Standard Pebble tile size

## Pebble Image Requirements

### Color Depth Guidelines
- **Aplite (B&W)**: 1-bit (2 colors)
- **Basalt/Chalk/Diorite (Color)**: 8-bit (64 colors - 6-bit color + 2-bit transparency)
- **Emery (Color HR)**: 8-bit (64 colors)

### Recommended Sizes
- **App Icons**: 25×25 or 28×28 pixels
- **Menu Icons**: 25×25 pixels (shown in system menu)
- **Splash Screens**: 120×120 to 144×168 pixels (varies by platform)
- **Timeline Pins**: 32×32 or 64×64 pixels
- **Watchface Elements**: Varies (can be larger)

### Best Practices
1. **Use 1-bit for B&W**: Saves memory, perfect for Aplite
2. **Keep file sizes small**: Watch memory is limited
3. **PNG format**: Standard for Pebble
4. **Avoid gradients**: Use solid colors or dithering
5. **Test on actual device**: Emulator may show differently

## How to Replicate These Images

### Tools Needed
- **ImageMagick** (command line): `brew install imagemagick`
- **GIMP** (GUI): Free, supports indexed/1-bit color
- **Photoshop**: Export as PNG-8 or PNG-1
- **Online**: Use pebble-dev tools or online converters

### Creating Similar Images

#### For 1-bit Black & White (logo_splash.png, tile_splash.png)
```bash
# Convert any image to 1-bit B&W
convert input.png -colorspace Gray -depth 1 -colors 2 output.png

# Resize and convert
convert input.png -resize 120x120 -colorspace Gray -depth 1 -colors 2 logo_splash.png
```

#### For Menu Icons (25×25, 1-bit)
```bash
convert icon.png -resize 25x25 -colorspace Gray -depth 1 -colors 2 menu_icon.png
```

#### For Timeline Tiles (32×32, 1-bit)
```bash
convert icon.png -resize 32x32 -colorspace Gray -depth 1 -colors 2 tile_splash.png
```

#### Optimize File Size
```bash
# Use pngcrush or optipng
optipng -o7 image.png
# or
pngcrush -rem alla -reduce image.png output.png
```

## Current Image Status
✅ **logo_splash.png** - Perfect for Pebble splash screen
✅ **menu_icon.png** - Perfect for system menu (ultra-optimized!)
✅ **tile_splash.png** - Perfect for timeline tiles
⚠️ **bus.png** - Too complex (RGBA), can be simplified to 1-bit if needed

## Recommendations
1. Keep current images - they're perfectly optimized
2. If adding new icons, follow the 1-bit grayscale pattern
3. Use 25×25 or 28×28 for icons, 120×120 for splash
4. Test on both color and B&W Pebble platforms