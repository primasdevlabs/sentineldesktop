import os
import subprocess
import platform
from sentinel.modules.skills import BaseSkill

class SystemAutomationSkill(BaseSkill):
    def __init__(self):
        super().__init__("SystemAutomation")

    def match_intent(self, intent_name):
        return intent_name in ["system.open_app", "system.control_volume", "system.shutdown"]

    def execute(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        params = intent_data.get("slots", {})
        
        if intent_name == "system.open_app":
            app_name = params.get("app_name", "browser")
            self.open_app(app_name)
        elif intent_name == "system.control_volume":
            level = params.get("level", 50)
            self.set_volume(level)
        elif intent_name == "system.shutdown":
            self.speak("Initiating system shutdown sequence.")
            # self.shutdown()

    def open_app(self, app_name):
        self.speak(f"Opening {app_name}.")
        try:
            if platform.system() == "Windows":
                os.startfile(app_name) # This usually requires full path or registered app
            elif platform.system() == "Darwin": # macOS
                subprocess.Popen(["open", "-a", app_name])
            else: # Linux
                subprocess.Popen([app_name])
        except Exception as e:
            self.speak(f"I couldn't open {app_name}. Error: {e}")

    def set_volume(self, level):
        self.speak(f"Setting volume to {level} percent.")
        # Implementation varies wildly by OS (nircmd on Windows, amixer on Linux)
        pass

    def shutdown(self):
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("sudo shutdown now")
