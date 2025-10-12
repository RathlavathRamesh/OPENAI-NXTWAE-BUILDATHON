
import configparser
import json
import os
from dataclasses import dataclass


class ConfigLoader:
    def __init__(self):
        self.settings = {}
        self.config = configparser.ConfigParser()
        file_path = os.path.join(
            os.path.dirname(__file__),
            "local_config.ini",
        )
        self.config.read(file_path)
        for section in self.config.sections():
            for key, value in self.config.items(section):
                self.settings[key.upper()] = value
    #Function to get the config value by key
    def get(self, key, default=None):
        return self.settings.get(key, default)
# Singleton instance for shared access
config_loader = ConfigLoader()

@dataclass
class Config:
    GOOGLE_API_KEY = config_loader.get("GOOGLE_API_KEY")
    OPENAI_KEY = config_loader.get("OPENAI_KEY")
    DB_CONNECTION_STRING = config_loader.get("DB_CONNECTION_STRING")
    DB_SCHEMA = config_loader.get("DB_SCHEMA")