"""
NextRide Backend API (Flask)
Provides GTFS schedule data and stop search for Dutch public transport.
Security-first, read-only, stateless API.

Following: KISS, DRY, Clean Code, Security-First principles
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime
from typing import Optional

from config import settings
from gtfs_parser import GTFSParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Security: CORS - only allow specific origins
CORS(app, 
     origins=settings.ALLOWED_ORIGINS,
     methods=["GET"],  # Read-only API
     allow_headers=["*"],
     max_age=3600)

# Security: Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://"
)

# Global GTFS parser instance
gtfs_parser: Optional[GTFSParser] = None


@app.before_request
def add_security_headers():
    """Add security headers to all responses"""
    pass  # Headers added in after_request


@app.after_request
def security_headers(response):
    """Add security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


def init_gtfs_data():
    """Initialize GTFS data on startup"""
    global gtfs_parser
    
    logger.info("Loading GTFS data (this may take a minute)...")
    
    try:
        gtfs_parser = GTFSParser(settings.GTFS_DATA_DIR)
        gtfs_parser.load_data()  # Synchronous - simpler!
        logger.info(f"✅ GTFS data loaded: {gtfs_parser.get_stats()}")
    except Exception as e:
        logger.error(f"❌ Failed to load GTFS data: {e}")
        # Don't fail startup, but API will return errors


@app.route("/")
@limiter.limit("60/minute")
def root():
    """API root - health check and info"""
    if not gtfs_parser:
        return jsonify({
            "status": "unavailable",
            "message": "GTFS data not loaded"
        }), 503
    
    return jsonify({
        "service": "NextRide Backend API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/stops/search?query=Haarlem",
            "nearby": "/api/stops/nearby?lat=52.38&lon=4.63&radius=1000",
            "departures": "/api/stops/{stop_code}/departures"
        },
        "stats": gtfs_parser.get_stats()
    })


@app.route("/health")
@limiter.limit("120/minute")
def health_check():
    """Health check endpoint for monitoring"""
    if not gtfs_parser:
        return jsonify({
            "status": "unhealthy",
            "reason": "GTFS data not loaded"
        }), 503
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/stops/search")
@limiter.limit("30/minute")
def search_stops():
    """
    Search for stops by name, city, or street.
    
    Example: /api/stops/search?query=Haarlem+Spaarn&limit=10
    """
    if not gtfs_parser:
        return jsonify({"error": "GTFS data not loaded"}), 503
    
    # Input validation
    query = request.args.get('query', '').strip()
    if not query or len(query) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400
    if len(query) > 100:
        return jsonify({"error": "Query too long (max 100 characters)"}), 400
    
    try:
        limit = int(request.args.get('limit', 20))
        if limit < 1 or limit > 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400
    
    try:
        logger.info(f"Search request: query='{query}', limit={limit}")
        
        results = gtfs_parser.search_stops(query, limit)
        
        return jsonify({
            "query": query,
            "count": len(results),
            "stops": results
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Search failed"}), 500


@app.route("/api/stops/nearby")
@limiter.limit("30/minute")
def nearby_stops():
    """
    Find stops near a GPS coordinate.
    
    Example: /api/stops/nearby?lat=52.38&lon=4.63&radius=1000&limit=10
    """
    if not gtfs_parser:
        return jsonify({"error": "GTFS data not loaded"}), 503
    
    # Input validation
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        
        if not (-90 <= lat <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90"}), 400
        if not (-180 <= lon <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180"}), 400
        
        radius = int(request.args.get('radius', 1000))
        if not (100 <= radius <= 10000):
            return jsonify({"error": "Radius must be between 100 and 10000 meters"}), 400
        
        limit = int(request.args.get('limit', 20))
        if not (1 <= limit <= 100):
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
            
    except (TypeError, ValueError) as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400
    
    try:
        logger.info(f"Nearby request: lat={lat}, lon={lon}, radius={radius}m")
        
        results = gtfs_parser.find_nearby_stops(lat, lon, radius, limit)
        
        return jsonify({
            "location": {"lat": lat, "lon": lon},
            "radius_meters": radius,
            "count": len(results),
            "stops": results
        })
    
    except Exception as e:
        logger.error(f"Nearby search error: {e}")
        return jsonify({"error": "Nearby search failed"}), 500


@app.route("/api/stops/<stop_code>/departures")
@limiter.limit("60/minute")
def get_departures(stop_code):
    """
    Get scheduled departures for a stop.
    Returns next departures from GTFS schedule (not real-time).
    
    Example: /api/stops/hlmcen/departures?limit=10
    """
    if not gtfs_parser:
        return jsonify({"error": "GTFS data not loaded"}), 503
    
    # Input validation
    stop_code = stop_code.strip().lower()
    if not stop_code.replace('_', '').replace('-', '').isalnum():
        return jsonify({"error": "Invalid stop code format"}), 400
    
    try:
        limit = int(request.args.get('limit', 10))
        if not (1 <= limit <= 50):
            return jsonify({"error": "Limit must be between 1 and 50"}), 400
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400
    
    try:
        logger.info(f"Departures request: stop_code={stop_code}, limit={limit}")
        
        departures = gtfs_parser.get_scheduled_departures(stop_code, limit)
        
        if not departures:
            return jsonify({
                "error": f"No scheduled departures found for stop '{stop_code}'"
            }), 404
        
        return jsonify({
            "stop_code": stop_code,
            "timestamp": datetime.now().isoformat(),
            "count": len(departures),
            "departures": departures,
            "note": "These are scheduled departures. Check OV API for real-time data."
        })
    
    except Exception as e:
        logger.error(f"Departures error: {e}")
        return jsonify({"error": "Failed to fetch departures"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Initialize GTFS data before starting server
    init_gtfs_data()
    
    # Run Flask development server
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )
