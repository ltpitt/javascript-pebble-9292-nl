# OV API Complete Guide - Verified December 2025

## Summary

This guide contains **verified, tested information** about using Dutch public transport APIs for the NextRide Pebble app.

### Key Findings

1. **Real-time data**: Available via OV API v0 for ~4,111 major stops (timing points)
2. **Scheduled data**: Available via GTFS for ALL stops (including small street stops)
3. **Not all stops have real-time data** - small stops only have schedules
4. **Two different ID systems**: `stop_code` (OV API) vs `stop_id` (GTFS internal)

---

## Real-Time API (OV API v0)

### Endpoint

```
http://v0.ovapi.nl/stopareacode/{stop_code}
```

### Coverage

- **~4,111 stops** across Netherlands
- Only includes **timing points** (major stops with real-time tracking)
- Does NOT include all street-level bus stops

### Response Structure

```json
{
  "StopCode": {
    "TimingPointCode": {
      "Passes": {
        "PassKey": {
          "LinePublicNumber": "22",
          "DestinationName50": "Amsterdam Centraal",
          "TransportType": "BUS",
          "ExpectedDepartureTime": "2025-12-07T00:45:00"
        }
      }
    }
  }
}
```

### Verified Working Examples

**Haarlem Byzantiumstraat (hlmbyz)**
```bash
curl "http://v0.ovapi.nl/stopareacode/hlmbyz"
# Returns 7+ live departures
```

**Haarlem Nassaulaan (hlmnsl)**
```bash
curl "http://v0.ovapi.nl/stopareacode/hlmnsl"
# Returns 6+ live departures
```

**Haarlem Centraal (hlmcen)**
```bash
curl "http://v0.ovapi.nl/stopareacode/hlmcen"
# Returns 50+ live departures
```

### Get All Available Stops

```bash
curl "http://v0.ovapi.nl/stopareacode"
# Returns JSON with all 4,111 stops
```

Each stop includes:
- `TimingPointCode` - The stop code
- `TimingPointName` - Human-readable name
- `TimingPointTown` - City/town name
- `Latitude`, `Longitude` - GPS coordinates

---

## GTFS Data (Complete Schedules)

### Endpoint

```
http://gtfs.ovapi.nl/nl/gtfs-nl.zip
```

### Coverage

- **ALL stops** in Netherlands (hundreds of thousands)
- Includes small street-level stops without real-time tracking
- Full scheduled timetables
- Updated daily (format: `NL-YYYYMMDD.gtfs.zip`)

### Files in GTFS ZIP

| File | Size | Purpose |
|------|------|---------|
| `stops.txt` | 6.5 MB | All stop locations with coordinates |
| `stop_times.txt` | 1.2 GB | Complete scheduled timetable |
| `routes.txt` | 193 KB | All bus/train lines |
| `trips.txt` | 79 MB | Trip definitions |
| `calendar_dates.txt` | 7.3 MB | Service dates |

### Example: Finding a Stop in GTFS

**Download and search:**
```bash
curl "http://gtfs.ovapi.nl/nl/gtfs-nl.zip" -o gtfs-nl.zip
unzip -q gtfs-nl.zip
grep -i "spaarnhoven" stops.txt
```

**Result:**
```
3476039,55100120,"Haarlem, Spaarnhovenstraat",52.404407,4.648227,0,stoparea:456014
3476040,55100130,"Haarlem, Spaarnhovenstraat",52.403838,4.647723,0,stoparea:456014
```

### Example: Getting Scheduled Times

**Format:** `trip_id,stop_sequence,stop_id,stop_headsign,arrival_time,departure_time,...`

```bash
grep "^[^,]*,[^,]*,3476039," stop_times.txt | head -5
```

**Result:**
```
319645511,8,3476039,,06:11:00,06:11:00,0,0,0,2334,2331
319645513,28,3476039,IJmuiden Rotonde Stadspark,06:35:00,06:35:00,0,0,0,11536,11521
319645515,28,3476039,IJmuiden Rotonde Stadspark,07:01:00,07:01:00,0,0,0,11536,11521
```

### IMPORTANT: Two ID Systems

GTFS uses TWO different identifiers:

1. **`stop_id`** - Internal GTFS identifier (e.g., `3476039`)
   - Used in `stop_times.txt` for lookups
   - Required for scheduled timetable queries

2. **`stop_code`** - Public stop code (e.g., `55100120`)
   - User-facing identifier
   - May be used by OV API (but not always)
   - Format in `stops.txt`: `stop_id,stop_code,stop_name,...`

---

## Verified Test Results

### ✅ Stops WITH Real-Time Data

| Stop Code | Name | City | Real-Time | Schedule |
|-----------|------|------|-----------|----------|
| `hlmbyz` | Byzantiumstraat | Haarlem | ✅ Yes (7+ deps) | ✅ Yes |
| `hlmnsl` | Nassaulaan | Haarlem | ✅ Yes (6+ deps) | ✅ Yes |
| `hlmcen` | Haarlem Centraal | Haarlem | ✅ Yes (50+ deps) | ✅ Yes |
| `asdcs` | Amsterdam Centraal | Amsterdam | ✅ Yes (100+ deps) | ✅ Yes |

