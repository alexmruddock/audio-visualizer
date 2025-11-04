"""
Audio analysis module for BPM detection and frequency analysis.
"""

import numpy as np
import time
from typing import Optional, Tuple, Deque, TYPE_CHECKING
from collections import deque

# Import config types with fallback
if TYPE_CHECKING:
    from config import Config, AudioConfig, BPMConfig, FrequencyBands
else:
    try:
        from config import Config, AudioConfig, BPMConfig, FrequencyBands
    except ImportError:
        Config = None
        AudioConfig = None
        BPMConfig = None
        FrequencyBands = None


class AudioAnalyzer:
    """Analyzes audio for BPM detection and frequency features."""
    
    def __init__(
        self,
        sample_rate: int = 44100,
        hop_size: int = 512,
        buffer_size: int = 1024,
        config: Optional['Config'] = None
    ):
        """
        Initialize audio analyzer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            hop_size: Hop size for processing
            buffer_size: Buffer size for audio processing
            config: Optional Config object (uses defaults if None)
        """
        # Use config if provided, otherwise use defaults
        if config:
            audio_cfg = config.audio
            bpm_cfg = config.bpm
            freq_bands = config.frequency_bands
        else:
            # Create default configs
            audio_cfg = AudioConfig() if AudioConfig else type('', (), {
                'sample_rate': 44100, 'hop_size': 512, 'buffer_size': 1024,
                'target_rms': 0.3, 'autocorr_interval': 5
            })()
            bpm_cfg = BPMConfig() if BPMConfig else type('', (), {
                'min_bpm': 60.0, 'max_bpm': 200.0, 'min_beat_interval': 0.25,
                'beat_history_size': 20, 'bpm_history_size': 10
            })()
            freq_bands = FrequencyBands() if FrequencyBands else type('', (), {
                'sub_bass': (20, 60), 'bass': (60, 250), 'low_mid': (250, 500),
                'mid': (500, 2000), 'high_mid': (2000, 4000),
                'treble': (4000, 10000), 'high_treble': (10000, 20000)
            })()
        
        self.sample_rate = sample_rate or audio_cfg.sample_rate
        self.hop_size = hop_size or audio_cfg.hop_size
        self.buffer_size = buffer_size or audio_cfg.buffer_size
        
        # Store config for later use
        self.config = config
        self.audio_cfg = audio_cfg
        
        # BPM detection with autocorrelation
        self.beat_times: Deque[float] = deque(maxlen=bpm_cfg.beat_history_size)
        self.current_bpm: float = 0.0
        self.last_beat_time: Optional[float] = None
        self.min_beat_interval = bpm_cfg.min_beat_interval
        
        # Audio buffer for beat detection (using bass-weighted energy)
        self.audio_buffer: Deque[float] = deque(maxlen=2048)
        
        # Previous magnitude for spectral flux calculation
        self.prev_magnitude: Optional[np.ndarray] = None
        
        # Previous samples for transient detection
        self.prev_samples: Optional[np.ndarray] = None
        
        # BPM smoothing buffer
        self.bpm_history: Deque[float] = deque(maxlen=bpm_cfg.bpm_history_size)
        
        # Performance: throttle autocorrelation (expensive operation)
        self.autocorr_frame_count = 0
        self.autocorr_interval = audio_cfg.autocorr_interval
        
        # Volume normalization
        self.peak_level = 0.0
        self.rms_level = 0.0
        self.volume_gain = 1.0
        self.target_rms = audio_cfg.target_rms
        
        # Frequency bands (Hz) - more granular analysis
        self.sub_bass_range = freq_bands.sub_bass
        self.bass_range = freq_bands.bass
        self.low_mid_range = freq_bands.low_mid
        self.mid_range = freq_bands.mid
        self.high_mid_range = freq_bands.high_mid
        self.treble_range = freq_bands.treble
        self.high_treble_range = freq_bands.high_treble
        
        # BPM limits
        self.min_bpm = bpm_cfg.min_bpm
        self.max_bpm = bpm_cfg.max_bpm
        
        # Spectrum analyzer buffer
        self.spectrum_buffer: Deque[np.ndarray] = deque(maxlen=100)
        
    def _detect_onset(self, samples: np.ndarray, bass_energy: float = 0.0) -> bool:
        """
        Detect onset (beat) using bass-weighted energy envelope.
        Focuses on kick drums in techno/electronic music.
        
        Args:
            samples: Audio samples
            bass_energy: Energy in bass frequencies (from FFT)
        
        Returns:
            True if onset detected
        """
        # Calculate total energy
        total_energy = np.sum(samples ** 2)
        
        # Weight bass energy more heavily for kick drum detection
        # Bass energy is already calculated from FFT
        weighted_energy = total_energy * 0.3 + bass_energy * 0.7
        
        # Check minimum time since last beat
        current_time = time.time()
        if self.last_beat_time is not None:
            time_since_last = current_time - self.last_beat_time
            if time_since_last < self.min_beat_interval:
                self.audio_buffer.append(weighted_energy)
                return False
        
        # Threshold-based onset detection with adaptive threshold
        if len(self.audio_buffer) > 10:
            recent_energy = np.mean(list(self.audio_buffer)[-10:])
            # Lower threshold (2.0x) for better sensitivity to techno beats
            # Use dynamic threshold based on recent energy
            threshold = recent_energy * 2.0
            # Also check if weighted energy exceeds absolute minimum
            min_threshold = max(0.005, recent_energy * 1.5)
            
            if weighted_energy > threshold and weighted_energy > min_threshold:
                self.last_beat_time = current_time
                return True
        
        self.audio_buffer.append(weighted_energy)
        return False
    
    def process_audio(self, samples: np.ndarray) -> Tuple[bool, float, dict]:
        """
        Process audio chunk and extract features.
        
        Args:
            samples: Audio samples (float32 array)
            
        Returns:
            Tuple of (is_beat, bpm, features_dict)
            - is_beat: Boolean indicating if a beat was detected
            - bpm: Current BPM estimate
            - features: Dictionary with frequency band data
            
        Raises:
            ValueError: If samples array is invalid
        """
        # Validate input
        if samples is None or len(samples) == 0:
            return False, self.current_bpm, self._get_default_features()
        
        try:
            samples = np.asarray(samples, dtype=np.float32)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid audio samples: {e}")
        
        # Ensure samples are the right size
        if len(samples) < self.hop_size:
            samples = np.pad(samples, (0, self.hop_size - len(samples)))
        
        # Frequency analysis using FFT with professional techniques
        # Use longer buffer for better frequency resolution
        if len(samples) < self.buffer_size:
            fft_samples = np.pad(samples, (0, self.buffer_size - len(samples)))
        else:
            fft_samples = samples[:self.buffer_size]
        
        # Apply Hann window for better frequency resolution (professional technique)
        window = np.hanning(len(fft_samples))
        windowed_samples = fft_samples * window
        
        # Zero-pad for better frequency resolution (common in professional DAWs)
        fft_size = getattr(self.audio_cfg, 'fft_size', 2048) if self.audio_cfg else 2048
        fft_result = np.fft.rfft(windowed_samples, n=fft_size)
        magnitude = np.abs(fft_result)
        freqs = np.fft.rfftfreq(fft_size, 1.0 / self.sample_rate)
        
        # Calculate positive frequencies only (rfft already gives positive only)
        positive_freqs = freqs
        positive_magnitude = magnitude
        
        # Calculate spectral flux for better onset detection
        spectral_flux = 0.0
        if self.prev_magnitude is not None and len(self.prev_magnitude) == len(positive_magnitude):
            # Positive differences only (energy increase)
            diff = positive_magnitude - self.prev_magnitude
            positive_diff = np.maximum(diff, 0)
            spectral_flux = float(np.sum(positive_diff))
        
        # Store current magnitude and samples for next iteration
        self.prev_magnitude = positive_magnitude.copy()
        self.prev_samples = samples.copy()
        
        # Get bass energy for beat detection (kick drums are typically 60-100 Hz)
        bass_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.bass_range)
        
        # Enhanced beat detection: combine energy-based and spectral flux
        energy_onset = self._detect_onset(samples[:self.hop_size], bass_energy)
        
        # Spectral flux also indicates onset (sudden frequency content change)
        flux_threshold = np.mean(positive_magnitude) * 0.5  # Adaptive threshold
        flux_onset = spectral_flux > flux_threshold
        
        # Combine both methods for more accurate beat detection
        is_beat = energy_onset or (flux_onset and bass_energy > 0.01)
        
        if is_beat:
            current_time = time.time()
            self.beat_times.append(current_time)
            
            if len(self.beat_times) >= 2:
                # Calculate BPM from beat intervals using actual timestamps
                intervals = np.diff(list(self.beat_times))
                if len(intervals) > 0:
                    # Filter out outliers (beats too close or too far apart)
                    # 0.3 seconds = max 200 BPM, 3.0 seconds = min 20 BPM
                    filtered_intervals = intervals[(intervals >= 0.3) & (intervals <= 3.0)]
                    if len(filtered_intervals) > 0:
                        avg_interval = np.mean(filtered_intervals)
                        if avg_interval > 0:
                            # Convert interval (seconds) to BPM
                            calculated_bpm = 60.0 / avg_interval
                            # Clamp to reasonable range
                            calculated_bpm = np.clip(calculated_bpm, self.min_bpm, self.max_bpm)
                            
                            # Use autocorrelation for better BPM detection (throttled for performance)
                            self.autocorr_frame_count += 1
                            if self.autocorr_frame_count >= self.autocorr_interval:
                                autocorr_bpm = self._autocorrelation_bpm(samples)
                                if autocorr_bpm > 0:
                                    # Blend autocorrelation with beat interval method
                                    calculated_bpm = 0.7 * calculated_bpm + 0.3 * autocorr_bpm
                                self.autocorr_frame_count = 0
                            
                            # Smooth BPM with moving average
                            self.bpm_history.append(calculated_bpm)
                            if len(self.bpm_history) >= 3:
                                self.current_bpm = np.mean(list(self.bpm_history))
                            else:
                                self.current_bpm = calculated_bpm
                    elif len(intervals) > 0:
                        # Fallback if all intervals are outliers
                        avg_interval = np.median(intervals)
                        if 0.3 <= avg_interval <= 3.0:
                            calculated_bpm = 60.0 / avg_interval
                            self.current_bpm = np.clip(calculated_bpm, self.min_bpm, self.max_bpm)
        
        # Calculate frequency band energies (already computed above)
        try:
            mid_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.mid_range)
            treble_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.treble_range)
            
            # Volume normalization
            rms = np.sqrt(np.mean(samples ** 2))
            peak = np.abs(samples).max()
            
            # Update levels with exponential moving average
            self.rms_level = 0.9 * self.rms_level + 0.1 * rms
            self.peak_level = 0.9 * self.peak_level + 0.1 * peak
            
            # Auto-gain control (prevent clipping)
            if self.rms_level > 0.01:
                target_gain = self.target_rms / self.rms_level
                self.volume_gain = 0.95 * self.volume_gain + 0.05 * target_gain
                self.volume_gain = min(2.0, max(0.1, self.volume_gain))  # Clamp gain
            
            # Calculate multiple frequency bands
            sub_bass_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.sub_bass_range)
            low_mid_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.low_mid_range)
            high_mid_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.high_mid_range)
            high_treble_energy = self._get_band_energy(positive_magnitude, positive_freqs, self.high_treble_range)
            
            # Store spectrum for analyzer view (downsampled for performance)
            # Only store every Nth value to reduce memory and processing
            spectrum_downsample = 2
            if len(positive_magnitude) > 512:
                spectrum_indices = np.linspace(0, len(positive_magnitude) - 1, 512, dtype=int)
                spectrum_data = positive_magnitude[spectrum_indices]
            else:
                spectrum_data = positive_magnitude[::spectrum_downsample]
            self.spectrum_buffer.append(spectrum_data.copy())
            
            # Normalize energies (0-1 range) for bass/mid/treble
            total_energy = bass_energy + mid_energy + treble_energy
            normalized_bass = bass_energy / total_energy if total_energy > 0 else 0
            normalized_mid = mid_energy / total_energy if total_energy > 0 else 0
            normalized_treble = treble_energy / total_energy if total_energy > 0 else 0
            
            # Calculate band energies for detailed analysis (raw values)
            raw_band_energies = {
                'sub_bass': float(sub_bass_energy),
                'bass': float(bass_energy),
                'low_mid': float(low_mid_energy),
                'mid': float(mid_energy),
                'high_mid': float(high_mid_energy),
                'treble': float(treble_energy),
                'high_treble': float(high_treble_energy),
            }
            
            # Normalize band energies (0-1 range) relative to the maximum band energy
            max_band_energy = max(raw_band_energies.values()) if raw_band_energies.values() else 1.0
            if max_band_energy > 0:
                band_energies = {
                    band: float(energy / max_band_energy)
                    for band, energy in raw_band_energies.items()
                }
            else:
                band_energies = {band: 0.0 for band in raw_band_energies.keys()}
            
            # Calculate advanced spectral features
            spectral_centroid = self._calculate_spectral_centroid(positive_magnitude, positive_freqs)
            
            features = {
                'bass': float(normalized_bass),
                'mid': float(normalized_mid),
                'treble': float(normalized_treble),
                'total_energy': float(np.mean(positive_magnitude)),
                'spectral_centroid': float(spectral_centroid),
                'spectral_flux': float(spectral_flux),
                'band_energies': band_energies,
                'spectrum': spectrum_data,  # Full spectrum for analyzer (downsampled)
                'rms': float(self.rms_level),
                'peak': float(self.peak_level),
                'volume_gain': float(self.volume_gain)
            }
        except Exception as e:
            # Return default features on error
            import sys
            print(f"Warning: Error processing audio features: {e}", file=sys.stderr)
            return False, self.current_bpm, self._get_default_features()
        
        return is_beat, self.current_bpm, features
    
    def _get_default_features(self) -> dict:
        """Return default feature dictionary for error cases."""
        return {
            'bass': 0.0,
            'mid': 0.0,
            'treble': 0.0,
            'total_energy': 0.0,
            'spectral_centroid': 0.0,
            'spectral_flux': 0.0,
            'band_energies': {
                'sub_bass': 0.0, 'bass': 0.0, 'low_mid': 0.0,
                'mid': 0.0, 'high_mid': 0.0, 'treble': 0.0, 'high_treble': 0.0
            },
            'spectrum': np.array([]),
            'rms': 0.0,
            'peak': 0.0,
            'volume_gain': 1.0
        }
    
    def _get_band_energy(
        self,
        magnitude: np.ndarray,
        freqs: np.ndarray,
        freq_range: Tuple[float, float]
    ) -> float:
        """Calculate energy in a frequency band."""
        mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
        return float(np.sum(magnitude[mask]))
    
    def _calculate_spectral_centroid(
        self,
        magnitude: np.ndarray,
        freqs: np.ndarray
    ) -> float:
        """Calculate spectral centroid (brightness indicator)."""
        if np.sum(magnitude) == 0:
            return 0.0
        return float(np.sum(freqs * magnitude) / np.sum(magnitude))
    
    def _autocorrelation_bpm(self, samples: np.ndarray) -> float:
        """
        Estimate BPM using autocorrelation on energy envelope.
        
        Returns:
            Estimated BPM (0 if detection fails)
        """
        if len(samples) < 512:
            return 0.0
        
        # Calculate energy envelope
        window_size = 256
        energy_envelope = []
        for i in range(0, len(samples) - window_size, window_size // 2):
            window = samples[i:i + window_size]
            energy = np.sum(window ** 2)
            energy_envelope.append(energy)
        
        if len(energy_envelope) < 32:
            return 0.0
        
        energy_array = np.array(energy_envelope)
        
        # Normalize
        if np.std(energy_array) > 0:
            energy_array = (energy_array - np.mean(energy_array)) / np.std(energy_array)
        
        # Autocorrelation
        autocorr = np.correlate(energy_array, energy_array, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        
        # Find peaks in autocorrelation (corresponding to periodicities)
        # Look for peaks in BPM range (60-200 BPM)
        # Convert to samples: at 44.1kHz, window_size samples = window_size/44100 seconds
        sample_period = window_size / self.sample_rate
        
        # BPM range: 60-200 BPM = 1.0s to 0.3s period
        min_period_samples = int(0.3 / sample_period)  # 200 BPM
        max_period_samples = int(1.0 / sample_period)   # 60 BPM
        
        if len(autocorr) < max_period_samples:
            return 0.0
        
        # Find peak in valid range
        valid_range = autocorr[min_period_samples:max_period_samples]
        if len(valid_range) == 0:
            return 0.0
        
        peak_idx = np.argmax(valid_range) + min_period_samples
        period_samples = peak_idx
        
        # Convert to BPM
        period_seconds = period_samples * sample_period
        if period_seconds > 0:
            estimated_bpm = 60.0 / period_seconds
            return np.clip(estimated_bpm, self.min_bpm, self.max_bpm)
        
        return 0.0
    
    def get_bpm(self) -> float:
        """Get current BPM estimate."""
        return self.current_bpm
    
    def reset(self) -> None:
        """Reset analyzer state."""
        self.beat_times.clear()
        self.current_bpm = 0.0
        self.last_beat_time = None
        self.bpm_history.clear()
        self.peak_level = 0.0
        self.rms_level = 0.0
        self.volume_gain = 1.0
        self.spectrum_buffer.clear()

