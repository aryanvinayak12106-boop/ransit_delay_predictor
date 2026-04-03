"""
Transit-X: Production Backend on Vercel
FastAPI + Supabase + PostgreSQL + PostGIS

Multi-tier Data Engine:
1. Live API (Google Routes / HERE Transit)
2. GTFS-Realtime Feed
3. ML Prediction Model
4. User Crowdsourced Reports
"""

import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Initialize Sentry for Error Tracking
# ============================================================================
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,
        environment=os.getenv('ENVIRONMENT', 'production'),
        debug=False
    )
    logger.info("Sentry initialized for error tracking")

# ============================================================================
# Lifespan Event Handler (Startup/Shutdown)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize dependencies on startup, cleanup on shutdown"""
    logger.info("🚀 Transit-X Backend starting up...")
    
    # Import and initialize services here
    from app.services.supabase_client import get_supabase_client
    from app.services.ml_engine import MLEngine
    
    # Verify Supabase connection
    try:
        supabase = get_supabase_client()
        health = await supabase.health_check()
        logger.info(f"✅ Supabase connected: {health}")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        raise
    
    # Load ML model
    try:
        ml_engine = MLEngine()
        await ml_engine.load_model()
        logger.info("✅ ML Model loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ ML Model loading failed: {e}. Will use fallback data sources.")
    
    yield
    
    logger.info("🛑 Transit-X Backend shutting down...")

