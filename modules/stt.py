"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/stt.py
Description: Speech-to-Text (STT) and Natural Language Understanding (NLU) 
             bridge. Interfaces with Rhasspy to convert spoken audio into 
             structured text and intents.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import requests
from typing import Dict, Any
from sentinel.core.events import Events

class STTModule:
    """
    Handles the conversion of user speech into actionable data.
    
    This module acts as a client for the local Rhasspy server, which performs
    the heavy lifting of acoustic modeling and intent parsing.
    """
    
    def __init__(self, rhasspy_url: str) -> None:
        """
        Initializes the STT client with the Rhasspy server endpoint.
        
        Args:
            rhasspy_url: Base URL of the Rhasspy instance (e.g., http://localhost:12101).
        """
        self.url = rhasspy_url

    def listen(self) -> None:
        """
        Triggers Rhasspy's command listener.
        
        This method is typically called after a Wake Word or Clap detection.
        It waits for Rhasspy to process audio and then emits the resulting
        transcription and intent data via the system event bus.
        """
        try:
            # Rhasspy's /api/listen-for-command records audio and performs STT/NLU
            response = requests.post(f"{self.url}/api/listen-for-command")
            
            if response.status_code == 200:
                data: Dict[str, Any] = response.json()
                text: str = data.get("text", "")
                
                # Broadcast raw text for logging and general processing
                Events.emit(Events.USER_SPOKEN_TEXT, text=text)
                
                # If an intent was successfully identified, broadcast for Skill mapping
                if "intent" in data and data.get("intent", {}).get("name"):
                    Events.emit(Events.INTENT_DETECTED, intent_data=data)
            else:
                Events.emit(Events.ERROR_OCCURRED, message=f"Rhasspy STT Error: HTTP {response.status_code}")
                
        except Exception as e:
            Events.emit(Events.ERROR_OCCURRED, message=f"STT Network Exception: {e}")

    def text_to_intent(self, text: str) -> None:
        """
        Directly parses a text string into an intent.
        
        Useful for secondary processing or testing where audio input is bypassed.
        
        Args:
            text: The text string to analyze.
        """
        try:
            response = requests.post(f"{self.url}/api/text-to-intent", data=text)
            
            if response.status_code == 200:
                intent_data: Dict[str, Any] = response.json()
                Events.emit(Events.INTENT_DETECTED, intent_data=intent_data)
            else:
                Events.emit(Events.ERROR_OCCURRED, message=f"Rhasspy NLU Error: HTTP {response.status_code}")
                
        except Exception as e:
            Events.emit(Events.ERROR_OCCURRED, message=f"NLU Network Exception: {e}")
