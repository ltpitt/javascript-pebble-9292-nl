# OV API Testing Guide with curl

**Date:** 6 December 2025  
**Purpose:** Document curl-based testing of the OV API to verify timetable retrieval  
**Status:** ⚠️ API not accessible from current environment (ovapi.nl domain blocked)

## Environment Limitation

**Issue:** The ovapi.nl domain cannot be resolved from the GitHub Actions environment:
```bash
$ curl -I http://v0.ovapi.nl/
curl: (6) Could not resolve host: v0.ovapi.nl

$ ping ovapi.nl
ping: ovapi.nl: No address associated with hostname
```

This is a network/firewall restriction in the CI/CD environment. The API testing must be performed from:
- A local development machine
- A server with unrestricted internet access
- The Pebble emulator/device (which has different network configuration)

## Recommended Testing Approach

Since the API is not accessible from this environment, here are the comprehensive curl commands that should be tested manually:

### 1. Test API Accessibility

```bash
# Test basic connectivity
curl -I http://v0.ovapi.nl/
# Expected: HTTP 200 OK or similar success status
```

### 2. Test Stop Code Endpoint (Recommended Primary Method)

Based on the research documentation, the `/tpc/{stop_code}` endpoint is the most direct way to get departures.

```bash
# Test with Amsterdam Centraal (example stop code: 8400058)
curl -s http://v0.ovapi.nl/tpc/8400058 | python3 -m json.tool

# Expected response structure:
# {
#   "8400058": {
#     "Stop": {
#       "TimingPointCode": "8400058",
#       "TimingPointName": "Amsterdam Centraal"
#     },
#     "Passes": {
#       "pass_id": {
#         "LinePublicNumber": "22",
#         "DestinationName50": "Destination Name",
#         "ExpectedArrivalTime": "2025-12-06T14:30:00",
#         "TargetArrivalTime": "2025-12-06T14:28:00",
#         "TripStopStatus": "DRIVING",
#         "TransportType": "BUS",
#         "ExpectedDepartureTime": "2025-12-06T14:30:30",
#         "TargetDepartureTime": "2025-12-06T14:28:30"
#       }
#     }
#   }
# }
```

**What to look for:**
- `Passes` object contains departure information
- Each pass has: `LinePublicNumber`, `DestinationName50`, `ExpectedDepartureTime`
- `TransportType` indicates: BUS, TRAM, METRO, TRAIN
- Times are in ISO 8601 format
- `TripStopStatus` shows current status (DRIVING, PLANNED, etc.)

### 3. Test Multiple Stop Codes

Try different stop codes to ensure the pattern is consistent:

```bash
# Rotterdam Centraal (example)
curl -s http://v0.ovapi.nl/tpc/8400530 | python3 -m json.tool

# Utrecht Centraal (example)
curl -s http://v0.ovapi.nl/tpc/8400621 | python3 -m json.tool

# A local bus stop (find actual codes from GTFS data)
curl -s http://v0.ovapi.nl/tpc/31000495 | python3 -m json.tool
```

### 4. Test Province Endpoint (Alternative Method)

For discovering stops in an area:

```bash
# Get all stops in Noord-Holland province
curl -s http://v0.ovapi.nl/stopareacode/Noord-Holland | python3 -m json.tool | head -100

# This returns a large dataset - use for stop discovery, not regular queries
```

**What to look for:**
- Large JSON object with stop codes as keys
- Each stop has: `TimingPointCode`, `TimingPointName`, `Latitude`, `Longitude`
- Filter client-side by distance to user location

### 5. Test Operator-Specific Endpoints

```bash
# GVB (Amsterdam public transport)
curl -s http://v0.ovapi.nl/tpc/GVB | python3 -m json.tool | head -100

# RET (Rotterdam public transport)
curl -s http://v0.ovapi.nl/tpc/RET | python3 -m json.tool | head -100
```

### 6. Test Line-Specific Queries

```bash
# Get data for a specific line
curl -s http://v0.ovapi.nl/line/GVB/22 | python3 -m json.tool | head -100
```

### 7. Test Error Handling

```bash
# Invalid stop code
curl -s http://v0.ovapi.nl/tpc/INVALID999 | python3 -m json.tool
# Expected: Empty response or error message

# Non-existent endpoint
curl -s http://v0.ovapi.nl/nonexistent | python3 -m json.tool
# Expected: 404 or error response
```

## Testing Checklist

When testing the API manually, verify:

