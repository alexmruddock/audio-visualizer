"""
Particle class for particle system.
"""

import random
from typing import List, Tuple


class Particle:
    """Individual particle in the particle system."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        """
        Initialize a particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.size = random.uniform(2, 6)
        self.life = 1.0
        self.decay = random.uniform(0.005, 0.015)
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_length = 10
        
    def update(self, dt: float, width: int, height: int, gravity: float = 0.1) -> bool:
        """
        Update particle physics.
        
        Args:
            dt: Delta time
            width: Screen width
            height: Screen height
            gravity: Gravity strength
            
        Returns:
            True if particle is still alive
        """
        # Update velocity (gravity)
        self.vy += gravity
        
        # Update position
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Boundary bounce
        if self.x < 0 or self.x > width:
            self.vx *= -0.8
            self.x = max(0, min(width, self.x))
        if self.y < 0 or self.y > height:
            self.vy *= -0.8
            self.y = max(0, min(height, self.y))
        
        # Update life
        self.life -= self.decay
        return self.life > 0
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get current color with alpha based on life."""
        alpha = int(self.life * 255)
        return (*self.color, alpha)