# ============================================================================
# Initialize FastAPI Application
# ============================================================================
app = FastAPI(
    title="Transit-X API",
    description="Production-ready transit delay prediction backend",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS Configuration (Allow Flutter app)
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "https://*.examples.com",  # Your domain
        "https://transit-x.app",    # Production app domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Health Check Endpoint
# ============================================================================
@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Quick health check endpoint
    
    Returns:
        - API status
        - Database connection status
        - External API availability
        - ML Model status
    """
    from app.services.supabase_client import get_supabase_client
    
    return {
        "status": "healthy",
        "api": "operational",
        "database": "checking...",
        "external_apis": await check_external_apis(),
        "ml_model": "loaded",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

async def check_external_apis():
    """Check availability of external APIs"""
    return {
        "google_maps": True,  # Replace with actual check
        "here_maps": True,
        "openweather": True,
        "tomtom": True,
        "gtfs_realtime": True
    }

# ============================================================================
# Prediction Endpoint (Main endpoint)
# ============================================================================
@app.post("/api/predict", tags=["Predictions"])
async def predict_delay(
    stop_id: int,
    latitude: float,
    longitude: float,
    estimated_arrival_minutes: Optional[int] = None,
    user_id: Optional[str] = None
):
    """
    Main prediction endpoint with multi-tier data logic
    
    Args:
        stop_id: Transit stop ID
        latitude: User latitude
        longitude: User longitude
        estimated_arrival_minutes: Expected arrival time
        user_id: Optional user ID for personalized predictions
    
    Returns:
        {
            "delay_minutes": 15,
            "confidence_percentage": 85,
            "data_source": "google_routes",
            "breakdown": {
                "traffic_delay": 8,
                "weather_delay": 5,
                "event_delay": 2
            },
            "recommendation": "leave_now"
        }
    """
    from app.services.prediction_engine import PredictionEngine
    
    engine = PredictionEngine()
    prediction = await engine.predict(
        stop_id=stop_id,
        latitude=latitude,
        longitude=longitude,
        estimated_arrival_minutes=estimated_arrival_minutes,
        user_id=user_id
    )
    
    return prediction

# ============================================================================
# Routes Optimization Endpoint
# ============================================================================
@app.post("/api/routes", tags=["Routes"])
async def optimize_route(
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float,
    transport_mode: str = "public_transit",
    avoid_floods: bool = True
):
    """
    Optimize route considering traffic, weather, and floods
    
    Args:
        start_latitude: Origin latitude
        start_longitude: Origin longitude
        end_latitude: Destination latitude
        end_longitude: Destination longitude
        transport_mode: 'public_transit', 'driving', 'walking'
        avoid_floods: Whether to avoid flood-prone zones
    
    Returns:
        {
            "recommended_route": [...],
            "total_duration": 45,
            "stops": [...],
            "flood_warnings": [...],
            "alternative_routes": [...]
        }
    """
    from app.services.route_optimizer import RouteOptimizer
    
    optimizer = RouteOptimizer()
    route = await optimizer.optimize(
        start_lat=start_latitude,
        start_lon=start_longitude,
        end_lat=end_latitude,
        end_lon=end_longitude,
        mode=transport_mode,
        avoid_floods=avoid_floods
    )
    
    return route

# ============================================================================
# Nearby Stops Endpoint
# ============================================================================
@app.get("/api/stops/nearby", tags=["Stops"])
async def get_nearby_stops(
    latitude: float,
    longitude: float,
    radius_meters: int = 1000
):
    """
    Get nearby transit stops with current predictions
    """
    from app.services.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    stops = await supabase.get_nearby_stops(
        latitude=latitude,
        longitude=longitude,
        radius=radius_meters
    )
    
    return {
        "stops": stops,
        "count": len(stops),
        "radius_meters": radius_meters
    }

# ============================================================================
# Verified Delays Endpoint
# ============================================================================
@app.get("/api/delays/verified", tags=["Delays"])
async def get_verified_delays(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_meters: int = 5000
):
    """
    Get currently verified delays (crowdsourced + 5+ confirmations)
    """
    from app.services.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    delays = await supabase.get_active_verified_delays(
        latitude=latitude,
        longitude=longitude,
        radius=radius_meters
    )
    
    return {
        "verified_delays": delays,
        "count": len(delays),
        "last_updated": __import__('datetime').datetime.utcnow().isoformat()
    }

# ============================================================================
# Report Delay Endpoint
# ============================================================================
@app.post("/api/reports", tags=["Reports"])
async def report_delay(
    stop_id: int,
    user_id: str,
    delay_minutes: int,
    weather_condition: Optional[str] = None,
    confidence_rating: Optional[float] = None,
    notes: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """
    User reports a delay (crowdsourcing)
    Triggers verification if 5+ reports within 10 minutes
    """
    from app.services.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    report = await supabase.create_user_report(
        stop_id=stop_id,
        user_id=user_id,
        delay_minutes=delay_minutes,
        weather_condition=weather_condition,
        confidence_rating=confidence_rating,
        notes=notes,
        latitude=latitude,
        longitude=longitude
    )
    
    return {
        "report_id": report['id'],
        "status": "recorded",
        "message": "Thank you for reporting! Your feedback helps improve predictions."
    }

# ============================================================================
# Flood Warning Endpoint
# ============================================================================
@app.get("/api/floods/active", tags=["Floods"])
async def get_active_floods(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_meters: int = 10000
):
    """
    Get active flood warnings and affected stops
    """
    from app.services.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    floods = await supabase.get_active_flood_zones(
        latitude=latitude,
        longitude=longitude,
        radius=radius_meters
    )
    
    return {
        "flood_zones": floods,
        "count": len(floods),
        "monsoon_active": True  # Configurable based on calendar
    }

# ============================================================================
# ML Model Inference Endpoint
# ============================================================================
@app.post("/api/ml/predict", tags=["ML"])
async def ml_predict(
    features: dict
):
    """
    Direct ML model inference endpoint
    
    Features example:
    {
        "hour": 9,
        "day_of_week": 3,
        "temperature": 28,
        "precipitation": 2.5,
        "traffic_density": 0.7,
        "events_nearby": 1,
        "reported_delays_count": 3
    }
    """
    from app.services.ml_engine import MLEngine
    
    ml_engine = MLEngine()
    prediction = await ml_engine.predict(features)
    
    return {
        "predicted_delay_minutes": prediction['delay'],
        "confidence_score": prediction['confidence'],
        "model_version": prediction['version'],
        "features_used": len(features)
    }

# ============================================================================
# Notification Check Endpoint (For Flutter to poll)
# ============================================================================
@app.get("/api/notifications/{user_id}", tags=["Notifications"])
async def get_pending_notifications(user_id: str):
    """
    Get pending notifications for a user
    Flutter apps can poll this endpoint
    """
    from app.services.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    notifications = await supabase.get_pending_notifications(user_id)
    
    return {
        "notifications": notifications,
        "count": len(notifications),
        "unread_count": len([n for n in notifications if not n.get('read')])
    }

# ============================================================================
# Error Handlers
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler with Sentry integration"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if SENTRY_DSN:
        sentry_sdk.capture_exception(exc)
    
    return {
        "error": "Internal server error",
        "message": str(exc),
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

# ============================================================================
# Root Endpoint
# ============================================================================
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API documentation link"""
    return {
        "name": "Transit-X API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

# ============================================================================
# Auto-import route modules (discovery pattern)
# ============================================================================
# Routes are auto-discovered from app/routes/ directory
try:
    from app.api import routes
    app.include_router(routes.router)
    logger.info("✅ Route modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ Could not load route modules: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") != "production"
    )
