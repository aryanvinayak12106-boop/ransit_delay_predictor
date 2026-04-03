"""
Weather Service Integration
OpenWeatherMap API integration with caching
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class WeatherService:
    """OpenWeatherMap API client for weather data"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/3.0"
        self.timeout = 5
        self.cache_timeout = 1800  # 30 minutes
    
    async def get_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get current weather data for a location
        
        Returns:
        {
            'temperature': 28,          # Celsius
            'condition': 'rainy',
            'precipitation_mm': 2.5,
            'wind_speed': 15,           # km/h
            'visibility': 800,          # meters
            'intensity': 0.75,          # 0.0-1.0, used for delay calculation
            'timestamp': '2024-04-02T10:30:00Z'
        }
        """
        try:
            if not self.api_key:
                logger.warning("OpenWeatherMap API key not configured")
                return self._default_weather()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/onecall",
                    params={
                        'lat': latitude,
                        'lon': longitude,
                        'appid': self.api_key,
                        'units': 'metric'
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse current weather
            current = data.get('current', {})
            weather = {
                'temperature': current.get('temp', 25),
                'condition': self._parse_condition(current.get('weather', [])),
                'precipitation_mm': current.get('rain', {}).get('1h', 0),
                'wind_speed': current.get('wind_speed', 0),
                'visibility': current.get('visibility', 10000),
                'intensity': self._calculate_weather_intensity(
                    current.get('weather', []),
                    current.get('rain', {}).get('1h', 0)
                ),
                'timestamp': datetime.utcfromtimestamp(current.get('dt', 0)).isoformat() + 'Z'
            }
            
            logger.info(f"Weather data fetched: {weather['condition']}")
            return weather
        
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._default_weather()
    
    def _parse_condition(self, weather_list: list) -> str:
        """Parse weather condition from OpenWeatherMap"""
        if not weather_list:
            return "unknown"
        
        main_condition = weather_list[0].get('main', '').lower()
        
        condition_mapping = {
            'clear': 'clear',
            'clouds': 'cloudy',
            'rain': 'rainy',
            'drizzle': 'rainy',
            'thunderstorm': 'storm',
            'snow': 'snowy',
            'mist': 'fog',
            'smoke': 'fog',
            'haze': 'fog',
            'dust': 'windy',
            'sand': 'windy',
            'ash': 'foggy',
            'squall': 'windy',
            'tornado': 'tornado'
        }
        
        return condition_mapping.get(main_condition, 'unknown')
    
    def _calculate_weather_intensity(
        self,
        weather_list: list,
        precipitation_mm: float
    ) -> float:
        """
        Calculate weather intensity (0.0-1.0)
        Used for delay multiplier
        """
        intensity = 0.0
        
        # Check main condition
        if weather_list:
            main_condition = weather_list[0].get('main', '').lower()
            if main_condition == 'clear':
                intensity = 0.0
            elif main_condition == 'clouds':
                intensity = 0.1
            elif main_condition in ['rain', 'drizzle']:
                intensity = 0.6
            elif main_condition == 'thunderstorm':
                intensity = 0.9
            elif main_condition == 'snow':
                intensity = 0.8
            else:
                intensity = 0.4
        
        # Add precipitation impact
        if precipitation_mm > 5:
            intensity = max(intensity, 0.7 + (precipitation_mm / 100))
        elif precipitation_mm > 2:
            intensity = max(intensity, 0.5 + (precipitation_mm / 50))
        
        return min(1.0, intensity)  # Cap at 1.0
    
    def _default_weather(self) -> Dict[str, Any]:
        """Return default weather when API unavailable"""
        return {
            'temperature': 25,
            'condition': 'unknown',
            'precipitation_mm': 0,
            'wind_speed': 0,
            'visibility': 10000,
            'intensity': 0.5,  # Medium intensity by default
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    async def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        hours_ahead: int = 3
    ) -> list:
        """Get weather forecast for next N hours"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/onecall",
                    params={
                        'lat': latitude,
                        'lon': longitude,
                        'appid': self.api_key,
                        'units': 'metric'
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            hourly = data.get('hourly', [])[:hours_ahead]
            
            forecast = []
            for hour_data in hourly:
                forecast.append({
                    'timestamp': datetime.utcfromtimestamp(hour_data.get('dt')).isoformat() + 'Z',
                    'temperature': hour_data.get('temp'),
                    'condition': self._parse_condition(hour_data.get('weather', [])),
                    'precipitation_probability': hour_data.get('pop', 0),  # Probability of Precipitation
                    'intensity': self._calculate_weather_intensity(
                        hour_data.get('weather', []),
                        hour_data.get('rain', {}).get('1h', 0)
                    )
                })
            
            return forecast
        
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return []

# ============================================================================
# Singleton instance
# ============================================================================
_weather_service_instance = None

def get_weather_service() -> WeatherService:
    """Get or create singleton weather service"""
    global _weather_service_instance
    if _weather_service_instance is None:
        _weather_service_instance = WeatherService()
    return _weather_service_instance
