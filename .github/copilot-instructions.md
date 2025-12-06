# NextRide for Pebble - Development Instructions

A Pebble.js smartwatch application for accessing Dutch public transport information via OV API (ovapi.nl).

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Prerequisites and Environment Setup
- Install Node.js and npm: `npm --version` (should show 10.8+)
- **Install Rebble SDK**: Follow official guide at `https://developer.repebble.com/sdk/`
- The new Rebble SDK replaces the old pebble-tool and provides local emulator support
- SDK includes `pebble` command-line tool for building and testing

### Project Structure Validation
- Always verify project structure first:
  ```bash
  ls -la
  # Expected: LICENSE, README.md, appinfo.json, resources/, src/, TASKS.md
  ```
- Validate appinfo.json: `cat appinfo.json | python3 -m json.tool`
- Validate JavaScript syntax: `node -c src/js/app.js`

### JavaScript Code Quality
- Install linting tools: `npm install --save-dev jshint eslint` -- takes 10-15 seconds
- Run JavaScript validation: `npx jshint src/js/app.js`
- Currently implementing fresh NextRide app - no legacy code issues

### Resources Status
All required resources are present:
- `resources/images/menu_icon.png` -- ✓ Present
- `resources/images/logo_splash.png` -- ✓ Present
- `resources/images/tile_splash.png` -- ✓ Present
- `resources/fonts/UbuntuMono-Regular.ttf` -- ✓ Present

### Build Process
Using the new Rebble SDK from `https://developer.repebble.com/sdk/`:

1. **Build the application** (expected time: 30-60 seconds):
   ```bash
   pebble build
   # Builds for all target platforms defined in appinfo.json
   ```

2. **Run in local emulator** (expected time: 10-15 seconds):
   ```bash
   pebble install --emulator basalt
   # Launches emulator and installs the app
   # Platforms: aplite, basalt, chalk, diorite, emery
   ```

3. **Package for distribution** (optional):
   ```bash
   pebble package
   # Creates a .pbw file for sideloading to physical watch
   ```

### Testing and Validation

#### JavaScript Validation (Always Works)
- **ALWAYS run before any changes**: `node -c src/js/app.js`
- **Check code quality**: `npx jshint src/js/app.js` 
- **Expected time**: 1-2 seconds

#### API Connectivity Testing
- **Test OV API accessibility**: `curl -I https://ovapi.nl/`
- The app uses ovapi.nl for real-time Dutch public transport data
- API is free and open, no authentication required

#### End-to-End Validation
Testing can be performed using the local Rebble emulator:
1. **Build and launch**: `pebble build && pebble install --emulator basalt`
2. **Test in emulator**: Use emulator's simulated location and network
3. **Manual testing**: Follow TASKS.md for test scenarios
4. **Physical device testing**: Optional - install .pbw on actual Pebble watch

### Development Workflow

#### Making Code Changes
1. **Check TASKS.md** for current task and success criteria
2. **ALWAYS validate syntax first**: `node -c src/js/app.js`
3. **Run linting**: `npx jshint src/js/app.js`
4. **Test building**: `pebble build`
5. **Test in emulator**: `pebble install --emulator basalt`
6. **Update TASKS.md** when task is complete

#### Development Approach
- Following TDD principles with manual testing
- Complete one task at a time from TASKS.md
- Test each task before moving to next
- Document any issues or API limitations discovered

#### Configuration Changes
- **App configuration**: Edit `appinfo.json` (validate with `python3 -m json.tool`)
- **Resource changes**: Update `resources/` directory and corresponding `appinfo.json` entries
- **Configuration page**: Edit `config.html` for user-facing settings
- **API endpoints**: OV API integration in `src/js/app.js`

### Common Tasks and Known Timings

#### Repository Operations (Always Work)
- **Repository exploration**: `find . -name "*.js" -o -name "*.json"` -- 1 second
- **Check file structure**: `ls -la resources/` -- instant
- **View source code**: `cat src/js/app.js` -- instant
- **Check tasks**: `cat TASKS.md` -- instant

#### Build Operations (Require Rebble SDK)
- **Clean build**: `pebble clean && pebble build` -- 30-60 seconds
- **Install to emulator**: `pebble install --emulator basalt` -- 10-20 seconds
- **Package for distribution**: `pebble package` -- 10-15 seconds

### Project Context and Architecture

#### Application Purpose
- **Transit Information**: Provides real-time departure information for Dutch public transport
- **User-Configurable**: Users set destinations via config page; can use GPS or saved locations
- **API Integration**: Uses OV API (ovapi.nl) for free, real-time transit data
- **Location Services**: Supports both GPS and manually configured addresses

#### Key Files and Their Purpose
- **`appinfo.json`**: Pebble app metadata, capabilities, and resource definitions
- **`src/js/app.js`**: Main application logic using Pebble.js APIs (ui, ajax, settings)
- **`src/js/main.js`**: Pebble.js framework loader
- **`src/main.c`**: Native C host for Pebble.js runtime
- **`config.html`**: Configuration page for user settings (opens on phone)
- **`TASKS.md`**: Development task tracking with success criteria
- **`LICENSE`**: MIT license
- **`README.md`**: Project documentation

#### Technical Dependencies
- **Pebble.js SDK 3**: JavaScript framework for Pebble development
- **OV API (ovapi.nl)**: Free, open Dutch public transport API
- **Node.js**: For JavaScript validation and tooling
- **Rebble SDK**: Official Pebble development toolkit

### Troubleshooting

#### Build Failures
- **Symptom**: `pebble build` fails
- **Solution**: Check appinfo.json syntax with `python3 -m json.tool appinfo.json`
- **Solution**: Validate JavaScript with `node -c src/js/app.js`
- **Check**: Ensure all resources referenced in appinfo.json exist

#### Emulator Issues
- **Symptom**: Emulator won't start
- **Solution**: Check Rebble SDK installation at `https://developer.repebble.com/sdk/`
- **Solution**: Try different platform: `pebble install --emulator aplite`
- **Logs**: Check emulator output for specific errors

#### API Connectivity Issues
- **Symptom**: OV API not accessible in emulator
- **Test**: `curl https://ovapi.nl/` from terminal
- **Note**: Emulator may need network configuration
- **Workaround**: Test with mock data first, then real API

#### JavaScript Errors
- **Symptom**: App crashes or behaves incorrectly
- **Debug**: Check emulator console/logs for JavaScript errors
- **Validate**: Run `npx jshint src/js/app.js` for code quality issues
- **Test**: Use console.log() statements for debugging

### CI/CD Considerations
Manual validation workflow for each change:
1. **Always run**: `node -c src/js/app.js` for syntax validation (1-2 seconds)
2. **Always run**: `npx jshint src/js/app.js` for code quality (1-2 seconds)
3. **Always run**: `pebble build` for full build validation (30-60 seconds)
4. **Test in emulator**: `pebble install --emulator basalt` (10-20 seconds)
5. **Manual testing**: Follow test steps in TASKS.md
6. **Expected total time**: 2-3 minutes per change cycle

### Development Best Practices
1. **Follow TASKS.md**: Work through tasks sequentially
2. **Test incrementally**: Don't accumulate untested changes
3. **Use emulator**: Test each feature as it's implemented
4. **Document issues**: Update TASKS.md with any problems discovered
5. **Validate before commit**: Always run full validation workflow
6. **Check logs**: Monitor emulator console for JavaScript errors