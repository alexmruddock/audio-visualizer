"""
Shared utilities for visualization modes.
"""

import pygame
import numpy as np
from typing import Tuple, List, Dict, Optional
from constants import (
    COLOR_GRID, COLOR_GRID_WAVEFORM, COLOR_CENTER_LINE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_WHITE, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_DIM, COLOR_OVERLAY_BG, COLOR_OVERLAY_ALPHA,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, OVERLAY_MARGIN,
    OVERLAY_WIDTH, OVERLAY_HEIGHT_BASIC, OVERLAY_HEIGHT_TALL,
    BAR_BOTTOM_FRACTION, BAR_HEIGHT_FRACTION,
    BEAT_FLASH_ALPHA, BEAT_FLASH_HEIGHT_FACTOR
)


def get_color_from_features(features: dict) -> Tuple[int, int, int]:
    """
    Generate color based on frequency features.
    
    Args:
        features: Audio features dictionary with 'bass', 'mid', 'treble'
        
    Returns:
        RGB color tuple
    """
    bass = features.get('bass', 0)
    mid = features.get('mid', 0)
    treble = features.get('treble', 0)
    
    # Mix colors based on frequency bands
    r = int(255 * bass + 150 * mid + 100 * treble)
    g = int(100 * bass + 255 * mid + 150 * treble)
    b = int(150 * bass + 100 * mid + 255 * treble)
    
    # Clamp values
    r = max(50, min(255, r))
    g = max(50, min(255, g))
    b = max(50, min(255, b))
    
    return (r, g, b)


