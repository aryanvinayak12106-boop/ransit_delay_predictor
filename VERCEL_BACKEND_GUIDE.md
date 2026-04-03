# Transit-X Backend Architecture & Implementation Guide

## 🚀 Overview

**Transit-X** is a production-grade transit delay prediction system running on Vercel (Python FastAPI). It implements a sophisticated **multi-tier data fallback architecture** that ensures predictions are always available, even when primary data sources fail.

---

## 📊 Multi-Tier Data Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Request (Stop prediction)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │    PredictionEngine.predict()            │
        └────────────────────┬────────────────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
┌─────────────┐         ┌──────────────┐      ┌────────────────┐
│Google Routes│         │ HERE Transit │      │GTFS-Realtime   │
│API (1 sec)  │         │API (1 sec)   │      │Feed (2 sec)    │
│95% confidence        │90% confidence │      │80% confidence  │
└──────┬──────┘         └──────┬───────┘      └────────┬───────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                ┌──────────────┴──────────────┐
                ▼                             ▼
            SUCCESS?                   ML Model Inference
         (Parallel with timeout)        (Scikit-learn RFC)
            Return result               70% confidence
                │                              │
                └──────────────────┬───────────┘
                                   │
                            SUCCESS?
                          (Always succeeds)
                           Return result
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │Check Crowdsourced Reports│
                    │(Verified delays table)   │
                    │70-95% confidence         │
                    └──────────────┬───────────┘
                                   │
                            SUCCESS?
                         Returns verified delay
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   Fallback Heuristic     │
                    │  (Rule-based logic)      │
                    │   40% confidence         │
                    └──────────────────────────┘
                                   │
                                   ▼
        ┌──────────────────────────────────────────┐
        │       Enhanced Response                   │
        ├──────────────────────────────────────────┤
        │- Traffic Impact (TomTom API)              │
        │- Weather Impact (OpenWeather)             │
        │- Event Impact (Supabase city_events)      │
        │- Flood Multiplier (PostGIS zones)         │
        │- Recommendation (leave_now, etc)          │
        └──────────────────────────────────────────┘
                        │
                        ▼
            ┌──────────────────────┐
            │  Return to Flutter   │
            └──────────────────────┘
```

---

## 🏗️ Backend Project Structure

```
transit_delay_predictor/
├── api/                                      # Vercel serverless functions
│   ├── main.py                              # FastAPI app + routes
│   │
│   ├── services/                            # Business logic layer
│   │   ├── supabase_client.py              # Database operations
│   │   ├── prediction_engine.py            # Multi-tier fallback logic ⭐
│   │   ├── ml_engine.py                    # Random Forest model inference
│   │   ├── weather_service.py              # OpenWeatherMap API
│   │   ├── traffic_service.py              # TomTom Traffic API
│   │   ├── notification_service.py         # OneSignal integration
│   │   └── route_optimizer.py              # Route optimization
│   │
│   └── models/                              # Pydantic request/response models
│       ├── prediction.py
│       ├── route.py
│       └── notification.py
│
├── supabase/
│   ├── migrations/
│   │   ├── 001_init_schema.sql            # Initial schema
│   │   └── 002_flood_zones_...sql         # Flood zones + events ✅
│   │
│   └── functions/                           # Edge Functions (Deno)
│       ├── fetch_weather/
│       ├── fetch_events/
│       └── _shared/cors.ts
│
├── models/                                  # ML models
│   ├── delay_predictor.joblib             # Pre-trained Random Forest
│   └── training_data.csv                  # Training dataset (Kaggle)
│
├── vercel.json                             # Vercel deployment config ✅
├── requirements.txt                        # Python dependencies ✅
├── .env.example                            # Environment variables ✅
├── runtime.txt                             # Python version
└── README.md                               # Documentation
```

---

## 📝 API Endpoints

### 1. **Predict Delay** (Main Endpoint)

```http
POST /api/predict
```

**Request:**
```json
{
  "stop_id": 123,
  "latitude": 12.9352,
  "longitude": 77.6245,
  "estimated_arrival_minutes": 15,
  "user_id": "uuid-of-user"
}
```

**Response:**
```json
{
  "delay_minutes": 12,
  "confidence_percentage": 85,
  "data_source": "google_routes",
  "breakdown": {
    "traffic_delay": 8,
    "weather_delay": 3,
    "event_delay": 1,
    "flood_impact": 0
  },
  "recommendation": "leave_now",
  "warning": null,
  "timestamp": "2024-04-02T10:30:00Z",
  "response_time_ms": 342
}
```

### 2. **Get Nearby Stops**

```http
GET /api/stops/nearby?latitude=12.9352&longitude=77.6245&radius_meters=1000
```

### 3. **Get Verified Delays**

```http
GET /api/delays/verified?latitude=12.9352&longitude=77.6245&radius_meters=5000
```

Returns delays verified by 5+ user reports within 10 minutes.

### 4. **Report Delay** (Crowdsourcing)

```http
POST /api/reports
```

**Request:**
```json
{
  "stop_id": 123,
  "user_id": "uuid",
  "delay_minutes": 15,
  "weather_condition": "rainy",
  "confidence_rating": 4.5,
  "notes": "Heavy traffic due to accident",
  "latitude": 12.9352,
  "longitude": 77.6245
}
```

### 5. **Get Active Floods**

```http
GET /api/floods/active?latitude=12.9352&longitude=77.6245&radius_meters=10000
```

Returns flood zones and affected stops.

### 6. **ML Model Direct Inference**

```http
POST /api/ml/predict
```

**Request:**
```json
{
  "hour": 9,
  "day_of_week": 3,
  "temperature": 28,
  "precipitation_mm": 2.5,
  "traffic_density": 0.7,
  "events_count": 1,
  "reports_count": 5,
  "is_weekend": false,
  "weather_severity": 0.6
}
```

---

## 🔐 Authentication & Authorization

### API Key Authentication
```python
# In headers:
Authorization: Bearer SUPABASE_KEY

