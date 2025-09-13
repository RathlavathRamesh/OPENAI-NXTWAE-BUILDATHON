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
        api_key (str): OpenWeatherMap API key

    Returns:
        dict: Weather data or error message
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(url)
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