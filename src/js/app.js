/**
 * NextRide - Dutch Public Transport App for Pebble
 * Shows real-time departure information for configured stops
 */

var UI = require('ui');
var Settings = require('settings');
var ajax = require('ajax');
var Vector2 = require('vector2');

// Global settings storage
var appSettings = {
  defaultStop: null,
  stops: []
};

// Configure settings
Settings.config(
  { url: 'http://davidenastri.it/nextride/config.html' },
  function(e) {
    console.log('Opening configuration page');
  },
  function(e) {
    console.log('Configuration closed');
    
    // Parse settings from config page
    if (e.response) {
      try {
        var settings = JSON.parse(decodeURIComponent(e.response));
        console.log('Received settings: ' + JSON.stringify(settings));
        
        // Store settings
        appSettings.defaultStop = settings.defaultStop || null;
        appSettings.stops = settings.stops || [];
        
        // Save to persistent storage (Settings.option handles serialization)
        Settings.option('defaultStop', appSettings.defaultStop);
        Settings.option('stops', appSettings.stops);
        
        console.log('Saved ' + appSettings.stops.length + ' stops');
        console.log('Default stop: ' + appSettings.defaultStop);
        
        // Show confirmation
        showMainMenu();
      } catch (error) {
        console.log('Error parsing settings: ' + error);
        showError('Configuration Error', 'Failed to save settings');
      }
    }
  }
);

// Load saved settings on startup
function loadSettings() {
  appSettings.defaultStop = Settings.option('defaultStop') || null;
  var stopsData = Settings.option('stops');
  
  // Handle both JSON strings (legacy) and objects (current)
  if (typeof stopsData === 'string') {
    try {
      appSettings.stops = JSON.parse(stopsData);
    } catch (e) {
      console.log('Error parsing stops JSON: ' + e);
      appSettings.stops = [];
    }
  } else if (Array.isArray(stopsData)) {
    appSettings.stops = stopsData;
  } else {
    appSettings.stops = [];
  }
  
  console.log('Loaded settings on startup');
  console.log('Stops: ' + appSettings.stops.length);
  console.log('Default: ' + appSettings.defaultStop);
}

// Show error card
function showError(title, message) {
  var errorCard = new UI.Card({
    title: title,
    body: message,
    scrollable: true
  });
  errorCard.show();
}

// Get current GPS location
function getCurrentLocation(callback) {
  console.log('Getting current GPS location...');
  
  var locationOptions = {
    enableHighAccuracy: true,
    maximumAge: 10000,
    timeout: 10000
  };
  
  navigator.geolocation.getCurrentPosition(
    function(pos) {
      console.log('GPS success: ' + pos.coords.latitude + ', ' + pos.coords.longitude);
      callback(null, {
        lat: pos.coords.latitude,
        lon: pos.coords.longitude
      });
    },
    function(err) {
      console.log('GPS error: ' + err.message);
      var errorMsg = 'Unable to get location.';
      if (err.code === 1) {
        errorMsg = 'Location permission denied.';
      } else if (err.code === 3) {
        errorMsg = 'Location timeout.';
      }
      callback(errorMsg);
    },
    locationOptions
  );
}

