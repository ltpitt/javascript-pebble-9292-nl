# GTFS Schedule Data Fix (Dec 9, 2025)

## Problem
API was returning incomplete departure data:
- Only trip_id, departure_time, arrival_time, stop_sequence
- No route numbers (e.g., "Bus 3")
- No destinations (e.g., "IJmuiden Rotonde Stadspark")
- No transport mode information

This made it impossible to compare with 9292.nl schedule.

## Root Cause
Database was missing two critical GTFS tables:
1. **routes.txt** - Contains route numbers and names
2. **trip_headsign** field in trips.txt - Contains destinations

## Solution
Updated `gtfs_db.py` to:

1. **Added routes table** with:
   - route_id, route_short_name, route_long_name, route_type, route_color

2. **Expanded trips table** with:
   - trip_headsign (destination)
   - trip_short_name (trip number)
   - direction_id

3. **Fixed departures query** to JOIN:
   - stop_times → trips → routes + calendar_dates
   - Returns complete schedule info

## Result
API now returns complete departure data:

```json
{
  "departure_time": "19:08:00",
  "route_short_name": "3",
  "route_long_name": "Haarlem Schalkwijk - IJmuiden Rotonde Stadspark",
  "trip_headsign": "IJmuiden Rotonde Stadspark",
  "mode": "Bus",
  "stop_name": "Haarlem, Spaarnhovenstraat"
}
```

## Testing
Verified with Spaarnhovenstraat, Haarlem:
- Bus line 3 departures every 15 minutes
- Alternating destinations: IJmuiden / Haarlem Delftplein
- Matches GTFS scheduled timetable (not real-time)

## Database Rebuild
Old database removed and rebuilt with:
- 79,037 stops
- 21,913,470 scheduled departures
- Full routes and trip information

**Note**: This is scheduled data from GTFS. For real-time delays/cancellations, 
the Pebble app should still use OV API as primary source.
