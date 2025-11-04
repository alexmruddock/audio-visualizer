"""
Matrix visualization mode.
"""

import pygame
import random
from typing import List, Tuple
from modes.base import VisualizationMode
from utils import get_color_from_features


class MatrixMode(VisualizationMode):
    """Matrix/rain style visualization mode."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.matrix_chars: List[Tuple[int, int, str, float]] = []  # x, y, char, life
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        if is_beat or random.random() < features.get('total_energy', 0) * 0.1:
            for _ in range(int(features.get('total_energy', 0) * 5)):
                x = random.randint(0, self.width - 20)
                y = random.randint(0, self.height - 20)
                char = random.choice('0123456789ABCDEF')
                life = 1.0
                self.matrix_chars.append((x, y, char, life))
        
        # Update character lives
        for i, char_data in enumerate(self.matrix_chars[:]):
            x, y, char, life = char_data
            new_life = life - 0.01 * dt * 60
            if new_life <= 0:
                self.matrix_chars.remove(char_data)
            else:
                self.matrix_chars[i] = (x, y, char, new_life)
    
    def render(self, screen: pygame.Surface) -> None:
        # Fade characters
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.set_alpha(10)
        fade_surface.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))
        
        # Draw matrix characters
        font = pygame.font.Font(None, 20)
        
        for char_data in self.matrix_chars[:]:
            x, y, char, life = char_data
            if life <= 0:
                continue
            
            intensity = min(255, life * 255)
            color = (0, int(intensity), 0)
            
            freq_color = get_color_from_features(self.features)
            blend_color = (
                int(color[0] * 0.3 + freq_color[0] * 0.7),
                int(color[1] * 0.3 + freq_color[1] * 0.7),
                int(color[2] * 0.3 + freq_color[2] * 0.7)
            )
            
            text_surface = font.render(char, True, blend_color)
            screen.blit(text_surface, (x, y))
    
    def reset(self) -> None:
        self.matrix_chars.clear()