// Find nearby transit stops using OV API
function findNearbyStops(lat, lon, callback) {
  console.log('Finding stops near: ' + lat + ', ' + lon);
  
  // Note: This fetches all 4,111+ stops from the API to find nearby ones.
  // This is a known limitation as the API doesn't support coordinate-based search.
  // Future improvement: Implement client-side caching of stop data to avoid
  // repeated downloads, or filter by province/region to reduce data size.
  var url = 'http://v0.ovapi.nl/stopareacode';
  
  ajax({
    url: url,
    type: 'json'
  }, function(data) {
    console.log('Received stop data from OV API');
    console.log('Data keys: ' + Object.keys(data).length);
    
    // Find closest stops within 1km
    var nearbyStops = [];
    var checkedAreas = 0;
    var foundStops = 0;
    
    // Iterate through all stop area codes
    for (var stopAreaCode in data) {
      if (data.hasOwnProperty(stopAreaCode)) {
        checkedAreas++;
        var stopArea = data[stopAreaCode];
        
        // Check if this stop area has coordinates directly
        if (stopArea && stopArea.Latitude && stopArea.Longitude) {
          foundStops++;
          var distance = calculateDistance(lat, lon, 
            parseFloat(stopArea.Latitude), 
            parseFloat(stopArea.Longitude)
          );
          
          // Log first few for debugging
          if (foundStops <= 5) {
            console.log('Check stop ' + foundStops + ': ' + stopArea.TimingPointName + ' @ ' + distance.toFixed(3) + 'km');
          }
          
          if (distance < 10) { // Within 10km
            nearbyStops.push({
              code: stopAreaCode,
              name: stopArea.TimingPointName || stopAreaCode,
              distance: distance
            });
          }
        }
      }
    }
    
    console.log('Checked ' + checkedAreas + ' areas, found ' + foundStops + ' stops total');
    
    // Sort by distance
    nearbyStops.sort(function(a, b) {
      return a.distance - b.distance;
    });
    
    console.log('Found ' + nearbyStops.length + ' nearby stops within 10km');
    
    if (nearbyStops.length === 0) {
      callback('No stops found nearby');
    } else {
      console.log('Returning top 10: ' + nearbyStops.slice(0, 10).map(function(s) { return s.name; }).join(', '));
      callback(null, nearbyStops.slice(0, 10)); // Return top 10
    }
  }, function(error, status, request) {
    console.log('OV API error: ' + JSON.stringify(error));
    console.log('Status: ' + status);
    callback('Failed to fetch stops: ' + (status || 'network error'));
  });
}

