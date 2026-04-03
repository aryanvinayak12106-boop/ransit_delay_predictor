# 🎯 Transit-X Quick Reference Card

## 🚀 30-Second Overview

**Transit-X** = Production transit delay prediction using Flutter + Vercel + Supabase

**Key Differentiator**: Multi-tier fallback ensures predictions always available
```
Google API → HERE API → GTFS → ML Model → User Reports → Heuristic
95% conf   90% conf   80%    70%       70-95%         40%
```

---

## 📁 Critical Files to Edit

| File | Purpose | Edit |
|------|---------|------|
| `.env` | API credentials | Copy from `.env.example`, fill credentials |
| `lib/config/constants.dart` | App config | Update Supabase/Maps/Vercel URLs |
| `vercel.json` | Backend config | Already complete ✅ |
| `supabase/migrations/*` | Database | Already deployed ✅ |

---

## 🔧 Setup Checklist (Quick)

- [ ] Create Supabase project → copy URL/key
- [ ] Get Google Maps API key
- [ ] Get weather API key
- [ ] Deploy backend: `vercel --prod`
- [ ] Update config files
- [ ] Run: `flutter run`
- [ ] Test endpoints

**Total Time**: ~30 minutes

---

## 📊 API Endpoints Quick Ref

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Service status |
| `/api/predict` | POST | **Main endpoint** |
| `/api/stops/nearby` | GET | Get stops in radius |
| `/api/delays/verified` | GET | Crowdsourced delays |
| `/api/reports` | POST | Report delay |
| `/api/floods/active` | GET | Flood zones |
| `/api/ml/predict` | POST | Direct ML inference |
| `/api/notifications/{user_id}` | GET | Pending notifications |

**Base URL**: `https://your-project.vercel.app`

---

## 🗄️ Important Database Tables

| Table | Records | Purpose |
|-------|---------|---------|
| `stops` | 100s | Transit stops with PostGIS |
| `city_events` | Varies | Traffic disruptions |
| `user_reports` | Volatile | Crowdsourced delays |
| `verified_delays` | Real-time | 5+ report verification |
| `flood_prone_zones` | 10-50 | Monsoon waterlogging areas |
| `notification_queue` | Queue | OneSignal delivery queue |
| `api_call_metrics` | Logs | API performance tracking |
| `ml_model_metrics` | Version | Model accuracy tracking |

---

## 🔐 Environment Variables (All Required)

```bash
# Database
SUPABASE_URL=
SUPABASE_KEY=

# External APIs
GOOGLE_MAPS_API_KEY=
HERE_API_KEY=
TOMTOM_API_KEY=
OPENWEATHER_API_KEY=
GTFS_REALTIME_URL=

# Monitoring
SENTRY_DSN=

# Notifications
ONESIGNAL_API_KEY=
ONESIGNAL_APP_ID=

# ML
ML_MODEL_PATH=

# Config
ENVIRONMENT=production
```

---

## 🧵 Key Concepts

### Confidence Scoring
```
95%: Google Maps (real-time from authorities)
90%: HERE Transit (real-time from HERE)
80%: GTFS-Realtime (official data)
70%: ML Model (trained on historical data)
70-95%: User Reports (boosted by count)
40%: Heuristic (last resort)
```

### Fallback Logic
```python
if google_api_response:
    return google_prediction  # 95% confidence
elif here_api_response:
    return here_prediction    # 90% confidence
elif gtfs_response:
    return gtfs_prediction    # 80% confidence
elif ml_model_available:
    return ml_prediction      # 70% confidence
elif verified_reports:
    return report_prediction  # 70-95% confidence
else:
    return heuristic_fallback # 40% confidence
```

### Real-Time Trigger
```sql
-- If 5 unique users report delay at same stop within 10 min:
-- → verified_delays.is_verified = TRUE
-- → confidence increased to 85-95%
-- → Notification sent to all users at that stop
```

