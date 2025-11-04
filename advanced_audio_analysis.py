"""
Advanced audio analysis techniques inspired by professional DAWs.
"""

import numpy as np
from typing import Tuple, Optional


class AdvancedAudioAnalyzer:
    """
    Advanced audio analysis with techniques used by professional DAWs.
    
    Techniques inspired by Ableton Live, Logic Pro, and other professional software:
    - Multiple FFT window sizes for different purposes
    - Overlap-add processing for smoother analysis
    - Advanced windowing functions
    - Multiple onset detection algorithms
    - Spectral feature extraction
    - Transient detection
    """
    
    @staticmethod
    def hann_window(size: int) -> np.ndarray:
        """Hann window for better frequency resolution."""
        return np.hanning(size)
    
    @staticmethod
    def blackman_window(size: int) -> np.ndarray:
        """Blackman window for better side-lobe rejection."""
        return np.blackman(size)
    
    @staticmethod
    def spectral_flux(magnitude: np.ndarray, prev_magnitude: Optional[np.ndarray] = None) -> float:
        """
        Calculate spectral flux - measures change in frequency content.
        Used by Ableton Live for onset detection.
        """
        if prev_magnitude is None or len(prev_magnitude) != len(magnitude):
            return 0.0
        
        # Positive differences only (energy increase)
        diff = magnitude - prev_magnitude
        positive_diff = np.maximum(diff, 0)
        return float(np.sum(positive_diff))
    
    @staticmethod
    def spectral_rolloff(magnitude: np.ndarray, freqs: np.ndarray, percentile: float = 0.85) -> float:
        """
        Calculate spectral rolloff - frequency below which X% of energy resides.
        Useful for distinguishing percussive vs sustained sounds.
        """
        total_energy = np.sum(magnitude)
        if total_energy == 0:
            return 0.0
        
        cumsum = np.cumsum(magnitude)
        threshold = total_energy * percentile
        
        # Find frequency where cumulative energy exceeds threshold
        idx = np.where(cumsum >= threshold)[0]
        if len(idx) > 0:
            return float(freqs[idx[0]])
        return float(freqs[-1])
    
    @staticmethod
    def spectral_centroid(magnitude: np.ndarray, freqs: np.ndarray) -> float:
        """
        Calculate spectral centroid - indicates brightness/timbre.
        Higher values = brighter sound.
        """
        total_energy = np.sum(magnitude)
        if total_energy == 0:
            return 0.0
        
        weighted_sum = np.sum(freqs * magnitude)
        return float(weighted_sum / total_energy)
    
    @staticmethod
    def zero_crossing_rate(samples: np.ndarray) -> float:
        """
        Calculate zero-crossing rate - indicates noisiness/transient content.
        Higher values = more transient/noisy.
        """
        if len(samples) < 2:
            return 0.0
        
        signs = np.sign(samples)
        crossings = np.sum(np.abs(np.diff(signs))) / 2
        return float(crossings / len(samples))
    
    @staticmethod
    def detect_transient(samples: np.ndarray, 
                        prev_samples: Optional[np.ndarray] = None,
                        threshold: float = 0.3) -> bool:
        """
        Detect transient (sudden energy increase).
        Used to separate kick drums from sustained bass.
        """
        if prev_samples is None or len(prev_samples) != len(samples):
            return False
        
        current_energy = np.mean(np.abs(samples))
        prev_energy = np.mean(np.abs(prev_samples))
        
        if prev_energy == 0:
            return current_energy > threshold
        
        # Transient if energy increases significantly
        energy_ratio = current_energy / prev_energy
        return energy_ratio > (1.0 + threshold)
    
    @staticmethod
    def phase_deviation(samples: np.ndarray, 
                       prev_samples: Optional[np.ndarray] = None) -> float:
        """
        Calculate phase deviation - measures phase changes.
        Useful for detecting attacks in sustained sounds.
        """
        if prev_samples is None or len(prev_samples) != len(samples):
            return 0.0
        
        # Use Hilbert transform to get phase
        from scipy.signal import hilbert
        
        try:
            analytic_current = hilbert(samples)
            analytic_prev = hilbert(prev_samples)
            
            phase_current = np.angle(analytic_current)
            phase_prev = np.angle(analytic_prev)
            
            phase_diff = np.abs(phase_current - phase_prev)
            # Normalize to 0-1
            phase_diff = np.minimum(phase_diff, np.pi) / np.pi
            
            return float(np.mean(phase_diff))
        except:
            return 0.0


def compute_spectral_features(magnitude: np.ndarray, 
                              freqs: np.ndarray,
                              prev_magnitude: Optional[np.ndarray] = None) -> dict:
    """
    Compute multiple spectral features like professional DAWs.
    
    Returns:
        Dictionary with spectral features:
        - spectral_flux: Change in frequency content
        - spectral_rolloff: Frequency containing 85% of energy
        - spectral_centroid: Brightness indicator
        - spectral_bandwidth: Frequency spread
    """
    features = {}
    
    # Spectral flux
    features['spectral_flux'] = AdvancedAudioAnalyzer.spectral_flux(magnitude, prev_magnitude)
    
    # Spectral rolloff
    features['spectral_rolloff'] = AdvancedAudioAnalyzer.spectral_rolloff(magnitude, freqs)
    
    # Spectral centroid (brightness)
    features['spectral_centroid'] = AdvancedAudioAnalyzer.spectral_centroid(magnitude, freqs)
    
    # Spectral bandwidth (spread around centroid)
    if features['spectral_centroid'] > 0:
        centroid_diff = (freqs - features['spectral_centroid']) ** 2
        weighted_diff = np.sum(centroid_diff * magnitude)
        total_energy = np.sum(magnitude)
        if total_energy > 0:
            features['spectral_bandwidth'] = float(np.sqrt(weighted_diff / total_energy))
        else:
            features['spectral_bandwidth'] = 0.0
    else:
        features['spectral_bandwidth'] = 0.0
    
    return features

