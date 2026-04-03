# Transit Delay Predictor - Setup Guide

## Project Overview

A cross-platform Flutter mobile app that predicts public transport delays using machine learning, real-time weather data, and local events. The app combines historical delay patterns with live data to provide accurate delay predictions.

## Prerequisites

- **Flutter SDK**: >= 3.0.0
- **Dart**: >= 3.0.0
- **Supabase Account**: https://supabase.com
- **Google Maps API Key**: https://cloud.google.com/maps/apis
- **OpenWeatherMap API Key**: https://openweathermap.org/api

## Step 1: Supabase Setup

### 1.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Note your project URL and Anon Key

### 1.2 Enable PostGIS Extension

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Run this query:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
4. Click Execute

### 1.3 Run Database Migration

1. In SQL Editor, click "New Query"
2. Copy contents of `supabase/migrations/001_init_schema.sql`
3. Paste into the query editor
4. Click Execute

### 1.4 Configure Supabase in Project

Update `lib/config/supabase_config.dart`:
```dart
const String supabaseUrl = 'https://YOUR_PROJECT_ID.supabase.co';
const String supabaseAnonKey = 'YOUR_ANON_KEY';
```

## Step 2: Google Maps Setup

### 2.1 Get API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Maps SDK for Android** and **Maps SDK for iOS**
4. Go to Credentials and create an API key

### 2.2 Android Configuration

Edit `android/app/src/main/AndroidManifest.xml`:
```xml
<manifest ... >
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    
    <application>
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="YOUR_GOOGLE_MAPS_API_KEY"/>
    </application>
</manifest>
```

### 2.3 iOS Configuration

Edit `ios/Runner/Info.plist`:
```xml
<dict>
    ...
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>This app needs your location to show nearby transport stops</string>
    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>This app needs your location to show nearby transport stops</string>
    <key>com.google.ios.maps.API_KEY</key>
    <string>YOUR_GOOGLE_MAPS_API_KEY</string>
    ...
</dict>
```

## Step 3: Weather API Setup

Update `lib/config/constants.dart`:
```dart
class ApiConfig {
  static const String openWeatherMapApiKey = 'YOUR_OPENWEATHERMAP_API_KEY';
  static const String googleMapsApiKey = 'YOUR_GOOGLE_MAPS_API_KEY';
  // ...
}
```

## Step 4: Supabase Edge Functions

### 4.1 Install Supabase CLI

```bash
npm install -g supabase
```

### 4.2 Login to Supabase

```bash
supabase login
```

### 4.3 Link Project

```bash
cd transit_delay_predictor
supabase link --project-ref YOUR_PROJECT_ID
```

### 4.4 Deploy Edge Functions

```bash
supabase functions deploy fetch_weather
supabase functions deploy fetch_events
```

### 4.5 Test Functions

```bash
# Test fetch_weather function
supabase functions invoke fetch_weather --body '{
  "latitude": 0.0,
  "longitude": 0.0,
  "apiKey": "YOUR_OPENWEATHERMAP_API_KEY"
}'
```

## Step 5: Flutter Project Setup

### 5.1 Get Dependencies

```bash
cd transit_delay_predictor
flutter pub get
```

### 5.2 Generate Build Files (Android)

```bash
cd android
./gradlew clean
cd ..
```

### 5.3 Run the App

#### Development (Debug)
```bash
flutter run
```

#### Release
```bash
flutter run --release
```

#### Specific Device
```bash
flutter devices  # List available devices
flutter run -d <device_id>
```

## Step 6: Database Sample Data

The migration script includes sample stops and events. To add more:

```sql
INSERT INTO stops (name, location, route_type, stop_code, avg_daily_passengers)
VALUES
  ('Your Stop', ST_SetSRID(ST_Point(longitude, latitude), 4326), 'bus', 'CODE001', 10000);

INSERT INTO events (event_name, location, start_time, end_time, impact_radius_meters, importance_level, event_type)
VALUES
  ('Event Name', ST_SetSRID(ST_Point(longitude, latitude), 4326), NOW(), NOW() + INTERVAL '2 hours', 1000, 'high', 'concert');
```

## API Integration Points

### OpenWeatherMap

**Endpoint**: `/data/2.5/weather?lat={lat}&lon={lon}&appid={key}`