---

## 🗺️ Architecture Layers

```
Flutter UI (Package)
    ↓ HTTP
Vercel Backend (FastAPI)
    ↓ Services
Supabase Database (PostgreSQL + PostGIS)
    ↓ External APIs
Google/HERE/OpenWeather/TomTom
```

---

## 🚀 Deployment Commands

```bash
# Backend
vercel --prod              # Deploy to Vercel

# Database
# Run migrations in Supabase SQL Editor:
# 1. migrations/001_init_schema.sql
# 2. migrations/002_flood_zones_...sql

# Flutter
flutter pub get            # Install deps
flutter run               # Run on device
flutter build apk --release   # Build Android
flutter build ios --release   # Build iOS
```

---

## 📱 Flutter Integration

```dart
// Main prediction call
final response = await http.post(
  Uri.parse('$VERCEL_URL/api/predict'),
  body: jsonEncode({
    'stop_id': stopId,
    'latitude': location.latitude,
    'longitude': location.longitude
  })
);

final prediction = DelayPrediction.fromJson(jsonDecode(response.body));

// Show delay with colored marker
Color markerColor = prediction.delayMinutes > 15 ? Colors.red :
                    prediction.delayMinutes > 5 ? Colors.yellow :
                    Colors.green;
```

---

## 💻 Python Backend Quick Ref

```python
# Main prediction endpoint
@app.post("/api/predict")
async def predict_delay(stop_id: int, latitude: float, longitude: float):
    engine = PredictionEngine()
    prediction = await engine.predict(
        stop_id=stop_id,
        latitude=latitude,
        longitude=longitude
    )
    return prediction

# Service usage
from api.services.supabase_client import get_supabase_client
from api.services.prediction_engine import PredictionEngine
from api.services.ml_engine import get_ml_engine

supabase = get_supabase_client()
prediction_engine = PredictionEngine()
ml_engine = get_ml_engine()
```

---

## 🌐 External API Keys Source

| API | Link | Cost | Rate Limit |
|-----|------|------|-----------|
| **Google Maps** | console.cloud.google.com | Free tier available | 50k/day |
| **HERE Maps** | developer.here.com | Free tier: 250k/month | Varies |
| **TomTom Traffic** | developer.tomtom.com | Free tier: 2500/day | Varies |
| **OpenWeather** | openweathermap.org | Free tier: 60 calls/min | 3/sec |
| **GTFS-Realtime** | Transit authority | Public feed | Unlimited |

---

## 🔍 Testing Endpoints

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Predict delay
curl -X POST https://your-project.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stop_id": 123,
    "latitude": 12.9352,
    "longitude": 77.6245
  }'

# Get nearby stops
curl "https://your-project.vercel.app/api/stops/nearby?latitude=12.9352&longitude=77.6245"

# Get verified delays
curl "https://your-project.vercel.app/api/delays/verified?latitude=12.9352&longitude=77.6245"
```

---

## 📊 Monitoring Dashboards

| Tool | Link | What to Check |
|------|------|---------------|
| **Vercel** | vercel.com/dashboard | Deploy status, logs, errors |
| **Sentry** | sentry.io | Exception tracking, performance |
| **Supabase** | supabase.io/dashboard | DB queries, realtime, logs |
| **OneSignal** | onesignal.com | Notification delivery, clicks |

---

## ⚡ Performance Tips

1. **Parallel API Calls**: Use `asyncio.gather()` for Google + HERE
2. **Caching**: Cache weather for 30 minutes
3. **Indexes**: PostGIS spatial indexes on location columns
4. **Timeouts**: 1s per API, 10s total request
5. **Connection Pool**: Reuse HTTP connections

```python
# Fast parallel calls with timeout
results = await asyncio.gather(
    google_api_call(),
    here_api_call(),
    timeout=1.0  # 1 second each
)
```

---

## 🆘 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ServiceUnavailable` | Supabase down | Check status.supabase.com |
| `Timeout` | API too slow | Try next fallback, increase timeout |
| `401 Unauthorized` | Bad API key | Verify in .env, check Supabase |
| `404 Not Found` | Wrong URL | Check VERCEL_BACKEND_URL |
| `5xx Server Error` | Backend crash | Check Sentry dashboard |

