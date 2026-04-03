# Transit Delay Predictor - Implementation Notes

## Project Structure Explanation

### `/lib/config/`
- **supabase_config.dart**: Supabase client initialization
- **constants.dart**: App-wide configuration, colors, themes, API keys

### `/lib/models/`
- **stop.dart**: Transport stop model with location data
- **event.dart**: City event model with impact radius
- **delay_prediction.dart**: ML prediction results with breakdown
- **user_report.dart**: Crowdsourced delay reports
- **saved_route.dart**: User's saved routes with preferences

### `/lib/services/`
- **supabase_service.dart**: Database operations (CRUD)
- **weather_service.dart**: OpenWeatherMap API integration
- **prediction_service.dart**: ML-inspired prediction engine
- **location_service.dart**: GPS and geolocation management
- **notification_service.dart**: Local push notifications

### `/lib/providers/`
State management using Provider pattern:
- **location_provider.dart**: User's current location state
- **stops_provider.dart**: Available stops and nearby stops
- **predictions_provider.dart**: Delay predictions and caching
- **user_routes_provider.dart**: Saved routes management

### `/lib/screens/`
- **home_screen.dart**: Main map view with stops
- **details_screen.dart**: Stop details and predictions
- **saved_routes_screen.dart**: Dashboard of user routes
- **route_settings_screen.dart**: Create/edit route settings
- **reports_screen.dart**: View submitted reports

### `/lib/widgets/`
Reusable UI components:
- **delay_breakdown_sheet.dart**: Shows delay factors breakdown
- **report_dialog.dart**: Report actual delay dialog
- Custom map markers and prediction cards

### `/lib/utils/`
- **color_helpers.dart**: Delay state color coding
- **delay_formatter.dart**: Format delays, times, distances

### `/supabase/`
- **migrations/001_init_schema.sql**: Complete database schema
- **functions/fetch_weather/**: Edge function for weather
- **functions/fetch_events/**: Edge function for events

## Key Algorithms

### Delay Prediction Engine

```
Total Delay = (Weather Delay × 0.4) + (Event Delay × 0.5) + (Time Delay × 0.1)

Weather Delay:
- Clear: 0 min
- Clouds: 1-2 min
- Rain: 10 min × intensity (0-1)
- Thunder: 15 min
- Snow: 12 min

Event Delay:
- Based on event importance (critical=20m, high=12m, medium=6m)
- Multiplied by proximity factor (0-1)
- Closer events have more impact

Time Delay:
- Peak hours (7-9 AM, 5-7 PM): 8 min
- Mid-day (9-5): 4 min
- Off-peak (10 PM-7 AM): 1 min
```

### Confidence Score Calculation

```
Base: 0.5
+ Weather data: 0.15
+ Nearby events: 0.15-0.25 (more for critical)
= Final: 0.3-0.95
```

## Database Schema Highlights

### PostGIS Usage

```sql
-- Store locations as geographic points
location GEOGRAPHY(POINT, 4326)

-- Find nearby stops
ST_Distance(stops.location, point) <= radius

-- Create spatial indexes for performance
CREATE INDEX idx_stops_location ON stops USING GIST (location);
```

### Security (RLS Policies)

- Public can read stops and events
- Users can only manage their own routes
- Verified users can create reports

### Optimization

- Predictions expire after 30 minutes
- Spatial indexes on location columns
- Indices on frequently queried fields (user_id, stop_id)

## Real-time Features

### Location Updates
- Start when app initializes
- Poll every 30 seconds
- Trigger prediction updates when near stops

### Notification Triggers
```dart
if (predictedDelay > route.notificationThreshold) {
  showNotification("Your route delayed by $predictedDelay minutes");
}
```

### Map Updates
- Markers update as predictions change
- Color-coded based on delay category
- Click to view detailed breakdown

## API Integrations

### OpenWeatherMap
- Called for each nearby stop
- Caches results for 30 minutes
- Provides weather intensity (0-1 scale)

### Supabase Edge Functions
- **fetch_weather**: Proxy weather requests for cost optimization
- **fetch_events**: Query events with PostGIS filtering
- Run on Deno runtime (TypeScript)

## State Flow

```
LocationProvider updates user position
    ↓
StopsProvider fetches nearby stops
    ↓
PredictionsProvider generates predictions for each stop
    ↓
UI updates with color-coded markers
    ↓
User clicks marker
    ↓
DetailsScreen shows breakdown and options
    ↓
User can report/save route
    ↓
UserRoutesProvider saves to database
    ↓
NotificationService alerts for saved route delays
```

## Material 3 Design Implementation

- **Color Scheme**: Seeded from primary color
- **Typography**: Uses Material 3 text styles
- **Components**: Material 3 buttons, cards, dialogs
- **Dark Mode**: Supported via system theme
- **Accessibility**: Uses semantic colors and sizes

## Error Handling Strategy

1. **Network Errors**: Show snackbars with retry buttons
2. **Permission Errors**: Direct to settings
3. **Database Errors**: Fallback to local cache
4. **API Errors**: Graceful degradation with default values

## Performance Considerations

- **Lazy Loading**: Map loads tiles on demand
- **Pagination**: Limits nearby stops to 50
- **Caching**: Predictions cached in memory
- **Background Tasks**: Location updates in background
- **Image Optimization**: Vector icons where possible

## Testing Strategy

### Unit Tests
- Prediction algorithm accuracy
- Distance calculations
- Color mapping logic

### Widget Tests
- Screen rendering
- User interactions
- Form validation

### Integration Tests
- Supabase connectivity
- API response handling
- End-to-end user flows

### Manual Testing
- Location permissions
- Map interaction
- Notification display
- Database CRUD operations

## Future Enhancements

1. **Machine Learning**
   - Replace simplified logic with TensorFlow Lite model
   - Train on historical user reports
   - Continuous model improvement

2. **Social Features**
   - Real-time delay crowdsourcing
   - User profiles and contributions
   - Leaderboards for accurate reporters

3. **Advanced Analytics**
   - Predictability score by stop
   - Seasonal patterns
   - Route optimization suggestions

4. **Integration Expansions**
   - Transit agency APIs (GTFS)
   - Social media event detection
   - Traffic incident feeds

5. **Accessibility**
   - Voice narration for delays
   - High contrast mode
   - Reduced motion options

## Deployment Checklist

- [ ] Update API keys in configuration
- [ ] Test on physical devices
- [ ] Run full test suite
- [ ] Clear debug logs
- [ ] Optimize assets
- [ ] Set up error tracking (Sentry)
- [ ] Configure analytics
- [ ] Review privacy policy
- [ ] Test offline functionality
- [ ] Prepare app store listings

## Maintenance

### Regular Updates
- Update dependencies monthly
- Monitor API rate limits
- Review error logs weekly
- Update sample data monthly

### Monitoring
- Set up error tracking
- Monitor API performance
- Track user analytics
- Alert on threshold breaches

### Security
- Rotate API keys regularly
- Audit database access logs
- Review RLS policies
- Update dependencies for vulnerabilities
