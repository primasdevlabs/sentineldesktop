"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/scheduler.py
Description: The primary task scheduling and reminder engine. Manages 
             time-based triggers and persistent task tracking.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import time
import threading
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sentinel.core.events import Events

class SentinelScheduler:
    """
    A persistent time-based task executor.
    
    Responsible for checking due tasks at regular intervals and 
    broadcasting reminders or automated actions when the trigger 
    time is reached.
    """
    
    def __init__(self, memory_manager: Any, check_interval: int = 30) -> None:
        """
        Initializes the scheduler and loads existing tasks from disk.
        
        Args:
            memory_manager: Reference to the MemoryManager for persistence.
            check_interval: Frequency (in seconds) to check for due tasks.
        """
        self.memory = memory_manager
        self.check_interval = check_interval
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        
        # Hydrate task list from MemoryManager storage
        self.tasks: List[Dict[str, Any]] = self.memory.get("scheduled_tasks", [])

    def start(self) -> None:
        """Starts the background monitoring loop in a daemon thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def add_task(self, 
                 task_type: str, 
                 trigger_time: datetime, 
                 message: str, 
                 repeat: bool = False) -> Dict[str, Any]:
        """
        Registers a new task in the system.
        
        Args:
            task_type: Identifier for the task (e.g., 'reminder', 'alarm').
            trigger_time: Datetime object representing the execution time.
            message: The message to display/speak when triggered.
            repeat: Whether to reschedule the task automatically (WIP).
        
        Returns:
            Dict: The created task object.
        """
        task = {
            "id": str(uuid.uuid4())[:8],
            "type": task_type,
            "time": trigger_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "repeat": repeat
        }
        
        self.tasks.append(task)
        
        # Atomically update persistent storage
        self.memory.set("scheduled_tasks", self.tasks)
        Events.emit("task.created", task=task)
        
        return task

    def _loop(self) -> None:
        """
        Private loop: Periodically scans the task list for due items.
        """
        while self._running:
            now = datetime.now()
            due_tasks: List[Dict[str, Any]] = []
            remaining_tasks: List[Dict[str, Any]] = []

            # Partition tasks into 'Due' and 'Upcoming'
            for task in self.tasks:
                try:
                    task_time = datetime.strptime(task["time"], "%Y-%m-%d %H:%M:%S")
                    if now >= task_time:
                        due_tasks.append(task)
                    else:
                        remaining_tasks.append(task)
                except ValueError:
                    # Handle corrupt time strings
                    continue

            # Process due items
            if due_tasks:
                for task in due_tasks:
                    self._trigger_task(task)
                
                # Update memory with remaining (upcoming) tasks
                self.tasks = remaining_tasks
                self.memory.set("scheduled_tasks", self.tasks)

            time.sleep(self.check_interval)

    def _trigger_task(self, task: Dict[str, Any]) -> None:
        """
        Executes a due task by broadcasting notification and vocal events.
        
        Args:
            task: The task object being triggered.
        """
        # Notify the UI to show a visual reminder
        Events.emit("reminder.triggered", message=task["message"])
        
        # Request a verbal announcement from the core assistant
        # Prepending 'Reminder:' ensures the LLM/Persona handles it as an alert.
        Events.emit(Events.ASSISTANT_RESPONSE, text=f"Reminder: {task['message']}")

    def stop(self) -> None:
        """Gracefully stops the monitoring loop."""
        self._running = False
