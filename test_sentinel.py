import sys
import os
import time
import json
from sentinel.core.assistant import Assistant
from sentinel.core.events import Events
from sentinel.modules.skills.time.skill import TimeSkill
from sentinel.modules.skills.weather.skill import WeatherSkill

class MockTTS:
    def speak(self, text):
        print(f"\n[SENTINEL TTS]: {text}")
    def stop(self):
        print("[SENTINEL TTS]: Speech Interrupted")

class MockSTT:
    def listen(self):
        print("[SENTINEL STT]: Listening for command...")

def test_sentinel():
    print("--- Sentinel System Logic Test ---")
    os.makedirs("sentinel/data", exist_ok=True)
    assistant = Assistant("sentinel/config/config.yaml")
    mock_tts = MockTTS()
    assistant.register_module("tts", mock_tts)
    assistant.register_module("stt", MockSTT())
    assistant.register_skill(TimeSkill())
    assistant.register_skill(WeatherSkill(api_key=None, city="London"))
    
    print("\n> Testing Name Setup...")
    assistant.handle_intent({"intent": {"name": ""}, "text": "Sentinel, call me Alex"})
    
    print("\n> Testing Time Skill (Routing)...")
    assistant.handle_intent({"intent": {"name": "time.query"}, "text": "What time is it?"})

    print("\n> Testing Conversational Brain (LLM)...")
    assistant.handle_intent({"intent": {"name": ""}, "text": "Who was Nikola Tesla?"})
    time.sleep(5)

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_sentinel()
