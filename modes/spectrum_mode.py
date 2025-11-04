"""
Spectrum analyzer visualization mode.
"""

import pygame
import numpy as np
from typing import List, Optional
from modes.base import VisualizationMode
from constants import (
    COLOR_BACKGROUND_DARK, COLOR_GRID, COLOR_TEXT_DIM, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY, COLOR_OVERLAY_BG, COLOR_OVERLAY_ALPHA,
    BAR_BOTTOM_FRACTION, BAR_HEIGHT_FRACTION, SPECTRUM_MAX_BARS,
    SPECTRUM_PEAK_HOLD_DECAY, SPECTRUM_FREQUENCY_LABELS,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, OVERLAY_MARGIN, OVERLAY_WIDTH,
    OVERLAY_HEIGHT_TALL, HELP_TEXT_Y_OFFSET_SPECTRUM
)


class SpectrumMode(VisualizationMode):
    """Professional high-fidelity spectrum analyzer."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.spectrum_peak_hold: Optional[np.ndarray] = None
        self.spectrum_rms_history: List[np.ndarray] = []
        self.spectrum_rms_history_size = 5
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        # Spectrum smoothing happens in render
    
    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND_DARK)
        
        # Get spectrum from features
        if 'spectrum' not in self.features or self.features['spectrum'] is None:
            return
        
        spectrum = np.array(self.features['spectrum'])
        if len(spectrum) == 0:
            return
        
        # Filter out NaN and Inf values
        spectrum = np.nan_to_num(spectrum, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Smooth spectrum with RMS averaging
        self.spectrum_rms_history.append(spectrum.copy())
        if len(self.spectrum_rms_history) > self.spectrum_rms_history_size:
            self.spectrum_rms_history.pop(0)
        
        # Calculate RMS average
        if len(self.spectrum_rms_history) > 0:
            spectrum_array = np.array(self.spectrum_rms_history)
            spectrum_smooth = np.mean(spectrum_array, axis=0)
        else:
            spectrum_smooth = spectrum
        
        # Normalize spectrum (log scale)
        max_val = np.max(spectrum_smooth)
        if max_val > 0:
            normalized = np.log10(spectrum_smooth + 1) / np.log10(max_val + 1)
            normalized = np.nan_to_num(normalized, nan=0.0, posinf=0.0, neginf=0.0)
        else:
            normalized = np.zeros_like(spectrum_smooth)
        
        # Initialize/update peak hold
        if self.spectrum_peak_hold is None or len(self.spectrum_peak_hold) != len(normalized):
            self.spectrum_peak_hold = normalized.copy()
        else:
            self.spectrum_peak_hold = np.maximum(
                self.spectrum_peak_hold * SPECTRUM_PEAK_HOLD_DECAY,
                normalized
            )
        
        # Downsample for performance
        max_bars = min(SPECTRUM_MAX_BARS, self.width // 2)
        if len(normalized) > max_bars:
            indices = np.linspace(0, len(normalized) - 1, max_bars, dtype=int)
            normalized = normalized[indices]
            self.spectrum_peak_hold = self.spectrum_peak_hold[indices]
            spectrum_smooth = spectrum_smooth[indices]
        
        # Draw grid lines
        for i in range(5):
            y_pos = int(self.height * BAR_BOTTOM_FRACTION - (i * self.height * 0.15))
            pygame.draw.line(screen, COLOR_GRID, (0, y_pos), (self.width, y_pos), 1)
        
        # Draw frequency labels with grid markers
        font = pygame.font.Font(None, FONT_SIZE_SMALL)
        label_y = self.height - HELP_TEXT_Y_OFFSET_SPECTRUM
        
        for label, pos in SPECTRUM_FREQUENCY_LABELS:
            x_pos = int(pos * self.width)
            pygame.draw.line(screen, COLOR_GRID, (x_pos, 0), (x_pos, self.height), 1)
            text_surface = font.render(label, True, COLOR_TEXT_DIM)
            screen.blit(text_surface, (x_pos - 20, label_y))
        
        # Draw spectrum bars
        bar_width = max(1, self.width // len(normalized))
        bottom_y = int(self.height * BAR_BOTTOM_FRACTION)
        
        for i in range(len(normalized)):
            x = int((i / len(normalized)) * self.width)
            norm_val = float(normalized[i])
            norm_val = max(0.0, min(1.0, norm_val))
            height = int(norm_val * self.height * BAR_HEIGHT_FRACTION)
            
            # Calculate frequency-based color
            freq_hue = i / len(normalized) if len(normalized) > 0 else 0.0
            freq_hue = 0.0 if np.isnan(freq_hue) or np.isinf(freq_hue) else freq_hue
            
            # Professional spectrum color mapping
            if freq_hue < 0.2:
                r, g, b = int(180 + freq_hue * 75), 0, int(150 + freq_hue * 105)
            elif freq_hue < 0.4:
                t = (freq_hue - 0.2) / 0.2
                r, g, b = 255, int(t * 100), 0
            elif freq_hue < 0.55:
                t = (freq_hue - 0.4) / 0.15
                r, g, b = 255, 255, int(t * 255)
            elif freq_hue < 0.7:
                t = (freq_hue - 0.55) / 0.15
                r, g, b = int(255 * (1 - t)), 255, int(255 * t)
            elif freq_hue < 0.85:
                t = (freq_hue - 0.7) / 0.15
                r, g, b = 0, int(255 * (1 - t)), 255
            else:
                t = (freq_hue - 0.85) / 0.15
                r, g, b = int(255 * t), 0, 255
            
            # Draw bar with gradient
            if height > 0:
                base_color = (r, g, b)
                
                for y_offset in range(height):
                    gradient_factor = y_offset / max(1, height)
                    grad_color = (
                        int(base_color[0] * (0.3 + 0.7 * gradient_factor)),
                        int(base_color[1] * (0.3 + 0.7 * gradient_factor)),
                        int(base_color[2] * (0.3 + 0.7 * gradient_factor))
                    )
                    pygame.draw.line(screen, grad_color,
                                   (x, bottom_y - y_offset),
                                   (x + bar_width - 1, bottom_y - y_offset),
                                   1)
                
                highlight_color = (
                    min(255, base_color[0] + 50),
                    min(255, base_color[1] + 50),
                    min(255, base_color[2] + 50)
                )
                pygame.draw.line(screen, highlight_color,
                               (x, bottom_y - height),
                               (x + bar_width - 1, bottom_y - height),
                               2)
            
            # Draw peak hold indicator
            peak_height = int(self.spectrum_peak_hold[i] * self.height * BAR_HEIGHT_FRACTION)
            if peak_height > height + 2:
                peak_y = bottom_y - peak_height
                pygame.draw.circle(screen, COLOR_TEXT_WHITE,
                                 (x + bar_width // 2, peak_y), 2)
        
        # Draw info overlay
        overlay_y = OVERLAY_MARGIN
        info_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        overlay_surface = pygame.Surface((OVERLAY_WIDTH, OVERLAY_HEIGHT_TALL))
        overlay_surface.set_alpha(COLOR_OVERLAY_ALPHA)
        overlay_surface.fill(COLOR_OVERLAY_BG)
        screen.blit(overlay_surface, (OVERLAY_MARGIN, overlay_y))
        
        mode_text = info_font.render("Spectrum Analyzer", True, COLOR_TEXT_PRIMARY)
        screen.blit(mode_text, (OVERLAY_MARGIN + 10, overlay_y + 5))
        
        if self.current_bpm > 0:
            bpm_text = info_font.render(f"BPM: {int(self.current_bpm)}", True, COLOR_TEXT_WHITE)
            screen.blit(bpm_text, (OVERLAY_MARGIN + 10, overlay_y + 32))
        
        rms = self.features.get('rms', 0)
        peak = self.features.get('peak', 0)
        gain = self.features.get('volume_gain', 1.0)
        
        texts = [
            f"RMS: {rms:.3f}",
            f"Peak: {peak:.3f}",
            f"Gain: {gain:.2f}x"
        ]
        
        for i, text in enumerate(texts):
            text_surface = info_font.render(text, True, COLOR_TEXT_SECONDARY)
            screen.blit(text_surface, (OVERLAY_MARGIN + 10, overlay_y + 59 + i * 22))
        
        # Draw beat indicator
        if self.beat_triggered:
            beat_surface = pygame.Surface((self.width, 3))
            beat_surface.set_alpha(150)
            beat_surface.fill(COLOR_TEXT_WHITE)
            screen.blit(beat_surface, (0, bottom_y))
    
    def reset(self) -> None:
        self.spectrum_peak_hold = None
        self.spectrum_rms_history.clear()

