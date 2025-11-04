"""
Waveform visualization mode.
"""

import pygame
from typing import List
from modes.base import VisualizationMode
from constants import (
    COLOR_BACKGROUND_WAVEFORM, COLOR_GRID_WAVEFORM, COLOR_CENTER_LINE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY,
    COLOR_OVERLAY_BG, COLOR_OVERLAY_ALPHA, WAVEFORM_SCALE_FACTOR,
    WAVEFORM_MARGIN, WAVEFORM_MAX_LENGTH, WAVEFORM_RESET_INTERVAL,
    WAVEFORM_PEAK_DECAY, FONT_SIZE_MEDIUM, OVERLAY_MARGIN, OVERLAY_WIDTH,
    OVERLAY_HEIGHT_BASIC
)


class WaveformMode(VisualizationMode):
    """Professional oscilloscope-style waveform visualization."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.waveform_buffer: List[float] = []
        self.waveform_peak_hold: List[float] = []
        self.waveform_reset_timer = 0.0
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        energy = features.get('total_energy', 0)
        waveform_value = (energy - 0.5) * 2.0  # Range: -1 to 1
        self.waveform_buffer.append(waveform_value)
        
        self.waveform_reset_timer += dt
        if self.waveform_reset_timer >= WAVEFORM_RESET_INTERVAL:
            self.waveform_buffer.clear()
            self.waveform_peak_hold.clear()
            self.waveform_reset_timer = 0.0
        
        if len(self.waveform_buffer) > WAVEFORM_MAX_LENGTH:
            self.waveform_buffer.pop(0)
            if len(self.waveform_peak_hold) > 0:
                self.waveform_peak_hold.pop(0)
    
    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND_WAVEFORM)
        
        center_y = self.height // 2
        
        # Draw grid lines
        # Horizontal center line
        pygame.draw.line(screen, COLOR_CENTER_LINE, (0, center_y), (self.width, center_y), 1)
        # Horizontal grid lines
        for i in [1, 2, 3]:
            offset = self.height * 0.15 * i
            pygame.draw.line(screen, COLOR_GRID_WAVEFORM, (0, center_y - offset), 
                           (self.width, center_y - offset), 1)
            pygame.draw.line(screen, COLOR_GRID_WAVEFORM, (0, center_y + offset), 
                           (self.width, center_y + offset), 1)
        # Vertical grid lines
        for i in range(0, self.width, self.width // 10):
            pygame.draw.line(screen, COLOR_GRID_WAVEFORM, (i, 0), (i, self.height), 1)
        
        if len(self.waveform_buffer) < 2:
            return
        
        # Normalize waveform values
        max_abs_value = max(abs(v) for v in self.waveform_buffer) if self.waveform_buffer else 1.0
        scale_factor = min(0.9, 0.8 / max_abs_value) if max_abs_value > 0 else 0.8
        
        points = []
        points_top = []
        
        # Dynamic color based on frequency content
        bass = self.features.get('bass', 0)
        mid = self.features.get('mid', 0)
        treble = self.features.get('treble', 0)
        
        base_color = (
            int(50 + treble * 100),
            int(200 + bass * 55),
            int(180 + mid * 75)
        )
        
        # Draw waveform points
        for i, value in enumerate(self.waveform_buffer):
            x = (i / len(self.waveform_buffer)) * self.width
            scaled_value = value * scale_factor
            y = center_y - scaled_value * self.height * WAVEFORM_SCALE_FACTOR
            
            y = max(WAVEFORM_MARGIN, min(self.height - WAVEFORM_MARGIN, y))
            points.append((x, y))
            
            # Update peak hold
            if i < len(self.waveform_peak_hold):
                peak = self.waveform_peak_hold[i]
                scaled_peak = peak * scale_factor
                peak_y = center_y - scaled_peak * self.height * WAVEFORM_SCALE_FACTOR
                peak_y = max(WAVEFORM_MARGIN, min(self.height - WAVEFORM_MARGIN, peak_y))
                points_top.append((x, peak_y))
                
                if abs(value) > abs(peak):
                    self.waveform_peak_hold[i] = value
                else:
                    self.waveform_peak_hold[i] *= WAVEFORM_PEAK_DECAY
            else:
                self.waveform_peak_hold.append(value)
                points_top.append((x, y))
        
        if len(points) > 1:
            # Draw filled area (above and below center line)
            above_poly = []
            below_poly = []
            
            above_poly.append((points[0][0], center_y))
            below_poly.append((points[0][0], center_y))
            
            for i, (x, y) in enumerate(points):
                if y <= center_y:
                    above_poly.append((x, y))
                    if i > 0 and points[i-1][1] > center_y:
                        x1, y1 = points[i-1]
                        t = (center_y - y1) / (y - y1) if y != y1 else 0
                        x_int = x1 + t * (x - x1)
                        above_poly.insert(-1, (x_int, center_y))
                else:
                    below_poly.append((x, y))
                    if i > 0 and points[i-1][1] <= center_y:
                        x1, y1 = points[i-1]
                        t = (center_y - y1) / (y - y1) if y != y1 else 0
                        x_int = x1 + t * (x - x1)
                        below_poly.insert(-1, (x_int, center_y))
            
            above_poly.append((points[-1][0], center_y))
            below_poly.append((points[-1][0], center_y))
            
            if len(above_poly) > 2:
                pygame.draw.polygon(screen, (*base_color, 30), above_poly)
            if len(below_poly) > 2:
                pygame.draw.polygon(screen, (*base_color, 20), below_poly)
            
            # Draw main waveform line
            pygame.draw.lines(screen, base_color, False, points, 2)
            
            # Draw peak hold line (dotted)
            if len(points_top) > 1:
                peak_color = (base_color[0] // 2, base_color[1] // 2, base_color[2])
                for i in range(len(points_top) - 1):
                    if i % 3 == 0:
                        pygame.draw.line(screen, peak_color, 
                                       points_top[i], points_top[i + 1], 1)
            
            # Draw zero-crossing indicators
            for i in range(len(points) - 1):
                if (points[i][1] <= center_y < points[i + 1][1]) or \
                   (points[i][1] >= center_y > points[i + 1][1]):
                    pygame.draw.circle(screen, (base_color[0], base_color[1], 255), 
                                     (int(points[i][0]), int(center_y)), 2)
        
        # Draw info overlay
        overlay_y = OVERLAY_MARGIN
        overlay_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        overlay_surface = pygame.Surface((OVERLAY_WIDTH, OVERLAY_HEIGHT_BASIC))
        overlay_surface.set_alpha(COLOR_OVERLAY_ALPHA)
        overlay_surface.fill(COLOR_OVERLAY_BG)
        screen.blit(overlay_surface, (OVERLAY_MARGIN, overlay_y))
        
        mode_text = overlay_font.render("Waveform", True, COLOR_TEXT_PRIMARY)
        screen.blit(mode_text, (OVERLAY_MARGIN + 10, overlay_y + 5))
        
        if self.current_bpm > 0:
            bpm_text = overlay_font.render(f"BPM: {int(self.current_bpm)}", True, COLOR_TEXT_WHITE)
            screen.blit(bpm_text, (OVERLAY_MARGIN + 10, overlay_y + 32))
        
        rms = self.features.get('rms', 0)
        peak = self.features.get('peak', 0)
        info_text = overlay_font.render(f"RMS: {rms:.3f} | Peak: {peak:.3f}", True, COLOR_TEXT_SECONDARY)
        screen.blit(info_text, (OVERLAY_MARGIN + 10, overlay_y + 59))
    
    def reset(self) -> None:
        self.waveform_buffer.clear()
        self.waveform_peak_hold.clear()
        self.waveform_reset_timer = 0.0

