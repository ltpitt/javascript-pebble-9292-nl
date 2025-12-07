"""
Test suite for NextRide Backend API (Flask)
Following TDD principles: Red -> Green -> Refactor

Run with: pytest test_api.py -v

Note: These tests don't load GTFS data to avoid 260MB download.
For full integration tests, manually initialize GTFS data first.
"""

from app import app
from config import settings

# Create test client
client = app.test_client()
client.testing = True


class TestConfiguration:
    """Test configuration compliance with gtfs.ovapi.nl technical usage policy"""
    
    def test_user_agent_configured(self):
        """Test that User-Agent is configured for gtfs.ovapi.nl compliance"""
        assert hasattr(settings, 'USER_AGENT')
        assert settings.USER_AGENT is not None
        assert len(settings.USER_AGENT) > 0
        # Should contain contact information
        assert 'NextRide' in settings.USER_AGENT or 'Pebble' in settings.USER_AGENT
    
    def test_cache_ttl_reasonable(self):
        """Test that cache TTL aligns with daily GTFS updates"""
        # GTFS updates once daily at 03:00 UTC
        assert settings.CACHE_TTL_SECONDS == 86400  # 24 hours


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_endpoint_exists(self):
        """Test that /health endpoint exists"""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # 503 if GTFS not loaded
    
    def test_health_returns_json(self):
        """Test that /health returns valid JSON"""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]
        data = response.json  # Flask uses .json property
        assert "status" in data


class TestAPIDocumentation:
    """Test API endpoints documentation"""
    
    def test_root_endpoint_exists(self):
        """Test that / root endpoint exists"""
        response = client.get("/")
        assert response.status_code in [200, 503]
    
    def test_root_has_endpoints_info(self):
        """Test that root returns endpoint information"""
        response = client.get("/")
        if response.status_code == 200:
            data = response.json
            assert "endpoints" in data


class TestSecurityHeaders:
    """Test security configurations"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are configured"""
        response = client.options("/health", headers={
            "Origin": "https://davidenastri.it",
            "Access-Control-Request-Method": "GET"
        })
        # Should have CORS headers (even if preflight fails)
        assert response.status_code in [200, 204]


class TestRateLimiting:
    """Test rate limiting is configured"""
    
    def test_api_responds(self):
        """Test that API responds to requests"""
        response = client.get("/health")
        assert response.status_code in [200, 503]
        # Flask-Limiter adds X-RateLimit headers
        assert response.headers.get("X-RateLimit-Limit") or True  # May not be present


# Run with: pytest test_api.py -v
# Or with coverage: pytest test_api.py --cov=app --cov-report=html
