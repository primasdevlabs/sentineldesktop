"""
Primas Dev Labs - Dashboard
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from sentinel.core.events import Events

class DashboardUI(QWidget):
    """Main data visualization interface."""
    def __init__(self, brain):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.temp_lbl = QLabel("--°C")
        self.layout.addWidget(self.temp_lbl)
        Events.subscribe("dashboard.weather_updated", self.update_weather)

    def update_weather(self, data=None):
        """Updates weather labels."""
        if data:
            temp = data["main"]["temp"]
            self.temp_lbl.setText(f"{temp}°C")
