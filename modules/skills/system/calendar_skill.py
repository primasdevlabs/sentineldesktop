from sentinel.modules.skills import BaseSkill
from sentinel.core.events import Events

class CalendarSkill(BaseSkill):
    def __init__(self, brain):
        super().__init__("CalendarSkill")
        self.brain = brain

    def match_intent(self, intent_name):
        return intent_name in ["calendar.query", "calendar.show_schedule"]

    def execute(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        
        if intent_name == "calendar.query":
            events = self.brain.sync_calendar()
            if not events:
                self.speak("Your calendar looks clear for today.")
            else:
                summary = f"You have {len(events)} events today. Your next one is {events[0]['summary']}."
                self.speak(summary)
        
        elif intent_name == "calendar.show_schedule":
            self.speak("Displaying your daily schedule now.")
            Events.emit("ui.toggle_schedule", visible=True)