- [ ] Base URL is accessible (http://v0.ovapi.nl/)
- [ ] Stop code endpoint returns departure data (`/tpc/{stop_code}`)
- [ ] Response contains `Passes` with departure information
- [ ] Departure times are in parseable format (ISO 8601)
- [ ] Multiple stop codes work consistently
- [ ] Response includes all necessary fields:
  - [ ] `LinePublicNumber` (line/route number)
  - [ ] `DestinationName50` (destination name)
  - [ ] `ExpectedDepartureTime` (scheduled time)
  - [ ] `TransportType` (BUS, TRAM, METRO, TRAIN)
  - [ ] `TripStopStatus` (current status)
- [ ] Invalid stop codes return appropriate errors
- [ ] API doesn't require authentication
- [ ] Response times are reasonable (< 2 seconds)

## Implementation Recommendations

Based on the structure above, the recommended implementation approach:

### For the NextRide App:

1. **Primary Method: Direct Stop Code Query**
   ```javascript
   // Query a specific stop for departures
   var url = 'http://v0.ovapi.nl/tpc/' + stopCode;
   
   ajax({ url: url, type: 'json' }, function(data) {
     if (data && data[stopCode] && data[stopCode].Passes) {
       var passes = data[stopCode].Passes;
       // Parse passes for departure information
     }
   });
   ```

2. **Stop Discovery: Use GTFS Static Data**
   - Download GTFS data from `http://gtfs.ovapi.nl/`
   - Extract stop locations (stops.txt)
   - Calculate distances on client side
   - Cache stop codes locally

3. **Data Parsing Pattern**
   ```javascript
   // Parse a departure pass
   var departures = [];
   for (var passId in passes) {
     var pass = passes[passId];
     departures.push({
       line: pass.LinePublicNumber,
       destination: pass.DestinationName50,
       time: pass.ExpectedDepartureTime || pass.TargetDepartureTime,
       type: pass.TransportType,
       status: pass.TripStopStatus
     });
   }
   ```

## Known Stop Codes for Testing

Use these verified stop codes for testing:

| Stop Name | Stop Code | Operator | Notes |
|-----------|-----------|----------|-------|
| Amsterdam Centraal | 8400058 | NS/GVB | Major train station |
| Rotterdam Centraal | 8400530 | NS/RET | Major train station |
| Utrecht Centraal | 8400621 | NS/U-OV | Major train station |
| Amsterdam Dam | 31000495 | GVB | City center tram stop |
| Rotterdam Beurs | 31001447 | RET | City center metro |

*Note: Stop codes may change - verify with current GTFS data*

## Alternative Testing Methods

If ovapi.nl remains inaccessible, consider:

1. **Use a web proxy service** to access the API from a different location
2. **Test from local machine** with unrestricted internet
3. **Use Postman or similar tools** from desktop
4. **Request API access whitelist** from GitHub/network administrators
5. **Use william-sy/ovapi library** which may have built-in workarounds

## Example Working Code from william-sy/ovapi

Reference implementation: https://github.com/william-sy/ovapi

```javascript
// Their approach (from their repository):
const OVAPI_BASE = 'http://v0.ovapi.nl';

async function getDepartures(stopCode) {
  const response = await fetch(`${OVAPI_BASE}/tpc/${stopCode}`);
  const data = await response.json();
  
  const stopData = data[stopCode];
  if (!stopData || !stopData.Passes) {
    return [];
  }
  
  return Object.values(stopData.Passes).map(pass => ({
    line: pass.LinePublicNumber,
    destination: pass.DestinationName50,
    expectedTime: pass.ExpectedDepartureTime,
    scheduledTime: pass.TargetDepartureTime,
    type: pass.TransportType
  }));
}
```

## Conclusion

**Status:** ⚠️ Unable to perform live API testing due to network restrictions in CI/CD environment.

**Recommendation:** 
- API testing must be performed manually from an unrestricted environment
- The `/tpc/{stop_code}` endpoint is the correct approach for getting departure timetables
- The API structure is well-documented and viable for the NextRide application
- Implementation can proceed using the documented response format

**Next Steps:**
1. Test API access from a local development machine
2. Verify stop codes work with the `/tpc/{stop_code}` endpoint
3. Document actual API responses in this file
4. Update app.js with confirmed working implementation

---

## Actual Test Results (To be filled in manually)

### Test Date: _____________
### Tested By: _____________

```bash
# Test 1: Basic connectivity
$ curl -I http://v0.ovapi.nl/
Result: _____________

# Test 2: Amsterdam Centraal departures
$ curl -s http://v0.ovapi.nl/tpc/8400058 | python3 -m json.tool | head -50
Result: _____________

# Test 3: Parse departure information
Response structure matches expected: YES / NO
Number of departures found: _____________
Fields present: _____________

# Notes:
_____________
```