# Or in request:
?api_key=SUPABASE_KEY
```

### Row-Level Security (RLS)

Protected tables have RLS policies:
- **flood_prone_zones**: SELECT only (public read)
- **verified_delays**: SELECT only (public read for navigation)
- **notification_queue**: SELECT/UPDATE restricted to user_id
- **user_reports**: INSERT restricted to authenticated users

---

## 🔧 Key Services

### 1. Supabase Client Service
```python
from api.services.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Get nearby stops with PostGIS
stops = await supabase.get_nearby_stops(
    latitude=12.9352,
    longitude=77.6245,
    radius_meters=1000
)

# Get verified delays
delays = await supabase.get_active_verified_delays(
    latitude=12.9352,
    longitude=77.6245
)

# Create user report (triggers verification if 5+ reports)
report = await supabase.create_user_report(
    stop_id=123,
    user_id='uuid',
    delay_minutes=15,
    weather_condition='rainy'
)
```

### 2. Prediction Engine (Multi-Tier Fallback)
```python
from api.services.prediction_engine import PredictionEngine

engine = PredictionEngine()

prediction = await engine.predict(
    stop_id=123,
    latitude=12.9352,
    longitude=77.6245
)

# Returns: {delay_minutes, confidence_percentage, data_source, breakdown, ...}
```

**Fallback Order:**
1. Google Routes API (95% confidence, 1 sec timeout)
2. HERE Transit API (90% confidence, 1 sec timeout)
3. GTFS-Realtime Feed (80% confidence, 2 sec timeout)
4. ML Prediction Model (70% confidence, instant)
5. Verified Crowdsourced Reports (70-95% confidence)
6. Heuristic Fallback (40% confidence)

### 3. ML Engine (Scikit-learn Random Forest)
```python
from api.services.ml_engine import get_ml_engine

ml_engine = get_ml_engine()
await ml_engine.load_model()

prediction = await ml_engine.predict({
    'hour': 9,
    'day_of_week': 3,
    'temperature': 28,
    'precipitation_mm': 2.5,
    'traffic_density': 0.7,
    'events_count': 1,
    'reports_count': 5,
    'is_weekend': False,
    'weather_severity': 0.6
})

# Returns: {delay_minutes, confidence, version, model_type}
```

### 4. Weather Service (OpenWeatherMap)
```python
from api.services.weather_service import get_weather_service

weather = get_weather_service()

current = await weather.get_weather(latitude=12.9352, longitude=77.6245)
# {temperature, condition, precipitation_mm, intensity, ...}

forecast = await weather.get_hourly_forecast(latitude, longitude, hours_ahead=3)
# [{timestamp, temperature, condition, precipitation_probability, intensity}, ...]
```

### 5. Traffic Service (TomTom)
```python
from api.services.traffic_service import get_traffic_service

traffic = get_traffic_service()

