# 9292-nl-pebble

Pebble JavaScript client to access Dutch public transport departure times. 

## ⚠️ Important Update (2025)

The original 9292.nl public API is no longer freely available and now requires a paid subscription. This updated version provides multiple solutions to continue using the app:

## Available Data Sources

### 1. 9292.nl Official API (Recommended)
- **Status**: Requires paid subscription
- **Setup**: Get API key from [9292.nl developers](https://9292.nl/developers)
- **Features**: Full real-time data, most accurate
- **Cost**: Subscription-based pricing

### 2. Demo Mode (Default)
- **Status**: Always available
- **Setup**: No configuration needed
- **Features**: Mock departure data for testing
- **Cost**: Free

### 3. Alternative APIs (Future)
- NS API integration (planned)
- OpenOV integration (planned)

## Configuration

1. Install the app on your Pebble
2. Open the app and select "Settings"
3. Configure your preferred data source:
   - For 9292.nl API: Enter your API key
   - For demo mode: No setup required

## Usage

The app provides departure times for two pre-configured routes:
- **Home**: Aalsmeer Dorpsstraat → Haarlem Station  
- **Work**: Haarlem Raaksbrug → Uithoorn Busstation

Routes can be customized through the configuration interface.

## Technical Details

- Built with Pebble.js SDK v3
- Supports location services
- Automatic fallback to demo mode on API failures
- Robust error handling and user feedback

## Migration from Original Version

If you were using the original version:
1. The app will automatically use demo mode if no API key is configured
2. To get real data, obtain a 9292.nl API subscription
3. Configure your API key in the settings

## Contributing

Pull requests welcome for additional API integrations and improvements.
