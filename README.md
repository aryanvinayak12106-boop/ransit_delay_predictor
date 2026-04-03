# Transit Delay Predictor

A cross-platform Flutter mobile app that predicts public transport delays using machine learning, real-time weather data, and local events.

## Features

- **Live Map View**: Real-time Google Maps showing transport stops with color-coded delay predictions
- **Real-time Prediction Engine**: ML-based predictions combining weather, events, and time of day
- **User Dashboard**: Save routes and receive notifications for significant delays
- **Crowdsourcing**: Report actual delays to improve predictions
- **Delay Breakdown**: Detailed explanation of delay factors (weather, events, time)

## Tech Stack

- **Frontend**: Flutter with Material 3, Google Maps
- **Backend**: Supabase (PostgreSQL + PostGIS)
- **ML Logic**: Random Forest inspired prediction engine
- **External APIs**: OpenWeatherMap

## Project Structure

```
transit_delay_predictor/
├── lib/
│   ├── main.dart                          # App entry point
│   ├── config/
│   │   ├── supabase_config.dart          # Supabase initialization
│   │   └── constants.dart                 # App constants
│   ├── models/
│   │   ├── stop.dart                      # Transport stop model
│   │   ├── event.dart                     # City event model
│   │   ├── delay_prediction.dart          # Prediction result model
│   │   └── user_report.dart               # User crowdsource report
│   ├── services/
│   │   ├── supabase_service.dart          # Supabase database operations
│   │   ├── weather_service.dart           # OpenWeatherMap integration
│   │   ├── prediction_service.dart        # ML prediction logic
│   │   ├── location_service.dart          # Geolocation handling
│   │   └── notification_service.dart      # Local notifications
│   ├── providers/
│   │   ├── stops_provider.dart            # Stops state management
│   │   ├── predictions_provider.dart      # Predictions state management
│   │   ├── user_routes_provider.dart      # User saved routes
│   │   └── location_provider.dart         # User location state
│   ├── screens/
│   │   ├── home_screen.dart               # Main map view
│   │   ├── details_screen.dart            # Stop details & predictions
│   │   ├── saved_routes_screen.dart       # Dashboard
│   │   ├── route_settings_screen.dart     # Add/edit routes
│   │   └── reports_screen.dart            # Crowdsourcing interface
│   ├── widgets/
│   │   ├── map_view.dart                  # Google Maps widget
│   │   ├── delay_breakdown_sheet.dart     # Delay explanation UI
│   │   ├── stop_marker.dart               # Custom map markers
│   │   ├── prediction_card.dart           # Prediction display card
│   │   └── report_dialog.dart             # Report delay dialog
│   └── utils/
│       ├── delay_formatter.dart           # Format delay display
│       ├── color_helpers.dart             # Color coding logic
│       └── geo_helpers.dart               # Geographic calculations
├── supabase/
│   ├── migrations/
│   │   └── 001_init_schema.sql            # Database schema
│   └── functions/
│       ├── predict_delay/
│       │   └── index.ts                   # Edge Function for predictions
│       └── fetch_events/
│           └── index.ts                   # Edge Function for events
├── assets/
│   ├── images/
│   ├── icons/
│   └── data/
├── pubspec.yaml
└── README.md
```

## Getting Started

### Prerequisites

- Flutter SDK (>=3.0.0)
- Supabase account
- Google Maps API key
- OpenWeatherMap API key

### Setup Instructions

1. **Clone/Create Flutter Project**
   ```bash
   cd transit_delay_predictor
   flutter pub get
   ```

2. **Configure Supabase**
   - Create a new Supabase project
   - Enable PostGIS extension
   - Run the migration SQL
   - Update credentials in `lib/config/supabase_config.dart`

3. **Setup Google Maps**
   - Obtain API key from Google Cloud Console
   - Add to `AndroidManifest.xml` and `Info.plist`

4. **Configure OpenWeatherMap**
   - Get API key from OpenWeatherMap
   - Add to environment variables

5. **Run the App**
   ```bash
   flutter run
   ```

## Database Schema

See `supabase/migrations/001_init_schema.sql` for complete schema including:
- stops (transport stops with geographic location)
- events (city events with impact radius)
- delay_predictions (ML predictions)
- user_reports (crowdsourcing data)
- saved_routes (user preferences)

## ML Prediction Logic

The prediction engine weighs factors as follows:
- **Rain/Weather**: High impact (40%)
- **Event Proximity**: Extreme impact (50%)
- **Time of Day**: Low impact (10%)
- **Base delay**: Varies by stop type

## API Documentation

See `/docs` directory for:
- Supabase Edge Functions API
- Weather Service Integration
- Prediction Service Interface

## Contributing

1. Create a feature branch
2. Make changes
3. Submit pull request

## License

MIT License