---

## 📈 Key Metrics to Monitor

```sql
-- Response time by data source
SELECT api_provider, AVG(response_time_ms) 
FROM api_call_metrics 
GROUP BY api_provider;

-- Verification success rate
SELECT COUNT(*) as verified, 
       COUNT(*) FILTER (WHERE is_verified) as success_rate
FROM verified_delays;

-- ML Model accuracy
SELECT accuracy_percentage FROM ml_model_metrics 
WHERE is_active = TRUE;
```

---

## 🎯 Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get request timing
import time
start = time.time()
result = await predict(...)
elapsed = time.time() - start
logger.info(f"Prediction took {elapsed:.2f}s")

# Check data source used
logger.info(f"Data source: {result['data_source']} ({result['confidence_percentage']}%)")
```

---

## 📚 File Organization Reminder

```
transit_delay_predictor/
├── api/                      ← Vercel backend
├── lib/                       ← Flutter app
├── supabase/                  ← Database migrations
├── vercel.json               ← EDIT: Deployed ✅
├── requirements.txt          ← EDIT: Dependencies ✅
├── .env.example              ← COPY & EDIT with your keys
├── IMPLEMENTATION_COMPLETE.md ← START HERE
├── SYSTEM_ARCHITECTURE.md    ← Full deployment guide
└── VERCEL_BACKEND_GUIDE.md   ← Backend reference
```

---

## ⚙️ Production Checklist

```
WEEK 1:
- [ ] Deploy Supabase database
- [ ] Deploy Vercel backend
- [ ] Test all endpoints
- [ ] Set up Sentry
- [ ] Set up OneSignal

WEEK 2:
- [ ] Configure Flutter with backend URL
- [ ] Build Flutter app
- [ ] Test on real device
- [ ] Submit to App Store
- [ ] Submit to Play Store

WEEK 3:
- [ ] Monitor errors (Sentry)
- [ ] Check metrics (api_call_metrics)
- [ ] Optimize slow endpoints
- [ ] Fine-tune ML model
- [ ] Launch!
```

---

## 💡 Pro Tips

1. **Parallel API Calls**: Both Google AND HERE in parallel (1 sec timeout each)
2. **Always Cache**: Weather, traffic data, verified delays
3. **Smart Timeouts**: 1s per source, 10s global max
4. **Monitor Confidence**: Track if too many fallbacks (< 70%)
5. **Batch ML Retraining**: Weekly with latest data
6. **Flood-Aware**: Multiply delay by risk_multiplier from stop_flood_mapping
7. **Real-Time Updates**: Use PostgreSQL NOTIFY for instant verification

---

## 🔗 Important Links

- **Vercel Docs**: https://vercel.com/docs/frameworks/python
- **FastAPI**: https://fastapi.tiangolo.com/
- **Supabase Realtime**: https://supabase.io/docs/guides/realtime
- **PostGIS**: https://postgis.net/documentation/
- **Flutter HTTP**: https://pub.dev/packages/http

---

## ✅ Success Criteria

Your app is ready when:
- ✅ `/api/health` returns `{"status": "healthy"}`
- ✅ Flutter shows map with green/yellow/red markers
- ✅ Predictions have `confidence_percentage > 70%`
- ✅ Reports create verified delays when 5+ occur
- ✅ Notifications queue correctly
- ✅ Sentry captures zero exceptions

---

**Created**: April 2, 2026  
**Version**: 1.0.0  
**Status**: 🚀 Production Ready

**Next Step**: Read IMPLEMENTATION_COMPLETE.md for full overview
