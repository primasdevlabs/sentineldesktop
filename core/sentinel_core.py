"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/sentinel_core.py
Description: The central hub of the Sentinel system. Manages state, system 
             configuration, resource monitoring, and event-driven communication 
             between hardware modules and software skills.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import yaml
import logging
import threading
import time
import os
from typing import Dict, Any, List, Optional

# Core Architecture Imports
from .events import Events
from .conversation_manager import ConversationManager
from .memory_manager import MemoryManager
from .proactive_engine import ProactiveEngine
from .scheduler import SentinelScheduler
from .resource_manager import ResourceManager
from .module_manager import ModuleManager
from sentinel.core.dashboard_controller import DashboardController
from sentinel.services.google_calendar_service import GoogleCalendarService

class SentinelCore:
    """
    The main orchestrator class for the Sentinel AI.
    
    Responsible for:
    - Loading system-wide configurations.
    - Initializing core managers (Memory, Conversation, Modules).
    - Subscribing to system events (Voice, Claps, User Input).
    - Managing the global state machine (Idle, Listening, Thinking, Speaking).
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initializes the Core Brain and its dependency-injected managers.
        
        Args:
            config_path: Optional override for the config.yaml location.
        """
        # Anchor all paths to the root of the sentinel package
        self.root_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if config_path is None:
            config_path = os.path.join(self.root_dir, 'config', 'config.yaml')

        # Load Global Config
        self.config: Dict[str, Any] = self.load_config(config_path)
        
        # Setup Logging Infrastructure
        self.setup_logging()
        self.state: str = "idle"  # Initial state
        
        # Initialize Sub-Managers
        self.memory = MemoryManager()
        self.module_manager = ModuleManager(self)
        
        # Memory cap enforcement (Prevents resource leaks during long uptime)
        memory_cap = self.config.get('system', {}).get('memory_cap', 256)
        self.resource_manager = ResourceManager(memory_cap_mb=memory_cap)
        
        self.conversation_manager = ConversationManager(self.config, self.memory)
        self.dashboard_controller = DashboardController(self)
        self.proactive_engine = ProactiveEngine(self)
        self.scheduler = SentinelScheduler(self.memory)
        
        # External Services (Calendar, etc.)
        self.calendar = GoogleCalendarService(
            credentials_path=os.path.join(self.root_dir, 'config', 'credentials.json'),
            token_path=os.path.join(self.root_dir, 'config', 'token.json')
        )
        
        # --- System Event Subscriptions ---
        # Sentinel uses a Pub/Sub model for complete decoupling.
        Events.subscribe(Events.WAKE_WORD_DETECTED, self.on_wake)
        Events.subscribe(Events.DOUBLE_CLAP_DETECTED, self.on_wake)
        Events.subscribe(Events.USER_SPOKEN_TEXT, self.on_user_input)
        Events.subscribe(Events.INTENT_DETECTED, self.on_intent)
        Events.subscribe(Events.ERROR_OCCURRED, self.on_error)

    def load_config(self, path: str) -> Dict[str, Any]:
        """Loads and parses the system YAML configuration file."""
        if not os.path.exists(path):
            # Fallback check for relative execution paths
            if path == 'sentinel/config/config.yaml' and os.path.exists('config/config.yaml'):
                path = 'config/config.yaml'
            else:
                raise FileNotFoundError(f"Configuration not found at: {path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def setup_logging(self) -> None:
        """Initializes the rolling file logger for the assistant."""
        log_dir = os.path.join(self.root_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'assistant.log')
        
        level_str = self.config.get('logging', {}).get('level', 'INFO')
        level = getattr(logging, level_str)
        
        logging.basicConfig(
            filename=log_file, 
            level=level, 
            format='%(asctime)s - [%(levelname)s] - %(message)s'
        )
        self.logger = logging.getLogger("SentinelCore")

    def set_state(self, state: str) -> None:
        """Sets the system state and notifies the UI via events."""
        self.state = state
        Events.emit(Events.STATUS_CHANGED, status=state)

    def register_skill(self, skill_instance: Any) -> None:
        """Injects dependencies into a skill and adds it to the registry."""
        skill_instance.memory = self.memory
        if not hasattr(self, "skills"): 
            self.skills: List[Any] = []
        self.skills.append(skill_instance)

    def on_wake(self) -> None:
        """Triggered when 'Sentinel' or a clap is detected. Activates STT."""
        self.set_state("listening")
        self.module_manager.enable("stt")

    def on_user_input(self, text: str) -> None:
        """Called when STT produces a final transcription string."""
        if not text: 
            self.set_state("idle")

    def on_intent(self, intent_data: Dict[str, Any]) -> None:
        """
        The routing engine for speech intents. 
        Checks skill registry first, then falls back to conversational LLM.
        """
        intent_name = intent_data.get('intent', {}).get('name')
        text = intent_data.get("text", "")
        
        self.set_state("thinking")
        
        # Hardcoded interrupt commands
        if text.lower() in ["stop", "cancel"]:
            self.set_state("idle")
            return
            
        handled = False
        # Route to specific skill handlers if an intent was identified
        if intent_name and hasattr(self, "skills"):
            for skill in self.skills:
                if skill.match_intent(intent_name):
                    self.set_state("executing")
                    skill.execute(intent_data)
                    handled = True
                    break
        
        # If no skill handled it, fallback to the AI conversation manager
        if not handled: 
            self.conversation_manager.get_response(text)

    def speak(self, text: str) -> None:
        """Triggers the TTS module and updates state."""
        self.set_state("speaking")
        # Ensure text is personalized (e.g., adding user name) via memory
        p_text = self.memory.personalize_text(text)
        Events.emit(Events.ASSISTANT_RESPONSE, text=p_text)

    def start(self) -> None:
        """Main activation sequence for background services and modules."""
        self.resource_manager.start_monitoring()
        self.proactive_engine.start()
        self.scheduler.start()
        self.dashboard_controller.start()
        
        # Enable modules defined as autostart in config
        for mod_name, enabled in self.config.get('modules', {}).items():
            if enabled: 
                self.module_manager.enable(mod_name)
                
        self.speak("Sentinel initialized.")

    def on_error(self, message: str) -> None:
        """Global error handler for core-level issues."""
        if hasattr(self, 'logger'): 
            self.logger.error(f"Error: {message}")
