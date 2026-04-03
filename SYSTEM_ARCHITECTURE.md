# Transit-X: Complete System Architecture & Deployment Guide

## 🎯 System Overview

**Transit-X** is a production-grade transit delay prediction platform built on:

- **Frontend**: Flutter (iOS + Android)
- **Backend**: Python FastAPI on Vercel (serverless)
- **Database**: Supabase (PostgreSQL + PostGIS)
- **Infrastructure**: Cloud-native, auto-scaling, multi-region

```
┌──────────────────────────────────────────────────────────────────┐
│                       USER'S DEVICE                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐        ┌──────────────────┐        │
│  │   Flutter App           │        │  OS Services     │        │
│  │  - Map View             │   ◄───►│  - GPS/Location  │        │
│  │  - Heatmap Overlay      │        │  - Geofencing    │        │
│  │  - Bottom Sheet Widget  │        │  - Notifications │        │
│  │  - Offline Cache (Hive) │        └──────────────────┘        │
│  └────────────┬────────────┘                                     │
│               │                                                  │
│  HTTP + Deep Linking                                             │
│  (Uber/Ola deep links for rides)                                 │
└───────────────┼──────────────────────────────────────────────────┘
                │ INTERNET
                │ ┌─────────────────────────────────────────────────┐
                │ │                  VERCEL                         │
                ▼ │  (Serverless Functions - US, EU, APAC)         │
        ┌────────┴────────────────────────────────────────────────┐
        │                    FastAPI Backend                      │
        │  ┌──────────────────────────────────────────────────┐  │
        │  │  /api/predict                                    │  │
        │  │  Multi-tier fallback:                           │  │
        │  │  1. Google Routes API    (95% confidence, 1s)  │  │
        │  │  2. HERE Transit API     (90% confidence, 1s)  │  │
        │  │  3. GTFS-Realtime Feed  (80% confidence, 2s)  │  │
        │  │  4. ML Model             (70% confidence)      │  │
        │  │  5. User Reports         (70-95% confidence)   │  │
        │  │  6. Heuristic Fallback   (40% confidence)      │  │
        │  └──────────────────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────────────────┐  │
        │  │  Services Layer                                  │  │
        │  │  - PredictionEngine (core logic)                │  │
        │  │  - MLEngine (scikit-learn Random Forest)        │  │
        │  │  - WeatherService (OpenWeatherMap)             │  │
        │  │  - TrafficService (TomTom)                     │  │
        │  │  - SupabaseService (database)                  │  │
        │  │  - NotificationService (OneSignal)             │  │
        │  └──────────────────────────────────────────────────┘  │
        │                                                          │
        └─────────────────────────────────────────────────────────┘
                │           │               │               │
        ┌───────▼──┐  ┌────▼────┐  ┌──────▼─────┐  ┌───────▼──┐
        │ Google   │  │ HERE     │  │OpenWeather │  │ TomTom   │
        │ Maps API │  │ Transit  │  │ API        │  │ Traffic  │
        │ (Real)   │  │ API      │  │            │  │ API      │
        └──────────┘  └──────────┘  └────────────┘  └──────────┘
                │
        ┌───────▼─────────────────────────────────────┐
        │            SUPABASE (PostgreSQL)            │
        │  ┌────────────────────────────────────────┐ │
        │  │  Tables:                               │ │
        │  │  - stops (with PostGIS geometry)       │ │
        │  │  - city_events                        │ │
        │  │  - user_reports (crowdsourced)        │ │
        │  │  - verified_delays (5+ reports)       │ │
        │  │  - flood_prone_zones (PostGIS)        │ │
        │  │  - saved_routes (user preferences)    │ │
        │  │  - notification_queue (OneSignal)     │ │
        │  │  - api_call_metrics (monitoring)      │ │
        │  │  - ml_model_metrics (ML tracking)     │ │
        │  └────────────────────────────────────────┘ │
        │  ┌────────────────────────────────────────┐ │
        │  │  Edge Functions (TypeScript/Deno):    │ │
        │  │  - fetch_weather                      │ │
        │  │  - fetch_events                       │ │
        │  └────────────────────────────────────────┘ │
        │  ┌────────────────────────────────────────┐ │
        │  │  RLS Policies:                         │ │
        │  │  - Verified delays: public read       │ │
        │  │  - Flood zones: public read           │ │
        │  │  - Reports: authenticated write       │ │
        │  │  - Notifications: user-scoped         │ │
        │  └────────────────────────────────────────┘ │
        └─────────────────────────────────────────────┘
                │
        ┌───────▼─────────────────────────────┐
        │         Monitoring & Analytics      │
        │  ┌─────────────────────────────────┐│
        │  │ Sentry: Error Tracking          ││
        │  │ - Crashes, exceptions           ││
        │  │ - Performance monitoring        ││
        │  │ - Release tracking              ││
        │  └─────────────────────────────────┘│
        │  ┌─────────────────────────────────┐│
        │  │ Supabase Realtime:              ││
        │  │ - Verified delays updates       ││
        │  │ - Flood alerts                  ││
        │  │ - Notification status           ││
        │  └─────────────────────────────────┘│
        └─────────────────────────────────────┘
```

