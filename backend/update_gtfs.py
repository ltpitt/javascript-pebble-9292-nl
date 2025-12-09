#!/usr/bin/env python3
"""
GTFS Update Script
Checks for new GTFS data, downloads if available, and rebuilds database.
Run daily via cron after 04:00 CET (after gtfs.ovapi.nl updates at 03:00 UTC)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config import settings
from gtfs_db import GTFSDatabase

# Configure logging
log_dir = backend_dir / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "gtfs-update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main update routine"""
    logger.info("=" * 60)
    logger.info(f"Starting GTFS update check at {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # Initialize database (will check for updates automatically)
        db = GTFSDatabase(settings.GTFS_DATA_DIR)
        
        # Check if we need to download
        data_dir = Path(settings.GTFS_DATA_DIR)
        gtfs_file = data_dir / "gtfs-nl.zip"
        db_file = data_dir / "gtfs.db"
        
        needs_download = not gtfs_file.exists() or db._is_cache_expired()
        needs_rebuild = not db_file.exists() or db._is_db_outdated()
        
        if needs_download:
            logger.info("📥 New GTFS data available, downloading...")
        else:
            logger.info("✓ GTFS data is up to date")
        
        if needs_rebuild:
            logger.info("🔨 Database rebuild required...")
        else:
            logger.info("✓ Database is current")
        
        if not needs_download and not needs_rebuild:
            logger.info("✅ No updates needed, exiting")
            return 0
        
        # Load data (downloads + rebuilds if needed)
        logger.info("Loading GTFS database...")
        db.load_data()
        
        # Get stats
        stats = db.get_stats()
        logger.info(f"✅ Update completed successfully!")
        logger.info(f"📊 Stats: {stats}")
        
        # Note about service restart
        logger.info("")
        logger.info("⚠️  Remember to restart Flask service:")
        logger.info("   pkill -f 'flask run' && nohup ./venv/bin/python -m flask run --host=0.0.0.0 --port=8000 &")
        logger.info("   OR: sudo systemctl restart nextride-backend")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Update failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
