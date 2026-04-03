import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { corsHeaders } from "../_shared/cors.ts"

interface WeatherData {
  condition: string
  intensity: number
  temperature: number
  humidity: number
  wind_speed: number
  description: string
}

// OpenWeatherMap API base URL
const OPENWEATHER_API = "https://api.openweathermap.org/data/2.5"

serve(async (req) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders })
  }

  try {
    const { latitude, longitude, apiKey } = await req.json()

    if (!latitude || !longitude || !apiKey) {
      return new Response(
        JSON.stringify({
          error: "Missing required parameters: latitude, longitude, apiKey",
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    // Fetch weather data from OpenWeatherMap
    const weatherUrl = `${OPENWEATHER_API}/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`
    const weatherResponse = await fetch(weatherUrl)

    if (!weatherResponse.ok) {
      return new Response(
        JSON.stringify({
          error: `Weather API error: ${weatherResponse.status}`,
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    const weatherData = await weatherResponse.json()
    const parsedWeather = parseWeatherResponse(weatherData)

    return new Response(JSON.stringify(parsedWeather), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: `Failed to fetch weather: ${error.message}`,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    )
  }
})

function parseWeatherResponse(data: any): WeatherData {
  const weather = data.weather[0]
  const main = data.main
  const wind = data.wind

  const condition = weather.main as string
  const description = weather.description as string
  const temperature = main.temp as number
  const humidity = main.humidity as number
  const windSpeed = wind?.speed ?? 0

  // Calculate intensity (0.0 to 1.0)
  const intensity = calculateWeatherIntensity(condition, main)

  return {
    condition: condition.toLowerCase(),
    intensity,
    temperature,
    humidity,
    wind_speed: windSpeed,
    description,
  }
}

function calculateWeatherIntensity(
  condition: string,
  main: any
): number {
  const clouds = main.clouds ?? 0

  switch (condition.toLowerCase()) {
    case "thunderstorm":
      return 1.0
    case "rain":
      const humidity = main.humidity as number
      return Math.min(humidity / 100, 1.0)
    case "drizzle":
      return 0.4
    case "snow":
      return 0.9
    case "hail":
      return 0.95
    case "fog":
    case "mist":
    case "smoke":
    case "haze":
      return 0.3
    case "clouds":
      return (clouds / 100) * 0.2
    case "clear":
    case "sunny":
      return 0.0
    default:
      return 0.1
  }
}
