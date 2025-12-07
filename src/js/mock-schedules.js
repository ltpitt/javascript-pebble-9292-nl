/**
 * Mock Schedule Data for NextRide MVP
 * 
 * Since OVAPI real-time is unreliable and GTFS requires server-side processing,
 * use static schedules based on typical timetables for major routes.
 * 
 * This provides a working demo and can be replaced with real API later.
 */

// Generate departures for next 2 hours based on frequency
function generateDepartures(baseTime, frequency, count) {
  var departures = [];
  var time = new Date(baseTime);
  
  for (var i = 0; i < count; i++) {
    departures.push(new Date(time));
    time = new Date(time.getTime() + frequency * 60000); // Add minutes
  }
  
  return departures;
}

// Get current time rounded to next 5 minutes
function getNextDepartureBase() {
  var now = new Date();
  var minutes = now.getMinutes();
  var roundedMinutes = Math.ceil(minutes / 5) * 5;
  now.setMinutes(roundedMinutes);
  now.setSeconds(0);
  now.setMilliseconds(0);
  return now;
}

// Mock schedules for major stops
var MOCK_SCHEDULES = {
  'asdcs': { // Amsterdam Centraal
    name: 'Amsterdam, Centraal Station',
    lines: [
      {
        line: '2',
        headsign: 'Nieuw Sloten',
        type: 'TRAM',
        frequency: 10, // Every 10 minutes
        peakHours: [7, 8, 9, 17, 18, 19] // Higher frequency during these hours
      },
      {
        line: '4',
        headsign: 'RAI Station',
        type: 'TRAM',
        frequency: 10
      },
      {
        line: '12',
        headsign: 'Station Sloterdijk',
        type: 'TRAM',
        frequency: 8
      },
      {
        line: '26',
        headsign: 'IJburg',
        type: 'TRAM',
        frequency: 12
      },
      {
        line: '48',
        headsign: 'Buikslotermeer',
        type: 'BUS',
        frequency: 15
      }
    ]
  },
  
  'utcs': { // Utrecht Centraal
    name: 'Utrecht, Centraal Station',
    lines: [
      {
        line: '2',
        headsign: 'P+R Westraven',
        type: 'TRAM',
        frequency: 10
      },
      {
        line: '3',
        headsign: 'Nieuwegein, Stadscentrum',
        type: 'TRAM',
        frequency: 15
      },
      {
        line: '12',
        headsign: 'Nieuwegein Zuid',
        type: 'BUS',
        frequency: 20
      }
    ]
  },
  
  'rtdcs': { // Rotterdam Centraal
    name: 'Rotterdam, Centraal Station',
    lines: [
      {
        line: '7',
        headsign: 'Woudestein',
        type: 'TRAM',
        frequency: 10
      },
      {
        line: '21',
        headsign: 'De Akkers',
        type: 'TRAM',
        frequency: 12
      },
      {
        line: '23',
        headsign: 'Beverwaard',
        type: 'TRAM',
        frequency: 15
      }
    ]
  },
  
  'gdacs': { // Den Haag Centraal
    name: 'Den Haag, Centraal Station',
    lines: [
      {
        line: '1',
        headsign: 'Delft Tanthof',
        type: 'TRAM',
        frequency: 10
      },
      {
        line: '9',
        headsign: 'Scheveningen',
        type: 'TRAM',
        frequency: 12
      },
      {
        line: '16',
        headsign: 'Wateringen',
        type: 'TRAM',
        frequency: 15
      }
    ]
  }
};

/**
 * Generate mock departures for a stop
 * @param {string} stopCode - Stop area code
 * @returns {Array} Array of departure objects
 */
function getMockDepartures(stopCode) {
  var schedule = MOCK_SCHEDULES[stopCode];
  if (!schedule) {
    console.log('No mock schedule for: ' + stopCode);
    return [];
  }
  
  var now = new Date();
  var currentHour = now.getHours();
  var baseTime = getNextDepartureBase();
  var allDepartures = [];
  
  // Generate departures for each line
  schedule.lines.forEach(function(line) {
    var frequency = line.frequency;
    
    // Increase frequency during peak hours
    if (line.peakHours && line.peakHours.indexOf(currentHour) !== -1) {
      frequency = Math.max(5, Math.floor(frequency * 0.7)); // 30% more frequent
    }
    
    // Generate next 2 hours of departures
    var departureTimes = generateDepartures(baseTime, frequency, 12);
    
    departureTimes.forEach(function(time) {
      // Add some random variation (-1 to +2 minutes)
      var variation = Math.floor(Math.random() * 4) - 1;
      var variedTime = new Date(time.getTime() + variation * 60000);
      
      allDepartures.push({
        stopName: schedule.name,
        line: line.line,
        headsign: line.headsign,
        time: variedTime.toISOString(),
        scheduledTime: time.toISOString(),
        delay: variation,
        type: line.type,
        operator: 'Mock',
        status: 'SCHEDULED'
      });
    });
  });
  
  // Sort by time
  allDepartures.sort(function(a, b) {
    return new Date(a.time) - new Date(b.time);
  });
  
  // Filter to only future departures
  allDepartures = allDepartures.filter(function(dep) {
    return new Date(dep.time) > now;
  });
  
  return allDepartures;
}

/**
 * Check if mock data is available for a stop
 */
function hasMockData(stopCode) {
  return MOCK_SCHEDULES.hasOwnProperty(stopCode);
}

/**
 * Get list of all stops with mock data
 */
function getMockStops() {
  var stops = [];
  for (var code in MOCK_SCHEDULES) {
    if (MOCK_SCHEDULES.hasOwnProperty(code)) {
      stops.push({
        code: code,
        name: MOCK_SCHEDULES[code].name,
        lineCount: MOCK_SCHEDULES[code].lines.length
      });
    }
  }
  return stops;
}

// Export functions
module.exports = {
  getMockDepartures: getMockDepartures,
  hasMockData: hasMockData,
  getMockStops: getMockStops
};
