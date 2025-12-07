# Installing OVAPI Integration in Home Assistant

## Step 1: Access Your Home Assistant

You need to access your Home Assistant's file system. Choose your method:

### Option A: If you have SSH access
```bash
ssh your-homeassistant-hostname
```

### Option B: If you have Samba/Network share
Navigate to your HA config folder via file explorer

### Option C: Using the Terminal add-on
1. Install "Terminal & SSH" add-on from Supervisor → Add-on Store
2. Start it and open the web UI

## Step 2: Download the OVAPI Integration

In your Home Assistant terminal:

```bash
# Navigate to config directory
cd /config

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Clone the integration
cd custom_components
git clone https://github.com/william-sy/ovapi.git

# Verify installation
ls -la ovapi/
```

You should see files like:
- `__init__.py`
- `manifest.json`
- `config_flow.py`
- `sensor.py`

## Step 3: Restart Home Assistant

1. Go to Settings → System → Restart
2. Wait for HA to come back online (1-2 minutes)

## Step 4: Add the Integration

1. Go to **Settings → Devices & Services**
2. Click **+ ADD INTEGRATION** (bottom right)
3. Search for **"OVAPI"** or **"OVAPI Bus Information"**
4. Click on it

## Step 5: Configure Your Stop

### Option 1: Search for Stop (Recommended)
1. Select "Search for a stop"
2. Enter your stop name (e.g., "Amsterdam Centraal")
3. Select from results
4. Choose direction or "Both directions"
5. Configure:
   - **Line Number**: Leave empty for all lines, or enter specific line (e.g., "22")
   - **Destination**: Leave as "All destinations" or filter
   - **Walking Time**: Minutes to walk to stop (default: 5)
   - **Update Interval**: 60 seconds (default)

### Option 2: Manual Stop Code Entry
1. Select "Enter stop code manually"
2. Enter your stop code (e.g., "31000495")
   - Find codes at https://9292.nl or on physical stop signage
3. Configure same options as above

## Step 6: Find Your Stop Code (if needed)

### Method 1: Using 9292.nl
1. Go to https://9292.nl
2. Search for your stop
3. Look in the URL or page details for the stop code

### Method 2: Check Physical Stop
Some bus stops display their stop code on signage

### Method 3: Use the GTFS Data
The integration searches GTFS data automatically when you use the search feature

## Step 7: Check Your Sensors

After configuration, you'll get these sensors:

```
sensor.<stop_name>_current_bus
sensor.<stop_name>_next_bus
sensor.<stop_name>_current_bus_delay
sensor.<stop_name>_next_bus_delay
sensor.<stop_name>_current_bus_departure
sensor.<stop_name>_next_bus_departure
sensor.<stop_name>_time_to_leave
```

Example for stop "31000495":
```
sensor.bus_stop_31000495_current_bus
sensor.bus_stop_31000495_time_to_leave
```

## Step 8: Create a Dashboard Card

Add this to your dashboard:

```yaml
type: entities
title: Bus Departures
entities:
  - entity: sensor.bus_stop_31000495_current_bus
    name: Next Bus
  - entity: sensor.bus_stop_31000495_current_bus_departure
    name: Departs in
  - entity: sensor.bus_stop_31000495_current_bus_delay
    name: Delay
  - entity: sensor.bus_stop_31000495_time_to_leave
    name: Leave in
```

## Step 9: Use It in Your Pebble App

Once working in HA, expose it via:

### Option A: HA REST API
Your Pebble app can query:
```
GET http://your-ha-ip:8123/api/states/sensor.bus_stop_31000495_current_bus
Authorization: Bearer YOUR_LONG_LIVED_TOKEN
```

### Option B: Webhook/Automation
Create an automation that posts departure data to your Pebble app server

## Troubleshooting

### Integration Not Found After Restart
```bash
# Check if files are in correct location
ls -la /config/custom_components/ovapi/

# Check manifest.json exists
cat /config/custom_components/ovapi/manifest.json
```

### No Data Showing
- Verify your stop code is correct
- Check during peak hours (services may not run at night)
- Look at Home Assistant logs: Settings → System → Logs

### Stop Not Found in Search
- Not all stops are in GTFS database
- Try manual entry with stop code instead
- Example: Rotterdam Huslystraat (31002742) has real-time data but not in search

### Sensors Show "Unknown"
- Bus line might not be running at current time
- Check if filters (line number, destination) are too restrictive
- Wait a few minutes for first update

## Quick Installation Script

If you have SSH access, run this:

```bash
#!/bin/bash
cd /config
mkdir -p custom_components
cd custom_components
git clone https://github.com/william-sy/ovapi.git
echo "Installation complete! Now restart Home Assistant."
```

## Alternative: Manual File Copy

If git isn't available:

1. Download the zip: https://github.com/william-sy/ovapi/archive/refs/heads/main.zip
2. Extract it
3. Copy the `custom_components/ovapi` folder to your HA's `custom_components` directory
4. Restart HA

## Next Steps

After it's working in Home Assistant:
1. Note which stop codes work reliably
2. Use those stop codes in your Pebble app
3. Or create HA automation to push data to your app
4. Consider hosting your FastAPI server and using OVAPI data there

---

**Need help?** Check:
- Home Assistant logs: Settings → System → Logs
- Integration docs: https://github.com/william-sy/ovapi
- HA Community: https://community.home-assistant.io/
