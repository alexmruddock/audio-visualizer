"""
Circles visualization mode - Enhanced with advanced audio-reactive effects.
Optimized for performance.
"""

import pygame
import math
import random
from typing import List, Tuple, Dict, Optional
from modes.base import VisualizationMode
from utils import get_color_from_features, get_spectrum_color

# Performance constants
MAX_CIRCLES = 50  # Maximum circles to prevent accumulation
MAX_TRAIL_LENGTH = 8  # Reduced trail length
GRADIENT_STEPS = 3  # Reduced gradient steps (was radius/2)
ENABLE_TRAILS = True  # Can disable for extra performance
ENABLE_GLOW = True  # Can disable for extra performance
SIMPLIFIED_RENDERING_THRESHOLD = 10  # Use simple rendering for small circles


class Circle:
    """Individual circle with advanced properties."""

    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int],
                 angle: float = 0.0, orbit_radius: float = 0.0, orbit_speed: float = 0.0):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.radius = radius
        self.color = color
        self.angle = angle
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.rotation_angle = 0.0
        self.rotation_speed = random.uniform(-0.02, 0.02)
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.1, 0.3)
        self.life = 1.0
        self.fade_speed = random.uniform(0.005, 0.02)
        self.glow_intensity = 0.0
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_length = min(MAX_TRAIL_LENGTH, random.randint(3, 8))
        self.cached_color: Optional[Tuple[int, int, int]] = None
        self.color_cache_frame = -1

    def update(self, dt: float, center_x: float, center_y: float, features: dict,
               is_beat: bool, bpm: float) -> bool:
        """Update circle state. Returns False if circle should be removed."""

        # Update orbit
        if self.orbit_radius > 0:
            self.angle += self.orbit_speed * dt * 60  # Scale with dt
            self.x = center_x + math.cos(self.angle) * self.orbit_radius
            self.y = center_y + math.sin(self.angle) * self.orbit_radius

        # Update rotation
        self.rotation_angle += self.rotation_speed * dt * 60

        # Update pulse
        self.pulse_phase += self.pulse_speed * dt * 60
        pulse_factor = 1.0 + 0.3 * math.sin(self.pulse_phase)

        # Audio-reactive sizing
        bass_boost = 1.0 + features.get('bass', 0) * 2.0
        treble_shake = 1.0 + features.get('treble', 0) * 0.5 * math.sin(self.pulse_phase * 3)

        self.radius = self.base_radius * pulse_factor * bass_boost * treble_shake

        # Beat reaction
        if is_beat:
            self.glow_intensity = min(1.0, self.glow_intensity + 0.5)
            self.radius *= 1.2

        # Update glow
        self.glow_intensity *= 0.95

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Update life
        self.life -= self.fade_speed
        return self.life > 0

    def render(self, screen: pygame.Surface, features: dict, frame_counter: int) -> None:
        """Render the circle with advanced effects."""
        if self.life <= 0:
            return

        # Check if circle is off-screen (quick cull)
        if (self.x + self.radius < 0 or self.x - self.radius > screen.get_width() or
            self.y + self.radius < 0 or self.y - self.radius > screen.get_height()):
            return

        # Cache color calculation (update every few frames)
        if self.cached_color is None or frame_counter != self.color_cache_frame:
            base_color = self.color
            spectral_centroid = features.get('spectral_centroid', 0) / 10000  # Normalize
            dynamic_color = get_spectrum_color(spectral_centroid)

            # Blend colors based on energy
            energy = features.get('bass', 0) + features.get('mid', 0) + features.get('treble', 0)
            blend_factor = min(1.0, energy * 2.0)
            r = int(base_color[0] * (1 - blend_factor) + dynamic_color[0] * blend_factor)
            g = int(base_color[1] * (1 - blend_factor) + dynamic_color[1] * blend_factor)
            b = int(base_color[2] * (1 - blend_factor) + dynamic_color[2] * blend_factor)
            # Clamp color values to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            self.cached_color = (r, g, b)
            self.color_cache_frame = frame_counter

        color = self.cached_color
        alpha = int(255 * self.life)

        # Use simplified rendering for small circles
        if self.radius < SIMPLIFIED_RENDERING_THRESHOLD:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.radius))
            return

        # Draw trail (simplified, only for larger circles)
        if ENABLE_TRAILS and len(self.trail) > 1 and self.radius >= 8:
            # Only draw every other trail point for performance
            for i in range(1, len(self.trail), 2):
                if i < len(self.trail):
                    prev_x, prev_y = self.trail[i-1]
                    curr_x, curr_y = self.trail[i]
                    # Simplified trail - just use darker color
                    trail_color = (min(255, color[0] // 3), min(255, color[1] // 3), min(255, color[2] // 3))
                    pygame.draw.line(screen, trail_color, (prev_x, prev_y), (curr_x, curr_y), 1)

        # Draw glow effect (simplified - uses surface for alpha)
        if ENABLE_GLOW and self.glow_intensity > 0.15:
            glow_radius = int(self.radius * (1.0 + self.glow_intensity * 0.5))
            glow_alpha = int(alpha * self.glow_intensity * 0.3)
            glow_alpha = max(0, min(255, glow_alpha))  # Clamp alpha to valid range
            if glow_alpha > 10:  # Only create surface if meaningful
                glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
                # Use RGBA color tuple for SRCALPHA surface
                glow_color = (*color, glow_alpha)
                pygame.draw.circle(glow_surf, glow_color,
                                 (glow_radius + 2, glow_radius + 2), glow_radius)
                screen.blit(glow_surf, (int(self.x - glow_radius - 2), int(self.y - glow_radius - 2)))

        # Draw main circle with gradient
        self._draw_gradient_circle(screen, self.x, self.y, self.radius, color, alpha)

        # Draw rotating elements for orbiting circles (only for larger circles)
        if self.orbit_radius > 0 and self.radius >= 10:
            # Reduced marker count for performance
            marker_count = 6  # Reduced from 8
            for i in range(marker_count):
                marker_angle = self.rotation_angle + (i * 2 * math.pi / marker_count)
                marker_x = self.x + math.cos(marker_angle) * (self.radius * 0.8)
                marker_y = self.y + math.sin(marker_angle) * (self.radius * 0.8)
                # Use darker color for markers instead of alpha
                marker_color = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.circle(screen, marker_color, (int(marker_x), int(marker_y)), 2)

    def _draw_gradient_circle(self, screen: pygame.Surface, x: float, y: float,
                            radius: float, color: Tuple[int, int, int], alpha: int) -> None:
        """Draw a circle with simplified radial gradient."""
        if radius < 1:
            return

        radius_int = int(radius)
        x_int = int(x)
        y_int = int(y)

        # For small circles, use simple filled circle
        if radius_int < SIMPLIFIED_RENDERING_THRESHOLD:
            pygame.draw.circle(screen, color, (x_int, y_int), radius_int)
            return

        # Simplified gradient: fewer steps, use direct drawing
        # Draw outer circle with full color
        pygame.draw.circle(screen, color, (x_int, y_int), radius_int)
        
        # Draw inner gradient circles (reduced steps) - use darker colors instead of alpha
        step = max(2, radius_int // GRADIENT_STEPS)
        for r in range(radius_int - step, 0, -step):
            gradient_factor = r / radius_int
            # Create darker shade instead of using alpha
            grad_r = int(color[0] * (0.4 + 0.6 * gradient_factor))
            grad_g = int(color[1] * (0.4 + 0.6 * gradient_factor))
            grad_b = int(color[2] * (0.4 + 0.6 * gradient_factor))
            grad_color = (grad_r, grad_g, grad_b)
            pygame.draw.circle(screen, grad_color, (x_int, y_int), r)

        # Add outline
        outline_color = (color[0] // 2, color[1] // 2, color[2] // 2)
        pygame.draw.circle(screen, outline_color, (x_int, y_int), radius_int, 1)


class CirclesMode(VisualizationMode):
    """Enhanced pulsing circles visualization mode with advanced effects."""

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.circles: List[Circle] = []
        self.center_x = width // 2
        self.center_y = height // 2
        self.time = 0.0
        self.pattern_phase = 0.0
        self.beat_counter = 0
        self.frame_counter = 0
        self.bg_surface: Optional[pygame.Surface] = None  # Cached background

        # Initialize with some base circles
        self._initialize_base_circles()

    def _initialize_base_circles(self) -> None:
        """Initialize the base circle pattern."""
        self.circles.clear()

        # Central pulsing circles
        for i in range(3):
            radius = 30 + i * 25
            color = (100 + i * 50, 150, 200 + i * 30)
            circle = Circle(self.center_x, self.center_y, radius, color)
            circle.rotation_speed = 0.01 * (i + 1)
            self.circles.append(circle)

        # Orbiting circles
        for i in range(6):
            angle = (i * 2 * math.pi) / 6
            orbit_radius = 80 + i * 15
            x = self.center_x + math.cos(angle) * orbit_radius
            y = self.center_y + math.sin(angle) * orbit_radius
            radius = 15 + i * 3
            color = (200, 100 + i * 20, 150)
            circle = Circle(x, y, radius, color, angle, orbit_radius, 0.02)
            self.circles.append(circle)

    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        self.time += dt

        # Update pattern phase
        self.pattern_phase += dt * 0.5

        # Limit circle count
        if len(self.circles) > MAX_CIRCLES:
            # Remove oldest circles (those with lowest life)
            self.circles.sort(key=lambda c: c.life)
            self.circles = self.circles[-MAX_CIRCLES:]

        # Handle beat
        if is_beat:
            self.beat_counter += 1
            self._trigger_beat_effects(features)

        # Update all circles
        self.circles = [c for c in self.circles if c.update(dt, self.center_x, self.center_y,
                                                          features, is_beat, bpm)]

        # Continuous spawning based on energy (throttled to prevent accumulation)
        if len(self.circles) < MAX_CIRCLES * 0.8:  # Only spawn if below 80% capacity
            energy = features.get('bass', 0) + features.get('mid', 0) + features.get('treble', 0)
            if energy > 0.3 and random.random() < energy * 0.05:  # Reduced spawn rate
                self._spawn_energy_circle(features)

        # Dynamic pattern morphing
        if bpm > 0:
            morph_speed = bpm / 120.0
            self._update_circle_patterns(dt * morph_speed, features)

    def _trigger_beat_effects(self, features: dict) -> None:
        """Trigger special effects on beat."""
        # Limit burst circles based on current count
        available_slots = MAX_CIRCLES - len(self.circles)
        if available_slots < 3:
            return  # Skip if too many circles

        color = get_color_from_features(features)

        # Spawn burst circles (reduced count)
        burst_count = min(random.randint(4, 8), available_slots - 1)  # Reduced from 8-16
        for i in range(burst_count):
            angle = (i * 2 * math.pi) / burst_count + random.uniform(-0.2, 0.2)
            distance = random.uniform(50, 150)
            x = self.center_x + math.cos(angle) * distance
            y = self.center_y + math.sin(angle) * distance
            radius = random.uniform(5, 20)
            speed = random.uniform(0.05, 0.15)

            # Create orbiting burst circle
            circle = Circle(x, y, radius, color, angle, distance, speed)
            circle.fade_speed = 0.02
            self.circles.append(circle)

        # Add central flash (only if we have room)
        if available_slots > burst_count:
            flash_circle = Circle(self.center_x, self.center_y, 150, (255, 255, 255))  # Smaller
            flash_circle.fade_speed = 0.15  # Faster fade
            flash_circle.pulse_speed = 2.0
            self.circles.append(flash_circle)

    def _spawn_energy_circle(self, features: dict) -> None:
        """Spawn circles based on audio energy."""
        color = get_color_from_features(features)

        # Random position near center
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(20, self.center_x * 0.8)
        x = self.center_x + math.cos(angle) * distance
        y = self.center_y + math.sin(angle) * distance
        radius = random.uniform(8, 25)

        circle = Circle(x, y, radius, color)
        circle.orbit_radius = distance * 0.5
        circle.orbit_speed = random.choice([-0.03, 0.03])
        circle.fade_speed = 0.01
        self.circles.append(circle)

    def _update_circle_patterns(self, dt: float, features: dict) -> None:
        """Update circle patterns based on audio features."""
        spectral_flux = features.get('spectral_flux', 0)
        spectral_centroid = features.get('spectral_centroid', 0)
        bass = features.get('bass', 0)
        mid = features.get('mid', 0)
        treble = features.get('treble', 0)

        # Morph orbiting circles based on spectral flux
        for circle in self.circles:
            if circle.orbit_radius > 0:
                flux_factor = 1.0 + spectral_flux * 0.1
                circle.orbit_speed *= flux_factor
                circle.orbit_speed = max(-0.2, min(0.2, circle.orbit_speed))

        # Adjust rotation speeds based on BPM
        bpm_factor = self.current_bpm / 120.0 if self.current_bpm > 0 else 1.0
        for circle in self.circles:
            circle.rotation_speed = circle.rotation_speed * 0.95 + (circle.rotation_speed * bpm_factor) * 0.05

        # Dynamic pattern morphing based on frequency balance
        total_energy = bass + mid + treble
        if total_energy > 0.1:
            bass_ratio = bass / total_energy
            mid_ratio = mid / total_energy
            treble_ratio = treble / total_energy

            # Morph patterns based on frequency dominance
            if bass_ratio > 0.6:  # Bass heavy - compact central pattern
                self._morph_to_compact_pattern(dt * 2.0)
            elif treble_ratio > 0.5:  # Treble heavy - expansive orbiting pattern
                self._morph_to_expansive_pattern(dt * 1.5)
            elif mid_ratio > 0.5:  # Mid heavy - balanced geometric pattern
                self._morph_to_geometric_pattern(dt * 1.0)
            else:  # Balanced - flowing pattern
                self._morph_to_flowing_pattern(dt * 0.8)

        # Spectral centroid affects circle sizes and speeds
        centroid_factor = min(1.0, spectral_centroid / 8000.0) if spectral_centroid > 0 else 0.5
        for circle in self.circles:
            # Higher centroid = smaller, faster circles
            size_factor = 1.0 - centroid_factor * 0.3
            circle.base_radius = circle.base_radius * 0.98 + (circle.base_radius * size_factor) * 0.02
            circle.orbit_speed *= (1.0 + centroid_factor * 0.1)

    def _morph_to_compact_pattern(self, morph_speed: float) -> None:
        """Morph circles into a compact central formation."""
        base_circles = [c for c in self.circles if c.orbit_radius == 0][:3]  # Central circles
        orbiting_circles = [c for c in self.circles if c.orbit_radius > 0]

        # Tighten orbiting circles
        target_orbit_radius = 60
        for circle in orbiting_circles:
            circle.orbit_radius = circle.orbit_radius * (1 - morph_speed) + target_orbit_radius * morph_speed

        # Increase central circle sizes
        for i, circle in enumerate(base_circles):
            target_radius = 40 + i * 30
            circle.base_radius = circle.base_radius * (1 - morph_speed) + target_radius * morph_speed

    def _morph_to_expansive_pattern(self, morph_speed: float) -> None:
        """Morph circles into an expansive orbiting formation."""
        orbiting_circles = [c for c in self.circles if c.orbit_radius > 0]

        # Expand orbiting circles
        for i, circle in enumerate(orbiting_circles):
            target_orbit_radius = 120 + i * 20
            circle.orbit_radius = circle.orbit_radius * (1 - morph_speed) + target_orbit_radius * morph_speed
            circle.orbit_speed = circle.orbit_speed * (1 - morph_speed) + 0.05 * morph_speed

        # Reduce central circle sizes
        base_circles = [c for c in self.circles if c.orbit_radius == 0][:3]
        for circle in base_circles:
            target_radius = 15
            circle.base_radius = circle.base_radius * (1 - morph_speed) + target_radius * morph_speed

    def _morph_to_geometric_pattern(self, morph_speed: float) -> None:
        """Morph circles into a geometric formation."""
        orbiting_circles = [c for c in self.circles if c.orbit_radius > 0]

        # Create geometric orbit pattern (equilateral triangle + square)
        geometric_positions = [
            (0, 90),    # Top
            (90, 90),   # Right
            (180, 90),  # Bottom
            (270, 90),  # Left
            (45, 120),  # Top-right
            (135, 120), # Bottom-right
        ]

        for i, circle in enumerate(orbiting_circles):
            if i < len(geometric_positions):
                target_angle, target_radius = geometric_positions[i]
                # Smooth angle transition
                angle_diff = (target_angle * math.pi / 180) - circle.angle
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                elif angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                circle.angle += angle_diff * morph_speed

                circle.orbit_radius = circle.orbit_radius * (1 - morph_speed) + target_radius * morph_speed

    def _morph_to_flowing_pattern(self, morph_speed: float) -> None:
        """Morph circles into a flowing, organic formation."""
        orbiting_circles = [c for c in self.circles if c.orbit_radius > 0]

        # Create flowing wave pattern
        time_offset = self.time * 2
        for i, circle in enumerate(orbiting_circles):
            # Wave-based positioning
            wave_angle = circle.angle + time_offset + i * math.pi / 3
            target_radius = 80 + 30 * math.sin(wave_angle)
            circle.orbit_radius = circle.orbit_radius * (1 - morph_speed) + target_radius * morph_speed

            # Vary speeds for organic feel
            target_speed = 0.02 + 0.01 * math.sin(wave_angle * 2)
            circle.orbit_speed = circle.orbit_speed * (1 - morph_speed) + target_speed * morph_speed

    def render(self, screen: pygame.Surface) -> None:
        # Clear with cached or simple background
        self._draw_gradient_background(screen)

        # Increment frame counter for color caching
        self.frame_counter += 1

        # Only sort when needed (not every frame)
        if len(self.circles) > 10:
            # Sort circles by size for proper layering (smaller on top)
            sorted_circles = sorted(self.circles, key=lambda c: c.radius)
        else:
            sorted_circles = self.circles  # Skip sort for small counts

        # Render all circles
        for circle in sorted_circles:
            circle.render(screen, self.features, self.frame_counter)

        # Add spectral visualization overlay (simplified)
        self._draw_spectral_overlay(screen)

    def _draw_gradient_background(self, screen: pygame.Surface) -> None:
        """Draw a subtle gradient background (optimized)."""
        # Use cached background surface if available
        if self.bg_surface is None or self.bg_surface.get_size() != (self.width, self.height):
            # Create cached background surface
            self.bg_surface = pygame.Surface((self.width, self.height))
            # Draw gradient less frequently (every 8 pixels for performance)
            for y in range(0, self.height, 4):
                factor = y / self.height
                r = int(10 * (1 - factor))
                g = int(5 * (1 - factor))
                b = int(20 * factor)
                color = (r, g, b)
                # Fill multiple lines at once
                pygame.draw.rect(self.bg_surface, color, (0, y, self.width, 4))
        
        # Blit cached background
        screen.blit(self.bg_surface, (0, 0))

    def _draw_spectral_overlay(self, screen: pygame.Surface) -> None:
        """Draw spectral information overlay."""
        features = self.features

        # Draw frequency-based arcs
        bass = features.get('bass', 0)
        mid = features.get('mid', 0)
        treble = features.get('treble', 0)

        center_x, center_y = self.center_x, self.center_y
        max_radius = min(self.width, self.height) * 0.4

        # Bass arc (bottom)
        if bass > 0.1:
            bass_radius = max_radius * bass
            bass_color = (255, 100, 100, 100)
            bass_rect = pygame.Rect(center_x - bass_radius, center_y - bass_radius,
                                  bass_radius * 2, bass_radius * 2)
            pygame.draw.arc(screen, bass_color[:3], bass_rect, math.pi * 0.8, math.pi * 2.2, 3)

        # Mid arc (sides)
        if mid > 0.1:
            mid_radius = max_radius * mid * 0.8
            mid_color = (100, 255, 100, 100)
            mid_rect = pygame.Rect(center_x - mid_radius, center_y - mid_radius,
                                 mid_radius * 2, mid_radius * 2)
            pygame.draw.arc(screen, mid_color[:3], mid_rect, math.pi * 0.3, math.pi * 2.7, 3)

        # Treble arc (top)
        if treble > 0.1:
            treble_radius = max_radius * treble * 0.6
            treble_color = (100, 100, 255, 100)
            treble_rect = pygame.Rect(center_x - treble_radius, center_y - treble_radius,
                                    treble_radius * 2, treble_radius * 2)
            pygame.draw.arc(screen, treble_color[:3], treble_rect, math.pi * 1.8, math.pi * 0.2, 3)

    def update_size(self, width: int, height: int) -> None:
        """Update window size and reposition circles."""
        super().update_size(width, height)
        self.center_x = width // 2
        self.center_y = height // 2

        # Invalidate background cache
        self.bg_surface = None

        # Reinitialize base circles for new size
        self._initialize_base_circles()

    def reset(self) -> None:
        """Reset mode state."""
        self.circles.clear()
        self.time = 0.0
        self.pattern_phase = 0.0
        self.beat_counter = 0
        self._initialize_base_circles()

