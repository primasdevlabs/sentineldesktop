"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: modules/audio/input.py
Description: Low-level audio capture wrapper. Provides a high-performance 
             PCM stream for AI hardware modules.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import numpy as np
import sounddevice as sd
import queue
import logging
from typing import Optional, Any

class AudioInput:
    """
    Buffer-managed microphone input handler.
    
    Wraps the sounddevice library to provide a thread-safe queue of 
    audio frames, specifically formatted for NLU and Wake Word engines.
    """
    
    def __init__(self, sample_rate: int = 16000, frame_length: int = 512) -> None:
        """
        Initializes the input parameters.
        
        Args:
            sample_rate: Recording rate (Hz). Defaults to 16k for AI engines.
            frame_length: Number of samples per frame.
        """
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.audio_queue: queue.Queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self.logger = logging.getLogger("AudioInput")

    def _callback(self, indata: np.ndarray, frames: int, time: Any, status: sd.CallbackFlags) -> None:
        """
        Hardware callback function: Invoked whenever new audio data is available.
        
        Converts float32 audio to the int16 PCM format required by 
        Picovoice/Rhasspy and adds it to the internal queue.
        """
        if status:
            self.logger.warning(f"Microphone Hardware Error: {status}")
            
        # Conversion: Float (-1.0 to 1.0) to Int16 (-32767 to 32767)
        pcm = (indata * 32767).astype(np.int16)
        self.audio_queue.put(pcm.flatten())

    def start(self) -> bool:
        """
        Initializes the hardware input stream.
        
        Returns:
            bool: True if the stream started successfully.
        """
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.frame_length,
                callback=self._callback,
                dtype='float32'
            )
            self.stream.start()
            self.logger.info(f"Microphone initialized at {self.sample_rate}Hz.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to access microphone: {e}")
            return False

    def read(self) -> np.ndarray:
        """
        Blocking read: Retrieves the oldest audio frame from the queue.
        
        Returns:
            np.ndarray: A frame of int16 PCM audio.
        """
        return self.audio_queue.get()

    def stop(self) -> None:
        """Terminates the hardware stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
