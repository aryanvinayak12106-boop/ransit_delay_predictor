"""
Multi-Tier Data Source Manager
Implements fallback logic for delay prediction

Priority Order:
1. Live API (Google Routes API / HERE Transit API) - 95% confidence
2. GTFS-Realtime Feed - 80% confidence
3. ML Prediction Model - 70% confidence
4. User Crowdsourced Reports - 70% + verification boost
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """Data source priority levels"""
    GOOGLE_MAPS = "google_routes"       # Highest priority
    HERE_MAPS = "here_maps"              # High priority
    GTFS_REALTIME = "gtfs_realtime"     # Medium-high
    ML_MODEL = "ml_model"                # Medium
    CROWDSOURCED = "user_report"         # Medium
    HEURISTIC = "heuristic"              # Fallback

class DataSourceConfidence(Enum):
    """Confidence scores by source"""
    GOOGLE_MAPS = 95
    HERE_MAPS = 90
    GTFS_REALTIME = 80
    ML_MODEL = 70
    CROWDSOURCED = 70  # Can increase to 85+ with 5+ confirmations
    HEURISTIC = 40

class PredictionEngine:
    """
    Multi-tier prediction engine with fallback logic
    """
    
    def __init__(self):
        self.google_api_key = __import__('os').getenv('GOOGLE_MAPS_API_KEY')
        self.here_api_key = __import__('os').getenv('HERE_API_KEY')
        self.gtfs_url = __import__('os').getenv('GTFS_REALTIME_URL')
        self.timeout = 5  # seconds per API call
    
    async def predict(
        self,
        stop_id: int,
        latitude: float,
        longitude: float,
        estimated_arrival_minutes: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main prediction method with fallback logic
        
        Returns:
        {
            'delay_minutes': 15,
            'confidence_percentage': 85,
            'data_source': 'google_routes',
            'breakdown': {
                'traffic_delay': 8,
                'weather_delay': 5,
                'event_delay': 2
            },
            'recommendation': 'leave_now',
            'timestamp': '2024-04-02T10:30:00Z'
        }
        """
        
        logger.info(f"Predicting delay for stop {stop_id}")
        start_time = datetime.utcnow()
        
        # Try data sources in priority order
        prediction = None
        
        # ==============================================
        # Tier 1: Try live APIs in parallel
        # ==============================================
        live_tasks = [
            self._try_google_routes(stop_id, latitude, longitude),
            self._try_here_maps(stop_id, latitude, longitude)
        ]
        
        live_results = await asyncio.gather(*live_tasks, return_exceptions=True)
        
        for result in live_results:
            if isinstance(result, dict) and result.get('delay_minutes') is not None:
                prediction = result
                logger.info(f"✅ Got prediction from {result.get('data_source')}")
                break
        
        # ==============================================
        # Tier 2: Try GTFS-Realtime if needed
        # ==============================================
        if not prediction:
            logger.info("⚠️ Live APIs failed, trying GTFS-Realtime...")
            prediction = await self._try_gtfs_realtime(stop_id, latitude, longitude)
        
        # ==============================================
        # Tier 3: Try ML Model if needed
        # ==============================================
        if not prediction:
            logger.info("⚠️ GTFS failed, trying ML Model...")
            prediction = await self._try_ml_model(stop_id, latitude, longitude)
        
        # ==============================================
        # Tier 4: Try crowdsourced reports
        # ==============================================
        if not prediction:
            logger.info("⚠️ ML failed, using crowdsourced reports...")
            prediction = await self._try_crowdsourced(stop_id, latitude, longitude)
        
        # ==============================================
        # Tier 5: Fallback to heuristic
        # ==============================================
        if not prediction:
            logger.error("❌ All data sources failed, using heuristic...")
            prediction = self._fallback_heuristic(stop_id)
        
        # ==============================================
        # Post-processing: Enhance with additional data
        # ==============================================
        
        # Add traffic impact
        prediction['breakdown']['traffic_delay'] = await self._get_traffic_delay(
            latitude, longitude
        )
        
        # Add weather impact
        prediction['breakdown']['weather_delay'] = await self._get_weather_delay(
            latitude, longitude
        )
        
        # Add event impact
        prediction['breakdown']['event_delay'] = await self._get_event_delay(
            stop_id, latitude, longitude
        )
        
        # Add flood impact multiplier if applicable
        flood_multiplier = await self._get_flood_impact(stop_id)
        if flood_multiplier > 1.0:
            original_delay = prediction['delay_minutes']
            prediction['delay_minutes'] = int(original_delay * flood_multiplier)
            prediction['breakdown']['flood_impact'] = int(original_delay * (flood_multiplier - 1))
            prediction['warning'] = f"⚠️ Area affected by flooding. Delay multiplied by {flood_multiplier:.1f}x"
        
        # Final delay calculation
        prediction['delay_minutes'] = int(
            sum(prediction['breakdown'].values())
        )
        
        # Add recommendation
        prediction['recommendation'] = self._get_recommendation(
            prediction['delay_minutes'],
            estimated_arrival_minutes
        )
        
        # Add metadata
        prediction['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        prediction['response_time_ms'] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return prediction
    
    # ==================================================
    # Tier 1: Live APIs
    # ==================================================
    
    async def _try_google_routes(
        self,
        stop_id: int,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Try Google Routes API"""
        if not self.google_api_key:
            return None
        
        try:
            # In production, call Google Routes API
            # For now, return mock data
            logger.info("Calling Google Routes API...")
            
            # Simulated API call
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # response = await client.get(
                #     f"https://routes.googleapis.com/...",
                #     params={"key": self.google_api_key}
                # )
                # data = response.json()
                
                # Mock response
                return {
                    'delay_minutes': 12,
                    'confidence_percentage': 95,
                    'data_source': 'google_routes',
                    'breakdown': {
                        'traffic_delay': 12,
                        'weather_delay': 0,
                        'event_delay': 0
                    }
                }
        
        except Exception as e:
            logger.warning(f"Google Routes API failed: {e}")
            return None
    
    async def _try_here_maps(
        self,
        stop_id: int,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Try HERE Transit API"""
        if not self.here_api_key:
            return None
        
        try:
            logger.info("Calling HERE Transit API...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # response = await client.get(
                #     f"https://transit.api.here.com/...",
                #     params={"apikey": self.here_api_key}
                # )
                # data = response.json()
                
                # Mock response
                return {
                    'delay_minutes': 10,
                    'confidence_percentage': 90,
                    'data_source': 'here_maps',
                    'breakdown': {
                        'traffic_delay': 10,
                        'weather_delay': 0,
                        'event_delay': 0
                    }
                }
        
        except Exception as e:
            logger.warning(f"HERE Transit API failed: {e}")
            return None
    
    # ==================================================
    # Tier 2: GTFS-Realtime
    # ==================================================
    
    async def _try_gtfs_realtime(
        self,
        stop_id: int,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Try GTFS-Realtime feed"""
        if not self.gtfs_url:
            return None
        
        try:
            logger.info("Fetching GTFS-Realtime feed...")
            
            # In production, parse GTFS-RT protobuf
            # For now, return mock
            return {
                'delay_minutes': 8,
                'confidence_percentage': 80,
                'data_source': 'gtfs_realtime',
                'breakdown': {
                    'traffic_delay': 5,
                    'weather_delay': 3,
                    'event_delay': 0
                }
            }
        
        except Exception as e:
            logger.warning(f"GTFS-Realtime failed: {e}")
            return None
    
    # ==================================================
    # Tier 3: ML Model
    # ==================================================
    
    async def _try_ml_model(
        self,
        stop_id: int,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Try ML model prediction"""
        try:
            from app.services.ml_engine import get_ml_engine
            from app.services.supabase_client import get_supabase_client
            
            logger.info("Using ML Model for prediction...")
            
            # Gather features
            supabase = get_supabase_client()
            weather = await supabase.get_weather_for_location(latitude, longitude)
            events = await supabase.rpc('get_nearby_active_events', {
                'p_latitude': latitude,
                'p_longitude': longitude,
                'p_radius_meters': 1000
            }).execute() if hasattr(supabase, 'rpc') else {'data': []}
            
            # Get crowdsourced reports count
            reports_count = 0  # Would fetch from supabase
            
            # Prepare features
            features = {
                'hour': datetime.utcnow().hour,
                'day_of_week': datetime.utcnow().weekday(),
                'temperature': weather.get('temperature', 25),
                'precipitation_mm': weather.get('precipitation_mm', 0),
                'traffic_density': 0.5,  # Would fetch from traffic service
                'events_count': len(events.get('data', [])) if events else 0,
                'reports_count': reports_count,
                'is_weekend': datetime.utcnow().weekday() >= 5,
                'weather_severity': weather.get('intensity', 0)
            }
            
            ml_engine = get_ml_engine()
            prediction_result = await ml_engine.predict(features)
            
            return {
                'delay_minutes': prediction_result['delay_minutes'],
                'confidence_percentage': prediction_result['confidence'],
                'data_source': 'ml_model',
                'breakdown': {
                    'traffic_delay': int(prediction_result['delay_minutes'] * 0.6),
                    'weather_delay': int(prediction_result['delay_minutes'] * 0.3),
                    'event_delay': int(prediction_result['delay_minutes'] * 0.1)
                }
            }
        
        except Exception as e:
            logger.warning(f"ML Model failed: {e}")
            return None
    
    # ==================================================
    # Tier 4: Crowdsourced Reports
    # ==================================================
    
    async def _try_crowdsourced(
        self,
        stop_id: int,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Try verified crowdsourced delays"""
        try:
            from app.services.supabase_client import get_supabase_client
            
            logger.info("Using crowdsourced reports...")
            
            supabase = get_supabase_client()
            verified_delays = await supabase.get_active_verified_delays(
                latitude=latitude,
                longitude=longitude,
                radius_meters=500
            )
            
            if verified_delays:
                delay_info = verified_delays[0]
                confidence = 70 + (delay_info.get('verification_count', 0) * 5)  # Boost with count
                
                return {
                    'delay_minutes': delay_info.get('current_delay_minutes', 0),
                    'confidence_percentage': min(95, confidence),
                    'data_source': 'user_report',
                    'breakdown': {
                        'traffic_delay': delay_info.get('current_delay_minutes', 0),
                        'weather_delay': 0,
                        'event_delay': 0
                    },
                    'verification_count': delay_info.get('verification_count', 0)
                }
            
            return None
        
        except Exception as e:
            logger.warning(f"Crowdsourced lookup failed: {e}")
            return None
    
    # ==================================================
    # Tier 5: Fallback Heuristic
    # ==================================================
    
    def _fallback_heuristic(self, stop_id: int) -> Dict[str, Any]:
        """Fallback to simple heuristic"""
        logger.error(f"All data sources failed for stop {stop_id}")
        
        return {
            'delay_minutes': 5,  # Assume 5 min delay
            'confidence_percentage': 40,
            'data_source': 'heuristic',
            'breakdown': {
                'traffic_delay': 3,
                'weather_delay': 1,
                'event_delay': 1
            },
            'warning': '⚠️ Using default heuristic. Data sources unavailable.'
        }
    
    # ==================================================
    # Helper: Traffic Delay
    # ==================================================
    
    async def _get_traffic_delay(self, latitude: float, longitude: float) -> int:
        """Get traffic-related delay"""
        try:
            from app.services.traffic_service import TrafficService
            traffic = TrafficService()
            density = await traffic.get_traffic_density(latitude, longitude)
            return int(density * 20)  # 0-20 minutes based on density
        except:
            return 0
    
    # ==================================================
    # Helper: Weather Delay
    # ==================================================
    
    async def _get_weather_delay(self, latitude: float, longitude: float) -> int:
        """Get weather-related delay"""
        try:
            from app.services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            weather = await supabase.get_weather_for_location(latitude, longitude)
            
            intensity = weather.get('intensity', 0)
            return int(intensity * 10)  # 0-10 minutes based on weather
        except:
            return 0
    
    # ==================================================
    # Helper: Event Delay
    # ==================================================
    
    async def _get_event_delay(self, stop_id: int, latitude: float, longitude: float) -> int:
        """Calculate event-related delay"""
        try:
            from app.services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Try to get nearby events from database
            # events = await supabase.rpc('get_nearby_active_events', ...)
            # return len(events) * 5  # 5 min per major event
            
            return 0
        except:
            return 0
    
    # ==================================================
    # Helper: Flood Impact
    # ==================================================
    
    async def _get_flood_impact(self, stop_id: int) -> float:
        """Get flood multiplier for stop (e.g., 1.0 = no impact, 1.5 = 50% increase)"""
        try:
            from app.services.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Query stop_flood_mapping to get risk multiplier
            # result = await supabase.table('stop_flood_mapping')
            #     .select('risk_multiplier')
            #     .eq('stop_id', stop_id)
            #     .single()
            #     .execute()
            
            # return result.data['risk_multiplier'] if result.data else 1.0
            
            return 1.0  # No flood impact by default
        except:
            return 1.0
    
    # ==================================================
    # Helper: Recommendation
    # ==================================================
    
    def _get_recommendation(
        self,
        delay_minutes: int,
        estimated_arrival_minutes: Optional[int] = None
    ) -> str:
        """Get user recommendation based on delay"""
        
        if delay_minutes > 15:
            return "delay_significant"  # Consider alternative transport
        elif delay_minutes > 10:
            return "delay_moderate"     # May want to leave soon
        elif delay_minutes > 5:
            return "delay_minor"        # Minor delay expected
        else:
            return "on_time"            # On time or very small delay
