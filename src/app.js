    var ui = require('ui');
    var ajax = require('ajax');
    var vibe = require('ui/vibe');
    var settings = require('settings');
    var resultCard = new ui.Card();

    // Configuration for different API providers
    var API_CONFIG = {
        // Primary: 9292.nl API (requires subscription/API key)
        '9292': {
            name: '9292.nl Official API',
            baseUrl: 'https://api.9292.nl/0.1/',
            requiresAuth: true,
            enabled: false // Disabled until API key is configured
        },
        // Alternative: NS API for train data
        'ns': {
            name: 'NS (Dutch Railways) API',
            baseUrl: 'https://gateway.apiportal.ns.nl/',
            requiresAuth: true,
            enabled: false // Requires subscription
        },
        // Fallback: Mock data for demonstration
        'mock': {
            name: 'Demo Mode (Mock Data)',
            baseUrl: null,
            requiresAuth: false,
            enabled: true
        }
    };



    var trip = {
        destinations: [{
            title: "Home",
            subtitle: "Home sweet home"
        }, {
            title: "Work",
            subtitle: "It's off to work we go"
        }],
        configureSettings: function() {
            settings.config({
                    url: './config.html'
                },
                function(e) {
                    console.log('closed configurable');
                    console.log(JSON.stringify(e.options));
                    if (e.failed) {
                        console.log(e.response);
                    } else if (e.options) {
                        // Store API configuration from user settings
                        if (e.options.apiProvider) {
                            trip.setApiProvider(e.options.apiProvider);
                        }
                        if (e.options.apiKey) {
                            trip.setApiKey(e.options.apiKey);
                        }
                    }
                }
            );
        },
        
        setApiProvider: function(provider) {
            if (API_CONFIG[provider]) {
                this.currentProvider = provider;
                console.log('API provider set to: ' + provider);
            }
        },
        
        setApiKey: function(apiKey) {
            this.apiKey = apiKey;
            // Enable APIs that require authentication if key is provided
            if (apiKey) {
                API_CONFIG['9292'].enabled = true;
                API_CONFIG['ns'].enabled = true;
            }
        },
        
        getCurrentProvider: function() {
            return this.currentProvider || this.getFirstAvailableProvider();
        },
        
        getFirstAvailableProvider: function() {
            for (var provider in API_CONFIG) {
                if (API_CONFIG[provider].enabled) {
                    return provider;
                }
            }
            return 'mock'; // Fallback to mock if nothing else is available
        },
        showResultCard: function(coordinates, event) {
            var routeConfig;
            if (trip.destinations[event.itemIndex].title == 'Home') {
                resultCard.title('Home');
                routeConfig = {
                    departure: 'aalsmeer/bushalte-dorpsstraat',
                    destination: 'Haarlem Station',
                    departureName: 'Aalsmeer, Dorpsstraat',
                    destinationName: 'Haarlem Station'
                };
            } else {
                resultCard.title('Work');
                resultCard.icon('images/bus.png');
                routeConfig = {
                    departure: 'haarlem/bushalte-raaksbrug',
                    destination: 'Uithoorn Busstation', 
                    departureName: 'Haarlem, Raaksbrug',
                    destinationName: 'Uithoorn Busstation'
                };
            }
            trip.fetchDepartureData(routeConfig);
            resultCard.show();
        },
        
        fetchDepartureData: function(routeConfig) {
            var provider = this.getCurrentProvider();
            console.log('Using provider: ' + provider);
            
            resultCard.subtitle('Loading...');
            resultCard.body('Fetching data from ' + API_CONFIG[provider].name);
            
            switch(provider) {
                case '9292':
                    this.fetch9292Data(routeConfig);
                    break;
                case 'ns':
                    this.fetchNSData(routeConfig);
                    break;
                case 'mock':
                    this.fetchMockData(routeConfig);
                    break;
                default:
                    this.showError('No available data provider configured');
            }
        },
        
        fetch9292Data: function(routeConfig) {
            var apiUrl = API_CONFIG['9292'].baseUrl + 'locations/' + routeConfig.departure + '/departure-times?lang=en-GB';
            var headers = {};
            
            if (this.apiKey) {
                headers['Authorization'] = 'Bearer ' + this.apiKey;
            }
            
            this.makeApiRequest(apiUrl, headers, function(data) {
                trip.parse9292Response(data, routeConfig.destinationName);
            });
        },
        
        fetchNSData: function(routeConfig) {
            // NS API implementation would go here
            // This is a placeholder showing the structure
            this.showError('NS API integration not yet implemented. Please configure 9292.nl API key or use demo mode.');
        },
        
        fetchMockData: function(routeConfig) {
            // Simulate API delay
            setTimeout(function() {
                var mockDepartures = [
                    {
                        time: '14:25',
                        destinationName: routeConfig.destinationName,
                        realtimeText: '+2 min delay',
                        route: '300'
                    },
                    {
                        time: '14:40', 
                        destinationName: routeConfig.destinationName,
                        realtimeText: 'On time',
                        route: '300'
                    }
                ];
                
                trip.displayDeparture(mockDepartures[0]);
            }, 1000);
        },
        
        makeApiRequest: function(url, headers, successCallback) {
            ajax({
                url: url,
                type: 'json',
                headers: headers
            },
            successCallback,
            function(error) {
                console.log('API request failed: ' + error);
                trip.handleApiError(error);
            });
        },
        
        parse9292Response: function(data, targetDestination) {
            try {
                if (!data.tabs || !data.tabs[0] || !data.tabs[0].departures) {
                    throw new Error('Invalid API response format');
                }
                
                var departures = data.tabs[0].departures;
                var found = false;
                
                for (var i = 0; i < departures.length; i++) {
                    if (departures[i].destinationName == targetDestination) {
                        this.displayDeparture(departures[i]);
                        found = true;
                        break;
                    }
                }
                
                if (!found) {
                    this.showError('No departures found for ' + targetDestination);
                }
            } catch (e) {
                console.log('Error parsing response: ' + e.message);
                this.showError('Error parsing departure data');
            }
        },
        
        displayDeparture: function(departure) {
            resultCard.subtitle(departure.time);
            var delay = departure.realtimeText ? '\n' + departure.realtimeText : '';
            var route = departure.route ? ' (' + departure.route + ')' : '';
            resultCard.body(departure.destinationName + route + delay);
            vibe.vibrate('short');
        },
        
        handleApiError: function(error) {
            var provider = this.getCurrentProvider();
            
            if (provider !== 'mock') {
                // Try to fallback to mock data
                console.log('Falling back to demo mode due to API error');
                this.currentProvider = 'mock';
                resultCard.subtitle('API Error');
                resultCard.body('Switching to demo mode...');
                
                setTimeout(function() {
                    // Retry with mock data
                    trip.fetchMockData({
                        destinationName: 'Demo Destination'
                    });
                }, 2000);
            } else {
                this.showError('Demo mode failed. Please check configuration.');
            }
        },
        
        showError: function(message) {
            resultCard.subtitle('Error');
            resultCard.body(message + '\n\nTry configuring API access in settings.');
            vibe.vibrate('long');
        },
        getLocation: function(event) {
            var locationOptions = {
                enableHighAccuracy: true,
                maximumAge: 10000,
                timeout: 10000
            };

            function locationSuccess(pos) {
                console.log('lat= ' + pos.coords.latitude + ' lon= ' + pos.coords.longitude);
                trip.showResultCard(pos.coords.latitude + ',' + pos.coords.longitude, event);
            }

            function locationError(err) {
                console.log('location error (' + err.code + '): ' + err.message);
                trip.showError('Location access failed: ' + err.message);
            }
            navigator.geolocation.getCurrentPosition(locationSuccess, locationError, locationOptions);
        }
    };

    // Initialize the app
    var destinationsMenu = new ui.Menu({
        sections: [{
            title: 'Choose a destination',
            items: trip.destinations
        }]
    });

    // Add settings menu item
    destinationsMenu.section(0).items.push({
        title: 'Settings',
        subtitle: 'Configure API access'
    });

    destinationsMenu.on('select', function(event) {
        if (event.itemIndex < trip.destinations.length) {
            // Regular destination selected
            trip.showResultCard('0,0', event);
        } else {
            // Settings selected
            trip.configureSettings();
        }
    });

    destinationsMenu.show();