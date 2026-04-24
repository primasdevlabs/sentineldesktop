"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/skills/weather/skill.py
Description: Atmospheric awareness skill.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import requests
import time
from typing import Dict, Any, Optional
from sentinel.modules.skills import BaseSkill

class WeatherSkill(BaseSkill):
    def __init__(self, api_key: str, city: str) -> None:
        super().__init__("WeatherSkill")
        self.api_key = api_key
        self.city = city
        self.cache: Optional[Dict[str, Any]] = None
        self.last_fetch: float = 0.0
        self.memory: Optional[Any] = None

    def match_intent(self, intent_name: str) -> bool:
        return intent_name in ["weather.current", "weather.forecast"]

    def execute(self, intent_data: Dict[str, Any]) -> None:
        if not self.api_key or self.api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            self.speak("Weather API key not configured.")
            return

        current_time = time.time()
        if self.cache and (current_time - self.last_fetch < 600):
            self.process_weather(self.cache)
            return

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.cache = response.json()
                self.last_fetch = current_time
                self.process_weather(self.cache)
            else:
                self.speak("Unable to reach weather service.")
        except Exception:
            self.speak("Connection error.")

    def process_weather(self, data: Dict[str, Any]) -> None:
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        user_name = self.memory.get("user_name", "") if self.memory else ""
        prefix = f"{user_name}, " if user_name else ""
        self.speak(f"{prefix}the weather in {self.city} is {desc} at {temp} degrees.")
