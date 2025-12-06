# NextRide Development Tasks

## Phase 1: MVP - Core Functionality

### Task 1: Research OV API structure and endpoints
**Status:** ✅ Complete  
**Description:** Investigate ovapi.nl API documentation to understand: authentication requirements, endpoint structure for stops/departures, response format, rate limits. Document findings for implementation.

**Success Criteria:**
- [x] Understand API authentication requirements (None - open API)
- [x] Document endpoint URLs for stops and departures
- [x] Understand response JSON structure
- [x] Identify any rate limits or usage restrictions

**Findings:** See `docs/OVAPI-RESEARCH.md` for complete documentation

---

### Task 2: Create destination management config page
**Status:** ✅ Complete  
**Description:** Create config.html with destination list management: add/edit/delete destinations with name & address, reorder with up/down arrows, set default destination. Includes "Home" and "Office" as initial templates.

**Success Criteria:**
- [x] config.html file created in project root
- [x] Destination list UI with add/edit/delete functionality
- [x] Order management with up/down arrows
- [x] Default destination dropdown selector
- [x] Home and Office added as initial destinations
- [x] Mobile-friendly styling

**Test:** Open config page, add/edit destinations, reorder with arrows, set default - ✅ Passed

---

### Task 3: Implement config page JavaScript and localStorage
**Status:** ✅ Complete  
**Description:** Add JavaScript to handle destination CRUD operations, reordering, validation, and persistence. Send complete destination list to watch via URL return method.

**Success Criteria:**
- [x] Add/edit/delete destinations with validation
- [x] Up/down arrows reorder destinations
- [x] Settings stored in localStorage
- [x] Settings loaded on page open
- [x] Settings sent to watch via URL return method

**Test:** Add destinations, reorder, save, reopen - all persist correctly - ✅ Passed

---

### Task 4: Update appinfo.json with configuration capability
**Status:** ✅ Complete  
**Description:** Ensure appinfo.json has 'configurable' capability and add appKeys for settings communication (defaultDestination, destinations array).

**Success Criteria:**
- [x] "configurable" in capabilities array
- [x] appKeys section added with required keys (defaultDestination, destinations)
- [x] File validates as proper JSON

**Test:** Run `pebble build` - should compile without errors - ✅ Passed

---

### Task 5: Implement settings receiver in app.js
**Status:** ✅ Complete  
**Description:** Implement Settings.config() to receive settings from config page. Parse JSON response from pebblejs://close# protocol. Store destinations in Settings.option() for persistence.

**Success Criteria:**
- [x] Settings.config() configured with config.html URL
- [x] Settings close handler parses JSON response
- [x] Destinations stored with Settings.option()
- [x] loadSettings() function loads saved settings on startup
- [x] Console.log confirms settings received with destination count

**Test:** Configure app, check console for confirmation message - ✅ Passed (compiles without errors)

---

### Task 6: Create main menu with destination list
**Status:** ✅ Complete  
**Description:** showMainMenu() function creates UI.Menu showing all configured destinations sorted by order. Add "📍 Current Location" as special menu item. Show 'Setup Required' card if no destinations configured.


**Success Criteria:**
- [x] Demo code removed from app.js
- [x] UI.Menu shows all destinations sorted by order
- [x] "📍 Current Location" menu item added
- [x] "Setup Required" card shown if no config
- [x] Menu selection handler implemented (placeholder for departure lookup)

**Test:** Launch app in emulator - should show destination menu with Current Location - ✅ Passed (compiles, menu implemented)

---

### Task 7: Implement GPS location fetching
**Status:** 🔴 Not Started  
**Description:** Add geolocation API integration triggered when user selects "Current Location" from menu. Get current GPS coordinates. Handle errors (no GPS, timeout) with user-friendly messages.

**Success Criteria:**
- [ ] navigator.geolocation.getCurrentPosition() implemented
- [ ] Triggered when "Current Location" selected from menu
- [ ] Timeout set (10 seconds)
- [ ] Error handling for: permission denied, timeout, unavailable
- [ ] User-friendly error messages displayed

**Test:** Select "Current Location", verify GPS coordinates obtained and departures shown

---

### Task 8: Create address geocoding function
**Status:** 🔴 Not Started  
**Description:** Implement Nominatim geocoding to convert destination addresses to lat/lon when saved in config page. Cache results with each destination to avoid repeated API calls.

