from sentinel.modules.skills import BaseSkill
from sentinel.core.events import Events

class ControlSkill(BaseSkill):
    def __init__(self):
        super().__init__("ControlSkill")

    def match_intent(self, intent_name):
        return intent_name in ["system.show_controls", "system.hide_controls"]

    def execute(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        if intent_name == "system.show_controls":
            self.speak("Opening system control center.")
            Events.emit("ui.toggle_controls", visible=True)
        elif intent_name == "system.hide_controls":
            Events.emit("ui.toggle_controls", visible=False)
