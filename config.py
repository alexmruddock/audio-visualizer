"""
Configuration module for audio visualizer settings.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class AudioConfig:
    """Audio capture and analysis configuration."""
    sample_rate: int = 44100
    frames_per_buffer: int = 1024
    hop_size: int = 256  # Reduced for higher overlap (75% overlap with 1024 buffer)
    buffer_size: int = 1024
    fft_size: int = 2048  # Larger FFT for better frequency resolution
    target_rms: float = 0.3  # Target RMS level for normalization
    autocorr_interval: int = 5  # Autocorrelation runs every N frames


@dataclass
class BPMConfig:
    """BPM detection configuration."""
    min_bpm: float = 60.0
    max_bpm: float = 200.0
    min_beat_interval: float = 0.25  # Minimum seconds between beats (max 240 BPM)
    beat_history_size: int = 20
    bpm_history_size: int = 10


@dataclass
class VisualizerConfig:
    """Visualization configuration."""
    width: int = 1280
    height: int = 720
    max_particles: int = 500
    fps_target: int = 60
    waveform_max_length: int = 1000
    waveform_reset_interval: float = 5.0  # Reset every N seconds


@dataclass
class FrequencyBands:
    """Frequency band definitions."""
    sub_bass: Tuple[float, float] = (20, 60)
    bass: Tuple[float, float] = (60, 250)
    low_mid: Tuple[float, float] = (250, 500)
    mid: Tuple[float, float] = (500, 2000)
    high_mid: Tuple[float, float] = (2000, 4000)
    treble: Tuple[float, float] = (4000, 10000)
    high_treble: Tuple[float, float] = (10000, 20000)


@dataclass
class Config:
    """Main configuration object."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    bpm: BPMConfig = field(default_factory=BPMConfig)
    visualizer: VisualizerConfig = field(default_factory=VisualizerConfig)
    frequency_bands: FrequencyBands = field(default_factory=FrequencyBands)

