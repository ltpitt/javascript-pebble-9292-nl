# Backend API Integration

The NextRide Pebble app now supports an optional custom backend API for schedule data.

## Setup

1. **Start the backend server:**
   ```bash
   cd backend
   source venv/bin/activate
   python3 app.py
   ```
   The backend will run on `http://0.0.0.0:8000`

2. **Find your local IP address:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Example: `192.168.178.80`

3. **Configure in Pebble app:**
   - Open the NextRide app on your Pebble
   - Go to Settings (long press SELECT or tap gear icon)
   - Expand "⚙️ Advanced Settings"
   - Enter: `http://192.168.178.80:8000`
   - Save settings

## How It Works

- **Primary source**: OV API (ovapi.nl) for real-time departures
- **Fallback**: Your custom backend API for scheduled GTFS data
- **Optional**: Backend is only used when explicitly configured

## Backend API Endpoints

The backend provides:
- `GET /api/stops/search?query=Haarlem` - Search for stops
- `GET /api/stops/nearby?lat=52.38&lon=4.63&radius=1000` - Find nearby stops
- `GET /api/stops/{stop_code}/departures` - Get scheduled departures

## Benefits

- **Offline schedule data**: Base timetables work even if OV API is down
- **Custom schedules**: You can modify GTFS data for testing
- **Local network**: Faster responses when on same WiFi
- **Privacy**: Data stays on your local network

## Note

The backend currently provides **scheduled** GTFS data (updated weekly).
For **real-time** delays and cancellations, the app still uses OV API as primary source.
