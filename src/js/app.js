/**
 * NextRide - Dutch Public Transport App for Pebble
 * Shows real-time departure information for configured destinations
 */

var UI = require('ui');
var Settings = require('settings');
var ajax = require('ajax');
var Vector2 = require('vector2');

// Global settings storage
var appSettings = {
  defaultDestination: null,
  destinations: []
};

// Configure settings
Settings.config(
  { url: 'config.html' },
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
        appSettings.defaultDestination = settings.defaultDestination || null;
        appSettings.destinations = settings.destinations || [];
        
        // Save to persistent storage
        Settings.option('defaultDestination', appSettings.defaultDestination);
        Settings.option('destinations', appSettings.destinations);
        
        console.log('Saved ' + appSettings.destinations.length + ' destinations');
        console.log('Default destination: ' + appSettings.defaultDestination);
        
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
  appSettings.defaultDestination = Settings.option('defaultDestination') || null;
  appSettings.destinations = Settings.option('destinations') || [];
  
  console.log('Loaded settings on startup');
  console.log('Destinations: ' + appSettings.destinations.length);
  console.log('Default: ' + appSettings.defaultDestination);
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
  
  var url = 'http://v0.ovapi.nl/stopareacode';
  
  ajax({
    url: url,
    type: 'json'
  }, function(data) {
    console.log('Received stop data from OV API');
    console.log('Data keys: ' + Object.keys(data).length);
    
    // Find closest stops within 500m
    var nearbyStops = [];
    
    for (var stopCode in data) {
      if (data.hasOwnProperty(stopCode) && data[stopCode]) {
        var stop = data[stopCode];
        
        if (stop.Latitude && stop.Longitude) {
          var distance = calculateDistance(lat, lon, 
            parseFloat(stop.Latitude), 
            parseFloat(stop.Longitude)
          );
          
          if (distance < 0.5) { // Within 500m
            nearbyStops.push({
              code: stopCode,
              name: stop.TimingPointName || stopCode,
              distance: distance
            });
          }
        }
      }
    }
    
    // Sort by distance
    nearbyStops.sort(function(a, b) {
      return a.distance - b.distance;
    });
    
    console.log('Found ' + nearbyStops.length + ' nearby stops');
    
    if (nearbyStops.length === 0) {
      callback('No stops found nearby');
    } else {
      callback(null, nearbyStops.slice(0, 5)); // Return top 5
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

// Fetch departures for a stop
function fetchDepartures(stopCode, stopName, callback) {
  console.log('Fetching departures for: ' + stopCode);
  
  var url = 'http://v0.ovapi.nl/stopareacode/' + stopCode;
  
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
        if (stopData.hasOwnProperty(timingPointCode)) {
          var timingPoint = stopData[timingPointCode];
          
          // Check if this timing point has passes (departures)
          if (timingPoint && timingPoint.Passes) {
            console.log('Found passes in timing point: ' + timingPointCode);
            
            // Iterate through passes (departures)
            for (var passId in timingPoint.Passes) {
              if (timingPoint.Passes.hasOwnProperty(passId)) {
                var pass = timingPoint.Passes[passId];
                
                // Use ExpectedDepartureTime if available, otherwise TargetDepartureTime
                var departureTime = pass.ExpectedDepartureTime || pass.TargetDepartureTime;
                
                if (departureTime) {
                  var delay = 0;
                  if (pass.ExpectedDepartureTime && pass.TargetDepartureTime) {
                    delay = Math.round((new Date(pass.ExpectedDepartureTime) - 
                                       new Date(pass.TargetDepartureTime)) / 60000);
                  }
                  
                  departures.push({
                    line: pass.LinePublicNumber || 'Unknown',
                    destination: pass.DestinationName50 || 'Unknown',
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
      }
    } else {
      console.log('No data for stop code: ' + stopCode);
    }
    
    // Sort by time
    departures.sort(function(a, b) {
      return new Date(a.time) - new Date(b.time);
    });
    
    console.log('Found ' + departures.length + ' departures');
    
    if (departures.length === 0) {
      callback('No departures found for this stop');
    } else {
      callback(null, departures.slice(0, 10)); // Return next 10
    }
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
function showDepartures(stopName, departures, mainMenu) {
  var menuItems = [];
  
  departures.forEach(function(dep) {
    var timeStr = formatTimeRemaining(dep.time);
    var delayStr = dep.delay > 0 ? ' (+' + dep.delay + ')' : '';
    
    menuItems.push({
      title: dep.line + ' - ' + timeStr + delayStr,
      subtitle: dep.destination
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
      subtitle: dep.destination,
      body: 'Departs: ' + formatTimeRemaining(dep.time) + 
            (dep.delay > 0 ? '\nDelay: +' + dep.delay + ' min' : '\nOn time'),
      scrollable: true
    });
    detailCard.show();
    
    detailCard.on('click', 'back', function() {
      departureMenu.show();
    });
  });
  
  departureMenu.on('back', function() {
    mainMenu.show();
  });
  
  departureMenu.show();
}

// Show main menu with destinations
function showMainMenu() {
  if (!appSettings.destinations || appSettings.destinations.length === 0) {
    // No destinations configured
    var setupCard = new UI.Card({
      title: 'NextRide',
      subtitle: 'Setup Required',
      body: 'Open the Pebble app on your phone and configure your destinations.',
      scrollable: true
    });
    setupCard.show();
    return;
  }
  
  // Build menu items from destinations
  var menuItems = [];
  
  // Sort destinations by order
  var sortedDestinations = appSettings.destinations.slice().sort(function(a, b) {
    return a.order - b.order;
  });
  
  // Add each destination
  sortedDestinations.forEach(function(dest) {
    menuItems.push({
      title: dest.name,
      subtitle: dest.address
    });
  });
  
  // Add GPS option if not already in list
  menuItems.push({
    title: '📍 Current Location',
    subtitle: 'Use GPS'
  });
  
  // Create menu
  var mainMenu = new UI.Menu({
    sections: [{
      title: 'Select Destination',
      items: menuItems
    }]
  });
  
  // Handle menu selection
  mainMenu.on('select', function(e) {
    console.log('Selected: ' + e.item.title);
    
    var itemIndex = e.itemIndex;
    var isGPS = (e.item.title === '📍 Current Location');
    
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
          
          // Get departures for closest stop
          fetchDepartures(stops[0].code, stops[0].name, function(err, departures) {
            if (err) {
              showError('Departure Error', err);
              return;
            }
            
            showDepartures(stops[0].name, departures, mainMenu);
          });
        });
      });
    } else {
      // Use saved destination
      var dest = sortedDestinations[itemIndex];
      
      // Find nearby stops for this destination
      findNearbyStops(dest.lat, dest.lon, function(err, stops) {
        if (err) {
          showError('Stop Error', err);
          return;
        }
        
        loadingCard.body('Loading departures...');
        
        // Get departures for closest stop
        fetchDepartures(stops[0].code, stops[0].name, function(err, departures) {
          if (err) {
            showError('Departure Error', err);
            return;
          }
          
          showDepartures(stops[0].name, departures, mainMenu);
        });
      });
    }
  });
  
  mainMenu.show();
}

// Initialize app
loadSettings();

// If no settings and running in emulator, load test data
if ((!appSettings.destinations || appSettings.destinations.length === 0)) {
  console.log('No destinations found - loading test data for emulator');
  
  // Test data for emulator testing with real stop area codes
  appSettings.destinations = [
    {
      id: 1,
      name: 'Home',
      address: 'Amsterdam Centraal',
      order: 1,
      lat: 52.3791,
      lon: 4.9003
    },
    {
      id: 2,
      name: 'Office',
      address: 'Amsterdam Museumplein',
      order: 2,
      lat: 52.3579,
      lon: 4.8814
    }
  ];
  appSettings.defaultDestination = 'Home';
  
  console.log('Loaded test data: ' + appSettings.destinations.length + ' destinations');
}

showMainMenu();
