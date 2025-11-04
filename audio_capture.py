"""
Audio capture module for capturing system audio from BlackHole device.
"""

import sounddevice as sd
import numpy as np
from typing import Optional, List, Tuple
import queue
import logging

# Set up logging
logger = logging.getLogger(__name__)


class AudioCapture:
    """Handles audio capture from system audio input devices."""
    
    def __init__(self, sample_rate: int = 44100, frames_per_buffer: int = 1024):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)
            frames_per_buffer: Buffer size in frames (default: 1024)
        """
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.stream: Optional[sd.InputStream] = None
        self.input_device_index: Optional[int] = None
        self.audio_queue: queue.Queue = queue.Queue()
        
    def list_devices(self) -> List[Tuple[int, str]]:
        """
        List all available audio input devices.
        
        Returns:
            List of tuples (device_index, device_name)
        """
        devices = []
        device_list = sd.query_devices()
        for i, device in enumerate(device_list):
            if device['max_input_channels'] > 0:
                devices.append((i, device['name']))
        return devices
    
    def find_blackhole_device(self) -> Optional[int]:
        """
        Find BlackHole audio device index.
        
        Returns:
            Device index if found, None otherwise
        """
        devices = self.list_devices()
        for idx, name in devices:
            if 'blackhole' in name.lower():
                return idx
        return None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        try:
            if status:
                logger.warning(f"Audio status: {status}")
            
            # Validate input data
            if indata is None or len(indata) == 0:
                logger.warning("Empty audio data received")
                return
            
            # Convert stereo to mono if needed
            try:
                if indata.shape[1] > 1:
                    audio_data = np.mean(indata, axis=1)
                else:
                    audio_data = indata[:, 0]
                
                # Validate audio data
                if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
                    logger.warning("Invalid audio data (NaN/Inf detected)")
                    audio_data = np.nan_to_num(audio_data, nan=0.0, posinf=0.0, neginf=0.0)
                
                self.audio_queue.put(audio_data.copy())
            except (IndexError, ValueError) as e:
                logger.error(f"Error processing audio callback: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in audio callback: {e}")
    
    def start_stream(self, device_index: Optional[int] = None) -> None:
        """
        Start audio capture stream.
        
        Args:
            device_index: Audio device index to use. If None, auto-detect BlackHole.
            
        Raises:
            RuntimeError: If device not found or stream cannot be started
            ValueError: If device configuration is invalid
        """
        try:
            if device_index is None:
                device_index = self.find_blackhole_device()
                if device_index is None:
                    raise RuntimeError(
                        "BlackHole device not found. Please ensure BlackHole is installed "
                        "and configured. Use list_devices() to see available devices."
                    )
            
            self.input_device_index = device_index
            
            # Get device info to determine channel count
            try:
                device_info = sd.query_devices(device_index)
            except Exception as e:
                raise ValueError(f"Invalid device index {device_index}: {e}")
            
            channels = min(device_info['max_input_channels'], 2)  # Use stereo if available, else mono
            
            if channels <= 0:
                raise ValueError(f"Device {device_index} has no input channels")
            
            # Open audio stream
            try:
                self.stream = sd.InputStream(
                    device=device_index,
                    channels=channels,
                    samplerate=self.sample_rate,
                    blocksize=self.frames_per_buffer,
                    callback=self._audio_callback,
                    dtype=np.float32
                )
                self.stream.start()
            except Exception as e:
                raise RuntimeError(f"Failed to start audio stream: {e}")
        except (RuntimeError, ValueError):
            raise
        except Exception as e:
            raise RuntimeError(f"Unexpected error starting audio stream: {e}")
    
    def read_chunk(self) -> np.ndarray:
        """
        Read a chunk of audio data.
        
        Returns:
            NumPy array of audio samples (float32, normalized to [-1, 1])
            
        Raises:
            RuntimeError: If stream is not started or reading fails
        """
        if self.stream is None:
            raise RuntimeError("Stream not started. Call start_stream() first.")
        
        try:
            # Get audio data from queue
            samples = self.audio_queue.get(timeout=1.0)
            
            # Validate samples
            if samples is None or len(samples) == 0:
                logger.warning("Empty samples received, returning zeros")
                return np.zeros(self.frames_per_buffer, dtype=np.float32)
            
            # Ensure correct dtype and handle NaN/Inf
            samples = np.asarray(samples, dtype=np.float32)
            if np.any(np.isnan(samples)) or np.any(np.isinf(samples)):
                logger.warning("Invalid samples (NaN/Inf detected), cleaning")
                samples = np.nan_to_num(samples, nan=0.0, posinf=0.0, neginf=0.0)
            
            return samples
        except queue.Empty:
            # Return zeros if no data available (timeout)
            logger.debug("Audio queue timeout, returning zeros")
            return np.zeros(self.frames_per_buffer, dtype=np.float32)
        except Exception as e:
            logger.error(f"Error reading audio data: {e}")
            raise RuntimeError(f"Error reading audio data: {e}")
    
    def stop_stream(self) -> None:
        """Stop audio capture stream."""
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop_stream()
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

