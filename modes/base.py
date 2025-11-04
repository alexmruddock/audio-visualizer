"""
Base class for visualization modes.
"""

from abc import ABC, abstractmethod
from typing import Dict
import pygame


class VisualizationMode(ABC):
    """Base class for visualization modes."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize visualization mode.
        
        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        self.features: Dict = {}
        self.current_bpm = 0.0
        self.beat_triggered = False
    
    def update_size(self, width: int, height: int) -> None:
        """Update window size."""
        self.width = width
        self.height = height
    
    @abstractmethod
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        """
        Update mode state.
        
        Args:
            dt: Delta time in seconds
            bpm: Current BPM
            is_beat: Whether a beat was detected
            features: Audio features dictionary
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the visualization.
        
        Args:
            screen: Pygame surface to render to
        """
        pass
    
    def reset(self) -> None:
        """Reset mode state."""
        pass

