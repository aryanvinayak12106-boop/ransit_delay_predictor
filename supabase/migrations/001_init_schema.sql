-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for fresh migrations)
DROP TABLE IF EXISTS user_reports CASCADE;
DROP TABLE IF EXISTS saved_routes CASCADE;
DROP TABLE IF EXISTS delay_predictions CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- User Profiles Table
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  preferred_transport_types TEXT[] DEFAULT '{}',
  notification_enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transport Stops Table
CREATE TABLE stops (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  route_type TEXT NOT NULL CHECK (route_type IN ('bus', 'metro', 'train', 'tram', 'cable_car')),
  stop_code TEXT UNIQUE,
  avg_daily_passengers INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create spatial index on stops
CREATE INDEX idx_stops_location ON stops USING GIST (location);
CREATE INDEX idx_stops_route_type ON stops(route_type);

-- City Events Table
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_name TEXT NOT NULL,
  event_description TEXT,
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE NOT NULL,
  impact_radius_meters INTEGER NOT NULL DEFAULT 1000,
  importance_level TEXT DEFAULT 'medium' CHECK (importance_level IN ('low', 'medium', 'high', 'critical')),
  event_type TEXT NOT NULL CHECK (event_type IN ('sports', 'concert', 'protest', 'construction', 'accident', 'weather', 'other')),
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create spatial index on events
CREATE INDEX idx_events_location ON events USING GIST (location);
CREATE INDEX idx_events_time_range ON events(start_time, end_time);
CREATE INDEX idx_events_importance ON events(importance_level);

-- Delay Predictions Table
CREATE TABLE delay_predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  stop_id UUID NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
  predicted_delay_minutes INTEGER NOT NULL,
  weather_condition TEXT,
  weather_intensity DECIMAL(3, 2) NOT NULL DEFAULT 0,
  event_proximity_meters INTEGER,
  event_impact_factor DECIMAL(3, 2) DEFAULT 0,
  time_of_day_factor DECIMAL(3, 2) DEFAULT 0,
  day_of_week TEXT,
  confidence_score DECIMAL(3, 2) NOT NULL DEFAULT 0.5,
  model_version TEXT DEFAULT '1.0',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 minutes')
);

-- Create indexes for predictions
CREATE INDEX idx_predictions_stop_id ON delay_predictions(stop_id);
CREATE INDEX idx_predictions_created_at ON delay_predictions(created_at);
CREATE INDEX idx_predictions_expires_at ON delay_predictions(expires_at);

-- User Reports Table (Crowdsourcing)
CREATE TABLE user_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  stop_id UUID NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
  reported_delay_minutes INTEGER NOT NULL,
  weather_condition TEXT,
  passenger_count INTEGER,
  report_accuracy_rating INTEGER CHECK (report_accuracy_rating BETWEEN 1 AND 5),
  additional_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  verified BOOLEAN DEFAULT false,
  verified_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  verified_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for reports
CREATE INDEX idx_reports_user_id ON user_reports(user_id);
CREATE INDEX idx_reports_stop_id ON user_reports(stop_id);
CREATE INDEX idx_reports_created_at ON user_reports(created_at);
CREATE INDEX idx_reports_verified ON user_reports(verified);

-- Saved Routes Table
CREATE TABLE saved_routes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  route_name TEXT NOT NULL,
  start_stop_id UUID NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
  end_stop_id UUID NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
  route_type TEXT NOT NULL,
  estimated_duration_minutes INTEGER,
  favorite BOOLEAN DEFAULT false,
  notification_enabled BOOLEAN DEFAULT true,
  notification_threshold_minutes INTEGER DEFAULT 10,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for saved routes
CREATE INDEX idx_saved_routes_user_id ON saved_routes(user_id);
CREATE INDEX idx_saved_routes_favorite ON saved_routes(favorite);
CREATE INDEX idx_saved_routes_created_at ON saved_routes(created_at);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE stops ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE delay_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_routes ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_profiles
CREATE POLICY "Users can read their own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = user_id);

-- RLS Policies for stops (public readable)
CREATE POLICY "Stops are publicly readable"
  ON stops FOR SELECT
  USING (true);

-- RLS Policies for events (public readable)
CREATE POLICY "Events are publicly readable"
  ON events FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can create events"
  ON events FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- RLS Policies for delay_predictions (public readable)
CREATE POLICY "Predictions are publicly readable"
  ON delay_predictions FOR SELECT
  USING (true);

-- RLS Policies for user_reports
CREATE POLICY "Users can view their own reports"
  ON user_reports FOR SELECT
  USING (auth.uid() = user_id OR auth.role() = 'authenticated');

