"""
Fractal visualization mode.
"""

import pygame
from modes.base import VisualizationMode
from utils import get_color_from_features
from constants import (
    COLOR_BACKGROUND_BLACK, FRACTAL_JULIA_C_DEFAULT,
    FRACTAL_ITERATIONS_DEFAULT, FRACTAL_ITERATIONS_MIN,
    FRACTAL_ITERATIONS_MAX, FRACTAL_ZOOM
)


class FractalMode(VisualizationMode):
    """Julia set fractal visualization."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.fractal_julia_c = FRACTAL_JULIA_C_DEFAULT
        self.fractal_iterations = FRACTAL_ITERATIONS_DEFAULT
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        bass = features.get('bass', 0)
        treble = features.get('treble', 0)
        real_part = -0.7 + bass * 0.6
        imag_part = 0.27015 + (treble - 0.5) * 0.4
        self.fractal_julia_c = complex(real_part, imag_part)
        
        if is_beat:
            self.fractal_iterations = min(FRACTAL_ITERATIONS_MAX, self.fractal_iterations + 5)
        else:
            self.fractal_iterations = max(FRACTAL_ITERATIONS_MIN, self.fractal_iterations - 0.1)
    
    def render(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND_BLACK)
        
        c = self.fractal_julia_c
        max_iter = int(self.fractal_iterations)
        
        # Viewport bounds
        zoom = FRACTAL_ZOOM
        x_min, x_max = -zoom, zoom
        y_min, y_max = -zoom, zoom
        
        base_color = get_color_from_features(self.features)
        
        # Adaptive step size for performance
        step = max(1, min(3, self.width // 640))
        
        for py in range(0, self.height, step):
            for px in range(0, self.width, step):
                # Map pixel to complex plane
                x = x_min + (px / self.width) * (x_max - x_min)
                y = y_min + (py / self.height) * (y_max - y_min)
                
                z = complex(x, y)
                
                # Julia set iteration
                n = 0
                while abs(z) < 2 and n < max_iter:
                    z = z * z + c
                    n += 1
                
                # Color based on iteration count
                if n < max_iter:
                    t = n / max_iter
                    r = int(base_color[0] * t + 255 * (1 - t))
                    g = int(base_color[1] * t + 255 * (1 - t))
                    b = int(base_color[2] * t + 255 * (1 - t))
                    color = (r, g, b)
                else:
                    color = (20, 20, 20)
                
                # Draw pixel
                if step == 1:
                    screen.set_at((px, py), color)
                else:
                    pygame.draw.rect(screen, color, (px, py, step, step))
    
    def reset(self) -> None:
        self.fractal_julia_c = FRACTAL_JULIA_C_DEFAULT
        self.fractal_iterations = FRACTAL_ITERATIONS_DEFAULT

