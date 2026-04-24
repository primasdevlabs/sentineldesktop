"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/proactive_engine.py
Description: The behavioral core for autonomous AI behavior. Manages 
             interruption queues, priority-based alerts, and proactive 
             verbal updates.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import threading
import time
import queue
from typing import Any, Tuple
from .events import Events

class ProactiveEngine:
    """
    The decision-making layer for system interruptions.
    
    This engine listens for background events (like calendar notifications
    or system alerts) and determines when and how Sentinel should
    proactively speak to the user.
    """
    
    def __init__(self, assistant_ref: Any) -> None:
        """
        Initializes the engine with a reference to the main assistant.
        
        Args:
            assistant_ref: Reference to the SentinelCore instance.
        """
        self.assistant = assistant_ref
        self.logger = assistant_ref.logger
        
        # Thread-safe priority queue for handling multiple simultaneous alerts.
        # Priority order: 1 (Critical) to 3 (Low).
        self.alert_queue: queue.PriorityQueue = queue.PriorityQueue()
        
        self._running: bool = False
        self.cooldown: int = 30 # Minimum seconds between proactive updates
        self.last_alert_time: float = 0.0

    def start(self) -> None:
        """Starts the background alert processing loop."""
        self._running = True
        threading.Thread(target=self._process_alerts, daemon=True).start()

    def post_alert(self, message: str, priority: int = 2) -> None:
        """
        Adds a new message to the proactive queue.
        
        Args:
            message: The text string Sentinel should speak.
            priority: Interruption priority (1=High, 2=Medium, 3=Low).
        """
        # Queue item: (Priority, Timestamp, Message)
        # Priority is the first element for PriorityQueue sorting.
        self.alert_queue.put((priority, time.time(), message))
        Events.emit("event.proactive_alert", message=message, priority=priority)

    def _process_alerts(self) -> None:
        """
        Main worker loop: Evaluates the queue and manages cooldowns.
        """
        while self._running:
            if not self.alert_queue.empty():
                current_time = time.time()
                
                # Prevent Sentinel from being too 'chatty' by enforcing a cooldown
                if current_time - self.last_alert_time > self.cooldown:
                    # Retrieve highest priority item (lowest integer)
                    priority, timestamp, message = self.alert_queue.get()
                    self._trigger_interruption(message)
                    self.last_alert_time = time.time()
                    
            time.sleep(1)

    def _trigger_interruption(self, message: str) -> None:
        """
        Executes a high-priority system interruption.
        
        Orchestrates state changes, UI updates, and TTS playback.
        
        Args:
            message: The message to speak.
        """
        self.logger.info(f"Proactive Interruption Triggered: {message}")
        
        # Kill any low-priority speech currently occurring
        # (This is handled globally via the status_changed event, but 
        # explicit stop ensures immediate silence)
        Events.emit(Events.STATUS_CHANGED, status="alert")
        
        # Use the Core Assistant's speak method (handles personalization/TTS)
        self.assistant.speak(message)

    def track_interaction(self, intent_name: str) -> None:
        """
        Future Hook: Intended for habit-tracking logic to learn 
        when the user is most/least receptive to interruptions.
        """
        pass

    def stop(self) -> None:
        """Gracefully terminates the engine thread."""
        self._running = False
