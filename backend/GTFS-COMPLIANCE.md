# GTFS OV API Technical Usage Policy Compliance

## Overview
Our backend follows the [gtfs.ovapi.nl technical usage policy](https://gtfs.ovapi.nl/README) to be a good citizen of the Dutch transit data ecosystem.

## Implementation Details

### ✅ 1. User-Agent Identification (Required)
**Policy**: "Identify in the User-Agent header who you are, this helps us to contact you."

**Implementation**: 
```python
USER_AGENT = "NextRide-Pebble/1.0 (+https://davidenastri.it; contact@davidenastri.it)"
```

Sent with every request to identify our application and provide contact information.

### ✅ 2. HTTP Caching Headers (If-Modified-Since, If-None-Match)
**Policy**: "Implement HTTP Headers such as If-Modified-Since and/or If-None-Match"

**Implementation**:
- Store `Last-Modified` and `ETag` from responses in `data/gtfs-metadata.txt`
- Send `If-Modified-Since` and `If-None-Match` on subsequent requests
- Handle `304 Not Modified` responses (no download needed)

**Result**: Verified working - receives `304 Not Modified` when data unchanged

### ✅ 3. Update Frequency Alignment
**Policy**: "We rarely update our schedules more than daily and our new operational day starts at 03AM UTC"

**Implementation**:
- Cache TTL: 24 hours (checked once daily)
- GTFS file last updated: `06-Dec-2025 02:51` (daily at ~03:00 UTC)
- File size: ~260MB (compressed), not 1.2GB as initially thought

### ✅ 4. Rate Limiting Handling
**Policy**: Implicit - service implements rate limiting (429 responses)

**Implementation**:
- Exponential backoff: 5min, 10min, 15min waits
- Max 3 retries over 30 minutes
- User-friendly logging with tips about daily update schedule
- Graceful failure with informative error messages

## Testing Results

### Header Test (7 Dec 2025)
```
Request Headers:
  User-Agent: NextRide-Pebble/1.0 (+https://davidenastri.it; contact@davidenastri.it)
  If-Modified-Since: Fri, 06 Dec 2025 02:51:00 GMT

Response: 304 Not Modified
  ETag: "69338c39=1044a1e9"
```

✅ **Result**: Server correctly responds with 304 when data unchanged, saving bandwidth

## Benefits

1. **Bandwidth Efficiency**: ~260MB download avoided when data unchanged (304 responses)
2. **Good Citizenship**: Proper identification allows gtfs.ovapi.nl to contact us if needed
3. **Rate Limit Avoidance**: Daily checks align with their update schedule
4. **Reliability**: Exponential backoff handles transient rate limiting gracefully

## Maintenance Notes

- **Cache location**: `backend/data/gtfs-metadata.txt`
- **GTFS file**: `backend/data/gtfs-nl.zip` (~260MB)
- **Update schedule**: Daily at 03:00 UTC
- **Contact**: If gtfs.ovapi.nl contacts us, update `USER_AGENT` contact info in `config.py`

## Future Improvements

- [ ] Align cache expiry to 03:00 UTC specifically (currently checks 24h from last load)
- [ ] Add retry-after header parsing if provided by server
- [ ] Monitor and log cache hit rates (304 vs 200 responses)
- [ ] Consider scheduling automatic updates at 03:15 UTC via cron/systemd
