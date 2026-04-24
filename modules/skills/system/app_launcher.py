"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/skills/system/app_launcher.py
Description: OS automation skill for launching local applications.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import subprocess
import os
from typing import Dict, Any
from sentinel.modules.skills import BaseSkill
from sentinel.core.events import Events

class AppLauncherSkill(BaseSkill):
    def __init__(self) -> None:
        super().__init__("AppLauncher")
        self.apps = {
            "chrome": "chrome.exe",
            "spotify": "spotify.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe"
        }

    def match_intent(self, intent_name: str) -> bool:
        return intent_name in ["system.launch_app"]

    def execute(self, intent_data: Dict[str, Any]) -> None:
        slots = intent_data.get("slots", {})
        app_name = slots.get("app_name", "").lower()
        background = slots.get("background", False)
        
        if not app_name:
            self.speak("Which application should I launch?")
            return

        app_path = self.apps.get(app_name, app_name)
        self._launch(app_name, app_path, background)

    def _launch(self, name: str, path: str, background: bool) -> None:
        try:
            Events.emit("system.app_launch_started", app_name=name)
            if background:
                subprocess.Popen(path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                self.speak(f"Starting {name} in the background.")
            else:
                subprocess.Popen(path, shell=True)
                self.speak(f"Opening {name}.")
        except Exception as e:
            self.speak(f"Error launching {name}.")
