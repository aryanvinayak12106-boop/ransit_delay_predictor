import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { corsHeaders } from "../_shared/cors.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

interface EventData {
  id: string
  event_name: string
  importance_level: string
  event_type: string
  distance_meters: number
  impact_radius_meters: number
  is_active: boolean
}

serve(async (req) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders })
  }

  try {
    const { latitude, longitude, radiusMeters = 2000 } = await req.json()

    if (!latitude || !longitude) {
      return new Response(
        JSON.stringify({
          error: "Missing required parameters: latitude, longitude",
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get("SUPABASE_URL")
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Get nearby active events using PostGIS
    const { data: events, error } = await supabase.rpc(
      "get_nearby_active_events",
      {
        p_latitude: latitude,
        p_longitude: longitude,
        p_radius_meters: radiusMeters,
      }
    )

    if (error) {
      throw new Error(`Database error: ${error.message}`)
    }

    // Transform and filter events
    const transformedEvents = (events || [])
      .map((event: any) => ({
        id: event.id,
        event_name: event.event_name,
        importance_level: event.importance_level,
        event_type: event.event_type,
        distance_meters: event.distance_meters,
        impact_radius_meters: event.impact_radius_meters,
        is_active: isEventActive(event.start_time, event.end_time),
      }))
      .sort(
        (a: EventData, b: EventData) =>
          priorityScore(b) - priorityScore(a)
      )

    return new Response(
      JSON.stringify({
        total: transformedEvents.length,
        events: transformedEvents,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: `Failed to fetch events: ${error.message}`,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    )
  }
})

function isEventActive(startTime: string, endTime: string): boolean {
  const now = new Date()
  const start = new Date(startTime)
  const end = new Date(endTime)
  return now >= start && now <= end
}

function priorityScore(event: EventData): number {
  let score = 0

  // Importance level scoring
  switch (event.importance_level) {
    case "critical":
      score += 100
      break
    case "high":
      score += 75
      break
    case "medium":
      score += 50
      break
    case "low":
      score += 25
      break
  }

  // Distance scoring (closer = higher priority)
  if (event.distance_meters < 500) score += 50
  else if (event.distance_meters < 1000) score += 30
  else if (event.distance_meters < 1500) score += 10

  return score
}
