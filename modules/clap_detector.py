"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/clap_detector.py
Description: Hardware interaction module for sound-based triggers. 
             Implements real-time analysis of audio peaks to detect single 
             and double claps.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import pyaudio
import numpy as np
import threading
import time
from typing import Optional
from sentinel.core.events import Events

class ClapDetectorModule:
    """
    A non-voice trigger mechanism for the assistant.
    
    Monitors the ambient audio environment for sharp acoustic peaks that 
    match the profile of a hand clap. Supports 'Double-Clap' detection to 
    prevent accidental triggers.
    """
    
    def __init__(self, 
                 threshold: float = 0.7, 
                 min_interval: float = 0.2, 
                 double_window: float = 0.5, 
                 cooldown: float = 2.0) -> None:
        """
        Initializes the acoustic detection parameters.
        
        Args:
            threshold: Normalized peak amplitude required to trigger (0.0 - 1.0).
            min_interval: Minimum time between claps to count as distinct.
            double_window: Maximum time between claps to count as a 'double'.
            cooldown: Time to wait after a trigger before listening again.
        """
        self.threshold = threshold
        self.min_interval = min_interval
        self.double_window = double_window
        self.cooldown = cooldown
        
        # Audio configuration
        self.chunk_size = 1024
        self.sample_rate = 44100
        self.pa: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        
        # State tracking for clap timing
        self.last_clap_time: float = 0.0
        self.last_trigger_time: float = 0.0

    def start(self) -> None:
        """
        Initializes the PyAudio stream and launches the detection thread.
        """
        try:
            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        except Exception as e:
            Events.emit(Events.ERROR_OCCURRED, message=f"Clap Detector Init Failed: {e}")

    def _loop(self) -> None:
        """
        Main processing loop: Performs peak-amplitude analysis on audio chunks.
        """
        while self._running:
            try:
                if not self.stream: break
                
                # Read raw PCM data from microphone
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate the normalized peak (0.0 to 1.0)
                # int16 max is 32768
                peak = np.abs(audio_data).max() / 32768.0
                
                if peak > self.threshold:
                    current_time = time.time()
                    
                    # Ignore claps if we are in a post-trigger cooldown period
                    if current_time - self.last_trigger_time < self.cooldown:
                        continue
                        
                    interval = current_time - self.last_clap_time
                    
                    # Logic to differentiate between Single and Double claps
                    if interval > self.min_interval:
                        if interval < self.double_window:
                            # DOUBLE CLAP: Trigger High-Priority system activation
                            Events.emit(Events.DOUBLE_CLAP_DETECTED)
                            self.last_trigger_time = current_time
                            self.last_clap_time = 0 # Reset to prevent triple-claps
                        else:
                            # SINGLE CLAP: Potential trigger, waiting for second clap
                            Events.emit(Events.CLAP_DETECTED)
                            self.last_clap_time = current_time
                            
            except Exception as e:
                # Log error and wait before potentially restarting
                time.sleep(1) 
                break

    def stop(self) -> None:
        """Gracefully terminates the audio stream and resources."""
        self._running = False
        if self.stream:
            self.stream.close()
        if self.pa:
            self.pa.terminate()
