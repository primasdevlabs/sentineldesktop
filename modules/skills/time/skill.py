"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/skills/time/skill.py
Description: Core temporal awareness skill. Provides real-time date and time 
             information with personalized delivery.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

from sentinel.modules.skills import BaseSkill
from datetime import datetime
from typing import Dict, Any, Optional

class TimeSkill(BaseSkill):
    """
    Standard skill for temporal queries.
    
    Handles intents related to current clock time and calendar date. 
    Uses MemoryManager injection for personalized greetings.
    """
    
    def __init__(self) -> None:
        """Initializes the TimeSkill registry."""
        super().__init__("TimeSkill")
        self.memory: Optional[Any] = None # Injected by SentinelCore during registration

    def match_intent(self, intent_name: str) -> bool:
        """
        Determines if this skill can handle the given NLU intent.
        
        Args:
            intent_name: The name of the detected intent.
        """
        return intent_name in ["time.query", "date.query"]

    def execute(self, intent_data: Dict[str, Any]) -> None:
        """
        Executes the time/date logic and broadcasts the vocal response.
        
        Args:
            intent_data: Structured data from the NLU engine containing 
                         intent names and slots.
        """
        intent_name = intent_data.get("intent", {}).get("name")
        now = datetime.now()
        
        # --- Personalization ---
        user_name = self.memory.get("user_name", "") if self.memory else ""
        greeting = f"{user_name}, " if user_name else ""
        
        if intent_name == "time.query":
            # Format: e.g., "02:30 PM"
            time_str = now.strftime("%I:%M %p")
            self.speak(f"{greeting}it's {time_str}")
            
        elif intent_name == "date.query":
            # Format: e.g., "Monday, April 24, 2026"
            date_str = now.strftime("%A, %B %d, %Y")
            self.speak(f"{greeting}today is {date_str}")