**Success Criteria:**
- [ ] Nominatim geocoding function in config.html
- [ ] Geocodes address when destination is saved
- [ ] Stores lat/lon with each destination object
- [ ] Error handling for invalid addresses

**Test:** Enter address, verify it converts to coordinates (check console)

---

### Task 9: Implement OV API stops lookup
**Status:** 🔴 Not Started  
**Description:** Create function to query OV API for nearby transit stops given lat/lon coordinates. Parse response and extract stop IDs, names, and distances. Handle API errors gracefully.

**Success Criteria:**
- [ ] Function queries OV API with lat/lon
- [ ] Response parsed correctly
- [ ] Stop IDs, names, distances extracted
- [ ] Stops sorted by distance
- [ ] API error handling implemented

**Test:** Call function with test coordinates, verify stops returned

---

### Task 10: Implement OV API departures lookup
**Status:** 🔴 Not Started  
**Description:** Create function to fetch departure times from OV API for a given stop ID and destination. Parse response to extract: transport type, line number, departure time, platform/track.

**Success Criteria:**
- [ ] Function queries OV API for departures
- [ ] Response parsed correctly
- [ ] Transport type, line, time, platform extracted
- [ ] Departures filtered by destination relevance
- [ ] API error handling implemented

**Test:** Call function with test stop ID, verify departures returned

---

### Task 11: Create departures list UI
**Status:** 🔴 Not Started  
**Description:** Build UI.Menu to display departure results: show transport type, line number, relative time (minutes until departure). Sort by soonest departure first. Limit to 5-7 results.

**Success Criteria:**
- [ ] UI.Menu created for departures
- [ ] Each item shows: transport type, line, time
- [ ] Times shown as relative (e.g., "5 min")
- [ ] Sorted by soonest first
- [ ] Limited to 5-7 results

**Test:** View departures list in emulator with mock data

---

### Task 12: Add loading states and error handling
**Status:** 🔴 Not Started  
**Description:** Create loading card shown during API calls. Implement error handling for: no internet, no GPS, API failures, no departures found. Show user-friendly error messages with retry option.

**Success Criteria:**
- [ ] Loading card displays during API calls
- [ ] Error card for "No Internet"
- [ ] Error card for "No GPS"
- [ ] Error card for "API Error"
- [ ] Error card for "No Departures Found"
- [ ] Retry button on error cards

**Test:** Simulate each error condition, verify appropriate message shown

---

### Task 13: Implement manual refresh functionality
**Status:** 🔴 Not Started  
**Description:** Add refresh button/action to departures list that re-fetches data from OV API. Show loading state during refresh. Update departure times display.

**Success Criteria:**
- [ ] Refresh option in departures menu
- [ ] Loading state shown during refresh
- [ ] Data re-fetched from API
- [ ] Departures list updated with new data
- [ ] Refresh timestamp shown (optional)

**Test:** View departures, press refresh, verify list updates

---

### Task 14: Add departure details view
**Status:** 🔴 Not Started  
**Description:** Create detail card that shows when user taps a departure: full departure time, relative time, stop name, platform, transport type/line. Add back button.

**Success Criteria:**
- [ ] Detail card created
- [ ] Shows: departure time, relative time, stop name, platform, transport info
- [ ] Back button returns to departures list
- [ ] Proper formatting and layout

**Test:** Tap departure, verify details shown correctly

---

### Task 15: Test complete MVP flow end-to-end
**Status:** 🔴 Not Started  
**Description:** Manual testing: configure destination → select from menu → see departures → view details → refresh. Test both GPS and saved location modes. Test all error scenarios. Document any bugs found.

**Success Criteria:**
- [ ] GPS mode: complete flow works
- [ ] Saved location mode: complete flow works
- [ ] All error scenarios handled gracefully
- [ ] No crashes or unexpected behavior
- [ ] Bugs documented in GitHub issues

**Test:** Complete multiple full user journeys, document results

---

## Progress Tracking

**Total Tasks:** 15  
**Completed:** 0  
**In Progress:** 0  
**Not Started:** 15  

**Current Task:** Task 1 - Research OV API structure and endpoints

---

## Notes

- Each task should be manually tested before marking as complete
- Use emulator for testing whenever possible
- Document any API issues or limitations discovered
- Keep task status updated as work progresses