**Response Fields Used**:
- `weather[0].main`: Weather condition
- `main.temp`: Temperature
- `main.humidity`: Humidity
- `wind.speed`: Wind speed

### Supabase Edge Functions

**fetch_weather**: Get weather data and intensity score

**fetch_events**: Get nearby active events with proximity

## Testing

### Run Unit Tests

```bash
flutter test
```

### Test Specific File

```bash
flutter test test/services/prediction_service_test.dart
```

### Generate Coverage Report

```bash
flutter test --coverage
lcov --list coverage/lcov.info
```

## Build for Production

### Android APK

```bash
flutter build apk --release
```

### Android App Bundle

```bash
flutter build appbundle --release
```

### iOS

```bash
flutter build ios --release
```

## Troubleshooting

### Location Permission Issues

- **Android**: Check `android/app/src/main/AndroidManifest.xml` has permission declarations
- **iOS**: Check `ios/Runner/Info.plist` has usage descriptions
- **Both**: Ensure user allows permission at runtime

### Maps Not Showing

- Verify Google Maps API key is correct
- Check API is enabled in Google Cloud Console
- Clear app cache and reinstall

### Supabase Connection Failed

- Verify Supabase URL and Anon Key are correct
- Check internet connection
- Verify database is running (check Supabase dashboard)

### Weather Data Not Loading

- Verify OpenWeatherMap API key is correct
- Check API call quota hasn't been exceeded
- Verify latitude/longitude are correct

## Architecture Overview

```
Flutter App (UI Layer)
    ↓
State Management (Provider Pattern)
    ↓
Services Layer (Business Logic)
    ├── Supabase Service
    ├── Weather Service
    ├── Prediction Service
    ├── Location Service
    └── Notification Service
    ↓
External APIs
    ├── Supabase (Database + Edge Functions)
    ├── OpenWeatherMap API
    ├── Google Maps API
    └── Device Services (Location, Notifications)
```

## Prediction Algorithm

The ML-inspired prediction engine uses weighted factors:

1. **Weather Intensity** (40%)
   - Rain: High impact (5-15 min)
   - Thunderstorm: Extreme (15+ min)
   - Snow: Very high (12 min)
   - Other: Lower impact

2. **Event Proximity** (50%)
   - Critical events near stops: 20 min
   - High importance: 12 min
   - Medium: 6 min
   - Distance decay: Impact decreases with distance

3. **Time of Day** (10%)
   - Peak hours (7-9 AM, 5-7 PM): 8 min
   - Mid-day: 4 min
   - Off-peak: 1 min

**Confidence Score**: Based on available data (0.3-0.95)

## Development Tips

### Add New Screen

1. Create file in `lib/screens/`
2. Add route in `main.dart` or use `Navigator.push()`
3. Create corresponding provider if needed

### Add New Service

1. Create singleton in `lib/services/`
2. Use in providers or UI directly via `context.read<>()`

### Update Database Schema

1. Create new migration SQL file
2. Run in Supabase SQL Editor
3. Update model classes if needed

### Debug Predictions

Enable logging in `prediction_service.dart`:
```dart
_logger.d('Prediction details: $prediction');
```

View logs:
```bash
flutter logs
```

## Performance Optimization

- Cache predictions for 30 minutes
- Batch location updates (30s intervals)
- Lazy load map tiles
- Limit nearby stops to 50 results
- Use geospatial indexes in database

## Security Considerations

- Store API keys in `.env` file (use `flutter_dotenv`)
- Enable RLS policies in Supabase
- Validate user input before API calls
- Use HTTPS for all API requests
- Implement rate limiting for API calls

## Next Steps

1. Implement user authentication (Supabase Auth)
2. Add more sophisticated ML model (TensorFlow Lite)
3. Implement offline caching
4. Add real-time updates via WebSocket
5. Create admin dashboard for event management
6. Implement user analytics and telemetry

## Support & Documentation

- **Flutter Docs**: https://flutter.dev/docs
- **Supabase Docs**: https://supabase.com/docs
- **Google Maps Docs**: https://developers.google.com/maps
- **OpenWeatherMap Docs**: https://openweathermap.org/api

## License

MIT License - See LICENSE file for details