### ❌ Stops WITHOUT Real-Time Data

| Stop Code | Stop ID | Name | City | Real-Time | Schedule |
|-----------|---------|------|------|-----------|----------|
| `55100120` | `3476039` | Spaarnhovenstraat | Haarlem | ❌ No (empty) | ✅ Yes |
| `55100130` | `3476040` | Spaarnhovenstraat | Haarlem | ❌ No (empty) | ✅ Yes |

**Testing commands:**
```bash
# Returns empty {}
curl "http://v0.ovapi.nl/stopareacode/55100120"
curl "http://v0.ovapi.nl/stopareacode/3476039"
curl "http://v0.ovapi.nl/stopareacode/stoparea:456014"

# All three formats return no real-time data
```

---

## Implementation Strategy

### For Pebble App (Current)

**Use OV API v0 for real-time data:**
- Pros: Simple, fast, no processing needed
- Cons: Limited to ~4,111 timing points
- Best for: Major stops with real-time tracking

**Implementation:**
```javascript
// Already working in pebble-app/js/app.js
fetch('http://v0.ovapi.nl/stopareacode/' + stopCode)
  .then(response => response.json())
  .then(data => {
    // Parse nested structure: StopCode → TimingPointCode → Passes
  });
```

### For Complete Coverage (Future)

**Hybrid approach:**
1. Try OV API v0 for real-time data
2. If empty, fall back to GTFS scheduled data
3. Requires backend server to parse 1.2GB GTFS file

**Why backend needed:**
- GTFS `stop_times.txt` is 1.2GB (too large for Pebble/phone)
- Must be pre-processed and indexed
- Query by stop_code → return next departures from schedule

---

## Configuration Page Integration

The `config.html` page needs GTFS data for stop search.

### Current Implementation (config.html)

**Problem:** Code was trying to use OV API for search, but should use GTFS
- OV API has only 4,111 timing points
- GTFS has ALL stops including street-level stops

### Recommended Approach

**Option 1: Download GTFS ZIP in config page**
```javascript
// In config.html (runs on phone, has resources)
fetch('http://gtfs.ovapi.nl/nl/gtfs-nl.zip')
  .then(response => response.blob())
  .then(blob => {
    // Extract stops.txt
    // Parse CSV
    // Build searchable index
    // Allow user to search by city + street name
  });
```

**Option 2: Use backend service**
- Build Node.js server that hosts GTFS data
- Expose API: `GET /search?city=Haarlem&stop=Spaarn`
- Returns matching stops with coordinates and stop_codes

---

## Common Pitfalls

### ❌ Don't assume all stop codes have real-time data
Many stops return empty `{}` - they're in GTFS schedules only.

### ❌ Don't confuse stop_id with stop_code
- `stop_id` = GTFS internal (3476039)
- `stop_code` = Public code (55100120)
- Neither guarantees real-time data availability

### ❌ Don't download GTFS on Pebble watch
The 1.2GB file is way too large. Use a backend server.

### ✅ Do test with working stops first
Start with `hlmbyz`, `hlmnsl`, `hlmcen` - guaranteed to have data.

### ✅ Do handle empty responses gracefully
Show "No departures available" instead of crashing.

---

## Quick Reference Commands

**Get all available stops:**
```bash
curl "http://v0.ovapi.nl/stopareacode" > all_stops.json
```

**Test a specific stop:**
```bash
curl "http://v0.ovapi.nl/stopareacode/hlmbyz" | python3 -m json.tool
```

**Search for stops in GTFS:**
```bash
curl -s "http://gtfs.ovapi.nl/nl/gtfs-nl.zip" -o gtfs.zip
unzip -q gtfs.zip
grep -i "haarlem" stops.txt | grep -i "spaarnh"
```

**Find scheduled times:**
```bash
# Get stop_id first from stops.txt (column 1)
grep "^[^,]*,[^,]*,STOP_ID," stop_times.txt | head -20
```

---

## URLs Summary

| Purpose | URL | Method | Auth |
|---------|-----|--------|------|
| All stops metadata | `http://v0.ovapi.nl/stopareacode` | GET | None |
| Real-time departures | `http://v0.ovapi.nl/stopareacode/{code}` | GET | None |
| GTFS complete data | `http://gtfs.ovapi.nl/nl/gtfs-nl.zip` | GET | None |
| GTFS dated version | `http://gtfs.ovapi.nl/nl/NL-YYYYMMDD.gtfs.zip` | GET | None |

All endpoints are:
- ✅ Free to use
- ✅ No authentication required
- ✅ No rate limiting observed
- ✅ CORS-enabled for browser use

---

## Conclusion

**For NextRide Pebble App:**
- ✅ Current implementation works correctly with OV API v0
- ✅ Use stop codes from OV API's timing points (4,111 stops)
- ⚠️ Users must select stops that have real-time data
- 🔮 Future: Add GTFS backend for complete stop coverage

**Status:** Production-ready for timing points. GTFS integration optional enhancement.
