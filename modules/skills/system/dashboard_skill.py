from sentinel.modules.skills import BaseSkill
from sentinel.core.events import Events

class DashboardSkill(BaseSkill):
    def __init__(self, controller):
        super().__init__("DashboardSkill")
        self.controller = controller

    def match_intent(self, intent_name):
        return intent_name in ["system.show_dashboard", "system.hide_dashboard", "system.refresh_weather"]

    def execute(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        if intent_name == "system.show_dashboard":
            self.speak("Opening system dashboard.")
            Events.emit("ui.toggle_dashboard", visible=True)
        elif intent_name == "system.hide_dashboard":
            Events.emit("ui.toggle_dashboard", visible=False)
        elif intent_name == "system.refresh_weather":
            self.speak("Refreshing environment data.")
            self.controller.refresh_weather()
