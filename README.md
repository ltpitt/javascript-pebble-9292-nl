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

#### How to Run in Demo Mode

Demo mode is the default mode when no API key is configured. It provides mock departure data for testing and development purposes without requiring any external API access.

**Quick Start:**
1. Install the app on your Pebble smartwatch
2. Launch the app - it will automatically use demo mode
3. Select either "Home" or "Work" destination
4. The app will display mock departure times with simulated delays

**Mock Data Provided:**
- Departure times: 14:25 and 14:40
- Sample delay information: "+2 min delay" and "On time"
- Route numbers and destination names
- Realistic timing simulation (1-second loading delay)

**Demo Mode Features:**
- No network connectivity required
- Instant fallback if API services fail
- Consistent mock data for testing UI and functionality
- Automatic vibration feedback on data display
- Error handling demonstration

### 3. Alternative APIs (Future)
- NS API integration (planned)
- OpenOV integration (planned)

## Configuration

1. Install the app on your Pebble
2. Open the app and select "Settings"
3. Configure your preferred data source:
   - For 9292.nl API: Enter your API key
   - For demo mode: No setup required

## Testing with Demo Mode

### Running the Application in Demo Mode

The application includes a comprehensive demo mode that allows you to test all functionality without requiring API access or network connectivity.

#### Step-by-Step Demo Mode Testing:

1. **Launch the App**: Open the 9292-nl app on your Pebble
2. **Main Menu**: You'll see three options:
   - Home (Aalsmeer Dorpsstraat → Haarlem Station)
   - Work (Haarlem Raaksbrug → Uithoorn Busstation)  
   - Settings
3. **Select a Route**: Choose either "Home" or "Work"
4. **View Mock Data**: The app will display:
   - Loading indicator with "Fetching data from Demo Mode (Mock Data)"
   - Mock departure time (e.g., "14:25")
   - Destination information
   - Realistic delay information (e.g., "+2 min delay" or "On time")
   - Route numbers when available

#### Expected Demo Mode Behavior:

- **Loading Time**: 1-second simulated delay for realistic experience
- **Vibration Feedback**: Short vibration when data is displayed
- **Multiple Departures**: Demo mode provides 2 sample departures per route
- **Error Recovery**: If other APIs fail, the app automatically falls back to demo mode
- **No Configuration Required**: Demo mode works immediately without setup

#### Demo Mode Data Structure:

```
Mock Departure Example:
- Time: 14:25
- Destination: Haarlem Station (or Uithoorn Busstation)  
- Status: +2 min delay (or "On time")
- Route: 300
```

### Verifying Demo Mode is Active:

You can confirm demo mode is running by:
1. Checking the loading message: "Fetching data from Demo Mode (Mock Data)"
2. Observing consistent mock times (14:25, 14:40)
3. No requirement for internet connectivity
4. Immediate availability without API key configuration

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

## Development & Testing

### Demo Mode Development

Demo mode is particularly useful for development and testing scenarios:

#### Development Benefits:
- **Offline Development**: Test app functionality without internet access
- **Consistent Data**: Predictable responses for UI testing
- **Error Simulation**: Test error handling and fallback mechanisms  
- **Performance Testing**: Measure app responsiveness without API latency
- **UI Validation**: Verify display formatting with known data sets

#### Customizing Demo Mode:

To modify the mock data for testing different scenarios, edit the `fetchMockData` function in `src/app.js`:

```javascript
// Located around line 157-177 in src/app.js
fetchMockData: function(routeConfig) {
    setTimeout(function() {
        var mockDepartures = [
            {
                time: '14:25',                    // Customize departure time
                destinationName: routeConfig.destinationName,
                realtimeText: '+2 min delay',     // Customize delay status
                route: '300'                      // Customize route number
            },
            // Add more mock departures here
        ];
        trip.displayDeparture(mockDepartures[0]);
    }, 1000); // Adjust loading delay here
}
```

#### Demo Mode Troubleshooting:

**Issue**: Demo mode not activating
- **Solution**: Ensure no API key is configured in settings
- **Check**: The app should automatically fall back to demo mode

**Issue**: No data displayed in demo mode  
- **Solution**: Check console logs for JavaScript errors
- **Verify**: Mock data structure matches expected format

**Issue**: App crashes in demo mode
- **Solution**: Validate app.js syntax with `node -c src/app.js`
- **Check**: Ensure all required Pebble.js modules are available

### Running the App
For development and testing, you can use [rebble-docker](https://github.com/pebble-dev/rebble-docker) to run the Pebble app in an emulated environment:

```bash
# Clone and set up rebble-docker
git clone https://github.com/pebble-dev/rebble-docker.git
cd rebble-docker
docker-compose up -d

# Access the Pebble simulator at http://localhost:9000
```

This provides a complete Pebble development environment including:
- Pebble SDK and tools
- CloudPebble IDE interface
- Device simulator for testing

### Building the App
The app is built using Pebble.js SDK v3. You can import the project into CloudPebble or use the command-line tools provided by rebble-docker.

## Contributing

Pull requests welcome for additional API integrations and improvements.
