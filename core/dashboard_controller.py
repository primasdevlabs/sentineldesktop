import psutil
import threading
import time
import requests
from sentinel.core.events import Events

class DashboardController:
    def __init__(self, brain):
        self.brain = brain
        self._running = False
        self.stats = {"cpu": 0, "ram": 0, "disk": 0}
        self.weather_data = None
        self.last_weather_update = 0

    def start(self):
        self._running = True
        threading.Thread(target=self._stats_loop, daemon=True).start()
        threading.Thread(target=self._weather_loop, daemon=True).start()

    def _stats_loop(self):
        while self._running:
            self.stats["cpu"] = psutil.cpu_percent(interval=1)
            self.stats["ram"] = psutil.virtual_memory().percent
            self.stats["disk"] = psutil.disk_usage('/').percent
            Events.emit("dashboard.stats_updated", stats=self.stats)
            
            if self.stats["cpu"] > 90:
                Events.emit(Events.STATUS_CHANGED, status="alert")
            time.sleep(2)

    def _weather_loop(self):
        while self._running:
            self.refresh_weather()
            time.sleep(600) # 10 minutes

    def refresh_weather(self):
        cfg = self.brain.config.get('weather', {})
        api_key = cfg.get('api_key')
        city = cfg.get('city', 'London')
        
        if not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            return

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                self.weather_data = resp.json()
                Events.emit("dashboard.weather_updated", data=self.weather_data)
        except Exception as e:
            print(f"Weather Update Error: {e}")

    def stop(self):
        self._running = False