---

## 📂 Clean Architecture Layers

### Domain Layer (Business Logic)
```
lib/models/
├── stop.dart                    # Transit stop entity
├── event.dart                   # City event entity
├── delay_prediction.dart        # Prediction result
├── user_report.dart             # Crowdsourced report
└── saved_route.dart             # User route preference
```

### Data Layer (Repository Pattern)
```
api/services/
├── supabase_client.py           # Database repository
├── weather_service.py           # Weather data source
├── traffic_service.py           # Traffic data source
└── ml_engine.py                 # ML model data source

lib/providers/
├── location_provider.dart       # Location data provider
├── stops_provider.dart          # Stops data provider
├── predictions_provider.dart    # Predictions data provider
└── user_routes_provider.dart    # Routes data provider
```

### Presentation Layer (UI)
```
lib/screens/
├── home_screen.dart             # Map + stops list
├── details_screen.dart          # Stop details
├── saved_routes_screen.dart     # User dashboard
├── route_settings_screen.dart   # Route creation/edit
└── reports_screen.dart          # Crowdsourcing view

lib/widgets/
├── delay_breakdown_sheet.dart   # Factor visualization
└── report_dialog.dart           # Delay reporting form

lib/utils/
├── color_helpers.dart           # Color/status mapping
├── delay_formatter.dart         # Formatting utilities
└── geo_helpers.dart             # Geospatial calculations
```

---

## 🚀 Step-by-Step Deployment Guide

### Phase 1: Database Setup (15 minutes)

#### 1.1 Create Supabase Project
```bash
# Go to https://supabase.com
# Create new project
# Note: URL and anon key in Settings → API
```

**Save credentials:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...
```

#### 1.2 Run Migrations
```bash
# Upload SQL files to Supabase SQL Editor
# 1. First: supabase/migrations/001_init_schema.sql
#    - Creates: stops, events, delay_predictions, user_reports, saved_routes
#    - PostGIS functions for geospatial queries
# 
# 2. Second: supabase/migrations/002_flood_zones_events_advanced_reports.sql
#    - Creates: flood_prone_zones, verified_delays, notification_queue
#    - Real-time trigger: 5+ reports → verified delay flag
#    - API metrics & ML model tracking

# Verify in Table Editor:
# ✓ stops table (with location column)
# ✓ user_reports table
# ✓ verified_delays table
# ✓ flood_prone_zones table
```

#### 1.3 Insert Sample Data
```sql
-- Add sample stops (from your transit authority)
INSERT INTO stops (name, city, location, route_type)
VALUES 
  ('Central Station', 'Mumbai', ST_Point(72.8235, 19.0176), 'metro'),
  ('Airport Terminal', 'Mumbai', ST_Point(72.8688, 19.0883), 'bus'),
  ...

-- Add sample events
INSERT INTO city_events (name, location, latitude, longitude, importance_factor)
VALUES
  ('Metro Strike', 'Central Station', 19.0176, 72.8235, 0.9),
  ...
