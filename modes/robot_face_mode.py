"""
Robot face visualization mode.
"""

import pygame
from modes.base import VisualizationMode
from constants import COLOR_BACKGROUND_BLACK, STROBE_DECAY, STROBE_THRESHOLD


class RobotFaceMode(VisualizationMode):
    """Robot face with strobe effects visualization."""

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.strobe_intensity = 0.0
        self.last_beat_time = 0.0
        self.beat_cooldown = 0.5  # Minimum 0.5 seconds between beats
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat

        # Apply extremely fast decay to make flashes virtually instant
        self.strobe_intensity *= 0.1

        # Update beat cooldown timer
        self.last_beat_time += dt  

        # Trigger strobe on beat detection with cooldown
        if is_beat and self.last_beat_time >= self.beat_cooldown:
            self.strobe_intensity = 1.0
            self.last_beat_time = 0.0  # Reset cooldown timer
            # print(f"BEAT TRIGGERED: strobe_intensity = {self.strobe_intensity}")  # Debug

        # Trigger strobe based on bass intensity (similar to pupil size logic)
        # Temporarily disabled to isolate beat detection
        # bass = features.get('bass', 0.0)
        # print(f"Current bass: {bass:.3f}")  # Debug: see bass values
        # bass_multiplier = 1 + bass * 0.5  # Same multiplier as pupil size
        # if bass_multiplier > 2.5:  # Very high threshold (bass > 3.0) - extremely rare
        #     # Set strobe intensity proportional to bass strength
        #     strobe_from_bass = min(bass * 0.8, 1.0)  # Scale bass to 0-1 range
        #     self.strobe_intensity = max(self.strobe_intensity, strobe_from_bass)
        #     print(f"BASS TRIGGER: bass={bass:.2f}, multiplier={bass_multiplier:.2f}")
        #     print(f"BASS PEAK: bass={bass:.2f}, strobe_intensity = {self.strobe_intensity}")  # Debug
    
    def render(self, screen: pygame.Surface) -> None:
        # Fill background
        screen.fill(COLOR_BACKGROUND_BLACK)
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Scale face based on window size
        face_size = min(self.width, self.height) * 0.6
        
        # Draw robot head
        head_width = int(face_size * 0.8)
        head_height = int(face_size * 1.0)
        head_rect = pygame.Rect(
            center_x - head_width // 2,
            center_y - head_height // 2,
            head_width,
            head_height
        )
        
        head_color = (40, 40, 40) if self.strobe_intensity < 0.3 else (60, 60, 60)
        pygame.draw.rect(screen, head_color, head_rect, border_radius=20)
        
        # Draw eyes
        eye_size = int(face_size * 0.15)
        eye_spacing = int(face_size * 0.25)
        left_eye_x = center_x - eye_spacing - eye_size // 2
        right_eye_x = center_x + eye_spacing - eye_size // 2
        eye_y = center_y - int(face_size * 0.15)
        
        bass = self.features.get('bass', 0.0)
        mid = self.features.get('mid', 0.0)
        treble = self.features.get('treble', 0.0)
        
        eye_brightness = min(255, int(100 + bass * 155 + self.strobe_intensity * 155))
        eye_color = (eye_brightness, eye_brightness, eye_brightness)
        
        pygame.draw.circle(screen, eye_color, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(screen, eye_color, (right_eye_x, eye_y), eye_size)
        
        # Eye pupils
        pupil_size = int(eye_size * 0.4 * (1 + bass * 0.5))
        pupil_color = (20, 20, 20)
        pygame.draw.circle(screen, pupil_color, (left_eye_x, eye_y), pupil_size)
        pygame.draw.circle(screen, pupil_color, (right_eye_x, eye_y), pupil_size)
        
        # Draw mouth
        mouth_y = center_y + int(face_size * 0.2)
        mouth_width = int(face_size * 0.4)
        mouth_height = int(face_size * 0.08)
        num_bars = 5
        
        mouth_brightness = min(255, int(50 + mid * 205))
        mouth_color = (mouth_brightness, mouth_brightness, mouth_brightness)
        
        for i in range(num_bars):
            bar_width = mouth_width // num_bars
            bar_x = center_x - mouth_width // 2 + i * bar_width
            bar_height = int(mouth_height * (0.3 + mid * 0.7))
            bar_rect = pygame.Rect(bar_x, mouth_y, bar_width - 2, bar_height)
            pygame.draw.rect(screen, mouth_color, bar_rect)
        
        # Draw antenna/scanner
        antenna_y = center_y - head_height // 2
        antenna_width = int(face_size * 0.1)
        antenna_height = int(face_size * 0.15)
        antenna_rect = pygame.Rect(
            center_x - antenna_width // 2,
            antenna_y - antenna_height,
            antenna_width,
            antenna_height
        )
        antenna_color = (80, 80, 80) if self.strobe_intensity < 0.3 else (120, 120, 120)
        pygame.draw.rect(screen, antenna_color, antenna_rect)
        
        # Scanner light
        scanner_light_size = int(antenna_width * 0.6 * (1 + treble * 0.5))
        scanner_color = (200, 200, 255)
        pygame.draw.circle(screen, scanner_color, 
                          (center_x, antenna_y - antenna_height // 2), scanner_light_size)
        
        # Strobe flash on beats and high bass peaks
        # print(f"strobe_intensity: {self.strobe_intensity:.3f}")  # Debug
        # Uncomment to see strobe intensity values:
        # print(f"strobe_intensity: {self.strobe_intensity:.6f}")
        if self.strobe_intensity > STROBE_THRESHOLD:
            strobe_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            strobe_alpha = int(min(self.strobe_intensity, 0.8) * 255)
            pygame.draw.rect(strobe_surface, (255, 255, 255, strobe_alpha),
                           (0, 0, self.width, self.height))
            screen.blit(strobe_surface, (0, 0))
    
    def reset(self) -> None:
        self.strobe_intensity = 0.0
        self.last_beat_time = 0.0