// Calculate distance between two coordinates (Haversine formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
  var R = 6371; // Earth's radius in km
  var dLat = (lat2 - lat1) * Math.PI / 180;
  var dLon = (lon2 - lon1) * Math.PI / 180;
  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
          Math.sin(dLon/2) * Math.sin(dLon/2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Fetch departures for a specific stop
function fetchDepartures(stopCode, stopName, callback) {
  console.log('=== FETCH DEPARTURES START ===');
  console.log('stopCode parameter: ' + stopCode + ' (type: ' + typeof stopCode + ')');
  console.log('stopName parameter: ' + stopName + ' (type: ' + typeof stopName + ')');
  console.log('callback parameter type: ' + typeof callback);
  
  if (!stopCode) {
    console.log('ERROR: stopCode is undefined/null!');
    callback('Stop code is missing');
    return;
  }
  
  if (!stopName) {
    console.log('WARNING: stopName is undefined/null, using default');
    stopName = 'Unknown Stop';
  }
  
  var url = 'http://v0.ovapi.nl/stopareacode/' + stopCode;
  console.log('API URL: ' + url);
  
  ajax({
    url: url,
    type: 'json'
  }, function(data) {
    console.log('Received departure data');
    console.log('Response keys: ' + (data ? Object.keys(data).join(', ') : 'null'));
    
    var departures = [];
    
    // Parse the nested response structure: stopAreaCode → timingPoints → passes
    if (data && data[stopCode]) {
      var stopData = data[stopCode];
      console.log('Stop data has ' + Object.keys(stopData).length + ' timing points');
      
      // Iterate through timing points at this stop
      for (var timingPointCode in stopData) {
        var timingPoint = stopData[timingPointCode];
        
        // Check if this timing point has passes (departures)
        if (timingPoint && timingPoint.Passes) {
          var passCount = Object.keys(timingPoint.Passes).length;
          console.log('Found ' + passCount + ' passes in timing point: ' + timingPointCode);
          
          // Iterate through passes (departures)
          var processedPasses = 0;
          for (var passId in timingPoint.Passes) {
            var pass = timingPoint.Passes[passId];
            processedPasses++;
            
            if (pass) {
              // Log first pass to see structure
              if (processedPasses === 1) {
                console.log('First pass keys: ' + Object.keys(pass).join(', '));
                console.log('ExpectedDepartureTime: ' + pass.ExpectedDepartureTime);
                console.log('TargetDepartureTime: ' + pass.TargetDepartureTime);
              }
              
              // Use ExpectedDepartureTime if available, otherwise TargetDepartureTime
              var departureTime = pass.ExpectedDepartureTime || pass.TargetDepartureTime;
              
              if (departureTime) {
                var delay = 0;
                // Calculate delay only if both times are present and valid
                if (pass.ExpectedDepartureTime && pass.TargetDepartureTime) {
                  var expectedMs = Date.parse(pass.ExpectedDepartureTime);
                  var targetMs = Date.parse(pass.TargetDepartureTime);
                  if (!isNaN(expectedMs) && !isNaN(targetMs)) {
                    delay = Math.round((expectedMs - targetMs) / 60000);
                  }
                }
                
                departures.push({
                  line: pass.LinePublicNumber || 'Unknown',
                  headsign: pass.DestinationName50 || 'Unknown',
                  time: departureTime,
                  delay: delay,
                  type: pass.TransportType || 'BUS',
                  platform: timingPointCode
                });
              }
            }
          }
        }
      }
    } else {
      console.log('No data for stop code: ' + stopCode);
    }
    
    // Sort by time
    departures.sort(function(a, b) {
      return new Date(a.time) - new Date(b.time);
    });
    
    console.log('Found ' + departures.length + ' departures');
    console.log('Calling callback with departures...');
    
    if (departures.length === 0) {
      console.log('No departures found, calling callback with error');
      callback('No departures found for this stop');
    } else {
      console.log('Calling callback with ' + departures.slice(0, 10).length + ' departures');
      callback(null, departures.slice(0, 10)); // Return next 10
    }
    console.log('=== FETCH DEPARTURES END ===');
  }, function(error, status, request) {
    console.log('Departure API error: ' + JSON.stringify(error));
    console.log('Status: ' + status);
    console.log('URL: ' + url);
    callback('Failed to fetch departures: ' + (status || 'network error'));
  });
}

// Format time remaining until departure
function formatTimeRemaining(departureTime) {
  var now = new Date();
  var departure = new Date(departureTime);
  var minutes = Math.round((departure - now) / 60000);
  
  if (minutes < 1) {
    return 'Now';
  } else if (minutes === 1) {
    return '1 min';
  } else {
    return minutes + ' min';
  }
}

// Show departures in a menu
function showDepartures(stopName, departures, mainMenu, loadingCard) {
  console.log('=== SHOW DEPARTURES START ===');
  console.log('stopName: ' + stopName + ' (type: ' + typeof stopName + ')');
  console.log('departures: ' + (departures ? departures.length + ' items' : 'NULL/UNDEFINED'));
  console.log('mainMenu type: ' + typeof mainMenu);
  
  // Hide loading card before showing menu
  if (loadingCard) {
    loadingCard.hide();
  }
  
  if (!departures || !Array.isArray(departures)) {
    console.log('ERROR: departures is not an array!');
    showError('Display Error', 'Invalid departure data');
    return;
  }
  
  var menuItems = [];
  
  departures.forEach(function(dep) {
    var timeStr = formatTimeRemaining(dep.time);
    var delayStr = dep.delay > 0 ? ' (+' + dep.delay + ')' : '';
    
    menuItems.push({
      title: (dep.line || '?') + ' - ' + timeStr + delayStr,
      subtitle: dep.headsign || 'Unknown'
    });
  });
  
  var departureMenu = new UI.Menu({
    sections: [{
      title: stopName,
      items: menuItems
    }]
  });
  
  departureMenu.on('select', function(e) {
    // Show details
    var dep = departures[e.itemIndex];
    var detailCard = new UI.Card({
      title: 'Line ' + dep.line,
      subtitle: dep.headsign,
      body: 'Departs: ' + formatTimeRemaining(dep.time) + 
            (dep.delay > 0 ? '\nDelay: +' + dep.delay + ' min' : '\nOn time'),
      scrollable: true
    });
    detailCard.show();
    // Back button will automatically return to previous window (departureMenu)
  });
  
  // Back button will automatically return to previous window (mainMenu)
  
  departureMenu.show();
}

// Try to fetch departures from multiple stops until we find one with departures
function fetchDeparturesFromStops(stops, currentIndex, callback) {
  if (currentIndex >= stops.length) {
    var now = new Date();
    var timeStr = now.getHours() + ':' + (now.getMinutes() < 10 ? '0' : '') + now.getMinutes();
    callback('No departures found at ' + stops.length + ' nearby stops. This may be due to weekend/holiday schedule or off-peak hours (' + timeStr + ').');
    return;
  }
  
  var stop = stops[currentIndex];
  console.log('Trying stop ' + (currentIndex + 1) + '/' + stops.length + ': ' + stop.name);
  
  fetchDepartures(stop.code, stop.name, function(err, departures) {
    if (err) {
      // Try next stop
      console.log('No departures at ' + stop.name + ', trying next stop...');
      fetchDeparturesFromStops(stops, currentIndex + 1, callback);
    } else {
      // Found departures!
      callback(null, departures, stop.name);
    }
  });
}

// Show main menu with stops
function showMainMenu() {
  if (!appSettings.stops || appSettings.stops.length === 0) {
    // No stops configured
    var setupCard = new UI.Card({
      title: 'NextRide',
      subtitle: 'Setup Required',
      body: 'Open the Pebble app on your phone and configure your stops.',
      scrollable: true
    });
    setupCard.show();
    return;
  }
  
  // Build menu items from stops
  var menuItems = [];
  
  console.log('Building menu with ' + appSettings.stops.length + ' stops');
  
  // Add GPS option first
  var gpsItem = {
    title: String('Current Location'),
    subtitle: String('Use GPS')
  };
  console.log('Adding GPS item first: ' + JSON.stringify(gpsItem));
  menuItems.push(gpsItem);
  
  // Sort stops by order
  var sortedStops = appSettings.stops.slice().sort(function(a, b) {
    return (a.order || 0) - (b.order || 0);
  });
  
  console.log('Sorted stops: ' + sortedStops.length);
  
  // Add each stop - ensure all properties are strings
  sortedStops.forEach(function(stop, index) {
    console.log('Stop ' + index + ': ' + JSON.stringify(stop));
    var item = {
      title: String(stop.name || 'Unnamed Stop'),
      subtitle: String(stop.address || '')
    };
    console.log('Menu item: ' + JSON.stringify(item));
    menuItems.push(item);
  });
  
  console.log('Total menu items: ' + menuItems.length);
  
  // Create menu
  var mainMenu = new UI.Menu({
    sections: [{
      title: 'My Stops',
      items: menuItems
    }]
  });
  
  console.log('Menu created successfully');
  
  console.log('Menu created successfully');
  
  // Handle menu selection
  mainMenu.on('select', function(e) {
    console.log('=== MENU SELECTION START ===');
    console.log('Selected item title: ' + e.item.title);
    console.log('Selected item subtitle: ' + e.item.subtitle);
    console.log('Item index: ' + e.itemIndex);
    console.log('Total sorted stops: ' + sortedStops.length);
    
    var itemIndex = e.itemIndex;
    var isGPS = (e.item.title === 'Current Location');
    console.log('Is GPS selection: ' + isGPS);
    
    // Show loading card
    var loadingCard = new UI.Card({
      title: 'NextRide',
      body: isGPS ? 'Getting location...' : 'Finding stops...',
      scrollable: false
    });
    loadingCard.show();
    
    if (isGPS) {
      // Get GPS location
      getCurrentLocation(function(err, coords) {
        if (err) {
          showError('Location Error', err);
          return;
        }
        
        loadingCard.body('Finding nearby stops...');
        
        // Find nearby stops
        findNearbyStops(coords.lat, coords.lon, function(err, stops) {
          if (err) {
            showError('Stop Error', err);
            return;
          }
          
          loadingCard.body('Loading departures...');
          
          // Try to get departures from multiple stops until we find one with data
          fetchDeparturesFromStops(stops, 0, function(err, departures, stopName) {
            if (err) {
              showError('Departure Error', err);
              return;
            }
            
            showDepartures(stopName, departures, mainMenu, loadingCard);
          });
        });
      });
    } else {
      // Use saved stop (adjust index since GPS is now at position 0)
      var stopIndex = itemIndex - 1;
      console.log('Using saved stop at adjusted index: ' + stopIndex);
      var stop = sortedStops[stopIndex];
      console.log('Stop object: ' + JSON.stringify(stop));
      console.log('Stop has stopCode: ' + (stop.stopCode ? 'YES' : 'NO'));
      console.log('Stop has lat/lon: ' + (stop.lat && stop.lon ? 'YES' : 'NO'));
      
      // If stop has a direct stopCode (for testing), use it directly
      if (stop.stopCode) {
        console.log('Using direct stop code: ' + stop.stopCode);
        console.log('Stop name: ' + stop.name);
        loadingCard.body('Loading departures...');
        
        console.log('Calling fetchDepartures with stopCode=' + stop.stopCode + ', name=' + stop.name);
        fetchDepartures(stop.stopCode, stop.name, function(err, departures) {
          if (err) {
            showError('Departure Error', err);
            return;
          }
          
          showDepartures(stop.name, departures, mainMenu, loadingCard);
        });
      } else {
        // Find nearby stops for this location
        findNearbyStops(stop.lat, stop.lon, function(err, nearbyStops) {
          if (err) {
            showError('Stop Error', err);
            return;
          }
          
          loadingCard.body('Loading departures...');
          
          // Get departures for closest stop
          fetchDepartures(nearbyStops[0].code, nearbyStops[0].name, function(err, departures) {
            if (err) {
              showError('Departure Error', err);
              return;
            }
            
            showDepartures(nearbyStops[0].name, departures, mainMenu, loadingCard);
          });
        });
      }
    }
  });
  
  console.log('About to show main menu');
  mainMenu.show();
  console.log('Main menu shown');
}

// Initialize app
loadSettings();

// DEMO MODE: Set to true to test without config page
var DEMO_MODE = true;

// If no settings, either show setup card or load demo data
if ((!appSettings.stops || appSettings.stops.length === 0)) {
  if (DEMO_MODE) {
    console.log('DEMO MODE: Loading test data for Haarlem');
    
    // Demo data: Bus stops in Haarlem with live departures
    // Spaarnhovenstraat street exists but has no direct bus stop in OV API
    // Using nearby stops with current departures for testing
    appSettings.stops = [
      {
        id: 1,
        name: 'Byzantiumstraat',
        address: 'Haarlem (Residential area)',
        order: 1,
        lat: 52.37471,
        lon: 4.643629,
        stopCode: 'hlmbyz'  // 7 live departures
      },
      {
        id: 2,
        name: 'Nassaulaan',
        address: 'Near Haarlem Centraal Station',
        order: 2,
        lat: 52.383495,
        lon: 4.632862,
        stopCode: 'hlmnsl'  // 6 live departures, ~800m from station
      }
    ];
    appSettings.defaultStop = 'Nassaulaan';
    
    console.log('Loaded demo data: ' + appSettings.stops.length + ' stops');
    console.log('Demo stops use direct stop codes for testing');
  }
}

showMainMenu();
