"""
Supabase Database Client Service
Handles all database operations with async/await pattern
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
import logging
from supabase import create_client, Client
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SupabaseService:
    """Async Supabase database service"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            result = await asyncio.to_thread(
                self.client.table('stops').select('id').limit(1).execute
            )
            return {
                "status": "healthy",
                "connected": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    # ========================================================================
    # STOPS OPERATIONS
    # ========================================================================
    
    async def get_nearby_stops(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 1000
    ) -> List[Dict]:
        """
        Get all stops within radius using PostGIS
        
        Query: SELECT * FROM stops 
               WHERE ST_DWithin(location, ST_Point(lon, lat), radius)
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.rpc(
                    'get_nearby_stops',
                    {
                        'p_latitude': latitude,
                        'p_longitude': longitude,
                        'p_radius_meters': radius_meters
                    }
                ).execute()
            )
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error fetching nearby stops: {e}")
            return []
    
    async def get_stop_by_id(self, stop_id: int) -> Optional[Dict]:
        """Get specific stop details"""
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table('stops')
                    .select('*')
                    .eq('id', stop_id)
                    .single()
                    .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error fetching stop {stop_id}: {e}")
            return None
    
    # ========================================================================
    # WEATHER & TRAFFIC DATA
    # ========================================================================
    
    async def get_weather_for_location(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Fetch cached weather data from database
        If not fresh, fetch from OpenWeatherMap
        """
        try:
            # Try to get cached weather (less than 30 min old)
            cache_threshold = datetime.utcnow() - timedelta(minutes=30)
            
            result = await asyncio.to_thread(
                lambda: self.client.table('weather_cache')
                    .select('*')
                    .gte('updated_at', cache_threshold.isoformat())
                    .order('updated_at', desc=True)
                    .limit(1)
                    .execute()
            )
            
            if result.data:
                return result.data[0]
            
            # Fetch from OpenWeatherMap if cache miss
            from app.services.weather_service import WeatherService
            weather = await WeatherService().get_weather(latitude, longitude)
            
            # Cache it
            await self.cache_weather(latitude, longitude, weather)
            
            return weather
        
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return {"temperature": 28, "condition": "unknown", "confidence": 0.5}
    
    async def cache_weather(
        self,
        latitude: float,
        longitude: float,
        weather_data: Dict
    ):
        """Cache weather data in database"""
        try:
            await asyncio.to_thread(
                lambda: self.client.table('weather_cache')
                    .upsert({
                        'latitude': latitude,
                        'longitude': longitude,
                        'temperature': weather_data.get('temperature'),
                        'condition': weather_data.get('condition'),
                        'precipitation_mm': weather_data.get('precipitation_mm'),
                        'updated_at': datetime.utcnow().isoformat()
                    })
                    .execute()
            )
        except Exception as e:
            logger.warning(f"Could not cache weather: {e}")
    
    # ========================================================================
    # USER REPORTS (CROWDSOURCING)
    # ========================================================================
    
    async def create_user_report(
        self,
        stop_id: int,
        user_id: str,
        delay_minutes: int,
        weather_condition: Optional[str] = None,
        confidence_rating: Optional[float] = None,
        notes: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict:
        """
        Create a user report
        Database trigger will check: if 5+ reports in 10 min, set is_verified
        """
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table('user_reports')
                    .insert({
                        'stop_id': stop_id,
                        'user_id': user_id,
                        'reported_delay_minutes': delay_minutes,
                        'weather_condition': weather_condition,
                        'accuracy_rating': confidence_rating,
                        'notes': notes,
                        'report_latitude': latitude,
                        'report_longitude': longitude,
                        'source_app': 'transit_x_vercel',
                        'created_at': datetime.utcnow().isoformat()
                    })
                    .execute()
            )
            
            logger.info(f"Report created for stop {stop_id}")
            return result.data[0] if result.data else {}
        
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise
    
    # ========================================================================
    # VERIFIED DELAYS (REAL-TIME)
    # ========================================================================
    
    async def get_active_verified_delays(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_meters: int = 5000
    ) -> List[Dict]:
        """
        Get all currently active, verified delays
        Query uses: get_active_verified_delays() PostGIS function
        """
        try:
            if latitude and longitude:
                # Query with location filter
                result = await asyncio.to_thread(
                    lambda: self.client.rpc(
                        'get_active_verified_delays_nearby',
                        {
                            'p_latitude': latitude,
                            'p_longitude': longitude,
                            'p_radius_meters': radius_meters
                        }
                    ).execute()
                )
            else:
                # Query all verified delays
                result = await asyncio.to_thread(
                    lambda: self.client.table('verified_delays')
                        .select('*')
                        .eq('is_verified', True)
                        .is_('resolved_at', None)
                        .gt('updated_at', (datetime.utcnow() - timedelta(minutes=30)).isoformat())
                        .order('verification_confidence_score', desc=True)
                        .execute()
                )
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error fetching verified delays: {e}")
            return []
    
    # ========================================================================
    # FLOOD ZONES
    # ========================================================================
    
    async def get_flood_zones_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 10000
    ) -> List[Dict]:
        """Get flood zones near a location"""
        try:
            result = await asyncio.to_thread(
                lambda: self.client.rpc(
                    'get_nearby_flood_zones',
                    {
                        'p_latitude': latitude,
                        'p_longitude': longitude,
                        'p_radius_meters': radius_meters
                    }
                ).execute()
            )
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error fetching flood zones: {e}")
            return []
    
    async def get_active_flood_zones(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_meters: int = 10000
    ) -> List[Dict]:
        """Get currently active flood warnings"""
        try:
            # Query flood zones with current water level > critical level
            result = await asyncio.to_thread(
                lambda: self.client.table('flood_prone_zones')
                    .select('*')
                    .gt('current_water_level_cm', 'critical_water_level_cm')
                    .order('current_water_level_cm', desc=True)
                    .execute()
            )
            
            zones = result.data if result.data else []
            
            # Filter by location if provided
            if latitude and longitude:
                from geopy.distance import geodesic
                filtered = []
                for zone in zones:
                    # Get zone centroid from geometry
                    dist = geodesic(
                        (latitude, longitude),
                        (zone.get('center_lat'), zone.get('center_lon'))
                    ).meters
                    
                    if dist <= radius_meters:
                        filtered.append(zone)
                
                zones = filtered
            
            return zones
        
        except Exception as e:
            logger.error(f"Error fetching active flood zones: {e}")
            return []
    
    # ========================================================================
    # NOTIFICATIONS
    # ========================================================================
    
    async def get_pending_notifications(self, user_id: str) -> List[Dict]:
        """Get pending notifications for a user"""
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table('notification_queue')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('status', 'pending')
                    .order('created_at', desc=True)
                    .limit(20)
                    .execute()
            )
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []
    
    async def queue_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        stop_id: Optional[int] = None,
        deep_link: Optional[str] = None
    ) -> Dict:
        """Queue a notification for OneSignal delivery"""
        try:
            result = await asyncio.to_thread(
                lambda: self.client.table('notification_queue')
                    .insert({
                        'user_id': user_id,
                        'notification_type': notification_type,
                        'title': title,
                        'message': message,
                        'stop_id': stop_id,
                        'deep_link': deep_link,
                        'status': 'pending',
                        'created_at': datetime.utcnow().isoformat()
                    })
                    .execute()
            )
            
            return result.data[0] if result.data else {}
        
        except Exception as e:
            logger.error(f"Error queuing notification: {e}")
            raise
    
    # ========================================================================
    # API METRICS LOGGING
    # ========================================================================
    
    async def log_api_call(
        self,
        api_provider: str,
        response_time_ms: int,
        is_successful: bool,
        data_freshness_seconds: Optional[int] = None,
        confidence_score: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """Log API call metrics for monitoring"""
        try:
            await asyncio.to_thread(
                lambda: self.client.table('api_call_metrics')
                    .insert({
                        'api_provider': api_provider,
                        'response_time_ms': response_time_ms,
                        'is_successful': is_successful,
                        'data_freshness_seconds': data_freshness_seconds,
                        'confidence_score': confidence_score,
                        'error_message': error_message,
                        'created_at': datetime.utcnow().isoformat()
                    })
                    .execute()
            )
        except Exception as e:
            logger.warning(f"Could not log API metrics: {e}")

# ============================================================================
# Singleton instance
# ============================================================================
_supabase_instance = None

def get_supabase_client() -> SupabaseService:
    """Get or create singleton Supabase client"""
    global _supabase_instance
    if _supabase_instance is None:
        _supabase_instance = SupabaseService()
    return _supabase_instance
