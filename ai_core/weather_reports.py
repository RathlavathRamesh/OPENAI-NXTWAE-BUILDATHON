import requests
from typing import Dict, Any
import os


API_KEY = os.getenv('WEATHER_API_KEY') # Replace with your OpenWeatherMap API key

def get_weather_by_coords(lat : float, lon : float) -> Dict[str, Any]:
    """
    Fetches the current weather report for given latitude and longitude using OpenWeatherMap API.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Weather data or mock data if API key not available
    """
    if not API_KEY:
        # Return mock weather data if no API key
        return {
            'location': (lat, lon),
            'description': 'Clear sky',
            'temperature_C': 25.0,
            'humidity_percent': 60,
            'pressure_hPa': 1013.25,
            'wind_speed_mps': 5.0,
            'visibility_m': 10000,
            'cloudiness_percent': 10,
            'note': 'Mock weather data - API key not configured'
        }
    
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            report = {
                'location': (lat, lon),
                'description': data['weather'][0]['description'],
                'temperature_C': data['main']['temp'],
                'humidity_percent': data['main']['humidity'],
                'pressure_hPa': data['main']['pressure'],
                'wind_speed_mps': data['wind']['speed'],
                'visibility_m': data.get('visibility', 'N/A'),
                'cloudiness_percent': data['clouds']['all'],
            }
            return report
        else:
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        # Return mock data if API call fails
        return {
            'location': (lat, lon),
            'description': 'Unknown',
            'temperature_C': 22.0,
            'humidity_percent': 50,
            'pressure_hPa': 1013.25,
            'wind_speed_mps': 3.0,
            'visibility_m': 8000,
            'cloudiness_percent': 20,
            'note': f'Weather API error: {str(e)}'
        }