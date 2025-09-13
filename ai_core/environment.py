from configparser import ConfigParser

config = ConfigParser()
config.read('local_config.ini')

class Config:
    WEATHER_API_KEY = config.get('KEYS','WEATHER_API_KEY')  # Replace with your OpenWeatherMap API key