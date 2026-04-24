"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/events.py
Description: Central Event Bus for the Sentinel system. Utilizes a Pub/Sub
             mechanism to enable decoupled communication between hardware 
             modules, core logic, and UI components.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

from pubsub import pub
from typing import Callable, Any

class Events:
    """
    Static Event Registry and Dispatcher.
    
    This class defines the vocabulary of the system. All internal communication
    should flow through these topics to ensure that modules (like TTS or UI) 
    do not need direct references to each other.
    """
    
    # --- Interaction Events ---
    WAKE_WORD_DETECTED = "wake_word.detected"    # Triggered by Porcupine/Voice
    CLAP_DETECTED = "clap.detected"             # Single clap audio trigger
    DOUBLE_CLAP_DETECTED = "clap.double_detected" # High-priority interaction trigger
    
    # --- Speech & Language Events ---
    USER_SPOKEN_TEXT = "user.spoken"            # Raw STT output
    INTENT_DETECTED = "intent.detected"         # NLU/LLM parsed intent
    ASSISTANT_RESPONSE = "assistant.response"   # Text ready for TTS
    
    # --- System State Events ---
    STATUS_CHANGED = "status.changed"           # For UI state synchronization
    SKILL_EXECUTED = "skill.executed"           # Logging/Debugging trace
    ERROR_OCCURRED = "error.occurred"           # Global error notification
    
    @staticmethod
    def subscribe(topic: str, listener: Callable[..., Any]) -> None:
        """
        Registers a callback function to a specific event topic.
        
        Args:
            topic: The string identifier for the event.
            listener: The function/method to invoke when the event occurs.
        """
        pub.subscribe(listener, topic)

    @staticmethod
    def emit(topic: str, **kwargs: Any) -> None:
        """
        Broadcasts an event to all registered listeners.
        
        Args:
            topic: The string identifier for the event.
            **kwargs: Dynamic data payload associated with the event.
        """
        pub.sendMessage(topic, **kwargs)
