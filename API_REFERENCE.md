# Transit Delay Predictor - API Reference

## REST API Endpoints

### Supabase Edge Functions

#### 1. Fetch Weather

**Endpoint**: `POST /functions/v1/fetch_weather`

**Request**:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "apiKey": "YOUR_OPENWEATHERMAP_KEY"
}
```

**Response** (Success - 200):
```json
{
  "condition": "rain",
  "intensity": 0.8,
  "temperature": 15.5,
  "humidity": 85,
  "wind_speed": 12.3,
  "description": "light rain"
}
```

**Response** (Error - 500):
```json
{
  "error": "Failed to fetch weather: {error_message}"
}
```

**Weather Conditions**:
- `clear` - Clear sky
- `clouds` - Cloudy
- `rain` - Rain
- `drizzle` - Drizzle
- `thunderstorm` - Thunderstorm
- `snow` - Snow
- `mist`/`fog` - Visibility issues
- `wind` - Strong wind

**Intensity Scale** (0.0 - 1.0):
- 0.0 - 0.2: Low (minimal impact)
- 0.2 - 0.5: Moderate (some impact)
- 0.5 - 0.8: High (significant impact)
- 0.8 - 1.0: Extreme (severe impact)

---

#### 2. Fetch Events

**Endpoint**: `POST /functions/v1/fetch_events`

**Request**:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radiusMeters": 2000
}
```

**Response** (Success - 200):
```json
{
  "total": 2,
  "events": [
    {
      "id": "uuid-123",
      "event_name": "IPL Cricket Match",
      "importance_level": "critical",
      "event_type": "sports",
      "distance_meters": 500,
      "impact_radius_meters": 1500,
      "is_active": true
    },
    {
      "id": "uuid-456",
      "event_name": "Music Concert",
      "importance_level": "high",
      "event_type": "concert",
      "distance_meters": 1200,
      "impact_radius_meters": 1000,
      "is_active": true
    }
  ]
}
```

**Event Types**:
- `sports` - Sports event
- `concert` - Music/entertainment
- `protest` - Public protest
- `construction` - Road construction
- `accident` - Traffic accident
- `weather` - Weather-related closure
- `other` - Other

**Importance Levels**:
- `critical` - Max 20 min delay
- `high` - Up to 12 min delay
- `medium` - Up to 6 min delay
- `low` - Up to 2 min delay

---

## Supabase Tables API

### Stops Table

**Create** (Admin):
```dart
final response = await supabase
  .from('stops')
  .insert({
    'name': 'Central Station',
    'location': 'SRID=4326;POINT(40.7128 -74.0060)',
    'route_type': 'train',
    'stop_code': 'CS001',
    'avg_daily_passengers': 50000,
  })
  .select();
```

**Read** (Public):
```dart
final response = await supabase
  .from('stops')
  .select()
  .order('name');
```

**Nearby Stops** (Function):
```dart
final response = await supabase.rpc('get_nearby_stops', params: {
  'p_latitude': 40.7128,
  'p_longitude': -74.0060,
  'p_radius_meters': 2000,
});
```

---

### Events Table

**Create**:
```dart
final response = await supabase
  .from('events')
  .insert({
    'event_name': 'Cricket Match',
    'location': 'SRID=4326;POINT(40.7128 -74.0060)',
    'start_time': DateTime.now().toIso8601String(),
    'end_time': DateTime.now().add(Duration(hours: 3)).toIso8601String(),
    'impact_radius_meters': 1500,
    'importance_level': 'critical',
    'event_type': 'sports',
  })
  .select();
```

**Get Active Events By Location**:
```dart
final response = await supabase.rpc('get_nearby_active_events', params: {
  'p_latitude': 40.7128,
  'p_longitude': -74.0060,
  'p_radius_meters': 2000,
});
```

---

### Delay Predictions Table

**Create**:
```dart
final response = await supabase
  .from('delay_predictions')
  .insert({
    'stop_id': 'stop-uuid',
    'predicted_delay_minutes': 12,
    'weather_condition': 'rain',
    'weather_intensity': 0.8,
    'event_proximity_meters': 500,
    'event_impact_factor': 0.7,
    'time_of_day_factor': 0.8,
    'day_of_week': 'Monday',
    'confidence_score': 0.85,
    'model_version': '1.0',
  })
  .select();
```

