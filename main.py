"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: main.py
Description: The primary entry point for the Sentinel AI Assistant. 
             Orchestrates the lifecycle of the core brain, module registration, 
             skill loading, and UI execution.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import sys
import os
import threading
from typing import Optional

# Ensure the project root is in the path for module resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core Brain & Infrastructure
from sentinel.core.sentinel_core import SentinelCore
from sentinel.modules.wake_word import WakeWordModule
from sentinel.modules.stt import STTModule
from sentinel.modules.tts import ElevenLabsTTS, TTSModule

# Skill Modules
from sentinel.modules.skills.time.skill import TimeSkill
from sentinel.modules.skills.weather.skill import WeatherSkill
from sentinel.modules.skills.system.app_launcher import AppLauncherSkill
from sentinel.modules.skills.system.scheduler_skill import SchedulerSkill
from sentinel.modules.skills.system.calendar_skill import CalendarSkill
from sentinel.modules.skills.system.control_skill import ControlSkill
from sentinel.modules.skills.system.dashboard_skill import DashboardSkill

# UI Components
from sentinel.modules.ui.lock_orb import start_lock_orb
from sentinel.modules.ui.theme import apply_sentinel_theme
from PyQt6.QtWidgets import QApplication

def main() -> None:
    """
    Main application loop. 
    1. Initializes the SentinelCore (The Brain).
    2. Registers critical hardware and AI modules (TTS, Wake Word, STT).
    3. Loads feature-rich skills into the ecosystem.
    4. Launches the PyQt6 liquid-orb UI.
    """
    
    # --- 1. Initialize Core Brain ---
    # The brain handles configuration loading, event bus initialization, 
    # and internal state management.
    brain = SentinelCore()
    
    # --- 2. Module Registration & Dependency Injection ---
    # Modules are registered with the ModuleManager to allow for 
    # dynamic status checking and hot-reloading.
    
    # Configure Text-to-Speech (TTS)
    # Supports Local (Balcon) and Cloud-based (ElevenLabs) engines.
    l_tts = TTSModule(
        balcon_path=brain.config['tts'].get('balcon_path', ''), 
        voice=brain.config['tts'].get('voice', '')
    )
    
    el_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    
    if el_key and brain.config['tts'].get('engine') == "elevenlabs":
        # Register ElevenLabs with a local fallback if internet/API fails
        brain.module_manager.register(
            "tts", 
            ElevenLabsTTS, 
            api_key=el_key, 
            voice_id=brain.config['tts'].get('voice_id'), 
            fallback_engine=l_tts
        )
    else:
        # Default to local TTS if no API key is present
        brain.module_manager.register(
            "tts", 
            TTSModule, 
            balcon_path=brain.config['tts'].get('balcon_path', ''), 
            voice=brain.config['tts'].get('voice', '')
        )
        
    # Register Wake Word (Porcupine) and Speech-To-Text (Rhasspy)
    brain.module_manager.register(
        "wake_word", 
        WakeWordModule, 
        access_key=brain.config['assistant'].get('access_key', '')
    )
    brain.module_manager.register(
        "stt", 
        STTModule, 
        rhasspy_url=brain.config['rhasspy'].get('url', '')
    )
    
    # --- 3. Feature Skill Registration ---
    # Skills extend the assistant's capabilities through a standardized API.
    brain.register_skill(TimeSkill())
    brain.register_skill(WeatherSkill(
        api_key=brain.config['weather'].get('api_key'), 
        city=brain.config['weather'].get('city')
    ))
    brain.register_skill(AppLauncherSkill())
    brain.register_skill(SchedulerSkill(brain.scheduler))
    brain.register_skill(CalendarSkill(brain))
    brain.register_skill(ControlSkill())
    brain.register_skill(DashboardSkill(brain.dashboard_controller))
    
    # --- 4. Background Threading ---
    # Start the event loop and proactive engine in a daemon thread 
    # to keep the main thread free for the UI loop.
    threading.Thread(target=brain.start, daemon=True).start()
    
    # --- 5. UI Initialization ---
    app = QApplication(sys.argv)
    
    # Apply global 'Sentinel-Blue' branding/theme
    apply_sentinel_theme(app)
    
    # Launch the primary Lock Orb (JARVIS-style interaction point)
    # This also initializes the DashboardController and underlying Windows.
    app, win = start_lock_orb(brain)
    
    # Execute the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