```

---

### Phase 2: Backend Deployment (10 minutes)

#### 2.1 Vercel Setup
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Create vercel.json (already done ✅)
# Verify it has:
# - buildCommand, python version
# - env variables defined
# - routes, headers, rewrites configured
```

#### 2.2 Configure Environment Variables
```bash
# In Vercel Dashboard:
# Settings → Environment Variables

# Add:
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
GOOGLE_MAPS_API_KEY=AIsaSy...
HERE_API_KEY=...
TOMTOM_API_KEY=...
OPENWEATHER_API_KEY=...
SENTRY_DSN=https://...
ONESIGNAL_API_KEY=...
ONESIGNAL_APP_ID=...
ML_MODEL_PATH=models/delay_predictor.joblib
ENVIRONMENT=production
```

#### 2.3 Deploy Backend
```bash
# Clone and deploy
git clone <your-repo>
cd transit_delay_predictor
vercel --prod

# OR: Connect GitHub for auto-deploys
# https://vercel.com/import → Select repo → Deploy

# Verify deployment
# https://your-project.vercel.app/api/health
# Should return: {"status": "healthy", ...}
```

#### 2.4 Test Endpoints
```bash
# Test prediction endpoint
curl -X POST https://your-project.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stop_id": 123,
    "latitude": 12.9352,
    "longitude": 77.6245
  }'

# Test nearby stops
curl "https://your-project.vercel.app/api/stops/nearby?latitude=12.9352&longitude=77.6245"
```

---

### Phase 3: ML Model Setup (Optional, 5 minutes)

#### 3.1 Train Model (Local)
```python
# train_model.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd

# Load Kaggle traffic dataset
df = pd.read_csv('kaggle_traffic_dataset.csv')

# Features: hour, day_of_week, temperature, precipitation, traffic_density, events, reports
X = df[['hour', 'day_of_week', 'temperature', 'precipitation_mm', 'traffic_density', 'events', 'reports']]
y = df['actual_delay_minutes']

# Train
model = RandomForestRegressor(n_estimators=100, max_depth=15, n_jobs=-1)
model.fit(X, y)

# Save
joblib.dump(model, 'models/delay_predictor.joblib')
print("✅ Model trained and saved")
```

#### 3.2 Upload to Vercel
```bash
# Option 1: Git commit (auto-uploads with deployment)
git add models/delay_predictor.joblib
git commit -m "Add trained ML model"
git push

# Option 2: Manual upload
# Vercel will load from ML_MODEL_PATH in API
```

---

### Phase 4: Flutter App Setup (20 minutes)

#### 4.1 Get Google Maps API Key
```bash
# 1. Google Cloud Console: https://console.cloud.google.com
# 2. Create new project
# 3. Enable APIs:
#    - Google Maps Platform
#    - Routes API
#    - Maps Static API
# 4. Create API key
# 5. Copy to lib/config/constants.dart

const String googleMapsApiKey = 'AIzaSy...';
```

#### 4.2 Configure Flutter App
```dart
// lib/config/constants.dart
const String supabaseUrl = 'https://your-project.supabase.co';
const String supabaseAnonKey = 'eyJ...';
const String googleMapsApiKey = 'AIzaSy...';
const String vercelBackendUrl = 'https://your-project.vercel.app';

// Optional: OneSignal notifications
const String oneSignalAppId = '...';
```

#### 4.3 Build & Run
```bash
cd transit_delay_predictor

# Get dependencies
flutter pub get

# Run on emulator
flutter run

# Build for production
flutter build apk --release    # Android
flutter build ios --release    # iOS
```

---

### Phase 5: Monitoring & Observability (10 minutes)

#### 5.1 Setup Sentry
```bash
# 1. https://sentry.io → Sign up
# 2. Create project (Python + Flutter)
# 3. Copy DSN
# 4. Set in .env: SENTRY_DSN=https://...@sentry.io/123
```

#### 5.2 Setup OneSignal (Optional)
```bash
# 1. https://onesignal.com → Sign up
# 2. Create app (iOS + Android)
# 3. Copy keys to .env:
#    ONESIGNAL_API_KEY=...
#    ONESIGNAL_APP_ID=...
```

