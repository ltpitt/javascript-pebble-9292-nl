# Documentation Index

⭐ **START HERE:** [OV-API-COMPLETE-GUIDE.md](OV-API-COMPLETE-GUIDE.md) - Complete verified guide (Dec 2025)

This directory contains all documentation related to the OV API research and testing for the NextRide Pebble application.

## 📚 Current Documentation

### ⭐ Authoritative Guide
- **[OV-API-COMPLETE-GUIDE.md](OV-API-COMPLETE-GUIDE.md)** - **USE THIS!** Complete, verified, tested guide
  - Real-time API (OV API v0) with working examples
  - GTFS scheduled data details
  - Verified test results from December 2025
  - Implementation strategies
  - Common pitfalls and solutions

### Quick Reference
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Quick curl commands (verified Dec 2025)

### Integration Example
- **[HOMEASSISTANT-OVAPI-INSTALL.md](HOMEASSISTANT-OVAPI-INSTALL.md)** - Home Assistant integration example

## 🎯 Key Findings (December 2025)

**Real-time API:**
```bash
curl "http://v0.ovapi.nl/stopareacode/hlmbyz"  # ✅ Returns 7+ live departures
```

**All stops:**
```bash
curl "http://v0.ovapi.nl/stopareacode"  # ✅ Returns 4,111 timing points
```

**GTFS complete data:**
```bash
curl "http://gtfs.ovapi.nl/nl/gtfs-nl.zip" -o gtfs.zip  # ✅ All stops + schedules
```

### Important Discoveries

✅ **Real-time data available** for ~4,111 timing points (major stops)  
⚠️ **Not all stops have real-time data** - small stops only in GTFS schedules  
✅ **App implementation correct** - works with timing points  
🔮 **GTFS integration optional** - for complete stop coverage (requires backend)

## 📖 Reading Order

1. **[OV-API-COMPLETE-GUIDE.md](OV-API-COMPLETE-GUIDE.md)** ⭐ Complete reference
2. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Quick commands
3. **[HOMEASSISTANT-OVAPI-INSTALL.md](HOMEASSISTANT-OVAPI-INSTALL.md)** - Integration example (optional)
| Authentication needed? | ❌ No (open API) |
| Working in app.js? | ✅ Yes (lines 185-245) |
| Can test in CI/CD? | ❌ No (DNS blocked) |
| Manual testing needed? | ✅ Yes |

## 🔗 External References

- **OV API Wiki:** https://github.com/koch-t/KV78Turbo-OVAPI/wiki
- **Working Example:** https://github.com/william-sy/ovapi
- **Base API:** http://v0.ovapi.nl/
- **GTFS Data:** http://gtfs.ovapi.nl/

---

Last Updated: December 6, 2025
