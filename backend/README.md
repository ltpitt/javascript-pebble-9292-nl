# NextRide Backend API

FastAPI backend service providing GTFS schedule data and stop search for Dutch public transport.

## Features

- ✅ **Security-first design**: Rate limiting, CORS, input validation
- ✅ **Read-only API**: No user data storage, completely stateless
- ✅ **GTFS data**: Downloads and parses Dutch public transport schedules
- ✅ **Fast search**: In-memory indexing for quick stop lookups
- ✅ **GPS-based search**: Find stops near any coordinate
- ✅ **Docker ready**: Easy deployment with Docker

## Security Features

1. **Rate Limiting**: Prevents API abuse
   - Search: 30 requests/minute
   - Departures: 60 requests/minute
   - General: 60 requests/minute

2. **CORS Protection**: Only allowed origins can access API

3. **Input Validation**: All inputs are sanitized and validated

4. **Security Headers**: X-Frame-Options, CSP, HSTS, etc.

5. **Read-only**: No POST/PUT/DELETE operations

6. **No Authentication**: Public data, no user tracking

## API Endpoints

### Search Stops
```bash
GET /api/stops/search?query=Haarlem&limit=10
```

Returns stops matching the search query.

### Nearby Stops
```bash
GET /api/stops/nearby?lat=52.38&lon=4.63&radius=1000&limit=10
```

Returns stops within radius (meters) of GPS coordinate.

### Get Departures
```bash
GET /api/stops/{stop_code}/departures?limit=10
```

Returns scheduled departures for a stop.

### Health Check
```bash
GET /health
```

Returns API health status.

## Installation

### Option 1: Docker (Recommended)

```bash
# Build image
cd backend
docker build -t nextride-backend .

# Run container
docker run -d \
  --name nextride-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  nextride-backend

# Check logs
docker logs -f nextride-backend
```

### Option 2: Direct Installation

```bash
# Install dependencies
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run server
python app.py

# Or with uvicorn directly
uvicorn app:app --host 127.0.0.1 --port 8000
```

## Configuration

Set environment variables:

```bash
# Server settings
export HOST="127.0.0.1"
export PORT="8000"
export DEBUG="false"

# Data directory
export GTFS_DATA_DIR="./data"
```

Or create a `.env` file (if using python-dotenv).

## Production Deployment

### With Nginx (HTTPS + Reverse Proxy)

```nginx
server {
    listen 443 ssl http2;
    server_name api.davidenastri.it;
    
    ssl_certificate /etc/letsencrypt/live/davidenastri.it/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/davidenastri.it/privkey.pem;
    
    location /nextride/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### As Systemd Service

Create `/etc/systemd/system/nextride-backend.service`:

```ini
[Unit]
Description=NextRide Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/nextride-backend
Environment="PATH=/var/www/nextride-backend/venv/bin"
ExecStart=/var/www/nextride-backend/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nextride-backend
sudo systemctl start nextride-backend
sudo systemctl status nextride-backend
```

## Performance Notes

### GTFS Data Loading

- **First startup**: Downloads ~1.2GB GTFS file (2-5 minutes)
- **Subsequent startups**: Uses cached file (~30 seconds to parse)
- **Memory usage**: ~500MB for stops index
- **Cache TTL**: 24 hours (refresh daily)

### Current Limitations

⚠️ **Stop Times Indexing**: Currently only indexes first 100k lines of stop_times.txt for memory efficiency. 

For production use, consider:
- SQLite database for full schedule storage
- PostgreSQL for better performance
- Redis for caching

### Scaling

For high traffic:
- Run multiple instances behind load balancer
- Use Redis for shared caching
- Move GTFS data to PostgreSQL
- Enable HTTP caching headers

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
export DEBUG=true
python app.py

# API documentation
open http://localhost:8000/docs
```

## Testing

```bash
# Test search
curl "http://localhost:8000/api/stops/search?query=Haarlem"

# Test nearby
curl "http://localhost:8000/api/stops/nearby?lat=52.38&lon=4.63&radius=1000"

# Test departures
curl "http://localhost:8000/api/stops/hlmcen/departures"

# Health check
curl "http://localhost:8000/health"
```

## Security Checklist

- [x] Rate limiting enabled
- [x] CORS configured for specific origins
- [x] Input validation on all endpoints
- [x] Security headers added
- [x] No sensitive data stored
- [x] Runs as non-root user (Docker)
- [x] HTTPS enforced in production
- [x] API docs disabled in production
- [ ] Consider adding IP allowlist for admin endpoints
- [ ] Consider adding API key for write operations (if added)

## Monitoring

Check logs:
```bash
# Docker
docker logs -f nextride-backend

# Systemd
sudo journalctl -u nextride-backend -f

# Health endpoint
curl http://localhost:8000/health
```

## Troubleshooting

### GTFS Download Fails
- Check internet connection
- Verify URL: http://gtfs.ovapi.nl/nl/gtfs-nl.zip
- Check disk space (need ~1.5GB free)

### High Memory Usage
- Stop times indexing loads sample data
- For full schedule, use database backend
- Increase Docker memory limit if needed

### API Returns 503
- GTFS data not loaded yet
- Check logs for download/parse errors
- Allow 2-5 minutes for first startup

## License

MIT License - See main repository LICENSE file

## Support

For issues related to:
- **GTFS data**: https://gtfs.ovapi.nl/
- **OV API**: https://github.com/koch-t/KV78Turbo-OVAPI/wiki
- **This backend**: Open issue in main repository
