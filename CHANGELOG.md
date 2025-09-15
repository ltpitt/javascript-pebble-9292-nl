# Changelog

## Version 2.0.0 (2025) - API Migration Update

### 🚨 Breaking Changes
- **API Migration**: Original 9292.nl free API no longer available
- **Configuration Required**: Real-time data now requires paid API subscription

### ✨ New Features
- **Multi-Provider Support**: Flexible architecture supporting multiple data sources
- **Demo Mode**: Mock data for testing and demonstration without API requirements
- **Configuration UI**: Web-based settings interface for API configuration
- **Graceful Fallback**: Automatic fallback to demo mode when APIs fail
- **Enhanced Error Handling**: Better user feedback and error messages
- **Provider Abstraction**: Easy to add new data sources in future updates

### 🔧 Technical Improvements
- **Robust Architecture**: Improved code structure with separation of concerns
- **Error Recovery**: Comprehensive error handling with fallback mechanisms
- **Settings Persistence**: User preferences stored locally
- **API Abstraction**: Unified interface for different transport data providers

### 📱 User Experience
- **Settings Menu**: Added settings option in main menu
- **Status Indicators**: Clear indication of current data source
- **Informative Messages**: Better user feedback during loading and errors
- **Guidance**: Help text explaining API requirements and alternatives

### 🔌 API Integrations
- **9292.nl Official API**: Support for paid subscription service
- **NS API (Planned)**: Dutch Railways integration (in development)
- **Demo Mode**: Mock data for testing and demonstration

### 📋 Migration Guide
1. **Immediate Use**: App works in demo mode without configuration
2. **Real Data**: Configure 9292.nl API key if you have a subscription
3. **Future Options**: Additional free APIs will be added as available

### 🐛 Bug Fixes
- Fixed geolocation error handling
- Improved AJAX error handling
- Better handling of malformed API responses
- Fixed menu item selection logic

### 🚀 Future Roadmap
- NS API integration completion
- OpenOV/GTFS integration
- User-configurable routes
- Location-based stop discovery
- Multi-modal journey planning
- Offline/cached data support

---

## Version 1.0.0 (Original)
- Initial release with 9292.nl free API support
- Basic departure time display
- Hardcoded routes (Home/Work)
- Location services integration