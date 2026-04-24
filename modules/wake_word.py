"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/wake_word.py
Description: Hardware interaction module for voice-activation. Interfaces 
             with Picovoice Porcupine to provide efficient, real-time 
             wake-word detection ("Sentinel").
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import pvporcupine
import threading
import logging
from typing import List, Optional
from .audio.input import AudioInput
from sentinel.core.events import Events

class WakeWordModule:
    """
    Manages the 'Always-On' listening state for system activation.
    
    This module captures audio frames via the local microphone and processes
    them through the Porcupine engine. When the keyword 'Sentinel' is detected,
    it broadcasts a system-wide WAKE_WORD_DETECTED event.
    """
    
    def __init__(self, 
                 access_key: str, 
                 keywords: List[str] = ['sentinel'], 
                 sensitivities: List[float] = [0.5]) -> None:
        """
        Initializes the detection engine parameters.
        
        Args:
            access_key: Valid Picovoice Access Key from the Picovoice Console.
            keywords: List of target wake words.
            sensitivities: Accuracy sensitivity for each keyword (0.0 to 1.0).
        """
        self.access_key = access_key
        self.keywords = keywords
        self.sensitivities = sensitivities
        self.porcupine: Optional[pvporcupine.Porcupine] = None
        self.audio_input: Optional[AudioInput] = None
        self._running: bool = False
        self.logger = logging.getLogger("WakeWord")

    def start(self) -> None:
        """
        Initializes the hardware audio stream and starts the detection thread.
        """
        try:
            # Initialize the Porcupine SDK engine
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.keywords,
                sensitivities=self.sensitivities
            )
            
            # Configure audio input to match Porcupine's required sample rate/frame length
            # Porcupine typically requires 16kHz audio.
            self.audio_input = AudioInput(
                sample_rate=self.porcupine.sample_rate,
                frame_length=self.porcupine.frame_length
            )
            
            if self.audio_input.start():
                self._running = True
                # Run the detection loop in a background thread to prevent UI/Core blocking
                threading.Thread(target=self._run, daemon=True).start()
                self.logger.info("Wake Word detection active and listening.")
        except Exception as e:
            self.logger.error(f"Failed to initialize WakeWord engine: {e}")

    def _run(self) -> None:
        """
        Main processing loop. Continuously reads PCM data and checks for triggers.
        """
        while self._running:
            if not self.audio_input or not self.porcupine:
                break
                
            pcm = self.audio_input.read()
            if pcm is None:
                continue
                
            # Process the audio frame
            result = self.porcupine.process(pcm)
            
            # If result >= 0, it represents the index of the detected keyword
            if result >= 0:
                self.logger.info(f"Wake word '{self.keywords[result]}' detected.")
                # Notify the entire system to switch to 'Listening' state
                Events.emit(Events.WAKE_WORD_DETECTED)

    def stop(self) -> None:
        """
        Gracefully releases hardware resources and terminates threads.
        """
        self._running = False
        if self.audio_input:
            self.audio_input.stop()
        if self.porcupine:
            self.porcupine.delete()
        self.logger.info("Wake Word detection stopped.")
