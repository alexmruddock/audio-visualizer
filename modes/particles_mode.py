"""
Particles visualization mode.
"""

import pygame
import math
import random
from typing import List, Tuple
from modes.base import VisualizationMode
from particles import Particle
from utils import get_color_from_features


class ParticlesMode(VisualizationMode):
    """Particle/fluid visualization mode."""
    
    def __init__(self, width: int, height: int, max_particles: int = 500):
        super().__init__(width, height)
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.trail_surface = pygame.Surface((width, height))
        self.trail_surface.set_alpha(200)
    
    def update_size(self, width: int, height: int) -> None:
        super().update_size(width, height)
        self.trail_surface = pygame.Surface((width, height))
        self.trail_surface.set_alpha(200)
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        # Spawn particles on beat
        if is_beat:
            color = get_color_from_features(features)
            spawn_count = int(10 + bpm / 10)
            self._spawn_particles(spawn_count, color)
        
        # Continuous spawning based on BPM
        if bpm > 0:
            spawn_probability = (bpm / 120.0) * 0.1
            if random.random() < spawn_probability:
                color = get_color_from_features(features)
                self._spawn_particles(random.randint(1, 5), color)
        
        # Update particles
        for particle in self.particles[:]:
            if not particle.update(dt, self.width, self.height):
                self.particles.remove(particle)
        
        # Adjust particle properties based on frequency
        bass_factor = 1 + self.features.get('bass', 0)
        treble_factor = 1 + self.features.get('treble', 0) * 0.1
        
        for particle in self.particles:
            particle.size = max(2, min(15, particle.size * bass_factor))
            particle.vx *= treble_factor
            particle.vy *= treble_factor
    
    def render(self, screen: pygame.Surface) -> None:
        # Fade trail surface
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.set_alpha(10)
        fade_surface.fill((0, 0, 0))
        self.trail_surface.blit(fade_surface, (0, 0))
        
        screen.fill((0, 0, 0))
        
        # Draw particles with trails
        for particle in self.particles:
            if len(particle.trail) > 1:
                points = [(int(x), int(y)) for x, y in particle.trail]
                if len(points) > 1:
                    pygame.draw.lines(self.trail_surface, particle.color, False, points, 2)
            
            size_key = int(particle.size)
            alpha = int(particle.life * 255)
            
            if size_key <= 8:
                pygame.draw.circle(
                    screen,
                    (*particle.color, alpha),
                    (int(particle.x), int(particle.y)),
                    size_key
                )
            else:
                particle_surf = pygame.Surface((size_key * 2, size_key * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surf,
                    (*particle.color, alpha),
                    (size_key, size_key),
                    size_key
                )
                screen.blit(particle_surf, (int(particle.x - size_key), int(particle.y - size_key)))
        
        screen.blit(self.trail_surface, (0, 0))
    
    def _spawn_particles(self, count: int, color: Tuple[int, int, int]) -> None:
        """Spawn new particles."""
        center_x = self.width // 2
        center_y = self.height // 2
        
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 100)
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            color_variation = (
                max(0, min(255, color[0] + random.randint(-30, 30))),
                max(0, min(255, color[1] + random.randint(-30, 30))),
                max(0, min(255, color[2] + random.randint(-30, 30)))
            )
            
            particle = Particle(x, y, color_variation)
            energy = self.features.get('total_energy', 0)
            particle.size = random.uniform(2, 6) * (1 + energy * 2)
            
            self.particles.append(particle)
    
    def reset(self) -> None:
        self.particles.clear()
        self.trail_surface.fill((0, 0, 0))