# Get traffic density (0.0-1.0)
density = await traffic.get_traffic_density(latitude, longitude)

# Get incidents (accidents, closures, events)
incidents = await traffic.get_incidents(latitude, longitude, radius_meters=5000)
# {incidents: [...], count, timestamp}

# Get traffic flow
flow = await traffic.get_traffic_flow(latitude, longitude)
# {avg_speed_kmh, free_flow_speed_kmh, congestion_level, event_rating}
```

---

## 📊 Database Schema Highlights

### flood_prone_zones Table
```sql
CREATE TABLE flood_prone_zones (
  id BIGSERIAL PRIMARY KEY,
  zone_name VARCHAR(255) UNIQUE,
  boundary GEOMETRY(POLYGON, 4326),        -- PostGIS polygon
  center_point GEOMETRY(POINT, 4326),      -- Generated from boundary
  flood_risk_level VARCHAR(20),            -- critical, high, medium, low
  monsoon_months INT[],                    -- [6,7,8,9] for June-Sept
  current_water_level_cm FLOAT,
  critical_water_level_cm FLOAT
);
```

### verified_delays Table
```sql
CREATE TABLE verified_delays (
  id BIGSERIAL PRIMARY KEY,
  stop_id BIGINT REFERENCES stops(id),
  current_delay_minutes INT,
  is_verified BOOLEAN,                     -- TRUE if 5+ reports
  verification_count INT,                  -- How many reports
  verification_confidence_score FLOAT,     -- 0-100%
  updated_at TIMESTAMP,
  resolved_at TIMESTAMP
);
```

### Real-Time Trigger Logic
```sql
-- When user creates a report, if 5+ reports in last 10 min:
CREATE FUNCTION verify_delay_on_multiple_reports()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT COUNT(*) FROM user_reports 
      WHERE stop_id = NEW.stop_id 
      AND created_at >= CURRENT_TIMESTAMP - INTERVAL '10 minutes') >= 5
  THEN
    UPDATE verified_delays SET is_verified = TRUE WHERE stop_id = NEW.stop_id;
    NOTIFY delay_verified, ...;  -- Trigger real-time updates
  END IF;
  RETURN NEW;
END;
$$;
```

---

## 🚀 Deployment on Vercel

### 1. Clone & Install

```bash
git clone <repo>
cd transit_delay_predictor
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Fill in your API keys (see .env.example for details)
```

### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Or connect GitHub for auto-deploys:
# https://vercel.com/import
```

### 4. Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...
GOOGLE_MAPS_API_KEY=AIsaSy...
HERE_API_KEY=...
TOMTOM_API_KEY=...
OPENWEATHER_API_KEY=...
SENTRY_DSN=https://...sentry.io
ONESIGNAL_API_KEY=...
ONESIGNAL_APP_ID=...
```

---

## 📈 Monitoring & Logging

### Sentry Integration
```python
# Automatic error tracking
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    environment='production',
    traces_sample_rate=1.0
)
```

### API Metrics Logging
```sql
-- Track which data source was used
SELECT 
  api_provider,
  COUNT(*) as call_count,
  AVG(response_time_ms) as avg_response_time,
  AVG(confidence_score) as avg_confidence
FROM api_call_metrics
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY api_provider
ORDER BY call_count DESC;
```

### Real-Time Subscriptions (Supabase)
```python
# Listen for verified delays
from supabase import realtime

async def on_delay_verified(payload):
    stop_id = payload['new']['stop_id']
    delay = payload['new']['current_delay_minutes']
    print(f"✅ Delay verified: Stop {stop_id}, {delay} min delay")

channel = supabase.realtime.on(
    'verified_delays',
    event='*',
    schema='public',
    callback=on_delay_verified
).subscribe()
```

---

## 🔄 Confidence Score Calculation

Confidence = Data Quality Score

```
Google Maps:           95% (real-time, authoritative)
HERE Maps:             90% (real-time, reliable)
GTFS-Realtime:         80% (official but 30s delay)
ML Model:              70% (base score)
  + 5% per report:            (70 + count*5, max 85%)
