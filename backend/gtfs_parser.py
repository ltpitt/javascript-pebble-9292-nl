"""
GTFS Parser for Dutch Public Transport Data
Downloads, parses, and indexes GTFS data for fast queries.
"""

import os
import zipfile
import csv
import requests
import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import math

from config import settings

logger = logging.getLogger(__name__)


class GTFSParser:
    """Parse and query GTFS data for Dutch public transport"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory indexes for fast queries
        self.stops: Dict[str, Dict] = {}  # stop_code -> stop info
        self.stop_times: Dict[str, List[Dict]] = {}  # stop_code -> list of departures
        
        self.gtfs_file = self.data_dir / "gtfs-nl.zip"
        self.metadata_file = self.data_dir / "gtfs-metadata.txt"
        self.last_download: Optional[datetime] = None
        self.last_modified: Optional[str] = None
        self.etag: Optional[str] = None
        
        # Load metadata if exists
        self._load_metadata()
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded GTFS data"""
        return {
            "stops_count": len(self.stops),
            "stops_with_schedule": len(self.stop_times),
            "last_download": self.last_download.isoformat() if self.last_download else None,
            "last_modified": self.last_modified,
            "etag": self.etag
        }
    
    def _load_metadata(self):
        """Load Last-Modified and ETag from previous download"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('Last-Modified:'):
                            self.last_modified = line.split(':', 1)[1].strip()
                        elif line.startswith('ETag:'):
                            self.etag = line.split(':', 1)[1].strip()
                        elif line.startswith('Downloaded:'):
                            date_str = line.split(':', 1)[1].strip()
                            self.last_download = datetime.fromisoformat(date_str)
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
    
    def _save_metadata(self, last_modified: str = None, etag: str = None):
        """Save Last-Modified and ETag for next request"""
        try:
            with open(self.metadata_file, 'w') as f:
                f.write(f"Downloaded: {datetime.now().isoformat()}\n")
                if last_modified:
                    f.write(f"Last-Modified: {last_modified}\n")
                    self.last_modified = last_modified
                if etag:
                    f.write(f"ETag: {etag}\n")
                    self.etag = etag
        except Exception as e:
            logger.warning(f"Could not save metadata: {e}")
    
    def load_data(self):
        """Load GTFS data - download if needed, then parse"""
        # Check if we need to download
        should_download = (
            not self.gtfs_file.exists() or
            self._is_cache_expired()
        )
        
        if should_download:
            logger.info("Downloading GTFS data...")
            self._download_gtfs()
        else:
            logger.info("Using cached GTFS data")
        
        # Parse the data
        logger.info("Parsing stops.txt...")
        self._parse_stops()
        
        logger.info("Parsing stop_times.txt (this takes a while)...")
        self._parse_stop_times()
        
        logger.info(f"✅ Loaded {len(self.stops)} stops with {len(self.stop_times)} having schedules")
    
    def _is_cache_expired(self) -> bool:
        """Check if cached GTFS file is too old"""
        if not self.gtfs_file.exists():
            return True
        
        file_age = datetime.now() - datetime.fromtimestamp(self.gtfs_file.stat().st_mtime)
        return file_age.total_seconds() > settings.CACHE_TTL_SECONDS
    
    def _download_gtfs(self):
        """
        Download GTFS ZIP file following gtfs.ovapi.nl technical usage policy:
        1. Identify with User-Agent header
        2. Use If-Modified-Since and If-None-Match for efficient caching
        3. Implement exponential backoff for rate limiting (5, 10, 15 min)
        
        Updates are daily at 03:00 UTC, so 304 Not Modified is expected most of the time.
        """
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            try:
                # Build headers following gtfs.ovapi.nl technical usage policy
                headers = {
                    'User-Agent': settings.USER_AGENT,  # Required: identify ourselves
                }
                
                # Add caching headers if we have them from previous download
                if self.last_modified:
                    headers['If-Modified-Since'] = self.last_modified
                if self.etag:
                    headers['If-None-Match'] = self.etag
                
                logger.info(f"Checking {settings.GTFS_URL}... (attempt {attempt + 1}/{max_retries + 1})")
                if self.last_modified:
                    logger.info(f"Using If-Modified-Since: {self.last_modified}")
                
                response = requests.get(settings.GTFS_URL, headers=headers, stream=True, timeout=300)
                
                # 304 Not Modified - no need to download
                if response.status_code == 304:
                    logger.info("✅ GTFS data is up-to-date (304 Not Modified)")
                    return
                
                # 429 Rate Limited - wait and retry
                if response.status_code == 429:
                    if attempt < max_retries:
                        wait_minutes = (attempt + 1) * 5  # 5, 10, 15 minutes
                        logger.warning(f"⏳ Rate limited (429). Waiting {wait_minutes} minutes before retry...")
                        logger.info("💡 Tip: GTFS updates once daily at 03:00 UTC. Check less frequently to avoid rate limits.")
                        time.sleep(wait_minutes * 60)
                        continue
                    else:
                        raise Exception(f"Rate limited after {max_retries} retries. Please try again later.")
                
                response.raise_for_status()
                
                # New data available - download it
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                logger.info(f"Downloading new GTFS data: {total_size / (1024*1024):.1f}MB...")
                
                with open(self.gtfs_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Log progress every 50MB
                            if downloaded % (50 * 1024 * 1024) < 8192:  # Within one chunk of 50MB
                                mb = downloaded / (1024 * 1024)
                                percent = (downloaded / total_size * 100) if total_size > 0 else 0
                                logger.info(f"Downloaded {mb:.0f}MB ({percent:.0f}%)...")
                
                # Save metadata for next request
                last_modified = response.headers.get('Last-Modified')
                etag = response.headers.get('ETag')
                self._save_metadata(last_modified, etag)
                
                self.last_download = datetime.now()
                logger.info(f"✅ Downloaded {downloaded / (1024*1024):.1f}MB successfully")
                return  # Success!
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Already handled above
                    continue
                logger.error(f"HTTP error downloading GTFS: {e}")
                raise
            except Exception as e:
                if attempt < max_retries and "429" in str(e):
                    wait_minutes = (attempt + 1) * 5
                    logger.warning(f"⏳ Download failed. Waiting {wait_minutes} minutes before retry...")
                    time.sleep(wait_minutes * 60)
                    continue
                logger.error(f"Failed to download GTFS: {e}")
                raise
    
    def _parse_stops(self):
        """Parse stops.txt from GTFS ZIP"""
        try:
            with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
                with zf.open('stops.txt', 'r') as f:
                    # Read as text
                    text_file = (line.decode('utf-8') for line in f)
                    reader = csv.DictReader(text_file)
                    
                    for row in reader:
                        stop_code = row.get('stop_code', '').strip().lower()
                        if not stop_code:
                            continue
                        
                        self.stops[stop_code] = {
                            'stop_id': row.get('stop_id', ''),
                            'stop_code': stop_code,
                            'stop_name': row.get('stop_name', ''),
                            'lat': float(row.get('stop_lat', 0)),
                            'lon': float(row.get('stop_lon', 0)),
                            'zone_id': row.get('zone_id', ''),
                            'stop_url': row.get('stop_url', ''),
                        }
            
            logger.info(f"Parsed {len(self.stops)} stops")
            
        except Exception as e:
            logger.error(f"Failed to parse stops.txt: {e}")
            raise
    
    def _parse_stop_times(self):
        """
        Parse stop_times.txt from GTFS ZIP
        WARNING: This is a 1.2GB file - indexing millions of departures
        
        Current strategy: Index first 2M rows (~1GB RAM) for broad coverage
        TODO: Implement SQLite database for production (proper indexing + date filtering)
        """
        try:
            logger.info("Indexing stop_times.txt (first 2M rows for broad coverage)...")
            logger.info("This will take 2-3 minutes and use ~1GB RAM")
            
            # Increased from 100k → 2M for proper coverage
            # 100k rows = ~497 stops (1%)
            # 2M rows = ~20,000-30,000 stops (50-70% coverage estimate)
            max_lines = 2_000_000
            parsed = 0
            
            with zipfile.ZipFile(self.gtfs_file, 'r') as zf:
                with zf.open('stop_times.txt', 'r') as f:
                    text_file = (line.decode('utf-8') for line in f)
                    reader = csv.DictReader(text_file)
                    
                    for row in reader:
                        if parsed >= max_lines:
                            break
                        
                        stop_id = row.get('stop_id', '').strip()
                        
                        # Find stop_code from stop_id
                        stop_code = self._get_stop_code_by_id(stop_id)
                        if not stop_code:
                            continue
                        
                        if stop_code not in self.stop_times:
                            self.stop_times[stop_code] = []
                        
                        self.stop_times[stop_code].append({
                            'trip_id': row.get('trip_id', ''),
                            'arrival_time': row.get('arrival_time', ''),
                            'departure_time': row.get('departure_time', ''),
                            'stop_sequence': int(row.get('stop_sequence', 0)),
                        })
                        
                        parsed += 1
                        
                        # Progress logging every 250k rows
                        if parsed % 250_000 == 0:
                            logger.info(f"  ... processed {parsed:,} rows, {len(self.stop_times):,} stops indexed so far")
            
            logger.info(f"✅ Indexed {parsed:,} stop times for {len(self.stop_times):,} stops")
            coverage_pct = (len(self.stop_times) / len(self.stops)) * 100 if self.stops else 0
            logger.info(f"📊 Coverage: {coverage_pct:.1f}% of all stops have schedule data")
            
        except Exception as e:
            logger.error(f"Failed to parse stop_times.txt: {e}")
            # Don't raise - app can still work for stop search
    
    def _get_stop_code_by_id(self, stop_id: str) -> Optional[str]:
        """Find stop_code by stop_id (reverse lookup)"""
        for stop_code, stop_info in self.stops.items():
            if stop_info['stop_id'] == stop_id:
                return stop_code
        return None
    
    def search_stops(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search stops by name or city
        Returns list of matching stops with their info
        """
        query_lower = query.lower()
        results = []
        
        for stop_code, stop in self.stops.items():
            stop_name = stop['stop_name'].lower()
            
            # Simple substring match (can be improved with fuzzy matching)
            if query_lower in stop_name:
                results.append({
                    'stop_code': stop_code,
                    'stop_name': stop['stop_name'],
                    'lat': stop['lat'],
                    'lon': stop['lon'],
                    'has_schedule': stop_code in self.stop_times
                })
                
                if len(results) >= limit:
                    break
        
        # Sort by relevance (exact match first, then alphabetical)
        results.sort(key=lambda x: (
            not x['stop_name'].lower().startswith(query_lower),
            x['stop_name']
        ))
        
        return results
    
    def find_nearby_stops(self, lat: float, lon: float, radius_meters: int, limit: int = 20) -> List[Dict]:
        """
        Find stops within radius of GPS coordinate
        Returns list of stops sorted by distance
        """
        results = []
        
        for stop_code, stop in self.stops.items():
            distance = self._calculate_distance(lat, lon, stop['lat'], stop['lon'])
            
            if distance <= radius_meters:
                results.append({
                    'stop_code': stop_code,
                    'stop_name': stop['stop_name'],
                    'lat': stop['lat'],
                    'lon': stop['lon'],
                    'distance_meters': round(distance),
                    'has_schedule': stop_code in self.stop_times
                })
        
        # Sort by distance
        results.sort(key=lambda x: x['distance_meters'])
        
        return results[:limit]
    
    def get_scheduled_departures(self, stop_code: str, limit: int = 10) -> List[Dict]:
        """
        Get scheduled departures for a stop
        Note: This is sample data - full implementation requires trip/route lookups
        """
        stop_code = stop_code.lower()
        
        if stop_code not in self.stop_times:
            return []
        
        departures = self.stop_times[stop_code][:limit]
        
        # Convert to user-friendly format
        results = []
        for dep in departures:
            results.append({
                'departure_time': dep['departure_time'],
                'trip_id': dep['trip_id'],
                'stop_sequence': dep['stop_sequence'],
                'note': 'Full trip details require trips.txt and routes.txt parsing'
            })
        
        return results
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in meters
        """
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
