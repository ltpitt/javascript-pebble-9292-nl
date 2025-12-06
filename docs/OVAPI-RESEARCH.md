# OV API Research - Task 1 Findings

**Date:** 6 December 2025  
**API:** ovapi.nl (Dutch Public Transport API)  
**Status:** ✅ API is accessible and free to use

## API Overview

### Base Information
- **Base URL:** `https://v0.ovapi.nl/`
- **Authentication:** None required (open API)
- **Rate Limits:** Not officially documented, use reasonable request frequency
- **Data Format:** JSON
- **Coverage:** All Dutch public transport (buses, trams, trains, metros)

## Key Endpoints

### 1. Stop/Station Lookup
**Endpoint Pattern:** `/stopareacode/{location}`

Example queries:
- Find stops near a location (by city name or area)
- Returns stop codes, names, and basic info

### 2. Nearby Stops (by coordinates)
**Endpoint Pattern:** Not directly supported - need to use geographic search

**Alternative approach:**
- Use the `/tpc/{province}` endpoint to get all stops in a province
- Filter by distance calculation on client side
- OR: Use `/stopareacode/{areaname}` for city-level searches

### 3. Real-time Departures
**Endpoint Pattern:** `/tpc/{province}` or `/line/{operator}/{line}`

Returns:
- Current departures from all stops
- Transport type (bus/tram/metro/train)
- Line numbers
- Departure times
- Delays
- Destinations

### 4. Stop-specific Data
**Endpoint Pattern:** `/stop/{tpc}/{stopcode}`

Where:
- `tpc` = Transport operator code (e.g., GVB for Amsterdam)
- `stopcode` = Specific stop identifier

Returns detailed departure information for that specific stop.

## Response Format

### Typical Stop Data Structure
```json
{
  "StopCode": {
    "TimingPointCode": "12345",
    "TimingPointName": "Station Name",
    "Latitude": 52.3702,
    "Longitude": 4.8952,
    "Passes": [
      {
        "LinePublicNumber": "397",
        "DestinationName50": "Destination",
        "TransportType": "BUS",
        "ExpectedArrivalTime": "2025-12-06T14:30:00",
        "ExpectedDepartureTime": "2025-12-06T14:30:30",
        "TripStopStatus": "DRIVING",
        "OperatorCode": "GVB"
      }
    ]
  }
}
```

### Transport Types
- `BUS` - Bus
- `TRAM` - Tram
- `METRO` - Metro/Subway  
- `TRAIN` - Train
- `FERRY` - Ferry

## Implementation Strategy for NextRide

### Recommended Approach

**Option 1: Direct Stop Code (Simpler)**
1. User provides stop code directly (e.g., "12345")
2. Query `/stop/{tpc}/{stopcode}` for departures
3. Filter by destination if needed
4. Display results

**Option 2: Geographic Search (Better UX)**
1. Get user's GPS coordinates or geocode address
2. Query `/tpc/{province}` to get all stops in area
3. Calculate distance to each stop on client side
4. Filter to nearest 3-5 stops
5. Query departures for those stops
6. Display aggregated results

**Recommended: Hybrid Approach**
1. Start with province-level data: `/tpc/Noord-Holland` (for Amsterdam area)
2. Filter stops by distance from user location
3. Cache stop data locally to reduce API calls
4. Query specific stop departures when needed

### Data Flow
```
User Location (GPS/Address)
    ↓
Get Province Code (hardcode common ones: Noord-Holland, Zuid-Holland, Utrecht)
    ↓
Query: /tpc/{province}
    ↓
Filter stops by distance (<1km radius)
    ↓
Extract stop codes + names
    ↓
For each nearby stop:
  Query: /stop/{tpc}/{stopcode}
    ↓
Aggregate departures
    ↓
Filter by destination (if user configured)
    ↓
Sort by departure time
    ↓
Display to user
```

## Limitations & Considerations

### API Limitations
1. **No direct coordinate search** - Must filter client-side
2. **Province-level queries are large** - Cache aggressively
3. **No authentication** - Respect fair use, don't hammer the API
4. **Real-time only** - No schedule data for future dates

### Performance Optimizations
1. **Cache stop locations** - They don't change often
2. **Limit requests** - Query every 30-60 seconds max for refreshes
3. **Filter aggressively** - Only query stops within reasonable walking distance
4. **Province detection** - Map common cities to provinces to reduce data

### Error Handling Needed
- Network timeout
- Invalid stop codes
- No departures found
- API temporarily unavailable
- Malformed JSON responses

## Province Codes (Common)

For geographic filtering:
- `Noord-Holland` - Amsterdam, Haarlem, Zaandam area
- `Zuid-Holland` - Rotterdam, Den Haag area
- `Utrecht` - Utrecht area
- `Gelderland` - Arnhem, Nijmegen area
- Additional provinces available in API

## Alternative: GTFS Data

If real-time API is problematic:
- Static GTFS data available at: `http://gtfs.ovapi.nl/`
- Contains schedules, stop locations, routes
- Good for stop location lookup
- Not real-time

## Next Steps for Implementation

**Task 2-4:** Build configuration page
- Let users enter destination address or choose GPS
- Optionally: Let advanced users enter stop codes directly

**Task 7-9:** Location & Stop Discovery
- Implement GPS fetching
- Implement geocoding (address → coordinates)
- Query OV API for nearby stops
- Cache stop data

**Task 10-11:** Departure Display
- Query real-time departures
- Parse and filter by destination
- Display in UI with relative times

## Test Examples

Once implemented, test with:
- **Amsterdam Central:** TPC=GVB area
- **Rotterdam Central:** TPC=RET area
- **Utrecht Central:** TPC=U-OV area

## Documentation Links
- GitHub Wiki: https://github.com/koch-t/KV78Turbo-OVAPI/wiki
- API Base: https://ovapi.nl/
- GTFS Data: http://gtfs.ovapi.nl/

---

**Research Status:** ✅ Complete  
**Ready for Implementation:** Yes  
**Recommended Next Task:** Task 2 - Create configuration page
