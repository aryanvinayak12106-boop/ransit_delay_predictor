"""
Traffic Service Integration
TomTom Traffic API for real-time road conditions
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class TrafficService:
    """
    TomTom Traffic API client for road conditions
    Provides: Traffic flow, incidents (accidents, closures), congestion
    """
    
    def __init__(self):
        self.api_key = os.getenv('TOMTOM_API_KEY')
        self.base_url = "https://api.tomtom.com/traffic/services/5"
        self.timeout = 5
    
    async def get_traffic_density(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 2000
    ) -> float:
        """
        Get traffic density around a location (0.0-1.0)
        0.0 = no traffic, 1.0 = complete gridlock
        """
        try:
            if not self.api_key:
                logger.warning("TomTom API key not configured")
                return 0.5  # Default to medium traffic
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/flowSegmentData/absolute/10/png",
                    params={
                        'point': f"{latitude},{longitude}",
                        'zoom': 13,
                        'style': 'dark',
                        'key': self.api_key
                    }
                )
                response.raise_for_status()
            
            # TomTom returns congestion level (0-4)
            # We convert to 0.0-1.0 scale
            # This is simplified; actual implementation would parse response
            density = 0.5  # Default
            
            logger.info(f"Traffic density: {density:.2f}")
            return density
        
        except Exception as e:
            logger.error(f"Traffic API error: {e}")
            return 0.5
    
    async def get_incidents(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 5000
    ) -> Dict[str, Any]:
        """
        Get traffic incidents (accidents, closures, events)
        
        Returns:
        {
            'incidents': [
                {
                    'id': 'incident-123',
                    'type': 'accident',  # accident, road_closure, construction, event
                    'severity': 'high',  # low, medium, high, critical
                    'latitude': 12.9352,
                    'longitude': 77.6245,
                    'description': 'Traffic accident on NH7',
                    'impact_minutes': 25,
                    'distance_meters': 800
                }
            ],
            'count': 1
        }
        """
        try:
            if not self.api_key:
                return {'incidents': [], 'count': 0}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/incidentDetails",
                    params={
                        'point': f"{latitude},{longitude}",
                        'radius': radius_meters,
                        'key': self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            incidents = []
            for incident in data.get('incidents', []):
                incident_obj = {
                    'id': incident.get('id'),
                    'type': self._parse_incident_type(incident.get('type')),
                    'severity': self._parse_severity(incident.get('severity')),
                    'latitude': incident.get('geometry', {}).get('coordinates', [None, None])[1],
                    'longitude': incident.get('geometry', {}).get('coordinates', [None, None])[0],
                    'description': incident.get('description'),
                    'impact_minutes': self._estimate_impact(incident),
                    'distance_meters': self._calculate_distance(
                        latitude, longitude,
                        incident.get('geometry', {}).get('coordinates', [None, None])
                    )
                }
                incidents.append(incident_obj)
            
            logger.info(f"Found {len(incidents)} traffic incidents")
            return {
                'incidents': incidents,
                'count': len(incidents),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"Incidents API error: {e}")
            return {'incidents': [], 'count': 0}
    
    def _parse_incident_type(self, incident_type: str) -> str:
        """Map TomTom incident type to our domain"""
        mapping = {
            '1': 'accident',          # Accident
            '2': 'work',              # Work
            '3': 'congestion',        # Congestion
            '4': 'disabled_vehicle',  # Disabled vehicle
            '5': 'road_hazard',       # Road hazard
            '6': 'road_closure',      # Road closure
            '7': 'event',             # Event
            '8': 'weather',           # Weather
            '9': 'slow_traffic',      # Slow traffic
            '10': 'speed_enforcement' # Speed enforcement
        }
        return mapping.get(incident_type, 'unknown')
    
    def _parse_severity(self, severity: int) -> str:
        """Map TomTom severity to our scale"""
        severity_mapping = {
            '0': 'unknown',
            '1': 'low',
            '2': 'medium',
            '3': 'high',
            '4': 'critical'
        }
        return severity_mapping.get(str(severity), 'medium')
    
    def _estimate_impact(self, incident: Dict[str, Any]) -> int:
        """Estimate delay in minutes based on incident"""
        incident_type = self._parse_incident_type(incident.get('type'))
        severity = self._parse_severity(incident.get('severity'))
        
        base_impact = {
            'accident': 10,
            'work': 15,
            'congestion': 5,
            'road_closure': 30,
            'event': 20,
            'weather': 15
        }
        
        multiplier = {
            'low': 1,
            'medium': 1.5,
            'high': 2,
            'critical': 3
        }
        
        impact = base_impact.get(incident_type, 5)
        impact *= multiplier.get(severity, 1)
        
        return int(impact)
    
    def _calculate_distance(
        self,
        user_lat: float,
        user_lon: float,
        incident_coords: Tuple[float, float]
    ) -> int:
        """Calculate distance in meters"""
        if not incident_coords[0] or not incident_coords[1]:
            return float('inf')
        
        # Haversine formula simplified
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth's radius in meters
        
        lat1 = radians(user_lat)
        lon1 = radians(user_lon)
        lat2 = radians(incident_coords[1])
        lon2 = radians(incident_coords[0])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return int(R * c)
    
    async def get_traffic_flow(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get detailed traffic flow information
        
        Returns:
        {
            'avg_speed_kmh': 25,
            'free_flow_speed_kmh': 60,
            'congestion_level': 0.75,  # 0.0-1.0
            'event_rating': 4           # 0-4 scale
        }
        """
        try:
            if not self.api_key:
                return {
                    'avg_speed_kmh': 40,
                    'free_flow_speed_kmh': 60,
                    'congestion_level': 0.5,
                    'event_rating': 2
                }
            
            # Simplified; actual implementation would call API
            return {
                'avg_speed_kmh': 35,
                'free_flow_speed_kmh': 60,
                'congestion_level': 0.5,
                'event_rating': 2,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"Traffic flow error: {e}")
            return {}

# ============================================================================
# Singleton instance
# ============================================================================
_traffic_service_instance = None

def get_traffic_service() -> TrafficService:
    """Get or create singleton traffic service"""
    global _traffic_service_instance
    if _traffic_service_instance is None:
        _traffic_service_instance = TrafficService()
    return _traffic_service_instance
