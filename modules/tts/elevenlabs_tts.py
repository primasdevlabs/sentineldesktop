"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/tts/elevenlabs_tts.py
Description: High-fidelity Neural Text-to-Speech (TTS) module. Interfaces
             with the ElevenLabs API to provide human-like voice synthesis 
             with real-time streaming capabilities.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import os
import threading
import subprocess
import time
from typing import Optional, Any
from elevenlabs.client import ElevenLabs
from sentinel.core.events import Events

class ElevenLabsTTS:
    """
    Neural Voice Engine for Sentinel.
    
    This module uses the ElevenLabs multilingual model to generate speech.
    It streams audio chunks directly to 'mpv' for low-latency playback
    and supports immediate interruption when the user starts speaking.
    """
    
    def __init__(self, 
                 api_key: str, 
                 voice_id: str = "Rachel", 
                 stability: float = 0.5, 
                 similarity_boost: float = 0.75, 
                 fallback_engine: Optional[Any] = None) -> None:
        """
        Initializes the ElevenLabs client and voice settings.
        
        Args:
            api_key: ElevenLabs API Key.
            voice_id: The ID or name of the voice to use.
            stability: Voice stability setting (0.0 to 1.0).
            similarity_boost: Voice clarity/similarity setting (0.0 to 1.0).
            fallback_engine: A local TTS engine to use if the cloud API fails.
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.fallback_engine = fallback_engine
        
        self.is_speaking: bool = False
        self.current_process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
        
        # Subscribe to assistant responses and state changes for interruptions
        Events.subscribe(Events.ASSISTANT_RESPONSE, self.speak)
        Events.subscribe(Events.STATUS_CHANGED, self.handle_interrupt)

    def handle_interrupt(self, status: str) -> None:
        """
        Stops current playback if the system switches to 'listening' mode.
        Allows for natural JARVIS-style conversation interruption.
        """
        if status == "listening":
            self.stop()

    def speak(self, text: str) -> None:
        """
        Initiates the speech generation process.
        
        Args:
            text: The text string to convert to speech.
        """
        self.stop()  # Kill any ongoing speech
        self._stop_event.clear()
        
        # Run generation in a background thread to keep the Core/UI responsive
        threading.Thread(target=self._generate_and_play, args=(text,), daemon=True).start()

    def _generate_and_play(self, text: str) -> None:
        """
        Private worker thread: Fetches stream from ElevenLabs and pipes to mpv.
        """
        try:
            self.is_speaking = True
            
            # Clean text of markdown characters common in LLM outputs
            clean_text = text.replace("*", "").replace("_", "").replace("#", "")
            
            # Request audio stream from ElevenLabs
            audio_stream = self.client.generate(
                text=clean_text,
                voice=self.voice_id,
                model="eleven_multilingual_v2",
                stream=True,
                voice_settings={
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost
                }
            )
            
            # Initialize mpv as a background process to play the incoming stream
            self.current_process = subprocess.Popen(
                ["mpv", "--no-video", "--no-terminal", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Stream chunks to mpv stdin
            for chunk in audio_stream:
                if self._stop_event.is_set():
                    break
                if chunk:
                    try:
                        if self.current_process and self.current_process.stdin:
                            self.current_process.stdin.write(chunk)
                    except (IOError, BrokenPipeError):
                        break
            
            # Clean up process
            if self.current_process and self.current_process.stdin:
                self.current_process.stdin.close()
                self.current_process.wait()
                
        except Exception as e:
            # If cloud TTS fails (internet/quota), try the local fallback
            if self.fallback_engine:
                self.fallback_engine.speak(text)
        finally:
            self.is_speaking = False

    def stop(self) -> None:
        """
        Immediately halts speech synthesis and kills the playback process.
        """
        self._stop_event.set()
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process = None
            except:
                pass
