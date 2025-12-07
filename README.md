# NextRide

A Pebble smartwatch app for checking real-time bus/tram/metro departures in the Netherlands.

## What It Does

NextRide shows **when the next bus arrives** at your favorite stops. Think of it as a quick departure board on your wrist.

**Use it for:**
- "When's my next bus at home?"
- "Should I run to catch it or wait?"
- "Is my bus delayed?"

**Not a route planner** - it shows departures FROM stops, not routes between locations.

## Features

- 🚌 Real-time departures from ~4,111 stops across Netherlands
- ⭐ Save your favorite stops (home, work, gym, etc.)
- 📍 GPS: Find nearest stop and see departures
- ⚡ Live updates with delays
- 🔍 Search stops by city and name in config page

## Installation

### For Users

Install from the Pebble App Store on your smartphone.

### For Developers

```bash
git clone https://github.com/ltpitt/javascript-pebble-9292-nl.git
cd javascript-pebble-9292-nl
pebble build
pebble install --phone <YOUR_PHONE_IP>
```

## Usage

1. **Configure on phone:**
   - Open Pebble app → NextRide Settings
   - Search for your frequent stops (e.g., "Haarlem Byzantiumstraat")
   - Click results to add them to "My Stops"

2. **Use on watch:**
   - Open NextRide app
   - Select a saved stop OR "📍 Current Location"
   - See next departures instantly

## Data Source

Uses OV API (ovapi.nl) - free, open real-time transit data for Netherlands.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