Heuristic:             40% (last resort)
```

**Boosters:**
- +10% for 5+ confirmed user reports
- +5% for consistent data across sources
- -10% if data source is > 5 minutes old

---

## 🧠 ML Model Training

### Features Used
```python
features = [
    'hour_of_day',              # 0-23
    'day_of_week',              # 0-6 (0=Monday)
    'temperature',              # Celsius
    'precipitation_mm',         # Rainfall
    'traffic_density',          # 0.0-1.0
    'event_count_nearby',       # 0-10
    'crowdsourced_delay_count', # User reports
    'is_weekend',               # Boolean
    'weather_severity'          # 0.0-1.0
]
```

### Model Architecture
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=100,           # Number of trees
    max_depth=15,               # Max tree depth
    random_state=42,
    n_jobs=-1                   # Use all cores
)

# Trained on Kaggle traffic dataset
# Updated monthly with new data
```

### Retraining Job
```python
# Background job (e.g., daily 2 AM)
async def retrain_model():
    # Collect training data from last 30 days
    training_data = await supabase.query(
        "SELECT * FROM user_reports WHERE created_at > NOW() - INTERVAL '30 days'"
    )
    
    ml_engine = get_ml_engine()
    metrics = await ml_engine.train_model(training_data)
    # Metrics: accuracy, precision, recall, f1, MAPE
```

---

## ⚠️ Error Handling

### Graceful Degradation
```python
try:
    # Try primary source
    prediction = await predictio_engine.predict(...)
except TimeoutError:
    # Falls back automatically
    prediction = await ml_engine.predict(...)
except Exception as e:
    logger.error(f"Prediction error: {e}")
    Sentry.capture_exception(e)
    prediction = heuristic_fallback()

return prediction  # Always returns something
```

### Timeout Strategy
```python
# Per API call timeout
GOOGLE_TIMEOUT = 1.0      # Second
HERE_TIMEOUT = 1.0        # Second
GTFS_TIMEOUT = 2.0        # Seconds
ML_TIMEOUT = 0.1          # Milliseconds (in-process)

# Total request timeout
REQUEST_TIMEOUT = 10      # Seconds (for entire prediction)
```

---

## 🔔 Push Notifications

### OneSignal Integration
```python
from api.services.notification_service import NotificationService

notifier = NotificationService()

# Send time-to-leave notification
await notifier.send_time_to_leave(
    user_id='uuid',
    stop_id=123,
    leave_in_minutes=15,
    delay_minutes=20
)

# Send flood warning
await notifier.send_flood_alert(
    user_id='uuid',
    flood_zone_name='Lower Parel-Worli',
    affected_stops=[123, 124, 125]
)
```

### Database Queue
- Notifications stored in `notification_queue` table
- Status: pending → sent → delivered
- Retry mechanism: 3 attempts
- Polling: Flutter app checks `/api/notifications/{user_id}`

---

## 📚 Integration with Flutter App

### Flutter Client Example
```dart
// In Flutter app
final response = await http.post(
  Uri.parse('https://transit-x.vercel.app/api/predict'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'stop_id': stopId,
    'latitude': location.latitude,
    'longitude': location.longitude,
    'estimated_arrival_minutes': 15,
    'user_id': userId
  })
);

final prediction = DelayPrediction.fromJson(jsonDecode(response.body));

// Show delay with color coding
Color delayColor = prediction.delayMinutes > 15 ? Colors.red : Colors.yellow;
Text('Delay: ${prediction.delayMinutes} min (${prediction.dataSource})');
```

---

## 🚨 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "All data sources failed" | Timeout on all APIs | Check external API status, verify API keys |
| Confidence too low (<50%) | Using heuristic fallback | Restart API, check Supabase connection |
| Flood data not updating | Database trigger issue | Verify `verify_delay_on_multiple_reports()` trigger |
| 5xx errors | Sentry captures | Check Sentry dashboard for stack trace |
| Slow response (> 5s) | Cascading fallbacks | Implement parallel API calls with watchdog timer |

---

## 🔒 Security Checklist

- [ ] API keys loaded from environment variables, not hardcoded
- [ ] Supabase RLS policies enabled
- [ ] Rate limiting configured (100 req/min per IP)
- [ ] CORS configured to allow only Flutter app domain
- [ ] Sentry configured to NOT log sensitive data
- [ ] Database backups enabled daily
- [ ] SSL/TLS on all endpoints
- [ ] API request signature validation
- [ ] IP whitelisting for admin endpoints

---

## 📞 Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Sentry SDK**: https://docs.sentry.io/platforms/python/
- **TomTom API**: https://developer.tomtom.com/traffic-api
- **OpenWeatherMap**: https://openweathermap.org/api

---

**Created**: April 2, 2026  
**Status**: Production Ready ✅  
**Version**: 1.0.0