CREATE POLICY "Users can create reports"
  ON user_reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for saved_routes
CREATE POLICY "Users can manage their own routes"
  ON saved_routes FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create routes"
  ON saved_routes FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their routes"
  ON saved_routes FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their routes"
  ON saved_routes FOR DELETE
  USING (auth.uid() = user_id);

-- Update timestamps function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stops_updated_at BEFORE UPDATE ON stops
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_routes_updated_at BEFORE UPDATE ON saved_routes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for active events (within impact time)
CREATE OR REPLACE VIEW active_events AS
SELECT *
FROM events
WHERE start_time <= NOW()
  AND end_time >= NOW();

-- View for nearby events with distance
CREATE OR REPLACE VIEW events_with_distance AS
SELECT 
  id,
  event_name,
  event_description,
  location,
  start_time,
  end_time,
  impact_radius_meters,
  importance_level,
  event_type,
  created_by,
  created_at,
  updated_at,
  ST_Distance(location, ST_SetSRID(ST_Point(0, 0), 4326))::integer as distance_meters
FROM events;

-- Function to find stops by proximity
CREATE OR REPLACE FUNCTION get_nearby_stops(
  p_longitude DECIMAL,
  p_latitude DECIMAL,
  p_radius_meters INTEGER DEFAULT 2000
)
RETURNS TABLE (
  id UUID,
  name TEXT,
  route_type TEXT,
  distance_meters BIGINT,
  location GEOGRAPHY
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    stops.id,
    stops.name,
    stops.route_type,
    ST_Distance(stops.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326))::bigint,
    stops.location
  FROM stops
  WHERE ST_Distance(stops.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326)) <= p_radius_meters
  ORDER BY ST_Distance(stops.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326))
  LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- Function to find events by proximity
CREATE OR REPLACE FUNCTION get_nearby_active_events(
  p_longitude DECIMAL,
  p_latitude DECIMAL,
  p_radius_meters INTEGER DEFAULT 2000
)
RETURNS TABLE (
  id UUID,
  event_name TEXT,
  impact_radius_meters INTEGER,
  importance_level TEXT,
  event_type TEXT,
  distance_meters BIGINT,
  location GEOGRAPHY,
  start_time TIMESTAMP WITH TIME ZONE,
  end_time TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    events.id,
    events.event_name,
    events.impact_radius_meters,
    events.importance_level,
    events.event_type,
    ST_Distance(events.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326))::bigint,
    events.location,
    events.start_time,
    events.end_time
  FROM events
  WHERE ST_Distance(events.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326)) <= p_radius_meters
    AND events.start_time <= NOW()
    AND events.end_time >= NOW()
  ORDER BY events.importance_level DESC, 
           ST_Distance(events.location, ST_SetSRID(ST_Point(p_longitude, p_latitude), 4326));
END;
$$ LANGUAGE plpgsql;

-- Insert sample stops for testing
INSERT INTO stops (name, location, route_type, stop_code, avg_daily_passengers)
VALUES
  ('Central Station', ST_SetSRID(ST_Point(0.0, 0.0), 4326), 'train', 'CS001', 50000),
  ('Main Bus Terminal', ST_SetSRID(ST_Point(0.1, 0.1), 4326), 'bus', 'BUS001', 30000),
  ('Metro Hub A', ST_SetSRID(ST_Point(-0.1, 0.05), 4326), 'metro', 'MET001', 75000),
  ('University Stop', ST_SetSRID(ST_Point(0.05, -0.1), 4326), 'bus', 'UNI001', 20000),
  ('Airport Express', ST_SetSRID(ST_Point(0.2, 0.2), 4326), 'train', 'AIR001', 40000);

-- Insert sample events for testing
INSERT INTO events (event_name, event_description, location, start_time, end_time, impact_radius_meters, importance_level, event_type)
VALUES
  ('IPL Cricket Match', 'International cricket tournament', ST_SetSRID(ST_Point(0.05, 0.05), 4326), 
   NOW() + INTERVAL '2 hours', NOW() + INTERVAL '6 hours', 1500, 'critical', 'sports'),
  ('Music Concert', 'Live music festival', ST_SetSRID(ST_Point(-0.05, -0.05), 4326),
   NOW() + INTERVAL '4 hours', NOW() + INTERVAL '12 hours', 1000, 'high', 'concert'),
  ('Road Construction', 'Main road repairs', ST_SetSRID(ST_Point(0.1, 0.05), 4326),
   NOW() - INTERVAL '1 day', NOW() + INTERVAL '7 days', 800, 'medium', 'construction');

COMMIT;
