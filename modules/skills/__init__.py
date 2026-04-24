from sentinel.core.events import Events

class BaseSkill:
    def __init__(self, name):
        self.name = name
        Events.subscribe(Events.INTENT_DETECTED, self.handle_intent)

    def handle_intent(self, intent_data):
        intent_name = intent_data.get("intent", {}).get("name")
        if self.match_intent(intent_name):
            self.execute(intent_data)

    def match_intent(self, intent_name):
        return False

    def execute(self, intent_data):
        pass

    def speak(self, text):
        Events.emit(Events.ASSISTANT_RESPONSE, text=text)
