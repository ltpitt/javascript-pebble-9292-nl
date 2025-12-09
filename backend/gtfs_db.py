"""
GTFS SQLite Database Parser
Efficient database-backed GTFS parsing for production use.

This replaces in-memory parsing with SQLite for:
- Full dataset support (all 1.3GB of stop_times.txt)
- Fast indexed queries
- Low memory footprint (~50MB vs 1GB+)
- Date-based filtering (only load relevant schedules)
"""

import csv
import logging
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

from config import settings

logger = logging.getLogger(__name__)


class GTFSDatabase:
    """SQLite-backed GTFS data store"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.gtfs_file = self.data_dir / "gtfs-nl.zip"
        self.db_file = self.data_dir / "gtfs.db"
        self.metadata_file = self.data_dir / "gtfs-metadata.txt"
        
        self.conn: Optional[sqlite3.Connection] = None
    
    def load_data(self):
        """Load GTFS data into SQLite database"""
        # Download GTFS if needed
        should_download = (
            not self.gtfs_file.exists() or
            self._is_cache_expired()
        )
        
        if should_download:
            logger.info("Downloading GTFS data...")
            self._download_gtfs()
        else:
            logger.info("Using cached GTFS data")
        
        # Check if DB needs rebuild
        should_rebuild = (
            not self.db_file.exists() or
            self._is_db_outdated()
        )
        
        if should_rebuild:
            logger.info("Building SQLite database from GTFS...")
            self._build_database()
        else:
            logger.info("Using existing SQLite database")
        
        # Connect to database
        self._connect()
        
        logger.info("✅ GTFS database ready")
    
    def _connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(str(self.db_file), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def _build_database(self):
        """Build SQLite database from GTFS ZIP"""
        # Remove old database
        if self.db_file.exists():
            self.db_file.unlink()
        
        # Create new database
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
        # Create tables with indexes
        logger.info("Creating database schema...")
        
        cursor.execute("""
            CREATE TABLE stops (
                stop_id TEXT PRIMARY KEY,
                stop_code TEXT,
                stop_name TEXT,
                stop_lat REAL,
                stop_lon REAL,
                zone_id TEXT,
                stop_url TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE stop_times (
                trip_id TEXT,
                arrival_time TEXT,
                departure_time TEXT,
                stop_id TEXT,
                stop_sequence INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE routes (
                route_id TEXT PRIMARY KEY,
                route_short_name TEXT,
                route_long_name TEXT,
                route_type INTEGER,
                route_color TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE trips (
                trip_id TEXT PRIMARY KEY,
                service_id TEXT,
                route_id TEXT,
                trip_headsign TEXT,
                trip_short_name TEXT,
                direction_id INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE calendar_dates (
                service_id TEXT,
                date TEXT,
                exception_type INTEGER
            )
        """)
        
        cursor.execute("CREATE INDEX idx_stop_code ON stops(stop_code)")
        cursor.execute("CREATE INDEX idx_stop_name ON stops(stop_name)")
        cursor.execute("CREATE INDEX idx_stop_times_stop_id ON stop_times(stop_id)")
        cursor.execute("CREATE INDEX idx_stop_times_departure ON stop_times(departure_time)")
        cursor.execute("CREATE INDEX idx_stop_times_trip_id ON stop_times(trip_id)")
        cursor.execute("CREATE INDEX idx_trips_service_id ON trips(service_id)")
        cursor.execute("CREATE INDEX idx_trips_route_id ON trips(route_id)")
        cursor.execute("CREATE INDEX idx_calendar_dates_lookup ON calendar_dates(service_id, date)")
        
        # Load stops.txt (fast - only 46k rows)
        logger.info("Loading stops.txt...")
        with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
            with zf.open('stops.txt', 'r') as f:
                text_file = (line.decode('utf-8') for line in f)
                reader = csv.DictReader(text_file)
                
                stops_data = []
                for row in reader:
                    stops_data.append((
                        row.get('stop_id', ''),
                        row.get('stop_code', '').strip().lower(),
                        row.get('stop_name', ''),
                        float(row.get('stop_lat', 0)),
                        float(row.get('stop_lon', 0)),
                        row.get('zone_id', ''),
                        row.get('stop_url', '')
                    ))
                
                cursor.executemany(
                    "INSERT INTO stops VALUES (?, ?, ?, ?, ?, ?, ?)",
                    stops_data
                )
                logger.info(f"✅ Loaded {len(stops_data):,} stops")
        
        # Load routes.txt (route names and numbers)
        logger.info("Loading routes.txt...")
        with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
            with zf.open('routes.txt', 'r') as f:
                text_file = (line.decode('utf-8') for line in f)
                reader = csv.DictReader(text_file)
                
                routes_data = []
                for row in reader:
                    routes_data.append((
                        row.get('route_id', ''),
                        row.get('route_short_name', ''),
                        row.get('route_long_name', ''),
                        int(row.get('route_type', 3)),
                        row.get('route_color', '')
                    ))
                
                cursor.executemany(
                    "INSERT INTO routes VALUES (?, ?, ?, ?, ?)",
                    routes_data
                )
                logger.info(f"✅ Loaded {len(routes_data):,} routes")
        
        # Load stop_times.txt (slow - millions of rows, use batch inserts)
        logger.info("Loading stop_times.txt (this takes 2-3 minutes)...")
        logger.info("💡 This is a one-time operation - subsequent starts will be instant")
        
        with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
            with zf.open('stop_times.txt', 'r') as f:
                text_file = (line.decode('utf-8') for line in f)
                reader = csv.DictReader(text_file)
                
                batch = []
                batch_size = 50000
                total = 0
                
                for row in reader:
                    batch.append((
                        row.get('trip_id', ''),
                        row.get('arrival_time', ''),
                        row.get('departure_time', ''),
                        row.get('stop_id', ''),
                        int(row.get('stop_sequence', 0))
                    ))
                    
                    if len(batch) >= batch_size:
                        cursor.executemany(
                            "INSERT INTO stop_times VALUES (?, ?, ?, ?, ?)",
                            batch
                        )
                        total += len(batch)
                        logger.info(f"  ... loaded {total:,} departures")
                        batch = []
                
                # Insert remaining
                if batch:
                    cursor.executemany(
                        "INSERT INTO stop_times VALUES (?, ?, ?, ?, ?)",
                        batch
                    )
                    total += len(batch)
                
                logger.info(f"✅ Loaded {total:,} scheduled departures")
        
        # Load trips.txt (maps trip_id to service_id + headsign)
        logger.info("Loading trips.txt...")
        with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
            with zf.open('trips.txt', 'r') as f:
                text_file = (line.decode('utf-8') for line in f)
                reader = csv.DictReader(text_file)
                
                batch = []
                batch_size = 50000
                total = 0
                
                for row in reader:
                    batch.append((
                        row.get('trip_id', ''),
                        row.get('service_id', ''),
                        row.get('route_id', ''),
                        row.get('trip_headsign', ''),
                        row.get('trip_short_name', ''),
                        int(row.get('direction_id', 0))
                    ))
                    
                    if len(batch) >= batch_size:
                        cursor.executemany(
                            "INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        total += len(batch)
                        logger.info(f"  ... loaded {total:,} trips")
                        batch = []
                
                if batch:
                    cursor.executemany(
                        "INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?)",
                        batch
                    )
                    total += len(batch)
                
                logger.info(f"✅ Loaded {total:,} trips")
        
        # Load calendar_dates.txt (service availability by date)
        logger.info("Loading calendar_dates.txt...")
        with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
            with zf.open('calendar_dates.txt', 'r') as f:
                text_file = (line.decode('utf-8') for line in f)
                reader = csv.DictReader(text_file)
                
                batch = []
                batch_size = 50000
                total = 0
                
                for row in reader:
                    batch.append((
                        row.get('service_id', ''),
                        row.get('date', ''),
                        int(row.get('exception_type', 1))
                    ))
                    
                    if len(batch) >= batch_size:
                        cursor.executemany(
                            "INSERT INTO calendar_dates VALUES (?, ?, ?)",
                            batch
                        )
                        total += len(batch)
                        logger.info(f"  ... loaded {total:,} calendar entries")
                        batch = []
                
                if batch:
                    cursor.executemany(
                        "INSERT INTO calendar_dates VALUES (?, ?, ?)",
                        batch
                    )
                    total += len(batch)
                
                logger.info(f"✅ Loaded {total:,} calendar entries")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database built successfully")
    
    def _is_db_outdated(self) -> bool:
        """Check if database is older than GTFS file"""
        if not self.db_file.exists():
            return True
        
        db_mtime = self.db_file.stat().st_mtime
        gtfs_mtime = self.gtfs_file.stat().st_mtime
        
        return gtfs_mtime > db_mtime
    
    def _is_cache_expired(self) -> bool:
        """Check if cached GTFS file is too old"""
        if not self.gtfs_file.exists():
            return True
        
        file_age = datetime.now() - datetime.fromtimestamp(self.gtfs_file.stat().st_mtime)
        return file_age.total_seconds() > settings.CACHE_TTL_SECONDS
    
    def _download_gtfs(self):
        """Download GTFS ZIP with proper etiquette"""
        # Load metadata for conditional requests
        etag = None
        last_modified = None
        
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('ETag:'):
                        etag = line.split(':', 1)[1].strip()
                    elif line.startswith('Last-Modified:'):
                        last_modified = line.split(':', 1)[1].strip()
        
        # Prepare headers
        headers = {'User-Agent': settings.USER_AGENT}
        if etag:
            headers['If-None-Match'] = etag
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        
        # Download
        response = requests.get(settings.GTFS_URL, headers=headers, stream=True)
        
        if response.status_code == 304:
            logger.info("GTFS file unchanged (304 Not Modified)")
            return
        
        if response.status_code != 200:
            raise Exception(f"Failed to download GTFS: HTTP {response.status_code}")
        
        # Save file
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(self.gtfs_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (50 * 1024 * 1024) == 0:
                        logger.info(f"  ... downloaded {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB")
        
        # Save metadata
        with open(self.metadata_file, 'w') as f:
            if 'ETag' in response.headers:
                f.write(f"ETag: {response.headers['ETag']}\n")
            if 'Last-Modified' in response.headers:
                f.write(f"Last-Modified: {response.headers['Last-Modified']}\n")
        
        logger.info(f"✅ Downloaded {total_size // (1024*1024)}MB")
    
    def search_stops(self, query: str, limit: int = 20) -> List[Dict]:
        """Search stops by name"""
        query_pattern = f"%{query.lower()}%"
        
        cursor = self.conn.execute("""
            SELECT 
                stop_code,
                stop_name,
                stop_lat,
                stop_lon,
                (SELECT COUNT(*) FROM stop_times WHERE stop_times.stop_id = stops.stop_id LIMIT 1) as has_schedule
            FROM stops
            WHERE LOWER(stop_name) LIKE ?
            ORDER BY stop_name
            LIMIT ?
        """, (query_pattern, limit))
        
        results = []
        for row in cursor:
            results.append({
                'stop_code': row['stop_code'],
                'stop_name': row['stop_name'],
                'lat': row['stop_lat'],
                'lon': row['stop_lon'],
                'has_schedule': row['has_schedule'] > 0
            })
        
        return results
    
    def get_scheduled_departures(self, stop_code: str, limit: int = 10) -> List[Dict]:
        """Get scheduled departures for a stop after current time, filtered by today's service"""
        from datetime import datetime
        
        # Find stop_id from stop_code
        cursor = self.conn.execute(
            "SELECT stop_id, stop_name FROM stops WHERE stop_code = ? LIMIT 1",
            (stop_code,)
        )
        row = cursor.fetchone()
        if not row:
            return []
        
        stop_id = row['stop_id']
        stop_name = row['stop_name']
        
        # Get current time and date
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        current_date = now.strftime('%Y%m%d')  # GTFS uses YYYYMMDD format
        
        # Get departures after current time with route and destination info
        # Join: stop_times -> trips -> routes + calendar_dates for active services
        cursor = self.conn.execute("""
            SELECT DISTINCT
                st.departure_time,
                st.arrival_time,
                r.route_short_name,
                r.route_long_name,
                r.route_type,
                t.trip_headsign,
                t.trip_short_name
            FROM stop_times st
            INNER JOIN trips t ON st.trip_id = t.trip_id
            INNER JOIN routes r ON t.route_id = r.route_id
            INNER JOIN calendar_dates cd ON t.service_id = cd.service_id
            WHERE st.stop_id = ?
            AND st.departure_time >= ?
            AND cd.date = ?
            AND cd.exception_type = 1
            ORDER BY st.departure_time
            LIMIT ?
        """, (stop_id, current_time, current_date, limit))
        
        results = []
        for row in cursor:
            # Determine transport mode from route_type
            # 0=Tram, 1=Metro, 2=Rail, 3=Bus, 4=Ferry, 5=Cable car, 6=Gondola, 7=Funicular
            route_type_names = {0: 'Tram', 1: 'Metro', 2: 'Train', 3: 'Bus', 4: 'Ferry', 
                               5: 'Cable Car', 6: 'Gondola', 7: 'Funicular'}
            mode = route_type_names.get(row['route_type'], 'Transit')
            
            results.append({
                'departure_time': row['departure_time'],
                'arrival_time': row['arrival_time'],
                'route_short_name': row['route_short_name'] or 'N/A',
                'route_long_name': row['route_long_name'] or '',
                'trip_headsign': row['trip_headsign'] or 'Unknown destination',
                'trip_short_name': row['trip_short_name'] or '',
                'mode': mode,
                'stop_name': stop_name
            })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM stops")
        stops_count = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(DISTINCT stop_id) FROM stop_times")
        stops_with_schedule = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM stop_times")
        total_departures = cursor.fetchone()[0]
        
        return {
            'stops_count': stops_count,
            'stops_with_schedule': stops_with_schedule,
            'total_departures': total_departures,
            'coverage_percent': round((stops_with_schedule / stops_count) * 100, 1) if stops_count > 0 else 0
        }
