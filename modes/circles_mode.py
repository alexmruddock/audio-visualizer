"""
Circles visualization mode.
"""

import pygame
from modes.base import VisualizationMode
from utils import get_color_from_features


class CirclesMode(VisualizationMode):
    """Pulsing circles visualization mode."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.circle_radius = 0.0
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        # Pulse circle on beat
        if is_beat:
            self.circle_radius = min(self.width, self.height) * 0.1
        
        # Decay radius
        self.circle_radius *= 0.95
    
    def render(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        color = get_color_from_features(self.features)
        
        # Draw multiple concentric circles
        for i in range(5):
            radius = self.circle_radius * (i + 1)
            if radius > 0:
                alpha = int(255 / (i + 1))
                circle_color = (*color[:3], alpha)
                
                circle_surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, circle_color, 
                                  (int(radius), int(radius)), int(radius), 2)
                screen.blit(circle_surf, 
                            (int(center_x - radius), int(center_y - radius)))
    
    def reset(self) -> None:
        self.circle_radius = 0.0

