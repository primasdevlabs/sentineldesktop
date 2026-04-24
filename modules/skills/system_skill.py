from . import BaseSkill

class SystemSkill(BaseSkill):
    def __init__(self):
        super().__init__("SystemSkill")

    def match_intent(self, intent_name):
        return intent_name in ["GetTime", "ShutdownSystem"]

    def execute(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        if intent_name == "GetTime":
            from datetime import datetime
            now = datetime.now().strftime("%H:%M")
            self.speak(f"The time is {now}")
        elif intent_name == "ShutdownSystem":
            self.speak("Shutting down the system. Goodbye.")
