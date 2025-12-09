# GTFS Auto-Update Setup

## Quick Setup

1. Make the update script executable:
```bash
chmod +x backend/update_gtfs.py
```

2. Add to crontab:
```bash
crontab -e
```

3. Add this line (runs daily at 04:30 CET):
```cron
30 3 * * * cd /path/to/javascript-pebble-9292-nl/backend && ./venv/bin/python update_gtfs.py >> logs/gtfs-cron.log 2>&1
```

**Important**: Replace `/path/to/` with your actual project path!

## With Automatic Service Restart

If you want the service to auto-restart after updates:

```cron
30 3 * * * cd /path/to/javascript-pebble-9292-nl/backend && ./update_gtfs.sh >> logs/gtfs-cron.log 2>&1
```

Create `backend/update_gtfs.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"

# Run update
./venv/bin/python update_gtfs.py

# If successful, restart Flask
if [ $? -eq 0 ]; then
    echo "Restarting Flask service..."
    pkill -f "flask run"
    sleep 2
    nohup ./venv/bin/python -m flask run --host=0.0.0.0 --port=8000 > logs/flask.log 2>&1 &
    echo "✅ Service restarted"
fi
```

Then:
```bash
chmod +x backend/update_gtfs.sh
```

## Systemd Service (Recommended for Production)

Create `/etc/systemd/system/nextride-backend.service`:
```ini
[Unit]
Description=NextRide Backend API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/javascript-pebble-9292-nl/backend
ExecStart=/path/to/javascript-pebble-9292-nl/backend/venv/bin/gunicorn -w 2 -b 0.0.0.0:8000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then update cron to restart service:
```bash
#!/bin/bash
cd "$(dirname "$0")"
./venv/bin/python update_gtfs.py
if [ $? -eq 0 ]; then
    sudo systemctl restart nextride-backend
fi
```

Enable and start:
```bash
sudo systemctl enable nextride-backend
sudo systemctl start nextride-backend
```

## Manual Update

Run anytime:
```bash
cd backend
./venv/bin/python update_gtfs.py
```

## Check Logs

```bash
tail -f backend/logs/gtfs-update.log
tail -f backend/logs/gtfs-cron.log
```

## Verify Cron is Running

```bash
crontab -l  # List your cron jobs
grep CRON /var/log/syslog  # Check cron execution logs
```

## Timing

- GTFS updates: **03:00 UTC** daily (04:00 CET winter, 05:00 CEST summer)
- Recommended cron: **03:30 UTC** (30 min buffer)
- Your cron: **04:30 CET** (safe, 1.5 hours after update)
