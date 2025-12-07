# Real-Time vs Non-Real-Time Stops - Pain Point Analysis

## Problem Statement

The OV API returns ~4,111 timing points (major stops), but **not all stops have active departures at all times**. This creates a situation where:
- Stops exist in the API with coordinates
- Stops return `Passes: {}` (empty) when queried
- App shows "No departures found" even though stops are nearby

## Current App Architecture

### 1. **GPS-Based Search Flow** (Current Location button)
```
User clicks "Current Location"
  ↓
getCurrentLocation() - Gets GPS coords (52.404, 4.648)
  ↓
findNearbyStops() - Fetches ALL 4,111 stops, filters by distance
  ↓
Returns 10 closest stops sorted by distance
  ↓
fetchDeparturesFromStops() - Tries each stop sequentially
  ↓
fetchDepartures() - Calls API for each stop
  ↓
Problem: Empty Passes {} returned even for real-time stops
```

**Pain Point #1: Distance-Based Sorting**
- Line 172-174: Sorts by distance only
- Doesn't prioritize stops with active departures
- Result: App tries 10 nearby stops with no service before finding Haarlem Centraal (2.86km away)

**Pain Point #2: No Pre-Filtering**
- Line 120-188: `findNearbyStops()` returns ANY stop within 10km
- Doesn't check if stop currently has departures
- Can't pre-filter because checking requires individual API calls

**Pain Point #3: Sequential Retry Logic**
- Line 502-520: `fetchDeparturesFromStops()` tries stops one-by-one
- Slow: Each API call takes ~200ms
- Trying 10 stops = ~2 seconds before finding data

### 2. **Saved Stops Flow** (Configured stops from config page)
```
User selects saved stop from menu
  ↓
Check if stop has stopCode (demo mode)
  ↓
  YES: fetchDepartures(stopCode) directly
  ↓
  NO: findNearbyStops(lat, lon) + get closest
  ↓
fetchDepartures() - Calls API
  ↓
Problem: Same empty Passes {} issue
```

**Pain Point #4: Config Page Stop Selection**
- Users configure stops via config.html (not in this file)
- Config page likely lets users pick ANY address
- No validation that stop has real-time data
- No way to pre-check if stop is good

**Pain Point #5: Fallback Logic for Saved Stops**
- Line 598-617: If saved stop has no stopCode, does GPS search
- Uses only closest stop (nearbyStops[0])
- No retry logic like GPS flow has

### 3. **Departure Fetching Logic**
```
fetchDepartures(stopCode, stopName, callback)
  ↓
Call http://v0.ovapi.nl/stopareacode/{stopCode}
  ↓
Parse: stopCode → timingPoints → Passes
  ↓
Check: if (timingPoint.Passes) { ... }
  ↓
Count: Object.keys(timingPoint.Passes).length
  ↓
Problem: Passes exists but is empty {}
```

**Pain Point #6: Empty Passes Detection**
- Line 245-246: Checks if `Passes` exists, gets count
- Count = 0 means no departures
- But we don't know WHY:
  - Weekend/holiday schedule?
  - Off-peak hours (night)?
  - Stop permanently inactive?
  - Temporary service disruption?

## Root Causes

### Cause 1: API Limitation
- `/stopareacode` endpoint returns ALL timing points
- No way to filter for "stops with current departures"
- Must check each stop individually

### Cause 2: Time-Dependent Data
- Saturday 12:40 = reduced service
- Small stops may have 0 departures
- Major stations (Haarlem Centraal) still active
- No way to know schedule ahead of time

### Cause 3: Distance ≠ Activity
- Closest stop may be inactive
- Active major station may be slightly farther
- Current sort: pure distance
- Better sort: active stops first, then distance

## Evidence from Recent Test

**User Location:** 52.4040076, 4.6484057 (Haarlem)

**Stops Found & Tried (in order):**
1. Haarlem, J.W. Lucasweg (hlmluw) - 0 passes - ~1-2km
2. Santpoort-Zuid, Station Zuid (sanns) - 0 passes - ~2-3km
3. Haarlem, Delftplein (hlmdpl) - 0 passes - ~1-2km
4. Haarlem, Ir. Lelyweg (hlmilw) - 0 passes - ~2-3km
5. Haarlem, Koudenhorn (hlmkdh) - 0 passes - ~3-4km

**Stop NOT Tried (but has data):**
- **Haarlem Centraal (hlmcen)** - **13 passes** - **2.86km away**
- Likely stop #6-8 in the list
- Has active departures NOW
- Slightly farther than small stops

## Proposed Solutions

### Solution A: Smart Sorting (RECOMMENDED)
**Idea:** Pre-fetch pass counts, sort by "has departures" + distance

**Pros:**
- Finds active stops first
- Works at any time of day
- Minimal code changes

**Cons:**
- Multiple API calls upfront (~10 calls)
- Takes 2-3 seconds
- But same time as current sequential approach

