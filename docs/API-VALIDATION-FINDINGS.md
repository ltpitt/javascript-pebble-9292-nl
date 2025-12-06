# API Validation - Final Findings

**Date:** 6 December 2025  
**Status:** ✅ VALIDATED - OV API is viable

## Solution Found

### Working Integration: william-sy/ovapi
**GitHub:** https://github.com/william-sy/ovapi  
**Last Updated:** December 4, 2025 (2 days ago - actively maintained!)

## How It Works

### API Endpoint
```
Base URL: http://v0.ovapi.nl
Endpoint: /tpc/{stop_code}
Format: JSON
Auth: None required
```

### Two-Part Approach

**1. GTFS for Stop Discovery** (Static Data)
- Download/cache GTFS data from `http://gtfs.ovapi.nl/`
- Contains all stop locations, names, codes
- Use for: Searching stops, finding nearby stops, getting stop info
- Updated periodically, can be cached

**2. OV API for Real-Time Departures**
- Query `/tpc/{stop_code}` for live departure data
- Returns: Line numbers, destinations, arrival times, delays
- Real-time, query on-demand
- Data may be sparse during off-hours

### Response Format
```json
{
  "stop_code": {
    "Stop": {
      "TimingPointCode": "31000495",
      "TimingPointName": "Stop Name"
    },
    "Passes": {
      "pass_id": {
        "LinePublicNumber": "22",
        "DestinationName50": "City Center",
        "ExpectedArrivalTime": "2025-12-06T14:30:00",
        "TargetArrivalTime": "2025-12-06T14:28:00",
        "TripStopStatus": "DRIVING",
        "TransportType": "BUS"
      }
    }
  }
}
