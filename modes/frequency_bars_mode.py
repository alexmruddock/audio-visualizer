"""
Frequency bars visualization mode.
"""

import pygame
from typing import Dict
from modes.base import VisualizationMode
from constants import (
    COLOR_BACKGROUND_DARK, COLOR_GRID, COLOR_TEXT_DIM, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY, COLOR_OVERLAY_BG, COLOR_OVERLAY_ALPHA,
    BAND_COLORS, BAND_POSITIONS, BAND_LABELS, SMOOTHING_FACTORS,
    BAR_BOTTOM_FRACTION, BAR_HEIGHT_FRACTION, PEAK_HOLD_DECAY,
    MAX_ENERGY_DECAY, BEAT_FLASH_ALPHA, BEAT_FLASH_HEIGHT_FACTOR,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, OVERLAY_MARGIN, OVERLAY_WIDTH,
    OVERLAY_HEIGHT_BASIC
)


class FrequencyBarsMode(VisualizationMode):
    """Professional high-fidelity multi-band frequency bar visualization."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.band_smoothed_values: Dict[str, float] = {}
        self.frequency_bars_max_energy: Dict[str, float] = {}
        self.frequency_bars_peak_hold: Dict[str, float] = {}
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        # Frequency bars don't need per-frame updates, smoothing happens in render
    
    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND_DARK)
        
        # Get band energies from features
        band_energies = self.features.get('band_energies', {})
        if not band_energies:
            # Fallback to basic bands
            band_energies = {
                'sub_bass': self.features.get('bass', 0) * 0.7,
                'bass': self.features.get('bass', 0),
                'low_mid': self.features.get('mid', 0) * 0.5,
                'mid': self.features.get('mid', 0),
                'high_mid': self.features.get('treble', 0) * 0.5,
                'treble': self.features.get('treble', 0),
                'high_treble': self.features.get('treble', 0) * 0.7,
            }
        
        # Smooth band energies with frequency-dependent smoothing
        smoothed_energies = {}
        for band, energy in band_energies.items():
            if band not in self.band_smoothed_values:
                self.band_smoothed_values[band] = energy
            else:
                smoothing_factor = SMOOTHING_FACTORS.get(band, 0.92)
                self.band_smoothed_values[band] = (
                    smoothing_factor * self.band_smoothed_values[band] + 
                    (1 - smoothing_factor) * energy
                )
            smoothed_energies[band] = self.band_smoothed_values[band]
        
        # Update historical maximums for independent band scaling
        for band, energy in smoothed_energies.items():
            if band not in self.frequency_bars_max_energy:
                self.frequency_bars_max_energy[band] = max(energy, 0.1)
            else:
                if energy > self.frequency_bars_max_energy[band]:
                    self.frequency_bars_max_energy[band] = energy
                else:
                    self.frequency_bars_max_energy[band] *= MAX_ENERGY_DECAY
        
        # Normalize each band independently
        normalized_energies = {}
        for band, energy in smoothed_energies.items():
            max_energy = self.frequency_bars_max_energy.get(band, 1.0)
            if max_energy > 0:
                normalized_energies[band] = min(0.9, energy / max_energy)
            else:
                normalized_energies[band] = 0.0
        
        smoothed_energies = normalized_energies
        
        # Update peak hold
        for band, energy in smoothed_energies.items():
            if band not in self.frequency_bars_peak_hold:
                self.frequency_bars_peak_hold[band] = energy
            else:
                self.frequency_bars_peak_hold[band] = max(
                    self.frequency_bars_peak_hold[band] * PEAK_HOLD_DECAY,
                    energy
                )
        
        # Define bands with colors and positions
        bands = [
            ('sub_bass', BAND_COLORS['sub_bass'], BAND_POSITIONS['sub_bass']),
            ('bass', BAND_COLORS['bass'], BAND_POSITIONS['bass']),
            ('low_mid', BAND_COLORS['low_mid'], BAND_POSITIONS['low_mid']),
            ('mid', BAND_COLORS['mid'], BAND_POSITIONS['mid']),
            ('high_mid', BAND_COLORS['high_mid'], BAND_POSITIONS['high_mid']),
            ('treble', BAND_COLORS['treble'], BAND_POSITIONS['treble']),
            ('high_treble', BAND_COLORS['high_treble'], BAND_POSITIONS['high_treble']),
        ]
        
        # Draw grid lines
        for i in range(5):
            y_pos = int(self.height * BAR_BOTTOM_FRACTION - (i * self.height * 0.15))
            pygame.draw.line(screen, COLOR_GRID, (0, y_pos), (self.width, y_pos), 1)
        
        # Draw vertical dividers
        for band_name, color, pos in bands[1:]:
            x_pos = int(pos * self.width)
            pygame.draw.line(screen, COLOR_GRID, (x_pos, 0), (x_pos, self.height), 1)
        
        # Draw frequency band labels
        font = pygame.font.Font(None, FONT_SIZE_SMALL)
        label_y = self.height - 25
        band_labels = [
            (BAND_LABELS['sub_bass'], BAND_POSITIONS['sub_bass']),
            (BAND_LABELS['bass'], BAND_POSITIONS['bass']),
            (BAND_LABELS['low_mid'], BAND_POSITIONS['low_mid']),
            (BAND_LABELS['mid'], BAND_POSITIONS['mid']),
            (BAND_LABELS['high_mid'], BAND_POSITIONS['high_mid']),
            (BAND_LABELS['treble'], BAND_POSITIONS['treble']),
            (BAND_LABELS['high_treble'], BAND_POSITIONS['high_treble']),
        ]
        
        for label, pos in band_labels:
            x_pos = int(pos * self.width)
            text_surface = font.render(label, True, COLOR_TEXT_DIM)
            screen.blit(text_surface, (x_pos - 25, label_y))
        
        # Draw bars
        bottom_y = int(self.height * BAR_BOTTOM_FRACTION)
        
        for i, (band_name, base_color, pos) in enumerate(bands):
            energy = smoothed_energies.get(band_name, 0)
            peak_hold = self.frequency_bars_peak_hold.get(band_name, 0)
            
            energy = max(0.0, min(1.0, energy))
            peak_hold = max(0.0, min(1.0, peak_hold))
            
            height = int(energy * self.height * BAR_HEIGHT_FRACTION)
            peak_height = int(peak_hold * self.height * BAR_HEIGHT_FRACTION)
            
            x = int(pos * self.width)
            if i < len(bands) - 1:
                section_width = int((bands[i+1][2] - pos) * self.width)
            else:
                section_width = self.width - x
            
            # Draw bar with gradient fill
            if height > 0:
                for y_offset in range(height):
                    gradient_factor = y_offset / max(1, height)
                    grad_color = (
                        int(base_color[0] * (0.4 + 0.6 * gradient_factor)),
                        int(base_color[1] * (0.4 + 0.6 * gradient_factor)),
                        int(base_color[2] * (0.4 + 0.6 * gradient_factor))
                    )
                    pygame.draw.line(screen, grad_color,
                                   (x + 2, bottom_y - y_offset),
                                   (x + section_width - 3, bottom_y - y_offset),
                                   1)
                
                highlight_color = (
                    min(255, base_color[0] + 60),
                    min(255, base_color[1] + 60),
                    min(255, base_color[2] + 60)
                )
                pygame.draw.line(screen, highlight_color,
                               (x + 2, bottom_y - height),
                               (x + section_width - 3, bottom_y - height),
                               3)
                pygame.draw.line(screen, highlight_color,
                               (x + 2, bottom_y - height),
                               (x + 2, bottom_y),
                               2)
            
            # Draw peak hold indicator
            if peak_height > height + 3:
                peak_y = bottom_y - peak_height
                pygame.draw.line(screen, COLOR_TEXT_WHITE,
                               (x + 2, peak_y),
                               (x + section_width - 3, peak_y),
                               2)
                pygame.draw.circle(screen, COLOR_TEXT_WHITE, (x + 2, peak_y), 3)
                pygame.draw.circle(screen, COLOR_TEXT_WHITE, (x + section_width - 3, peak_y), 3)
            
            # Beat flash effect
            if self.beat_triggered:
                flash_height = int(height * BEAT_FLASH_HEIGHT_FACTOR)
                flash_surface = pygame.Surface((section_width - 4, flash_height))
                flash_surface.set_alpha(BEAT_FLASH_ALPHA)
                flash_surface.fill(COLOR_TEXT_WHITE)
                screen.blit(flash_surface, (x + 2, bottom_y - flash_height))
        
        # Draw info overlay
        overlay_y = OVERLAY_MARGIN
        info_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        overlay_surface = pygame.Surface((OVERLAY_WIDTH, OVERLAY_HEIGHT_BASIC))
        overlay_surface.set_alpha(COLOR_OVERLAY_ALPHA)
        overlay_surface.fill(COLOR_OVERLAY_BG)
        screen.blit(overlay_surface, (OVERLAY_MARGIN, overlay_y))
        
        # Mode text (will be set by visualizer)
        mode_text = info_font.render("Frequency Bars", True, COLOR_TEXT_PRIMARY)
        screen.blit(mode_text, (OVERLAY_MARGIN + 10, overlay_y + 5))
        
        # BPM
        if self.current_bpm > 0:
            bpm_text = info_font.render(f"BPM: {int(self.current_bpm)}", True, COLOR_TEXT_WHITE)
            screen.blit(bpm_text, (OVERLAY_MARGIN + 10, overlay_y + 32))
        
        # Dominant frequency band
        dominant_band = max(smoothed_energies.items(), key=lambda x: x[1])[0] if smoothed_energies else "N/A"
        dominant_text = info_font.render(f"Dominant: {dominant_band.replace('_', ' ').title()}", True, COLOR_TEXT_SECONDARY)
        screen.blit(dominant_text, (OVERLAY_MARGIN + 10, overlay_y + 59))
        
        # Beat indicator at bottom
        if self.beat_triggered:
            beat_surface = pygame.Surface((self.width, 3))
            beat_surface.set_alpha(150)
            beat_surface.fill(COLOR_TEXT_WHITE)
            screen.blit(beat_surface, (0, bottom_y))
    
    def reset(self) -> None:
        self.band_smoothed_values.clear()
        self.frequency_bars_max_energy.clear()
        self.frequency_bars_peak_hold.clear()

