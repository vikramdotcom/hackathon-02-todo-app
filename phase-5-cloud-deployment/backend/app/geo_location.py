"""
Geolocation and IP-based Services

Handle geolocation, IP lookup, and location-based features.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import ipaddress

logger = logging.getLogger(__name__)


class GeoLocation:
    """Geographic location data."""

    def __init__(
        self,
        ip: str,
        country: str,
        country_code: str,
        region: str,
        city: str,
        latitude: float,
        longitude: float,
        timezone: str,
        isp: Optional[str] = None
    ):
        """Initialize geolocation."""
        self.ip = ip
        self.country = country
        self.country_code = country_code
        self.region = region
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.isp = isp
        self.looked_up_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ip": self.ip,
            "country": self.country,
            "country_code": self.country_code,
            "region": self.region,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "isp": self.isp,
            "looked_up_at": self.looked_up_at.isoformat()
        }

    def distance_to(self, other: 'GeoLocation') -> float:
        """Calculate distance to another location in kilometers."""
        from math import radians, sin, cos, sqrt, atan2

        # Haversine formula
        R = 6371  # Earth's radius in kilometers

        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c


class IPValidator:
    """Validate and analyze IP addresses."""

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Check if IP is valid."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP is private."""
        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False

    @staticmethod
    def is_loopback(ip: str) -> bool:
        """Check if IP is loopback."""
        try:
            return ipaddress.ip_address(ip).is_loopback
        except ValueError:
            return False

    @staticmethod
    def get_ip_version(ip: str) -> Optional[int]:
        """Get IP version (4 or 6)."""
        try:
            addr = ipaddress.ip_address(ip)
            return addr.version
        except ValueError:
            return None

    @staticmethod
    def is_in_subnet(ip: str, subnet: str) -> bool:
        """Check if IP is in subnet."""
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)
        except ValueError:
            return False


class GeoLocationService:
    """Geolocation lookup service."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize geolocation service."""
        self.api_key = api_key
        self.cache: Dict[str, GeoLocation] = {}

    async def lookup(self, ip: str) -> Optional[GeoLocation]:
        """Lookup IP geolocation."""
        # Check cache
        if ip in self.cache:
            return self.cache[ip]

        # Validate IP
        if not IPValidator.is_valid_ip(ip):
            logger.warning(f"Invalid IP address: {ip}")
            return None

        # Skip private/loopback IPs
        if IPValidator.is_private_ip(ip) or IPValidator.is_loopback(ip):
            logger.info(f"Skipping private/loopback IP: {ip}")
            return None

        # In production, use a real geolocation API
        # For now, return mock data
        location = GeoLocation(
            ip=ip,
            country="United States",
            country_code="US",
            region="California",
            city="San Francisco",
            latitude=37.7749,
            longitude=-122.4194,
            timezone="America/Los_Angeles",
            isp="Example ISP"
        )

        # Cache result
        self.cache[ip] = location

        logger.info(f"Looked up geolocation for {ip}: {location.city}, {location.country}")

        return location

    async def lookup_batch(self, ips: list[str]) -> Dict[str, Optional[GeoLocation]]:
        """Lookup multiple IPs."""
        results = {}

        for ip in ips:
            results[ip] = await self.lookup(ip)

        return results

    def get_client_ip(self, request) -> Optional[str]:
        """Extract client IP from request."""
        # Check X-Forwarded-For header
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP in chain
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to remote address
        if hasattr(request, "client") and request.client:
            return request.client.host

        return None


class LocationBasedFeatures:
    """Location-based feature utilities."""

    def __init__(self, geo_service: GeoLocationService):
        """Initialize location features."""
        self.geo_service = geo_service

    async def get_timezone_for_ip(self, ip: str) -> Optional[str]:
        """Get timezone for IP."""
        location = await self.geo_service.lookup(ip)
        return location.timezone if location else None

    async def is_ip_in_country(self, ip: str, country_code: str) -> bool:
        """Check if IP is in country."""
        location = await self.geo_service.lookup(ip)
        return location.country_code == country_code if location else False

    async def is_ip_in_region(self, ip: str, region: str) -> bool:
        """Check if IP is in region."""
        location = await self.geo_service.lookup(ip)
        return location.region == region if location else False

    async def get_nearby_users(
        self,
        ip: str,
        max_distance_km: float = 100
    ) -> list[Dict[str, Any]]:
        """Get users near IP location."""
        location = await self.geo_service.lookup(ip)

        if not location:
            return []

        # In production, query database for users within distance
        # For now, return empty list
        return []

    async def suggest_locale(self, ip: str) -> str:
        """Suggest locale based on IP location."""
        location = await self.geo_service.lookup(ip)

        if not location:
            return "en"

        # Map country codes to locales
        locale_map = {
            "US": "en",
            "GB": "en",
            "CA": "en",
            "ES": "es",
            "MX": "es",
            "AR": "es",
            "FR": "fr",
            "BE": "fr",
            "CH": "fr"
        }

        return locale_map.get(location.country_code, "en")


class GeoFencing:
    """Geofencing utilities."""

    def __init__(self):
        """Initialize geofencing."""
        self.fences: Dict[str, Tuple[float, float, float]] = {}

    def create_fence(
        self,
        name: str,
        latitude: float,
        longitude: float,
        radius_km: float
    ):
        """Create geofence."""
        self.fences[name] = (latitude, longitude, radius_km)
        logger.info(f"Created geofence: {name} at ({latitude}, {longitude}) with radius {radius_km}km")

    def is_in_fence(self, name: str, location: GeoLocation) -> bool:
        """Check if location is in fence."""
        if name not in self.fences:
            return False

        fence_lat, fence_lon, radius = self.fences[name]

        fence_location = GeoLocation(
            ip="",
            country="",
            country_code="",
            region="",
            city="",
            latitude=fence_lat,
            longitude=fence_lon,
            timezone=""
        )

        distance = location.distance_to(fence_location)
        return distance <= radius

    def get_fences_for_location(self, location: GeoLocation) -> list[str]:
        """Get all fences containing location."""
        return [
            name for name in self.fences
            if self.is_in_fence(name, location)
        ]


# Global instances
geo_service = GeoLocationService()
location_features = LocationBasedFeatures(geo_service)
geo_fencing = GeoFencing()


# Helper functions
async def lookup_ip(ip: str) -> Optional[GeoLocation]:
    """Lookup IP geolocation."""
    return await geo_service.lookup(ip)


async def get_client_location(request) -> Optional[GeoLocation]:
    """Get client location from request."""
    ip = geo_service.get_client_ip(request)
    if ip:
        return await geo_service.lookup(ip)
    return None


async def suggest_locale_for_request(request) -> str:
    """Suggest locale for request."""
    ip = geo_service.get_client_ip(request)
    if ip:
        return await location_features.suggest_locale(ip)
    return "en"