**Implementation:**
```javascript
// In findNearbyStops(), after getting nearby stops:
function checkStopActivity(stops, callback) {
  var checked = 0;
  var results = [];
  
  stops.forEach(function(stop) {
    ajax({
      url: 'http://v0.ovapi.nl/stopareacode/' + stop.code,
      type: 'json'
    }, function(data) {
      var passCount = 0;
      // Count passes
      for (var tp in data[stop.code]) {
        if (data[stop.code][tp].Passes) {
          passCount += Object.keys(data[stop.code][tp].Passes).length;
        }
      }
      
      results.push({
        code: stop.code,
        name: stop.name,
        distance: stop.distance,
        passCount: passCount
      });
      
      checked++;
      if (checked === stops.length) {
        // Sort by: passCount DESC, then distance ASC
        results.sort(function(a, b) {
          if (a.passCount !== b.passCount) {
            return b.passCount - a.passCount; // More passes first
          }
          return a.distance - b.distance; // Then closer first
        });
        callback(null, results);
      }
    });
  });
}
```

### Solution B: Major Stations First
**Idea:** Prioritize known major stations (centraal, station, etc.)

**Pros:**
- Fast - no extra API calls
- Works well for cities
- Simple keyword matching

**Cons:**
- Doesn't help in rural areas
- May skip closer active stops
- Requires station name patterns

**Implementation:**
```javascript
// In findNearbyStops(), after sorting by distance:
nearbyStops.sort(function(a, b) {
  // Major station keywords
  var aMajor = /centraal|station|cs/i.test(a.name);
  var bMajor = /centraal|station|cs/i.test(b.name);
  
  if (aMajor && !bMajor) return -1; // a first
  if (!aMajor && bMajor) return 1;  // b first
  
  return a.distance - b.distance; // Same priority, use distance
});
```

### Solution C: Hybrid Approach (BEST)
**Idea:** Combine keywords + pass count checking

**Flow:**
1. Get 20 nearest stops (not 10)
2. Prioritize major stations by keyword
3. Check top 10 for pass counts
4. Sort by activity + distance
5. Try in order

**Pros:**
- Best of both worlds
- Fast for cities (major stations)
- Thorough for suburbs (pass checking)
- Reliable results

**Cons:**
- More complex logic
- Still needs API calls

### Solution D: Better Error Messages
**Idea:** Don't change logic, just inform user better

**Pros:**
- Easy to implement
- Helps user understand
- No performance impact

**Cons:**
- Doesn't solve core problem
- User still waits for checks

**Implementation:**
```javascript
// In fetchDeparturesFromStops()
console.log('Checking stops for departures...');
var now = new Date();
var dayOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][now.getDay()];
var hour = now.getHours();

var message = 'No departures found at ' + stops.length + ' nearby stops.\n\n';

if (dayOfWeek === 'Saturday' || dayOfWeek === 'Sunday') {
  message += 'Weekend service is often reduced. ';
}

if (hour < 6 || hour > 23) {
  message += 'Night hours have limited service. ';
}

message += 'Try a different time or configure a major station in settings.';
```

## Recommendations

### Immediate (Next 1-2 hours):
1. ✅ **Implement Solution B (Major Stations First)**
   - Quick fix with keyword matching
   - Catches Haarlem Centraal and similar
   - No performance impact

2. ✅ **Improve Error Message (Solution D)**
   - Add context about time/day
   - Suggest alternatives
   - Better UX

### Short-term (This week):
3. ⏳ **Implement Solution A (Smart Sorting)**
   - Pre-check pass counts
   - Sort active stops first
   - Reliable at all times

### Long-term (Future enhancement):
4. 📋 **Update Config Page**
   - Validate stops have real-time data
   - Show last-seen departure count
   - Warn about inactive stops
   - Suggest nearby alternatives

5. 📋 **Caching Layer**
   - Cache stop list locally
   - Cache pass counts (5min TTL)
   - Reduce API calls
   - Faster responses

## Testing Plan

**Test Cases:**
1. ✅ **Saturday afternoon** (current) - Reduced service
2. ⏳ **Weekday morning** (8am) - Peak service
3. ⏳ **Sunday evening** (8pm) - Minimal service
4. ⏳ **Weekday night** (2am) - No service
5. ⏳ **Rural location** - Sparse stops

**Expected Results:**
- Solution B: Should find Haarlem Centraal first
- Solution A: Should rank by active departures
- Solution C: Best results in all scenarios

## Files That Need Changes

1. **src/js/app.js** (this file)
   - `findNearbyStops()` - Add smart sorting
   - `fetchDeparturesFromStops()` - Better error messages
   - Lines 120-188, 502-520

2. **config.html** (not analyzed yet)
   - Stop selection UI
   - Validation logic
   - Preview departures

3. **TASKS.md** (update)
   - Document realtime vs non-realtime
   - Add new test cases
   - Update success criteria

## Next Steps

**Choose implementation:**
- [ ] Start with Solution B (quick win)
- [ ] Then add Solution D (better UX)
- [ ] Finally Solution A (complete solution)
- [ ] Test at different times/days
- [ ] Update documentation