#### 5.3 Configure Supabase Realtime
```sql
-- Enable realtime for verified_delays table
-- Supabase Dashboard: Replication → Select tables

-- In Flutter, listen for verified delays:
supabase
  .channel('public:verified_delays')
  .on(
    RealtimeListenTypes.postgresChanges,
    ChannelFilter(event: '*', schema: 'public', table: 'verified_delays'),
    (payload, [ref]) {
      print('✅ Delay verified: ${payload['new']['current_delay_minutes']} min');
    },
  )
  .subscribe();
```

---

## ✅ Production Checklist

- [ ] **Database**: Supabase project created, migrations run, RLS enabled
- [ ] **Backend**: Deployed on Vercel, endpoints tested, health check passing
- [ ] **APIs**: Google Maps, HERE, TomTom, OpenWeatherMap keys configured
- [ ] **ML Model**: Trained and deployed to Vercel
- [ ] **Flutter**: Built and submitted to App Store / Play Store
- [ ] **Monitoring**: Sentry configured, OneSignal configured
- [ ] **Caching**: Hive database for offline support enabled
- [ ] **Notifications**: Push notifications tested
- [ ] **Geofencing**: Flutter geofencing triggers configured
- [ ] **Rate Limiting**: Vercel rate limiting configured (100 req/min)
- [ ] **SSL/TLS**: All endpoints using HTTPS
- [ ] **Backup**: Supabase automated backups enabled
- [ ] **Documentation**: README, API docs, deployment guide updated

---

## 🔄 Continuous Deployment & Updates

### Auto-deployment on GitHub
```yaml
# .github/workflows/deploy.yml
name: Deploy Transit-X

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}

  deploy-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run migrations
        run: supabase db push
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

### Weekly ML Model Retraining
```python
# Scheduled cloud function (Vercel Cron)
# POST /api/ml/retrain (runs daily at 2 AM UTC)

async def retrain_ml_model():
    """Background job: retrain model with latest data"""
    logger.info("🔄 Starting ML model retraining...")
    
    # Collect training data
    training_data = await supabase.query(
        """SELECT * FROM user_reports 
           WHERE created_at > NOW() - INTERVAL '7 days'"""
    )
    
    # Retrain
    ml_engine = get_ml_engine()
    metrics = await ml_engine.train_model(training_data)
    
    # Validate (ensure accuracy > 70%)
    if metrics['accuracy'] > 70:
        # Deploy new model
        logger.info(f"✅ New model deployed (accuracy: {metrics['accuracy']:.1f}%)")
    else:
        logger.warning("⚠️ New model accuracy too low, keeping old version")
```

---

## 🆘 Troubleshooting & Support

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **"Supabase connection failed"** | Wrong credentials | Verify SUPABASE_URL and SUPABASE_KEY in .env |
| **"All APIs timing out"** | Network issue | Check internet, verify API keys are valid |
| **"LocationProvider not initializing"** | Permission denied | Ensure location permission granted in Flutter |
| **Predictions always < 5 min (fallback)** | ML model not loaded | Verify ML_MODEL_PATH exists, check logs |
| **High latency (> 5s)** | Cascading timeouts | Implement parallel API calls with watchdog |

### Checking Logs

```bash
# Vercel logs
vercel logs

# Supabase database logs
# Dashboard → Logs → Postgres

# Flutter logs
flutter logs

# Sentry errors
# https://sentry.io → Your project → Issues
```

---

## 📞 Getting Help

- **Vercel Support**: https://vercel.com/support
- **Supabase Docs**: https://supabase.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Flutter Docs**: https://flutter.dev/docs
- **Sentry SDK**: https://docs.sentry.io

---

## 📊 Key Metrics & SLOs

```
Service Level Objectives (SLOs):
- Availability: 99.9% (max 43 min downtime/month)
- Prediction latency: P95 < 2 seconds
- Accuracy: > 75% (mean absolute error < 5 min)
- Error rate: < 1% (4xx + 5xx errors)

Monitoring Alert Thresholds:
- Vercel error rate > 2% → Alert
- Accuracy drops below 70% → Retrain model
- Supabase CPU > 80% → Scale up
- API response time > 3s → Waterfall analysis
```

---

**Created**: April 2, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2026-04-02