def draw_grid(screen: pygame.Surface, width: int, height: int, 
              grid_type: str = 'standard') -> None:
    """
    Draw grid lines for professional visualization.
    
    Args:
        screen: Pygame surface to draw on
        width: Screen width
        height: Screen height
        grid_type: 'standard' or 'waveform'
    """
    if grid_type == 'waveform':
        grid_color = COLOR_GRID_WAVEFORM
        center_y = height // 2
        
        # Horizontal center line
        pygame.draw.line(screen, COLOR_CENTER_LINE, (0, center_y), (width, center_y), 1)
        
        # Horizontal grid lines
        for i in [1, 2, 3]:
            offset = height * 0.15 * i
            pygame.draw.line(screen, grid_color, (0, center_y - offset), 
                           (width, center_y - offset), 1)
            pygame.draw.line(screen, grid_color, (0, center_y + offset), 
                           (width, center_y + offset), 1)
        
        # Vertical grid lines
        for i in range(0, width, width // 10):
            pygame.draw.line(screen, grid_color, (i, 0), (i, height), 1)
    else:
        # Standard grid (for frequency bars and spectrum)
        # Horizontal grid lines
        for i in range(5):
            y_pos = int(height * BAR_BOTTOM_FRACTION - (i * height * 0.15))
            pygame.draw.line(screen, COLOR_GRID, (0, y_pos), (width, y_pos), 1)


def draw_info_overlay(screen: pygame.Surface, width: int, height: int,
                      mode_name: str, bpm: float, info_texts: Optional[List[str]] = None,
                      height_type: str = 'basic') -> None:
    """
    Draw info overlay panel.
    
    Args:
        screen: Pygame surface to draw on
        width: Screen width
        height: Screen height
        mode_name: Name of the mode
        bpm: Current BPM
        info_texts: Optional list of additional info strings
        height_type: 'basic' or 'tall'
    """
    overlay_y = OVERLAY_MARGIN
    info_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
    
    overlay_height = OVERLAY_HEIGHT_BASIC if height_type == 'basic' else OVERLAY_HEIGHT_TALL
    overlay_surface = pygame.Surface((OVERLAY_WIDTH, overlay_height))
    overlay_surface.set_alpha(COLOR_OVERLAY_ALPHA)
    overlay_surface.fill(COLOR_OVERLAY_BG)
    screen.blit(overlay_surface, (OVERLAY_MARGIN, overlay_y))
    
    # Mode text
    display_name = mode_name.replace('_', ' ').title()
    mode_text = info_font.render(display_name, True, COLOR_TEXT_PRIMARY)
    screen.blit(mode_text, (OVERLAY_MARGIN + 10, overlay_y + 5))
    
    # BPM
    if bpm > 0:
        bpm_text = info_font.render(f"BPM: {int(bpm)}", True, COLOR_TEXT_WHITE)
        screen.blit(bpm_text, (OVERLAY_MARGIN + 10, overlay_y + 32))
    
    # Additional info texts
    if info_texts:
        for i, text in enumerate(info_texts):
            text_surface = info_font.render(text, True, COLOR_TEXT_SECONDARY)
            screen.blit(text_surface, (OVERLAY_MARGIN + 10, overlay_y + 59 + i * 22))


def draw_gradient_bar(screen: pygame.Surface, x: int, y: int, width: int, height: int,
                      base_color: Tuple[int, int, int], highlight: bool = True) -> None:
    """
    Draw a gradient-filled bar.
    
    Args:
        screen: Pygame surface to draw on
        x: X position
        y: Y position (top of bar)
        width: Bar width
        height: Bar height
        base_color: Base RGB color
        highlight: Whether to add highlight on top
    """
    if height <= 0:
        return
    
    # Draw gradient fill
    for y_offset in range(height):
        gradient_factor = y_offset / max(1, height)
        grad_color = (
            int(base_color[0] * (0.3 + 0.7 * gradient_factor)),
            int(base_color[1] * (0.3 + 0.7 * gradient_factor)),
            int(base_color[2] * (0.3 + 0.7 * gradient_factor))
        )
        pygame.draw.line(screen, grad_color,
                       (x, y + height - y_offset),
                       (x + width - 1, y + height - y_offset),
                       1)
    
    # Add highlight on top
    if highlight:
        highlight_color = (
            min(255, base_color[0] + 50),
            min(255, base_color[1] + 50),
            min(255, base_color[2] + 50)
        )
        pygame.draw.line(screen, highlight_color,
                       (x, y),
                       (x + width - 1, y),
                       2)


def draw_beat_flash(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """
    Draw beat flash effect.
    
    Args:
        screen: Pygame surface to draw on
        x: X position
        y: Y position (top of flash)
        width: Flash width
        height: Flash height
    """
    flash_height = int(height * BEAT_FLASH_HEIGHT_FACTOR)
    flash_surface = pygame.Surface((width, flash_height))
    flash_surface.set_alpha(BEAT_FLASH_ALPHA)
    flash_surface.fill(COLOR_TEXT_WHITE)
    screen.blit(flash_surface, (x, y - flash_height + height))


def get_spectrum_color(freq_hue: float) -> Tuple[int, int, int]:
    """
    Get color for spectrum analyzer based on frequency hue.
    
    Args:
        freq_hue: Frequency position (0.0 to 1.0)
        
    Returns:
        RGB color tuple
    """
    freq_hue = max(0.0, min(1.0, freq_hue))
    
    if freq_hue < 0.2:
        # Sub-bass: Deep red/purple
        r, g, b = int(180 + freq_hue * 75), 0, int(150 + freq_hue * 105)
    elif freq_hue < 0.4:
        # Bass: Red to orange
        t = (freq_hue - 0.2) / 0.2
        r, g, b = 255, int(t * 100), 0
    elif freq_hue < 0.55:
        # Low-mid: Yellow
        t = (freq_hue - 0.4) / 0.15
        r, g, b = 255, 255, int(t * 255)
    elif freq_hue < 0.7:
        # Mid: Green to cyan
        t = (freq_hue - 0.55) / 0.15
        r, g, b = int(255 * (1 - t)), 255, int(255 * t)
    elif freq_hue < 0.85:
        # High-mid: Cyan to blue
        t = (freq_hue - 0.7) / 0.15
        r, g, b = 0, int(255 * (1 - t)), 255
    else:
        # Treble: Blue to purple
        t = (freq_hue - 0.85) / 0.15
        r, g, b = int(255 * t), 0, 255
    
    return (r, g, b)
