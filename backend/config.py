"""
Configuration for NextRide Backend API
Security and deployment settings
"""

import os
from typing import List


class Settings:
    """Application settings"""
    
    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")  # localhost by default
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security: CORS - Allowed origins
    ALLOWED_ORIGINS: List[str] = [
        "https://davidenastri.it",
        "http://davidenastri.it",
        "http://localhost:*",  # For local development
    ]
    
    # If DEBUG mode, allow all origins (development only)
    if DEBUG:
        ALLOWED_ORIGINS.append("*")
    
    # Data directories
    GTFS_DATA_DIR: str = os.getenv("GTFS_DATA_DIR", "./data")
    
    # GTFS download URL
    GTFS_URL: str = "http://gtfs.ovapi.nl/nl/gtfs-nl.zip"
    
    # User-Agent for gtfs.ovapi.nl (required by their technical usage policy)
    USER_AGENT: str = "NextRide-Pebble/1.0 (+https://davidenastri.it; contact@davidenastri.it)"
    
    # Cache settings
    # GTFS updates daily at 03:00 UTC, so check once per day
    CACHE_TTL_SECONDS: int = 86400  # 24 hours (align with daily updates)
    
    # Rate limiting (already handled in app.py)
    # These are just documentation
    RATE_LIMIT_SEARCH: str = "30/minute"
    RATE_LIMIT_NEARBY: str = "30/minute"
    RATE_LIMIT_DEPARTURES: str = "60/minute"
    RATE_LIMIT_GENERAL: str = "60/minute"


# Global settings instance
settings = Settings()
