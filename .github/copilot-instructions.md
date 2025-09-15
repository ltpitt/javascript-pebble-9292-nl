# 9292.nl for Pebble - Development Instructions

A Pebble.js smartwatch application for accessing Dutch public transport information from the 9292.nl API.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Prerequisites and Environment Setup
- Install Python 3.12+ and pip3: `python3 --version` (should show 3.12+)
- Install Node.js and npm: `npm --version` (should show 10.8+)
- Install Pebble SDK: `pip3 install pebble-tool` -- **NOTE: This installation frequently fails due to network timeouts. NEVER CANCEL during installation attempts. Set timeout to 300+ seconds. If it fails, development can continue with limited functionality.**

### Project Structure Validation
- Always verify project structure first:
  ```bash
  cd /home/runner/work/javascript-pebble-9292-nl/javascript-pebble-9292-nl
  ls -la
  # Expected: LICENSE, README.md, appinfo.json, resources/, src/
  ```
- Validate appinfo.json: `cat appinfo.json | python3 -m json.tool`
- Validate JavaScript syntax: `node -c src/app.js`

### JavaScript Code Quality
- Install linting tools: `npm install --save-dev jslint jshint eslint` -- takes 10-15 seconds
- Run JavaScript validation: `npx jshint src/app.js`
- **KNOWN ISSUES in src/app.js (line numbers may vary):**
  - Line ~39: 'chosenDeparture' is already defined
  - Line ~40: 'chosenDestination' is already defined  
  - Line ~41: 'APIURL' is already defined
  - Line ~43: 'APIURL' used out of scope
  - Line ~43: 'chosenDestination' used out of scope
- **CRITICAL**: These JavaScript scope issues must be fixed before the app will function correctly

### Missing Resources Issue
The appinfo.json references resources that don't exist in the repository:
- `resources/images/menu_icon.png` -- **MISSING**
- `resources/images/logo_splash.png` -- **MISSING**  
- `resources/images/tile_splash.png` -- **MISSING**
- `resources/fonts/UbuntuMono-Regular.ttf` -- **MISSING**
- `resources/images/bus.png` -- ✓ Present (28x28 PNG)

**Before building:** Create placeholder images or update appinfo.json to remove references to missing files.

### Build Process
**WARNING**: Pebble SDK installation frequently fails due to network connectivity issues. The following represents the intended workflow when SDK is available:

1. **Install Pebble SDK** (expected time: 5-10 minutes, frequently fails):
   ```bash
   pip3 install pebble-tool
   # If this fails with timeout errors, try:
   # pip3 install --timeout=300 --retries=1 pebble-tool
   ```

2. **Build the application** (expected time: 30-60 seconds when SDK works):
   ```bash
   pebble build
   # NEVER CANCEL: Wait for completion even if it appears to hang
   ```

3. **Package for installation** (expected time: 10-15 seconds):
   ```bash
   pebble package
   # Creates a .pbw file for sideloading to watch
   ```

### Testing and Validation

#### JavaScript Validation (Always Works)
- **ALWAYS run before any changes**: `node -c src/app.js`
- **Check code quality**: `npx jshint src/app.js` 
- **Expected time**: 1-2 seconds

#### API Connectivity Testing (May Fail)
- **Test 9292 API accessibility**: `curl -I https://api.9292.nl/0.1/locations/`
- **NOTE**: This API may not be accessible from all environments
- The app uses endpoints like: `https://api.9292.nl/0.1/locations/{location}/departure-times?lang=en-GB`

#### End-to-End Validation
**CRITICAL**: Cannot be performed without Pebble hardware or emulator. Document that testing requires:
1. Pebble smartwatch paired with phone
2. Pebble app installed and configured
3. Location services enabled
4. Network connectivity for 9292.nl API

### Development Workflow

