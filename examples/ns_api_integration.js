// Example NS API Integration
// This file shows how to integrate with the Dutch Railways (NS) API
// as an alternative to the 9292.nl API

// NS API Configuration
const NS_API_CONFIG = {
    baseUrl: 'https://gateway.apiportal.ns.nl',
    endpoints: {
        stations: '/reisinformatie-api/api/v2/stations',
        departures: '/reisinformatie-api/api/v3/departures'
    }
};

// Example implementation for NS API integration
var nsApiIntegration = {
    
    // Find station code by name
    findStation: function(stationName, callback) {
        var url = NS_API_CONFIG.baseUrl + NS_API_CONFIG.endpoints.stations + 
                  '?q=' + encodeURIComponent(stationName);
        
        ajax({
            url: url,
            type: 'json',
            headers: {
                'Ocp-Apim-Subscription-Key': this.apiKey
            }
        },
        function(data) {
            if (data.payload && data.payload.length > 0) {
                callback(null, data.payload[0].code);
            } else {
                callback('Station not found');
            }
        },
        function(error) {
            callback('API error: ' + error);
        });
    },
    
    // Get departures for a station
    getDepartures: function(stationCode, callback) {
        var url = NS_API_CONFIG.baseUrl + NS_API_CONFIG.endpoints.departures + 
                  '?station=' + stationCode + '&maxJourneys=10';
        
        ajax({
            url: url,
            type: 'json',
            headers: {
                'Ocp-Apim-Subscription-Key': this.apiKey
            }
        },
        function(data) {
            if (data.payload && data.payload.departures) {
                callback(null, data.payload.departures);
            } else {
                callback('No departures found');
            }
        },
        function(error) {
            callback('API error: ' + error);
        });
    },
    
    // Convert NS departure format to app format
    formatDeparture: function(nsDeparture) {
        return {
            time: nsDeparture.plannedDateTime ? 
                  new Date(nsDeparture.plannedDateTime).toLocaleTimeString('en-GB', {
                      hour: '2-digit', 
                      minute: '2-digit'
                  }) : 'Unknown',
            destinationName: nsDeparture.direction || 'Unknown destination',
            realtimeText: nsDeparture.delay ? '+' + nsDeparture.delay + ' min' : 'On time',
            route: nsDeparture.name || 'Train',
            platform: nsDeparture.plannedTrack || null
        };
    },
    
    // Main method to get next departure
    getNextDeparture: function(fromStation, toDirection, callback) {
        var self = this;
        
        // First find the station code
        this.findStation(fromStation, function(error, stationCode) {
            if (error) {
                callback(error);
                return;
            }
            
            // Then get departures
            self.getDepartures(stationCode, function(error, departures) {
                if (error) {
                    callback(error);
                    return;
                }
                
                // Find departure towards the desired direction
                var matchingDeparture = null;
                for (var i = 0; i < departures.length; i++) {
                    if (departures[i].direction && 
                        departures[i].direction.toLowerCase().includes(toDirection.toLowerCase())) {
                        matchingDeparture = departures[i];
                        break;
                    }
                }
                
                if (matchingDeparture) {
                    callback(null, self.formatDeparture(matchingDeparture));
                } else {
                    callback('No departures found towards ' + toDirection);
                }
            });
        });
    }
};

// Integration example for the main app
function fetchNSData(routeConfig) {
    if (!this.apiKey) {
        this.showError('NS API key not configured');
        return;
    }
    
    nsApiIntegration.apiKey = this.apiKey;
    
    // Map our route config to NS stations
    var stationMappings = {
        'aalsmeer/bushalte-dorpsstraat': 'Aalsmeer', // Approximate - would need actual station
        'haarlem/bushalte-raaksbrug': 'Haarlem',
        'Haarlem Station': 'Haarlem',
        'Uithoorn Busstation': 'Amsterdam' // Approximate
    };
    
    var fromStation = stationMappings[routeConfig.departure] || routeConfig.departureName;
    var toDirection = stationMappings[routeConfig.destination] || routeConfig.destinationName;
    
    nsApiIntegration.getNextDeparture(fromStation, toDirection, function(error, departure) {
        if (error) {
            console.log('NS API error: ' + error);
            trip.handleApiError(error);
        } else {
            trip.displayDeparture(departure);
        }
    });
}

// Usage notes:
// 1. Get API key from https://apiportal.ns.nl/
// 2. Replace the fetchNSData function in the main app with this implementation
// 3. Update station mappings to match actual NS station codes
// 4. NS API only covers train services, not buses/trams