**Get Latest Prediction**:
```dart
final response = await supabase
  .from('delay_predictions')
  .select()
  .eq('stop_id', 'stop-uuid')
  .order('created_at', ascending: false)
  .limit(1)
  .single();
```

---

### User Reports Table

**Create**:
```dart
final response = await supabase
  .from('user_reports')
  .insert({
    'user_id': 'user-uuid',
    'stop_id': 'stop-uuid',
    'reported_delay_minutes': 15,
    'weather_condition': 'rain',
    'passenger_count': 45,
    'report_accuracy_rating': 4,
    'additional_notes': 'Heavy rain causing delays',
  })
  .select();
```

---

### Saved Routes Table

**Create**:
```dart
final response = await supabase
  .from('saved_routes')
  .insert({
    'user_id': 'user-uuid',
    'route_name': 'Home to Office',
    'start_stop_id': 'stop-1',
    'end_stop_id': 'stop-2',
    'route_type': 'bus',
    'estimated_duration_minutes': 45,
    'notification_enabled': true,
    'notification_threshold_minutes': 10,
  })
  .select();
```

**Update**:
```dart
final response = await supabase
  .from('saved_routes')
  .update({
    'favorite': true,
    'notification_threshold_minutes': 15,
  })
  .eq('id', 'route-uuid')
  .select();
```

---

## Authentication (Future)

### Sign Up

```dart
final response = await supabase.auth.signUp(
  email: 'user@example.com',
  password: 'secure_password',
);
```

### Sign In

```dart
final response = await supabase.auth.signInWithPassword(
  email: 'user@example.com',
  password: 'password',
);
```

### Get Current User

```dart
final user = supabase.auth.currentUser;
```

---

## Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | Success | Request succeeded |
| 400 | Bad Request | Missing or invalid parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | User not allowed |
| 404 | Not Found | Resource not found |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Service temporarily down |

---

## Rate Limiting

- **OpenWeatherMap**: 1000 calls/day (free tier)
- **Google Maps**: Check your API plan quotas
- **Supabase**: 200 requests/second for free plan

---

## CORS Policy

All requests should include headers:
```
Content-Type: application/json
Authorization: Bearer <anon_key>
```

---

## Example Usage (Flutter)

### Get Prediction for a Stop

```dart
// 1. Get weather
final weather = await weatherService.getWeatherData(lat, lon);

// 2. Get nearby events
final events = await supabaseService.getNearbyActiveEvents(lat, lon);

// 3. Generate prediction
final prediction = predictionService.calculateDelay(
  stopId: stop.id,
  weatherIntensity: weather['intensity'],
  weatherCondition: weather['condition'],
  nearbyEvents: events,
  eventProximityMeters: eventProx,
  currentTime: DateTime.now(),
);

// 4. Save to database
await supabaseService.savePrediction(prediction);
```

### Monitor a Route

```dart
// 1. Get saved route
final route = userRoutesProvider.savedRoutes[0];

// 2. Generate prediction for start stop
final prediction = await predictionsProvider.generatePrediction(
  stop: startStop,
  userLatitude: location.latitude,
  userLongitude: location.longitude,
);

// 3. Check threshold and notify
if (prediction.predictedDelayMinutes > route.notificationThresholdMinutes) {
  await notificationService.showDelayAlert(
    routeName: route.routeName,
    delayMinutes: prediction.predictedDelayMinutes,
    stopName: startStop.name,
  );
}
```

---

## Pagination Example

```dart
// Get page 1 (10 items per page)
final response = await supabase
  .from('stops')
  .select()
  .range(0, 9);  // 0-indexed, inclusive

// Get page 2
final response = await supabase
  .from('stops')
  .select()
  .range(10, 19);
```

---

## Troubleshooting

### "Location not provided"
Ensure latitude and longitude are sent with API request

### "API key invalid"
Verify API key in `.env` or constants

### "Timeout"
- Increase timeout threshold
- Check network connectivity
- Verify API endpoint is accessible

### "CORS error"
- Check browser console for headers issue
- Verify Supabase CORS settings
- Use Supabase client instead of direct HTTP

---

## Support

For API documentation questions:
- Supabase: https://supabase.com/docs
- OpenWeatherMap: https://openweathermap.org/api
- Google Maps: https://developers.google.com/maps/documentation
