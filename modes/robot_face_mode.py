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
    
    def update(self, dt: float, bpm: float, is_beat: bool, features: dict) -> None:
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        if is_beat:
            self.strobe_intensity = 1.0
        self.strobe_intensity *= STROBE_DECAY
    
    def render(self, screen: pygame.Surface) -> None:
        # Apply strobe flash
        if self.strobe_intensity > STROBE_THRESHOLD:
            strobe_surface = pygame.Surface((self.width, self.height))
            strobe_alpha = int(self.strobe_intensity * 255)
            strobe_surface.set_alpha(strobe_alpha)
            strobe_surface.fill((255, 255, 255))
            screen.fill(COLOR_BACKGROUND_BLACK)
            screen.blit(strobe_surface, (0, 0))
        else:
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
        
        eye_brightness = min(255, int(100 + self.features['bass'] * 155 + self.strobe_intensity * 155))
        eye_color = (eye_brightness, eye_brightness, eye_brightness)
        
        pygame.draw.circle(screen, eye_color, (left_eye_x, eye_y), eye_size)
        pygame.draw.circle(screen, eye_color, (right_eye_x, eye_y), eye_size)
        
        # Eye pupils
        pupil_size = int(eye_size * 0.4 * (1 + self.features['bass'] * 0.5))
        pupil_color = (20, 20, 20)
        pygame.draw.circle(screen, pupil_color, (left_eye_x, eye_y), pupil_size)
        pygame.draw.circle(screen, pupil_color, (right_eye_x, eye_y), pupil_size)
        
        # Draw mouth
        mouth_y = center_y + int(face_size * 0.2)
        mouth_width = int(face_size * 0.4)
        mouth_height = int(face_size * 0.08)
        num_bars = 5
        
        mouth_brightness = min(255, int(50 + self.features['mid'] * 205))
        mouth_color = (mouth_brightness, mouth_brightness, mouth_brightness)
        
        for i in range(num_bars):
            bar_width = mouth_width // num_bars
            bar_x = center_x - mouth_width // 2 + i * bar_width
            bar_height = int(mouth_height * (0.3 + self.features['mid'] * 0.7))
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
        scanner_light_size = int(antenna_width * 0.6 * (1 + self.features['treble'] * 0.5))
        scanner_color = (200, 200, 255)
        pygame.draw.circle(screen, scanner_color, 
                          (center_x, antenna_y - antenna_height // 2), scanner_light_size)
    
    def reset(self) -> None:
        self.strobe_intensity = 0.0

