import re
from datetime import datetime, timedelta
from sentinel.modules.skills import BaseSkill

class SchedulerSkill(BaseSkill):
    def __init__(self, scheduler_ref):
        super().__init__("SchedulerSkill")
        self.scheduler = scheduler_ref

    def match_intent(self, intent_name):
        return intent_name in ["system.set_reminder", "system.set_alarm"]

    def execute(self, intent_data):
        text = intent_data.get("text", "").lower()
        slots = intent_data.get("slots", {})
        
        message = slots.get("message", "Time is up")
        
        # Simple Natural Language Parsing
        # "in 10 minutes"
        minutes_match = re.search(r"in (\d+) minute", text)
        hours_match = re.search(r"in (\d+) hour", text)
        
        trigger_time = datetime.now()
        
        if minutes_match:
            trigger_time += timedelta(minutes=int(minutes_match.group(1)))
        elif hours_match:
            trigger_time += timedelta(hours=int(hours_match.group(1)))
        else:
            # Fallback for Rhasspy parsed time if available
            time_slot = slots.get("time")
            if time_slot:
                # Expecting HH:MM format from STT
                try:
                    target_time = datetime.strptime(time_slot, "%H:%M").time()
                    trigger_time = datetime.combine(datetime.now().date(), target_time)
                    if trigger_time < datetime.now():
                        trigger_time += timedelta(days=1)
                except:
                    self.speak("I couldn't understand the time you specified.")
                    return
            else:
                self.speak("When should I set that for?")
                return

        task = self.scheduler.add_task("reminder", trigger_time, message)
        self.speak(f"Okay, I've set a reminder for {trigger_time.strftime('%I:%M %p')}.")