#### Making Code Changes
1. **ALWAYS validate syntax first**: `node -c src/app.js`
2. **Run linting**: `npx jshint src/app.js`
3. **Fix any JavaScript scope errors** (see Known Issues above)
4. **Test building** (if SDK available): `pebble build`
5. **NEVER CANCEL builds** - Pebble builds can take 60+ seconds

#### Required Fixes for Functionality
The application currently has JavaScript scope issues that prevent proper operation:
- Variables `chosenDeparture`, `chosenDestination`, and `APIURL` are redeclared
- Variables are used outside their scope
- These must be fixed by either using proper scope or renaming variables

#### Configuration Changes
- **App configuration**: Edit `appinfo.json` (validate with `python3 -m json.tool`)
- **Resource changes**: Update `resources/` directory and corresponding `appinfo.json` entries
- **API endpoints**: Modify API URLs in `src/app.js` (around lines 35 and 41)

### Common Tasks and Known Timings

#### Repository Operations (Always Work)
- **Repository exploration**: `find . -name "*.js" -o -name "*.json"` -- 1 second
- **Check file structure**: `ls -la resources/` -- instant
- **View source code**: `cat src/app.js` -- instant

#### Build Operations (Require SDK)
- **Clean build**: `pebble clean && pebble build` -- 60-90 seconds. NEVER CANCEL.
- **Package for distribution**: `pebble package` -- 10-15 seconds
- **Install to emulator**: `pebble install --emulator` -- 30-45 seconds

### Project Context and Architecture

#### Application Purpose
- **Transit Information**: Provides real-time departure information for Dutch public transport
- **Hardcoded Routes**: Currently configured for specific Aalsmeer/Haarlem routes
- **API Integration**: Uses 9292.nl REST API for live data
- **Location Services**: Can use GPS for location-based queries (disabled in current code)

#### Key Files and Their Purpose
- **`appinfo.json`**: Pebble app metadata, capabilities, and resource definitions
- **`src/app.js`**: Main application logic using Pebble.js APIs (ui, ajax, vibe, settings)
- **`resources/images/bus.png`**: Menu icon for the application
- **`LICENSE`**: MIT license
- **`README.md`**: Basic project description (minimal)

#### Technical Dependencies
- **Pebble.js SDK 3**: JavaScript framework for Pebble development
- **9292.nl API**: Dutch public transport information service
- **Node.js**: For JavaScript validation and tooling
- **Python 3**: For Pebble SDK installation and tooling

### Troubleshooting

#### SDK Installation Failures
- **Symptom**: `pip3 install pebble-tool` times out or fails
- **Cause**: Network connectivity issues to PyPI servers
- **Workaround**: Development can continue with JavaScript validation only
- **DO NOT**: Repeatedly cancel and retry - each attempt takes 5+ minutes

#### JavaScript Scope Errors
- **Symptom**: JSHint reports variable redefinition errors
- **Fix**: Rename variables or restructure scope in `src/app.js`
- **CRITICAL**: App will not function correctly with these errors

#### Missing Resources
- **Symptom**: appinfo.json references non-existent files
- **Fix**: Either create placeholder resources or remove references from appinfo.json
- **Note**: Only `bus.png` currently exists

#### API Connectivity Issues
- **Symptom**: 9292.nl API not accessible
- **Cause**: Network restrictions or API changes
- **Impact**: App will not display real transit data

### CI/CD Considerations
No automated build pipeline exists. Manual validation required:
1. **Always run**: `node -c src/app.js` for syntax validation
2. **Always run**: `npx jshint src/app.js` for code quality
3. **If SDK available**: `pebble build` for full build validation
4. **Expected total time**: 2-3 minutes for full validation

### Emergency Procedures
If Pebble SDK is completely unavailable:
1. **Continue development** using JavaScript validation only
2. **Use Node.js** for syntax checking: `node -c src/app.js`
3. **Use JSHint** for code quality: `npx jshint src/app.js`
4. **Document changes** for later testing when SDK becomes available
5. **DO NOT** attempt to modify build processes or create workarounds